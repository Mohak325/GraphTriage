"""Unit tests for the Fault Gradient Computation Engine."""

import pytest
import networkx as nx
import numpy as np

from ai_models.graph_engine.fault_gradient import (
    FaultGradientEngine,
    FaultGradientResult,
    NodeGradient
)


class TestFaultGradientEngine:
    """Test suite verifying mathematical properties and stability of spectral diffusion."""

    def test_basic_diffusion_convergence(self, sample_topology):
        engine = FaultGradientEngine(alpha=0.85, epsilon=1e-6, max_iter=100)
        result = engine.compute(sample_topology)

        assert isinstance(result, FaultGradientResult)
        assert result.root_cause_id in sample_topology.nodes()
        assert 0.0 < result.confidence_score <= 1.0
        assert result.iterations_to_converge <= 100
        assert result.convergence_residual < 1e-6
        assert len(result.ranked_nodes) == sample_topology.number_of_nodes()

    def test_alpha_bounds_validation(self):
        with pytest.raises(ValueError):
            FaultGradientEngine(alpha=0.0)

        with pytest.raises(ValueError):
            FaultGradientEngine(alpha=1.0)

        with pytest.raises(ValueError):
            FaultGradientEngine(alpha=-0.5)

    def test_empty_graph_raises_error(self):
        empty_g = nx.DiGraph()
        engine = FaultGradientEngine()
        with pytest.raises(ValueError, match="Cannot compute fault gradient on an empty graph"):
            engine.compute(empty_g)

    def test_single_node_graph(self):
        g = nx.DiGraph()
        g.add_node("s1", name="solo-service", anomaly_score=0.9)
        engine = FaultGradientEngine()
        result = engine.compute(g)

        assert result.root_cause_id == "s1"
        assert result.confidence_score >= 0.9
        assert len(result.propagation_path) == 0

    def test_cyclic_dependency_graph_stability(self):
        """Ensure diffusion converges cleanly even with feedback loops (cycles)."""
        cyclic_g = nx.DiGraph()
        cyclic_g.add_edge("A", "B", weight=1.0)
        cyclic_g.add_edge("B", "C", weight=1.0)
        cyclic_g.add_edge("C", "A", weight=1.0)  # Cycle: A -> B -> C -> A
        cyclic_g.nodes["A"]["anomaly_score"] = 0.8
        cyclic_g.nodes["B"]["anomaly_score"] = 0.2
        cyclic_g.nodes["C"]["anomaly_score"] = 0.1

        engine = FaultGradientEngine(alpha=0.85, epsilon=1e-6)
        result = engine.compute(cyclic_g)

        assert result.iterations_to_converge <= 100
        assert result.convergence_residual < 1e-6
        assert len(result.ranked_nodes) == 3

    def test_error_rate_amplification(self):
        """Edges with elevated error rates should amplify backward causal propagation."""
        g = nx.DiGraph()
        # Edge A -> B has normal error rate
        g.add_edge("Gateway", "ServiceA", weight=1.0, error_rate=0.01)
        # Edge A -> C has 50% error rate (failing downstream)
        g.add_edge("Gateway", "ServiceB", weight=1.0, error_rate=0.50)
        g.nodes["Gateway"]["anomaly_score"] = 0.9
        g.nodes["ServiceA"]["anomaly_score"] = 0.1
        g.nodes["ServiceB"]["anomaly_score"] = 0.8

        engine = FaultGradientEngine(alpha=0.85)
        result = engine.compute(g)

        # ServiceB should rank higher than ServiceA due to error penalty
        grad_b = result.gradients_by_node["ServiceB"]
        grad_a = result.gradients_by_node["ServiceA"]
        assert grad_b > grad_a

    def test_propagation_path_structure(self, sample_topology):
        engine = FaultGradientEngine(alpha=0.85)
        result = engine.compute(sample_topology)

        hops = result.propagation_path
        assert len(hops) > 0
        for hop in hops:
            assert hop.source_service_id in sample_topology.nodes()
            assert hop.target_service_id in sample_topology.nodes()
            assert hop.edge_weight > 0.0

    def test_damping_factor_sensitivity(self, sample_topology):
        """Higher alpha gives greater weight to random walk vs initial teleportation."""
        engine_low = FaultGradientEngine(alpha=0.2)
        engine_high = FaultGradientEngine(alpha=0.9)

        res_low = engine_low.compute(sample_topology)
        res_high = engine_high.compute(sample_topology)

        assert res_low.iterations_to_converge <= res_high.iterations_to_converge
