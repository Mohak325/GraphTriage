# GRAPHTRIAGE: Project Presentation Slide Outline
**Graph-Augmented Multi-Agent Framework for Microservice Root Cause Analysis**

> **Course:** Cloud System Architecture (2025–2026)  
> **Team Members:**  
> - **Mohak Harsh** (PC 1 — Team Lead & Multi-Agent Architect)  
> - **Sandarbh Gupta** (PC 2 — Graph & Backend Engineer)  
> - **Aarnav Mishra** (PC 3 — Frontend & Evaluation Engineer)  
> **Repository:** `https://github.com/Mohak325/GraphTriage` (Branch: `feature/aarnav`)

---

## Slide 1: Title & Overview
- **Header:** GraphTriage: Scalable, Anti-Hallucinatory Root Cause Analysis in Microservice Topologies
- **Subtitle:** Combining Temporal Knowledge Graphs with Multi-Agent Adversarial Deliberation
- **Key Visual:** System architecture badge with tri-agent icons (Navigator, Diagnoser, Verifier) + Neo4j/Neptune graph.
- **Presenter:** Mohak Harsh (Intro)
- **Talking Points:**
  - Modern cloud native microservices consist of hundreds of interdependent services.
  - When an outage occurs, cascading failures trigger thousands of correlated alerts.
  - GraphTriage cuts diagnosis time from hours to seconds while preventing AI hallucinations.

---

## Slide 2: The Problem — Microservice Outage Cascades & Alert Storms
- **The Challenge:**
  - **Cascading Failures:** A single bottleneck (e.g. database lock or thread starvation) triggers failures across dozens of upstream callers.
  - **Alert Fatigue:** On-call engineers are inundated with 10,000+ alerts per incident.
  - **High MTTR:** Average enterprise MTTD/MTTR remains 28+ minutes, costing ~$9,000/minute of downtime.
- **Visuals:** Diagram showing single faulty node at backend tier propagating HTTP 504 errors upstream through cart and gateway tiers.
- **Presenter:** Sandarbh Gupta

---

## Slide 3: Research Gap — Why Existing Approaches Fail
- **Traditional Graph Algorithms (MicroCause, CloudRanger, Random Walk):**
  - Rely purely on topology or correlation metrics; blind to semantic logs, trace payloads, and software exceptions.
  - Suffer from $O(V^2)$ computational explosion on 500+ node topologies.
- **Ungrounded LLMs (Standard GPT-4 / Claude RCA):**
  - High hallucination rate (**28.4%** in empirical tests).
  - Produce plausible-sounding but structurally impossible diagnoses (e.g., claiming a frontend bug caused a downstream database dead lock).
  - Lack awareness of runtime topology and dependency constraints.
- **Presenter:** Mohak Harsh

---

## Slide 4: The GraphTriage Architecture
- **Novel Core Contribution:** A dual-layer framework:
  1. **Graph Layer (Neo4j / Amazon Neptune):** Ingests live topology and computes upstream anomaly propagation gradients to prune search space.
  2. **Multi-Agent Deliberation Layer (LangGraph):** Tri-agent team operating under an adversarial verification protocol.
- **Diagram:**
  ```
  Telemetry Stream (Metrics + Spans + Logs)
                 │
                 ▼
  Temporal Knowledge Graph (Neo4j / Neptune)
                 │
                 ▼
        [Navigator Agent] ──(Pruned Subgraph)──► [Diagnoser Agent]
                 ▲                                       │
                 │                                       ▼
                 └──────(Adversarial Feedback)◄── [Verifier Agent]
                                                         │ (Accept)
                                                         ▼
                                            Verified RCA Report + UI
  ```
- **Presenter:** Mohak Harsh

---

## Slide 5: The Tri-Agent Deliberation Protocol
- **1. Navigator Agent:**
  - Traverses the knowledge graph starting from degraded perimeter nodes.
  - Uses fault gradient calculations to prune 500 nodes down to top-K candidate subgraph in $<120\text{ms}$.
- **2. Diagnoser Agent:**
  - Ingests multimodal telemetry (CPU, RAM, OpenTelemetry spans, thread stack traces) only for the candidate subgraph.
  - Performs LLM semantic reasoning to formulate structured root cause hypotheses with confidence scores.
- **3. Verifier Agent (The Innovation):**
  - Challenges hypotheses using counterfactual questions: *"If node X is restored, does symptom Y disappear?"*
  - Rejects false causal illusions; triggers loop-back to Navigator if evidence fails.
- **Presenter:** Mohak Harsh

---

## Slide 6: Anti-Hallucination via Adversarial Counterfactual Reasoning
- **Mechanism:**
  - Generative models frequently mistake downstream symptoms for root causes.
  - Verifier poses adversarial challenges against graph dependencies.
  - Evaluates hypothesis validity using statistical p-values and counterfactual perturbation testing.
- **Empirical Impact:**
  - Reduces hallucination rate from **28.4%** down to **2.1%** (a 92.6% reduction).
- **Presenter:** Aarnav Mishra

---

## Slide 7: Interactive Dashboard & Cytoscape.js Visualization
- **Next.js 14 App Router UI (Built by Aarnav Mishra):**
  - **Live Topology Canvas:** Cytoscape.js force-directed graph with real-time fault gradient coloring (green -> amber -> crimson).
  - **Animated Traversal Path:** Visualizes Navigator's path as it pinpoints the failure origin.
  - **Node Inspector Drawer:** Live CPU, memory, P95 latency, and error rate telemetry upon clicking any service.
  - **Agent Activity Monitor:** Real-time WebSocket timeline tracking Navigator, Diagnoser, and Verifier actions.
  - **RCA Results Panel:** Calibrated confidence gauge, evidence chain, counterfactual ACCEPT/REJECT breakdown, and copyable remediation CLI commands.
- **Presenter:** Aarnav Mishra

---

## Slide 8: Experimental Evaluation & Benchmark Results
- **Benchmark Suite (`results/benchmark.py` on AIOps Challenge datasets):**
  - Compared against 4 baselines: MicroCause, DéjàVu, CloudRanger, Standard LLM-RCA.
- **Key Metrics Table:**

| Method | Top-1 Accuracy | Top-3 Accuracy | Top-5 Accuracy | Latency P50 | Latency P99 | Hallucination Rate |
|---|:---:|:---:|:---:|:---:|:---:|:---:|
| MicroCause | 71.4% | 82.5% | 89.1% | 18.40s | 42.10s | 0.0% |
| DéjàVu | 74.8% | 84.6% | 90.3% | 12.60s | 31.80s | 0.0% |
| CloudRanger | 76.2% | 86.4% | 91.8% | 24.20s | 58.60s | 0.0% |
| Standard LLM-RCA | 76.5% | 85.0% | 89.4% | 8.50s | 19.20s | 28.4% |
| **GraphTriage (Ours)** | **94.6%** | **98.2%** | **99.4%** | **3.42s** | **7.15s** | **2.1%** |

- **Highlights:**
  - **+18.1% higher Top-1 Accuracy** over best existing baseline.
  - **72.8% reduction in MTTD** (3.42s vs 12.60s).
- **Presenter:** Aarnav Mishra

---

## Slide 9: Ablation Study — Validating Framework Contributions
- **Component Breakdown:**
  - Full GraphTriage: **94.6%**
  - Without Verifier (No counterfactual check): **85.2%** (-9.4%)
  - Without Navigator (No graph fault gradient): **78.4%** (-16.2%)
  - Raw LLM Prompting Only: **76.5%** (-18.1%)
- **Takeaway:** Both the graph-guided pruning and the adversarial counterfactual verifier are mathematically critical to achieving high accuracy and eliminating hallucinations.
- **Presenter:** Aarnav Mishra

---

## Slide 10: Cloud Deployment Architecture (AWS Phase 4)
- **AWS Cloud Production Topology:**
  - **Amazon Neptune:** High-availability graph database executing Gremlin queries.
  - **Amazon Bedrock:** Claude 3.5 Sonnet / Titan Foundation models for multi-agent reasoning.
  - **Amazon OpenSearch & CloudWatch:** Distributed trace indexing and time-series metrics.
  - **AWS Amplify:** Serverless hosting of Next.js 14 App Router dashboard with SSR and WebSocket streaming.
  - **Automated Deployment:** Implemented via `frontend/deploy.sh` and `frontend/amplify.yml`.
- **Presenter:** Sandarbh Gupta & Aarnav Mishra

---

## Slide 11: Live Demonstration Flow
- **Demo Scenario:** Injected CPU core starvation and mutex lock into `order-orchestrator`.
- **Step 1:** Ingress alerts trigger incident `INC-9821`.
- **Step 2:** Graph View shows fault gradient propagating upstream to `cart-service` and `web-frontend`.
- **Step 3:** Agent Monitor streams Navigator graph pruning, Diagnoser hypothesis, and Verifier counterfactual challenge in real-time.
- **Step 4:** RCA panel presents verified verdict, evidence chain, and actionable `kubectl` remediation command.
- **Presenter:** All Members

---

## Slide 12: Future Work & Conclusion
- **Summary of Achievements:**
  - Built an end-to-end graph-augmented multi-agent RCA system.
  - Delivered interactive Next.js 14 Cytoscape dashboard with live WebSocket streaming.
  - Validated 94.6% Top-1 accuracy and 2.1% hallucination rate on standard benchmarks.
- **Future Directions:**
  - Self-healing autonomous remediation execution via Kubernetes Operator.
  - Cross-region multi-cloud topology federation.
  - Integration with OpenTelemetry eBPF auto-instrumentation.
- **Q&A Session**
- **Presenter:** Mohak Harsh, Sandarbh Gupta, Aarnav Mishra
