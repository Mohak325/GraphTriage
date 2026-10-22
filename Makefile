.PHONY: setup test test-backend test-frontend lint run run-backend run-frontend deploy schemas clean help

PYTHON ?= python3
NPM ?= npm

help:
	@echo "Carrier-Grade Telecom Cloud RCA Subsystem (Person C)"
	@echo "Available commands:"
	@echo "  make setup        Install all backend and frontend dependencies"
	@echo "  make test         Execute full backend (pytest >=85%) and frontend (vitest) test suites"
	@echo "  make lint         Run linting and static type checking (ruff, mypy, tsc)"
	@echo "  make run          Launch FastAPI backend (:8000) and Vite frontend (:3000) locally"
	@echo "  make schemas      Regenerate JSON Schemas and OpenAPI spec from Pydantic models"
	@echo "  make deploy       Deploy Person C AWS infrastructure (Terraform / CDK)"
	@echo "  make clean        Remove build artifacts and temporary caches"

setup:
	@echo "--> Installing Python dependencies..."
	$(PYTHON) -m pip install -q -r <(echo "fastapi uvicorn[standard] pydantic pydantic-settings httpx pyyaml pytest pytest-asyncio pytest-cov ruff mypy")
	@echo "--> Installing Frontend dependencies..."
	cd frontend && $(NPM) install

schemas:
	@echo "--> Generating Contract JSON Schemas and OpenAPI spec..."
	$(PYTHON) scripts/generate_schemas.py

test: test-backend test-frontend

test-backend:
	@echo "--> Running Python backend test suite (pytest >=85% target)..."
	PYTHONPATH=. $(PYTHON) -m pytest backend/tests -v --cov=backend/app --cov=contracts/pydantic --cov-report=term-missing

test-frontend:
	@echo "--> Running React frontend test suite (vitest)..."
	cd frontend && $(NPM) test

lint:
	@echo "--> Checking types and style..."
	-$(PYTHON) -m ruff check backend contracts
	-$(PYTHON) -m mypy backend/app contracts/pydantic --ignore-missing-imports
	cd frontend && $(NPM) run build

run:
	@echo "--> Starting local development services..."
	@echo "Backend:  http://localhost:8000"
	@echo "Frontend: http://localhost:3000"
	@trap 'kill 0' EXIT; \
	PYTHONPATH=. $(PYTHON) -m uvicorn backend.app.main:app --host 0.0.0.0 --port 8000 & \
	(cd frontend && $(NPM) run dev) & \
	wait

run-backend:
	PYTHONPATH=. $(PYTHON) -m uvicorn backend.app.main:app --host 0.0.0.0 --port 8000 --reload

run-frontend:
	cd frontend && $(NPM) run dev

deploy:
	@echo "--> Deploying Person C AWS Infrastructure (Step Functions, API Gateway, Amplify, EventBridge, SSM)..."
	cd infra/terraform && terraform init && terraform apply -auto-approve

clean:
	rm -rf .pytest_cache backend/tests/.pytest_cache .coverage
	rm -rf frontend/dist frontend/node_modules/.vite
	find . -type d -name "__pycache__" -exec rm -rf {} +
