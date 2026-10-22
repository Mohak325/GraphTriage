# Implementation Plan

## Intelligent Root Cause Analysis (RCA) Framework for Telecom Cloud Services

### Work Distribution: 3 Independent Team Members (Aligned with 2023–2026 Research Report)

| Field        | Value                                                              |
| ------------ | ------------------------------------------------------------------ |
| **Version**  | 2.0 (Grounded in 15 Peer-Reviewed Papers & Empirical Advances)     |
| **Date**     | 2026-10-15                                                         |
| **Duration** | 12 Weeks                                                           |
| **Target**   | Carrier-Grade Deployment on AWS Cloud                              |

---

## Design Principle: Total Independence

The project is structured so that each of the three team members develops, tests, and validates their subsystem **completely independently** without blocking each other. Integration occurs in Week 11 through strictly typed **Interface Contracts** (JSON Schemas, OpenAPI REST specifications, and Model Context Protocol schemas). Each member owns their dedicated AWS resources, code repositories, and isolated test suites.

```
+--------------------------------------------------------------------------------------------------------+
|                                    WEEK 0: AGREED INTERFACE CONTRACTS                                   |
+-----------------------------------+-----------------------------------+--------------------------------+
| Contract 1: Normalized Schema     | Contract 2: RCA Analysis API      | Contract 3: Agentic Diagnostics|
| (Person A produces -> B & C read) | (Person B serves -> Person C calls)| (Person C serves -> Dashboard) |
+-----------------------------------+-----------------------------------+--------------------------------+
                                                    |
         +------------------------------------------+------------------------------------------+
         |                                          |                                          |
         v                                          v                                          v
+------------------------+         +--------------------------------+         +--------------------------+
|       PERSON A         |         |            PERSON B            |         |         PERSON C         |
| Data Pipeline & Infra  |         |      ML / AI Engine & Twin     |         | Agentic AI & Dashboard   |
| (Layers 1-2 & Hygiene) |         | (Contamination, GNN, Probing)  |         | (MCP, AutoRCA, Liability)|
+------------------------+         +--------------------------------+         +--------------------------+
| - 3-Layer KPI Filter   |         | - MNSUAD (5% Contamination)    |         | - TAIA Multi-Agent Orchestrator|
| - SOMP Reset Normalizer|         | - TeleGAN-Core (Dual-AE GAN)   |         | - NFVAgent RAG (NFV-MANO)|
| - PCAP Wireshark Ingest|         | - DTFL Digital Twin (transGNN) |         | - TN-AutoRCA Code Synth  |
| - MCP Telemetry Server |         | - Golden Flow & SVM (100% PCAP)|         | - MCP Agent Client (AAL) |
| - MSK, Glue, Timestream|         | - ConfExp Active Probing Engine|         | - LASM SLA MRC Liability |
| - Benchmark Ingestion  |         | - Dual-Branch CNN-Transformer  |         | - AGORA State-Before-Act |
|   (RCAEval, TN-RCA530) |         | - SageMaker Real-Time Endpoint |         | - React 18 / HITL Portal |
+------------------------+         +--------------------------------+         +--------------------------+
         |                                          |                                          |
         +------------------------------------------+------------------------------------------+
                                                    |
                                    WEEK 11: INTEGRATION SPRINT
                                    WEEK 12: DEMO & BENCHMARK REPORT
```

---

## Shared Interface Contracts (Frozen at Week 0)

### Contract 1: Normalized Telemetry Event & SOMP Schema (Person A Produces)

```json
{
  "timestamp": "ISO-8601 (e.g., 2026-10-15T14:30:00.000Z)",
  "source_domain": "telecom_transport | 5g_core_sba | kubernetes_cnf | data_service",
  "source_component": "string (e.g., amf-01, smf-02, router-edge-4, pod-db-redis)",
  "event_type": "metric | log | alarm | pcap_frame | trace",
  "severity": "critical | major | minor | warning | info",
  "metric_name": "string | null",
  "metric_value_raw": "float | null",
  "metric_value_somp_delta": "float | null",
  "counter_reset_flag": "boolean (true if counter wrapped or reset)",
  "log_message": "string | null",
  "trace_id": "string | null",
  "pcap_metadata": {
    "frame_number": "int | null",
    "protocol": "string | null (e.g., NGAP, NAS-5GS, HTTP2)",
    "procedure": "string | null (e.g., Registration, PDU_Session_Establishment)",
    "message_type": "string | null (e.g., RegistrationReject, 504_GatewayTimeout)"
  },
  "metadata": {
    "tenant_id": "string",
    "cluster_id": "string",
    "kpi_filter_passed": true
  }
}
```

### Contract 2: RCA Analysis & Disambiguation API (Person B Serves)

`POST /api/rca/analyze`

**Request:**
```json
{
  "incident_id": "INC-2026-0042",
  "time_window": {"start": "2026-10-15T14:00:00Z", "end": "2026-10-15T14:15:00Z"},
  "affected_components": ["amf-01", "upf-edge-3", "router-core-2"],
  "telemetry_s3_path": "s3://rca-telemetry-lake/incidents/INC-2026-0042/",
  "trigger_active_probing": true
}
```

**Response:**
```json
{
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
    },
    {
      "component_id": "router-core-2",
      "fault_type": "BGP Route Flapping / Packet Drop",
      "domain": "telecom_transport",
      "anomaly_score": 0.681,
      "method": "DTFL_transGNN"
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
    "nodes": [{"id": "amf-01", "status": "anomalous"}, {"id": "upf-edge-3", "status": "degraded"}],
    "edges": [{"source": "amf-01", "target": "upf-edge-3", "latency_ms": 142.5}]
  }
}
```

### Contract 3: Governed Agentic Diagnostics & SLA Liability API (Person C Serves)

`POST /api/rca/diagnose-and-remediate`

**Request:** (Consumes Contract 2 output + S3 telemetry)
```json
{
  "incident_id": "INC-2026-0042",
  "rca_analysis": { /* Contract 2 Response */ },
  "actor_context": [
    {"actor_id": "MNO-Core-Operator", "service": "amf-01", "mrc_usd": 150000},
    {"actor_id": "Cloud-Infra-Provider", "service": "k8s-worker-node-14", "mrc_usd": 85000}
  ],
  "require_hitl_approval": true
}
```

**Response:**
```json
{
  "incident_id": "INC-2026-0042",
  "verdict": {
    "root_cause_service": "amf-01",
    "domain": "5g_core_sba",
    "confidence": 0.962,
    "synthesized_code_hash": "sha256:7f3b8..."
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
    "mrc_financial_penalty_usd": 30000.00
  },
  "remediation_plan": {
    "action": "horizontal_scale_and_pool_patch",
    "target": "amf-01",
    "parameters": {"replicas": 4, "client_pool_size": 2048},
    "state_estimation_compliance": "PASSED (Live Prometheus queried at T-2s)",
    "hitl_approval_status": "PENDING_OPERATOR_SIGNATURE"
  }
}
```

---

## Person A: Data Pipeline & Infrastructure Engineer

### Scope & Architecture Layers
- **Layers Owned**: Layer 1 (Multi-Domain Telemetry Collection) & Layer 2 (Ingestion, Hygiene, and Normalization).
- **Core Research Papers Grounding Person A**:
  - **IEEE ISCC 2025**: Three-Layer KPI Filtering Pipeline (Shannon Entropy $\tau_1=0.05$, Noise Decomposition, Pearson Cross-Correlation $\tau_3=0.95$).
  - **Paper 4 (TeleGAN-Core)**: Service-Oriented Metric Preprocessing (SOMP) with monotonic counter interval increments ($x_t'=x_t-x_{t-1}$).
  - **Paper 11 (Golden Flow)**: Wireshark JSON extraction for 5GC signaling PCAPs.
  - **Paper 14 (MCP-Diag)**: Model Context Protocol (MCP) telemetry server for Prometheus, Kubernetes, and 3GPP NWDAF interfaces.
- **AWS Infrastructure**: Kinesis Data Streams, MSK (Managed Kafka), Glue, S3 Data Lake, Timestream, OpenSearch, Neptune, DynamoDB, RDS PostgreSQL (pgvector), Lambda, IAM, CloudWatch.

### Detailed 12-Week Roadmap for Person A

| Week | Milestone | Deliverable | Exit Criteria |
|---|---|---|---|
| **1** | **Infra as Code (IaC)** | Terraform/CDK templates for MSK, Kinesis, Timestream, OpenSearch, Neptune, and S3. | All AWS resources provisioned in sandbox; IAM roles locked down. |
| **2** | **Benchmark Ingestion** | Ingestion pipeline for **RCAEval** (735 cases) and **TN-RCA530** (530 telecom base station cases) into S3. | All 1,265 benchmark incidents parsed and indexed in raw format. |
| **3** | **Production Datasets** | Ingest **Vodafone NFV** (11 countries, 5% contamination) and **ENCQOR 5G** SBA telemetry. | Baseline datasets stored in parquet format with metadata tags. |
| **4** | **3-Layer KPI Filter** | AWS Glue/Lambda implementing Shannon entropy ($\tau_1=0.05$), noise decomposition, and Pearson correlation ($\tau_3=0.95$). | Eliminates $\ge 88\%$ redundant KPIs on 5GC datasets without losing anomaly signals. |
| **5** | **SOMP Normalization Engine** | Lambda/Glue module converting cumulative counters into interval deltas ($x_t'=x_t-x_{t-1}$) with reset safety and mean/median gauge pooling. | Zero negative spikes on counter resets; output conforms to Contract 1. |
| **6** | **PCAP Extraction Engine** | Automated Wireshark JSON extractor for 5GC Registration, PDU Session, and Deregistration signaling PCAPs. | Extracts frame-by-frame protocol headers and status codes into OpenSearch. |
| **7** | **Topology Graph Loader** | AWS Glue script loading service-dependency and telecom transport graphs into Amazon Neptune (Gremlin/SPARQL). | Neptune graph queryable; represents 100% of benchmark topology nodes/links. |
| **8** | **Model Context Protocol (MCP) Server** | Lightweight FastAPI MCP Server exposing read-only Prometheus, K8s, and NWDAF queries via JSON-RPC. | Passes MCP client inspection test; returns structured telemetry tools. |
| **9** | **Vector Store & SOP Indexing** | RDS PostgreSQL + pgvector loaded with chunked ETSI NFV-MANO specs and 3GPP technical standards. | Semantic similarity search returns relevant standard sections in $<50$ms. |
| **10** | **Dataset Publishing Sprint** | Publish finalized, cleaned datasets to shared S3 buckets for Person B and Person C with README schema docs. | Person B and Person C can successfully query all datasets. |
| **11** | **Scale & Stress Testing** | Ingestion stress test: 25,000 events/second sustained over 4 hours through Kinesis/MSK to Timestream. | Zero message drops; DLQ remains empty; latency $<1.5$s. |
| **12** | **Operational Handover** | CloudWatch dashboard, automated cost-optimizer (S3 Glacier lifecycle), and handover documentation. | Handover package complete. |

---

## Person B: ML/AI Engine & Digital Twin Developer

### Scope & Architecture Layers
- **Layers Owned**: Layer 3 (Cross-Domain Correlation & Contamination-Resilient Detection) & Layer 4 (Topological Graph Learning, PCAP Verification, Active Probing).
- **Core Research Papers Grounding Person B**:
  - **Paper 1 (MNSUAD)**: DAGMM teacher ($\eta_1,\eta_2,\eta_3$) + Transformer Masked Autoencoder (MAE) + DevNet student under 5% data contamination.
  - **Paper 4 (TeleGAN-Core)**: BiLSTM Dual-Autoencoder GAN with critic reconstruction gap penalty ($L_G - L_C$).
  - **Paper 2 (DTFL)**: 3-layer Digital Twin (Physical, SFC-Twin, Service) with transGNN and Breadth/Depth-First Failure Localization (BDF-FL).
  - **Paper 11 (Golden Flow)**: Deterministic 3GPP call-flow state verifier + protocol-grouped SVM.
  - **Paper 12 (ConfExp)**: Active diagnostic probing test selection over 2D CV relevance matrix.
  - **Paper 15 (ST-GNN)**: Dual-Branch CNN-Transformer with learnable positional embeddings and dynamic KPI gating.
  - **Papers 1 & 13**: Post-hoc XAI (Mask Permutation, Cluster Permutation, SHAP, and Counterfactual Explanations).
- **AWS Infrastructure**: SageMaker Studio, SageMaker Training Jobs, SageMaker Real-Time Endpoints, Lambda.

### Detailed 12-Week Roadmap for Person B

| Week | Milestone | Deliverable | Exit Criteria |
|---|---|---|---|
| **1** | **Exploratory Data Analysis** | SageMaker notebooks analyzing RCAEval, TN-RCA530, and Vodafone NFV telemetry distributions. | Anomaly characteristics, class imbalance, and graph topologies mapped. |
| **2** | **Feature Engineering** | Multi-modal feature extractor: SOMP delta metrics, log frequency vectors, and trace latency percentiles. | Feature matrices saved as parquet for all 1,265 benchmark cases. |
| **3** | **MNSUAD Implementation** | Teacher DAGMM pseudo-labeling cascade + Transformer-MAE representation learner + DevNet student. | Achieves $\ge +20\%$ F1 gain over baseline on 5% contaminated Vodafone data. |
| **4** | **TeleGAN-Core Implementation** | BiLSTM Generator and Critic Dual-Autoencoder GAN with critic gap penalty ($L_{gap} = L_G - L_C$). | Effectively detects multivariate 5GC anomalies without false alert fatigue. |
| **5** | **Golden Flow PCAP Verifier** | Deterministic 3GPP signaling state-machine + Protocol-Grouped SVM on Wireshark JSON frames. | 100% detection accuracy on faulty Registration and PDU Session PCAPs. |
| **6** | **DTFL Digital Twin & transGNN** | 3-layer Digital Twin failure injection module + BERT text embedding + Graph Convolutional Network (transGNN). | Outperforms non-twin baselines by $\ge 12\%$ accuracy on SFC failure cases. |
| **7** | **Dual-Branch CNN-Transformer** | Spatio-temporal model fusing 1D-CNN local temporal features with 2-head Transformer and dynamic KPI gating. | Gating caps single branch at 60%; superior F1 on non-uniform 5G recovery times. |
| **8** | **ConfExp Active Probing** | Diagnostic test selection algorithm (Algorithm 2) computing dynamic CV confidence updates ($c_j$). | Deterministically isolates root-cause misconfigurations across simulated DNS/firewall CVs. |
| **9** | **XAI Attribution Engine** | Integrated SHAP, Mask Permutation, and Counterfactual perturbation modules. | Generates local feature attributions and minimum corrective perturbations. |
| **10** | **SageMaker Endpoint Deployment** | Package models into a unified SageMaker multi-model endpoint implementing Contract 2 API. | Endpoint responds in $<1.8$s per incident request with full Contract 2 JSON. |
| **11** | **Comprehensive Benchmark** | Evaluate on RCAEval (735 cases) and TN-RCA530 (530 telecom cases); compute Top-1/3/5, MRR, MAP@5. | Meets target metrics: $\ge 82\%$ Top-1 on RCAEval; $\ge 90\%$ F1 on TN-RCA530. |
| **12** | **Model Cards & Documentation** | Detailed model cards, hyperparameter configs, inference benchmarks, and handover documentation. | Handover package complete. |

---

## Person C: Agentic AI, SLA Liability, & Dashboard Developer

### Scope & Architecture Layers
- **Layers Owned**: Layer 4 (Agentic Reasoning & Code Synthesis) & Layer 5 (Decision, Governance, SLA Liability, and Operator Portal).
- **Core Research Papers Grounding Person C**:
  - **Paper 7 (TN-AutoRCA)**: Evaluate-analyze-repair agentic loop synthesizing executable graph-traversal code with contrastive feedback.
  - **Paper 5 (TAIA)**: Modular multi-agent orchestrator (Infrastructure, CNF Lifecycle, Observability) with closed-loop Prometheus verification and HITL governance.
  - **Paper 6 (NFVAgent)**: RAG agent over ETSI NFV-MANO operational guidelines and vendor SOPs.
  - **Paper 14 (MCP-Diag & NIKA)**: LangGraph ReAct agent communicating via Model Context Protocol (MCP) for zero tool hallucinations.
  - **AGORA (IEEE Access 2025)**: Strict state-estimation-before-actuation compliance validation.
  - **Paper 3 (LASM Analysis Service)**: Dynamic trust scoring and 10%–30% Monthly Recurring Charge (MRC) penalty attribution.
- **AWS Infrastructure**: Amazon Bedrock (Claude 3.5 Sonnet), AWS Step Functions, API Gateway (REST + WebSocket), AWS Amplify, CloudFront, SNS, SES, EventBridge, Systems Manager.

### Detailed 12-Week Roadmap for Person C

| Week | Milestone | Deliverable | Exit Criteria |
|---|---|---|---|
| **1** | **Bedrock & MCP Setup** | Amazon Bedrock connection + LangGraph ReAct agent configured with MCP client over Person A's mock server. | Zero tool-call formatting errors; structured JSON response guaranteed. |
| **2** | **Domain Rules Knowledge Base** | YAML knowledge repository encoding 50+ telecom failure propagation rules and 3GPP spec mappings. | Rules validate across transport, core, cloud, and DB failure topologies. |
| **3** | **NFVAgent RAG Pipeline** | RAG retrieval module querying RDS pgvector for ETSI NFV-MANO SOPs and historical incident workflows. | RAG context improves diagnostic accuracy on unseen VNF crash scenarios. |
| **4** | **TN-AutoRCA Meta-Agent** | Self-improving evaluate-analyze-repair loop: prompts LLM to generate and repair Python graph-traversal code. | Boosts baseline Gemini/Claude alarm RCA F1 on sample difficult graphs by $\ge +25\%$. |
| **5** | **AGORA & HITL Guardrails** | Compliance interceptor validating state-estimation-before-actuation + cryptographic approval token generator. | Blocks any mutating tool call that lacks prior real-time telemetry verification. |
| **6** | **LASM SLA Liability Engine** | Algorithmic service calculating actor trust metrics and 10%, 20%, 30% MRC contractual penalties. | Correctly attributes financial liability across multi-tenant test cases CS1–CS8. |
| **7** | **Step Functions Orchestration** | AWS Step Functions state machine linking Person B's Contract 2 API, Bedrock agents, and LASM engine. | End-to-end execution completes in $<60$s using mock ML responses. |
| **8** | **React Dashboard v1** | Amplify React 18 application displaying active incidents, fault verdicts, and fault-propagation chains. | UI renders cleanly; responsive layout with dark-mode carrier NOC theme. |
| **9** | **Dashboard v2 (Advanced)** | D3.js Digital Twin topology visualizer, SHAP waterfall charts, ConfExp probe trigger, and MRC liability table. | Operator can interactively inspect graph hops and trigger active probes. |
| **10** | **HITL Portal & Runbooks** | Cryptographic approval modal in dashboard; EventBridge + Systems Manager automated remediation runbooks. | Operator click triggers AWS SSM document to simulate container scaling/migration. |
| **11** | **Full System Integration** | Replace mock ML endpoints with Person B's SageMaker endpoint and mock data with Person A's live AWS data. | Flawless end-to-end execution across 5 complex failure scenarios. |
| **12** | **Demonstration & Usability** | Live end-to-end demonstration, user guide, video walkthrough, and handover documentation. | Handover package complete. |

---

## Cross-Team Integration & Validation Schedule

```
Week 0: Contracts Frozen (Contract 1: Schema, Contract 2: ML API, Contract 3: Agentic API)
Weeks 1 - 10: Fully Independent Development & Unit Benchmarking
Week 11: Integration Sprint
  - Day 1: Person A publishes production S3 prefixes and Neptune endpoints.
  - Day 2: Person B links SageMaker inference pipelines to Person A's normalized datasets.
  - Day 3: Person C connects Step Functions and MCP clients to Person B's SageMaker API.
  - Day 4: End-to-End Execution: Ingest raw telemetry -> SOMP/Hygiene -> ML/Twin -> Agentic RCA -> Dashboard.
  - Day 5: Multi-actor SLA liability attribution and automated SSM self-healing verification.
Week 12: Final Review, Carrier Demo, and Research Documentation.
```

---

## Technical Stack & Libraries

```bash
# Common Core
Python 3.11+, boto3, pydantic, pytest, structlog

# Person A (Data Pipeline)
kafka-python, pyarrow, gremlinpython, opensearch-py, sentence-transformers, terraform

# Person B (ML / Twin Engine)
torch, torch-geometric, scikit-learn, networkx, dgl, shap, causal-learn, statsmodels

# Person C (Agentic AI & Dashboard)
anthropic, langgraph, mcp, fastapi, uvicorn, react 18, vite, tailwindcss, d3.js, recharts
```
