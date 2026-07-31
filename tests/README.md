# Tests — Test Suites

## Purpose
This folder will contain all test suites for the GRAPHTRIAGE framework, including unit tests, integration tests, and end-to-end tests.

## Planned Test Categories
- **Unit Tests:** Individual agent logic, graph algorithms, API endpoints
- **Integration Tests:** Agent coordination, graph-agent interaction, API-frontend communication
- **End-to-End Tests:** Full RCA pipeline from data ingestion to diagnosis output
- **Benchmarking Tests:** Performance and accuracy evaluation scripts

## Planned Structure
```
tests/
├── unit/
│   ├── test_navigator_agent.py
│   ├── test_diagnoser_agent.py
│   ├── test_verifier_agent.py
│   └── test_fault_gradient.py
├── integration/
│   ├── test_agent_orchestration.py
│   └── test_graph_agent_pipeline.py
├── e2e/
│   └── test_full_rca_pipeline.py
└── conftest.py
```

## Status
> **Not yet implemented** — This folder is a placeholder for future development.
