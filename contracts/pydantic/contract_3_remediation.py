"""Contract 3: Governed Agentic Diagnostics & SLA Liability API Models.

Served by Person C to the Dashboard / OSS Operations.
POST /api/rca/diagnose-and-remediate
Frozen at Week 0.
"""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field, ConfigDict
from .contract_2_rca_analysis import RCAResponse


class ActorContextItem(BaseModel):
    model_config = ConfigDict(extra="forbid")

    actor_id: str = Field(..., description="Legal/operational actor identifier e.g. MNO-Core-Operator, Cloud-Infra-Provider")
    service: str = Field(..., description="Service or component managed by this actor e.g. amf-01")
    mrc_usd: float = Field(..., ge=0.0, description="Monthly Recurring Charge for this service in USD")


class DiagnoseAndRemediateRequest(BaseModel):
    """Contract 3: POST /api/rca/diagnose-and-remediate Request."""
    model_config = ConfigDict(extra="forbid")

    incident_id: str = Field(..., description="Incident identifier")
    rca_analysis: RCAResponse = Field(..., description="Contract 2 RCA response payload")
    actor_context: List[ActorContextItem] = Field(..., description="Contractual actor context and MRC pricing")
    require_hitl_approval: bool = Field(default=True, description="Whether to require human-in-the-loop sign-off")


class Verdict(BaseModel):
    model_config = ConfigDict(extra="forbid")

    root_cause_service: str = Field(..., description="Primary root cause component or service")
    domain: str = Field(..., description="Domain of primary fault e.g. 5g_core_sba")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence score of verdict")
    synthesized_code_hash: str = Field(..., description="SHA-256 hash of synthesized graph traversal code")


class SLALiabilityAttribution(BaseModel):
    model_config = ConfigDict(extra="forbid")

    culpable_actor: str = Field(..., description="Actor responsible for the SLA violation")
    dynamic_trust_score: float = Field(..., ge=0.0, le=1.0, description="LASM calculated dynamic trust score")
    mrc_penalty_percentage: float = Field(..., ge=0.0, le=100.0, description="Contractual penalty percentage (e.g., 10.0, 20.0, 30.0)")
    mrc_financial_penalty_usd: float = Field(..., ge=0.0, description="Calculated financial penalty in USD (mrc_usd * penalty %)")


class RemediationPlan(BaseModel):
    model_config = ConfigDict(extra="forbid")

    action: str = Field(..., description="Remediation action e.g. horizontal_scale_and_pool_patch")
    target: str = Field(..., description="Target component or resource e.g. amf-01")
    parameters: Dict[str, Any] = Field(default_factory=dict, description="Action parameters e.g. replicas, pool size")
    state_estimation_compliance: str = Field(..., description="AGORA compliance verdict e.g. 'PASSED (Live Prometheus queried at T-2s)'")
    hitl_approval_status: str = Field(..., description="Status e.g. PENDING_OPERATOR_SIGNATURE, APPROVED, REJECTED, EXECUTED")
    approval_token: Optional[str] = Field(default=None, description="Cryptographic single-use token if pending approval")


class DiagnoseAndRemediateResponse(BaseModel):
    """Contract 3: POST /api/rca/diagnose-and-remediate Response."""
    model_config = ConfigDict(extra="forbid")

    incident_id: str = Field(..., description="Incident identifier")
    verdict: Verdict = Field(..., description="Root cause verdict with confidence and code hash")
    fault_propagation_chain: List[str] = Field(..., description="Step-by-step causal chain of failure propagation")
    sla_liability_attribution: SLALiabilityAttribution = Field(..., description="LASM SLA liability and MRC penalty attribution")
    remediation_plan: RemediationPlan = Field(..., description="Actionable remediation plan with AGORA compliance")
