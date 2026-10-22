---
name: telecom-rca-framework
description: >
  Skill for building an Intelligent Root Cause Analysis (RCA) Framework for Telecom Cloud Services.
  Covers cross-layer telemetry collection & SOMP hygiene, contamination-resilient ML (MNSUAD),
  adversarial 5GC detection (TeleGAN-Core), digital twin SFC localization (DTFL), deterministic
  signaling verification (Golden Flow), active diagnostic probing (ConfExp), self-improving
  agentic code-synthesis (TN-AutoRCA on TN-RCA530), Model Context Protocol (MCP) tool calling,
  and multi-actor SLA liability attribution (LASM) on AWS Cloud.
---

# Intelligent RCA Framework for Telecom Cloud Services

## Overview

This skill provides comprehensive architectural, engineering, and empirical guidance for developing an **Intelligent Root Cause Analysis (RCA) Framework** tailored for modern **Telecom Cloud Services** (5G SBA, Kubernetes CNFs, VNFs, and Multi-Cloud Continuum). Grounded in **15 peer-reviewed research papers (2023–2026)**, the framework addresses high-dimensional telemetry drift, up to 5% training data contamination, class imbalance, and LLM tool hallucinations.

## When to Activate This Skill

Activate this skill when:
- Designing or implementing telecom/cloud incident diagnosis and root cause analysis pipelines.
- Implementing telemetry hygiene, 3-layer KPI filtering, or Service-Oriented Metric Preprocessing (SOMP).
- Building weakly-supervised anomaly detectors resilient to data contamination (MNSUAD, TeleGAN-Core).
- Constructing Digital Twin-assisted GNNs (DTFL), Spatio-Temporal GNNs, or Dual-Branch CNN-Transformers.
- Implementing deterministic protocol-level call-flow verifiers for 5GC PCAP signaling (Golden Flow).
- Implementing active diagnostic probing engines (ConfExp) across Configuration Variables (CVs).
- Developing agentic LLM diagnostics using Model Context Protocol (MCP) or self-improving code synthesis (TN-AutoRCA).
- Calculating dynamic trust scores and multi-actor Monthly Recurring Charge (MRC) liability penalties (LASM).
- Benchmarking on **RCAEval** (735 cases) or **TN-RCA530** (530 telecom base station cases).

---

## 4-Stage Operational Reference Pipeline

```
Stage 1: Telemetry Hygiene & SOMP Standardization
  - Layer 1: Shannon Entropy filter (tau1=0.05, removes ~87.93% static series)
  - Layer 2: Stochastic time-series decomposition noise filter (-0.16% volatile noise)
  - Layer 3: Pearson cross-correlation consolidation (tau3=0.95, removes 28%-71% duplicates)
  - SOMP: Counter reset safety (x'_t = x_t - x_{t-1}) and mean/median gauge pooling

Stage 2: Contamination-Aware Online Detection
  - MNSUAD: DAGMM teacher (eta1,eta2,eta3) + Transformer-MAE & DevNet student (resilient to 5% contamination)
  - TeleGAN-Core: BiLSTM Dual-Autoencoder GAN with critic reconstruction gap penalty
  - Golden Flow + SVM: Wireshark JSON extraction, deterministic 3GPP state verification (100% PCAP accuracy)

Stage 3: Topological & Active Disambiguation
  - DTFL: 3-layer Digital Twin (Physical <-> SFC-Twin) + transGNN (BERT + GCN) + BDF-FL search (+13% accuracy)
  - Spatio-Temporal GNN: Invocation graph attention + dual-branch CNN-Transformer with dynamic KPI gating (cap 60%)
  - ConfExp: Active diagnostic probing over 2D CV relevance matrix; updates confidence levels c_j

Stage 4: Governed Agentic Remediation & SLA Liability
  - TN-AutoRCA: Evaluate-analyze-repair loop with contrastive feedback synthesizing graph-traversal code (91.79% F1)
  - Model Context Protocol (MCP): Structured AAL schemas over NWDAF, K8s, Prometheus (100% extraction, <0.9% overhead)
  - Safety & Compliance: AGORA state-estimation-before-actuation compliance + Human-in-the-Loop (HITL) gate
  - LASM Analysis Service: Dynamic trust scoring; 10%, 20%, 30% MRC penalty attribution
```

---

## Normalized Event Schema (Contract 1)

All telemetry events MUST conform to this schema:

```json
{
  "timestamp": "ISO-8601",
  "source_domain": "telecom_transport | 5g_core_sba | kubernetes_cnf | data_service",
  "source_component": "string (e.g., amf-01, smf-02, router-edge-4)",
  "event_type": "metric | log | alarm | pcap_frame | trace",
  "severity": "critical | major | minor | warning | info",
  "metric_name": "string | null",
  "metric_value_raw": "float | null",
  "metric_value_somp_delta": "float | null",
  "counter_reset_flag": "boolean",
  "log_message": "string | null",
  "trace_id": "string | null",
  "pcap_metadata": {
    "frame_number": "int | null",
    "protocol": "string | null",
    "procedure": "string | null",
    "message_type": "string | null"
  },
  "metadata": {
    "tenant_id": "string",
    "cluster_id": "string",
    "kpi_filter_passed": true
  }
}
```

---

## AWS Service Mapping

| Component | AWS Service | Implementation Detail |
|---|---|---|
| **Event Bus** | Amazon MSK | Multi-broker Apache Kafka for cross-domain event streaming |
| **Real-time Ingestion** | Amazon Kinesis Data Streams | Ingests 5GC PM counters, logs, and PCAP streams ($\ge 25,000$ evt/s) |
| **Data Lake** | Amazon S3 | Parquet storage partitioned by domain, date, and incident ID |
| **KPI Hygiene & SOMP** | AWS Glue / Lambda | Implements Shannon entropy, Pearson correlation, and SOMP deltas |
| **Time-Series Store** | Amazon Timestream | High-throughput query engine for SOMP normalized metrics |
| **Log & Alarm Index** | Amazon OpenSearch | Full-text search over 5GC NF logs and Wireshark PCAP frames |
| **Topology & Twin DB** | Amazon Neptune | Property graph (Gremlin) representing SFC-Twin and physical links |
| **Vector Knowledge Store** | RDS PostgreSQL + pgvector | Chunked ETSI NFV-MANO SOPs and 3GPP technical standards |
| **Contamination & ML** | Amazon SageMaker | Hosting MNSUAD, TeleGAN-Core, DTFL transGNN, and ST-GNN endpoints |
| **Agentic AI & Meta-Loop** | Amazon Bedrock | Claude 3.5 Sonnet executing TAIA, NFVAgent, and TN-AutoRCA code synthesis |
| **Agent Tool Protocol** | MCP Telemetry Server | FastAPI JSON-RPC service exposing Prometheus, K8s, and NWDAF APIs |
| **Pipeline Orchestrator** | AWS Step Functions | Express Workflows coordinating ML, probing, agent, and LASM steps |
| **Remediation & Autoscaling**| EventBridge + SSM | Automated runbooks executing VNF scaling and pod migration ($<18$s) |
| **Operator Portal** | Amplify + CloudFront | React 18 dashboard with D3.js Digital Twin topology and HITL modal |

---

## Datasets and Benchmarks

1. **TN-RCA530 Benchmark (Paper 7 - ICLR 2026)**:
   - 530 real telecom base station operational scenarios (94.5% Difficult) featuring overlapping alarm storms.
   - Evaluates self-improving agentic code-synthesis loops (targets $\ge 90\%$ harmonic mean F1).
2. **RCAEval Benchmark (WWW 2025 - arXiv:2412.17015)**:
   - 735 microservice failure cases across 3 distinct topologies with metrics, logs, traces, and ground truth.
   - Evaluates cross-modal ranking, Top-K accuracy ($\ge 82\%$ Top-1), MRR ($\ge 0.88$), and MAP@5.
3. **Vodafone NFV Production Dataset (Paper 1 - IEEE TMC 2025)**:
   - 11-country European NFV infrastructure dataset containing up to 5% unlabeled anomalous contamination.
4. **ENCQOR 5G Testbed Dataset (Paper 4 - IEEE Access 2026)**:
   - Cloud-native 5G Core SBA telemetry evaluating SOMP and TeleGAN-Core.

---

## 15 Research Papers (2023–2026 Reference Guide)

When working on specific framework components, reference the corresponding academic paper:

- **Paper 1 (Johari et al., IEEE TMC 2025)**: MNSUAD — DAGMM teacher pseudo-labeling, Transformer-MAE + DevNet student under 5% contamination, XAI localization (Mask/Cluster Permutation, SHAP).
- **Paper 2 (Guo et al., IEEE TCC 2023)**: DTFL — 3-layer Digital Twin with controlled fault injection, transGNN (BERT + GCN), and BDF-FL search.
- **Paper 3 (Anser et al., IEEE TNSM 2025)**: LASM Analysis Service — dynamic trust scoring and 10%–30% Monthly Recurring Charge (MRC) SLA penalty attribution.
- **Paper 4 (Issa et al., IEEE Access 2026)**: TeleGAN-Core — Service-Oriented Metric Preprocessing (SOMP) with counter reset safety and BiLSTM Dual-Autoencoder GAN with critic gap penalty.
- **Paper 5 (Panek et al., IEEE ICC Wksps 2025)**: TAIA — modular multi-agent AI assistant, logical decomposition, Prometheus closed-loop re-evaluation, Human-in-the-Loop (HITL).
- **Paper 6 (Woo & Woo, IEEE/IFIP CNSM 2025)**: NFVAgent — RAG LLM agent integrated with ETSI NFV-MANO for resilient failure recovery without fine-tuning.
- **Paper 7 (Wu et al., ICLR 2026 / arXiv:2507.18190)**: TN-AutoRCA & TN-RCA530 — 530-case telecom alarm benchmark + evaluate-analyze-repair loop synthesizing executable graph-traversal code (elevates Gemini from 58.99% to 91.79% F1).
- **Paper 8 (Enz et al., IEEE ICC Wksps 2024)**: MALEAF — ML-driven container localization and multi-class fault classification (CPU, RAM, network) across edge-cloud continuum.
- **Paper 9 (Heeb et al., ACM SAC 2023)**: IoMiRCA — cross-tier dependency and telemetry correlation between IoT edge gateways and 5G core microservices.
- **Paper 10 (Wang et al., IEEE CRESS 2025/2026)**: Two-Stage Multi-Source RCA — coarse anomaly screening + cross-modal correlation of NF text logs, packet traffic, and container metrics.
- **Paper 11 (Isaac et al. / Jarrah et al., 2024/2025)**: Golden Flow + SVM + GenAI — Wireshark JSON extraction, deterministic 3GPP call-flow verifier, protocol-grouped SVM, domain-tuned LLM (100% PCAP detection).
- **Paper 12 (Koushki et al., JNSM 2025)**: ConfExp — active diagnostic probing over 2D CV relevance matrix; greedy test selection and dynamic confidence updates.
- **Paper 13 (Wang et al., IEEE OJ-COMS 2024)**: XAI for 6G Diagnostics — SHAP, LIME, LRP, and Counterfactual Explanations for diagnosing physical faults and erroneous black-box AI control actions.
- **Paper 14 (Chen, Wang, Yin et al., IJNM 2025/2026)**: MCP-Diag & NIKA — LangGraph ReAct agents using Model Context Protocol (MCP) over NWDAF, INT, and Prometheus (100% extraction, <0.9% overhead).
- **Paper 15 (Frontiers in AI 2025 & MDPI Appl. Sci. 2026)**: Spatio-Temporal Attention GNN & Dual-Branch CNN-Transformer with dynamic KPI gating (capped at 60%).

---

## Team Distribution & Interface Boundaries

### Person A: Data Pipeline & Infrastructure Engineer (Layers 1-2 & Hygiene)
- Owns AWS infrastructure (IaC), MSK, Kinesis, Glue, Timestream, OpenSearch, Neptune, DynamoDB, RDS pgvector.
- Implements 3-layer KPI filtering (Shannon entropy, noise decomposition, cross-correlation) eliminating $\ge 88\%$ redundant metrics.
- Implements SOMP delta increments ($x_t'=x_t-x_{t-1}$) with counter reset safety.
- Implements Wireshark PCAP-to-JSON extractor and Model Context Protocol (MCP) telemetry server.
- Ingests RCAEval, TN-RCA530, ENCQOR 5G, and Vodafone NFV into normalized S3 buckets.

### Person B: ML/AI Engine & Digital Twin Developer (Layers 3-4, Minus LLM)
- Implements MNSUAD (DAGMM teacher + Transformer-MAE & DevNet student) handling 5% data contamination.
- Implements TeleGAN-Core (BiLSTM Dual-Autoencoder GAN with critic gap penalty).
- Implements DTFL Digital Twin (transGNN + BDF-FL breadth/depth search).
- Implements Golden Flow state machine + Protocol-Grouped SVM (100% PCAP fault detection).
- Implements ConfExp active diagnostic probing engine (2D CV matrix + greedy test selection).
- Implements Dual-Branch CNN-Transformer with learnable positional embeddings and dynamic KPI gating.
- Packages models into SageMaker multi-model endpoint serving Contract 2 API (`POST /api/rca/analyze`).

### Person C: Governed Agentic AI, SLA Liability, & Dashboard Developer (Layers 4-5)
- Implements TAIA modular multi-agent orchestrator with step-by-step cognitive decomposition.
- Implements NFVAgent RAG retrieval over ETSI NFV-MANO SOPs and 3GPP standards.
- Implements TN-AutoRCA evaluate-analyze-repair loop synthesizing executable graph-traversal code.
- Implements Model Context Protocol (MCP) client in the Agent Abstraction Layer (AAL).
- Enforces AGORA state-estimation-before-actuation compliance and Human-in-the-Loop (HITL) cryptographic approval.
- Implements LASM Analysis Service adjudicating 10%–30% Monthly Recurring Charge (MRC) SLA penalties.
- Builds React 18 operator portal (Amplify + D3.js Digital Twin topology + SHAP charts + HITL dialogs).

---

## Coding Guidelines

### Python (Backend, ML, & Data)
- Python 3.11+ with strict type hinting (`mypy --strict`).
- Use `pydantic` v2 for all contract validations and payload serialization.
- Use `structlog` for structured, contextual JSON logging.
- Pytest with minimum 80% coverage on core preprocessing, ML evaluation, and agent tools.

### TypeScript (Frontend Portal)
- React 18 with functional hooks and strict TypeScript (`strict: true`).
- Vite build tooling.
- D3.js for Digital Twin graph and topology visualizations; Recharts for SOMP metric timeseries.
- AWS Amplify SDK for Cognito authentication and WebSocket subscriptions.

---

## Target Metrics Checklist

| Metric | Target | Verification Method |
|---|---|---|
| **TN-RCA530 F1-Score** | $\ge 90.0\%$ | Auto-RCA code synthesis on 530 base station cases |
| **RCAEval Top-1 Accuracy** | $\ge 82.0\%$ | Leave-one-system-out cross-validation on 735 cases |
| **RCAEval Top-3 Accuracy** | $\ge 92.0\%$ | Top-3 ranked root-cause services |
| **Mean Reciprocal Rank (MRR)** | $\ge 0.88$ | Mean reciprocal rank across all test cases |
| **MAP@5** | $\ge 0.85$ | Mean average precision at 5 |
| **PCAP Signaling Detection** | $100.0\%$ | Golden Flow + SVM on Registration/PDU PCAPs |
| **Contamination Robustness** | $\ge +20.0\%$ F1 gain | MNSUAD vs. vanilla autoencoder under 5% contamination |
| **DTFL SFC Accuracy Gain** | $\ge +12.0\%$ | DTFL vs. non-twin transGNN on dynamic SFCs |
| **KPI Compression Ratio** | $\ge 88.0\%$ | 3-layer daily KPI filter volume reduction |
| **MCP Tool Calling Overhead** | $< 0.9\%$ latency, 100% extraction | MCP-Diag test suite across 150 incidents |
| **Self-Healing Latency** | $< 18$ seconds | Automated VNF scaling / NSM path switch execution |
| **MTTR Reduction** | $\ge 70.0\%$ | Compared to manual NOC operator baseline |
