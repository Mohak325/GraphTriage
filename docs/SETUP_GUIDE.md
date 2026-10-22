# Developer & Operations Setup Guide (Person C Subsystem)

This guide covers building, testing, running, and deploying the **Person C Subsystem** (Agentic AI, SLA Liability & Carrier NOC Portal).

---

## 1. Prerequisites

- **Python**: 3.11 or 3.12 (`python3 --version`)
- **Node.js**: v20+ or v22+ (`node --version`)
- **npm**: 10+ (`npm --version`)
- **Docker & Docker Compose**: Optional, for containerized local execution
- **Terraform / AWS CLI**: Optional, for cloud deployment

---

## 2. Quickstart via Makefile

The repository includes a top-level `Makefile` automating all workflows:

```bash
# 1. Install all dependencies (Python backend + React frontend)
make setup

# 2. Run full test suite (pytest >=85% target + vitest frontend)
make test

# 3. Start local development servers (Backend :8000, Frontend :3000)
make run
```

---

## 3. Environment Variables Configuration

Copy `.env.example` to `.env`:

```bash
cp .env.example .env
```

### Key Configuration Variables:

| Variable | Default | Purpose |
|---|---|---|
| `USE_FIXTURES` | `true` | When `true`, uses fixture-backed clients reading static JSON files. When `false`, connects to live Person A/B endpoints. |
| `MOCK_BEDROCK` | `true` | When `true`, performs deterministic offline LLM reasoning. When `false`, calls AWS Bedrock Claude 3.5 Sonnet directly via boto3. |
| `BEDROCK_MODEL_ID` | `anthropic.claude-3-5-sonnet-20241022-v2:0` | Bedrock model identifier. |
| `AGORA_WINDOW_SECONDS`| `5.0` | Maximum time window in seconds for live telemetry estimation before mutating actuation. |
| `HITL_SECRET_KEY` | *(Secret string)* | Secret key for HMAC-SHA256 signing of approval tokens. |
| `HITL_TOKEN_EXPIRY_MINUTES` | `60` | Token expiration duration in minutes. |
| `LASM_HIGH_PENALTY_THRESHOLD` | `0.30` | Trust score below which 30% MRC penalty is assessed. |
| `LASM_MED_PENALTY_THRESHOLD` | `0.60` | Trust score range [0.30, 0.60) assessing 20% MRC penalty. |
| `LASM_LOW_PENALTY_THRESHOLD` | `0.80` | Trust score range [0.60, 0.80) assessing 10% MRC penalty. |

---

## 4. Running Tests

### Backend Test Suite (Pytest)
```bash
make test-backend
# Or directly:
PYTHONPATH=. python3 -m pytest backend/tests -v --cov=backend/app --cov=contracts/pydantic --cov-report=term-missing
```

The backend test suite validates:
- **Contract Schemas**: Contract 1, 2, and 3 Pydantic v2 models.
- **Reference Example**: Exact reproduction of `INC-2026-0042` from `IMPLEMENTATION_PLAN.md`.
- **LASM Multi-Tenant Cases**: Test cases `CS1` through `CS8`.
- **AGORA Guardrails**: State-estimation-before-actuation compliance and blocking.
- **TN-AutoRCA Sandbox**: AST security validation, SHA-256 integrity, and $\ge +25\%$ F1 gain.
- **HITL Cryptographic Security**: HMAC integrity, single-use replay defense, and expiration.
- **Telecom Domain Rules**: Validation of all 52 YAML failure propagation rules.

### Frontend Test Suite (Vitest)
```bash
make test-frontend
# Or directly:
cd frontend && npm test
```

---

## 5. Running with Docker Compose

To launch the isolated Person C stack in Docker (Backend + Frontend ONLY):

```bash
docker compose up --build
```

- **Backend REST & WebSocket**: `http://localhost:8000`
- **Carrier NOC Dashboard**: `http://localhost:3000`
- **Health Check**: `http://localhost:8000/healthz`
- **Swagger / OpenAPI UI**: `http://localhost:8000/docs`

---

## 6. AWS Cloud Deployment (Terraform)

To deploy Person C infrastructure to AWS:

```bash
make deploy
# Or directly:
cd infra/terraform
terraform init
terraform apply -auto-approve
```

Resources provisioned:
- AWS Step Functions state machine (Amazon States Language ASL definition)
- Amazon API Gateway HTTP API for Contract 3 REST and WebSocket API
- AWS Systems Manager Automation Documents (`scale_amf_service`, `restart_vnf_container`)
- Amazon EventBridge custom bus and remediation rules
- Amazon SNS topic for carrier alerts
- Amazon S3 bucket for Amplify / CloudFront frontend hosting
