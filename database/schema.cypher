// =============================================
// GRAPHTRIAGE — Neo4j Schema Definition
// =============================================
// Run this file to initialize the Neo4j database schema.
// Usage: cat schema.cypher | cypher-shell -u neo4j -p <password>
//   OR: Paste into Neo4j Browser at http://localhost:7474
// =============================================


// ===================
// CONSTRAINTS (Unique IDs)
// ===================

CREATE CONSTRAINT service_id_unique IF NOT EXISTS
FOR (s:Service) REQUIRE s.id IS UNIQUE;

CREATE CONSTRAINT host_id_unique IF NOT EXISTS
FOR (h:Host) REQUIRE h.id IS UNIQUE;

CREATE CONSTRAINT container_id_unique IF NOT EXISTS
FOR (c:Container) REQUIRE c.id IS UNIQUE;

CREATE CONSTRAINT network_id_unique IF NOT EXISTS
FOR (n:Network) REQUIRE n.id IS UNIQUE;

CREATE CONSTRAINT anomaly_id_unique IF NOT EXISTS
FOR (a:Anomaly) REQUIRE a.id IS UNIQUE;

CREATE CONSTRAINT incident_id_unique IF NOT EXISTS
FOR (i:Incident) REQUIRE i.id IS UNIQUE;


// ===================
// INDEXES (Query Performance)
// ===================

// Primary lookup indexes
CREATE INDEX service_name_idx IF NOT EXISTS
FOR (s:Service) ON (s.name);

CREATE INDEX service_type_idx IF NOT EXISTS
FOR (s:Service) ON (s.type);

CREATE INDEX service_status_idx IF NOT EXISTS
FOR (s:Service) ON (s.status);

// Anomaly indexes for time-range queries
CREATE INDEX anomaly_timestamp_idx IF NOT EXISTS
FOR (a:Anomaly) ON (a.timestamp);

CREATE INDEX anomaly_severity_idx IF NOT EXISTS
FOR (a:Anomaly) ON (a.severity);

// Incident indexes
CREATE INDEX incident_status_idx IF NOT EXISTS
FOR (i:Incident) ON (i.status);

CREATE INDEX incident_created_idx IF NOT EXISTS
FOR (i:Incident) ON (i.created_at);

// Composite indexes for common query patterns
CREATE INDEX service_status_score IF NOT EXISTS
FOR (s:Service) ON (s.status, s.anomaly_score);


// ===================
// NODE SCHEMA DOCUMENTATION
// ===================
// Note: Neo4j is schema-optional. These comments document
// the expected properties for each node label.

// (:Service)
//   id:             STRING    — Unique service identifier (e.g., "svc-api-gateway")
//   name:           STRING    — Human-readable name (e.g., "API Gateway")
//   type:           STRING    — Service type: "api", "database", "cache", "queue", "compute", "gateway"
//   status:         STRING    — Current status: "healthy", "degraded", "critical", "unknown"
//   anomaly_score:  FLOAT     — Current anomaly score [0.0 - 1.0], updated by telemetry ingestion
//   cpu_usage:      FLOAT     — Latest CPU utilization percentage
//   memory_usage:   FLOAT     — Latest memory utilization percentage
//   latency_ms:     FLOAT     — Latest average response latency in milliseconds
//   error_rate:     FLOAT     — Latest error rate [0.0 - 1.0]
//   rps:            FLOAT     — Latest requests per second
//   last_updated:   DATETIME  — Timestamp of last metric update

// (:Host)
//   id:             STRING    — Unique host identifier
//   hostname:       STRING    — FQDN or hostname
//   ip_address:     STRING    — IP address
//   cpu_cores:      INTEGER   — Number of CPU cores
//   memory_gb:      FLOAT     — Total memory in GB
//   status:         STRING    — "active", "maintenance", "down"

// (:Container)
//   id:             STRING    — Container ID
//   image:          STRING    — Docker image name:tag
//   status:         STRING    — "running", "stopped", "restarting"
//   cpu_limit:      FLOAT     — CPU limit (cores)
//   memory_limit:   STRING    — Memory limit (e.g., "512m")

// (:Network)
//   id:             STRING    — Network segment identifier
//   subnet:         STRING    — CIDR notation (e.g., "10.0.1.0/24")
//   bandwidth_mbps: INTEGER   — Available bandwidth in Mbps
//   zone:           STRING    — Availability zone

// (:Anomaly)
//   id:             STRING    — Unique anomaly identifier
//   type:           STRING    — "latency_spike", "error_burst", "resource_exhaustion", "cascade_failure", "misconfiguration"
//   severity:       STRING    — "low", "medium", "high", "critical"
//   score:          FLOAT     — Anomaly confidence score [0.0 - 1.0]
//   timestamp:      DATETIME  — When the anomaly was detected
//   description:    STRING    — Human-readable description
//   metrics:        STRING    — JSON string of contributing metric values

// (:Incident)
//   id:             STRING    — Unique incident/RCA identifier
//   status:         STRING    — "triggered", "processing", "completed", "failed"
//   root_cause:     STRING    — Service ID of identified root cause (set after RCA completes)
//   confidence:     FLOAT     — RCA confidence score [0.0 - 1.0]
//   created_at:     DATETIME  — When the incident was triggered
//   resolved_at:    DATETIME  — When the RCA completed
//   agent_trace:    STRING    — JSON string of agent activity log
//   telemetry_window_minutes: INTEGER — Time window used for telemetry analysis


// ===================
// RELATIONSHIP SCHEMA DOCUMENTATION
// ===================

// (:Service)-[:CALLS]->(:Service)
//   latency_ms:     FLOAT     — Average call latency
//   error_rate:     FLOAT     — Error rate for this call path [0.0 - 1.0]
//   rps:            FLOAT     — Requests per second on this edge
//   protocol:       STRING    — "http", "grpc", "amqp", "tcp"
//   last_updated:   DATETIME  — Last time this edge was observed

// (:Service)-[:DEPENDS_ON]->(:Service)
//   dependency_type: STRING   — "hard" (critical), "soft" (optional/fallback)

// (:Service)-[:RUNS_ON]->(:Host)
//   (no additional properties)

// (:Service)-[:RUNS_IN]->(:Container)
//   (no additional properties)

// (:Host)-[:CONNECTED_TO]->(:Network)
//   bandwidth_mbps: INTEGER   — Bandwidth on this connection

// (:Service)-[:HAS_ANOMALY]->(:Anomaly)
//   (anomaly is associated with the service)

// (:Incident)-[:AFFECTS]->(:Service)
//   (services affected by this incident)

// (:Incident)-[:ROOT_CAUSE]->(:Service)
//   (identified root cause service)
