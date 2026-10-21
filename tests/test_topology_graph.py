"""
Test Suite for Topology Graph Engine.
Grounding: Paper 2 (DTFL) & Paper 7 (TN-AutoRCA).
"""

from src.graph.neptune_loader import TopologyGraphEngine


def test_topology_graph_construction_and_traversal():
    engine = TopologyGraphEngine()

    # Add 5GC Core SBA nodes
    engine.add_network_function("amf-01", "AMF", status="anomalous")
    engine.add_network_function("smf-01", "SMF", status="normal")
    engine.add_network_function("upf-edge-3", "UPF", status="degraded")
    engine.add_network_function("nrf-01", "NRF", status="normal")

    # Add call links
    engine.add_call_dependency("amf-01", "smf-01", latency_ms=142.5)
    engine.add_call_dependency("smf-01", "upf-edge-3", latency_ms=35.0)
    engine.add_call_dependency("amf-01", "nrf-01", latency_ms=4.2)

    # Check 1-hop neighbors from amf-01
    one_hop = engine.get_k_hop_neighbors("amf-01", k=1)
    assert "amf-01" in one_hop
    assert "smf-01" in one_hop
    assert "nrf-01" in one_hop

    # Check 2-hop neighbors from amf-01 (should include upf-edge-3)
    two_hop = engine.get_k_hop_neighbors("amf-01", k=2)
    assert "upf-edge-3" in two_hop


def test_incident_subgraph_extraction_contract2():
    engine = TopologyGraphEngine()

    engine.add_network_function("amf-01", "AMF", status="anomalous")
    engine.add_network_function("smf-01", "SMF", status="normal")
    engine.add_call_dependency("amf-01", "smf-01", latency_ms=142.5)

    subgraph = engine.extract_incident_subgraph(["amf-01"], hop_expansion=1)

    node_ids = [n.id for n in subgraph.nodes]
    assert "amf-01" in node_ids
    assert "smf-01" in node_ids

    # Edge checks
    assert len(subgraph.edges) == 1
    edge = subgraph.edges[0]
    assert edge.source == "amf-01"
    assert edge.target == "smf-01"
    assert edge.latency_ms == 142.5
