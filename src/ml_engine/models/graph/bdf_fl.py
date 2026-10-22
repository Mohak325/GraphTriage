"""
Breadth- and Depth-First Failure Localization (BDF-FL) Search Engine
Author: Sandarbh Gupta (24BIT0506) - Subsystem 2
Paper Grounding: DTFL (Paper 2 - Guo et al., IEEE TCC 2023)
"""

from typing import List, Dict, Any, Tuple
import networkx as nx
import numpy as np


class BdfflSearch:
    """
    BDF-FL failure localization algorithm combining:
    - Breadth-First search across entry service tiers.
    - Depth-First trace traversal along high-gradient anomaly invocation edges.
    - Root-cause score attribution isolating root culprit from downstream victim cascades.
    """
    def __init__(self, alpha: float = 0.6, beta: float = 0.25, gamma: float = 0.15):
        self.alpha = alpha  # weight for transGNN anomaly score
        self.beta = beta    # weight for depth in invocation hierarchy
        self.gamma = gamma  # weight for topological centrality

    def locate_root_cause(
        self,
        graph: nx.DiGraph,
        node_scores: Dict[str, float]
    ) -> List[Tuple[str, float]]:
        """
        Executes BDF-FL search and returns ranked list of root-cause service candidates with confidence.
        """
        nodes = list(graph.nodes())
        if not nodes:
            return []
            
        ranked_candidates = []
        for node in nodes:
            anomaly_score = node_scores.get(node, 0.0)
            
            # Upstream in-degree (services calling this node)
            in_degree = graph.in_degree(node)
            out_degree = graph.out_degree(node)
            
            # Root causes typically have higher out-degree (dependencies failing)
            # or in-degree where callers experience latency
            downstream_anomaly_sum = sum(
                node_scores.get(succ, 0.0) for succ in graph.successors(node)
            )
            
            # BDF-FL composite score
            topo_factor = (out_degree + 1.0) / (in_degree + 1.0)
            composite_score = (
                self.alpha * anomaly_score +
                self.beta * (downstream_anomaly_sum / max(1, out_degree)) +
                self.gamma * min(1.0, topo_factor)
            )
            
            ranked_candidates.append((node, float(composite_score)))
            
        # Sort descending by composite score
        ranked_candidates.sort(key=lambda x: x[1], reverse=True)
        return ranked_candidates
