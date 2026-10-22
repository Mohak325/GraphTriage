"""
Test: Service Invocation Graph Construction & BDF-FL Localization
Author: Sandarbh Gupta (24BIT0506) - Subsystem 2
"""

import pytest
import numpy as np
from src.ml_engine.data.rcaeval_loader import RcaEvalLoader
from src.ml_engine.models.graph.trace_graph_builder import TraceGraphBuilder
from src.ml_engine.models.graph.bdf_fl import BdfflSearch
from src.ml_engine.models.graph.trans_gnn import TransGNNModel


def test_rcaeval_graph_and_bdffl():
    loader = RcaEvalLoader()
    case = loader.create_mock_case(
        case_id="CASE-TT-001",
        system_name="train-ticket",
        root_cause_service="ts-order-service"
    )
    
    # 1. Build Invocation Graph from Traces
    builder = TraceGraphBuilder()
    graph = builder.build_from_traces_df(case.traces_df)
    
    assert graph.number_of_nodes() >= 3
    assert graph.has_edge("ts-ui-dashboard", "ts-order-service")
    assert graph.has_edge("ts-order-service", "ts-payment-service")
    
    # 2. Compute anomaly scores
    services = sorted(list(graph.nodes()))
    A_norm = builder.get_adjacency_matrix(services)
    
    # Simulate feature matrix where ts-order-service exhibits high metrics
    X = np.ones((len(services), 8)) * 0.2
    root_idx = services.index("ts-order-service")
    X[root_idx] = 2.5  # high anomaly features
    
    trans_gnn = TransGNNModel(in_dim=8, hidden_dim=16)
    y_sim = np.zeros(len(services))
    y_sim[root_idx] = 1.0
    trans_gnn.fit(X, A_norm, y_sim)
    
    scores = trans_gnn.predict_node_anomalies(X, A_norm)
    score_dict = {s: float(scores[i]) for i, s in enumerate(services)}
    
    # 3. BDF-FL Search
    search = BdfflSearch()
    ranked_causes = search.locate_root_cause(graph, score_dict)
    
    assert len(ranked_causes) > 0
    top_cause, top_score = ranked_causes[0]
    # The true root cause service should rank #1
    assert top_cause == "ts-order-service"
    print(f"\n[PASSED] BDF-FL successfully localized top root cause: {top_cause} (score={top_score:.3f})")
