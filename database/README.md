# Database — Schemas & Configurations

## Purpose
This folder contains the database schema definitions, migration scripts, and configuration files for the Neo4j graph database used by GRAPHTRIAGE.

## Planned Contents
- Neo4j schema definition (node labels, relationship types, properties)
- Cypher initialization scripts
- Database configuration templates
- Seed data for development/testing

## Neo4j Graph Schema (Planned)
```cypher
// Node Types
(:Service {id: STRING, name: STRING, type: STRING, status: STRING})
(:Host {id: STRING, hostname: STRING, cpu_cores: INT, memory_gb: FLOAT})
(:Network {id: STRING, subnet: STRING, bandwidth_mbps: INT})

// Relationship Types
(:Service)-[:CALLS {latency_ms: FLOAT, error_rate: FLOAT, rps: FLOAT}]->(:Service)
(:Service)-[:RUNS_ON]->(:Host)
(:Host)-[:CONNECTED_TO {bandwidth_mbps: INT}]->(:Network)
(:Service)-[:HAS_ANOMALY {score: FLOAT, timestamp: DATETIME}]->(:Anomaly)
```

## Status
> **Not yet implemented** — This folder is a placeholder for future development.
