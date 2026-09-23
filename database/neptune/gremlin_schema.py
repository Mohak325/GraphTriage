"""AWS Neptune Gremlin Property Graph Schema & Traversal Definitions.

Defines vertex labels, edge labels, property keys, and Gremlin traversal queries
for running GraphTriage topology graphs on AWS Neptune clusters.
"""

from typing import Dict, Any, List, Optional
import json


class NeptuneLabels:
    """Vertex and Edge labels for Amazon Neptune property graphs."""

    # Vertex Labels
    SERVICE = "Service"
    HOST = "Host"
    CONTAINER = "Container"
    NETWORK = "Network"
    ANOMALY = "Anomaly"
    INCIDENT = "Incident"

    # Edge Labels
    CALLS = "CALLS"
    DEPENDS_ON = "DEPENDS_ON"
    RUNS_ON = "RUNS_ON"
    PART_OF = "PART_OF"
    HAS_ANOMALY = "HAS_ANOMALY"
    ROOT_CAUSE = "ROOT_CAUSE"
    IMPACTS = "IMPACTS"


class NeptuneProperties:
    """Standard property keys stored on Neptune elements."""

    # Identity
    ID = "entity_id"
    NAME = "name"
    TYPE = "service_type"
    STATUS = "status"

    # Operational metrics
    ANOMALY_SCORE = "anomaly_score"
    FAILURE_PROBABILITY = "failure_probability"
    RPS = "rps"
    LATENCY_P95 = "latency_p95"
    ERROR_RATE = "error_rate"

    # Edge metrics
    WEIGHT = "weight"
    PROTOCOL = "protocol"

    # Host & Container properties
    IP = "ip"
    REGION = "region"
    AZ = "az"
    CPU_CORES = "cpu_cores"
    MEMORY_GB = "memory_gb"
    IMAGE = "image"
    CONTAINER_PORT = "container_port"
    HOST_PORT = "host_port"

    # Anomaly properties
    SEVERITY = "severity"
    ANOMALY_TYPE = "anomaly_type"
    DESCRIPTION = "description"
    METRIC_IMPACTED = "metric_impacted"

    # Metadata
    VERSION = "version"
    LANGUAGE = "language"
    UPDATED_AT = "updated_at"


class GremlinQueries:
    """Pre-compiled Gremlin traversals for high-performance Neptune execution."""

    @staticmethod
    def get_service_vertex(service_id: str) -> str:
        """Fetch a single service vertex by entity_id with all property values."""
        clean_id = service_id.replace("'", "\\'")
        return f"g.V().hasLabel('{NeptuneLabels.SERVICE}').has('{NeptuneProperties.ID}', '{clean_id}').valueMap(true)"

    @staticmethod
    def get_all_services() -> str:
        """Project all service vertices with operational KPIs."""
        return (
            f"g.V().hasLabel('{NeptuneLabels.SERVICE}')"
            f".project('id', 'name', 'type', 'status', 'anomaly_score', 'failure_probability', 'rps', 'latency_p95', 'error_rate')"
            f".by('{NeptuneProperties.ID}')"
            f".by('{NeptuneProperties.NAME}')"
            f".by('{NeptuneProperties.TYPE}')"
            f".by('{NeptuneProperties.STATUS}')"
            f".by(coalesce(values('{NeptuneProperties.ANOMALY_SCORE}'), constant(0.0)))"
            f".by(coalesce(values('{NeptuneProperties.FAILURE_PROBABILITY}'), constant(0.0)))"
            f".by(coalesce(values('{NeptuneProperties.RPS}'), constant(0.0)))"
            f".by(coalesce(values('{NeptuneProperties.LATENCY_P95}'), constant(0.0)))"
            f".by(coalesce(values('{NeptuneProperties.ERROR_RATE}'), constant(0.0)))"
        )

    @staticmethod
    def get_call_graph() -> str:
        """Fetch all microservice dependency edges with call weight and telemetry."""
        return (
            f"g.E().hasLabel('{NeptuneLabels.CALLS}')"
            f".project('source', 'target', 'weight', 'error_rate', 'latency_p95', 'rps')"
            f".by(outV().values('{NeptuneProperties.ID}'))"
            f".by(inV().values('{NeptuneProperties.ID}'))"
            f".by(coalesce(values('{NeptuneProperties.WEIGHT}'), constant(1.0)))"
            f".by(coalesce(values('{NeptuneProperties.ERROR_RATE}'), constant(0.0)))"
            f".by(coalesce(values('{NeptuneProperties.LATENCY_P95}'), constant(0.0)))"
            f".by(coalesce(values('{NeptuneProperties.RPS}'), constant(0.0)))"
        )

    @staticmethod
    def get_k_hop_subgraph(service_id: str, k: int = 2) -> str:
        """Traverse k hops bidirectional from root service, collecting connected services and call edges."""
        clean_id = service_id.replace("'", "\\'")
        return (
            f"g.V().hasLabel('{NeptuneLabels.SERVICE}').has('{NeptuneProperties.ID}', '{clean_id}')"
            f".repeat(bothE('{NeptuneLabels.CALLS}').otherV().dedup()).times({k}).emit().dedup()"
            f".project('id', 'name', 'status', 'anomaly_score')"
            f".by('{NeptuneProperties.ID}')"
            f".by('{NeptuneProperties.NAME}')"
            f".by('{NeptuneProperties.STATUS}')"
            f".by(coalesce(values('{NeptuneProperties.ANOMALY_SCORE}'), constant(0.0)))"
        )

    @staticmethod
    def get_active_anomalies() -> str:
        """Fetch active anomalies with impacted service connections."""
        return (
            f"g.V().hasLabel('{NeptuneLabels.ANOMALY}')"
            f".project('anomaly_id', 'severity', 'anomaly_type', 'description', 'service_id')"
            f".by('{NeptuneProperties.ID}')"
            f".by('{NeptuneProperties.SEVERITY}')"
            f".by('{NeptuneProperties.ANOMALY_TYPE}')"
            f".by('{NeptuneProperties.DESCRIPTION}')"
            f".by(coalesce(__.in('{NeptuneLabels.HAS_ANOMALY}').values('{NeptuneProperties.ID}'), constant('unknown')))"
        )

    @staticmethod
    def get_cascading_failure_paths(min_anomaly_score: float = 0.5) -> str:
        """Identify downstream failure propagation paths where anomalous services call other services."""
        return (
            f"g.V().hasLabel('{NeptuneLabels.SERVICE}').has('{NeptuneProperties.ANOMALY_SCORE}', gt({min_anomaly_score}))"
            f".outE('{NeptuneLabels.CALLS}').as('call')"
            f".inV().as('downstream')"
            f".select('call', 'downstream')"
            f".by(project('weight', 'error_rate').by('{NeptuneProperties.WEIGHT}').by('{NeptuneProperties.ERROR_RATE}'))"
            f".by(project('id', 'status', 'anomaly_score').by('{NeptuneProperties.ID}').by('{NeptuneProperties.STATUS}').by('{NeptuneProperties.ANOMALY_SCORE}'))"
        )

    @staticmethod
    def add_or_update_service_vertex(
        service_id: str,
        name: str,
        service_type: str,
        status: str = "healthy",
        anomaly_score: float = 0.0,
        failure_prob: float = 0.0,
        rps: float = 0.0,
        latency_p95: float = 0.0,
        error_rate: float = 0.0,
        version: str = "v1.0.0",
        language: str = "python"
    ) -> str:
        """Idempotent Gremlin traversal to upsert a Service vertex."""
        clean_id = service_id.replace("'", "\\'")
        clean_name = name.replace("'", "\\'")
        clean_type = service_type.replace("'", "\\'")
        clean_status = status.replace("'", "\\'")
        clean_ver = version.replace("'", "\\'")
        clean_lang = language.replace("'", "\\'")

        return (
            f"g.V().hasLabel('{NeptuneLabels.SERVICE}').has('{NeptuneProperties.ID}', '{clean_id}')"
            f".fold()"
            f".coalesce("
            f"  unfold(),"
            f"  addV('{NeptuneLabels.SERVICE}').property('{NeptuneProperties.ID}', '{clean_id}')"
            f")"
            f".property('{NeptuneProperties.NAME}', '{clean_name}')"
            f".property('{NeptuneProperties.TYPE}', '{clean_type}')"
            f".property('{NeptuneProperties.STATUS}', '{clean_status}')"
            f".property('{NeptuneProperties.ANOMALY_SCORE}', {float(anomaly_score)})"
            f".property('{NeptuneProperties.FAILURE_PROBABILITY}', {float(failure_prob)})"
            f".property('{NeptuneProperties.RPS}', {float(rps)})"
            f".property('{NeptuneProperties.LATENCY_P95}', {float(latency_p95)})"
            f".property('{NeptuneProperties.ERROR_RATE}', {float(error_rate)})"
            f".property('{NeptuneProperties.VERSION}', '{clean_ver}')"
            f".property('{NeptuneProperties.LANGUAGE}', '{clean_lang}')"
        )

    @staticmethod
    def add_call_edge(
        source_service_id: str,
        target_service_id: str,
        weight: float = 1.0,
        rps: float = 100.0,
        latency_p95: float = 50.0,
        error_rate: float = 0.0
    ) -> str:
        """Idempotent Gremlin traversal to upsert a CALLS edge between two services."""
        src = source_service_id.replace("'", "\\'")
        tgt = target_service_id.replace("'", "\\'")
        return (
            f"g.V().hasLabel('{NeptuneLabels.SERVICE}').has('{NeptuneProperties.ID}', '{src}').as('from')"
            f".V().hasLabel('{NeptuneLabels.SERVICE}').has('{NeptuneProperties.ID}', '{tgt}').as('to')"
            f".coalesce("
            f"  inE('{NeptuneLabels.CALLS}').where(outV().as('from')),"
            f"  addE('{NeptuneLabels.CALLS}').from('from').to('to')"
            f")"
            f".property('{NeptuneProperties.WEIGHT}', {float(weight)})"
            f".property('{NeptuneProperties.RPS}', {float(rps)})"
            f".property('{NeptuneProperties.LATENCY_P95}', {float(latency_p95)})"
            f".property('{NeptuneProperties.ERROR_RATE}', {float(error_rate)})"
        )
