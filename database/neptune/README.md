# Amazon Neptune Graph Database Migration & Architecture

> **Author:** Sandarbh Gupta (Graph & Backend Engineer)  
> **Course:** Cloud System Architecture / Cloud Architecture Design  
> **Component:** AWS Cloud Phase 4 — `database/neptune/`

---

## 1. Overview

As part of **Phase 4 (AWS Deployment)**, GraphTriage extends its topological intelligence engine from local Neo4j to **Amazon Neptune**, AWS's fully managed, serverless, and multi-AZ graph database service.

Amazon Neptune powers the explicit **Knowledge Graph** of microservices, underlying hosts, containers, subnets, and active anomalies. The graph structure allows the **Navigator Agent** to traverse causal paths and perform spectral fault gradient diffusion across high-dimensional dependency trees.

```
                      +---------------------------------------+
                      |       GraphTriage Backend / Agents    |
                      |   (Navigator / FaultGradientEngine)   |
                      +---------------------------------------+
                                          |
                              WebSocket / HTTPS (8182)
                               (Apache TinkerPop Gremlin)
                                          v
                      +---------------------------------------+
                      |         Amazon Neptune Cluster        |
                      |  - Multi-AZ Storage Engine            |
                      |  - Read Replicas (Auto-scaling)       |
                      |  - VPC Peering / PrivateLink Endpoint |
                      +---------------------------------------+
                                          ^
                                          | S3 Bulk Load API
                      +---------------------------------------+
                      |        Amazon S3 Staging Bucket       |
                      |  - neptune_vertices.csv               |
                      |  - neptune_edges.csv                  |
                      +---------------------------------------+
```

---

## 2. Cypher to Gremlin Translation Matrix

GraphTriage supports dual graph engines: **Neo4j Cypher** and **Amazon Neptune Gremlin**. The translation semantics used across our schema are summarized below:

| Operation | Neo4j Cypher | Amazon Neptune Gremlin |
|-----------|--------------|------------------------|
| **Fetch Vertex by ID** | `MATCH (s:Service {id: "srv-api-gateway"}) RETURN s` | `g.V().hasLabel('Service').has('entity_id', 'srv-api-gateway').valueMap(true)` |
| **All Services with Metrics** | `MATCH (s:Service) RETURN s.id, s.name, s.anomaly_score` | `g.V().hasLabel('Service').project('id', 'name', 'anomaly_score').by('entity_id').by('name').by('anomaly_score')` |
| **Call Dependency Edges** | `MATCH (a:Service)-[r:CALLS]->(b:Service) RETURN a.id, b.id, r.weight` | `g.E().hasLabel('CALLS').project('src', 'tgt', 'w').by(outV().values('entity_id')).by(inV().values('entity_id')).by('weight')` |
| **k-Hop Subgraph** | `MATCH path = (s:Service {id: $id})-[*1..2]-(n) RETURN path` | `g.V().hasLabel('Service').has('entity_id', id).repeat(bothE('CALLS').otherV().dedup()).times(2).emit().dedup()` |
| **Upsert Vertex** | `MERGE (s:Service {id: $id}) ON CREATE SET ... ON MATCH SET ...` | `g.V().hasLabel('Service').has('entity_id', id).fold().coalesce(unfold(), addV('Service').property('entity_id', id)).property('name', ...)` |
| **Upsert Edge** | `MATCH (a), (b) MERGE (a)-[r:CALLS]->(b) SET r.weight = $w` | `g.V().has('entity_id', src).as('a').V().has('entity_id', tgt).as('b').coalesce(inE('CALLS').where(outV().as('a')), addE('CALLS').from('a').to('b')).property('weight', w)` |

---

## 3. Automated Migration Script

The `cypher_to_gremlin_migrator.py` utility automatically reads the canonical Neo4j seed data (`database/seed_data.cypher`) and compiles both a native Gremlin Groovy console script and AWS Neptune Bulk Loader CSV files.

### Usage:

```bash
# Run migration and validation
python database/neptune/cypher_to_gremlin_migrator.py \
  --cypher database/seed_data.cypher \
  --output-dir database/neptune \
  --validate
```

### Outputs:
1. `database/neptune/seed_gremlin.groovy`: Gremlin console script for interactive execution.
2. `database/neptune/bulk_loader/neptune_vertices.csv`: Vertices with Neptune property types (`~id`, `~label`, `latency_p95:Double`, `rps:Double`).
3. `database/neptune/bulk_loader/neptune_edges.csv`: Edges with source/target endpoints (`~id`, `~from`, `~to`, `~label`, `weight:Double`).

---

## 4. AWS Neptune Provisioning Runbook

### Step 1: Provision Neptune DB Cluster (AWS CLI)
```bash
aws neptune create-db-cluster \
  --db-cluster-identifier graphtriage-neptune-cluster \
  --engine neptune \
  --engine-version 1.3.1.0 \
  --master-username admin \
  --master-user-password <SECURE_PASSWORD> \
  --vpc-security-group-ids sg-0123456789abcdef0 \
  --db-subnet-group-name graphtriage-neptune-subnet-group \
  --backup-retention-period 7 \
  --preferred-backup-window 02:00-03:00

aws neptune create-db-instance \
  --db-instance-identifier graphtriage-neptune-instance-1 \
  --db-instance-class db.t4g.medium \
  --engine neptune \
  --db-cluster-identifier graphtriage-neptune-cluster
```

### Step 2: Stage Bulk Load CSVs to Amazon S3
```bash
aws s3 mb s3://graphtriage-neptune-bulkload-us-east-1
aws s3 cp database/neptune/bulk_loader/ s3://graphtriage-neptune-bulkload-us-east-1/seed/ --recursive
```

### Step 3: Trigger Neptune Bulk Loader
```bash
curl -X POST \
  -H 'Content-Type: application/json' \
  https://graphtriage-neptune-cluster.cluster-custom.us-east-1.neptune.amazonaws.com:8182/loader \
  -d '{
    "source" : "s3://graphtriage-neptune-bulkload-us-east-1/seed/",
    "format" : "csv",
    "iamRoleArn" : "arn:aws:iam::123456789012:role/NeptuneS3BucketAccessRole",
    "region" : "us-east-1",
    "failOnError" : "FALSE",
    "parallelism" : "MEDIUM"
  }'
```

---

## 5. Python Client Integration

The `NeptuneClient` class in `database/neptune/neptune_client.py` provides transparent drop-in compatibility with GraphTriage's `FaultGradientEngine`:

```python
from database.neptune.neptune_client import NeptuneClient
from ai_models.graph_engine.fault_gradient import FaultGradientEngine

async def run_neptune_triage():
    client = NeptuneClient()
    
    # 1. Fetch live topology as NetworkX graph
    G = await client.get_topology_graph()
    
    # 2. Run spectral fault gradient diffusion
    engine = FaultGradientEngine()
    result = engine.compute(G)
    
    print(f"Top Suspicious Root Cause: {result.root_cause_id}")
    print(f"Confidence: {result.confidence_score:.2%}")
```
