"""Dashboard support routes: incident list, details, topology, SHAP, and active probe trigger."""

import json
from pathlib import Path
from typing import Any, Dict, List, Optional
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from backend.app.api.routes_rca import INCIDENT_STORE
from backend.app.api.websocket import ws_manager
from backend.knowledge_base.validator import validate_kb
from backend.app.core.config import settings
from backend.app.core.security import hitl_manager

router = APIRouter(prefix="/api/dashboard", tags=["Operator Dashboard Support"])

FIXTURES_DIR = settings.FIXTURES_DIR


def ensure_fixtures_loaded():
    """Pre-populates INCIDENT_STORE from static JSON fixtures if empty."""
    if len(INCIDENT_STORE) < 5:
        # Load reference INC-2026-0042
        ref_file = FIXTURES_DIR / "contract_2_inc_2026_0042.json"
        if ref_file.exists():
            with open(ref_file, "r") as f:
                data = json.load(f)
                inc_id = data.get("incident_id", "INC-2026-0042")
                if inc_id not in INCIDENT_STORE:
                    ref_token = hitl_manager.generate_token(
                        incident_id=inc_id,
                        action="horizontal_scale_and_pool_patch",
                        target="amf-01",
                        parameters={"replicas": 4, "client_pool_size": 2048},
                    )
                    INCIDENT_STORE[inc_id] = {
                        "incident_id": inc_id,
                        "rca_analysis": data,
                        "response": {
                            "incident_id": inc_id,
                            "verdict": {
                                "root_cause_service": "amf-01",
                                "domain": "5g_core_sba",
                                "confidence": 0.962,
                                "synthesized_code_hash": "sha256:7f3b8a1c9e42d76f8b0e35a12cd68f44e1987ba42f89c0213d56e719ab45c321",
                            },
                            "fault_propagation_chain": [
                                "Misconfigured SBI client pool on amf-01",
                                "Frame 23: Registration Reject (Congestion) triggered",
                                "HTTP/2 stream multiplexing queue starvation across AMF-SMF link",
                                "Downstream packet drop on upf-edge-3",
                                "SLA breach: PDU Session Setup Latency > 250ms",
                            ],
                            "sla_liability_attribution": {
                                "culpable_actor": "MNO-Core-Operator",
                                "dynamic_trust_score": 0.42,
                                "mrc_penalty_percentage": 20.0,
                                "mrc_financial_penalty_usd": 30000.00,
                            },
                            "remediation_plan": {
                                "action": "horizontal_scale_and_pool_patch",
                                "target": "amf-01",
                                "parameters": {"replicas": 4, "client_pool_size": 2048},
                                "state_estimation_compliance": "PASSED (Live Prometheus queried at T-2s)",
                                "hitl_approval_status": "PENDING_OPERATOR_SIGNATURE",
                                "approval_token": ref_token,
                            },
                        },
                    }

        # Load scenarios 1 to 5
        scenario_files = [
            ("scenario_1_transport.json", "INC-2026-0043", "router-core-2", "telecom_transport", 0.955, "Optical Carrier Switch", "Cloud-Infra-Provider", 0.72, 10.0, 8500.0),
            ("scenario_2_k8s_cnf.json", "INC-2026-0044", "pod-db-redis", "kubernetes_cnf", 0.968, "Patch Memory Cgroup", "Cloud-Infra-Provider", 0.25, 30.0, 25500.0),
            ("scenario_3_database.json", "INC-2026-0045", "db-pg-cluster", "data_service", 0.938, "Deploy PgBouncer Pooler", "Cloud-Infra-Provider", 0.55, 20.0, 17000.0),
            ("scenario_4_vnf_crash.json", "INC-2026-0046", "smf-02", "5g_core_sba", 0.975, "Restart PFCP & Resync", "MNO-Core-Operator", 0.18, 30.0, 45000.0),
            ("scenario_5_multi_actor.json", "INC-2026-0047", "k8s-worker-node-14", "kubernetes_cnf", 0.961, "CFS Quota Unpinning", "Cloud-Infra-Provider", 0.38, 20.0, 17000.0),
        ]
        for fname, inc_id, comp, dom, conf, act, actor, trust, pen, fine in scenario_files:
            fpath = FIXTURES_DIR / fname
            if fpath.exists() and inc_id not in INCIDENT_STORE:
                with open(fpath, "r") as f:
                    s_data = json.load(f)
                    scen_token = hitl_manager.generate_token(
                        incident_id=inc_id,
                        action=act,
                        target=comp,
                        parameters={"target": comp, "action": act},
                    )
                    INCIDENT_STORE[inc_id] = {
                        "incident_id": inc_id,
                        "rca_analysis": s_data,
                        "response": {
                            "incident_id": inc_id,
                            "verdict": {
                                "root_cause_service": comp,
                                "domain": dom,
                                "confidence": conf,
                                "synthesized_code_hash": f"sha256:hash_{inc_id.lower().replace('-', '_')}",
                            },
                            "fault_propagation_chain": [
                                f"Root failure triggered on {comp}",
                                f"Anomalous telemetry detected in domain {dom}",
                                f"SLA latency degraded on downstream services",
                            ],
                            "sla_liability_attribution": {
                                "culpable_actor": actor,
                                "dynamic_trust_score": trust,
                                "mrc_penalty_percentage": pen,
                                "mrc_financial_penalty_usd": fine,
                            },
                            "remediation_plan": {
                                "action": act,
                                "target": comp,
                                "parameters": {"target": comp, "action": act},
                                "state_estimation_compliance": "PASSED (Live Prometheus queried at T-2s)",
                                "hitl_approval_status": "PENDING_OPERATOR_SIGNATURE",
                                "approval_token": scen_token,
                            },
                        },
                    }



class ProbeTriggerRequest(BaseModel):
    incident_id: str = Field(..., description="Target incident ID")
    probe_type: str = Field(default="http2_ping_nrf", description="Diagnostic probe type to execute")


@router.get("/incidents", summary="List all active incidents with severity and status")
async def list_incidents() -> List[Dict[str, Any]]:
    ensure_fixtures_loaded()
    results = []
    for inc_id, item in INCIDENT_STORE.items():
        resp = item.get("response", {})
        verdict = resp.get("verdict", {})
        rem = resp.get("remediation_plan", {})
        sla = resp.get("sla_liability_attribution", {})
        results.append({
            "incident_id": inc_id,
            "root_cause_service": verdict.get("root_cause_service", "Unknown"),
            "domain": verdict.get("domain", "5g_core_sba"),
            "confidence": verdict.get("confidence", 0.95),
            "hitl_approval_status": rem.get("hitl_approval_status", "PENDING_OPERATOR_SIGNATURE"),
            "culpable_actor": sla.get("culpable_actor", "MNO-Core-Operator"),
            "financial_penalty_usd": sla.get("mrc_financial_penalty_usd", 0.0),
        })
    return results


@router.get("/incidents/{incident_id}", summary="Get full incident diagnostic, topology, and SHAP data")
async def get_incident_details(incident_id: str) -> Dict[str, Any]:
    ensure_fixtures_loaded()
    if incident_id not in INCIDENT_STORE:
        raise HTTPException(status_code=404, detail="Incident not found")
    return INCIDENT_STORE[incident_id]


@router.post("/probes/trigger", summary="ConfExp: Trigger Active Diagnostic Probing")
async def trigger_active_probe(payload: ProbeTriggerRequest) -> Dict[str, Any]:
    """Simulates Paper 12 (ConfExp) diagnostic test selection and CV confidence update."""
    ensure_fixtures_loaded()
    inc_id = payload.incident_id
    if inc_id not in INCIDENT_STORE:
        raise HTTPException(status_code=404, detail="Incident not found")

    probe_result = {
        "incident_id": inc_id,
        "probe_executed": payload.probe_type,
        "round_trip_latency_ms": 12.4,
        "isolated_configuration_variable": "amf.sbi.client_pool_size",
        "prior_confidence": 0.88,
        "posterior_confidence": 0.985,
        "probe_status": "CONVERGED",
    }

    # Broadcast probe execution to dashboard via WebSocket
    await ws_manager.broadcast({
        "event": "PROBE_EXECUTED",
        "incident_id": inc_id,
        "data": probe_result,
    })

    return probe_result


@router.get("/rules", summary="Get telecom failure rules from knowledge base")
async def get_knowledge_base_rules() -> Dict[str, Any]:
    kb = validate_kb()
    return {
        "total_rules": len(kb.rules),
        "rules": [r.model_dump() for r in kb.rules],
    }
