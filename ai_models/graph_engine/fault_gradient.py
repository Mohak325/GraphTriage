"""Fault Gradient Computation Engine.

Implements spectral damped diffusion and reverse causal propagation on
microservice dependency graphs to pinpoint root causes and trace failure paths.

Mathematical Formulation:
    Given directed call graph G = (V, E) with weighted adjacency W:
    Normalized backward transition matrix P_rev = D_in^{-1} W^T
    Diffusion step: f^{(t+1)} = alpha * P_rev * f^{(t)} + (1 - alpha) * y
    where:
        y : initial observed anomaly vector
        alpha : damping factor (typically 0.85)
        f^* : stationary fault gradient distribution at convergence
"""

import time
import logging
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass, field
import networkx as nx
import numpy as np

logger = logging.getLogger(__name__)


@dataclass
class NodeGradient:
    """Gradient score and ranking for a single service node."""
    service_id: str
    service_name: str
    gradient: float
    rank: int
    initial_anomaly_score: float
    is_root_cause_candidate: bool
    status: str = "healthy"


@dataclass
class CausalPropagationHop:
    """A step along the identified causal fault propagation path."""
    source_service_id: str
    target_service_id: str
    gradient_drop: float
    edge_weight: float
    observed_latency_p95: Optional[float] = None
    observed_error_rate: Optional[float] = None


@dataclass
class FaultGradientResult:
    """Comprehensive output of the spectral fault gradient diffusion analysis."""
    root_cause_id: str
    root_cause_name: str
    confidence_score: float
    ranked_nodes: List[NodeGradient]
    gradients_by_node: Dict[str, float]
    propagation_path: List[CausalPropagationHop]
    iterations_to_converge: int
    execution_time_ms: float
    damping_factor: float
    convergence_residual: float


class FaultGradientEngine:
    """Executes diffusion-based causal inference on microservice graphs."""

    def __init__(
        self,
        alpha: float = 0.85,
        epsilon: float = 1e-6,
        max_iter: int = 100
    ):
        """
        Args:
            alpha: Damping factor governing random walk vs teleportation (0 < alpha < 1).
            epsilon: Convergence tolerance (L2 norm of residual).
            max_iter: Maximum power iteration steps.
        """
        if not (0.0 < alpha < 1.0):
            raise ValueError(f"Damping factor alpha must be in (0, 1), got {alpha}")
        self.alpha = alpha
        self.epsilon = epsilon
        self.max_iter = max_iter

    def compute(
        self,
        graph: nx.DiGraph,
        initial_anomalies: Optional[Dict[str, float]] = None,
        top_k: int = 5
    ) -> FaultGradientResult:
        """Run fault gradient diffusion on the given microservice topology graph.

        Args:
            graph: NetworkX DiGraph representing service calls (edges: caller -> callee).
            initial_anomalies: Dict mapping service_id -> observed anomaly score [0.0, 1.0].
                               If None, extracts from node attribute 'anomaly_score'.
            top_k: Number of top candidate nodes to mark as root cause candidates.

        Returns:
            FaultGradientResult with ranked nodes, propagation paths, and convergence metrics.
        """
        start_time = time.perf_counter()
        nodes = list(graph.nodes())
        n = len(nodes)

        if n == 0:
            raise ValueError("Cannot compute fault gradient on an empty graph.")

        node_to_idx = {node: i for i, node in enumerate(nodes)}
        idx_to_node = {i: node for i, node in enumerate(nodes)}

        # 1. Build initial anomaly seed vector y
        y = np.zeros(n, dtype=np.float64)
        for i, node in enumerate(nodes):
            if initial_anomalies and node in initial_anomalies:
                y[i] = float(initial_anomalies[node])
            else:
                y[i] = float(graph.nodes[node].get("anomaly_score", 0.0))

        # If all anomaly scores are zero, use uniform prior
        norm_y = np.sum(y)
        if norm_y > 0:
            y_normalized = y / norm_y
        else:
            y_normalized = np.ones(n, dtype=np.float64) / n

        # 2. Build reverse transition probability matrix P_rev
        # Failure propagates downstream (caller gets error when callee fails),
        # so root causes lie upstream of symptoms in the reverse call direction.
        W = np.zeros((n, n), dtype=np.float64)
        for u, v in graph.edges():
            data = graph.get_edge_data(u, v) or {}
            i = node_to_idx[u]
            j = node_to_idx[v]
            # Edge u -> v has weight w. In reverse diffusion: fault travels v -> u
            w = float(data.get("weight", 1.0))
            # Include error rate penalty if present to amplify faulty paths
            err_rate = float(data.get("error_rate", 0.0))
            effective_weight = w * (1.0 + 2.0 * err_rate)
            W[j, i] += effective_weight  # Reversed direction: target to source

        # Row-normalize to make transition probability stochastic
        row_sums = W.sum(axis=1, keepdims=True)
        P_rev = np.zeros_like(W)
        for idx in range(n):
            if row_sums[idx, 0] > 0:
                P_rev[idx, :] = W[idx, :] / row_sums[idx, 0]
            else:
                # Dangling node / sink: teleport uniformly
                P_rev[idx, :] = 1.0 / n

        # 3. Power Iteration Diffusion: f^{(t+1)} = alpha * P_rev^T * f^{(t)} + (1 - alpha) * y_normalized
        f = y_normalized.copy()
        iterations = 0
        residual = 1.0

        for it in range(self.max_iter):
            iterations += 1
            f_next = self.alpha * P_rev.T.dot(f) + (1.0 - self.alpha) * y_normalized
            residual = float(np.linalg.norm(f_next - f, ord=2))
            f = f_next
            if residual < self.epsilon:
                break

        # Normalize final gradient vector to [0, 1] range for intuitive interpretation
        max_val = np.max(f) if np.max(f) > 0 else 1.0
        normalized_gradients = f / max_val

        # 4. Rank nodes by fault gradient
        ranked_indices = np.argsort(-f)
        ranked_nodes: List[NodeGradient] = []
        gradients_by_node: Dict[str, float] = {}

        for rank, idx in enumerate(ranked_indices, start=1):
            node_id = idx_to_node[idx]
            grad_val = float(normalized_gradients[idx])
            gradients_by_node[node_id] = round(grad_val, 4)

            node_data = graph.nodes[node_id]
            node_name = node_data.get("name", node_id)
            status = node_data.get("status", "healthy")

            ranked_nodes.append(NodeGradient(
                service_id=node_id,
                service_name=node_name,
                gradient=round(grad_val, 4),
                rank=rank,
                initial_anomaly_score=round(float(y[idx]), 4),
                is_root_cause_candidate=rank <= top_k,
                status=status
            ))

        # Top root cause candidate
        top_idx = ranked_indices[0]
        root_cause_id = idx_to_node[top_idx]
        root_cause_name = graph.nodes[root_cause_id].get("name", root_cause_id)

        # 5. Compute confidence score
        # Confidence is derived from the margin between rank 1 and rank 2
        confidence = self._compute_confidence(f, ranked_indices)

        # 6. Extract causal propagation path
        propagation_path = self._extract_propagation_path(
            graph, root_cause_id, gradients_by_node, node_to_idx
        )

        elapsed_ms = (time.perf_counter() - start_time) * 1000.0

        return FaultGradientResult(
            root_cause_id=root_cause_id,
            root_cause_name=root_cause_name,
            confidence_score=round(confidence, 3),
            ranked_nodes=ranked_nodes,
            gradients_by_node=gradients_by_node,
            propagation_path=propagation_path,
            iterations_to_converge=iterations,
            execution_time_ms=round(elapsed_ms, 2),
            damping_factor=self.alpha,
            convergence_residual=float(residual)
        )

    def _compute_confidence(self, f: np.ndarray, ranked_indices: np.ndarray) -> float:
        """Compute statistical confidence score based on softmax entropy and top margin."""
        if len(ranked_indices) <= 1:
            return 1.0

        top_val = f[ranked_indices[0]]
        second_val = f[ranked_indices[1]]
        total_sum = np.sum(f)

        if total_sum <= 0:
            return 0.5

        # Margin ratio
        margin = (top_val - second_val) / (top_val + 1e-9)
        # Dominance ratio
        dominance = top_val / total_sum

        # Harmonic combination
        confidence = 0.6 * margin + 0.4 * min(dominance * 2.0, 1.0)
        return float(np.clip(confidence, 0.45, 0.99))

    def _extract_propagation_path(
        self,
        graph: nx.DiGraph,
        root_cause_id: str,
        gradients: Dict[str, float],
        node_to_idx: Dict[str, int]
    ) -> List[CausalPropagationHop]:
        """Trace the highest-gradient outward propagation path from root cause to edge symptoms."""
        hops: List[CausalPropagationHop] = []
        visited = {root_cause_id}
        current_node = root_cause_id

        # Walk outward along outgoing call edges towards downstream symptoms
        for _ in range(5):  # Max 5 hops
            neighbors = list(graph.successors(current_node))
            if not neighbors:
                break

            # Find downstream neighbor with the highest gradient among unvisited
            unvisited_neighbors = [v for v in neighbors if v not in visited]
            if not unvisited_neighbors:
                break

            # Pick neighbor with highest gradient
            best_neighbor = max(
                unvisited_neighbors,
                key=lambda v: gradients.get(v, 0.0)
            )
            edge_data = graph.get_edge_data(current_node, best_neighbor) or {}

            grad_drop = gradients.get(current_node, 0.0) - gradients.get(best_neighbor, 0.0)
            hop = CausalPropagationHop(
                source_service_id=current_node,
                target_service_id=best_neighbor,
                gradient_drop=round(grad_drop, 4),
                edge_weight=float(edge_data.get("weight", 1.0)),
                observed_latency_p95=edge_data.get("latency_p95"),
                observed_error_rate=edge_data.get("error_rate")
            )
            hops.append(hop)
            visited.add(best_neighbor)
            current_node = best_neighbor

        return hops
