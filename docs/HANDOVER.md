# Subsystem Handover Package (Person C)

## Intelligent Root Cause Analysis (RCA) Framework for Telecom Cloud Services
**Layer 4 (Agentic Reasoning & Code Synthesis) & Layer 5 (Governance, SLA Liability & Operator Portal)**

---

## 1. Summary of Deliverables Handed Over

| Deliverable ID | Component | File Path | Status |
|---|---|---|---|
| **DEL-C1** | LangGraph ReAct MCP Agent | `backend/app/agents/react_mcp_agent.py` | Complete (0% hallucinated tools) |
| **DEL-C2** | Telecom Domain Rules KB | `backend/knowledge_base/failure_rules.yaml` | Complete (52 rules validated across 4 domains) |
| **DEL-C3** | NFVAgent RAG Pipeline | `backend/app/agents/nfv_agent_rag.py` | Complete (ETSI NFV-MANO SOP retrieval + citations) |
| **DEL-C4** | TN-AutoRCA Meta-Agent | `backend/app/agents/tn_autorca_meta.py` | Complete (AST sandbox, SHA-256 hash, >=+25% F1) |
| **DEL-C5** | TAIA Orchestrator | `backend/app/agents/taia_orchestrator.py` | Complete (Infra, CNF, Observability sub-agents) |
| **DEL-C6** | AGORA Compliance Guardrail | `backend/app/services/agora_interceptor.py` | Complete (State-before-act verification) |
| **DEL-C7** | HITL Governance Engine | `backend/app/core/security.py` | Complete (HMAC-SHA256 single-use tokens + audit) |
| **DEL-C8** | LASM SLA Liability Engine | `backend/app/services/lasm_engine.py` | Complete (Dynamic trust, MRC tiers, CS1-CS8) |
| **DEL-C9** | AWS Step Functions ASL | `infra/step_functions/rca_orchestration.asl.json` | Complete (<60s end-to-end execution) |
| **DEL-C10** | Contract 3 FastAPI API | `backend/app/api/routes_rca.py` | Complete (REST + WebSocket feeds) |
| **DEL-C11** | React 18 Carrier Dashboard | `frontend/src/` | Complete (D3 Digital Twin, SHAP, HITL portal) |
| **DEL-C12** | SSM & EventBridge Runbooks| `infra/ssm_runbooks/` | Complete (AMF scaling & container recycle) |

---

## 2. Week 11 Cross-Team Integration Instructions

To connect Person C to live Person A (Data Pipeline) and Person B (SageMaker ML Engine):

### Step 1: Update `.env` Configuration
Change only three variables in `.env`:
```ini
# Switch from static fixtures to live AWS endpoints
USE_FIXTURES=false

# Switch from offline mock reasoning to live AWS Bedrock Claude 3.5 Sonnet
MOCK_BEDROCK=false

# Point to Person A's live MCP Telemetry Server (Week 11 Day 1)
PERSON_A_MCP_URL=http://<PERSON_A_MCP_ALB_ENDPOINT>:8080

# Point to Person B's live SageMaker RCA Endpoint (Week 11 Day 2)
PERSON_B_RCA_URL=http://<PERSON_B_SAGEMAKER_ENDPOINT>:8000

# Point to Person A's RDS PostgreSQL pgvector instance (Week 11 Day 1)
VECTOR_DB_URL=postgresql://<DB_USER>:<DB_PASSWORD>@<RDS_ENDPOINT>:5432/vectordb
```

### Step 2: Zero Code Changes Required
Because Person C strictly relies on `MCPTelemetryClientInterface`, `RCAClientInterface`, and `VectorStoreRAGClientInterface`, the factory automatically injects `LiveMCPTelemetryClient`, `LiveRCAClient`, and `LiveVectorStoreRAGClient` upon inspecting `USE_FIXTURES=false`.
Zero backend code modifications are needed for live integration.
