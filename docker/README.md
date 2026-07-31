# Docker — Containerization & Deployment

## Purpose
This folder will contain Docker configurations for containerizing and deploying all GRAPHTRIAGE services.

## Planned Contents
- `Dockerfile` for each service (backend, frontend, agents)
- `docker-compose.yml` for local development
- `docker-compose.prod.yml` for production deployment
- Kubernetes manifests (optional, for scaled deployment)
- Environment variable templates (`.env.example`)

## Services
| Service | Port | Description |
|---------|------|-------------|
| Backend API | 8000 | FastAPI REST server |
| Frontend | 3000 | Next.js dashboard |
| Neo4j | 7474/7687 | Graph database |
| Redis | 6379 | Task queue broker |

## Status
> 🔲 **Not yet implemented** — This folder is a placeholder for future development.
