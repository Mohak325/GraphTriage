# AWS Telemetry & Observability Pipeline

> **Author:** Sandarbh Gupta (Graph & Backend Engineer)  
> **Course:** Cloud System Architecture / Cloud Architecture Design  
> **Component:** AWS Cloud Phase 4 — `docker/aws/`

---

## 1. Architecture Overview

In a distributed cloud-native microservice environment, cascading outages produce massive alarm storms and log floods. The GraphTriage **AWS Telemetry Pipeline** continuously ingests, parses, and normalizes multi-modal telemetry streams (metrics, traces, and logs) using **Amazon CloudWatch** and **Amazon OpenSearch Service**.

```
  +-------------------------------------------------------------------------+
  |                     Microservice Mesh (Docker / EKS)                    |
  |  [api-gateway]  [order-service]  [payment-service]  [inventory-service] |
  +-------------------------------------------------------------------------+
           |                                             |
           | stdout / stderr Logs                        | System & Custom KPIs
           v                                             v
  +----------------------+                     +---------------------------+
  |  Fluent Bit Router   |                     |  Amazon CloudWatch Agent  |
  |  - JSON Parser       |                     |  - CPU / Memory / Disk / IO|
  |  - Anomaly Tagger    |                     |  - High-res Custom Metrics|
  +----------------------+                     +---------------------------+
           |                                             |
           +--------------------+   +--------------------+
                                |   |
                                v   v
                      +---------------------------------------+
                      |     Amazon OpenSearch Service 2.x     |
                      |  - graphtriage-metrics-*              |
                      |  - graphtriage-traces-*               |
                      |  - graphtriage-logs-*                 |
                      +---------------------------------------+
                                          |
                                          v (Continuous polling & threshold checks)
                      +---------------------------------------+
                      |   Telemetry Pipeline Stream Adapter   |
                      |     (docker/aws/telemetry_pipeline.py)|
                      +---------------------------------------+
                                          |
                                          | POST /api/ingest/anomaly
                                          v
                      +---------------------------------------+
                      |        GraphTriage API & Agents       |
                      |   (FaultGradientEngine & RCA Flow)    |
                      +---------------------------------------+
```

---

## 2. Telemetry Components & Files

| Component | File | Description |
|-----------|------|-------------|
| **CloudWatch Config** | `cloudwatch-agent-config.json` | High-resolution metric scraping (10s intervals) and container log group routing |
| **Fluent Bit Config** | `fluent-bit.conf` | Tail log collector with regex/JSON parsers and stream routing |
| **Fluent Bit Parsers** | `fluent-bit-parsers.conf` | Pre-configured regex parsers for container JSON, Nginx access logs, and microservice errors |
| **OpenSearch Templates** | `opensearch_index_templates.json` | Schema mappings for metrics, distributed traces, and log documents |
| **Stream Adapter** | `telemetry_pipeline.py` | Python event processor that computes anomaly scores from telemetry spikes |
| **Local Emulation Stack**| `docker-compose.aws.yml` | Standalone Docker stack with OpenSearch 2.11, OpenSearch Dashboards, and Fluent Bit |

---

## 3. Running Local AWS Observability Stack

You can test the full AWS telemetry stack locally without incurring AWS cloud costs:

```bash
# 1. Start OpenSearch and OpenSearch Dashboards
docker compose -f docker/aws/docker-compose.aws.yml up -d

# 2. Verify OpenSearch health
curl -s http://localhost:9200/_cat/health?v

# 3. Access OpenSearch Dashboards UI
# Open in browser: http://localhost:5601

# 4. Run the Telemetry Pipeline Stream Adapter
python docker/aws/telemetry_pipeline.py
```

---

## 4. Anomaly Detection Thresholds

The `TelemetryPipeline` applies heuristic and statistical thresholds to identify faulty components in real time:

- **Error Rate SLA Violation:** When `error_rate > 5.0%` (score scaled up to `1.0`).
- **Latency Breach:** When `latency_p95 > 500.0ms` (score scaled up to `1.0`).
- **Connection Saturated:** When `connection_pool_active_ratio > 85.0%`.
- **Log Burst Density:** When $\ge 3$ `ERROR` / `CRITICAL` entries occur within a single sliding window.

Detected anomalies are formatted as `AnomalyEvent` records and dispatched directly to the GraphTriage backend (`POST /api/ingest/anomaly`), where the **Fault Gradient Engine** diffuses the scores across the topology graph to isolate the root cause.
