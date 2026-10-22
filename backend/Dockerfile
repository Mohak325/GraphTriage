FROM python:3.12-slim

WORKDIR /workspace

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy backend requirements and install
COPY backend/pyproject.toml /workspace/backend/
RUN pip install --no-cache-dir \
    fastapi \
    "uvicorn[standard]" \
    pydantic \
    pydantic-settings \
    httpx \
    pyyaml \
    pytest \
    pytest-asyncio \
    pytest-cov

# Copy contracts, backend, and knowledge base
COPY contracts /workspace/contracts
COPY backend /workspace/backend

ENV PYTHONPATH=/workspace

EXPOSE 8000

CMD ["uvicorn", "backend.app.main:app", "--host", "0.0.0.0", "--port", "8000"]
