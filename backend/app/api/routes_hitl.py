"""HITL (Human-in-the-Loop) Governance API Routes.

Handles operator cryptographic approvals, rejections, and audit log inspection.
Upon valid approval, triggers SSM automation runbooks and updates incident state.
"""

from typing import Any, Dict, Optional
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field

from backend.app.core.security import hitl_manager
from backend.app.services.ssm_runbook_service import ssm_service
from backend.app.api.websocket import ws_manager
from backend.app.api.routes_rca import INCIDENT_STORE

router = APIRouter(prefix="/api/hitl", tags=["HITL Governance"])


class ApprovalRequest(BaseModel):
    incident_id: str = Field(..., description="Incident ID to approve")
    approval_token: str = Field(..., description="Cryptographic single-use token")
    operator_signature: str = Field(..., description="Operator signature e.g. NOC-ENG-49102-SIG")
    comments: Optional[str] = Field(default=None, description="Optional operational remarks")


class RejectionRequest(BaseModel):
    incident_id: str = Field(..., description="Incident ID to reject")
    approval_token: str = Field(..., description="Cryptographic single-use token")
    operator_signature: str = Field(..., description="Operator signature")
    reason: str = Field(..., description="Reason for rejecting remediation")


@router.post("/approve", summary="Approve remediation action with cryptographic signature")
async def approve_remediation(payload: ApprovalRequest) -> Dict[str, Any]:
    valid, message, token_payload = hitl_manager.verify_and_consume_token(
        token=payload.approval_token,
        operator_signature=payload.operator_signature,
        approve=True,
        comments=payload.comments,
    )
    if not valid or not token_payload:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=message,
        )

    # Dispatch to AWS Systems Manager Runbook automation
    doc_name = "scale_amf_service" if "amf" in token_payload.get("target", "") else "restart_vnf_container"
    execution = await ssm_service.execute_runbook(
        incident_id=payload.incident_id,
        document_name=doc_name,
        target=token_payload.get("target", ""),
        parameters=token_payload.get("parameters", {}),
        operator_signature=payload.operator_signature,
    )

    # Update in-memory incident status if present
    if payload.incident_id in INCIDENT_STORE:
        INCIDENT_STORE[payload.incident_id]["response"]["remediation_plan"]["hitl_approval_status"] = "APPROVED"

    # Broadcast WebSocket update
    await ws_manager.broadcast({
        "event": "HITL_APPROVED",
        "incident_id": payload.incident_id,
        "operator_signature": payload.operator_signature,
        "execution": execution,
    })

    return {
        "status": "APPROVED",
        "message": message,
        "execution": execution,
    }


@router.post("/reject", summary="Reject remediation action")
async def reject_remediation(payload: RejectionRequest) -> Dict[str, Any]:
    valid, message, token_payload = hitl_manager.verify_and_consume_token(
        token=payload.approval_token,
        operator_signature=payload.operator_signature,
        approve=False,
        comments=payload.reason,
    )
    if not valid:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=message,
        )

    if payload.incident_id in INCIDENT_STORE:
        INCIDENT_STORE[payload.incident_id]["response"]["remediation_plan"]["hitl_approval_status"] = "REJECTED"

    await ws_manager.broadcast({
        "event": "HITL_REJECTED",
        "incident_id": payload.incident_id,
        "reason": payload.reason,
    })

    return {
        "status": "REJECTED",
        "message": message,
    }


@router.get("/audit", summary="Get immutable cryptographic audit trail")
async def get_audit_trail(incident_id: Optional[str] = None):
    return {
        "audit_trail": hitl_manager.get_audit_trail(incident_id=incident_id),
        "ssm_executions": ssm_service.get_executions(incident_id=incident_id),
    }
