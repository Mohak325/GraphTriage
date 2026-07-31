# Agents — GRAPHTRIAGE Multi-Agent System

## Purpose
This folder contains the implementations of the three core agents in the GRAPHTRIAGE framework.

## Agents

### 1. Navigator Agent
- Leverages computed fault gradients to traverse the network topology graph
- Identifies the most probable anomaly location using gradient-guided search
- Outputs a localized subgraph for the Diagnoser Agent

### 2. Diagnoser Agent
- Receives the localized subgraph from the Navigator
- Performs deep semantic analysis on associated metrics, traces, and logs
- Uses LLM reasoning to generate a root cause hypothesis with evidence

### 3. Verifier Agent
- Implements the adversarial validation protocol
- Systematically challenges the diagnosis with counter-evidence
- Either confirms the diagnosis (with confidence score) or rejects it (triggering re-analysis)

## Status
> 🔲 **Not yet implemented** — This folder is a placeholder for future development.
