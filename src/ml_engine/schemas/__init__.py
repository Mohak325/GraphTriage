"""Contract 1 and Contract 2 schemas for ML engine inputs and outputs."""
from src.ml_engine.schemas.contract1_input import (
    TelemetryEvent,
    PcapMetadata,
    EventMetadata,
)
from src.ml_engine.schemas.contract2_output import (
    TimeWindow,
    RcaAnalysisRequest,
    XaiAttribution,
    RankedCause,
    PcapVerification,
    ActiveProbingResults,
    TopologyNode,
    TopologyEdge,
    TopologySubgraph,
    RcaAnalysisResponse,
)

NormalizedTelemetryEvent = TelemetryEvent

__all__ = [
    "TelemetryEvent",
    "NormalizedTelemetryEvent",
    "PcapMetadata",
    "EventMetadata",
    "TimeWindow",
    "RcaAnalysisRequest",
    "XaiAttribution",
    "RankedCause",
    "PcapVerification",
    "ActiveProbingResults",
    "TopologyNode",
    "TopologyEdge",
    "TopologySubgraph",
    "RcaAnalysisResponse",
]
