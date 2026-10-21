"""
Test Suite for Vector Store & SOP Indexing Engine.
Grounding: Paper 6 (NFVAgent).
"""

from src.rag.document_chunker import SOPVectorStore


def test_sop_document_chunking():
    store = SOPVectorStore(embedding_dim=64)

    doc_text = """
    ETSI GS NFV-IFA 007 Section 6.2 VNF Lifecycle Management.
    When a Virtual Network Function fails to complete the instantiation procedure within the
    negotiated SLA threshold, the NFV Orchestrator (NFVO) shall trigger an automated rollback
    or initiate a secondary VNF migration workflow to an alternate compute host.
    Failure to receive heartbeat signaling across the Or-Vnfm reference point indicates
    hypervisor CPU saturation or network interface detachment.
    """

    chunks = store.chunk_document(
        doc_source="ETSI_NFV_IFA007",
        full_text=doc_text,
        section_id="6.2",
        title="VNF Instantiation Failure",
        chunk_size_words=20,
        overlap_words=5,
        incident_type="VNF_crash",
        resolution_action="auto_scale_or_migrate"
    )

    assert len(chunks) >= 2
    assert chunks[0].doc_source == "ETSI_NFV_IFA007"
    assert chunks[0].section_id == "6.2"


def test_semantic_search_top_k():
    store = SOPVectorStore(embedding_dim=128)

    doc_a = "NFV VNF instantiation failure rollback secondary migration compute host"
    doc_b = "5G Core AMF registration reject HTTP2 stream multiplexing queue starvation"
    doc_c = "BGP routing flap edge router packet drop telemetry transport link"

    chunks_a = store.chunk_document("ETSI", doc_a, section_id="1.1", title="VNF Migration")
    chunks_b = store.chunk_document("3GPP", doc_b, section_id="2.2", title="AMF Rejection")
    chunks_c = store.chunk_document("IETF", doc_c, section_id="3.3", title="BGP Flap")

    store.add_chunks(chunks_a + chunks_b + chunks_c)

    # Search for VNF migration query
    results = store.search("VNF compute host migration", top_k=2)

    assert len(results) > 0
    top_chunk, score = results[0]
    assert top_chunk.doc_source == "ETSI"
    assert score > 0.0


def test_pgvector_ddl_generation():
    ddl = SOPVectorStore.get_pgvector_ddl()
    assert "CREATE EXTENSION IF NOT EXISTS vector" in ddl
    assert "sop_embeddings" in ddl
    assert "vector(384)" in ddl
