# GraphTriage — Engineering Handover & Collaborative Task Guide

> **Author:** Sandarbh Gupta (`feature/sandarbh`, 24BIT0506)  
> **Role:** Graph & Backend Engineer  
> **Course:** Cloud System Architecture / Cloud Architecture Design (Slot B1+TB1)  
> **Status:** **80% Project Implementation Complete** (Phases 1, 2, 3, 4 Finished & Verified)  
> **Test Status:** **57/57 Tests Passing (100%)**, 0 Pyright Type Errors  
> **Target Audience:** Future LLM instances, Team Lead (Mohak Harsh), Frontend/Evaluation Engineer (Aarnav Mishra)

---

## 1. Executive Summary for Other LLMs & Engineers

If you are an AI assistant or human engineer collaborating on this repository, **do not re-implement or break the Graph Engine, Backend API, or AWS Infrastructure**. Those layers are 100% complete, fully tested, and hardened.

Use this document to understand:
1. **What Sandarbh has completed** and the exact components available for you to import and use.
2. **What Mohak (Multi-Agent Architect)** needs to implement next.
3. **What Aarnav (Frontend & Evaluation)** needs to implement next.
4. **The exact data contracts and API endpoints** connecting all components.

---

## 2. Complete Inventory of Sandarbh's Deliverables

### A. Graph Database & Mathematical Engine Layer
* [database/schema.cypher](file:///c:/Users/sanda/OneDrive/Desktop/cloud/GraphTriage/database/schema.cypher): Neo4j DDL with unique constraints and indexes for Services, Hosts, Containers, Networks, and Anomalies.
* [database/seed_data.cypher](file:///c:/Users/sanda/OneDrive/Desktop/cloud/GraphTriage/database/seed_data.cypher): 12-microservice cloud topology with call dependencies, container allocations, and active cascading failure scenario (`srv-payment-service` DB pool saturation $\rightarrow$ `srv-order-service` timeout $\rightarrow$ `srv-api-gateway` 504 errors).
* [ai_models/graph_engine/fault_gradient.py](file:///c:/Users/sanda/OneDrive/Desktop/cloud/GraphTriage/ai_models/graph_engine/fault_gradient.py): **Spectral Fault Gradient Diffusion Engine**. Implements reverse causal power iteration:
  $$f^{(t+1)} = \alpha P_{\text{rev}} f^{(t)} + (1 - \alpha) y$$
  pinpointing root causes in $< 1\text{ms}$ with convergence guarantees.
* [ai_models/graph_engine/topology_builder.py](file:///c:/Users/sanda/OneDrive/Desktop/cloud/GraphTriage/ai_models/graph_engine/topology_builder.py): In-memory graph builder, trace aggregator, and graph validator.
* [ai_models/graph_engine/neo4j_client.py](file:///c:/Users/sanda/OneDrive/Desktop/cloud/GraphTriage/ai_models/graph_engine/neo4j_client.py): Async Neo4j Python client with connection pooling, retry logic, and NetworkX export.
* [ai_models/graph_engine/navigator_interface.py](file:///c:/Users/sanda/OneDrive/Desktop/cloud/GraphTriage/ai_models/graph_engine/navigator_interface.py): Pre-built bridge for Mohak's **Navigator Agent** (`get_suspicious_subgraph()`, `evaluate_causal_flow()`).

### B. Amazon Neptune Gremlin Migration (AWS Phase 4)
* [database/neptune/gremlin_schema.py](file:///c:/Users/sanda/OneDrive/Desktop/cloud/GraphTriage/database/neptune/gremlin_schema.py): Vertex/Edge labels, property constants, and compiled Gremlin traversals (`get_all_services`, `get_call_graph`, `get_k_hop_subgraph`, `get_cascading_failure_paths`, idempotent upserts).
* [database/neptune/cypher_to_gremlin_migrator.py](file:///c:/Users/sanda/OneDrive/Desktop/cloud/GraphTriage/database/neptune/cypher_to_gremlin_migrator.py): Automated compiler converting Cypher seed data into:
  1. [database/neptune/seed_gremlin.groovy](file:///c:/Users/sanda/OneDrive/Desktop/cloud/GraphTriage/database/neptune/seed_gremlin.groovy) (TinkerPop Gremlin console script)
  2. [database/neptune/bulk_loader/neptune_vertices.csv](file:///c:/Users/sanda/OneDrive/Desktop/cloud/GraphTriage/database/neptune/bulk_loader/neptune_vertices.csv) (Neptune typed headers: `~id`, `~label`, `name:String`, `latency_p95:Double`)
  3. [database/neptune/bulk_loader/neptune_edges.csv](file:///c:/Users/sanda/OneDrive/Desktop/cloud/GraphTriage/database/neptune/bulk_loader/neptune_edges.csv) (Neptune typed headers: `~id`, `~from`, `~to`, `~label`, `weight:Double`)
* [database/neptune/neptune_client.py](file:///c:/Users/sanda/OneDrive/Desktop/cloud/GraphTriage/database/neptune/neptune_client.py): Async Gremlin client with NetworkX export, dual-engine support, and offline mock fallback for local testing.
* [database/neptune/README.md](file:///c:/Users/sanda/OneDrive/Desktop/cloud/GraphTriage/database/neptune/README.md): Full Neptune architecture, Cypher vs Gremlin translation matrix, and AWS CLI provisioning guide.

### C. Backend API Gateway & Streaming Layer
* [backend/main.py](file:///c:/Users/sanda/OneDrive/Desktop/cloud/GraphTriage/backend/main.py): FastAPI app with lifespan hooks, CORS, and request timing headers.
* [backend/config.py](file:///c:/Users/sanda/OneDrive/Desktop/cloud/GraphTriage/backend/config.py): Pydantic Settings supporting Neo4j, Neptune, OpenSearch, Redis, and Gemini.
* [backend/routes/graph.py](file:///c:/Users/sanda/OneDrive/Desktop/cloud/GraphTriage/backend/routes/graph.py):
  - `GET /api/graph/topology` $\rightarrow$ Returns Cytoscape.js nodes & edges with real-time metrics.
  - `GET /api/graph/subgraph/{service_id}?k=2` $\rightarrow$ Returns k-hop ego network.
  - `GET /api/graph/heatmap` $\rightarrow$ Returns spectral anomaly scores for node coloring.
* [backend/routes/ingestion.py](file:///c:/Users/sanda/OneDrive/Desktop/cloud/GraphTriage/backend/routes/ingestion.py):
  - `POST /api/ingest/metrics` $\rightarrow$ Streaming batch metric ingestion.
  - `POST /api/ingest/traces` $\rightarrow$ Distributed trace span ingestion.
  - `POST /api/ingest/logs` $\rightarrow$ Unstructured error log ingestion.
  - `POST /api/ingest/anomaly` $\rightarrow$ High-priority anomaly injection triggering RCA.
* [backend/routes/rca.py](file:///c:/Users/sanda/OneDrive/Desktop/cloud/GraphTriage/backend/routes/rca.py):
  - `POST /api/rca/trigger` $\rightarrow$ Starts RCA workflow.
  - `GET /api/rca/{rca_id}/result` $\rightarrow$ Polls diagnosis result and agent trace.
  - `GET /api/rca/history` $\rightarrow$ Lists historical triage runs.
* [backend/routes/websocket.py](file:///c:/Users/sanda/OneDrive/Desktop/cloud/GraphTriage/backend/routes/websocket.py): Real-time WebSocket event streaming (`/ws/rca/{rca_id}`).

### D. AWS Cloud Infrastructure (All 12 Services Planned)
* [docker/aws/cloudformation-master.yaml](file:///c:/Users/sanda/OneDrive/Desktop/cloud/GraphTriage/docker/aws/cloudformation-master.yaml): One-click Infrastructure-as-Code deploying:
  - **VPC & Subnets**: Multi-AZ networking.
  - **Amazon Neptune**: Cluster + Instance + DB Subnet Group.
  - **Amazon S3**: Staging bucket for Neptune bulk loading and archives.
  - **Amazon DynamoDB**: `GraphTriage-Remediations` and `GraphTriage-AgentSessions` tables.
  - **Amazon SQS**: Alarm storm queue with Dead Letter Queue redrive policy.
  - **Amazon SNS**: `GraphTriage-SRE-Alerts` topic.
  - **Amazon CloudWatch**: `/aws/graphtriage/microservices` and `/aws/graphtriage/remediation` log groups.
  - **AWS Lambda**: Closed-loop remediation handler.
* [docker/aws/cloudwatch-agent-config.json](file:///c:/Users/sanda/OneDrive/Desktop/cloud/GraphTriage/docker/aws/cloudwatch-agent-config.json): CloudWatch Agent scraping configuration.
* [docker/aws/fluent-bit.conf](file:///c:/Users/sanda/OneDrive/Desktop/cloud/GraphTriage/docker/aws/fluent-bit.conf) & [fluent-bit-parsers.conf](file:///c:/Users/sanda/OneDrive/Desktop/cloud/GraphTriage/docker/aws/fluent-bit-parsers.conf): Fluent Bit log router.
* [docker/aws/opensearch_index_templates.json](file:///c:/Users/sanda/OneDrive/Desktop/cloud/GraphTriage/docker/aws/opensearch_index_templates.json): OpenSearch 2.x index templates for metrics, traces, and logs.
* [docker/aws/telemetry_pipeline.py](file:///c:/Users/sanda/OneDrive/Desktop/cloud/GraphTriage/docker/aws/telemetry_pipeline.py): Stream adapter detecting SLA violations (error rates > 5%, latency > 500ms, connection pool > 85%, error bursts) and pushing anomalies to the backend.
* [docker/aws/remediation_lambda.py](file:///c:/Users/sanda/OneDrive/Desktop/cloud/GraphTriage/docker/aws/remediation_lambda.py): Self-healing Lambda script (scaling pools, recycling pods, circuit breaking).
* [ai_models/llm/bedrock_provider.py](file:///c:/Users/sanda/OneDrive/Desktop/cloud/GraphTriage/ai_models/llm/bedrock_provider.py): Amazon Bedrock foundation LLM provider (Anthropic Claude 3 / Titan) with offline fallback.
* [frontend/deploy.sh](file:///c:/Users/sanda/OneDrive/Desktop/cloud/GraphTriage/frontend/deploy.sh): AWS Amplify deployment script for the Next.js dashboard.
* [docs/AWS_SERVICES_SETUP.md](file:///c:/Users/sanda/OneDrive/Desktop/cloud/GraphTriage/docs/AWS_SERVICES_SETUP.md): Comprehensive setup runbook for all 12 AWS services.

### E. Testing, Profiling & Security
* **Automated Test Suite**: 57 passing tests in [tests/](file:///c:/Users/sanda/OneDrive/Desktop/cloud/GraphTriage/tests/):
  - `tests/unit/test_fault_gradient.py` (8 tests)
  - `tests/unit/test_topology_builder.py` (6 tests)
  - `tests/unit/test_neo4j_client.py` (4 tests)
  - `tests/unit/test_neptune.py` (14 tests)
  - `tests/unit/test_aws_telemetry.py` (8 tests)
  - `tests/test_integration.py` (13 tests)
  - `tests/integration/test_frontend_api_contract.py` (4 tests)
* **Performance Profiling**:
  - [results/profiling/latency_profiler.py](file:///c:/Users/sanda/OneDrive/Desktop/cloud/GraphTriage/results/profiling/latency_profiler.py): Benchmarks scaling from 10 to 1,000 nodes ($P50 < 64\text{ms}$).
  - [results/profiling/throughput_benchmark.py](file:///c:/Users/sanda/OneDrive/Desktop/cloud/GraphTriage/results/profiling/throughput_benchmark.py): Measures API endpoint RPS and P99 latency.
* **Security & Configuration**:
  - [.gitignore](file:///c:/Users/sanda/OneDrive/Desktop/cloud/GraphTriage/.gitignore): Excludes `.env`, `.pem`, `credentials.csv`, `.aws/`, and log volumes.
  - [docker/.env.example](file:///c:/Users/sanda/OneDrive/Desktop/cloud/GraphTriage/docker/.env.example): Fully annotated credential template.

---

## 3. Guide for Mohak Harsh (`feature/mohak`) — Multi-Agent Architect

### What Sandarbh Has Already Provided for You:
1. **The Graph Traversal Bridge**:
   Import `NavigatorInterface` in [ai_models/graph_engine/navigator_interface.py](file:///c:/Users/sanda/OneDrive/Desktop/cloud/GraphTriage/ai_models/graph_engine/navigator_interface.py):
   ```python
   from ai_models.graph_engine.navigator_interface import NavigatorInterface

   nav = NavigatorInterface()
   # Localize top suspicious subgraphs using spectral diffusion:
   subgraph = nav.get_suspicious_subgraph(graph, top_k=3)
   ```
2. **LLM Provider Options**:
   - Google Gemini: Configured in `backend/config.py` (`GEMINI_API_KEY`).
   - Amazon Bedrock (Claude 3 / Titan): Implemented in [ai_models/llm/bedrock_provider.py](file:///c:/Users/sanda/OneDrive/Desktop/cloud/GraphTriage/ai_models/llm/bedrock_provider.py):
     ```python
     from ai_models.llm.bedrock_provider import BedrockLLMProvider
     bedrock = BedrockLLMProvider()
     diag = bedrock.diagnose_failure(service_id, subgraph_nodes, metrics, logs)
     ver = bedrock.verify_counterfactual(hypothesis, service_id, evidence)
     ```
3. **Backend Integration Hook**:
   Your orchestrator should plug directly into [backend/routes/rca.py](file:///c:/Users/sanda/OneDrive/Desktop/cloud/GraphTriage/backend/routes/rca.py) in `execute_rca_pipeline()`.

### What You (Mohak) Need to Work On:
* [ ] Implement **LangGraph StateGraph** in `ai_models/orchestrator.py` managing state transitions:
  `START -> navigator -> diagnoser -> verifier -> (if REJECT -> loop back to navigator max 3 times) -> END`.
* [ ] Implement agent nodes in `ai_models/agents/`:
  - `navigator.py`: Uses `NavigatorInterface` to prune graph search space.
  - `diagnoser.py`: Prompts LLM with subgraph context + telemetry.
  - `verifier.py`: Adversarial counterfactual validation (testing if downstream error disappears when root cause is held normal).
  - `calibration.py`: Confidence score calibration.
* [ ] Agent prompt engineering in `ai_models/llm/prompts.py`.

---

## 4. Guide for Aarnav Mishra (`feature/aarnav`) — Frontend & Evaluation

### What Sandarbh Has Already Provided for You:
1. **API Endpoints Ready for Cytoscape.js**:
   Your React / Cytoscape components can fetch directly from these endpoints:
   - `GET http://localhost:8000/api/graph/topology`
     Returns JSON elements: `{ "nodes": [...], "edges": [...] }` conforming to Cytoscape format.
   - `GET http://localhost:8000/api/graph/heatmap`
     Returns anomaly intensity dictionary: `{ "srv-payment-service": 0.96, "srv-order-service": 0.81, ... }` for node coloring.
   - `POST http://localhost:8000/api/rca/trigger`
     Body: `{"incident_id": "inc-001", "telemetry_window_minutes": 15}`.
   - `GET http://localhost:8000/api/rca/{rca_id}/result`
     Returns root cause node, confidence, and agent execution trace.
2. **Contract Tests**:
   Inspect [tests/integration/test_frontend_api_contract.py](file:///c:/Users/sanda/OneDrive/Desktop/cloud/GraphTriage/tests/integration/test_frontend_api_contract.py) to see the exact schema guarantees.
3. **Deployment**:
   Use [frontend/deploy.sh](file:///c:/Users/sanda/OneDrive/Desktop/cloud/GraphTriage/frontend/deploy.sh) to deploy your Next.js app to AWS Amplify.

### What You (Aarnav) Need to Work On:
* [ ] Initialize Next.js 14 App in `frontend/` (App Router, Tailwind/CSS, dark theme).
* [ ] Build Frontend Components:
  - `frontend/components/GraphView.tsx`: Cytoscape.js canvas rendering the topology graph.
  - `frontend/components/AgentMonitor.tsx`: Timeline showing Navigator $\rightarrow$ Diagnoser $\rightarrow$ Verifier progress.
  - `frontend/components/RCAResults.tsx`: Root cause card, confidence score meter, and remediation trigger.
* [ ] Phase 5 Evaluation Suite:
  - `results/benchmark.py`: Benchmark runner evaluating accuracy (Top-1, Top-3, Top-5, MTTD).
  - `results/charts/`: Generate comparison charts vs baseline methods.

---

## 5. How to Run & Verify the Codebase

### Running the Test Suite (All 57 Tests)
```powershell
.venv\Scripts\pytest -v
```

### Static Type Checking (0 Errors)
```powershell
.venv\Scripts\pyright
```

### Starting the FastAPI Backend
```powershell
.venv\Scripts\uvicorn backend.main:app --reload --port 8000
```
Swagger UI available at: `http://localhost:8000/docs`.

### Running Performance Profiling
```powershell
.venv\Scripts\python results/profiling/latency_profiler.py
.venv\Scripts\python results/profiling/throughput_benchmark.py
```

### Running Telemetry Anomaly Detection
```powershell
.venv\Scripts\python docker/aws/telemetry_pipeline.py
```

### Running Neptune Cypher-to-Gremlin Migration
```powershell
.venv\Scripts\python database/neptune/cypher_to_gremlin_migrator.py --validate
```
