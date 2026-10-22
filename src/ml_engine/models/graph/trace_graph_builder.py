"""
Trace Dependency Graph Builder from OpenTelemetry Spans
Author: Sandarbh Gupta (24BIT0506) - Subsystem 2
"""

from typing import Dict, Any, List, Tuple
import networkx as nx
import pandas as pd
import numpy as np


class TraceGraphBuilder:
    """
    Constructs service dependency invocation graphs from OpenTelemetry distributed traces.
    """
    def __init__(self):
        self.graph = nx.DiGraph()

    def build_from_traces_df(self, traces_df: pd.DataFrame) -> nx.DiGraph:
        """
        Builds a directed call graph where edges represent caller -> callee service invocations.
        """
        self.graph.clear()
        
        # Build span_id to service mapping
        span_to_service = {}
        for _, row in traces_df.iterrows():
            span_to_service[row["span_id"]] = row["service_name"]
            if not self.graph.has_node(row["service_name"]):
                self.graph.add_node(row["service_name"], call_count=0, error_count=0)
                
        # Connect parent spans to child spans
        for _, row in traces_df.iterrows():
            callee = row["service_name"]
            parent_id = row.get("parent_span_id")
            
            # Increment node statistics
            self.graph.nodes[callee]["call_count"] += 1
            if row.get("status_code", 200) >= 500:
                self.graph.nodes[callee]["error_count"] += 1
                
            if parent_id and parent_id in span_to_service:
                caller = span_to_service[parent_id]
                if caller != callee:
                    if self.graph.has_edge(caller, callee):
                        self.graph[caller][callee]["weight"] += 1
                        self.graph[caller][callee]["latency_sum"] += row.get("duration_ms", 10.0)
                    else:
                        self.graph.add_edge(
                            caller,
                            callee,
                            weight=1,
                            latency_sum=row.get("duration_ms", 10.0)
                        )
                        
        return self.graph

    def get_adjacency_matrix(self, service_order: List[str]) -> np.ndarray:
        """
        Returns normalized adjacency matrix with self-loops: A_hat = D^{-1/2} (A + I) D^{-1/2}
        """
        n = len(service_order)
        A = np.zeros((n, n), dtype=float)
        
        service_idx = {s: i for i, s in enumerate(service_order)}
        for u, v in self.graph.edges():
            if u in service_idx and v in service_idx:
                i, j = service_idx[u], service_idx[v]
                A[i, j] = 1.0
                
        # Add self-loops
        A_tilde = A + np.eye(n)
        D = np.diag(np.sum(A_tilde, axis=1))
        D_inv_sqrt = np.linalg.inv(np.sqrt(D))
        A_norm = np.dot(np.dot(D_inv_sqrt, A_tilde), D_inv_sqrt)
        return A_norm
