# Intelligent Root Cause Analysis (RCA) Framework for Telecom Cloud Services

Grounded in **15 peer-reviewed research papers (2023–2026)**, this repository contains the carrier-grade Root Cause Analysis framework for Telecom Cloud Services (5G Core SBA, Kubernetes CNFs/VNFs, transport, and multi-cloud continuum).

---

## 👥 Contributors & Work Distribution

- **Person A (Data Pipeline & Infrastructure Engineer)**: Mohak Harsh — Telemetry Ingestion, 3-Layer Hygiene Pipeline, SOMP Normalization, Neptune Graph, PCAP Golden Flow extraction, MCP JSON-RPC Server, and Terraform IaC.
- **Person B (ML / AI Engine & Digital Twin Engineer)**: Sandarbh Gupta — Contamination-Resilient Anomaly Detection (MNSUAD & DAGMM), Adversarial 5GC Anomaly Detection (TeleGAN-Core), Spatio-Temporal Dual-Branch CNN-Transformer, Digital Twin Fault Localization (transGNN / BDF-FL), Active Diagnostic Probing (ConfExp), and Contract 2 FastAPI Server.

---

## 🏛️ System Architecture & Subsystems

```
[Raw Sources: 5GC SBA, K8s CNF, Transport, PCAPs, Benchmark Datasets]
                           │
                           ▼
          ┌──────────────────────────────────┐
          │  Stage 1: Telemetry Hygiene      │
          │  - Layer 1: Shannon Entropy      │
          │  - Layer 2: Noise Decomposition  │
          │  - Layer 3: Pearson Correlation  │
          │  - SOMP: Counter Reset Safety    │
          └──────────────────────────────────┘
                           │
                           ▼
          ┌──────────────────────────────────┐
          │  Stage 2: Multi-Model Storage    │
          │  - Amazon Timestream (Metrics)   │
          │  - Amazon OpenSearch (Logs/PCAP) │
          │  - Amazon Neptune (Graph Topology)│
          │  - RDS pgvector (SOP Embeddings) │
          └──────────────────────────────────┘
                           │
             ┌─────────────┴─────────────┐
             ▼                           ▼
┌──────────────────────────┐┌──────────────────────────────────┐
│ Stage 3: MCP Agent Layer ││ Stage 4: ML Engine & Twin (C2)   │
│ - FastAPI MCP JSON-RPC   ││ - MNSUAD (5% Noise Contamination)│
│ - Tools: Prometheus,     ││ - TeleGAN-Core (Dual-AE GAN)     │
│   NWDAF, K8s, Neptune    ││ - DTFL TransGNN & BDF-FL         │
│ - ETSI NFV RAG Store     ││ - Golden Flow Signaling + SVM    │
└──────────────────────────┘│ - ConfExp Active Probing Engine  │
                            │ - Dual-Branch Spatio-Temporal    │
                            └──────────────────────────────────┘
```

---

## 📂 Repository Layout

```
├── .agents/skills/              # Antigravity IDE telecom-rca-framework skill
├── docs/                        # Master carrier-grade specs, PRD, plan, and reports
│   ├── SYSTEM_SPECIFICATION_AND_ARCHITECTURE.md
│   ├── PROJECT_REQUIREMENTS.md
│   ├── IMPLEMENTATION_PLAN.md
│   ├── complete_system_architecture.jpg
│   ├── aws_cloud_architecture.jpg
│   └── *.docx reports
├── infra/                       # Terraform IaC for AWS services (MSK, Neptune, Timestream)
├── src/
│   ├── contracts/               # Shared Pydantic data contracts (Contract 1, 2, 3)
│   ├── graph/                   # Amazon Neptune Gremlin & NetworkX topology engine
│   ├── hygiene/                 # 3-Layer Shannon Entropy, STL Loess & SOMP pipeline
│   ├── ingest/                  # Benchmark & telemetry ingesters (RCAEval, TN-RCA530, etc.)
│   ├── mcp/                     # Model Context Protocol (MCP) server & agent tools
│   ├── ml_engine/               # Person B: ML Engine, Digital Twin & Contract 2 Server
│   │   ├── benchmark_eval.py    # RCAEval & TN-RCA530 evaluation suite
│   │   ├── server.py            # Contract 2 REST FastAPI service (/analyze, /models, etc.)
│   │   ├── data/                # PCAP loader, synthetic noise injection, RCAEval loader
│   │   ├── explainability/      # Integrated Gradients & feature attribution (XAI)
│   │   ├── models/
│   │   │   ├── graph/           # TransGNN, TraceGraphBuilder, BDF-FL
│   │   │   ├── mnsuad/          # DAGMM teacher, Transformer DevNet student, MNSUAD trainer
│   │   │   ├── probing/         # ConfExp active diagnostic probing engine
│   │   │   ├── signaling/       # Deterministic 5GC PCAP Golden Flow verifier + SVM
│   │   │   ├── spatio_temporal/ # Dual-branch CNN-Transformer network
│   │   │   └── telegan/         # TeleGAN-Core dual autoencoder GAN
│   │   └── schemas/             # Strictly typed Contract 1 inputs & Contract 2 outputs
│   ├── pcap/                    # Wireshark/tshark extractor & 3GPP TS 23.502 golden flows
│   └── rag/                     # ETSI NFV-MANO SOP sliding-window vector store
├── tests/                       # Automated test suite (34 passing tests)
├── pyproject.toml               # Unified project metadata and dependencies
└── requirements.txt             # Production pip requirements
```

---

## 🚀 Running Tests & Local Execution

### 1. Run Complete Automated Test Suite (34 Tests)

```bash
# Run all tests across Layer 1-2 and Layer 3 ML engine
pytest -v
```

### 2. Start Model Context Protocol (MCP) Server (Port 8000)

```bash
uvicorn src.mcp.server:app --reload --port 8000
```

### 3. Start Contract 2 ML RCA Server (Port 8001)

```bash
uvicorn src.ml_engine.server:app --reload --port 8001
```

---

## 📄 Documentation Index

Detailed specifications, mathematical derivations, and research papers are available in [`docs/`](docs/):
- **[System Specification & Architecture Reference](docs/SYSTEM_SPECIFICATION_AND_ARCHITECTURE.md)**
- **[Project Requirements Document](docs/PROJECT_REQUIREMENTS.md)**
- **[12-Week Implementation Plan](docs/IMPLEMENTATION_PLAN.md)**
- **[Documentation Index & Reports](docs/README.md)**
