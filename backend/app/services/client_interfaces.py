"""Abstract interfaces for external team dependencies (Person A and Person B).

Person C maintains strict isolation:
- Person A's telemetry server is consumed via MCPTelemetryClientInterface.
- Person B's ML/Twin engine is consumed via RCAClientInterface (Contract 2).
- Vector store / RAG is consumed via VectorStoreRAGClientInterface.

Two implementations exist for each:
1. Fixture-backed (default for tests, local demos, and offline validation).
2. Live HTTP/DB-backed (used in production AWS integration via .env configuration).
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
from contracts.pydantic.contract_2_rca_analysis import RCARequest, RCAResponse
from contracts.pydantic.contract_1_telemetry import NormalizedTelemetryEvent


class MCPToolDefinition:
    def __init__(self, name: str, description: str, input_schema: Dict[str, Any]):
        self.name = name
        self.description = description
        self.input_schema = input_schema

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description,
            "input_schema": self.input_schema,
        }


class MCPTelemetryClientInterface(ABC):
    """Abstract interface for consuming Person A's MCP Telemetry Server."""

    @abstractmethod
    async def list_tools(self) -> List[MCPToolDefinition]:
        """Discover tools exposed by the MCP server dynamically."""
        pass

    @abstractmethod
    async def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Invoke an MCP tool call (e.g., query_prometheus, query_nwdaf, inspect_k8s_pod)."""
        pass

    @abstractmethod
    async def query_live_metric(self, component: str, metric_name: str) -> Optional[NormalizedTelemetryEvent]:
        """Query live telemetry for a specific component and metric to satisfy AGORA guardrails."""
        pass


class RCAClientInterface(ABC):
    """Abstract interface for consuming Person B's Contract 2 API (POST /api/rca/analyze)."""

    @abstractmethod
    async def analyze_incident(self, request: RCARequest) -> RCAResponse:
        """Call Person B's SageMaker / ML RCA endpoint to get ranked causes and topology."""
        pass


class RAGDocumentCitation:
    def __init__(self, doc_id: str, title: str, section: str, standard: str, content: str, score: float):
        self.doc_id = doc_id
        self.title = title
        self.section = section
        self.standard = standard
        self.content = content
        self.score = score

    def to_dict(self) -> Dict[str, Any]:
        return {
            "doc_id": self.doc_id,
            "title": self.title,
            "section": self.section,
            "standard": self.standard,
            "content": self.content,
            "score": self.score,
        }


class VectorStoreRAGClientInterface(ABC):
    """Abstract interface for retrieving ETSI NFV-MANO SOPs and incident knowledge."""

    @abstractmethod
    async def search_sop(self, query: str, top_k: int = 3) -> List[RAGDocumentCitation]:
        """Retrieve standard operational procedure citations matching query."""
        pass
