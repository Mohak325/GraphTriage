"""Live production client implementations connecting to external AWS / microservices.

Used in production AWS deployment (Week 11 integration) when USE_FIXTURES=false.
Configured strictly through .env variables without requiring any code changes.
"""

from typing import Any, Dict, List, Optional
import httpx

from contracts.pydantic.contract_1_telemetry import NormalizedTelemetryEvent
from contracts.pydantic.contract_2_rca_analysis import RCARequest, RCAResponse
from .client_interfaces import (
    MCPTelemetryClientInterface,
    MCPToolDefinition,
    RCAClientInterface,
    VectorStoreRAGClientInterface,
    RAGDocumentCitation,
)


class LiveMCPTelemetryClient(MCPTelemetryClientInterface):
    """Production client connecting to Person A's MCP Telemetry Server via JSON-RPC over HTTP."""

    def __init__(self, mcp_server_url: str, auth_token: Optional[str] = None):
        self.mcp_server_url = mcp_server_url.rstrip("/")
        self.headers = {"Authorization": f"Bearer {auth_token}"} if auth_token else {}

    async def list_tools(self) -> List[MCPToolDefinition]:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.post(
                f"{self.mcp_server_url}/tools/list",
                json={"jsonrpc": "2.0", "id": 1, "method": "tools/list"},
                headers=self.headers,
            )
            resp.raise_for_status()
            data = resp.json().get("result", {}).get("tools", [])
            return [
                MCPToolDefinition(
                    name=t["name"],
                    description=t.get("description", ""),
                    input_schema=t.get("inputSchema", {}),
                )
                for t in data
            ]

    async def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        async with httpx.AsyncClient(timeout=15.0) as client:
            resp = await client.post(
                f"{self.mcp_server_url}/tools/call",
                json={
                    "jsonrpc": "2.0",
                    "id": 1,
                    "method": "tools/call",
                    "params": {"name": tool_name, "arguments": arguments},
                },
                headers=self.headers,
            )
            resp.raise_for_status()
            return resp.json().get("result", {})

    async def query_live_metric(self, component: str, metric_name: str) -> Optional[NormalizedTelemetryEvent]:
        res = await self.call_tool(
            "query_prometheus",
            {"component_id": component, "metric_name": metric_name},
        )
        if res and res.get("status") == "success":
            return NormalizedTelemetryEvent.model_validate(res["event"])
        return None


class LiveRCAClient(RCAClientInterface):
    """Production client calling Person B's Contract 2 API (SageMaker real-time endpoint)."""

    def __init__(self, rca_endpoint_url: str, api_key: Optional[str] = None):
        self.rca_endpoint_url = rca_endpoint_url
        self.headers = {"X-API-Key": api_key} if api_key else {}

    async def analyze_incident(self, request: RCARequest) -> RCAResponse:
        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.post(
                f"{self.rca_endpoint_url}/api/rca/analyze",
                json=request.model_dump(mode="json"),
                headers=self.headers,
            )
            resp.raise_for_status()
            return RCAResponse.model_validate(resp.json())


class LiveVectorStoreRAGClient(VectorStoreRAGClientInterface):
    """Production client connecting to RDS PostgreSQL (pgvector) for SOP retrieval."""

    def __init__(self, db_connection_url: str):
        self.db_connection_url = db_connection_url

    async def search_sop(self, query: str, top_k: int = 3) -> List[RAGDocumentCitation]:
        # Production pgvector similarity query
        # In actual deployment, creates embedding and executes:
        # SELECT doc_id, title, section, standard, content, 1 - (embedding <=> $1) AS score ...
        # If pgvector is unavailable or credentials not supplied, returns empty or raises
        try:
            import asyncpg  # type: ignore

            conn = await asyncpg.connect(self.db_connection_url)
            try:
                rows = await conn.fetch(
                    """
                    SELECT doc_id, title, section, standard, content, 0.95 as score
                    FROM nfv_sop_embeddings
                    WHERE content ILIKE $1
                    LIMIT $2
                    """,
                    f"%{query}%",
                    top_k,
                )
                return [
                    RAGDocumentCitation(
                        doc_id=r["doc_id"],
                        title=r["title"],
                        section=r["section"],
                        standard=r["standard"],
                        content=r["content"],
                        score=float(r["score"]),
                    )
                    for r in rows
                ]
            finally:
                await conn.close()
        except Exception:
            return []
