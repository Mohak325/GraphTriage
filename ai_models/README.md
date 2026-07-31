# AI Models — Multi-Agent Framework Core

## Purpose
This folder contains the core multi-agent framework of GRAPHTRIAGE, including the three specialized agents, the graph engine, and LLM integration modules.

## Structure
```
ai_models/
├── agents/          # Navigator, Diagnoser, and Verifier agent implementations
├── graph_engine/    # Neo4j integration and fault gradient computation
├── llm/             # LLM provider wrappers and prompt templates
└── README.md        # This file
```

## Agents Overview
| Agent | Responsibility | Primary Input | Output |
|-------|---------------|---------------|--------|
| Navigator | Graph traversal & anomaly localization | Fault gradients, topology graph | Localized subgraph |
| Diagnoser | Semantic analysis of multimodal data | Subgraph + metrics/traces/logs | Root cause hypothesis |
| Verifier | Adversarial validation of diagnosis | Hypothesis + evidence | Confirmed/rejected diagnosis |

## Status
> **Not yet implemented** — This folder is a placeholder for future development.
