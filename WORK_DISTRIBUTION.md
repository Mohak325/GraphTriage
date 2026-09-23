# Work Distribution — GRAPHTRIAGE Project

> **Last Updated:** July 2025  
> **Course:** Cloud System Architecture

---

## Team Overview

| Member | Role |
|--------|------|
| Mohak Harsh | Team Lead / Multi-Agent Architect |
| Sandarbh Gupta | Graph & Backend Engineer |
| Aarnav Mishra | Frontend & Evaluation Engineer |

---

## Phase-Wise Task Allocation

### Phase 1: Research & Planning (Weeks 1–2)

| Task | Assignee | Status | Deliverable |
|------|----------|--------|-------------|
| Literature survey on RCA in distributed systems | All Members | Complete | `docs/literature_survey/` |
| Research gap analysis | All Members | Complete | `docs/research_gap/` |
| Architecture design & diagram | Mohak Harsh | Complete | `docs/architecture/` |
| Repository setup & folder structure | Mohak Harsh | Complete | Repository root |
| Technology stack finalization | All Members | Complete | `README.md` |
| Dataset identification & curation plan | Aarnav Mishra | Complete | `data/README.md` |

---

### Phase 2: Core Infrastructure (Weeks 3–5)

| Task | Assignee | Status | Deliverable |
|------|----------|--------|-------------|
| Neo4j schema design & setup | Sandarbh Gupta | Complete | `database/` |
| Network topology graph builder | Sandarbh Gupta | Complete | `ai_models/graph_engine/` |
| Fault gradient computation algorithm | Sandarbh Gupta | Complete | `ai_models/graph_engine/` |
| Synthetic data generation pipeline | Aarnav Mishra | Pending | `data/synthetic/` |
| FastAPI backend skeleton | Sandarbh Gupta | Complete | `backend/` |
| LangGraph multi-agent scaffold | Mohak Harsh | Pending | `ai_models/` |
| LLM provider integration (Gemini/GPT-4) | Mohak Harsh | Pending | `ai_models/llm/` |
| Docker environment setup | Sandarbh Gupta | Complete | `docker/` |

---

### Phase 3: Agent Development (Weeks 6–9)

| Task | Assignee | Status | Deliverable |
|------|----------|--------|-------------|
| **Navigator Agent** — graph traversal logic | Mohak Harsh | Pending | `ai_models/agents/` |
| **Navigator Agent** — fault gradient integration | Mohak Harsh + Sandarbh Gupta | Complete | `ai_models/agents/` |
| **Diagnoser Agent** — multimodal semantic analysis | Mohak Harsh | Pending | `ai_models/agents/` |
| **Diagnoser Agent** — LLM prompt engineering | Mohak Harsh | Pending | `ai_models/llm/` |
| **Verifier Agent** — adversarial validation protocol | Mohak Harsh | Pending | `ai_models/agents/` |
| Agent orchestration & state management | Mohak Harsh | Pending | `ai_models/` |
| Backend API endpoints for RCA | Sandarbh Gupta | Complete | `backend/` |
| Unit tests for backend & graph engine | Sandarbh Gupta | Complete | `tests/` |

---

### Phase 4: Frontend & AWS Cloud Deployment (Weeks 8–10)

| Task | Assignee | Status | Deliverable |
|------|----------|--------|-------------|
| React/Next.js project setup | Aarnav Mishra | Pending | `frontend/` |
| Network graph visualization (D3.js/Cytoscape) | Aarnav Mishra | Pending | `frontend/` |
| Real-time agent activity dashboard | Aarnav Mishra | Pending | `frontend/` |
| RCA results display & confidence scores | Aarnav Mishra | Pending | `frontend/` |
| API integration with backend | Aarnav Mishra + Sandarbh Gupta | Complete | `frontend/` |
| Responsive design & UX polish | Aarnav Mishra | Pending | `frontend/` |
| **Amazon Neptune Gremlin Migration** | Sandarbh Gupta | Complete | `database/neptune/` |
| **CloudWatch + OpenSearch Telemetry Pipeline** | Sandarbh Gupta | Complete | `docker/aws/` |

---

### Phase 5: Evaluation & Benchmarking (Weeks 10–12)

| Task | Assignee | Status | Deliverable |
|------|----------|--------|-------------|
| Benchmark suite design | Aarnav Mishra | Pending | `results/` |
| Accuracy evaluation (vs. baselines) | Aarnav Mishra + Mohak Harsh | Pending | `results/` |
| Latency & performance profiling | Sandarbh Gupta | Complete | `results/profiling/` |
| Hallucination rate measurement | Mohak Harsh | Pending | `results/` |
| Ablation studies (agent contributions) | All Members | Pending | `results/` |
| Results documentation & visualizations | Aarnav Mishra | Pending | `results/` |

---

### Phase 6: Documentation & Presentation (Weeks 11–12)

| Task | Assignee | Status | Deliverable |
|------|----------|--------|-------------|
| Final project report | All Members | Pending | `docs/` |
| Presentation slides | All Members | Pending | `presentation/` |
| Demo video / live demo preparation | Aarnav Mishra + Mohak Harsh | Pending | `presentation/` |
| README & documentation finalization | Mohak Harsh | Pending | Repository root |

---

## Responsibility Summary

### Mohak Harsh — Team Lead / Multi-Agent Architect
- Overall project architecture and design
- Multi-agent orchestration framework (LangGraph)
- All three agents: Navigator, Diagnoser, Verifier
- Adversarial validation protocol design
- LLM integration and prompt engineering
- Agent state management and coordination logic
- Repository management and documentation oversight

### Sandarbh Gupta — Graph & Backend Engineer
- Neo4j graph database setup and schema design
- Network topology graph construction and maintenance
- Fault gradient computation algorithms
- FastAPI backend development and API design
- Docker containerization and deployment configuration
- Performance profiling and optimization
- Graph query optimization (Cypher)

### Aarnav Mishra — Frontend & Evaluation Engineer
- React/Next.js dashboard development
- Interactive network graph visualization (D3.js / Cytoscape.js)
- Real-time monitoring UI components
- Synthetic dataset generation and curation
- Benchmarking suite design and execution
- Results analysis and visualization
- Presentation and demo preparation

---

## Collaboration Guidelines

- **Weekly Sync:** Team standup every Monday to discuss progress and blockers.
- **Code Reviews:** All PRs require at least one review from another team member.
- **Branch Strategy:** Feature branches (`feature/<name>`) merged into `dev`, then `main`.
- **Communication:** Discord/Slack channel for daily updates.
- **Documentation:** Every module must include inline documentation and a README.
