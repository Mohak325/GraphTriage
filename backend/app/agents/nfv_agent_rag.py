"""NFVAgent RAG Pipeline (ETSI NFV-MANO SOP Retrieval).

Grounded in Paper 6: Woo & Woo (IEEE/IFIP CNSM 2025).
Provides automated retrieval over ETSI NFV-MANO operational guidelines,
3GPP technical standards, and historical incident workflows with full citations.
Retrieval only: does not perform ungrounded generation.
"""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

from backend.app.services.client_interfaces import (
    VectorStoreRAGClientInterface,
    RAGDocumentCitation,
)
from backend.app.services.fixture_clients import FixtureVectorStoreRAGClient


class NFVRAGRecommendation(BaseModel):
    """Structured SOP recommendation grounded in ETSI NFV standards."""
    incident_id: str = Field(..., description="Incident ID")
    symptom_query: str = Field(..., description="Query symptom")
    recommended_procedure: str = Field(..., description="Derived mitigation procedure")
    citations: List[Dict[str, Any]] = Field(..., min_length=1, description="Standard and SOP citations")


class NFVAgentRAG:
    """RAG agent querying SOP knowledge base and formatting cited recommendations."""

    def __init__(self, rag_client: Optional[VectorStoreRAGClientInterface] = None):
        self.rag_client = rag_client or FixtureVectorStoreRAGClient()

    async def retrieve_remediation_guidelines(
        self,
        incident_id: str,
        fault_type: str,
        affected_component: str,
        top_k: int = 3,
    ) -> NFVRAGRecommendation:
        """Retrieves ETSI NFV-MANO SOP citations matching the fault."""
        query = f"{affected_component} {fault_type}"
        citations = await self.rag_client.search_sop(query, top_k=top_k)

        # Derive recommended procedure from highest scoring citation
        top_doc = citations[0] if citations else None
        proc = top_doc.content if top_doc else "Perform standard VNF health-check and replica restart."

        return NFVRAGRecommendation(
            incident_id=incident_id,
            symptom_query=query,
            recommended_procedure=proc,
            citations=[c.to_dict() for c in citations],
        )
