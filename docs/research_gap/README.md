# Research Gap Analysis — GRAPHTRIAGE Project

## Purpose
This folder contains the research gap analysis identifying the specific shortcomings in existing RCA approaches that the GRAPHTRIAGE framework aims to address.

---

## Identified Research Gaps

### Gap 1: Hallucination in LLM-Based RCA

**Problem:** Current LLM-powered RCA tools (RCACopilot, D-Bot) generate diagnoses directly from observability data without structural grounding. This leads to plausible but incorrect root cause identifications — a phenomenon known as hallucination.

**Current State:** No existing framework incorporates adversarial validation to systematically challenge and verify LLM-generated diagnoses.

**GRAPHTRIAGE Solution:** The **Verifier Agent** implements an adversarial validation protocol that independently challenges the Diagnoser Agent's hypothesis with counter-evidence, alternative explanations, and logical consistency checks before accepting a diagnosis.

---

### Gap 2: Lack of Graph-LLM Integration

**Problem:** Graph-based approaches (MonitorRank, MicroHECL) perform structural analysis but lack semantic reasoning. LLM-based approaches have semantic understanding but lack topological awareness. No system bridges both.

**Current State:** Structural and semantic analyses are performed in isolation, leading to either:
- Topologically valid but semantically shallow diagnoses (graph-only)
- Semantically rich but structurally ungrounded diagnoses (LLM-only)

**GRAPHTRIAGE Solution:** The **Navigator Agent** performs deterministic graph traversal using fault gradients, then passes the localized subgraph to the **Diagnoser Agent** for LLM-powered semantic analysis. This separation ensures structural correctness while enabling deep reasoning.

---

### Gap 3: Single-Modal Data Analysis

**Problem:** Most existing RCA tools analyze only one type of observability data — typically metrics (time-series) or traces (request flows) — missing correlations across data modalities.

**Current State:**
| Approach | Metrics | Traces | Logs |
|----------|---------|--------|------|
| CloudRanger | ✅ | ❌ | ❌ |
| MicroScope | ❌ | ✅ | ❌ |
| TraceAnomaly | ❌ | ✅ | ❌ |
| AutoMAP | ✅ | ❌ | ❌ |
| **GRAPHTRIAGE** | **✅** | **✅** | **✅** |

**GRAPHTRIAGE Solution:** The **Diagnoser Agent** performs multimodal semantic analysis, correlating metrics anomalies with trace patterns and log entries to produce holistic diagnoses.

---

### Gap 4: No Autonomous Multi-Agent RCA Framework

**Problem:** Existing multi-agent frameworks (AutoGen, MetaGPT, CAMEL) are general-purpose and lack domain-specific capabilities for network triage. No multi-agent system has been designed specifically for RCA with role specialization.

**Current State:** RCA is either performed by monolithic AI systems or requires significant human-in-the-loop intervention.

**GRAPHTRIAGE Solution:** Three specialized agents — Navigator, Diagnoser, and Verifier — each handle a distinct aspect of the RCA workflow, emulating the division of labor in human SRE teams. The orchestrator coordinates their interaction through a state machine with feedback loops.

---

### Gap 5: Fault Gradient-Guided Traversal

**Problem:** Existing graph-based approaches use static ranking algorithms (PageRank, random walks) that do not account for dynamic fault propagation patterns.

**Current State:** Anomaly localization on graphs treats all edges equally or uses pre-computed weights, missing the temporal dynamics of cascading failures.

**GRAPHTRIAGE Solution:** The **Graph Engine** computes real-time fault gradients based on anomaly score propagation, enabling the Navigator Agent to follow the path of highest fault probability — similar to gradient descent on the topology.

---

## Summary Comparison

| Feature | Traditional RCA | LLM-Only RCA | Graph-Only RCA | **GRAPHTRIAGE (Ours)** |
|---------|----------------|--------------|----------------|-----------------|
| Automated Triage | ❌ | ✅ | ✅ | **✅** |
| Hallucination Prevention | N/A | ❌ | N/A | **✅** |
| Graph-Based Localization | ❌ | ❌ | ✅ | **✅** |
| Semantic Analysis | ❌ | ✅ | ❌ | **✅** |
| Multimodal Data Fusion | ❌ | Partial | ❌ | **✅** |
| Adversarial Validation | ❌ | ❌ | ❌ | **✅** |
| Multi-Agent Architecture | ❌ | ❌ | ❌ | **✅** |
| Fault Gradient Traversal | ❌ | ❌ | ❌ | **✅** |

---

## Files in This Folder

| File | Description |
|------|-------------|
| `README.md` | This research gap analysis |
| `research_gap_analysis.pdf` | *(To be added)* Detailed research gap document |
