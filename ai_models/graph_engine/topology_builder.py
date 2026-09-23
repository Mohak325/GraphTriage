"""Network Topology Graph Builder.

Constructs, enriches, and validates heterogeneous microservice dependency graphs
from trace spans, service catalogs, and infrastructure mappings for downstream
diffusion and spectral analysis algorithms.
"""

import logging
from typing import List, Dict, Any, Optional, Tuple, Set
import networkx as nx
import numpy as np

logger = logging.getLogger(__name__)


class TopologyValidationError(Exception):
    """Raised when topology fails critical integrity constraints."""
    pass


class TopologyBuilder:
    """Constructs and enriches NetworkX microservice dependency graphs from traces and infrastructure metrics."""

    def __init__(self, default_weight: float = 1.0):
        self.default_weight = default_weight

    def build_from_traces(self, spans: List[Dict[str, Any]]) -> nx.DiGraph:
        """Construct a directed weighted call graph from raw distributed trace spans.

        Aggregates multiple spans between identical service pairs to compute:
        - Call frequency (total request count)
        - Latency p95 / mean latency
        - Error rate
        - Dynamic edge weight: w = (request_count / total) * (1.0 + error_rate * 2.0)
        """
        graph = nx.DiGraph()
        pair_metrics: Dict[Tuple[str, str], Dict[str, Any]] = {}

        for span in spans:
            caller = span.get("caller_service_id")
            callee = span.get("callee_service_id")
            if not caller or not callee or caller == callee:
                continue

            pair = (caller, callee)
            if pair not in pair_metrics:
                pair_metrics[pair] = {
                    "count": 0,
                    "latencies": [],
                    "errors": 0,
                    "endpoints": set()
                }

            pair_metrics[pair]["count"] += 1
            duration = float(span.get("duration_ms", 0.0))
            pair_metrics[pair]["latencies"].append(duration)
            if span.get("http_status", 200) >= 400 or span.get("has_error", False):
                pair_metrics[pair]["errors"] += 1
            if "endpoint" in span:
                pair_metrics[pair]["endpoints"].add(span["endpoint"])

        # Compute aggregate weights and assign to edges
        total_calls = sum(m["count"] for m in pair_metrics.values()) or 1

        for (caller, callee), metrics in pair_metrics.items():
            count = metrics["count"]
            error_rate = metrics["errors"] / count if count > 0 else 0.0
            latencies = metrics["latencies"]
            latency_p95 = float(np.percentile(latencies, 95)) if latencies else 0.0
            latency_mean = float(np.mean(latencies)) if latencies else 0.0

            # Dynamic weight reflecting flow traffic & failure severity
            relative_traffic = count / total_calls
            weight = round(relative_traffic * (1.0 + error_rate * 2.0), 4)

            # Ensure nodes exist
            if not graph.has_node(caller):
                graph.add_node(caller, id=caller, label=caller, type="service", status="healthy")
            if not graph.has_node(callee):
                graph.add_node(callee, id=callee, label=callee, type="service", status="healthy")

            graph.add_edge(
                caller,
                callee,
                weight=max(weight, 0.01),
                call_count=count,
                error_rate=round(error_rate, 4),
                latency_p95=round(latency_p95, 2),
                latency_mean=round(latency_mean, 2),
                endpoints=list(metrics["endpoints"])
            )

        logger.info(f"Built trace graph: {graph.number_of_nodes()} nodes, {graph.number_of_edges()} edges")
        return graph

    def enrich_with_anomalies(
        self,
        graph: nx.DiGraph,
        anomalies: List[Dict[str, Any]]
    ) -> nx.DiGraph:
        """Annotate nodes with active anomaly indicators and compute preliminary node risk scores."""
        # Initialize default anomaly score on all nodes
        for node in graph.nodes():
            if "anomaly_score" not in graph.nodes[node]:
                graph.nodes[node]["anomaly_score"] = 0.0
                graph.nodes[node]["anomalies"] = []

        for anom in anomalies:
            service_id = anom.get("service_id")
            if service_id and graph.has_node(service_id):
                severity = anom.get("severity", "low").lower()
                severity_weight = {
                    "critical": 1.0,
                    "high": 0.8,
                    "medium": 0.5,
                    "low": 0.2
                }.get(severity, 0.3)

                confidence = float(anom.get("confidence", 0.8))
                score = round(severity_weight * confidence, 3)

                # Keep maximum observed score on node
                current_score = graph.nodes[service_id].get("anomaly_score", 0.0)
                graph.nodes[service_id]["anomaly_score"] = max(current_score, score)
                graph.nodes[service_id]["status"] = "critical" if score >= 0.8 else ("degraded" if score >= 0.4 else "healthy")
                graph.nodes[service_id]["anomalies"].append(anom)

        return graph

    def validate_topology(self, graph: nx.DiGraph) -> Dict[str, Any]:
        """Validate structural integrity of the microservice graph.

        Checks:
        - Orphaned / isolated nodes (degree = 0)
        - Dead-end sinks (out-degree = 0 with no upstream reason)
        - Source nodes (in-degree = 0, usually API gateways)
        - Weakly connected components (graph fragmentation)
        - Cycle detection
        """
        isolated_nodes = list(nx.isolates(graph))
        in_degrees = {n: d for n, d in graph.in_degree}
        out_degrees = {n: d for n, d in graph.out_degree}

        source_nodes = [n for n, deg in in_degrees.items() if deg == 0 and out_degrees.get(n, 0) > 0]
        sink_nodes = [n for n, deg in out_degrees.items() if deg == 0 and in_degrees.get(n, 0) > 0]
        cycles = list(nx.simple_cycles(graph))
        components = list(nx.weakly_connected_components(graph))

        validation_result = {
            "is_valid": len(isolated_nodes) == 0 and len(components) <= 2,
            "total_nodes": graph.number_of_nodes(),
            "total_edges": graph.number_of_edges(),
            "isolated_nodes": isolated_nodes,
            "source_nodes": source_nodes,
            "sink_nodes": sink_nodes,
            "has_cycles": len(cycles) > 0,
            "cycle_count": len(cycles),
            "cycles": cycles[:5],
            "connected_components_count": len(components),
            "density": nx.density(graph) if graph.number_of_nodes() > 1 else 0.0
        }

        if isolated_nodes:
            logger.warning(f"Found {len(isolated_nodes)} isolated nodes in topology: {isolated_nodes}")

        return validation_result

    def compute_adjacency_matrix(
        self,
        graph: nx.DiGraph,
        weight_key: str = "weight"
    ) -> Tuple[np.ndarray, List[str]]:
        """Extract ordered row-stochastic or weighted adjacency matrix A and corresponding node IDs.

        Returns:
            (matrix, node_order_list)
        """
        nodes = list(graph.nodes())
        n = len(nodes)
        node_to_idx = {node: i for i, node in enumerate(nodes)}

        adj_matrix = np.zeros((n, n), dtype=np.float64)

        for u, v in graph.edges():
            i = node_to_idx[u]
            j = node_to_idx[v]
            data = graph.get_edge_data(u, v) or {}
            w = float(data.get(weight_key, 1.0))
            adj_matrix[i, j] = w

        return adj_matrix, nodes

    def to_cytoscape_elements(self, graph: nx.DiGraph) -> Dict[str, Any]:
        """Convert NetworkX DiGraph into Cytoscape.js JSON format for frontend rendering."""
        cytoscape_nodes = []
        for node_id in graph.nodes():
            node_data = graph.nodes[node_id]
            props = dict(node_data)
            label = props.pop("label", node_id)
            node_type = props.pop("type", "service")
            status = props.pop("status", "healthy")
            anomaly_score = float(props.pop("anomaly_score", 0.0))

            cytoscape_nodes.append({
                "data": {
                    "id": node_id,
                    "label": label,
                    "type": node_type,
                    "status": status,
                    "anomaly_score": anomaly_score,
                    **props
                }
            })

        cytoscape_edges = []
        for u, v in graph.edges():
            edge_id = f"e-{u}->{v}"
            data = graph.get_edge_data(u, v) or {}
            props = dict(data)
            weight = float(props.pop("weight", 1.0))

            cytoscape_edges.append({
                "data": {
                    "id": edge_id,
                    "source": u,
                    "target": v,
                    "weight": weight,
                    **props
                }
            })

        return {
            "elements": {
                "nodes": cytoscape_nodes,
                "edges": cytoscape_edges
            }
        }
