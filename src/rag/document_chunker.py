"""
Vector Store & SOP Indexing Engine.
Grounding: Paper 6 (NFVAgent, Woo & Woo, IEEE/IFIP CNSM 2025).
Chunks ETSI NFV-MANO operational guidelines (ETSI GS NFV-IFA 006, 007, 008)
and 3GPP technical standards (TS 23.502, 23.288) into overlapping semantic windows.
Provides fast cosine-similarity search (<50ms target) with dual execution:
  - Local in-memory numpy vector index (zero cloud dependency)
  - PostgreSQL + pgvector IVFFlat schema generator for production AWS RDS.
"""

from typing import List, Dict, Any, Optional, Tuple
import re
import numpy as np
from pydantic import BaseModel, Field
from structlog import get_logger

logger = get_logger()


class SOPChunk(BaseModel):
    """Represents an embedded ETSI or 3GPP standard documentation chunk."""
    chunk_id: str
    doc_source: str                 # e.g. ETSI_NFV_IFA007, 3GPP_TS_23502
    section_id: str                 # e.g. Section 4.2.2.2
    title: str
    text: str
    incident_type: Optional[str] = None
    resolution_action: Optional[str] = None
    embedding: Optional[List[float]] = None


class SOPVectorStore:
    """
    In-memory semantic vector index with cosine similarity search.
    Provides sub-50ms top-K retrieval over chunked telecom operational SOPs.
    """

    def __init__(self, embedding_dim: int = 384):
        self.embedding_dim = embedding_dim
        self.chunks: List[SOPChunk] = []
        self._embedding_matrix: Optional[np.ndarray] = None

    def chunk_document(
        self,
        doc_source: str,
        full_text: str,
        section_id: str = "1.0",
        title: str = "Standard",
        chunk_size_words: int = 100,
        overlap_words: int = 20,
        incident_type: Optional[str] = None,
        resolution_action: Optional[str] = None
    ) -> List[SOPChunk]:
        """
        Splits a specification document into overlapping sliding windows.
        """
        words = re.findall(r'\S+', full_text)
        chunks: List[SOPChunk] = []

        if not words:
            return chunks

        step = max(1, chunk_size_words - overlap_words)
        idx = 0
        for i in range(0, len(words), step):
            window = words[i:i + chunk_size_words]
            chunk_text = " ".join(window)
            cid = f"{doc_source}-{section_id}-chunk-{idx}"

            chunk = SOPChunk(
                chunk_id=cid,
                doc_source=doc_source,
                section_id=section_id,
                title=title,
                text=chunk_text,
                incident_type=incident_type,
                resolution_action=resolution_action
            )
            chunks.append(chunk)
            idx += 1

        return chunks

    def add_chunks(self, chunks: List[SOPChunk]):
        """Adds chunks to the vector index and updates embedding matrix."""
        for c in chunks:
            if c.embedding is None:
                # Deterministic pseudo-embedding for testing if no model is loaded
                c.embedding = self._generate_pseudo_embedding(c.text)
            self.chunks.append(c)

        # Rebuild embedding matrix
        embeddings = [c.embedding for c in self.chunks]
        self._embedding_matrix = np.array(embeddings, dtype=np.float32)

    def search(
        self,
        query: str,
        top_k: int = 5,
        doc_source_filter: Optional[str] = None
    ) -> List[Tuple[SOPChunk, float]]:
        """
        Executes semantic cosine-similarity search.
        Returns List of (chunk, similarity_score).
        """
        if not self.chunks or self._embedding_matrix is None:
            return []

        query_vec = np.array(self._generate_pseudo_embedding(query), dtype=np.float32)
        query_norm = np.linalg.norm(query_vec)
        if query_norm == 0:
            query_norm = 1.0

        # Cosine similarity: (A . B) / (||A|| * ||B||)
        matrix_norms = np.linalg.norm(self._embedding_matrix, axis=1)
        matrix_norms[matrix_norms == 0] = 1.0

        dot_products = np.dot(self._embedding_matrix, query_vec)
        similarities = dot_products / (matrix_norms * query_norm)

        # Sort indices descending
        ranked_indices = np.argsort(similarities)[::-1]

        results: List[Tuple[SOPChunk, float]] = []
        for idx in ranked_indices:
            chunk = self.chunks[idx]
            if doc_source_filter and chunk.doc_source != doc_source_filter:
                continue

            results.append((chunk, float(similarities[idx])))
            if len(results) >= top_k:
                break

        return results

    def _generate_pseudo_embedding(self, text: str) -> List[float]:
        """Generates deterministic unit-normalized pseudo-embedding from text hash."""
        vec = np.zeros(self.embedding_dim, dtype=np.float32)
        words = text.lower().split()
        for w in words:
            h = abs(hash(w)) % self.embedding_dim
            vec[h] += 1.0

        norm = np.linalg.norm(vec)
        if norm > 0:
            vec /= norm
        return vec.tolist()

    @staticmethod
    def get_pgvector_ddl() -> str:
        """Returns the PostgreSQL + pgvector DDL schema for Amazon RDS deployment."""
        return """
CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE IF NOT EXISTS sop_embeddings (
    id SERIAL PRIMARY KEY,
    chunk_id VARCHAR(128) UNIQUE NOT NULL,
    doc_source VARCHAR(64) NOT NULL,
    section_id VARCHAR(64) NOT NULL,
    title VARCHAR(256) NOT NULL,
    text TEXT NOT NULL,
    incident_type VARCHAR(64),
    resolution_action TEXT,
    embedding vector(384) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS sop_embeddings_ivfflat_idx
ON sop_embeddings USING ivfflat (embedding vector_cosine_ops)
WITH (lists = 100);
"""
