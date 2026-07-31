# Architecture — Design Documents & Diagrams

## Purpose
This folder contains the architecture design documents, system diagrams, and technical specifications for the GRAPHTRIAGE framework.

## Contents
| File | Description |
|------|-------------|
| `architecture_diagram.png` | High-level system architecture diagram |
| `README.md` | This file |

## Architecture Layers
1. **Data Ingestion Layer** — Metrics, traces, and log collectors with multimodal preprocessing
2. **Graph Engine** — Neo4j topology graph with fault gradient computation
3. **Multi-Agent Orchestrator** — Navigator, Diagnoser, and Verifier agents
4. **Presentation Layer** — FastAPI backend + React/Next.js dashboard

## Status
> Architecture design is complete. Detailed component-level diagrams will be added during implementation.
