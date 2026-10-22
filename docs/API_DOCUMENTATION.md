# API Specification: Contract 3 & Operational Endpoints

**Service Title**: Intelligent Telecom Cloud RCA & SLA Liability Service (Person C)  
**Version**: 2.0.0  
**Protocols**: REST (JSON) • WebSocket (JSON-RPC)  
**OpenAPI Specification**: `contracts/openapi/contract_3_openapi.json`

---

## 1. Core Endpoints Summary

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/api/rca/diagnose-and-remediate` | **Contract 3**: Governed Agentic Diagnostics, LASM SLA Liability Attribution & Remediation Synthesis. |
| `POST` | `/api/hitl/approve` | Submit cryptographic operator signature to approve pending remediation. |
| `POST` | `/api/hitl/reject` | Reject pending remediation plan with operator remarks. |
| `GET` | `/api/hitl/audit` | Retrieve immutable cryptographic token audit trail and SSM execution log. |
| `GET` | `/api/dashboard/incidents` | List active incidents with status, domain, and financial penalties. |
| `GET` | `/api/dashboard/incidents/{id}` | Get full diagnostic dossier (Contract 2 RCA, D3 topology subgraph, SHAP values). |
| `POST` | `/api/dashboard/probes/trigger` | Trigger ConfExp active diagnostic probe against an isolated Configuration Variable (CV). |
| `GET` | `/api/dashboard/rules` | Inspect 50+ telecom failure propagation rules in the knowledge base. |
| `GET` | `/healthz` | System health check and runtime mode flags. |
| `WS` | `/ws/incidents` | Real-time WebSocket event feed for carrier NOC dashboards. |

---

## 2. Contract 3 Specification

### `POST /api/rca/diagnose-and-remediate`

#### Request Payload
```json
{
  "incident_id": "INC-2026-0042",
  "rca_analysis": {
    "incident_id": "INC-2026-0042",
    "ranked_causes": [
      {
        "component_id": "amf-01",
        "fault_type": "Registration Congestion / Thread Pool Exhaustion",
        "domain": "5g_core_sba",
        "anomaly_score": 0.942,
        "method": "TeleGAN-Core + MNSUAD",
        "xai_attributions": [
          {"kpi": "amf_active_ngap_contexts", "shap_value": 0.42},
          {"kpi": "amf_cpu_saturation", "shap_value": 0.35}
        ]
      }
    ],
    "pcap_verification": {
      "protocol_violation": true,
      "deviating_frame": 23,
      "procedure": "User Registration",
      "cause_code": "5GS_Congestion"
    },
    "active_probing_results": {
      "probes_executed": ["dns_srv_query", "http2_ping_nrf"],
      "isolated_cv": "amf.sbi.client_pool_size",
      "confidence": 0.985
    },
    "topology_subgraph": {
      "nodes": [
        {"id": "amf-01", "status": "anomalous"},
        {"id": "upf-edge-3", "status": "degraded"}
      ],
      "edges": [
        {"source": "amf-01", "target": "upf-edge-3", "latency_ms": 142.5}
      ]
    }
  },
  "actor_context": [
    {"actor_id": "MNO-Core-Operator", "service": "amf-01", "mrc_usd": 150000.0},
    {"actor_id": "Cloud-Infra-Provider", "service": "k8s-worker-node-14", "mrc_usd": 85000.0}
  ],
  "require_hitl_approval": true
}
```

#### Response Payload (Frozen Week 0 Reference Match)
```json
{
  "incident_id": "INC-2026-0042",
  "verdict": {
    "root_cause_service": "amf-01",
    "domain": "5g_core_sba",
    "confidence": 0.962,
    "synthesized_code_hash": "sha256:7f3b8a1c9e42d76f8b0e35a12cd68f44e1987ba42f89c0213d56e719ab45c321"
  },
  "fault_propagation_chain": [
    "Misconfigured SBI client pool on amf-01",
    "Frame 23: Registration Reject (Congestion) triggered",
    "HTTP/2 stream multiplexing queue starvation across AMF-SMF link",
    "Downstream packet drop on upf-edge-3",
    "SLA breach: PDU Session Setup Latency > 250ms"
  ],
  "sla_liability_attribution": {
    "culpable_actor": "MNO-Core-Operator",
    "dynamic_trust_score": 0.42,
    "mrc_penalty_percentage": 20.0,
    "mrc_financial_penalty_usd": 30000.0
  },
  "remediation_plan": {
    "action": "horizontal_scale_and_pool_patch",
    "target": "amf-01",
    "parameters": {
      "replicas": 4,
      "client_pool_size": 2048
    },
    "state_estimation_compliance": "PASSED (Live Prometheus queried at T-2s)",
    "hitl_approval_status": "PENDING_OPERATOR_SIGNATURE",
    "approval_token": "eyJwYXlsb2FkIjogeyJpbmNpZGVudF9pZCI6ICJJTkMtMjAyNi0wMDQyIi..."
  }
}
```

---

## 3. Human-in-the-Loop (HITL) Endpoints

### `POST /api/hitl/approve`
**Request:**
```json
{
  "incident_id": "INC-2026-0042",
  "approval_token": "eyJwYXlsb2FkIjogeyJpbmNpZGVudF9pZCI6ICJJTkMtMjAyNi0wMDQyIi...",
  "operator_signature": "NOC-STAFF-ENG-78901-ED25519",
  "comments": "Reviewed live Prometheus SBI queue depth. Action verified."
}
```
**Response (200 OK):**
```json
{
  "status": "APPROVED",
  "message": "Token successfully verified and APPROVED",
  "execution": {
    "execution_id": "exec-ssm-1792431452-amf01",
    "incident_id": "INC-2026-0042",
    "document_name": "scale_amf_service",
    "target": "amf-01",
    "parameters": {"replicas": 4, "client_pool_size": 2048},
    "operator_signature": "NOC-STAFF-ENG-78901-ED25519",
    "status": "SUCCESS",
    "duration_ms": 1420,
    "sns_notification_sent": true,
    "eventbridge_event_published": true
  }
}
```

---

## 4. WebSocket Feed (`/ws/incidents`)

Subscribes to live operational updates. The backend broadcasts messages matching:
```json
{
  "event": "INCIDENT_DIAGNOSED | HITL_APPROVED | HITL_REJECTED | PROBE_EXECUTED",
  "incident_id": "INC-2026-0042",
  "data": { /* event payload */ }
}
```
