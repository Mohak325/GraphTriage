"""Graph neural networks and digital twin fault localization models."""
from src.ml_engine.models.graph.bdf_fl import BdfflSearch
from src.ml_engine.models.graph.trace_graph_builder import TraceGraphBuilder
from src.ml_engine.models.graph.trans_gnn import TransGNNModel

BDFFaultLocalizer = BdfflSearch
TransGNNLocalizer = TransGNNModel

__all__ = [
    "BdfflSearch",
    "BDFFaultLocalizer",
    "TraceGraphBuilder",
    "TransGNNModel",
    "TransGNNLocalizer",
]
