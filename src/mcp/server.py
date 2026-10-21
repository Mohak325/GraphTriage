"""
FastAPI Model Context Protocol (MCP) Telemetry Server.
Grounding: Paper 14 (MCP-Diag & NIKA, Chen et al., IJNM 2025/2026).
Exposes typed tool contracts for:
  - Prometheus PM metrics
  - 3GPP NWDAF (TS 23.288) analytics
  - Kubernetes CNF pod statuses & restart counts
  - Amazon Neptune / NetworkX topology neighbor traversal
Provides both standard REST and JSON-RPC 2.0 MCP interfaces with mock-mode support.
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
import json
from fastapi import FastAPI, HTTPException, Query, Body
from pydantic import BaseModel, Field
from structlog import get_logger

from src.graph.neptune_loader import TopologyGraphEngine

logger = get_logger()

# ----------------------------------------------------
# Request and Response Models for MCP Tools
# ----------------------------------------------------

class PrometheusQueryRequest(BaseModel):
    component_id: str = Field(description="e.g. amf-01, smf-02, router-edge-4")
    promql: str = Field(description="PromQL query expression, e.g. sum(rate(container_cpu_usage_seconds_total[1m]))")
    start_time: Optional[str] = Field(default=None, description="ISO-8601 start timestamp")
    end_time: Optional[str] = Field(default=None, description="ISO-8601 end timestamp")


class NWDAFQueryRequest(BaseModel):
    nf_type: str = Field(description="Target NF type: AMF, SMF, UPF, NRF")
    analytics_id: str = Field(description="3GPP TS 23.288 Analytics ID: NF_LOAD, SERVICE_EXPERIENCE, NETWORK_PERFORMANCE")
    time_window_seconds: int = Field(default=300, description="Time window in seconds")


class K8sStatusRequest(BaseModel):
    namespace: str = Field(default="5gc", description="Kubernetes namespace")
    pod_selector: str = Field(default="app=amf-01", description="Kubernetes label selector")


class TopologyQueryRequest(BaseModel):
    component_id: str = Field(description="Target component ID")
    hop_depth: int = Field(default=2, ge=1, le=5, description="Graph traversal hop depth")


class JSONRPCRequest(BaseModel):
    jsonrpc: str = "2.0"
    method: str
    params: Dict[str, Any] = Field(default_factory=dict)
    id: Optional[Any] = 1


class JSONRPCResponse(BaseModel):
    jsonrpc: str = "2.0"
    result: Optional[Any] = None
    error: Optional[Dict[str, Any]] = None
    id: Optional[Any] = 1


# ----------------------------------------------------
# Server Factory
# ----------------------------------------------------

def create_mcp_app(
    mock_mode: bool = True,
    graph_engine: Optional[TopologyGraphEngine] = None
) -> FastAPI:
    """Creates the FastAPI application with registered MCP tools."""
    app = FastAPI(
        title="Telecom RCA Model Context Protocol (MCP) Server",
        version="1.0.0",
        description="Standardized Agent Abstraction Layer exposing 3GPP NWDAF, K8s, Prometheus, and Neptune."
    )

    g_engine = graph_engine or TopologyGraphEngine()
    # Seed sample baseline topology for mock mode
    if mock_mode:
        g_engine.add_network_function("amf-01", "AMF", status="anomalous")
        g_engine.add_network_function("smf-01", "SMF", status="normal")
        g_engine.add_network_function("upf-edge-3", "UPF", status="degraded")
        g_engine.add_network_function("nrf-01", "NRF", status="normal")
        g_engine.add_call_dependency("amf-01", "smf-01", latency_ms=142.5)
        g_engine.add_call_dependency("smf-01", "upf-edge-3", latency_ms=35.0)
        g_engine.add_call_dependency("amf-01", "nrf-01", latency_ms=4.2)

    @app.get("/health")
    def health():
        return {
            "status": "healthy",
            "mock_mode": mock_mode,
            "timestamp": datetime.utcnow().isoformat()
        }

    # ----------------------------------------------------
    # Tool 1: Prometheus Metrics
    # ----------------------------------------------------
    @app.post("/tools/query_prometheus_metrics")
    def tool_query_prometheus(req: PrometheusQueryRequest) -> Dict[str, Any]:
        """Queries live or mock Prometheus PM counters."""
        if mock_mode:
            is_anomalous = "amf-01" in req.component_id
            val = 94.2 if is_anomalous else 24.5
            return {
                "status": "success",
                "component_id": req.component_id,
                "promql": req.promql,
                "data": {
                    "resultType": "matrix",
                    "result": [
                        {
                            "metric": {"__name__": "container_cpu_usage_ratio", "pod": f"{req.component_id}-pod-xyz"},
                            "values": [
                                [datetime.utcnow().timestamp() - 60, str(val - 5.0)],
                                [datetime.utcnow().timestamp(), str(val)]
                            ]
                        }
                    ]
                },
                "state_estimation_timestamp": datetime.utcnow().isoformat()
            }
        # In live mode, requests would query live Prometheus endpoint
        return {"status": "success", "component_id": req.component_id, "data": {}}

    # ----------------------------------------------------
    # Tool 2: 3GPP NWDAF Analytics
    # ----------------------------------------------------
    @app.post("/tools/query_nwdaf_analytics")
    def tool_query_nwdaf(req: NWDAFQueryRequest) -> Dict[str, Any]:
        """Queries 3GPP TS 23.288 Network Data Analytics Function (NWDAF)."""
        if mock_mode:
            return {
                "status": "success",
                "nf_type": req.nf_type,
                "analytics_id": req.analytics_id,
                "nf_load_statistics": {
                    "cpu_load_level": 88.5 if req.nf_type == "AMF" else 22.0,
                    "memory_load_level": 74.0,
                    "congestion_probability": 0.94 if req.nf_type == "AMF" else 0.05
                },
                "service_experience_score": 0.35 if req.nf_type == "AMF" else 0.98,
                "timestamp": datetime.utcnow().isoformat()
            }
        return {"status": "success", "nf_type": req.nf_type}

    # ----------------------------------------------------
    # Tool 3: Kubernetes Pod Status
    # ----------------------------------------------------
    @app.post("/tools/get_kubernetes_pod_status")
    def tool_get_k8s_status(req: K8sStatusRequest) -> Dict[str, Any]:
        """Queries Kubernetes CNF pod status, restart counts, and container events."""
        if mock_mode:
            is_faulty = "amf-01" in req.pod_selector
            return {
                "status": "success",
                "namespace": req.namespace,
                "selector": req.pod_selector,
                "pods": [
                    {
                        "pod_name": f"{req.pod_selector.split('=')[-1]}-79d4cf4b-abc",
                        "phase": "Running" if not is_faulty else "CrashLoopBackOff",
                        "ready": not is_faulty,
                        "restart_count": 8 if is_faulty else 0,
                        "cpu_limit": "2000m",
                        "cpu_current": "1980m" if is_faulty else "320m",
                        "last_termination_reason": "OOMKilled" if is_faulty else None
                    }
                ],
                "timestamp": datetime.utcnow().isoformat()
            }
        return {"status": "success", "namespace": req.namespace, "pods": []}

    # ----------------------------------------------------
    # Tool 4: Topology Neighbors Traversal
    # ----------------------------------------------------
    @app.post("/tools/query_topology_neighbors")
    def tool_query_topology(req: TopologyQueryRequest) -> Dict[str, Any]:
        """Queries graph neighbors within k hops from Neptune / NetworkX."""
        neighbors = g_engine.get_k_hop_neighbors(req.component_id, k=req.hop_depth)
        subgraph = g_engine.extract_incident_subgraph([req.component_id], hop_expansion=req.hop_depth)
        return {
            "status": "success",
            "component_id": req.component_id,
            "hop_depth": req.hop_depth,
            "neighbors": neighbors,
            "subgraph": subgraph.model_dump(),
            "timestamp": datetime.utcnow().isoformat()
        }

    # ----------------------------------------------------
    # MCP JSON-RPC 2.0 Handler
    # ----------------------------------------------------
    @app.post("/mcp")
    def handle_mcp_jsonrpc(rpc: JSONRPCRequest) -> JSONRPCResponse:
        """JSON-RPC 2.0 handler complying with Model Context Protocol."""
        method = rpc.method
        params = rpc.params

        try:
            if method == "tools/list":
                return JSONRPCResponse(
                    id=rpc.id,
                    result={
                        "tools": [
                            {
                                "name": "query_prometheus_metrics",
                                "description": "Query live Prometheus PM counters",
                                "inputSchema": PrometheusQueryRequest.model_json_schema()
                            },
                            {
                                "name": "query_nwdaf_analytics",
                                "description": "Query 3GPP NWDAF analytics",
                                "inputSchema": NWDAFQueryRequest.model_json_schema()
                            },
                            {
                                "name": "get_kubernetes_pod_status",
                                "description": "Query Kubernetes CNF pod status",
                                "inputSchema": K8sStatusRequest.model_json_schema()
                            },
                            {
                                "name": "query_topology_neighbors",
                                "description": "Query k-hop topology neighbors",
                                "inputSchema": TopologyQueryRequest.model_json_schema()
                            }
                        ]
                    }
                )
            elif method == "tools/call":
                tool_name = params.get("name")
                arguments = params.get("arguments", {})

                if tool_name == "query_prometheus_metrics":
                    res = tool_query_prometheus(PrometheusQueryRequest(**arguments))
                elif tool_name == "query_nwdaf_analytics":
                    res = tool_query_nwdaf(NWDAFQueryRequest(**arguments))
                elif tool_name == "get_kubernetes_pod_status":
                    res = tool_get_k8s_status(K8sStatusRequest(**arguments))
                elif tool_name == "query_topology_neighbors":
                    res = tool_query_topology(TopologyQueryRequest(**arguments))
                else:
                    return JSONRPCResponse(
                        id=rpc.id,
                        error={"code": -32601, "message": f"Method/Tool '{tool_name}' not found"}
                    )

                return JSONRPCResponse(
                    id=rpc.id,
                    result={"content": [{"type": "text", "text": json.dumps(res)}]}
                )
            else:
                return JSONRPCResponse(
                    id=rpc.id,
                    error={"code": -32601, "message": f"Unknown JSON-RPC method: {method}"}
                )
        except Exception as e:
            logger.error("JSON-RPC execution error", method=method, error=str(e))
            return JSONRPCResponse(
                id=rpc.id,
                error={"code": -32603, "message": f"Internal execution error: {str(e)}"}
            )

    return app


# Default app instance
app = create_mcp_app(mock_mode=True)
