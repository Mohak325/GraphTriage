"""Unit tests for AWS Neptune Gremlin schema, migration, and client."""

import os
import pytest
import networkx as nx

from database.neptune.gremlin_schema import NeptuneLabels, NeptuneProperties, GremlinQueries
from database.neptune.cypher_to_gremlin_migrator import CypherToGremlinMigrator
from database.neptune.neptune_client import NeptuneClient
from ai_models.graph_engine.fault_gradient import FaultGradientEngine


class TestGremlinSchemaAndQueries:
    """Validate Gremlin queries and constants."""

    def test_vertex_and_edge_labels(self):
        assert NeptuneLabels.SERVICE == "Service"
        assert NeptuneLabels.HOST == "Host"
        assert NeptuneLabels.CONTAINER == "Container"
        assert NeptuneLabels.ANOMALY == "Anomaly"
        assert NeptuneLabels.CALLS == "CALLS"
        assert NeptuneLabels.DEPENDS_ON == "DEPENDS_ON"
        assert NeptuneLabels.RUNS_ON == "RUNS_ON"

    def test_get_service_vertex_query(self):
        query = GremlinQueries.get_service_vertex("srv-api-gateway")
        assert "hasLabel('Service')" in query
        assert "has('entity_id', 'srv-api-gateway')" in query
        assert query.endswith("valueMap(true)")

    def test_get_all_services_query(self):
        query = GremlinQueries.get_all_services()
        assert "hasLabel('Service')" in query
        assert "project('id', 'name'" in query
        assert "by('anomaly_score')" in query or "by(coalesce" in query

    def test_get_call_graph_query(self):
        query = GremlinQueries.get_call_graph()
        assert "hasLabel('CALLS')" in query
        assert "outV().values('entity_id')" in query
        assert "inV().values('entity_id')" in query

    def test_get_k_hop_subgraph_query(self):
        query = GremlinQueries.get_k_hop_subgraph("srv-order-service", k=3)
        assert "has('entity_id', 'srv-order-service')" in query
        assert "times(3)" in query

    def test_upsert_service_vertex_idempotent(self):
        query = GremlinQueries.add_or_update_service_vertex(
            service_id="srv-test-service",
            name="test-service",
            service_type="test",
            status="healthy",
            anomaly_score=0.25
        )
        assert "fold().coalesce(" in query
        assert "addV('Service')" in query
        assert "0.25" in query

    def test_upsert_call_edge_idempotent(self):
        query = GremlinQueries.add_call_edge(
            source_service_id="srv-a",
            target_service_id="srv-b",
            weight=0.75,
            error_rate=0.02
        )
        assert "addE('CALLS')" in query
        assert "0.75" in query


class TestCypherToGremlinMigration:
    """Validate parsing Cypher seed data and emitting Gremlin & CSV artifacts."""

    @pytest.fixture
    def migrator(self):
        cypher_path = os.path.join("database", "seed_data.cypher")
        m = CypherToGremlinMigrator(cypher_path)
        m.parse()
        return m

    def test_parsed_nodes_and_edges(self, migrator):
        assert len(migrator.nodes) >= 12
        assert "srv-api-gateway" in migrator.nodes
        assert "srv-payment-service" in migrator.nodes
        assert len(migrator.edges) >= 20

    def test_groovy_script_generation(self, migrator):
        groovy = migrator.generate_gremlin_groovy()
        assert "g.V().drop().iterate()" in groovy
        assert "g.addV('Service')" in groovy
        assert "addE('CALLS')" in groovy
        assert "srv-payment-service" in groovy

    def test_bulk_csv_generation(self, migrator, tmp_path):
        out_dir = str(tmp_path / "bulk")
        files = migrator.generate_neptune_bulk_csv(out_dir)
        assert len(files) == 2
        vert_file, edge_file = files[0], files[1]

        assert os.path.exists(vert_file)
        assert os.path.exists(edge_file)

        with open(vert_file, "r", encoding="utf-8") as f:
            v_content = f.read()
            assert "~id,~label" in v_content
            assert "srv-payment-service" in v_content

        with open(edge_file, "r", encoding="utf-8") as f:
            e_content = f.read()
            assert "~id,~from,~to,~label" in e_content
            assert "CALLS" in e_content


class TestNeptuneClientIntegration:
    """Validate Neptune client interaction and fault gradient engine integration."""

    @pytest.mark.asyncio
    async def test_neptune_client_connectivity(self):
        client = NeptuneClient()
        connected = await client.verify_connectivity()
        assert connected is True

    @pytest.mark.asyncio
    async def test_get_topology_graph(self):
        client = NeptuneClient()
        G = await client.get_topology_graph()
        assert isinstance(G, nx.DiGraph)
        assert len(G.nodes) >= 5
        assert len(G.edges) >= 4
        assert "srv-api-gateway" in G.nodes
        assert G.nodes["srv-api-gateway"]["service_type"] == "gateway"

    @pytest.mark.asyncio
    async def test_get_k_hop_subgraph(self):
        client = NeptuneClient()
        subgraph = await client.get_k_hop_subgraph("srv-order-service", k=1)
        assert isinstance(subgraph, nx.DiGraph)
        assert "srv-order-service" in subgraph.nodes

    @pytest.mark.asyncio
    async def test_neptune_to_fault_gradient_diffusion(self):
        client = NeptuneClient()
        G = await client.get_topology_graph()
        engine = FaultGradientEngine()
        result = engine.compute(G)
        assert result.root_cause_id in G.nodes
        assert result.confidence_score > 0.0
        assert len(result.ranked_nodes) > 0
