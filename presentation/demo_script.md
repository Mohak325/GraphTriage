# GRAPHTRIAGE: Live Demonstration Script & Storyboard

> **Target Audience:** Professors, Cloud Architects, and Technical Evaluators  
> **Total Demo Duration:** 6–8 minutes  
> **Speaker Roles:**  
> - Mohak Harsh (Architectural Context & Intro)  
> - Sandarbh Gupta (Backend & Graph Engine)  
> - Aarnav Mishra (Live Dashboard Walkthrough & Evaluation Results)

---

## Demo Pre-requisites & Setup
1. **Frontend Dev Server:** Running on `http://localhost:3000` (`npm run dev` in `frontend/`)
2. **Synthetic Data & Topology:** Pre-generated via `python generator.py` and `python telemetry_generator.py`
3. **Target Incident:** `INC-9821` (CPU Starvation & Lock Contention in `order-orchestrator`)

---

## Segment 1: Introduction & Problem Context (1.5 mins)
**Speaker: Mohak Harsh**
- *"Good morning everyone. Today we are demonstrating **GRAPHTRIAGE**, our graph-augmented multi-agent root cause analysis engine for cloud native microservices."*
- *"When a complex microservice outage occurs, engineers are hit with alert storms. Symptoms cascade across dozens of services, masking the true root cause. Traditional tools either lack semantic understanding or ungrounded LLMs hallucinate inaccurate root causes."*
- *"GraphTriage solves this through a synergy: Neo4j/Neptune temporal knowledge graphs combined with a LangGraph tri-agent architecture featuring adversarial verification."*

---

## Segment 2: Dashboard Overview & KPI Metrics (1 min)
**Speaker: Aarnav Mishra**
- **Action:** Open `http://localhost:3000/dashboard` on screen.
- **Talking Points:**
  - *"Here is the GraphTriage executive dashboard, built with Next.js 14 App Router and Tailwind CSS in a sleek dark theme."*
  - Point to the 4 KPI cards:
    - *"Notice our **Mean Time to Diagnose is 3.2 minutes**, compared to the 28.4 minute industry baseline—an 88.7% reduction."*
    - *"Our benchmark **Top-1 accuracy stands at 94.6%**."*
    - *"At the top right, our Tri-Agent status widget shows all 3 agents—Navigator, Diagnoser, and Verifier—currently active."*
  - Point to the Recent Incidents table:
    - *"Here is our active incident `INC-9821`, detected with critical severity affecting checkout and cart flows."*
  - **Action:** Click on the **"Interactive Graph"** button in the header.

---

## Segment 3: Interactive Topology Graph & Fault Gradients (2 mins)
**Speaker: Aarnav Mishra & Sandarbh Gupta**
- **Action:** Navigate to `http://localhost:3000/graph`.
- **Talking Points:**
  - *"This canvas is powered by Cytoscape.js, dynamically rendering the active microservice topology graph."*
  - *"Notice the color coding based on our **Fault Propagation Gradient algorithm**:"*
    - Green nodes (`auth-service`, `catalog-service`) are healthy ($<0.2$).
    - Amber nodes (`cart-service`, `payment-gateway-proxy`) are degraded ($>0.3$).
    - Pulsing crimson nodes represent critical bottlenecks, with `order-orchestrator` at $1.0$.
  - **Action:** Click on `order-orchestrator` on the graph.
  - *"When I click `order-orchestrator`, the node inspector drawer slides out with correlated telemetry: CPU load is pinned at 98.6%, with 1420ms P95 latency and 28.5% error rate."*
  - **Action:** Point to the dashed cyan arrows.
  - *"The animated dashed path traces the Navigator agent's traversal route from the ingress load balancer directly down to the root cause."*
  - **Action:** Click **"Agent Monitor"** in the sidebar navigation.

---

## Segment 4: Real-time Multi-Agent Deliberation (2 mins)
**Speaker: Mohak Harsh & Aarnav Mishra**
- **Action:** Navigate to `http://localhost:3000/agents`.
- **Action:** Click the **"Simulate Stream"** button at the top right to start live streaming playback.
- **Talking Points:**
  - *"This page streams the live agent deliberation over our WebSocket interface `/ws/rca/{rca_id}`."*
  - *"Watch the sequence unfold:"*
    1. **Navigator Agent:** *"The Navigator analyzes the fault gradients, pruning the graph of 65 nodes down to a 4-node localized candidate subgraph in under 120ms."*
    2. **Diagnoser Agent:** *"The Diagnoser ingests metrics, distributed spans, and container logs for those 4 nodes, synthesizing a root cause hypothesis: CPU core starvation and thread contention."*
    3. **Verifier Agent (Our Novelty):** *"Now watch the Verifier engage in adversarial counterfactual reasoning. It challenges the hypothesis: 'If downstream database latency is neutralized, does the checkout stall persist?' The simulation confirms YES. The Verifier officially emits an **ACCEPT** verdict, eliminating false causal illusions."*
  - **Action:** Click **"RCA Diagnosis"** in the sidebar.

---

## Segment 5: Verified RCA Results & Actionable Remediation (1.5 mins)
**Speaker: Aarnav Mishra**
- **Action:** Navigate to `http://localhost:3000/rca`.
- **Talking Points:**
  - *"Here is the final verified RCA report:"*
    - *"Root cause isolated: `order-orchestrator` with **94.6% calibrated multi-agent confidence**."*
    - *"The **Multimodal Evidence Chain** compiles 6 correlated proofs across metrics, GC pauses, trace spans, and graph decay."*
    - *"The **Counterfactual Verification panel** explicitly shows why alternative hypotheses (e.g. gateway timeout or DB write lock) were **REJECTED**, while CPU core starvation was **ACCEPTED**."*
    - *"Finally, our **Actionable Remediation Playbook** provides immediate operational fixes, including one-click copyable Kubernetes scaling commands:"*
      - `kubectl scale deployment order-orchestrator --replicas=8`
- **Action:** Click the copy button next to the command to show interactive feedback.

---

## Segment 6: Benchmark Results & Conclusion (1 min)
**Speaker: All Members**
- **Action:** Display comparison charts from `results/charts/` (or reference the benchmark metrics).
- **Talking Points:**
  - *"Across 100 benchmark incidents on AIOps Challenge datasets, GraphTriage delivers:"*
    - **94.6% Top-1 Accuracy** (+18.1% over MicroCause and DéjàVu).
    - **72.8% reduction in diagnosis latency**.
    - **Hallucination rate reduced from 28.4% down to 2.1%** thanks to our adversarial Verifier.
  - *"The Next.js 14 frontend is fully prepared for AWS Amplify deployment with `deploy.sh` and `amplify.yml`."*
  - *"Thank you, and we welcome any questions!"*
