"""Frontend-Backend API Contract Test Suite (Collaboration with Aarnav).

Guarantees exact JSON schema compatibility with the Cytoscape.js graph canvas,
risk heatmap overlays, and live RCA dashboard components in the frontend.
"""

import pytest
from fastapi.testclient import TestClient


class TestFrontendAPIContract:
    """Rigorous contract validation for frontend visualization consuming Cytoscape.js format."""

    def test_cytoscape_topology_node_attributes(self, client: TestClient):
        """Cytoscape.js requires each node to have { data: { id, label } }."""
        response = client.get("/api/graph/topology")
        assert response.status_code == 200
        payload = response.json()

        nodes = payload["elements"]["nodes"]
        assert len(nodes) > 0

        for node in nodes:
            assert "data" in node, "Cytoscape element must have 'data' wrapper"
            d = node["data"]
            assert "id" in d and isinstance(d["id"], str)
            assert "label" in d and isinstance(d["label"], str)
            assert "type" in d
            assert "status" in d and d["status"] in ("healthy", "degraded", "critical")
            assert "anomaly_score" in d and (0.0 <= d["anomaly_score"] <= 1.0)

    def test_cytoscape_topology_edge_attributes(self, client: TestClient):
        """Cytoscape.js requires each edge to have { data: { id, source, target } }."""
        response = client.get("/api/graph/topology")
        assert response.status_code == 200
        payload = response.json()

        edges = payload["elements"]["edges"]
        assert len(edges) > 0

        node_ids = {n["data"]["id"] for n in payload["elements"]["nodes"]}

        for edge in edges:
            assert "data" in edge
            d = edge["data"]
            assert "id" in d
            assert "source" in d and d["source"] in node_ids, "Edge source must reference existing node"
            assert "target" in d and d["target"] in node_ids, "Edge target must reference existing node"
            assert "weight" in d and isinstance(d["weight"], (int, float))

    def test_heatmap_frontend_contract(self, client: TestClient):
        """Frontend heatmap color scales require normalized fault gradients [0, 1]."""
        response = client.get("/api/graph/heatmap")
        assert response.status_code == 200
        items = response.json()

        for item in items:
            assert "service_id" in item
            assert "service_name" in item
            assert "fault_gradient" in item
            assert "status" in item
            assert 0.0 <= item["fault_gradient"] <= 1.0
            assert item["criticality"] in ("low", "medium", "high", "critical")

    def test_cors_headers_present(self, client: TestClient):
        """Frontend browser requests require valid Access-Control headers."""
        response = client.options(
            "/api/graph/topology",
            headers={
                "Origin": "http://localhost:3000",
                "Access-Control-Request-Method": "GET"
            }
        )
        assert response.status_code == 200
        assert "access-control-allow-origin" in response.headers
