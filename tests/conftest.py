"""Shared pytest fixtures and test configuration for GraphTriage test suites."""

import pytest
from typing import Dict, Any, List
import networkx as nx
from fastapi.testclient import TestClient

from backend.main import app
from backend.routes.graph import _build_default_in_memory_graph


@pytest.fixture(scope="session")
def client() -> TestClient:
    """FastAPI TestClient fixture."""
    return TestClient(app)


@pytest.fixture
def sample_topology() -> nx.DiGraph:
    """Provides a fresh copy of the 12-microservice topology."""
    return _build_default_in_memory_graph()


@pytest.fixture
def mock_trace_spans() -> List[Dict[str, Any]]:
    """Sample OpenTelemetry trace spans for testing trace ingestion and aggregation."""
    return [
        {
            "trace_id": "tr-001",
            "span_id": "sp-001",
            "caller_service_id": "srv-api-gateway",
            "callee_service_id": "srv-order-service",
            "endpoint": "/checkout",
            "duration_ms": 142.5,
            "http_status": 200,
            "has_error": False
        },
        {
            "trace_id": "tr-001",
            "span_id": "sp-002",
            "caller_service_id": "srv-order-service",
            "callee_service_id": "srv-payment-service",
            "endpoint": "/process-payment",
            "duration_ms": 2500.0,
            "http_status": 504,
            "has_error": True
        },
        {
            "trace_id": "tr-002",
            "span_id": "sp-003",
            "caller_service_id": "srv-order-service",
            "callee_service_id": "srv-payment-service",
            "endpoint": "/process-payment",
            "duration_ms": 2400.0,
            "http_status": 500,
            "has_error": True
        },
        {
            "trace_id": "tr-003",
            "span_id": "sp-004",
            "caller_service_id": "srv-api-gateway",
            "callee_service_id": "srv-auth-service",
            "endpoint": "/verify-token",
            "duration_ms": 15.2,
            "http_status": 200,
            "has_error": False
        }
    ]


@pytest.fixture
def mock_anomaly_event() -> Dict[str, Any]:
    """Sample anomaly event payload."""
    return {
        "id": "anom-payment-test-01",
        "service_id": "srv-payment-service",
        "metric_name": "http_request_duration_seconds_p95",
        "metric_value": 2.45,
        "threshold": 0.50,
        "severity": "critical",
        "confidence": 0.96,
        "timestamp": "2026-09-22T21:46:15Z"
    }
