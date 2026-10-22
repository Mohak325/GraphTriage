"""Full End-to-End Scenario and Integration Tests for Person C Subsystem."""

import json
from pathlib import Path
import pytest
from httpx import AsyncClient, ASGITransport

from backend.app.main import app

FIXTURES_DIR = Path(__file__).resolve().parent / "fixtures"


@pytest.mark.asyncio
async def test_e2e_hitl_approval_and_ssm_execution():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # 1. Diagnose INC-2026-0042
        ref_file = FIXTURES_DIR / "contract_2_inc_2026_0042.json"
        with open(ref_file, "r") as f:
            rca_payload = json.load(f)

        diag_resp = await client.post(
            "/api/rca/diagnose-and-remediate",
            json={
                "incident_id": "INC-2026-0042",
                "rca_analysis": rca_payload,
                "actor_context": [
                    {"actor_id": "MNO-Core-Operator", "service": "amf-01", "mrc_usd": 150000.0},
                ],
                "require_hitl_approval": True,
            },
        )
        assert diag_resp.status_code == 200
        token = diag_resp.json()["remediation_plan"]["approval_token"]
        assert token is not None

        # 2. Operator submits approval with cryptographic signature
        approve_resp = await client.post(
            "/api/hitl/approve",
            json={
                "incident_id": "INC-2026-0042",
                "approval_token": token,
                "operator_signature": "NOC-LEAD-SIGNATURE-77312",
                "comments": "Approved after reviewing live Prometheus SBI queue depth.",
            },
        )
        assert approve_resp.status_code == 200
        appr_data = approve_resp.json()
        assert appr_data["status"] == "APPROVED"
        assert appr_data["execution"]["status"] == "SUCCESS"
        assert appr_data["execution"]["sns_notification_sent"] is True

        # 3. Verify audit trail records the decision
        audit_resp = await client.get("/api/hitl/audit?incident_id=INC-2026-0042")
        assert audit_resp.status_code == 200
        audit_data = audit_resp.json()
        assert len(audit_data["audit_trail"]) >= 2
        assert len(audit_data["ssm_executions"]) >= 1


@pytest.mark.asyncio
async def test_e2e_active_probe_trigger():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.post(
            "/api/dashboard/probes/trigger",
            json={
                "incident_id": "INC-2026-0042",
                "probe_type": "http2_ping_nrf",
            },
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["incident_id"] == "INC-2026-0042"
        assert data["probe_status"] == "CONVERGED"
        assert data["posterior_confidence"] == 0.985


@pytest.mark.asyncio
async def test_e2e_dashboard_incident_list():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/api/dashboard/incidents")
        assert resp.status_code == 200
        incidents = resp.json()
        assert len(incidents) >= 5
        incident_ids = [i["incident_id"] for i in incidents]
        assert "INC-2026-0042" in incident_ids
