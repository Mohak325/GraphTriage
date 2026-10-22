"""Unit and integration tests for ReAct MCP agent, NFVAgent RAG, and auxiliary services."""

import pytest
from httpx import AsyncClient, ASGITransport

from backend.app.main import app
from backend.app.agents.react_mcp_agent import ReactMCPAgent
from backend.app.agents.nfv_agent_rag import NFVAgentRAG
from backend.app.services.fixture_clients import (
    FixtureMCPTelemetryClient,
    FixtureRCAClient,
    FixtureVectorStoreRAGClient,
)
from backend.app.services.bedrock_client import BedrockLLMClient
from backend.app.core.security import hitl_manager
from contracts.pydantic.contract_2_rca_analysis import RCARequest, TimeWindow
from datetime import datetime, timezone


@pytest.mark.asyncio
async def test_react_mcp_agent_run():
    mcp_client = FixtureMCPTelemetryClient()
    agent = ReactMCPAgent(mcp_client=mcp_client)
    res = await agent.run(
        incident_id="INC-2026-0042",
        context={"affected_components": ["amf-01", "upf-edge-3"]},
    )
    assert res.root_cause_service == "amf-01"
    assert res.domain == "5g_core_sba"
    assert res.confidence >= 0.90
    assert len(res.fault_propagation_chain) >= 2
    assert "query_prometheus" in res.tools_invoked
    assert res.recommended_action == "horizontal_scale_and_pool_patch"


@pytest.mark.asyncio
async def test_nfv_agent_rag_retrieval():
    rag_client = FixtureVectorStoreRAGClient()
    nfv_agent = NFVAgentRAG(rag_client=rag_client)
    recommendation = await nfv_agent.retrieve_remediation_guidelines(
        incident_id="INC-2026-0042",
        fault_type="Registration Congestion / Thread Pool Exhaustion",
        affected_component="amf-01",
    )
    assert recommendation.incident_id == "INC-2026-0042"
    assert len(recommendation.citations) >= 1
    top_citation = recommendation.citations[0]
    assert "ETSI" in top_citation["standard"] or "3GPP" in top_citation["standard"]
    assert top_citation["score"] > 0.0


@pytest.mark.asyncio
async def test_fixture_rca_client():
    client = FixtureRCAClient()
    req = RCARequest(
        incident_id="INC-2026-0042",
        time_window=TimeWindow(
            start=datetime.now(timezone.utc),
            end=datetime.now(timezone.utc),
        ),
        affected_components=["amf-01"],
        telemetry_s3_path="s3://test/path",
        trigger_active_probing=True,
    )
    resp = await client.analyze_incident(req)
    assert resp.incident_id == "INC-2026-0042"
    assert resp.ranked_causes[0].component_id == "amf-01"


@pytest.mark.asyncio
async def test_hitl_rejection_flow():
    token = hitl_manager.generate_token(
        incident_id="INC-2026-9999",
        action="drain_node",
        target="k8s-worker-node-14",
        parameters={},
    )
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        reject_resp = await client.post(
            "/api/hitl/reject",
            json={
                "incident_id": "INC-2026-9999",
                "approval_token": token,
                "operator_signature": "NOC-SENIOR-ENG-12",
                "reason": "Blast radius too high; secondary carrier traffic present.",
            },
        )
        assert reject_resp.status_code == 200
        assert reject_resp.json()["status"] == "REJECTED"


@pytest.mark.asyncio
async def test_dashboard_rules_endpoint():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/api/dashboard/rules")
        assert resp.status_code == 200
        data = resp.json()
        assert data["total_rules"] >= 50


@pytest.mark.asyncio
async def test_health_check_endpoint():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/healthz")
        assert resp.status_code == 200
        assert resp.json()["status"] == "healthy"


@pytest.mark.asyncio
async def test_bedrock_llm_client_mock():
    client = BedrockLLMClient()
    response = await client.invoke_model(
        prompt="Synthesize telecom RCA for amf-01",
        system_instruction="You are a 3GPP SBA expert.",
    )
    assert response is not None
    assert len(response) > 0



@pytest.mark.asyncio
async def test_dashboard_incident_detail_and_404():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # Existing incident
        resp = await client.get("/api/dashboard/incidents/INC-2026-0042")
        assert resp.status_code == 200
        data = resp.json()
        assert data["incident_id"] == "INC-2026-0042"

        # Non-existing incident
        resp_404 = await client.get("/api/dashboard/incidents/INC-DOES-NOT-EXIST")
        assert resp_404.status_code == 404


@pytest.mark.asyncio
async def test_hitl_invalid_approval_and_rejection():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # Invalid approval
        bad_appr = await client.post(
            "/api/hitl/approve",
            json={
                "incident_id": "INC-2026-0042",
                "approval_token": "tampered-bad-token",
                "operator_signature": "NOC-ENG",
            },
        )
        assert bad_appr.status_code == 403

        # Invalid rejection
        bad_rej = await client.post(
            "/api/hitl/reject",
            json={
                "incident_id": "INC-2026-0042",
                "approval_token": "tampered-bad-token",
                "operator_signature": "NOC-ENG",
                "reason": "Testing",
            },
        )
        assert bad_rej.status_code == 403

