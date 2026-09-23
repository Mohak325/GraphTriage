# GRAPHTRIAGE — Comparison & AI-Assisted Team Implementation Plan

## 1. Are Both Documents the Same Project?

### ✅ Verdict: **YES — Same project, same team, same architecture, same concept**

Both `cloud.docx` and the [GraphTriage README](https://github.com/Mohak325/GraphTriage) describe **GRAPHTRIAGE** — the identical project by the same team (Mohak Harsh, Sandarbh Gupta, Aarnav Mishra) for the Cloud System Architecture course (2025–2026).

### Detailed Comparison

| Aspect | `cloud.docx` | GitHub README |
|--------|-------------|---------------|
| **Project Name** | GRAPHTRIAGE | GRAPHTRIAGE |
| **Team** | Sandarbh Gupta, Mohak Harsh, Aarnav Mishra | Mohak Harsh, Sandarbh Gupta, Aarnav Mishra |
| **Course** | Cloud Architecture Design | Cloud System Architecture |
| **Core Concept** | Graph-Augmented Multi-Agent Framework for RCA | Graph-Augmented Multi-Agent Framework for RCA |
| **Agents** | Navigator, Diagnoser, Verifier | Navigator, Diagnoser, Verifier |
| **Anti-Hallucination** | Adversarial Validation Protocol + Counterfactual reasoning | Adversarial Validation Protocol + Counterfactual reasoning |
| **Graph DB** | Amazon Neptune (AWS-focused) | Neo4j (local development) |
| **Cloud Provider** | AWS (Neptune, Bedrock, Lambda, OpenSearch, SQS, SNS, etc.) | Docker/local-first + optional Kubernetes |
| **LLM Backend** | Amazon Bedrock | OpenAI GPT-4 / Google Gemini |
| **Backend** | Not specified (implied FastAPI) | FastAPI |
| **Frontend** | Not specified | React/Next.js |
| **Data** | Temporal Knowledge Graphs | Neo4j + NetworkX |
| **Novelty (Extra)** | Echo State Networks + Deep Fuzzy Neural Networks, RAG, Dual-Layer KGs | Synthetic data generators, public benchmarks (AIOps, Train-Ticket, Sock Shop) |

### Key Differences

> [!IMPORTANT]
> The `cloud.docx` is the **academic proposal/report** (AWS-centric, theoretical, includes literature survey).  
> The **GitHub README** is the **engineering implementation spec** (local-first with Docker, practical tech stack, repo structure).

They describe the **same architecture at different levels of abstraction**:
- **cloud.docx** = "What we will build and why" (proposal to professors)
- **GitHub repo** = "How we will actually build it" (engineering blueprint)

---

## 2. Team-Based Implementation Plan (3 PCs, AI-Assisted)

Each team member works on their **own PC** with AI assistance (e.g., Antigravity, GitHub Copilot, ChatGPT). All code merges into the shared GitHub repo: `Mohak325/GraphTriage`.

---

### Team Structure

| PC | Member | Role | Primary Focus |
|----|--------|------|---------------|
| **PC 1** | **Mohak Harsh** | Team Lead / Multi-Agent Architect | Multi-agent orchestration (LangGraph), agent logic, adversarial validation |
| **PC 2** | **Sandarbh Gupta** | Graph & Backend Engineer | Neo4j graph engine, FastAPI backend, data ingestion, Docker setup |
| **PC 3** | **Aarnav Mishra** | Frontend & Evaluation Engineer | React/Next.js dashboard, data generation, benchmarking, visualization |

---

## Phase 1: Foundation Setup (Week 1–2) — All PCs Simultaneously

### PC 1 — Mohak (Multi-Agent Architect)

| # | Task | AI Prompt Strategy | Deliverable |
|---|------|--------------------|-------------|
| 1.1 | Initialize `ai_models/` Python package structure | Ask AI: *"Create a Python package structure for a multi-agent LLM system with Navigator, Diagnoser, Verifier agents using LangGraph"* | `ai_models/__init__.py`, `ai_models/agents/` |
| 1.2 | Set up LangGraph scaffold with state management | Ask AI: *"Build a LangGraph StateGraph with 3 nodes (navigator, diagnoser, verifier) and conditional edges for feedback loops"* | `ai_models/orchestrator.py` |
| 1.3 | Create LLM provider abstraction layer | Ask AI: *"Create a Python abstraction class that supports both OpenAI GPT-4 and Google Gemini APIs with a unified interface"* | `ai_models/llm/provider.py` |
| 1.4 | Design agent prompt templates | Ask AI: *"Write system prompts for a Navigator (graph traversal), Diagnoser (semantic analysis), and Verifier (adversarial validation) agent for network RCA"* | `ai_models/llm/prompts.py` |

### PC 2 — Sandarbh (Graph & Backend)

| # | Task | AI Prompt Strategy | Deliverable |
|---|------|--------------------|-------------|
| 2.1 | Set up Neo4j with Docker Compose | Ask AI: *"Create a docker-compose.yml with Neo4j 5.x, FastAPI, and Redis services with proper networking"* | `docker/docker-compose.yml` |
| 2.2 | Design Neo4j schema for microservice topology | Ask AI: *"Design a Neo4j Cypher schema for a microservice network topology with nodes (Service, Host, Container) and relationships (CALLS, DEPENDS_ON, RUNS_ON)"* | `database/schema.cypher` |
| 2.3 | Build FastAPI backend skeleton with CORS | Ask AI: *"Create a FastAPI backend with routes for /api/rca/trigger, /api/graph/topology, /api/agents/status, and WebSocket for real-time streaming"* | `backend/main.py`, `backend/routes/` |
| 2.4 | Create Neo4j Python driver wrapper | Ask AI: *"Build a Python class using neo4j-driver that provides methods for creating topology graphs, querying neighbors, and computing fault gradients"* | `ai_models/graph_engine/neo4j_client.py` |

### PC 3 — Aarnav (Frontend & Data)

| # | Task | AI Prompt Strategy | Deliverable |
|---|------|--------------------|-------------|
| 3.1 | Initialize Next.js 14+ dashboard with App Router | Ask AI: *"Create a Next.js 14 app with dark theme, sidebar navigation, and pages for Dashboard, Graph View, RCA Results, and Agent Logs"* | `frontend/` |
| 3.2 | Build synthetic network topology generator | Ask AI: *"Write a Python script that generates realistic microservice topology graphs (50-500 nodes) with random fault injection using NetworkX and exports to Neo4j-compatible CSV"* | `data/synthetic/generator.py` |
| 3.3 | Create multimodal telemetry data generator | Ask AI: *"Generate synthetic correlated metrics (CPU, memory, latency), traces (with span hierarchies), and log entries for microservice failures"* | `data/synthetic/telemetry_generator.py` |
| 3.4 | Set up Cytoscape.js/D3.js graph visualization component | Ask AI: *"Build a React component using Cytoscape.js that renders a network topology graph with node coloring based on anomaly scores and animated edge traversal"* | `frontend/components/GraphView.tsx` |

---

## Phase 2: Core Engine Development (Week 3–5) 

### PC 1 — Mohak

| # | Task | AI Prompt Strategy | Deliverable |
|---|------|--------------------|-------------|
| 1.5 | Implement Navigator Agent logic | Ask AI: *"Implement a Navigator agent that receives a Neo4j graph, computes fault gradients using anomaly propagation scores, and returns the top-K most suspicious subgraph nodes"* | `ai_models/agents/navigator.py` |
| 1.6 | Implement Diagnoser Agent logic | Ask AI: *"Build a Diagnoser agent that takes a localized subgraph + associated metrics/logs/traces and uses an LLM to produce a structured root cause hypothesis with confidence score"* | `ai_models/agents/diagnoser.py` |
| 1.7 | Implement Verifier Agent with adversarial protocol | Ask AI: *"Create a Verifier agent that receives a diagnosis, generates counterfactual questions, checks them against graph data, and outputs ACCEPT/REJECT with reasoning"* | `ai_models/agents/verifier.py` |
| 1.8 | Build the feedback loop (Verifier → Navigator re-engagement) | Ask AI: *"In LangGraph, add a conditional edge: if Verifier rejects, route back to Navigator with updated constraints; if accepts, route to final output"* | `ai_models/orchestrator.py` update |

### PC 2 — Sandarbh

| # | Task | AI Prompt Strategy | Deliverable |
|---|------|--------------------|-------------|
| 2.5 | Fault Gradient Computation algorithm | Ask AI: *"Implement a fault gradient computation using anomaly score propagation on a directed graph in NetworkX — compute weighted scores that propagate upstream from anomalous nodes"* | `ai_models/graph_engine/fault_gradient.py` |
| 2.6 | Data ingestion pipeline (metrics → graph enrichment) | Ask AI: *"Build a FastAPI endpoint that receives streaming metrics JSON, normalizes timestamps, and updates Neo4j node properties with latest anomaly scores"* | `backend/routes/ingestion.py` |
| 2.7 | Implement graph query APIs | Ask AI: *"Create FastAPI routes that expose Neo4j Cypher queries: get full topology, get subgraph around a node, get fault gradient heatmap data"* | `backend/routes/graph.py` |
| 2.8 | Build RCA trigger endpoint integrating orchestrator | Ask AI: *"Create a POST /api/rca/trigger endpoint that calls the LangGraph orchestrator, streams agent status updates via WebSocket, and stores results in DynamoDB/local DB"* | `backend/routes/rca.py` |

### PC 3 — Aarnav

| # | Task | AI Prompt Strategy | Deliverable |
|---|------|--------------------|-------------|
| 3.5 | Build real-time Agent Activity Monitor UI | Ask AI: *"Create a React component that connects to a WebSocket and displays a live timeline of agent activities (Navigator searching → Diagnoser analyzing → Verifier validating)"* | `frontend/components/AgentMonitor.tsx` |
| 3.6 | Build RCA Results panel | Ask AI: *"Create a React component that displays RCA results: root cause node, confidence score, evidence chain, counterfactual validation status, and remediation suggestions"* | `frontend/components/RCAResults.tsx` |
| 3.7 | Integrate graph visualization with backend API | Ask AI: *"Connect the Cytoscape.js graph component to the /api/graph/topology endpoint, add real-time fault gradient coloring, and highlight the Navigator's traversal path"* | `frontend/components/GraphView.tsx` update |
| 3.8 | Build Dashboard summary page | Ask AI: *"Create a dashboard page with summary cards: total incidents, MTTR, accuracy rate, active agents, and recent RCA results table"* | `frontend/app/dashboard/page.tsx` |

---

## Phase 3: Integration & Testing (Week 6–8)

### PC 1 — Mohak

| # | Task | AI Prompt Strategy | Deliverable |
|---|------|--------------------|-------------|
| 1.9 | End-to-end pipeline testing (inject fault → get RCA) | Ask AI: *"Write a Python test script that: 1) generates a synthetic topology, 2) injects a fault, 3) triggers the multi-agent RCA pipeline, 4) validates the output root cause matches the injected fault"* | `tests/test_e2e_pipeline.py` |
| 1.10 | Tune agent prompts for accuracy | Iterative AI: *"Analyze these 10 failed RCA cases and suggest prompt improvements for the Diagnoser agent to reduce false positives"* | Updated `ai_models/llm/prompts.py` |
| 1.11 | Implement agent confidence calibration | Ask AI: *"Add a confidence calibration module that adjusts raw LLM confidence scores based on graph evidence strength"* | `ai_models/agents/calibration.py` |

### PC 2 — Sandarbh

| # | Task | AI Prompt Strategy | Deliverable |
|---|------|--------------------|-------------|
| 2.9 | Integration testing (API ↔ Neo4j ↔ Orchestrator) | Ask AI: *"Write pytest integration tests for the FastAPI backend testing the full flow: ingest data → build graph → trigger RCA → return results"* | `tests/test_integration.py` |
| 2.10 | Performance optimization (graph queries) | Ask AI: *"Optimize these Neo4j Cypher queries for large graphs (500+ nodes) — add indexes, use APOC procedures where applicable"* | Updated `database/schema.cypher` |
| 2.11 | Docker production setup | Ask AI: *"Create a production Docker Compose with health checks, resource limits, log rotation, and environment variable configuration for all services"* | `docker/docker-compose.prod.yml` |

### PC 3 — Aarnav

| # | Task | AI Prompt Strategy | Deliverable |
|---|------|--------------------|-------------|
| 3.9 | Benchmarking suite | Ask AI: *"Build a Python benchmarking script that runs the RCA pipeline on AIOps Challenge datasets and measures: accuracy (top-1, top-3, top-5), latency (P50, P99), and hallucination rate"* | `results/benchmark.py` |
| 3.10 | Generate comparison charts | Ask AI: *"Using matplotlib/plotly, create charts comparing GraphTriage performance vs baseline methods across accuracy, latency, and hallucination metrics"* | `results/charts/` |
| 3.11 | Polish frontend with animations & responsive design | Ask AI: *"Add Framer Motion animations to the dashboard: fade-in cards, animated graph traversal, and pulse effects on anomaly nodes"* | Frontend polish |

---

## Phase 4: AWS Deployment & Presentation (Week 9–10)

### All PCs Collaborate

| # | Task | Owner | AI Prompt Strategy | Deliverable |
|---|------|-------|--------------------|-------------|
| 4.1 | Migrate Neo4j → Amazon Neptune | Sandarbh | *"Convert these Neo4j Cypher queries to Gremlin queries for Amazon Neptune"* | `database/neptune/` |
| 4.2 | Deploy LLM agents via Amazon Bedrock | Mohak | *"Refactor the LLM provider to use AWS Bedrock SDK (boto3) for Claude/Titan model invocation"* | `ai_models/llm/bedrock_provider.py` |
| 4.3 | Set up CloudWatch + OpenSearch telemetry pipeline | Sandarbh | *"Create AWS CDK/CloudFormation templates for CloudWatch metrics ingestion and OpenSearch log pipeline"* | `docker/aws/` |
| 4.4 | Deploy frontend to AWS (S3 + CloudFront or Amplify) | Aarnav | *"Create deployment scripts for Next.js to AWS Amplify with environment variables"* | `frontend/deploy.sh` |
| 4.5 | Create project presentation & demo video | Aarnav | *"Generate a presentation outline for GraphTriage covering: problem, architecture, demo, results, future work"* | `presentation/` |

---

## Git Workflow for 3 PCs

```
main (protected)
├── mohak/multi-agent       ← PC 1 pushes here
├── sandarbh/graph-backend  ← PC 2 pushes here
└── aarnav/frontend-data    ← PC 3 pushes here
```

### Rules:
1. Each member works on their **own branch**
2. Create **Pull Requests** to `main` for code review
3. Use **Git tags** for phase milestones: `v0.1-foundation`, `v0.2-core`, `v0.3-integrated`, `v1.0-final`
4. Daily sync via a shared channel/meet

---

## Integration Points (Contracts Between Teams)

> [!WARNING]  
> These API contracts must be agreed upon **before Phase 2** to prevent integration failures.

### Backend API Contract (Sandarbh → Mohak & Aarnav)

```python
# POST /api/rca/trigger
Request:  {"incident_id": str, "telemetry_window_minutes": int}
Response: {"rca_id": str, "status": "processing"}

# GET /api/rca/{rca_id}/result
Response: {"root_cause_node": str, "confidence": float, "evidence": [...], "agent_trace": [...]}

# WebSocket /ws/rca/{rca_id}
Messages: {"agent": "navigator|diagnoser|verifier", "status": str, "data": {...}}

# GET /api/graph/topology
Response: {"nodes": [...], "edges": [...], "fault_gradients": {...}}
```

### Agent Interface Contract (Mohak → Sandarbh)

```python
class AgentInput:
    subgraph: dict          # Neo4j subgraph data
    metrics: list[dict]     # Time-series metrics
    traces: list[dict]      # Distributed traces  
    logs: list[str]         # Log entries

class AgentOutput:
    root_cause: str
    confidence: float
    evidence: list[str]
    counterfactual_results: list[dict]
```

---

## User Review Required

> [!IMPORTANT]
> **Decision needed:** Should the team start with local development (Neo4j + Docker) and migrate to AWS later, or go AWS-first from day one? The plan above assumes local-first → AWS migration in Phase 4.

## Open Questions

1. **LLM Choice:** Should all 3 PCs use the same LLM API key (shared OpenAI/Gemini key) or should each PC use a different provider for testing?
2. **Dataset Priority:** Should Aarnav focus on synthetic data first, or start with public benchmarks (AIOps Challenge)?
3. **AWS Budget:** Is there an AWS Academy/student credit available, or should the demo stay Docker-local?
