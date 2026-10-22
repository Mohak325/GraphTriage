"""
Contract 2: RCA Analysis & Disambiguation API Schema
Author: Sandarbh Gupta (24BIT0506) - Subsystem 2
"""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class TimeWindow(BaseModel):
    start: str
    end: str


class RcaAnalysisRequest(BaseModel):
    incident_id: str
    time_window: Optional[TimeWindow] = None
    affected_components: List[str] = Field(default_factory=list)
    telemetry_local_path: Optional[str] = None
    telemetry_s3_path: Optional[str] = None
    trigger_active_probing: bool = True
    context: Dict[str, Any] = Field(default_factory=dict)


class XaiAttribution(BaseModel):
    kpi: str
    shap_value: float


class RankedCause(BaseModel):
    component_id: str
    fault_type: str
    domain: str
    anomaly_score: float
    method: str
    xai_attributions: List[XaiAttribution] = Field(default_factory=list)


class PcapVerification(BaseModel):
    protocol_violation: bool
    deviating_frame: Optional[int] = None
    procedure: Optional[str] = None
    cause_code: Optional[str] = None
    details: Optional[str] = None


class ActiveProbingResults(BaseModel):
    probes_executed: List[str] = Field(default_factory=list)
    isolated_cv: Optional[str] = None
    confidence: float = 0.0


class TopologyNode(BaseModel):
    id: str
    status: str = "normal"  # normal, anomalous, degraded
    component_type: Optional[str] = None


class TopologyEdge(BaseModel):
    source: str
    target: str
    latency_ms: Optional[float] = None
    error_rate: Optional[float] = None


class TopologySubgraph(BaseModel):
    nodes: List[TopologyNode] = Field(default_factory=list)
    edges: List[TopologyEdge] = Field(default_factory=list)


class RcaAnalysisResponse(BaseModel):
    incident_id: str
    status: str = "COMPLETED"
    ranked_causes: List[RankedCause] = Field(default_factory=list)
    pcap_verification: Optional[PcapVerification] = None
    active_probing_results: Optional[ActiveProbingResults] = None
    topology_subgraph: TopologySubgraph = Field(default_factory=TopologySubgraph)
    execution_time_ms: float = 0.0
