"""Unit tests for the Network Topology Graph Builder."""

import pytest
import networkx as nx
import numpy as np

from ai_models.graph_engine.topology_builder import TopologyBuilder


class TestTopologyBuilder:
    """Test suite for TopologyBuilder trace synthesis and validation."""

    def test_build_from_traces(self, mock_trace_spans):
        builder = TopologyBuilder()
        g = builder.build_from_traces(mock_trace_spans)

        assert isinstance(g, nx.DiGraph)
        assert g.number_of_nodes() == 4  # api-gateway, order-service, payment-service, auth-service
        assert g.has_node("srv-api-gateway")
        assert g.has_node("srv-order-service")
        assert g.has_node("srv-payment-service")

        # Check edge attributes between order and payment
        edge = g["srv-order-service"]["srv-payment-service"]
        assert edge["call_count"] == 2
        assert edge["error_rate"] == 1.0  # Both spans had errors
        assert edge["latency_p95"] >= 2400.0
        assert edge["weight"] > 0.0

    def test_enrich_with_anomalies(self):
        builder = TopologyBuilder()
        g = nx.DiGraph()
        g.add_node("srv-payment-service", name="payment")
        g.add_node("srv-order-service", name="order")

        anomalies = [
            {
                "service_id": "srv-payment-service",
                "severity": "critical",
                "confidence": 0.95,
                "metric_name": "db_pool"
            }
        ]

        enriched = builder.enrich_with_anomalies(g, anomalies)
        assert enriched.nodes["srv-payment-service"]["anomaly_score"] >= 0.8
        assert enriched.nodes["srv-payment-service"]["status"] == "critical"
        assert enriched.nodes["srv-order-service"]["anomaly_score"] == 0.0

    def test_validate_topology_detects_isolated_nodes(self):
        builder = TopologyBuilder()
        g = nx.DiGraph()
        g.add_edge("A", "B")
        g.add_node("C")  # Isolated

        val = builder.validate_topology(g)
        assert val["is_valid"] is False
        assert "C" in val["isolated_nodes"]

    def test_validate_topology_detects_cycles(self):
        builder = TopologyBuilder()
        g = nx.DiGraph()
        g.add_edge("A", "B")
        g.add_edge("B", "C")
        g.add_edge("C", "A")

        val = builder.validate_topology(g)
        assert val["has_cycles"] is True
        assert val["cycle_count"] == 1

    def test_compute_adjacency_matrix(self):
        builder = TopologyBuilder()
        g = nx.DiGraph()
        g.add_edge("s1", "s2", weight=2.5)

        matrix, node_order = builder.compute_adjacency_matrix(g)
        assert isinstance(matrix, np.ndarray)
        assert matrix.shape == (2, 2)
        idx1 = node_order.index("s1")
        idx2 = node_order.index("s2")
        assert matrix[idx1, idx2] == 2.5

    def test_to_cytoscape_elements_schema(self, sample_topology):
        builder = TopologyBuilder()
        cyto = builder.to_cytoscape_elements(sample_topology)

        assert "elements" in cyto
        assert "nodes" in cyto["elements"]
        assert "edges" in cyto["elements"]

        node = cyto["elements"]["nodes"][0]
        assert "data" in node
        assert "id" in node["data"]
        assert "label" in node["data"]

        edge = cyto["elements"]["edges"][0]
        assert "data" in edge
        assert "source" in edge["data"]
        assert "target" in edge["data"]
