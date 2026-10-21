# Intelligent Root Cause Analysis (RCA) Framework for Telecom Cloud Services
## Layer 1 & 2: Telemetry Ingestion, Hygiene, Storage & Agent Abstraction Layer
### Developer: Mohak Harsh (Person A — Data Pipeline & Infrastructure Engineer)

This repository contains the production-grade data foundation and agent interface for the Telecom Cloud RCA Framework, grounded in 15 peer-reviewed research papers (2023–2026).

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
                           ▼
          ┌──────────────────────────────────┐
          │  Stage 3: Model Context Protocol │
          │  - FastAPI MCP JSON-RPC Server   │
          │  - Tools: Prometheus, NWDAF, K8s,│
          │           Neptune Topology       │
          └──────────────────────────────────┘
```

---

## 📂 Directory Layout

- `src/contracts/`: Contract 1 Normalized Telemetry Event Pydantic schemas, plus Contract 2 (ML API) and Contract 3 (Agentic API) definitions.
- `src/hygiene/`:
  - `entropy_filter.py`: Layer 1 Shannon Entropy screening ($\tau_1=0.05$).
  - `noise_decomposition.py`: Layer 2 Stochastic Noise Decomposition with STL Loess.
  - `correlation_consolidator.py`: Layer 3 Pearson cross-correlation consolidation ($\tau_3=0.95$).
  - `somp_normalizer.py`: Service-Oriented Metric Preprocessing (monotonic delta intervals, counter reset safety, gauge pooling).
  - `pipeline.py`: End-to-end 3-Layer Hygiene Pipeline.
- `src/pcap/`:
  - `golden_flows.yaml`: 3GPP TS 23.502 canonical call-flow sequences (Registration, PDU Session Establishment, Deregistration).
  - `frame_parser.py`: Wireshark/tshark JSON frame extractor.
  - `wireshark_extractor.py`: Deterministic call-flow state-machine verifier.
- `src/graph/`:
  - `neptune_loader.py`: Dual-mode graph engine (Gremlin for live Neptune + NetworkX for zero-cloud local execution) and incident subgraph extractor.
- `src/ingest/`:
  - `rcaeval_ingester.py`: RCAEval benchmark ingester (735 cases across metrics, logs, traces).
  - `tn_rca530_ingester.py`: TN-RCA530 telecom base-station benchmark ingester (530 cases, BBU/RRU topologies, alarm storms).
  - `vodafone_ingester.py`: Vodafone NFV 11-country dataset ingester with 5% contamination tagging.
  - `encqor_ingester.py`: ENCQOR 5G SBA PM telemetry ingester with SOMP classification.
- `src/mcp/`:
  - `server.py`: FastAPI Model Context Protocol (MCP) server exposing Prometheus, NWDAF, K8s, and Neptune tools over REST and JSON-RPC 2.0.
- `src/rag/`:
  - `document_chunker.py`: Sliding-window ETSI NFV-MANO / 3GPP SOP chunker and semantic vector search index.
- `infra/`:
  - `main.tf`, `variables.tf`, `outputs.tf`: Complete Terraform IaC for all AWS services (kept ready for the final integration sprint).
- `tests/`:
  - Complete automated test suite covering all contracts, hygiene layers, PCAP verifiers, graph traversals, and MCP tools.

---

## 🚀 Running Tests & Local Execution

Activate the virtual environment and run the test suite:

```bash
# Run all tests
.venv\Scripts\pytest.exe -v

# Run MCP server locally
.venv\Scripts\uvicorn.exe src.mcp.server:app --reload --port 8000
```
