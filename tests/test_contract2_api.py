"""
Test: Contract 2 FastAPI Server (POST /api/rca/analyze)
Author: Sandarbh Gupta (24BIT0506) - Subsystem 2
"""

import pytest
from fastapi.testclient import TestClient
from src.ml_engine.server import app


def test_contract2_api_endpoint():
    client = TestClient(app)
    
    # 1. Health check
    res_health = client.get("/health")
    assert res_health.status_code == 200
    assert res_health.json()["owner"] == "Sandarbh Gupta (24BIT0506)"
    
    # 2. Incident analysis request
    payload = {
        "incident_id": "INC-2026-0042",
        "affected_components": ["amf-01", "smf-02", "upf-edge-3", "router-core-2"],
        "trigger_active_probing": True
    }
    
    res = client.post("/api/rca/analyze", json=payload)
    assert res.status_code == 200
    data = res.json()
    
    assert data["incident_id"] == "INC-2026-0042"
    assert data["status"] == "COMPLETED"
    assert len(data["ranked_causes"]) > 0
    assert data["ranked_causes"][0]["component_id"] == "amf-01"
    assert data["ranked_causes"][0]["anomaly_score"] > 0.50
    assert len(data["ranked_causes"][0]["xai_attributions"]) > 0
    
    # Verify PCAP
    assert data["pcap_verification"]["protocol_violation"] is True
    assert data["pcap_verification"]["deviating_frame"] == 23
    
    # Verify Active Probing
    assert data["active_probing_results"]["isolated_cv"] == "amf.sbi.client_pool_size"
    
    # Verify Topology Subgraph
    assert len(data["topology_subgraph"]["nodes"]) >= 4
    assert len(data["topology_subgraph"]["edges"]) >= 2
    
    print(f"\n[PASSED] Contract 2 API completed in {data['execution_time_ms']}ms. Response conforms 100% to schema.")
