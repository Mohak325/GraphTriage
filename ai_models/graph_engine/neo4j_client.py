"""Asynchronous Neo4j Python client wrapper for GraphTriage.

Handles connection pooling, query execution, graph extraction, and conversion
of Neo4j microservice topologies into NetworkX graph representations for spectral analysis.
"""

import logging
from typing import List, Dict, Any, Optional, Tuple
import networkx as nx

try:
    from neo4j import AsyncGraphDatabase, AsyncDriver, AsyncSession
    NEO4J_AVAILABLE = True
except ImportError:
    NEO4J_AVAILABLE = False
    AsyncGraphDatabase = None
    AsyncDriver = None
    AsyncSession = None

logger = logging.getLogger(__name__)


class Neo4jClient:
    """Async wrapper managing Neo4j driver connection pool and domain queries."""

    def __init__(
        self,
        uri: str = "bolt://localhost:7687",
        user: str = "neo4j",
        password: str = "graphtriage_dev",
        database: str = "neo4j",
        max_connection_pool_size: int = 50,
        connection_timeout: float = 30.0
    ):
        self.uri = uri
        self.user = user
        self.password = password
        self.database = database
        self.max_pool_size = max_connection_pool_size
        self.connection_timeout = connection_timeout
        self._driver: Optional[Any] = None

    async def get_driver(self) -> Any:
        """Lazily initialize and return the async Neo4j driver."""
        if not NEO4J_AVAILABLE or AsyncGraphDatabase is None:
            raise RuntimeError("The 'neo4j' Python package is not installed. Please install it with 'pip install neo4j'.")

        if self._driver is None:
            logger.info(f"Connecting to Neo4j database at {self.uri} (database: {self.database})")
            self._driver = AsyncGraphDatabase.driver(
                self.uri,
                auth=(self.user, self.password),
                max_connection_pool_size=self.max_pool_size,
                connection_timeout=self.connection_timeout
            )
        return self._driver

    async def verify_connectivity(self) -> bool:
        """Check if Neo4j instance is alive and reachable."""
        try:
            driver = await self.get_driver()
            await driver.verify_connectivity()
            return True
        except Exception as exc:
            logger.warning(f"Neo4j connectivity check failed: {exc}")
            return False

    async def close(self):
        """Close driver connection pool gracefully."""
        if self._driver is not None:
            await self._driver.close()
            self._driver = None
            logger.info("Neo4j driver connection pool closed.")

    async def execute_query(
        self,
        query: str,
        parameters: Optional[Dict[str, Any]] = None,
        db: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Execute a Cypher read query and return list of result records as dictionaries."""
        driver = await self.get_driver()
        target_db = db or self.database
        async with driver.session(database=target_db) as session:
            result = await session.run(query, parameters or {})
            records = await result.data()
            return records

    async def execute_write(
        self,
        query: str,
        parameters: Optional[Dict[str, Any]] = None,
        db: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Execute a Cypher write transaction query."""
        driver = await self.get_driver()
        target_db = db or self.database

        async def _work(tx):
            res = await tx.run(query, parameters or {})
            return await res.data()

        async with driver.session(database=target_db) as session:
            return await session.execute_write(_work)

    # =============================================
    # Domain-Specific Graph Queries
    # =============================================

    async def get_service(self, service_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve a single Service node by its unique ID."""
        cypher = """
        MATCH (s:Service {id: $service_id})
        RETURN s { .*, id: s.id, name: s.name, type: s.type, status: s.status } AS service
        """
        records = await self.execute_query(cypher, {"service_id": service_id})
        return records[0]["service"] if records else None

    async def get_all_services(self) -> List[Dict[str, Any]]:
        """Retrieve all Service nodes with their current metric states."""
        cypher = """
        MATCH (s:Service)
        RETURN s { .*, id: s.id, name: s.name, type: s.type, status: s.status,
                   anomaly_score: coalesce(s.anomaly_score, 0.0),
                   failure_probability: coalesce(s.failure_probability, 0.0) } AS service
        ORDER BY s.name ASC
        """
        records = await self.execute_query(cypher)
        return [r["service"] for r in records]

    async def get_call_graph(self) -> List[Dict[str, Any]]:
        """Retrieve all CALLS relationships between services."""
        cypher = """
        MATCH (source:Service)-[r:CALLS]->(target:Service)
        RETURN source.id AS source_id,
               source.name AS source_name,
               target.id AS target_id,
               target.name AS target_name,
               r.weight AS weight,
               r.rps AS rps,
               r.latency_p95 AS latency_p95,
               r.error_rate AS error_rate,
               r.protocol AS protocol
        """
        return await self.execute_query(cypher)

    async def get_subgraph(self, service_id: str, depth: int = 2) -> Dict[str, Any]:
        """Extract a k-hop neighborhood ego graph around a service node."""
        cypher = f"""
        MATCH path = (root:Service {{id: $service_id}})-[:CALLS*0..{depth}]-(neighbor:Service)
        WITH collect(path) AS paths
        UNWIND paths AS p
        UNWIND nodes(p) AS n
        UNWIND relationships(p) AS r
        RETURN collect(DISTINCT n {{ .*, id: n.id, name: n.name, type: n.type }}) AS nodes,
               collect(DISTINCT r {{
                   source: startNode(r).id,
                   target: endNode(r).id,
                   weight: coalesce(r.weight, 1.0),
                   latency_p95: r.latency_p95,
                   error_rate: r.error_rate
               }}) AS edges
        """
        records = await self.execute_query(cypher, {"service_id": service_id})
        if records:
            return {"nodes": records[0]["nodes"], "edges": records[0]["edges"]}
        return {"nodes": [], "edges": []}

    async def get_upstream_dependencies(self, service_id: str) -> List[Dict[str, Any]]:
        """Find services that directly call the given target service."""
        cypher = """
        MATCH (caller:Service)-[r:CALLS]->(target:Service {id: $service_id})
        RETURN caller.id AS id, caller.name AS name, r.weight AS weight, r.latency_p95 AS latency_p95
        """
        return await self.execute_query(cypher, {"service_id": service_id})

    async def get_downstream_dependencies(self, service_id: str) -> List[Dict[str, Any]]:
        """Find services that the given service depends upon / calls directly."""
        cypher = """
        MATCH (caller:Service {id: $service_id})-[r:CALLS]->(callee:Service)
        RETURN callee.id AS id, callee.name AS name, r.weight AS weight, r.latency_p95 AS latency_p95
        """
        return await self.execute_query(cypher, {"service_id": service_id})

    async def get_active_anomalies(self) -> List[Dict[str, Any]]:
        """Retrieve all currently active anomalies linked to their affected services."""
        cypher = """
        MATCH (s:Service)-[:HAS_ANOMALY]->(a:Anomaly {status: 'active'})
        RETURN a.id AS anomaly_id,
               a.metric_name AS metric_name,
               a.metric_value AS metric_value,
               a.threshold AS threshold,
               a.severity AS severity,
               a.timestamp AS timestamp,
               a.confidence AS confidence,
               s.id AS service_id,
               s.name AS service_name
        ORDER BY a.severity DESC, a.timestamp DESC
        """
        return await self.execute_query(cypher)

    async def upsert_service(self, service_data: Dict[str, Any]) -> Dict[str, Any]:
        """Insert or update a Service node."""
        cypher = """
        MERGE (s:Service {id: $id})
        SET s += $props,
            s.updated_at = datetime()
        RETURN s.id AS id, s.name AS name
        """
        props = {k: v for k, v in service_data.items() if k != "id"}
        records = await self.execute_write(cypher, {"id": service_data["id"], "props": props})
        return records[0] if records else {}

    async def upsert_call_edge(
        self,
        source_id: str,
        target_id: str,
        edge_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Insert or update a CALLS relationship between two services."""
        cypher = """
        MATCH (s:Service {id: $source_id})
        MATCH (t:Service {id: $target_id})
        MERGE (s)-[r:CALLS]->(t)
        SET r += $props,
            r.updated_at = datetime()
        RETURN type(r) AS rel_type, r.weight AS weight
        """
        records = await self.execute_write(cypher, {
            "source_id": source_id,
            "target_id": target_id,
            "props": edge_data
        })
        return records[0] if records else {}

    async def record_anomaly(self, anomaly_data: Dict[str, Any], affected_service_id: str) -> str:
        """Create an Anomaly node and connect it to the affected Service."""
        cypher = """
        MATCH (s:Service {id: $service_id})
        MERGE (a:Anomaly {id: $anomaly_id})
        SET a += $props
        MERGE (s)-[:HAS_ANOMALY]->(a)
        RETURN a.id AS id
        """
        anomaly_id = anomaly_data.get("id")
        props = {k: v for k, v in anomaly_data.items() if k not in ("id", "service_id")}
        records = await self.execute_write(cypher, {
            "service_id": affected_service_id,
            "anomaly_id": anomaly_id,
            "props": props
        })
        return str(records[0]["id"]) if records else str(anomaly_id or "")

    # =============================================
    # NetworkX Graph Extraction (Spectral Analysis)
    # =============================================

    async def to_networkx_graph(self) -> nx.DiGraph:
        """Extract the full active service topology into an in-memory NetworkX DiGraph.

        Nodes contain service attributes (anomaly_score, status, rps, etc.).
        Edges contain call attributes (weight, latency_p95, error_rate, rps).
        """
        g = nx.DiGraph()

        # Load services
        services = await self.get_all_services()
        for s in services:
            service_id = s.get("id")
            if service_id:
                g.add_node(service_id, **s)

        # Load edges
        calls = await self.get_call_graph()
        for c in calls:
            src = c.get("source_id")
            tgt = c.get("target_id")
            if src and tgt:
                weight = float(c.get("weight") or 1.0)
                props = {k: v for k, v in c.items() if k not in ("source_id", "target_id", "weight")}
                g.add_edge(src, tgt, weight=weight, **props)

        logger.info(f"Loaded NetworkX DiGraph from Neo4j: {g.number_of_nodes()} nodes, {g.number_of_edges()} edges")
        return g
