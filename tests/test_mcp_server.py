"""
Test Suite for FastAPI Model Context Protocol (MCP) Server.
Grounding: Paper 14 (MCP-Diag & NIKA).
"""

from fastapi.testclient import TestClient
import json
from src.mcp.server import create_mcp_app


def test_mcp_health_endpoint():
    app = create_mcp_app(mock_mode=True)
    client = TestClient(app)

    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_mcp_query_prometheus_tool():
    app = create_mcp_app(mock_mode=True)
    client = TestClient(app)

    payload = {
        "component_id": "amf-01",
        "promql": "sum(rate(amf_requests_total[1m]))"
    }
    response = client.post("/tools/query_prometheus_metrics", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert "state_estimation_timestamp" in data


def test_mcp_query_nwdaf_tool():
    app = create_mcp_app(mock_mode=True)
    client = TestClient(app)

    payload = {
        "nf_type": "AMF",
        "analytics_id": "NF_LOAD",
        "time_window_seconds": 300
    }
    response = client.post("/tools/query_nwdaf_analytics", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["nf_type"] == "AMF"
    assert "nf_load_statistics" in data


def test_mcp_get_kubernetes_status():
    app = create_mcp_app(mock_mode=True)
    client = TestClient(app)

    payload = {
        "namespace": "5gc",
        "pod_selector": "app=amf-01"
    }
    response = client.post("/tools/get_kubernetes_pod_status", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert len(data["pods"]) > 0


def test_mcp_jsonrpc_tools_list_and_call():
    app = create_mcp_app(mock_mode=True)
    client = TestClient(app)

    # 1. tools/list
    rpc_list = {
        "jsonrpc": "2.0",
        "method": "tools/list",
        "id": 1
    }
    res_list = client.post("/mcp", json=rpc_list)
    assert res_list.status_code == 200
    body_list = res_list.json()
    tools = body_list["result"]["tools"]
    tool_names = [t["name"] for t in tools]
    assert "query_prometheus_metrics" in tool_names
    assert "query_topology_neighbors" in tool_names

    # 2. tools/call
    rpc_call = {
        "jsonrpc": "2.0",
        "method": "tools/call",
        "params": {
            "name": "query_topology_neighbors",
            "arguments": {
                "component_id": "amf-01",
                "hop_depth": 2
            }
        },
        "id": 2
    }
    res_call = client.post("/mcp", json=rpc_call)
    assert res_call.status_code == 200
    body_call = res_call.json()
    assert body_call["error"] is None
    content_text = body_call["result"]["content"][0]["text"]
    parsed_content = json.loads(content_text)
    assert parsed_content["component_id"] == "amf-01"
    assert "smf-01" in parsed_content["neighbors"]
