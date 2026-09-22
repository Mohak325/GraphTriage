"""Navigator Agent Interface Bridge.

Provides high-level graph context, causal hypothesis evaluation, and hybrid
spectral-agent score combination for Mohak's multi-agent RCA orchestration system.
"""

import logging
from typing import List, Dict, Any, Optional, Set
import networkx as nx
from ai_models.graph_engine.fault_gradient import FaultGradientResult

logger = logging.getLogger(__name__)


class NavigatorGraphBridge:
    """Bridges the graph engine algorithms with multi-agent LLM exploration."""

    def __init__(self, spectral_weight: float = 0.6):
        """
        Args:
            spectral_weight: Weight given to graph diffusion score (1 - spectral_weight for agent confidence).
        """
        self.spectral_weight = spectral_weight

    def extract_neighborhood_context(
        self,
        graph: nx.DiGraph,
        service_id: str,
        depth: int = 2
    ) -> Dict[str, Any]:
        """Generate structured contextual summary of a service's graph neighborhood for LLM agent prompts.

        Includes upstream callers, downstream dependencies, error rates, latencies,
        and linked anomalies.
        """
        if not graph.has_node(service_id):
            return {"error": f"Service '{service_id}' does not exist in graph"}

        node_props = dict(graph.nodes[service_id])

        # Immediate upstream callers (who calls this service?)
        callers = []
        for u in graph.predecessors(service_id):
            data = graph.get_edge_data(u, service_id) or {}
            callers.append({
                "service_id": u,
                "service_name": graph.nodes[u].get("name", u),
                "weight": data.get("weight", 1.0),
                "latency_p95": data.get("latency_p95"),
                "error_rate": data.get("error_rate", 0.0),
                "status": graph.nodes[u].get("status", "healthy")
            })

        # Immediate downstream dependencies (who does this service call?)
        dependencies = []
        for v in graph.successors(service_id):
            data = graph.get_edge_data(service_id, v) or {}
            dependencies.append({
                "service_id": v,
                "service_name": graph.nodes[v].get("name", v),
                "weight": data.get("weight", 1.0),
                "latency_p95": data.get("latency_p95"),
                "error_rate": data.get("error_rate", 0.0),
                "status": graph.nodes[v].get("status", "healthy")
            })

        # Multi-hop ego subgraph nodes
        ego_nodes = list(nx.ego_graph(graph, service_id, radius=depth, undirected=True))
        subgraph_nodes = [
            {"id": n, "name": graph.nodes[n].get("name", n), "anomaly_score": graph.nodes[n].get("anomaly_score", 0.0)}
            for n in ego_nodes
        ]

        return {
            "target_service": {
                "id": service_id,
                "name": node_props.get("name", service_id),
                "type": node_props.get("type", "service"),
                "status": node_props.get("status", "healthy"),
                "anomaly_score": node_props.get("anomaly_score", 0.0),
                "rps": node_props.get("rps"),
                "latency_p95": node_props.get("latency_p95"),
                "error_rate": node_props.get("error_rate"),
                "anomalies": node_props.get("anomalies", [])
            },
            "upstream_callers": callers,
            "downstream_dependencies": dependencies,
            "neighborhood_services_count": len(subgraph_nodes),
            "neighborhood_nodes": subgraph_nodes
        }

    def evaluate_hypotheses(
        self,
        graph: nx.DiGraph,
        candidate_root_causes: List[str],
        observed_symptoms: List[str]
    ) -> List[Dict[str, Any]]:
        """Evaluate structural causal plausibility of candidate root causes.

        A candidate C is structurally plausible for symptom S if there exists a directed path
        from C to S in the call graph (since callee faults cascade outward to callers).
        """
        evaluations = []

        for candidate in candidate_root_causes:
            if not graph.has_node(candidate):
                continue

            reachable_symptoms = []
            path_lengths = []

            for symptom in observed_symptoms:
                if not graph.has_node(symptom):
                    continue
                # In reverse call direction, fault flows from callee to caller
                # If candidate is callee and symptom is caller: caller has path to candidate
                # Or candidate has path to symptom in fault propagation direction
                has_downstream = nx.has_path(graph, symptom, candidate)
                if has_downstream:
                    path_len = nx.shortest_path_length(graph, symptom, candidate)
                    reachable_symptoms.append(symptom)
                    path_lengths.append(path_len)

            coverage_ratio = len(reachable_symptoms) / max(len(observed_symptoms), 1)
            mean_dist = float(sum(path_lengths) / len(path_lengths)) if path_lengths else 999.0
            structural_plausibility = round(coverage_ratio * (1.0 / (1.0 + 0.2 * mean_dist)), 3)

            evaluations.append({
                "candidate_service_id": candidate,
                "candidate_name": graph.nodes[candidate].get("name", candidate),
                "explained_symptoms_count": len(reachable_symptoms),
                "explained_symptoms": reachable_symptoms,
                "symptom_coverage_ratio": round(coverage_ratio, 3),
                "average_causal_distance": round(mean_dist, 2) if path_lengths else None,
                "structural_plausibility": structural_plausibility
            })

        # Sort by highest plausibility
        evaluations.sort(key=lambda x: x["structural_plausibility"], reverse=True)
        return evaluations

    def combine_spectral_and_agent_scores(
        self,
        diffusion_results: FaultGradientResult,
        agent_confidences: Dict[str, float],
        agent_rationales: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """Combine spectral fault diffusion gradients with LLM Agent verification scores.

        Uses weighted Bayesian ensemble:
            final_score = spectral_weight * gradient + (1 - spectral_weight) * agent_score
        """
        combined_rankings = []
        agent_rationales = agent_rationales or {}

        for node in diffusion_results.ranked_nodes:
            sid = node.service_id
            spec_grad = node.gradient
            agent_score = agent_confidences.get(sid, 0.5)

            final_score = (self.spectral_weight * spec_grad) + ((1.0 - self.spectral_weight) * agent_score)

            combined_rankings.append({
                "service_id": sid,
                "service_name": node.service_name,
                "final_score": round(final_score, 4),
                "spectral_gradient": spec_grad,
                "agent_confidence": round(agent_score, 4),
                "initial_anomaly": node.initial_anomaly_score,
                "agent_rationale": agent_rationales.get(sid, "Evaluated via graph topology")
            })

        combined_rankings.sort(key=lambda x: x["final_score"], reverse=True)

        top_choice = combined_rankings[0] if combined_rankings else None

        return {
            "root_cause_service_id": top_choice["service_id"] if top_choice else None,
            "root_cause_service_name": top_choice["service_name"] if top_choice else None,
            "confidence_score": top_choice["final_score"] if top_choice else 0.0,
            "rankings": combined_rankings,
            "ensemble_weights": {
                "spectral_weight": self.spectral_weight,
                "agent_weight": round(1.0 - self.spectral_weight, 2)
            }
        }

    def generate_cypher_exploration_query(
        self,
        current_service_id: str,
        direction: str = "both",
        limit: int = 10
    ) -> str:
        """Generate Cypher query for interactive LLM tool execution."""
        if direction == "upstream":
            pattern = f"(upstream:Service)-[r:CALLS]->(current:Service {{id: '{current_service_id}'}})"
            ret = "upstream.id AS id, upstream.name AS name, r.weight AS weight, r.error_rate AS error_rate"
        elif direction == "downstream":
            pattern = f"(current:Service {{id: '{current_service_id}'}})-[r:CALLS]->(downstream:Service)"
            ret = "downstream.id AS id, downstream.name AS name, r.weight AS weight, r.latency_p95 AS latency_p95"
        else:
            pattern = f"(current:Service {{id: '{current_service_id}'}})-[r:CALLS]-(neighbor:Service)"
            ret = "neighbor.id AS id, neighbor.name AS name, type(r) AS rel, r.weight AS weight"

        return f"MATCH {pattern} RETURN {ret} LIMIT {limit};"
