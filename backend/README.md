# Backend — GRAPHTRIAGE REST API

## Purpose
This folder contains the **FastAPI** backend that exposes REST endpoints for triggering Root Cause Analysis, querying results, managing the network topology graph, and streaming real-time agent activity.

## Planned Features
- RCA trigger endpoint (POST `/api/v1/rca/trigger`)
- Results query endpoint (GET `/api/v1/rca/results/{incident_id}`)
- Agent status streaming via WebSocket
- Network topology CRUD operations
- Authentication and rate limiting

## Tech Stack
- **Framework:** FastAPI
- **Database:** Neo4j (via neo4j-driver)
- **Task Queue:** Celery + Redis (for async RCA execution)
- **Validation:** Pydantic v2
- **Documentation:** Auto-generated OpenAPI / Swagger

## Status
> **Not yet implemented** — This folder is a placeholder for future development.
