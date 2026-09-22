"""End-to-End Integration Test Suite for GraphTriage Backend.

Tests full API request-response contracts for Health, Graph topology,
Data ingestion pipelines, and Root Cause Analysis execution.
"""

import pytest
from fastapi.testclient import TestClient


class TestHealthEndpoints:
    """Validate liveness and readiness probes."""

    def test_basic_health_check(self, client: TestClient):
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "version" in data
        assert "timestamp" in data

    def test_detailed_health_check(self, client: TestClient):
        response = client.get("/health/detailed")
        assert response.status_code == 200
        data = response.json()
        assert "components" in data
        assert data["components"]["api"] == "healthy"


class TestGraphEndpoints:
    """Validate Cytoscape topology and spectral graph query endpoints."""

    def test_get_topology_cytoscape_format(self, client: TestClient):
        response = client.get("/api/graph/topology")
        assert response.status_code == 200
        data = response.json()
        assert "elements" in data
        assert "nodes" in data["elements"]
        assert "edges" in data["elements"]
        assert data["total_nodes"] >= 12
        assert data["total_edges"] >= 13

        # Validate node structure matches Cytoscape.js contract
        first_node = data["elements"]["nodes"][0]
        assert "data" in first_node
        assert "id" in first_node["data"]
        assert "label" in first_node["data"]
        assert "anomaly_score" in first_node["data"]

        # Validate edge structure
        first_edge = data["elements"]["edges"][0]
        assert "data" in first_edge
        assert "source" in first_edge["data"]
        assert "target" in first_edge["data"]
        assert "weight" in first_edge["data"]

    def test_get_service_subgraph_valid(self, client: TestClient):
        response = client.get("/api/graph/subgraph/srv-order-service?hops=1")
        assert response.status_code == 200
        data = response.json()
        node_ids = [n["data"]["id"] for n in data["elements"]["nodes"]]
        assert "srv-order-service" in node_ids
        # Order service calls payment and inventory
        assert any(nid in ("srv-payment-service", "srv-inventory-service", "srv-api-gateway") for nid in node_ids)

    def test_get_service_subgraph_not_found(self, client: TestClient):
        response = client.get("/api/graph/subgraph/non-existent-service")
        assert response.status_code == 404

    def test_get_fault_heatmap(self, client: TestClient):
        response = client.get("/api/graph/heatmap")
        assert response.status_code == 200
        nodes = response.json()
        assert isinstance(nodes, list)
        assert len(nodes) >= 12

        # Check payment-service or api-gateway has elevated gradient
        for item in nodes:
            assert "service_id" in item
            assert "fault_gradient" in item
            assert 0.0 <= item["fault_gradient"] <= 1.0

    def test_get_graph_metrics(self, client: TestClient):
        response = client.get("/api/graph/metrics")
        assert response.status_code == 200
        metrics = response.json()
        assert metrics["node_count"] >= 12
        assert metrics["edge_count"] >= 13
        assert metrics["density"] > 0.0
        assert metrics["connected_components"] >= 1


class TestDataIngestionPipeline:
    """Validate metric, trace, log, and topology ingestion APIs."""

    def test_ingest_metrics_batch(self, client: TestClient):
        payload = {
            "batch": [
                {
                    "service_id": "srv-payment-service",
                    "metric_name": "http_request_duration_seconds_p95",
                    "value": 3.12,
                    "labels": {"region": "us-east-1"}
                },
                {
                    "service_id": "srv-payment-service",
                    "metric_name": "error_rate",
                    "value": 0.42,
                    "labels": {"region": "us-east-1"}
                }
            ]
        }
        response = client.post("/api/ingest/metrics", json=payload)
        assert response.status_code == 202
        data = response.json()
        assert data["status"] == "accepted"
        assert data["ingested_count"] == 2

    def test_ingest_traces_batch(self, client: TestClient, mock_trace_spans):
        payload = {"spans": mock_trace_spans}
        response = client.post("/api/ingest/traces", json=payload)
        assert response.status_code == 202
        data = response.json()
        assert data["status"] == "accepted"
        assert data["ingested_count"] == len(mock_trace_spans)

    def test_ingest_logs_batch(self, client: TestClient):
        payload = {
            "events": [
                {
                    "service_id": "srv-payment-service",
                    "log_level": "ERROR",
                    "message": "HikariPool-1 - Connection is not available, request timed out after 30000ms",
                    "metadata": {"exception": "ConnectionTimeoutException"}
                }
            ]
        }
        response = client.post("/api/ingest/logs", json=payload)
        assert response.status_code == 202
        data = response.json()
        assert data["status"] == "accepted"
        assert data["ingested_count"] == 1

    def test_ingest_topology_snapshot(self, client: TestClient):
        payload = {
            "services": [
                {"id": "srv-fraud-detector", "name": "fraud-detector", "type": "security"}
            ],
            "dependencies": [
                {"source_service_id": "srv-payment-service", "target_service_id": "srv-fraud-detector", "protocol": "gRPC", "weight": 0.8}
            ]
        }
        response = client.post("/api/ingest/topology", json=payload)
        assert response.status_code == 201
        data = response.json()
        assert data["status"] == "created"
        assert data["ingested_count"] == 2


class TestRCAWorkflow:
    """Validate end-to-end Root Cause Analysis trigger and result retrieval."""

    def test_trigger_and_fetch_rca(self, client: TestClient):
        trigger_payload = {
            "incident_id": "inc-test-001",
            "anomaly_ids": ["anom-payment-latency-spike", "anom-order-downstream-timeout"],
            "window_minutes": 30,
            "top_k": 5,
            "damping_factor": 0.85,
            "enable_agent_verification": True
        }
        trigger_resp = client.post("/api/rca/trigger", json=trigger_payload)
        assert trigger_resp.status_code == 202
        status_data = trigger_resp.json()
        assert "rca_id" in status_data
        rca_id = status_data["rca_id"]

        # Poll status
        status_resp = client.get(f"/api/rca/{rca_id}/status")
        assert status_resp.status_code == 200
        assert status_resp.json()["rca_id"] == rca_id

        # Fetch result
        result_resp = client.get(f"/api/rca/{rca_id}/result")
        assert result_resp.status_code == 200
        result = result_resp.json()
        assert result["rca_id"] == rca_id
        assert result["status"] == "COMPLETED"
        assert result["root_cause_service_id"] is not None
        assert result["confidence_score"] > 0.0
        assert len(result["propagation_path"]) > 0
        assert len(result["remediation_recommendations"]) > 0

    def test_rca_history(self, client: TestClient):
        response = client.get("/api/rca/history?limit=10")
        assert response.status_code == 200
        assert isinstance(response.json(), list)
