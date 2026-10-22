"""Tests for Contract 3 API: POST /api/rca/diagnose-and-remediate.

Verifies exact reproduction of the reference example from IMPLEMENTATION_PLAN.md:
- incident_id: INC-2026-0042
- root_cause_service: amf-01
- domain: 5g_core_sba
- confidence: 0.962
- culpable_actor: MNO-Core-Operator
- dynamic_trust_score: 0.42
- mrc_penalty_percentage: 20.0
- mrc_financial_penalty_usd: 30000.00
- action: horizontal_scale_and_pool_patch
- target: amf-01
- parameters: replicas: 4, client_pool_size: 2048
- state_estimation_compliance: PASSED (Live Prometheus queried at T-2s)
- hitl_approval_status: PENDING_OPERATOR_SIGNATURE
"""

import json
from pathlib import Path
import pytest
from httpx import AsyncClient, ASGITransport

from backend.app.main import app

FIXTURES_DIR = Path(__file__).resolve().parent / "fixtures"


@pytest.mark.asyncio
async def test_reproduce_contract_3_reference_example():
    ref_file = FIXTURES_DIR / "contract_2_inc_2026_0042.json"
    with open(ref_file, "r") as f:
        rca_payload = json.load(f)

    request_body = {
        "incident_id": "INC-2026-0042",
        "rca_analysis": rca_payload,
        "actor_context": [
            {"actor_id": "MNO-Core-Operator", "service": "amf-01", "mrc_usd": 150000.0},
            {"actor_id": "Cloud-Infra-Provider", "service": "k8s-worker-node-14", "mrc_usd": 85000.0},
        ],
        "require_hitl_approval": True,
    }

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post("/api/rca/diagnose-and-remediate", json=request_body)

    assert response.status_code == 200, f"Error: {response.text}"
    data = response.json()

    # Verify exact match with frozen Contract 3 specification in IMPLEMENTATION_PLAN.md
    assert data["incident_id"] == "INC-2026-0042"

    # Verdict
    verdict = data["verdict"]
    assert verdict["root_cause_service"] == "amf-01"
    assert verdict["domain"] == "5g_core_sba"
    assert verdict["confidence"] == 0.962
    assert verdict["synthesized_code_hash"].startswith("sha256:")

    # Fault propagation chain
    chain = data["fault_propagation_chain"]
    assert "Misconfigured SBI client pool on amf-01" in chain[0]
    assert "Frame 23: Registration Reject (Congestion) triggered" in chain[1]
    assert "HTTP/2 stream multiplexing queue starvation across AMF-SMF link" in chain[2]
    assert "Downstream packet drop on upf-edge-3" in chain[3]
    assert "SLA breach: PDU Session Setup Latency > 250ms" in chain[4]

    # SLA liability attribution (LASM)
    sla = data["sla_liability_attribution"]
    assert sla["culpable_actor"] == "MNO-Core-Operator"
    assert sla["dynamic_trust_score"] == 0.42
    assert sla["mrc_penalty_percentage"] == 20.0
    assert sla["mrc_financial_penalty_usd"] == 30000.00

    # Remediation plan & AGORA compliance
    rem = data["remediation_plan"]
    assert rem["action"] == "horizontal_scale_and_pool_patch"
    assert rem["target"] == "amf-01"
    assert rem["parameters"]["replicas"] == 4
    assert rem["parameters"]["client_pool_size"] == 2048
    assert "PASSED (Live Prometheus queried at T-2s)" in rem["state_estimation_compliance"]
    assert rem["hitl_approval_status"] == "PENDING_OPERATOR_SIGNATURE"
    assert rem["approval_token"] is not None


@pytest.mark.asyncio
async def test_diagnose_policy_auto_approval():
    ref_file = FIXTURES_DIR / "contract_2_inc_2026_0042.json"
    with open(ref_file, "r") as f:
        rca_payload = json.load(f)

    request_body = {
        "incident_id": "INC-2026-0042",
        "rca_analysis": rca_payload,
        "actor_context": [
            {"actor_id": "MNO-Core-Operator", "service": "amf-01", "mrc_usd": 150000.0},
        ],
        "require_hitl_approval": False,
    }

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post("/api/rca/diagnose-and-remediate", json=request_body)

    assert response.status_code == 200
    data = response.json()
    rem = data["remediation_plan"]
    assert rem["hitl_approval_status"] == "APPROVED_BY_POLICY"
    assert rem["approval_token"] is None


@pytest.mark.asyncio
async def test_diagnose_all_scenarios():
    scenario_files = sorted(FIXTURES_DIR.glob("scenario_*.json"))
    assert len(scenario_files) >= 5, "Expected at least 5 scenario fixtures"

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        for scen_file in scenario_files:
            with open(scen_file, "r") as f:
                scen_payload = json.load(f)

            inc_id = scen_payload["incident_id"]
            primary_cause = scen_payload["ranked_causes"][0]
            expected_target = primary_cause["component_id"]
            expected_domain = primary_cause["domain"]

            req = {
                "incident_id": inc_id,
                "rca_analysis": scen_payload,
                "actor_context": [
                    {"actor_id": "MNO-Core-Operator", "service": expected_target, "mrc_usd": 120000.0},
                    {"actor_id": "Cloud-Infra-Provider", "service": "k8s-node-infra", "mrc_usd": 60000.0},
                ],
                "require_hitl_approval": True,
            }

            resp = await client.post("/api/rca/diagnose-and-remediate", json=req)
            assert resp.status_code == 200, f"Failed on {scen_file.name}: {resp.text}"
            data = resp.json()

            assert data["incident_id"] == inc_id
            assert data["verdict"]["root_cause_service"] == expected_target
            assert data["verdict"]["domain"] == expected_domain
            assert data["verdict"]["synthesized_code_hash"].startswith("sha256:")
            assert len(data["fault_propagation_chain"]) >= 2
            assert data["sla_liability_attribution"]["culpable_actor"] is not None
            assert data["remediation_plan"]["target"] == expected_target
            assert data["remediation_plan"]["hitl_approval_status"] == "PENDING_OPERATOR_SIGNATURE"
            assert data["remediation_plan"]["approval_token"] is not None

