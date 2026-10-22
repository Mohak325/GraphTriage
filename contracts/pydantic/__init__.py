"""Shared Interface Contracts (Frozen at Week 0).

Contains Pydantic v2 schemas for:
- Contract 1: Normalized Telemetry Event & SOMP Schema (Person A produces -> B & C read)
- Contract 2: RCA Analysis & Disambiguation API (Person B serves -> Person C calls)
- Contract 3: Governed Agentic Diagnostics & SLA Liability API (Person C serves -> Dashboard)
"""

from .contract_1_telemetry import (
    NormalizedTelemetryEvent,
    SourceDomain,
    EventType,
    Severity,
    PcapMetadata,
    EventMetadata,
)
from .contract_2_rca_analysis import (
    RCARequest,
    RCAResponse,
    RankedCause,
    XAIAttribution,
    PcapVerification,
    ActiveProbingResults,
    TopologySubgraph,
    TopologyNode,
    TopologyEdge,
    TimeWindow,
)
from .contract_3_remediation import (
    DiagnoseAndRemediateRequest,
    DiagnoseAndRemediateResponse,
    ActorContextItem,
    Verdict,
    SLALiabilityAttribution,
    RemediationPlan,
)

__all__ = [
    "NormalizedTelemetryEvent",
    "SourceDomain",
    "EventType",
    "Severity",
    "PcapMetadata",
    "EventMetadata",
    "RCARequest",
    "RCAResponse",
    "RankedCause",
    "XAIAttribution",
    "PcapVerification",
    "ActiveProbingResults",
    "TopologySubgraph",
    "TopologyNode",
    "TopologyEdge",
    "TimeWindow",
    "DiagnoseAndRemediateRequest",
    "DiagnoseAndRemediateResponse",
    "ActorContextItem",
    "Verdict",
    "SLALiabilityAttribution",
    "RemediationPlan",
]
