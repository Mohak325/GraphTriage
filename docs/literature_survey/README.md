# Literature Survey — GRAPHTRIAGE Project

## Purpose
This folder contains the comprehensive literature survey conducted as part of the GRAPHTRIAGE Project, covering existing work in Root Cause Analysis (RCA), AIOps, graph-based fault localization, and multi-agent systems.

---

## Survey Scope

The literature survey covers the following key areas:

### 1. Root Cause Analysis in Distributed Systems
| Paper / Work | Year | Key Contribution | Limitation |
|-------------|------|-------------------|------------|
| MicroCause (Li et al.) | 2022 | Causal inference for microservice RCA | Requires predefined causal graphs; no multimodal analysis |
| CloudRanger (Wang et al.) | 2018 | Random walk on service call graphs | Limited to metric-based anomaly detection; no semantic reasoning |
| MicroScope (Lin et al.) | 2018 | Front-end request trace analysis | Single-modal (traces only); no graph-based localization |
| AutoMAP (Ma et al.) | 2020 | Automated metric-based anomaly propagation | Relies on metric correlation; misses log/trace signals |

### 2. AIOps and LLM-Based Approaches
| Paper / Work | Year | Key Contribution | Limitation |
|-------------|------|-------------------|------------|
| RCACopilot (Chen et al.) | 2024 | LLM-powered RCA for cloud incidents | Susceptible to hallucinations; no structural grounding |
| D-Bot (Zhou et al.) | 2024 | LLM-based database diagnosis | Domain-specific to databases; no network topology awareness |
| OpsEval (Liu et al.) | 2024 | Benchmark for LLM-based IT operations | Evaluation-only; no framework for deployment |
| AIOps Handbook (Dang et al.) | 2019 | Survey of AI for IT operations | Pre-LLM era; primarily statistical methods |

### 3. Graph-Based Fault Localization
| Paper / Work | Year | Key Contribution | Limitation |
|-------------|------|-------------------|------------|
| MonitorRank (Kim et al.) | 2013 | PageRank-based anomaly ranking on service graphs | Static graph; no dynamic fault propagation modeling |
| MicroHECL (Wu et al.) | 2020 | Heterogeneous graph learning for RCA | Requires extensive training data; not zero-shot capable |
| TraceAnomaly (Liu et al.) | 2020 | Trace-based anomaly detection using VAE | Single-modal; no integration with topology graphs |
| CausalRCA (Azam et al.) | 2022 | Causal discovery graphs for RCA | Computationally expensive causal discovery phase |

### 4. Multi-Agent Systems for Autonomous Operations
| Paper / Work | Year | Key Contribution | Limitation |
|-------------|------|-------------------|------------|
| AutoGen (Wu et al.) | 2023 | Framework for multi-agent LLM conversations | General-purpose; no domain-specific RCA capabilities |
| AgentScope (Gao et al.) | 2024 | Flexible multi-agent platform | No graph integration or structured traversal |
| MetaGPT (Hong et al.) | 2023 | Multi-agent software engineering | Focused on code generation; not applicable to network triage |
| CAMEL (Li et al.) | 2023 | Role-playing multi-agent communication | Lacks adversarial validation mechanisms |

---

## Key Findings

1. **No existing framework** combines graph-based topological traversal with LLM-powered multi-agent semantic analysis.
2. **Hallucination mitigation** in LLM-based RCA is largely unaddressed — most systems trust LLM outputs without adversarial validation.
3. **Multimodal data fusion** (metrics + traces + logs) remains underexplored in automated RCA pipelines.
4. **Fault gradient computation** on network graphs has not been applied to guide LLM-based diagnostic agents.

---

## References

> Full references with DOIs and publication venues will be added as the literature survey document is finalized.

---

## Files in This Folder

| File | Description |
|------|-------------|
| `README.md` | This overview document |
| `literature_survey.pdf` | *(To be added)* Full literature survey document |
| `references.bib` | *(To be added)* BibTeX references file |
