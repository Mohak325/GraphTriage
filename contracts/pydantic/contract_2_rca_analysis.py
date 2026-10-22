"""Contract 2: RCA Analysis & Disambiguation API Models.

Served by Person B, consumed by Person C.
POST /api/rca/analyze
Frozen at Week 0.
"""

from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field, ConfigDict


class TimeWindow(BaseModel):
    model_config = ConfigDict(extra="forbid")

    start: datetime = Field(..., description="Start of incident analysis window")
    end: datetime = Field(..., description="End of incident analysis window")


class RCARequest(BaseModel):
    """Contract 2: POST /api/rca/analyze Request."""
    model_config = ConfigDict(extra="forbid")

    incident_id: str = Field(..., description="Unique incident identifier e.g. INC-2026-0042")
    time_window: TimeWindow = Field(..., description="Time window for telemetry analysis")
    affected_components: List[str] = Field(..., description="Components exhibiting anomalous KPIs or alarms")
    telemetry_s3_path: str = Field(..., description="S3 URI path to raw and normalized telemetry files")
    trigger_active_probing: bool = Field(default=True, description="Whether to trigger ConfExp active probing")


class XAIAttribution(BaseModel):
    model_config = ConfigDict(extra="forbid")

    kpi: str = Field(..., description="KPI or feature name")
    shap_value: float = Field(..., description="SHAP feature attribution value")


class RankedCause(BaseModel):
    model_config = ConfigDict(extra="forbid")

    component_id: str = Field(..., description="Component identified as likely root cause")
    fault_type: str = Field(..., description="Specific classified fault or failure mode")
    domain: str = Field(..., description="Network or cloud domain e.g. 5g_core_sba, telecom_transport")
    anomaly_score: float = Field(..., ge=0.0, le=1.0, description="Normalized anomaly score")
    method: str = Field(..., description="Detection method e.g. TeleGAN-Core + MNSUAD, DTFL_transGNN")
    xai_attributions: Optional[List[XAIAttribution]] = Field(default=None, description="SHAP feature importance")


class PcapVerification(BaseModel):
    model_config = ConfigDict(extra="forbid")

    protocol_violation: bool = Field(..., description="True if signaling protocol flow was violated")
    deviating_frame: Optional[int] = Field(default=None, description="Exact frame number where deviation occurred")
    procedure: Optional[str] = Field(default=None, description="3GPP procedure name")
    cause_code: Optional[str] = Field(default=None, description="3GPP or HTTP/2 cause code")


class ActiveProbingResults(BaseModel):
    model_config = ConfigDict(extra="forbid")

    probes_executed: List[str] = Field(default_factory=list, description="Diagnostic probes executed")
    isolated_cv: str = Field(..., description="Isolated Configuration Variable root cause")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Diagnostic probing confidence")


class TopologyNode(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: str = Field(..., description="Component identifier")
    status: str = Field(..., description="Component state e.g. anomalous, degraded, healthy")


class TopologyEdge(BaseModel):
    model_config = ConfigDict(extra="forbid")

    source: str = Field(..., description="Source node id")
    target: str = Field(..., description="Target node id")
    latency_ms: float = Field(..., description="Observed network link latency in milliseconds")


class TopologySubgraph(BaseModel):
    model_config = ConfigDict(extra="forbid")

    nodes: List[TopologyNode] = Field(..., description="Nodes involved in failure subgraph")
    edges: List[TopologyEdge] = Field(..., description="Directed edges in failure subgraph")


class RCAResponse(BaseModel):
    """Contract 2: POST /api/rca/analyze Response."""
    model_config = ConfigDict(extra="forbid")

    incident_id: str = Field(..., description="Incident identifier")
    ranked_causes: List[RankedCause] = Field(..., description="Ranked candidate root causes")
    pcap_verification: Optional[PcapVerification] = Field(default=None, description="Golden Flow verification")
    active_probing_results: Optional[ActiveProbingResults] = Field(default=None, description="ConfExp probing outcome")
    topology_subgraph: TopologySubgraph = Field(..., description="Local failure propagation subgraph")
