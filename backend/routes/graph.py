"""Graph query and topology visualization endpoints.

Integrates directly with Neo4jClient and FaultGradientEngine to provide
live topology graphs, k-hop subgraphs, and spectral heatmap analytics.
"""

from typing import List, Dict, Any, Optional
from fastapi import APIRouter, HTTPException, Query, Request
from pydantic import BaseModel, Field
import networkx as nx

from backend.config import get_settings
from ai_models.graph_engine.fault_gradient import FaultGradientEngine
from ai_models.graph_engine.topology_builder import TopologyBuilder

router = APIRouter(prefix="/api/graph", tags=["Graph & Topology"])
settings = get_settings()
engine = FaultGradientEngine(alpha=settings.FAULT_GRADIENT_ALPHA, epsilon=settings.FAULT_GRADIENT_EPSILON)
builder = TopologyBuilder()


# =============================================
# Cytoscape.js & Graph Schema Models
# =============================================

class NodeData(BaseModel):
    id: str
    label: str
    type: str = "service"
    status: str = "healthy"
    anomaly_score: float = 0.0
    failure_probability: float = 0.0
    rps: Optional[float] = None
    latency_p95: Optional[float] = None
    error_rate: Optional[float] = None
    properties: Dict[str, Any] = {}


class EdgeData(BaseModel):
    id: str
    source: str
    target: str
    label: str = "CALLS"
    weight: float = 1.0
    rps: Optional[float] = None
    latency_p95: Optional[float] = None
    error_rate: Optional[float] = None
    properties: Dict[str, Any] = {}


class CytoscapeElementNode(BaseModel):
    data: NodeData


class CytoscapeElementEdge(BaseModel):
    data: EdgeData


class CytoscapeGraphElements(BaseModel):
    nodes: List[CytoscapeElementNode] = []
    edges: List[CytoscapeElementEdge] = []


class CytoscapeTopologyResponse(BaseModel):
    elements: CytoscapeGraphElements
    total_nodes: int = 0
    total_edges: int = 0


class HeatmapNode(BaseModel):
    service_id: str
    service_name: str
    fault_gradient: float
    anomaly_score: float
    status: str
    criticality: str = "medium"


class GraphMetricsResponse(BaseModel):
    node_count: int
    edge_count: int
    density: float
    average_degree: float
    connected_components: int


# =============================================
# Default In-Memory Topology (12 Microservices)
# =============================================

def _build_default_in_memory_graph() -> nx.DiGraph:
    """Build the baseline 12-microservice e-commerce topology in NetworkX."""
    g = nx.DiGraph()

    services = [
        ("srv-api-gateway", "api-gateway", "gateway", "degraded", 0.72, 0.65, 3450.0, 420.5, 0.082),
        ("srv-auth-service", "auth-service", "auth", "healthy", 0.05, 0.02, 1200.0, 18.2, 0.001),
        ("srv-user-service", "user-service", "user", "healthy", 0.08, 0.04, 850.0, 35.0, 0.003),
        ("srv-order-service", "order-service", "business", "degraded", 0.81, 0.78, 920.0, 850.0, 0.145),
        ("srv-payment-service", "payment-service", "payment", "critical", 0.96, 0.94, 410.0, 2450.0, 0.380),
        ("srv-inventory-service", "inventory-service", "inventory", "degraded", 0.65, 0.52, 600.0, 390.0, 0.095),
        ("srv-shipping-service", "shipping-service", "logistics", "healthy", 0.12, 0.06, 220.0, 48.0, 0.005),
        ("srv-notification-service", "notification-service", "messaging", "healthy", 0.09, 0.03, 480.0, 22.0, 0.002),
        ("srv-recommendation-service", "recommendation-service", "ml-service", "healthy", 0.15, 0.08, 750.0, 85.0, 0.008),
        ("srv-analytics-service", "analytics-service", "data-pipeline", "healthy", 0.04, 0.01, 1500.0, 15.0, 0.001),
        ("srv-billing-service", "billing-service", "finance", "healthy", 0.11, 0.05, 180.0, 62.0, 0.004),
        ("srv-search-service", "search-service", "search", "healthy", 0.18, 0.09, 1100.0, 55.0, 0.006),
    ]

    for sid, name, stype, status, anom, fail, rps, lat, err in services:
        g.add_node(
            sid,
            id=sid,
            name=name,
            label=name,
            type=stype,
            status=status,
            anomaly_score=anom,
            failure_probability=fail,
            rps=rps,
            latency_p95=lat,
            error_rate=err
        )

    edges = [
        ("srv-api-gateway", "srv-auth-service", 0.35, 1200.0, 18.2, 0.001),
        ("srv-api-gateway", "srv-user-service", 0.25, 850.0, 35.0, 0.003),
        ("srv-api-gateway", "srv-order-service", 0.20, 920.0, 850.0, 0.145),
        ("srv-api-gateway", "srv-search-service", 0.12, 1100.0, 55.0, 0.006),
        ("srv-api-gateway", "srv-recommendation-service", 0.08, 750.0, 85.0, 0.008),
        ("srv-order-service", "srv-payment-service", 0.45, 410.0, 2450.0, 0.380),
        ("srv-order-service", "srv-inventory-service", 0.30, 600.0, 390.0, 0.095),
        ("srv-order-service", "srv-shipping-service", 0.15, 220.0, 48.0, 0.005),
        ("srv-order-service", "srv-notification-service", 0.10, 480.0, 22.0, 0.002),
        ("srv-payment-service", "srv-billing-service", 0.50, 180.0, 62.0, 0.004),
        ("srv-payment-service", "srv-notification-service", 0.50, 180.0, 22.0, 0.001),
        ("srv-search-service", "srv-inventory-service", 0.60, 500.0, 390.0, 0.040),
        ("srv-recommendation-service", "srv-user-service", 0.40, 300.0, 35.0, 0.003),
        ("srv-analytics-service", "srv-order-service", 0.10, 100.0, 15.0, 0.001),
        ("srv-analytics-service", "srv-payment-service", 0.10, 80.0, 15.0, 0.001)
    ]

    for src, tgt, weight, rps, lat, err in edges:
        g.add_edge(src, tgt, weight=weight, rps=rps, latency_p95=lat, error_rate=err)

    return g


# Global in-memory topology state (synchronized with live ingestion)
ACTIVE_GRAPH = _build_default_in_memory_graph()


async def _get_current_graph(request: Request) -> nx.DiGraph:
    """Retrieve graph from active Neo4j connection pool if available, otherwise return in-memory graph."""
    client = getattr(request.app.state, "neo4j_client", None)
    if client:
        try:
            g = await client.to_networkx_graph()
            if g.number_of_nodes() > 0:
                return g
        except Exception:
            pass
    return ACTIVE_GRAPH


# =============================================
# API Endpoints
# =============================================

@router.get("/topology", response_model=CytoscapeTopologyResponse)
async def get_topology(
    request: Request,
    format: str = Query("cytoscape", description="Format: 'cytoscape' or 'standard'")
):
    """Retrieve full microservice topology graph formatted for Cytoscape.js."""
    g = await _get_current_graph(request)
    cytoscape_dict = builder.to_cytoscape_elements(g)

    nodes = [CytoscapeElementNode(**n) for n in cytoscape_dict["elements"]["nodes"]]
    edges = [CytoscapeElementEdge(**e) for e in cytoscape_dict["elements"]["edges"]]

    return CytoscapeTopologyResponse(
        elements=CytoscapeGraphElements(nodes=nodes, edges=edges),
        total_nodes=len(nodes),
        total_edges=len(edges)
    )


@router.get("/subgraph/{service_id}", response_model=CytoscapeTopologyResponse)
async def get_service_subgraph(
    service_id: str,
    request: Request,
    hops: int = Query(default=1, ge=1, le=4, description="Ego network hop distance")
):
    """Retrieve a localized k-hop neighborhood around a target service."""
    g = await _get_current_graph(request)
    if not g.has_node(service_id):
        raise HTTPException(status_code=404, detail=f"Service '{service_id}' not found in graph topology.")

    subgraph = nx.ego_graph(g, service_id, radius=hops, undirected=True)
    cytoscape_dict = builder.to_cytoscape_elements(subgraph)

    nodes = [CytoscapeElementNode(**n) for n in cytoscape_dict["elements"]["nodes"]]
    edges = [CytoscapeElementEdge(**e) for e in cytoscape_dict["elements"]["edges"]]

    return CytoscapeTopologyResponse(
        elements=CytoscapeGraphElements(nodes=nodes, edges=edges),
        total_nodes=len(nodes),
        total_edges=len(edges)
    )


@router.get("/heatmap", response_model=List[HeatmapNode])
async def get_fault_heatmap(request: Request):
    """Compute and retrieve fault risk gradient heatmap scores across all microservices using spectral diffusion."""
    g = await _get_current_graph(request)
    result = engine.compute(g)

    heatmap_nodes = []
    for node in result.ranked_nodes:
        sid = node.service_id
        g_val = node.gradient
        init_anom = node.initial_anomaly_score

        criticality = "high" if sid in ("srv-payment-service", "srv-order-service", "srv-api-gateway") else "medium"

        heatmap_nodes.append(HeatmapNode(
            service_id=sid,
            service_name=node.service_name,
            fault_gradient=g_val,
            anomaly_score=init_anom,
            status=node.status,
            criticality=criticality
        ))

    return heatmap_nodes


@router.get("/metrics", response_model=GraphMetricsResponse)
async def get_graph_metrics(request: Request):
    """Return structural graph characteristics and topological connectivity metrics."""
    g = await _get_current_graph(request)
    node_count = g.number_of_nodes()
    edge_count = g.number_of_edges()

    density = nx.density(g) if node_count > 1 else 0.0
    avg_deg = (edge_count / node_count) if node_count > 0 else 0.0
    comp_count = nx.number_weakly_connected_components(g) if node_count > 0 else 0

    return GraphMetricsResponse(
        node_count=node_count,
        edge_count=edge_count,
        density=round(density, 4),
        average_degree=round(avg_deg, 2),
        connected_components=comp_count
    )
