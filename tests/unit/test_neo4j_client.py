"""Unit tests for the Neo4j async client wrapper."""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
import networkx as nx

from ai_models.graph_engine.neo4j_client import Neo4jClient


class TestNeo4jClient:
    """Test suite for Neo4jClient wrapper."""

    def test_client_init_defaults(self):
        client = Neo4jClient()
        assert client.uri == "bolt://localhost:7687"
        assert client.user == "neo4j"
        assert client.database == "neo4j"
        assert client.max_pool_size == 50

    def test_client_custom_config(self):
        client = Neo4jClient(
            uri="bolt://prod-cluster:7687",
            user="admin",
            password="secret_password",
            database="triage_db",
            max_connection_pool_size=100
        )
        assert client.uri == "bolt://prod-cluster:7687"
        assert client.user == "admin"
        assert client.database == "triage_db"
        assert client.max_pool_size == 100

    @pytest.mark.asyncio
    async def test_to_networkx_graph_conversion(self):
        """Verify mock data correctly transforms to NetworkX DiGraph."""
        client = Neo4jClient()

        mock_services = [
            {"id": "s1", "name": "service-1", "type": "gateway", "anomaly_score": 0.8},
            {"id": "s2", "name": "service-2", "type": "backend", "anomaly_score": 0.2}
        ]
        mock_calls = [
            {"source_id": "s1", "target_id": "s2", "weight": 0.75, "latency_p95": 45.0, "error_rate": 0.02}
        ]

        with patch.object(client, "get_all_services", new=AsyncMock(return_value=mock_services)), \
             patch.object(client, "get_call_graph", new=AsyncMock(return_value=mock_calls)):
            g = await client.to_networkx_graph()

            assert isinstance(g, nx.DiGraph)
            assert g.number_of_nodes() == 2
            assert g.number_of_edges() == 1
            assert g.nodes["s1"]["name"] == "service-1"
            assert g["s1"]["s2"]["weight"] == 0.75
            assert g["s1"]["s2"]["latency_p95"] == 45.0

    @pytest.mark.asyncio
    async def test_close_safe_idempotent(self):
        client = Neo4jClient()
        # Should not raise when driver was never initialized
        await client.close()
        assert client._driver is None
