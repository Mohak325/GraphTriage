from __future__ import annotations
from typing import Any, Literal
from pydantic import BaseModel, Field
from typing_extensions import TypedDict
import enum

class AgentStatus(str, enum.Enum):
    IDLE = "IDLE"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"

class NodeData(BaseModel):
    node_id: str
    service_name: str
    node_type: str
    properties: dict[str, Any] = Field(default_factory=dict)
    anomaly_score: float = 0.0

class EdgeData(BaseModel):
    source: str
    target: str
    relationship: str
    properties: dict[str, Any] = Field(default_factory=dict)

class SubgraphData(BaseModel):
    nodes: list[NodeData]
    edges: list[EdgeData]
    center_node: str
    depth: int = 2

class MetricDataPoint(BaseModel):
    timestamp: str
    service_name: str
    metric_name: str
    value: float
    is_anomalous: bool = False

class TraceSpan(BaseModel):
    trace_id: str
    span_id: str
    parent_span_id: str | None = None
    service_name: str
    operation: str
    duration_ms: float
    status: str
    timestamp: str

class IncidentData(BaseModel):
    incident_id: str
    telemetry_window_minutes: int = 30
    timestamp: str
    affected_services: list[str] = Field(default_factory=list)
    description: str = ""

class NavigatorResult(BaseModel):
    suspicious_nodes: list[str]
    fault_scores: dict[str, float]
    traversal_path: list[str]
    localized_subgraph: SubgraphData
    reasoning: str

class CounterfactualResult(BaseModel):
    question: str
    expected_evidence: str
    actual_finding: str
    passed: bool

class DiagnosisResult(BaseModel):
    root_cause_node: str
    confidence: float = Field(ge=0.0, le=1.0)
    evidence_chain: list[str]
    remediation: list[str]
    reasoning: str

class VerificationResult(BaseModel):
    verdict: Literal['ACCEPT', 'REJECT']
    confidence: float = Field(ge=0.0, le=1.0)
    counterfactual_results: list[CounterfactualResult]
    rejection_reason: str = ""
    rejection_feedback: str = ""

class RCAOutput(BaseModel):
    rca_id: str
    incident_id: str
    root_cause_node: str
    confidence: float
    evidence_chain: list[str]
    counterfactual_results: list[CounterfactualResult]
    remediation: list[str]
    iterations: int
    status: Literal['confirmed', 'best_effort', 'failed']

class TriageState(TypedDict, total=False):
    incident: dict
    topology_nodes: list[dict]
    topology_edges: list[dict]
    metrics: list[dict]
    traces: list[dict]
    logs: list[str]
    navigator_result: dict | None
    diagnosis_result: dict | None
    verification_result: dict | None
    rejection_feedback: str
    iteration: int
    max_iterations: int
    status: str
    agent_updates: list[dict]
    final_output: dict | None
