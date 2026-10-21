"""
Contract definitions for Telecom Cloud RCA Framework.
- Contract 1: Normalized Telemetry Event & SOMP Schema (Person A produces -> B & C consume)
- Contract 2: RCA Analysis & Disambiguation API Models (Person B serves -> C calls)
- Contract 3: Governed Agentic Diagnostics & SLA Liability API Models (Person C serves -> Dashboard)
"""

from datetime import datetime
from typing import Optional, Literal, List, Dict, Any
from pydantic import BaseModel, Field, ConfigDict


# ==========================================
# CONTRACT 1: NORMALIZED TELEMETRY EVENT
# ==========================================

class PCAPMetadata(BaseModel):
    """Signaling and call-flow metadata extracted from 5GC PCAP / Wireshark frames."""
    model_config = ConfigDict(extra="allow")

    frame_number: Optional[int] = Field(default=None, description="Wireshark frame number")
    protocol: Optional[str] = Field(default=None, description="e.g. NGAP, NAS-5GS, HTTP2, PFCP")
    procedure: Optional[str] = Field(default=None, description="e.g. Registration, PDU_Session_Establishment, Deregistration")
    message_type: Optional[str] = Field(default=None, description="e.g. RegistrationReject, 504_GatewayTimeout, RegistrationRequest")
    source_ip: Optional[str] = None
    dest_ip: Optional[str] = None
    status_code: Optional[int] = None
    cause_code: Optional[str] = None


class EventMetadata(BaseModel):
    """Operational metadata, tenant fencing, and pipeline audit tags."""
    model_config = ConfigDict(extra="allow")

    tenant_id: str = Field(default="default-tenant", description="Tenant or slice identifier")
    cluster_id: str = Field(default="cluster-01", description="Kubernetes or Edge cluster identifier")
    kpi_filter_passed: bool = Field(default=True, description="Whether event passed 3-layer KPI filter")
    contamination_suspected: bool = Field(default=False, description="Flag for MNSUAD weakly supervised training")
    network_slice_id: Optional[str] = None
    datacenter_region: Optional[str] = None


class NormalizedTelemetryEvent(BaseModel):
    """
    Contract 1: Carrier-Grade Normalized Telemetry Event.
    Standardized across 5GC SBA, Kubernetes CNF, transport networks, and data layers.
    """
    model_config = ConfigDict(extra="allow")

    timestamp: datetime = Field(
        default_factory=datetime.utcnow,
        description="ISO-8601 UTC timestamp"
    )
    source_domain: Literal[
        "telecom_transport",
        "5g_core_sba",
        "kubernetes_cnf",
        "data_service"
    ] = Field(description="Telemetry source domain")

    source_component: str = Field(
        description="Culprit or reporting component, e.g. amf-01, smf-02, router-edge-4, pod-db-redis"
    )
    event_type: Literal[
        "metric",
        "log",
        "alarm",
        "pcap_frame",
        "trace"
    ] = Field(description="Event classification")

    severity: Literal[
        "critical",
        "major",
        "minor",
        "warning",
        "info"
    ] = Field(default="info", description="Severity gradation")

    # Metrics and SOMP delta attributes
    metric_name: Optional[str] = Field(default=None, description="Standardized KPI / gauge / counter name")
    metric_value_raw: Optional[float] = Field(default=None, description="Raw unnormalized observed metric")
    metric_value_somp_delta: Optional[float] = Field(default=None, description="SOMP interval delta x'_t = x_t - x_{t-1}")
    counter_reset_flag: bool = Field(default=False, description="True if monotonic counter wrapped or reset")

    # Unstructured Log / Alarm attributes
    log_message: Optional[str] = Field(default=None, description="Unstructured log or alarm synopsis")
    alarm_id: Optional[str] = Field(default=None, description="Unique telecom alarm code")

    # Distributed Tracing attributes
    trace_id: Optional[str] = Field(default=None, description="W3C / Jaeger trace ID")
    span_id: Optional[str] = None
    parent_span_id: Optional[str] = None

    # Signaling & PCAP
    pcap_metadata: Optional[PCAPMetadata] = None

    # Pipeline & Tenant Metadata
    metadata: EventMetadata = Field(default_factory=EventMetadata)


# ==========================================
# CONTRACT 2: RCA ANALYSIS & DISAMBIGUATION API
# ==========================================

class TimeWindow(BaseModel):
    start: datetime
    end: datetime


class XAIAttribution(BaseModel):
    kpi: str
    shap_value: float


class RankedCause(BaseModel):
    component_id: str
    fault_type: str
    domain: str
    anomaly_score: float
    method: str
    xai_attributions: List[XAIAttribution] = Field(default_factory=list)


class PCAPVerification(BaseModel):
    protocol_violation: bool
    deviating_frame: Optional[int] = None
    procedure: Optional[str] = None
    cause_code: Optional[str] = None


class ActiveProbingResults(BaseModel):
    probes_executed: List[str] = Field(default_factory=list)
    isolated_cv: Optional[str] = None
    confidence: float = 0.0


class GraphNode(BaseModel):
    id: str
    status: str = "normal"
    component_type: Optional[str] = None


class GraphEdge(BaseModel):
    source: str
    target: str
    latency_ms: Optional[float] = None
    call_count: Optional[int] = None


class TopologySubgraph(BaseModel):
    nodes: List[GraphNode] = Field(default_factory=list)
    edges: List[GraphEdge] = Field(default_factory=list)


class RCARequest(BaseModel):
    incident_id: str
    time_window: TimeWindow
    affected_components: List[str]
    telemetry_s3_path: Optional[str] = None
    trigger_active_probing: bool = True


class RCAResponse(BaseModel):
    incident_id: str
    ranked_causes: List[RankedCause]
    pcap_verification: Optional[PCAPVerification] = None
    active_probing_results: Optional[ActiveProbingResults] = None
    topology_subgraph: Optional[TopologySubgraph] = None


# ==========================================
# CONTRACT 3: AGENTIC DIAGNOSTICS & SLA LIABILITY
# ==========================================

class ActorContext(BaseModel):
    actor_id: str
    service: str
    mrc_usd: float


class RemediateRequest(BaseModel):
    incident_id: str
    rca_analysis: RCAResponse
    actor_context: List[ActorContext] = Field(default_factory=list)
    require_hitl_approval: bool = True


class RCAVerdict(BaseModel):
    root_cause_service: str
    domain: str
    confidence: float
    synthesized_code_hash: Optional[str] = None


class SLALiabilityAttribution(BaseModel):
    culpable_actor: str
    dynamic_trust_score: float
    mrc_penalty_percentage: float
    mrc_financial_penalty_usd: float


class RemediationPlan(BaseModel):
    action: str
    target: str
    parameters: Dict[str, Any] = Field(default_factory=dict)
    state_estimation_compliance: str = "PASSED"
    hitl_approval_status: str = "PENDING_OPERATOR_SIGNATURE"


class RemediateResponse(BaseModel):
    incident_id: str
    verdict: RCAVerdict
    fault_propagation_chain: List[str]
    sla_liability_attribution: SLALiabilityAttribution
    remediation_plan: RemediationPlan
