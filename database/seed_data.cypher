// =============================================
// GRAPHTRIAGE — Seed Data & Sample Topology
// =============================================
// Populates a realistic 12-microservice cloud architecture
// with hosts, containers, networks, call dependencies,
// metrics, and an active cascading failure scenario.
//
// Usage:
//   cat seed_data.cypher | cypher-shell -u neo4j -p <password>
//   OR: Run in Neo4j Browser (http://localhost:7474)
// =============================================


// =============================================
// 1. INFRASTRUCTURE: Networks & Hosts
// =============================================

MERGE (netPublic:Network {id: "net-public-edge", name: "Public Edge Subnet", cidr: "10.0.1.0/24", vpc: "vpc-prod-main"})
MERGE (netCore:Network {id: "net-app-core", name: "Internal Mesh Core Subnet", cidr: "10.0.2.0/24", vpc: "vpc-prod-main"})
MERGE (netSecure:Network {id: "net-data-secure", name: "Secure Payment/Data Subnet", cidr: "10.0.3.0/24", vpc: "vpc-prod-main"});

MERGE (h1:Host {id: "host-k8s-node-01", name: "k8s-worker-pool-1a", ip: "10.0.2.11", region: "us-east-1", az: "us-east-1a", cpu_cores: 16, memory_gb: 64, status: "healthy"})
MERGE (h2:Host {id: "host-k8s-node-02", name: "k8s-worker-pool-1b", ip: "10.0.2.12", region: "us-east-1", az: "us-east-1b", cpu_cores: 16, memory_gb: 64, status: "healthy"})
MERGE (h3:Host {id: "host-k8s-node-03", name: "k8s-worker-pool-1c", ip: "10.0.3.13", region: "us-east-1", az: "us-east-1c", cpu_cores: 32, memory_gb: 128, status: "degraded"});


// =============================================
// 2. MICROSERVICES
// =============================================

MERGE (sGateway:Service {
    id: "srv-api-gateway",
    name: "api-gateway",
    type: "gateway",
    status: "degraded",
    anomaly_score: 0.72,
    failure_probability: 0.65,
    rps: 3450.0,
    error_rate: 0.082,
    latency_p95: 420.5,
    version: "v2.4.1",
    language: "go"
})

MERGE (sAuth:Service {
    id: "srv-auth-service",
    name: "auth-service",
    type: "auth",
    status: "healthy",
    anomaly_score: 0.05,
    failure_probability: 0.02,
    rps: 1200.0,
    error_rate: 0.001,
    latency_p95: 18.2,
    version: "v1.9.0",
    language: "rust"
})

MERGE (sUser:Service {
    id: "srv-user-service",
    name: "user-service",
    type: "business",
    status: "healthy",
    anomaly_score: 0.08,
    failure_probability: 0.04,
    rps: 850.0,
    error_rate: 0.003,
    latency_p95: 35.0,
    version: "v3.1.2",
    language: "python"
})

MERGE (sOrder:Service {
    id: "srv-order-service",
    name: "order-service",
    type: "business",
    status: "degraded",
    anomaly_score: 0.81,
    failure_probability: 0.78,
    rps: 920.0,
    error_rate: 0.145,
    latency_p95: 850.0,
    version: "v2.8.0",
    language: "java"
})

MERGE (sPayment:Service {
    id: "srv-payment-service",
    name: "payment-service",
    type: "payment",
    status: "critical",
    anomaly_score: 0.96,
    failure_probability: 0.94,
    rps: 410.0,
    error_rate: 0.380,
    latency_p95: 2450.0,
    version: "v2.1.0",
    language: "java"
})

MERGE (sInventory:Service {
    id: "srv-inventory-service",
    name: "inventory-service",
    type: "inventory",
    status: "degraded",
    anomaly_score: 0.65,
    failure_probability: 0.52,
    rps: 600.0,
    error_rate: 0.095,
    latency_p95: 390.0,
    version: "v1.7.4",
    language: "go"
})

MERGE (sShipping:Service {
    id: "srv-shipping-service",
    name: "shipping-service",
    type: "logistics",
    status: "healthy",
    anomaly_score: 0.12,
    failure_probability: 0.06,
    rps: 220.0,
    error_rate: 0.005,
    latency_p95: 48.0,
    version: "v1.4.0",
    language: "python"
})

MERGE (sNotification:Service {
    id: "srv-notification-service",
    name: "notification-service",
    type: "messaging",
    status: "healthy",
    anomaly_score: 0.09,
    failure_probability: 0.03,
    rps: 480.0,
    error_rate: 0.002,
    latency_p95: 22.0,
    version: "v2.0.1",
    language: "node"
})

MERGE (sRecommendation:Service {
    id: "srv-recommendation-service",
    name: "recommendation-service",
    type: "ml-service",
    status: "healthy",
    anomaly_score: 0.15,
    failure_probability: 0.08,
    rps: 750.0,
    error_rate: 0.008,
    latency_p95: 85.0,
    version: "v3.0.0",
    language: "python"
})

MERGE (sAnalytics:Service {
    id: "srv-analytics-service",
    name: "analytics-service",
    type: "data-pipeline",
    status: "healthy",
    anomaly_score: 0.04,
    failure_probability: 0.01,
    rps: 1500.0,
    error_rate: 0.001,
    latency_p95: 15.0,
    version: "v1.2.3",
    language: "scala"
})

MERGE (sBilling:Service {
    id: "srv-billing-service",
    name: "billing-service",
    type: "finance",
    status: "healthy",
    anomaly_score: 0.11,
    failure_probability: 0.05,
    rps: 180.0,
    error_rate: 0.004,
    latency_p95: 62.0,
    version: "v1.6.2",
    language: "java"
})

MERGE (sSearch:Service {
    id: "srv-search-service",
    name: "search-service",
    type: "search",
    status: "healthy",
    anomaly_score: 0.18,
    failure_probability: 0.09,
    rps: 1100.0,
    error_rate: 0.006,
    latency_p95: 55.0,
    version: "v2.2.0",
    language: "go"
});


// =============================================
// 3. SERVICE-TO-SERVICE CALL GRAPHS (CALLS)
// =============================================

// Gateway calls downstream services
MERGE (sGateway)-[:CALLS {weight: 0.35, rps: 1200.0, latency_p95: 18.2, error_rate: 0.001, protocol: "gRPC"}]->(sAuth)
MERGE (sGateway)-[:CALLS {weight: 0.25, rps: 850.0, latency_p95: 35.0, error_rate: 0.003, protocol: "HTTP/2"}]->(sUser)
MERGE (sGateway)-[:CALLS {weight: 0.20, rps: 920.0, latency_p95: 850.0, error_rate: 0.145, protocol: "gRPC"}]->(sOrder)
MERGE (sGateway)-[:CALLS {weight: 0.12, rps: 1100.0, latency_p95: 55.0, error_rate: 0.006, protocol: "HTTP/2"}]->(sSearch)
MERGE (sGateway)-[:CALLS {weight: 0.08, rps: 750.0, latency_p95: 85.0, error_rate: 0.008, protocol: "HTTP/2"}]->(sRecommendation)

// Order Service orchestration (Critical Path)
MERGE (sOrder)-[:CALLS {weight: 0.45, rps: 410.0, latency_p95: 2450.0, error_rate: 0.380, protocol: "gRPC"}]->(sPayment)
MERGE (sOrder)-[:CALLS {weight: 0.30, rps: 600.0, latency_p95: 390.0, error_rate: 0.095, protocol: "gRPC"}]->(sInventory)
MERGE (sOrder)-[:CALLS {weight: 0.15, rps: 220.0, latency_p95: 48.0, error_rate: 0.005, protocol: "HTTP/2"}]->(sShipping)
MERGE (sOrder)-[:CALLS {weight: 0.10, rps: 480.0, latency_p95: 22.0, error_rate: 0.002, protocol: "AMQP"}]->(sNotification)

// Payment Service downstream
MERGE (sPayment)-[:CALLS {weight: 0.50, rps: 180.0, latency_p95: 62.0, error_rate: 0.004, protocol: "gRPC"}]->(sBilling)
MERGE (sPayment)-[:CALLS {weight: 0.50, rps: 180.0, latency_p95: 22.0, error_rate: 0.001, protocol: "AMQP"}]->(sNotification)

// Search & Recs call User & Inventory
MERGE (sSearch)-[:CALLS {weight: 0.60, rps: 500.0, latency_p95: 390.0, error_rate: 0.040, protocol: "HTTP/2"}]->(sInventory)
MERGE (sRecommendation)-[:CALLS {weight: 0.40, rps: 300.0, latency_p95: 35.0, error_rate: 0.003, protocol: "HTTP/2"}]->(sUser)

// Analytics taps major flows (async read-only)
MERGE (sAnalytics)-[:CALLS {weight: 0.10, rps: 100.0, latency_p95: 15.0, error_rate: 0.001, protocol: "Kafka"}]->(sOrder)
MERGE (sAnalytics)-[:CALLS {weight: 0.10, rps: 80.0, latency_p95: 15.0, error_rate: 0.001, protocol: "Kafka"}]->(sPayment);


// =============================================
// 4. ARCHITECTURAL DEPENDENCY GRAPH (DEPENDS_ON)
// =============================================

MERGE (sOrder)-[:DEPENDS_ON {type: "hard", criticality: "high"}]->(sPayment)
MERGE (sOrder)-[:DEPENDS_ON {type: "hard", criticality: "high"}]->(sInventory)
MERGE (sOrder)-[:DEPENDS_ON {type: "soft", criticality: "medium"}]->(sShipping)
MERGE (sOrder)-[:DEPENDS_ON {type: "soft", criticality: "low"}]->(sNotification)
MERGE (sGateway)-[:DEPENDS_ON {type: "hard", criticality: "critical"}]->(sAuth)
MERGE (sGateway)-[:DEPENDS_ON {type: "hard", criticality: "high"}]->(sOrder)
MERGE (sPayment)-[:DEPENDS_ON {type: "hard", criticality: "high"}]->(sBilling);


// =============================================
// 5. INFRASTRUCTURE MAPPING (RUNS_ON)
// =============================================

// Node 1 hosts Edge & Auth
MERGE (sGateway)-[:RUNS_ON {replicas: 4, memory_limit: "2Gi", cpu_limit: "2000m"}]->(h1)
MERGE (sAuth)-[:RUNS_ON {replicas: 3, memory_limit: "1Gi", cpu_limit: "1000m"}]->(h1)
MERGE (sUser)-[:RUNS_ON {replicas: 3, memory_limit: "1Gi", cpu_limit: "1000m"}]->(h1)

// Node 2 hosts Core Business
MERGE (sOrder)-[:RUNS_ON {replicas: 4, memory_limit: "4Gi", cpu_limit: "2000m"}]->(h2)
MERGE (sShipping)-[:RUNS_ON {replicas: 2, memory_limit: "1Gi", cpu_limit: "1000m"}]->(h2)
MERGE (sNotification)-[:RUNS_ON {replicas: 2, memory_limit: "512Mi", cpu_limit: "500m"}]->(h2)
MERGE (sRecommendation)-[:RUNS_ON {replicas: 2, memory_limit: "4Gi", cpu_limit: "2000m"}]->(h2)

// Node 3 hosts Data / Financial / Heavy workloads
MERGE (sPayment)-[:RUNS_ON {replicas: 3, memory_limit: "4Gi", cpu_limit: "4000m"}]->(h3)
MERGE (sInventory)-[:RUNS_ON {replicas: 3, memory_limit: "2Gi", cpu_limit: "2000m"}]->(h3)
MERGE (sBilling)-[:RUNS_ON {replicas: 2, memory_limit: "2Gi", cpu_limit: "2000m"}]->(h3)
MERGE (sSearch)-[:RUNS_ON {replicas: 3, memory_limit: "4Gi", cpu_limit: "2000m"}]->(h3)
MERGE (sAnalytics)-[:RUNS_ON {replicas: 2, memory_limit: "4Gi", cpu_limit: "2000m"}]->(h3);


// =============================================
// 6. ACTIVE ANOMALIES & INCIDENTS (Fault Scenario)
// =============================================

// Root Cause Anomaly on Payment Service: Connection pool exhaustion
MERGE (anom1:Anomaly {
    id: "anom-payment-conn-pool-exhausted",
    metric_name: "db_connection_pool_active_ratio",
    metric_value: 0.998,
    threshold: 0.85,
    severity: "critical",
    status: "active",
    timestamp: "2026-09-22T21:45:00Z",
    description: "Database connection pool saturated at 99.8%. Thread starvation observed in PaymentService worker threads.",
    confidence: 0.97
})

// Secondary Anomaly on Payment Service: Latency spike
MERGE (anom2:Anomaly {
    id: "anom-payment-latency-spike",
    metric_name: "http_request_duration_seconds_p95",
    metric_value: 2.45,
    threshold: 0.50,
    severity: "critical",
    status: "active",
    timestamp: "2026-09-22T21:46:15Z",
    description: "p95 latency exceeded 2400ms threshold by 390%. Downstream timeouts triggering.",
    confidence: 0.95
})

// Cascading Anomaly on Order Service: Timeout cascade
MERGE (anom3:Anomaly {
    id: "anom-order-downstream-timeout",
    metric_name: "downstream_timeout_rate",
    metric_value: 0.380,
    threshold: 0.05,
    severity: "high",
    status: "active",
    timestamp: "2026-09-22T21:47:30Z",
    description: "Calls to PaymentService timing out after 2000ms SLA. Circuit breaker half-open.",
    confidence: 0.91
})

// Secondary Anomaly on Inventory Service: Lock contention
MERGE (anom4:Anomaly {
    id: "anom-inventory-lock-wait",
    metric_name: "db_row_lock_wait_time_ms",
    metric_value: 780.0,
    threshold: 150.0,
    severity: "medium",
    status: "active",
    timestamp: "2026-09-22T21:48:00Z",
    description: "Stock reservation lock wait times elevated due to hung checkout transactions.",
    confidence: 0.84
})

// Cascading Anomaly on API Gateway: HTTP 504 Gateway Timeouts
MERGE (anom5:Anomaly {
    id: "anom-gateway-504-spike",
    metric_name: "http_status_5xx_rate",
    metric_value: 0.082,
    threshold: 0.01,
    severity: "high",
    status: "active",
    timestamp: "2026-09-22T21:49:00Z",
    description: "Ingress 504 error rate spiked to 8.2% on /checkout and /order endpoints.",
    confidence: 0.89
})

// Connect Anomalies to Affected Services
MERGE (sPayment)-[:HAS_ANOMALY]->(anom1)
MERGE (sPayment)-[:HAS_ANOMALY]->(anom2)
MERGE (sOrder)-[:HAS_ANOMALY]->(anom3)
MERGE (sInventory)-[:HAS_ANOMALY]->(anom4)
MERGE (sGateway)-[:HAS_ANOMALY]->(anom5)

// Master Incident representing this cascading failure
MERGE (inc1:Incident {
    id: "inc-2026-0922-001",
    title: "Cascading Checkout & Payment Failure in US-East",
    status: "investigating",
    severity: "critical",
    created_at: "2026-09-22T21:50:00Z",
    root_cause_service_id: "srv-payment-service",
    root_cause_confidence: 0.94,
    description: "Checkout requests failing across US-East cluster due to database connection starvation in Payment Service cascading to Order Service and API Gateway."
})

// Connect Incident to Root Cause and Impacted Services
MERGE (inc1)-[:ROOT_CAUSE]->(sPayment)
MERGE (inc1)-[:IMPACTS]->(sOrder)
MERGE (inc1)-[:IMPACTS]->(sGateway)
MERGE (inc1)-[:IMPACTS]->(sInventory);
