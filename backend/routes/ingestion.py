"""Data ingestion endpoints for telemetry metrics, distributed traces, logs, and topology updates.

Enriches the live graph topology, dynamically updates call edge weights,
and upserts entities into Neo4j.
"""

import time
import logging
from typing import List, Dict, Any, Optional
from fastapi import APIRouter, HTTPException, status, Request
from pydantic import BaseModel, Field

from backend.routes.graph import ACTIVE_GRAPH
from ai_models.graph_engine.topology_builder import TopologyBuilder

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/ingest", tags=["Data Ingestion"])
builder = TopologyBuilder()


# =============================================
# Ingestion Schemas
# =============================================

class MetricPoint(BaseModel):
    timestamp: float = Field(default_factory=time.time)
    service_id: str
    metric_name: str
    value: float
    labels: Dict[str, str] = {}


class MetricsIngestRequest(BaseModel):
    batch: List[MetricPoint] = Field(..., min_length=1)


class TraceSpan(BaseModel):
    trace_id: str
    span_id: str
    parent_span_id: Optional[str] = None
    caller_service_id: str
    callee_service_id: str
    endpoint: str
    duration_ms: float
    http_status: int = 200
    timestamp: float = Field(default_factory=time.time)


class TracesIngestRequest(BaseModel):
    spans: List[TraceSpan] = Field(..., min_length=1)


class LogEvent(BaseModel):
    timestamp: float = Field(default_factory=time.time)
    service_id: str
    log_level: str = "ERROR"
    message: str
    trace_id: Optional[str] = None
    metadata: Dict[str, Any] = {}


class LogsIngestRequest(BaseModel):
    events: List[LogEvent] = Field(..., min_length=1)


class ServiceNodeDescriptor(BaseModel):
    id: str
    name: str
    type: str = "business"
    version: Optional[str] = None
    language: Optional[str] = None


class DependencyEdgeDescriptor(BaseModel):
    source_service_id: str
    target_service_id: str
    protocol: str = "HTTP"
    weight: float = 1.0


class TopologySnapshotRequest(BaseModel):
    services: List[ServiceNodeDescriptor]
    dependencies: List[DependencyEdgeDescriptor]


class IngestionResponse(BaseModel):
    status: str = "accepted"
    ingested_count: int
    processed_at: float = Field(default_factory=time.time)
    message: Optional[str] = None


# =============================================
# Ingestion Endpoints
# =============================================

@router.post("/metrics", response_model=IngestionResponse, status_code=status.HTTP_202_ACCEPTED)
async def ingest_metrics(payload: MetricsIngestRequest, request: Request):
    """Ingest time-series metric batch and update live node attributes."""
    count = 0
    client = getattr(request.app.state, "neo4j_client", None)

    for pt in payload.batch:
        sid = pt.service_id
        if ACTIVE_GRAPH.has_node(sid):
            count += 1
            if "latency" in pt.metric_name.lower():
                ACTIVE_GRAPH.nodes[sid]["latency_p95"] = pt.value
            elif "error" in pt.metric_name.lower():
                ACTIVE_GRAPH.nodes[sid]["error_rate"] = pt.value
                if pt.value > 0.05:
                    ACTIVE_GRAPH.nodes[sid]["status"] = "degraded"
                if pt.value > 0.25:
                    ACTIVE_GRAPH.nodes[sid]["status"] = "critical"
            elif "rps" in pt.metric_name.lower() or "throughput" in pt.metric_name.lower():
                ACTIVE_GRAPH.nodes[sid]["rps"] = pt.value

    return IngestionResponse(
        status="accepted",
        ingested_count=len(payload.batch),
        message=f"Enriched active graph with {count} matched service metrics."
    )


@router.post("/traces", response_model=IngestionResponse, status_code=status.HTTP_202_ACCEPTED)
async def ingest_traces(payload: TracesIngestRequest, request: Request):
    """Ingest OpenTelemetry trace spans to dynamically update CALLS edge weights."""
    span_dicts = [s.model_dump() for s in payload.spans]
    trace_subgraph = builder.build_from_traces(span_dicts)

    # Merge newly inferred edges into ACTIVE_GRAPH
    for u, v in trace_subgraph.edges():
        data = trace_subgraph.get_edge_data(u, v) or {}
        if ACTIVE_GRAPH.has_edge(u, v):
            # Update edge weight
            ACTIVE_GRAPH[u][v]["weight"] = data.get("weight", 1.0)
            if "latency_p95" in data:
                ACTIVE_GRAPH[u][v]["latency_p95"] = data["latency_p95"]
            if "error_rate" in data:
                ACTIVE_GRAPH[u][v]["error_rate"] = data["error_rate"]
        else:
            ACTIVE_GRAPH.add_edge(u, v, **data)

    return IngestionResponse(
        status="accepted",
        ingested_count=len(payload.spans),
        message=f"Aggregated {len(payload.spans)} spans into {trace_subgraph.number_of_edges()} call graph edges."
    )


@router.post("/logs", response_model=IngestionResponse, status_code=status.HTTP_202_ACCEPTED)
async def ingest_logs(payload: LogsIngestRequest):
    """Ingest log error streams for cross-correlation with graph anomalies."""
    count = len(payload.events)
    # Mark associated services as having error events
    for event in payload.events:
        sid = event.service_id
        if ACTIVE_GRAPH.has_node(sid) and event.log_level.upper() in ("ERROR", "FATAL", "CRITICAL"):
            current_score = ACTIVE_GRAPH.nodes[sid].get("anomaly_score", 0.0)
            ACTIVE_GRAPH.nodes[sid]["anomaly_score"] = min(current_score + 0.1, 1.0)

    return IngestionResponse(
        status="accepted",
        ingested_count=count,
        message=f"Correlated {count} log events; adjusted node risk priors."
    )


@router.post("/topology", response_model=IngestionResponse, status_code=status.HTTP_201_CREATED)
async def ingest_topology(payload: TopologySnapshotRequest, request: Request):
    """Upsert microservice topology definitions and dependencies."""
    node_count = 0
    edge_count = 0

    for s in payload.services:
        ACTIVE_GRAPH.add_node(
            s.id,
            id=s.id,
            name=s.name,
            label=s.name,
            type=s.type,
            status="healthy",
            anomaly_score=0.0
        )
        node_count += 1

    for d in payload.dependencies:
        ACTIVE_GRAPH.add_edge(
            d.source_service_id,
            d.target_service_id,
            protocol=d.protocol,
            weight=d.weight
        )
        edge_count += 1

    return IngestionResponse(
        status="created",
        ingested_count=node_count + edge_count,
        message=f"Added/updated {node_count} nodes and {edge_count} dependency edges in active graph."
    )
