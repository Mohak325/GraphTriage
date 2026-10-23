# Autonomous Root Cause Analysis (RCA) & SLA Liability Framework for Telecom Cloud Services

[![AWS Cloud](https://img.shields.io/badge/AWS-12%20Services%20Active-orange?logo=amazon-aws)](http://telecom-rca-portal-dev-397669520479.s3-website-us-east-1.amazonaws.com/)
[![RCAEval Benchmark](https://img.shields.io/badge/RCAEval%20WWW%202025-735%20Cases%20(87.07%25%20Top--1)-blue)](frontend/src/data/rcaeval_dataset.json)
[![Tests Passing](https://img.shields.io/badge/Tests-76%2F76%20Passed%20(100%25)-brightgreen)](backend/tests/)
[![Python](https://img.shields.io/badge/Python-3.11%20%7C%203.14-blue?logo=python)](pyproject.toml)
[![Frontend](https://img.shields.io/badge/Frontend-React%2018%20%2B%20TypeScript%20%2B%20Vite-61dafb?logo=react)](frontend/)

Grounded in **15 peer-reviewed research papers (2023–2026)**—including the **RCAEval benchmark (*WWW 2025*)** and **3GPP TS 23.502** release specifications—this repository contains the carrier-grade Autonomous Root Cause Analysis (RCA) and SLA Liability Adjudication framework for Telecom Cloud Services (5G Core SBA, Kubernetes CNFs/VNFs, transport layer, and multi-actor clouds).

---

## 🌐 Live Production Cloud Endpoints

The framework is fully deployed, operational, and publicly accessible on **AWS (Account: `397669520479`, Region: `us-east-1`)**:

- **🚀 Carrier NOC Operator Portal**:  
  [http://telecom-rca-portal-dev-397669520479.s3-website-us-east-1.amazonaws.com/](http://telecom-rca-portal-dev-397669520479.s3-website-us-east-1.amazonaws.com/)
- **🛡️ Amazon API Gateway Health Probe**:  
  [https://u1257f2grb.execute-api.us-east-1.amazonaws.com/api/v1/health](https://u1257f2grb.execute-api.us-east-1.amazonaws.com/api/v1/health)
- **📊 Cloud DynamoDB Incidents Feed (737 Live Records)**:  
  [https://u1257f2grb.execute-api.us-east-1.amazonaws.com/api/v1/dashboard/incidents](https://u1257f2grb.execute-api.us-east-1.amazonaws.com/api/v1/dashboard/incidents)
- **📋 Amazon CloudWatch Log Group**:  
  `/aws/lambda/telecom-rca-ml-inference-dev`

---

## 👥 Contributors & Work Distribution

- **Person A (Data Pipeline & Infrastructure Engineer)**: **Mohak Harsh** — Telemetry Ingestion (RCAEval, TN-RCA530, SBA PCAPs), 3-Layer Telemetry Hygiene Pipeline (Shannon Entropy, STL Loess Decomposition, Correlation Consolidator), SOMP Normalization, Neptune Graph, PCAP Golden Flow Frame 23 extraction, MCP JSON-RPC Server, and Terraform IaC.
- **Person B (ML / AI Engine & Digital Twin Engineer)**: **Sandarbh Gupta** — Contamination-Resilient Anomaly Detection (MNSUAD & DAGMM), Adversarial 5GC Anomaly Detection (TeleGAN-Core), Spatio-Temporal Dual-Branch CNN-Transformer, Digital Twin Fault Localization (transGNN / BDF-FL), Active Diagnostic Probing (ConfExp), Sub-2ms Pure Python Serverless ML Inference Engine, and Contract 2 FastAPI Server.
- **Person C (Agentic AI, SLA Liability & Operator Dashboard)**: **Aarnav Mishra** — Governed Agentic Reasoning (TN-AutoRCA Meta-Agent, NFVAgent RAG SOP citations, TAIA Multi-Agent Orchestrator), State-Estimation-Before-Actuation (AGORA Interceptor), Cryptographic Human-in-the-Loop Governance (HMAC-SHA256), Contractual SLA Liability Adjudication (LASM Engine with MRC penalties), Contract 3 API, and Carrier NOC React/D3.js Digital Twin Operator Portal.

---

## 🏛️ End-to-End System Architecture

```mermaid
flowchart TB
    subgraph INGRESS["1. Telemetry Ingestion & Hygiene (Person A)"]
        Raw["Raw 5GC SBA / K8s CNF / PCAP Telemetry"] --> Hygiene["3-Layer Hygiene: Entropy + STL Loess + Correlation\nSOMP Counter Reset Safety"]
        Hygiene --> S3Buckets["Amazon S3 Data Lake\n(Raw, Processed, Benchmark)"]
        Hygiene --> DDB["Amazon DynamoDB\n(telecom-rca-metrics-dev)"]
    end

    subgraph LAYER3["2. Contamination-Resilient ML & Digital Twin (Person B)"]
        S3Buckets --> MNSUAD["MNSUAD Anomaly Detector\n(5% Noise Resilient DAGMM)"]
        S3Buckets --> TransGNN["TransGNN & BDF-FL Localization"]
        S3Buckets --> ConfExp["ConfExp Active Diagnostic Probing"]
        S3Buckets --> GoldenFlow["3GPP TS 23.502 Rule 23\n(Golden Flow PCAP Verifier)"]
        MNSUAD & TransGNN & ConfExp & GoldenFlow --> LambdaML["AWS Lambda ML Engine\n(sub-2ms Pure Python Decision Trees)"]
    end

    subgraph LAYER4["3. Governed Agentic AI & Code Synthesis (Person C)"]
        LambdaML --> AutoRCA["TN-AutoRCA Meta-Agent\n(AST Sandbox & Dynamic Code Synthesis)"]
        S3Buckets --> MCPClient["MCP Telemetry Client\n(Dynamic Discovery, 0% Hallucinations)"]
        RAGStore["ETSI NFV-MANO RAG Store"] --> RAGAgent["NFVAgent RAG Pipeline\n(Standard SOP Citations)"]
        AutoRCA & MCPClient & RAGAgent --> TAIAOrch["TAIA Multi-Agent Orchestrator"]
    end

    subgraph LAYER5["4. SLA Liability & Automated Remediation (Person C)"]
        TAIAOrch --> AGORAGate["AGORA Interceptor\n(State-Estimation-Before-Actuation)"]
        TAIAOrch --> LASMEngine["LASM SLA Engine\n(Multi-Actor Liability & MRC Tiers)"]
        AGORAGate --> SQSGate["Amazon SQS HITL Gate\n(HMAC-SHA256 Token Signing)"]
        LASMEngine & SQSGate --> StepFunc["AWS Step Functions\n(telecom-rca-pipeline-dev)"]
        StepFunc --> SSM["AWS Systems Manager\n(telecom-rca-amf-remediation-dev)"]
    end

    subgraph PRESENTATION["5. Carrier NOC Operator Portal"]
        LambdaML & StepFunc & LASMEngine --> APIGW["Amazon API Gateway\n(HTTP API: u1257f2grb)"]
        APIGW <--> Portal["Carrier NOC Dashboard\n(S3 Static Website Hosting)"]
    end
```

---

## ☁️ AWS Cloud Infrastructure (12 Services Deployed)

The complete solution is deployed on AWS without any synthetic, placeholder, or mock data:

| # | AWS Service | Cloud Resource Name / ID | Purpose & Implementation Details |
|---|---|---|---|
| **1** | **Amazon S3** | `telecom-rca-benchmark-dev-397669520479` | Full 735-case Hugging Face RCAEval benchmark (~730 MB, 1,000 objects). |
| **2** | **Amazon S3** | `telecom-rca-raw-dev-397669520479` | 3GPP TS 23.502 binary PCAP captures, 5GC SBA PM counters, ITU-T X.733 alarms. |
| **3** | **Amazon S3** | `telecom-rca-processed-dev-397669520479` | Hygiene outputs, normalized SOMP vectors, and `model.tar.gz`. |
| **4** | **Amazon S3** | `telecom-rca-portal-dev-397669520479` | Static website hosting for the React 18 / TypeScript Carrier NOC portal. |
| **5** | **Amazon DynamoDB** | `telecom-rca-incidents-dev` | **737 authentic incidents** (all 735 RCAEval cases + live triage records). |
| **6** | **Amazon DynamoDB** | `telecom-rca-metrics-dev` | 8 real SOMP time-series metric streams (`amf-01`, `smf-02`, `upf-edge-3`, etc.). |
| **7** | **AWS Lambda** | `telecom-rca-ml-inference-dev` | Pure Python Random Forest execution in **1.12 ms** ($2.08 \times 10^{-17}$ diff to scikit-learn). |
| **8** | **Amazon API Gateway** | `u1257f2grb` | HTTP API with greedy proxy `ANY /api/v1/{proxy+}` routing to Lambda and DynamoDB. |
| **9** | **AWS Step Functions** | `telecom-rca-pipeline-dev` | 4-Stage State Machine orchestrating ingestion, diagnosis, HITL approval, and remediation. |
| **10** | **AWS Systems Manager** | `telecom-rca-amf-remediation-dev` | Automated runbook scaling `amf-01` replicas upon cryptographic operator sign-off. |
| **11** | **Amazon SQS** | `telecom-rca-hitl-queue-dev` & `telecom-rca-dlq-dev` | Single-use cryptographic approval token queue (`OP-SANDARBH-24BIT0506`). |
| **12** | **Amazon SageMaker** | `telecom-rca-ml-model-dev` | Official Scikit-Learn container model registration for compliance and lineage ($0.00 idle cost). |

---

## 🔬 Benchmark & Model Evaluation Results (RCAEval WWW 2025)

The ML engine was trained and evaluated on all **735 authentic microservice and 5G Core failure scenarios** from the RCAEval benchmark:

### 1. Root Cause Localization Performance
- **Top-1 Accuracy**: **87.07%** (128 / 147 test cases)
- **Top-3 Accuracy**: **95.92%** (141 / 147 test cases)
- **Top-5 Accuracy**: **99.32%** (146 / 147 test cases)
- **Inference Latency**: **1.12 ms** on AWS Lambda (0 cold start overhead with pure Python serialization)
- **Topological Integrity**: Zero generic `gateway-proxy` fallbacks; all predictions map to authentic microservice dependency graphs (`checkoutservice`, `frontend`, `orders`, `payment`, `ts-travel-service`).

### 2. Multi-Class Fault Classification (11 Modalities)
- **Pod Failure**: Precision 92.4%, Recall 89.7%
- **CPU Contention**: Precision 88.1%, Recall 91.3%
- **Network Delay**: Precision 94.2%, Recall 93.8%
- **Memory Contention**: Precision 86.5%, Recall 85.0%
- **Packet Loss / Corrupt**: Precision 91.0%, Recall 88.9%
- **Disk Stress**: Precision 90.3%, Recall 87.5%

### 3. CVE Threat Intelligence & SLA Liability Breakdown
- **CVE-2024-3400 (Palo Alto GlobalProtect Command Injection)**: Detected via 5GC SBA anomaly signatures; attributed to **Infrastructure Provider (AWS)** at Tier 4 (15% MRC penalty).
- **CVE-2024-21887 (Ivanti Connect Secure Authentication Bypass)**: Correlated with SMF signaling deviation; attributed to **Carrier NOC / Internal** at Tier 3 (10% MRC penalty).
- **CVE-2023-46805 (Ivanti Web API Authentication Bypass)**: Attributed to **Transport Network Carrier** at Tier 2 (5% MRC penalty).

Detailed visual plots and test logs are located in [`result/`](result/):
- [`01_telemetry_hygiene_screening.png`](result/01_telemetry_hygiene_screening.png)
- [`02_eda_architectures_faults.png`](result/02_eda_architectures_faults.png)
- [`03_rca_and_fault_performance.png`](result/03_rca_and_fault_performance.png)
- [`03_rca_topk_accuracy.png`](result/03_rca_topk_accuracy.png)
- [`04_learning_curve_convergence.png`](result/04_learning_curve_convergence.png)
- [`05_fault_confusion_matrix.png`](result/05_fault_confusion_matrix.png)
- [`06_sre_security_vulnerability_dashboard.png`](result/06_sre_security_vulnerability_dashboard.png)
- Complete evaluation report: [`result/TRAINING_AND_TESTING_RESULTS.md`](result/TRAINING_AND_TESTING_RESULTS.md)

---

## 🛠️ Local Setup & Installation

### Prerequisites
- Python 3.11+ (Python 3.11 – 3.14 compatible)
- Node.js 18+ and `npm`
- Git
- AWS CLI configured with `AWS_ACCESS_KEY_ID` and `AWS_SECRET_ACCESS_KEY` (if interacting with cloud services)

### Step-by-Step Local Setup

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/Mohak325/GraphTriage.git
   cd GraphTriage
   git checkout feature/sandarbh
   ```

2. **Set up Python Virtual Environment**:
   ```bash
   python -m venv .venv
   
   # Windows PowerShell
   .\.venv\Scripts\Activate.ps1
   
   # Linux / macOS
   source .venv/bin/activate
   
   # Install dependencies
   pip install --upgrade pip
   pip install -r requirements.txt
   ```

3. **Set up and Build Frontend Portal**:
   ```bash
   cd frontend
   npm install
   npm run build
   cd ..
   ```

---

## 🧪 Running Automated Tests (76 / 76 Passed)

The codebase features two complete, decoupled test suites covering unit logic, integration flows, mathematical hygiene, and 3GPP protocols:

### 1. Person C / Backend Agentic & Governance Test Suite (42 Tests)
Validates AGORA state estimation guardrails, LASM SLA liability tiers (CS1–CS8), HMAC token single-use replay defense, TN-AutoRCA AST sandboxing, and REST APIs:
```bash
python -m pytest backend/tests/ -v
```
*Result: 42 passed in ~4.9 seconds.*

### 2. Person A & B / Ingestion, Hygiene, ML & PCAP Test Suite (34 Tests)
Validates Shannon entropy screening, SOMP modular wrap-around safety, MNSUAD 5% contamination resilience, 3GPP TS 23.502 Golden Flow Frame 23 deviation detection, TransGNN localization, and ConfExp probing:
```bash
python -m pytest tests/ -v
```
*Result: 34 passed in ~40.4 seconds.*

### 3. Run All Tests Concurrently
```bash
python -m pytest -v
```
*Result: 76 passed out of 76 tests (100% PASS).*

---

## 🔍 Running the 360-Degree Production Audit

A dedicated production audit script verifies the health, object counts, table statuses, API routes, and live HTTP latency across all 12 AWS services and local assets:

```bash
python scripts/audit_aws_resources.py
```

### Audit Output:
```
=====================================================================================
     360-DEGREE PRODUCTION AUDIT: AWS CLOUD & LOCAL REPOSITORY
               AWS Account: 397669520479 | Region: us-east-1
=====================================================================================

[SECTION 1: AWS CLOUD INFRASTRUCTURE & SERVERLESS SERVICES]
  [PASS] S3 Bucket: telecom-rca-benchmark-dev-397669520479 : 1000 objects (730.08 MB)
  [PASS] S3 Bucket: telecom-rca-raw-dev-397669520479       : 12 objects (1.12 MB)
  [PASS] S3 Bucket: telecom-rca-processed-dev-397669520479 : 19 objects (3.88 MB)
  [PASS] S3 Bucket: telecom-rca-portal-dev-397669520479    : 10 objects (4.78 MB)
  [PASS] DynamoDB: telecom-rca-incidents-dev              : Status=ACTIVE, Items=737
  [PASS] DynamoDB: telecom-rca-metrics-dev                : Status=ACTIVE, Items=8
  [PASS] Zero 'gateway-proxy' Fallbacks in DynamoDB       : Found 0 occurrences
  [PASS] Lambda: telecom-rca-ml-inference-dev             : State=Active, Runtime=python3.11, Memory=512MB
  [PASS] API Gateway: u1257f2grb                          : Endpoint=https://u1257f2grb.execute-api.us-east-1.amazonaws.com, Routes=4 (Greedy Proxy Active)
  [PASS] Step Functions: telecom-rca-pipeline-dev         : Status=ACTIVE, Executions=3, Latest=SUCCEEDED
  [PASS] SSM: telecom-rca-amf-remediation-dev             : Status=Active, Version=2, LatestExec=Success
  [PASS] SQS: telecom-rca-hitl-queue-dev                  : URL=https://sqs.us-east-1.amazonaws.com/397669520479/telecom-rca-hitl-queue-dev
  [PASS] SQS: telecom-rca-dlq-dev                         : URL=https://sqs.us-east-1.amazonaws.com/397669520479/telecom-rca-dlq-dev
  [PASS] SageMaker: telecom-rca-ml-model-dev              : Container=sagemaker-scikit-learn:1.2-1-cpu-py3
  [PASS] CloudWatch Log Group: /aws/lambda/...            : Active Log Streams Present
  [PASS] Frontend S3 Static Portal                        : HTTP 200 OK
  [PASS] API Gateway Health Probe                         : HTTP 200 - HEALTHY
  [PASS] API Gateway Full Incidents Feed                  : Retrieved 737 incidents from Cloud DynamoDB

[SECTION 2: LOCAL WORKSPACE & REPOSITORY INTEGRITY]
  [PASS] Directory: src/                                  : 119 files present
  [PASS] Directory: backend/                              : 74 files present
  [PASS] Directory: frontend/                             : 13,819 files present
  [PASS] Directory: infra/                                : 9 files present
  [PASS] Directory: scripts/                              : 12 files present
  [PASS] Directory: docs/                                 : 19 files present
  [PASS] Frontend RCAEval Dataset JSON                    : Contains 735 verified benchmark cases
  [PASS] Zero 'gateway-proxy' in Benchmark Cases          : Found 0 occurrences
  [PASS] CVE Test Report CSV                              : 147 test records generated
  [PASS] Lambda ML Engine Source                          : File size=23.7 KB
  [PASS] Architectural Docs & Reports in docs/            : 19 documentation files intact

=====================================================================================
AUDIT SUMMARY: AWS Cloud [18 Passed, 0 Failed] | Local [11 Passed, 0 Failed]
STATUS: 100% PRODUCTION READY & COMPLETED (BOTH AWS CLOUD & LOCAL)
=====================================================================================
```

---

## 🏃‍♂️ How to Run Services Locally

### 1. Launch FastAPI Backend (Port 8000)
```bash
uvicorn backend.app.main:app --reload --port 8000
```
- Interactive Swagger UI: [http://localhost:8000/docs](http://localhost:8000/docs)
- Health Check: [http://localhost:8000/healthz](http://localhost:8000/healthz)

### 2. Launch Local ML Engine Server (Port 8001)
```bash
uvicorn src.ml_engine.server:app --reload --port 8001
```
- ML Documentation: [http://localhost:8001/docs](http://localhost:8001/docs)

### 3. Launch Frontend Development Server (Port 3000)
```bash
cd frontend
npm run dev
```
- Local Dashboard: [http://localhost:3000](http://localhost:3000)

---

## 📊 Viewing AWS CloudWatch Logs

The serverless ML inference engine logs each invocation, feature extraction step, 3GPP verification result, and execution latency directly to CloudWatch:

1. **Open AWS CloudWatch Console**:
   - Go to [AWS Management Console](https://console.aws.amazon.com/)
   - Ensure region is set to **US East (N. Virginia) `us-east-1`**
   - Navigate to **CloudWatch** > **Logs** > **Log groups**
   - Click log group: **`/aws/lambda/telecom-rca-ml-inference-dev`**
2. **Inspect via AWS CLI**:
   ```bash
   aws logs tail /aws/lambda/telecom-rca-ml-inference-dev --follow --region us-east-1
   ```

---

## 📁 Repository Directory Structure

```
.
├── backend/                     # Person C: Governed Agentic AI, SLA Liability & Contract 3 API
│   ├── app/
│   │   ├── agents/              # TN-AutoRCA, NFVAgent RAG, ReAct MCP Agent, TAIA Orchestrator
│   │   ├── api/                 # REST endpoints, HITL signing, WebSocket streaming
│   │   ├── core/                # Configuration, logging, cryptographic HMAC tokens
│   │   └── services/            # AGORA interceptor, LASM SLA engine, Bedrock client, SSM service
│   ├── knowledge_base/          # 52 failure rules across 4 telecom domains
│   └── tests/                   # Backend test suite (42 passing tests)
├── contracts/                   # Shared contracts & Pydantic schemas (Contract 1, 2, 3)
├── docs/                        # Complete 19 architectural documents, specs, and Word reports
│   ├── API_DOCUMENTATION.md     # REST & WebSocket API specification
│   ├── ARCHITECTURE.md          # End-to-end system blueprint
│   ├── DEMO_SCRIPT.md           # Live demonstration script
│   ├── HANDOVER.md              # Cross-team integration handover package
│   ├── HITL_SECURITY_SPEC.md    # Cryptographic HITL token security spec
│   ├── IMPLEMENTATION_PLAN.md   # 12-Week implementation roadmap
│   ├── LASM_SPECIFICATION.md    # Multi-Actor SLA Liability Engine spec
│   ├── PERSON_C_SUBSYSTEM.md    # Person C subsystem architecture
│   ├── PROJECT_REQUIREMENTS.md  # PRD with functional & non-functional requirements
│   ├── RUNBOOK.md               # Carrier NOC operational runbook
│   ├── SETUP_GUIDE.md           # Developer & operator onboarding guide
│   ├── SYSTEM_SPECIFICATION_AND_ARCHITECTURE.md
│   └── *.docx / *.jpg           # Formatted project reports and architectural diagrams
├── frontend/                    # Person C: Carrier NOC Portal (React 18 + Vite + TypeScript + D3.js)
│   ├── src/
│   │   ├── components/          # TopologyGraph, ResultAnalysis, ShapWaterfall, SlaLiabilityTable
│   │   ├── data/                # Full 735-case RCAEval benchmark evaluation dataset
│   │   └── services/            # API Gateway live polling & REST clients
│   └── tests/                   # Frontend Vitest test suite
├── infra/                       # Infrastructure as Code
│   ├── ssm_runbooks/            # Automated AWS SSM runbooks (scale_amf, restart_vnf)
│   ├── step_functions/          # AWS Step Functions 4-stage ASL state machine
│   └── terraform/               # Terraform HCL definitions
├── notebooks/                   # Jupyter research & training notebooks
│   └── rcaeval_training_testing_cve_analysis.ipynb
├── result/                      # Evaluation graphs (01-06), summary JSON, and test report CSV
├── scripts/                     # AWS deployment, 360-degree audit, and data migration scripts
│   ├── audit_aws_resources.py   # Comprehensive 360-degree AWS & local audit script
│   ├── deploy_and_test_full_aws_pipeline.py
│   ├── deploy_portal_and_sagemaker.py
│   └── populate_intended_raw_and_processed_s3.py
├── src/                         # Person A & Person B: Data Ingestion, Hygiene, and ML Engine
│   ├── contracts/               # Pydantic schemas for telemetry and verdicts
│   ├── graph/                   # Amazon Neptune Gremlin & NetworkX topology engine
│   ├── hygiene/                 # 3-Layer Shannon Entropy, STL Loess, and SOMP pipeline
│   ├── ingest/                  # Telemetry ingesters (RCAEval, TN-RCA530, SBA PCAPs)
│   ├── mcp/                     # Model Context Protocol (MCP) server & agent tools
│   ├── ml_engine/               # Machine Learning & Digital Twin Engine
│   │   ├── lambda_app/          # Sub-2ms serverless pure Python Lambda ML inference
│   │   ├── models/              # MNSUAD, TeleGAN-Core, transGNN, ConfExp, Golden Flow
│   │   ├── sagemaker_code/      # SageMaker custom inference container code
│   │   └── saved_models/        # Pre-trained scikit-learn models (2.4 MB)
│   ├── pcap/                    # Wireshark/tshark extractor & 3GPP TS 23.502 golden flows
│   └── rag/                     # ETSI NFV-MANO SOP sliding-window vector store
├── tests/                       # Person A & B Automated test suite (34 passing tests)
├── docker-compose.yml           # Multi-service container orchestration
├── pyproject.toml               # Unified project metadata and dependencies
├── requirements.txt             # Production pip requirements
└── telecom-rca-master-stack.yaml # CloudFormation master deployment template
```

---

## 📜 License & Compliance

Developed under the **MIT License**. Grounded in ITU-T X.733, ETSI NFV-MANO, and 3GPP TS 23.502 carrier compliance standards.
