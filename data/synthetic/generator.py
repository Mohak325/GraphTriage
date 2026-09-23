#!/usr/bin/env python3
"""
GraphTriage - Synthetic Network Topology & Fault Generator
Generates realistic microservice topology graphs (50-500 nodes) with random/targeted
fault injection and exports to Neo4j-compatible CSVs and API-compatible JSON.

Author: Aarnav Mishra (PC 3 — Frontend & Evaluation Engineer)
Project: GRAPHTRIAGE
"""

import argparse
import csv
import json
import os
import random
from typing import Dict, List, Tuple, Any
import networkx as nx

SERVICE_TEMPLATES = [
    # Gateways
    ("api-gateway", "gateway", "gateway"),
    ("ingress-lb", "gateway", "gateway"),
    ("public-bff", "gateway", "gateway"),
    ("mobile-gateway", "gateway", "gateway"),
    
    # Frontend / Client facing
    ("web-frontend", "frontend", "service"),
    ("mobile-frontend", "frontend", "service"),
    ("admin-portal", "frontend", "service"),
    ("partner-portal", "frontend", "service"),

    # Core Business Services
    ("auth-service", "backend", "service"),
    ("user-profile-service", "backend", "service"),
    ("tenant-service", "backend", "service"),
    ("catalog-service", "backend", "service"),
    ("search-service", "backend", "service"),
    ("recommendation-engine", "backend", "service"),
    ("cart-service", "backend", "service"),
    ("order-orchestrator", "backend", "service"),
    ("order-fulfillment", "backend", "service"),
    ("payment-gateway-proxy", "backend", "service"),
    ("payment-processor", "backend", "service"),
    ("fraud-detection", "backend", "service"),
    ("billing-service", "backend", "service"),
    ("invoice-service", "backend", "service"),
    ("inventory-manager", "backend", "service"),
    ("warehouse-dispatcher", "backend", "service"),
    ("shipping-tracker", "backend", "service"),
    ("pricing-engine", "backend", "service"),
    ("discount-service", "backend", "service"),
    ("notification-dispatcher", "backend", "service"),
    ("email-service", "backend", "service"),
    ("sms-gateway", "backend", "service"),
    ("push-notification", "backend", "service"),
    ("audit-logger", "backend", "service"),
    ("analytics-collector", "backend", "service"),
    ("report-generator", "backend", "service"),

    # Data & Storage
    ("postgres-primary", "data", "database"),
    ("postgres-replica", "data", "database"),
    ("mysql-cluster", "data", "database"),
    ("mongodb-orders", "data", "database"),
    ("redis-cache-master", "data", "cache"),
    ("redis-session-store", "data", "cache"),
    ("memcached-cluster", "data", "cache"),
    ("elasticsearch-cluster", "data", "database"),
    ("neo4j-graph-db", "data", "database"),

    # Messaging / Queue
    ("kafka-broker-1", "messaging", "queue"),
    ("kafka-broker-2", "messaging", "queue"),
    ("kafka-broker-3", "messaging", "queue"),
    ("rabbitmq-orders", "messaging", "queue"),
    ("sqs-notification-queue", "messaging", "queue"),
]

FAULT_TYPES = [
    "cpu_saturation",
    "memory_leak_oom",
    "network_packet_loss",
    "db_pool_exhaustion",
    "cascading_timeout"
]

class MicroserviceTopologyGenerator:
    def __init__(self, node_count: int = 100, seed: int = 42):
        self.node_count = max(20, min(node_count, 1000))
        self.seed = seed
        random.seed(seed)
        self.graph = nx.DiGraph()
        self.fault_info: Dict[str, Any] = {}

    def _generate_node_list(self) -> List[Dict[str, Any]]:
        nodes = []
        base_len = len(SERVICE_TEMPLATES)
        
        for i in range(self.node_count):
            if i < base_len:
                base_name, tier, s_type = SERVICE_TEMPLATES[i]
                node_id = base_name
            else:
                base_name, tier, s_type = SERVICE_TEMPLATES[i % base_len]
                instance_idx = (i // base_len) + 1
                node_id = f"{base_name}-cluster-{instance_idx}"
            
            nodes.append({
                "id": node_id,
                "name": node_id,
                "type": s_type,
                "tier": tier,
                "anomaly_score": 0.05,
                "status": "healthy",
                "metrics": {
                    "cpu_percent": round(random.uniform(15.0, 45.0), 1),
                    "memory_percent": round(random.uniform(30.0, 60.0), 1),
                    "latency_p95": round(random.uniform(12.0, 45.0), 1),
                    "error_rate": round(random.uniform(0.0, 0.5), 2),
                }
            })
        return nodes

    def generate_topology(self) -> nx.DiGraph:
        """Construct a realistic layered microservice call graph."""
        nodes = self._generate_node_list()
        tier_map = {"gateway": [], "frontend": [], "backend": [], "data": [], "messaging": []}

        for n in nodes:
            self.graph.add_node(n["id"], **n)
            tier = n["tier"]
            if tier in tier_map:
                tier_map[tier].append(n["id"])

        # Layer 1: Gateways -> Frontends
        for gw in tier_map["gateway"]:
            targets = random.sample(tier_map["frontend"], min(len(tier_map["frontend"]), max(2, len(tier_map["frontend"]) // 2)))
            for tgt in targets:
                self.graph.add_edge(gw, tgt, type="CALLS", weight=round(random.uniform(0.7, 1.0), 2), latency_ms=round(random.uniform(4.0, 15.0), 1))

        # Layer 2: Frontends -> Core Backends
        for fe in tier_map["frontend"]:
            targets = random.sample(tier_map["backend"], min(len(tier_map["backend"]), max(4, len(tier_map["backend"]) // 3)))
            for tgt in targets:
                self.graph.add_edge(fe, tgt, type="CALLS", weight=round(random.uniform(0.5, 0.95), 2), latency_ms=round(random.uniform(10.0, 30.0), 1))

        # Layer 3: Backend -> Backend (service-to-service calls)
        backend_nodes = tier_map["backend"]
        for b_node in backend_nodes:
            # 2 to 5 downstream service calls
            k = min(len(backend_nodes) - 1, random.randint(1, 4))
            candidates = [x for x in backend_nodes if x != b_node and not self.graph.has_edge(x, b_node)]
            if candidates:
                targets = random.sample(candidates, min(len(candidates), k))
                for tgt in targets:
                    self.graph.add_edge(b_node, tgt, type="CALLS", weight=round(random.uniform(0.3, 0.8), 2), latency_ms=round(random.uniform(15.0, 45.0), 1))

        # Layer 4: Backend -> Data & Messaging
        for b_node in backend_nodes:
            # Connect to 1-2 databases or caches
            if tier_map["data"]:
                data_tgts = random.sample(tier_map["data"], min(len(tier_map["data"]), random.randint(1, 2)))
                for dt in data_tgts:
                    edge_type = "DEPENDS_ON" if "database" in self.graph.nodes[dt]["type"] else "CALLS"
                    self.graph.add_edge(b_node, dt, type=edge_type, weight=round(random.uniform(0.8, 1.0), 2), latency_ms=round(random.uniform(2.0, 12.0), 1))
            
            # Connect to messaging
            if tier_map["messaging"] and random.random() < 0.4:
                msg_tgt = random.choice(tier_map["messaging"])
                self.graph.add_edge(b_node, msg_tgt, type="WRITES_TO", weight=round(random.uniform(0.4, 0.9), 2), latency_ms=round(random.uniform(5.0, 15.0), 1))

        return self.graph

    def inject_fault(self, fault_type: str = "cpu_saturation", target_node: str = None) -> Dict[str, Any]:
        """Inject a fault and propagate anomaly gradients upstream."""
        if not target_node or target_node not in self.graph:
            backend_candidates = [n for n, d in self.graph.nodes(data=True) if d.get("tier") == "backend"]
            if not backend_candidates:
                backend_candidates = list(self.graph.nodes())
            target_node = random.choice(backend_candidates)

        if fault_type not in FAULT_TYPES:
            fault_type = random.choice(FAULT_TYPES)

        # Baseline metrics adjustment for root cause
        target_data = self.graph.nodes[target_node]
        target_data["anomaly_score"] = 0.98
        target_data["status"] = "critical"
        
        if fault_type == "cpu_saturation":
            target_data["metrics"]["cpu_percent"] = 98.4
            target_data["metrics"]["latency_p95"] = 840.5
            target_data["metrics"]["error_rate"] = 12.4
        elif fault_type == "memory_leak_oom":
            target_data["metrics"]["memory_percent"] = 99.2
            target_data["metrics"]["error_rate"] = 35.8
            target_data["metrics"]["latency_p95"] = 1200.0
        elif fault_type == "network_packet_loss":
            target_data["metrics"]["error_rate"] = 28.5
            target_data["metrics"]["latency_p95"] = 620.0
        elif fault_type == "db_pool_exhaustion":
            target_data["metrics"]["latency_p95"] = 2100.0
            target_data["metrics"]["error_rate"] = 42.0
            target_data["metrics"]["cpu_percent"] = 85.0
        elif fault_type == "cascading_timeout":
            target_data["metrics"]["latency_p95"] = 3400.0
            target_data["metrics"]["error_rate"] = 18.0

        # Calculate upstream fault propagation gradients
        fault_gradients = {node: 0.05 for node in self.graph.nodes()}
        fault_gradients[target_node] = 1.0

        # BFS upstream on predecessors (callers suffer degradation)
        queue = [(target_node, 1.0, 0)]
        visited = {target_node}

        decay_factor = 0.65
        while queue:
            curr_node, curr_gradient, depth = queue.pop(0)
            if depth >= 4:
                continue

            for pred in self.graph.predecessors(curr_node):
                if pred not in visited:
                    visited.add(pred)
                    edge_data = self.graph.get_edge_data(pred, curr_node)
                    weight = edge_data.get("weight", 0.7)
                    propagated_score = round(curr_gradient * decay_factor * weight, 3)
                    
                    fault_gradients[pred] = max(fault_gradients[pred], propagated_score)
                    
                    pred_data = self.graph.nodes[pred]
                    pred_data["anomaly_score"] = fault_gradients[pred]
                    if fault_gradients[pred] > 0.6:
                        pred_data["status"] = "critical"
                    elif fault_gradients[pred] > 0.3:
                        pred_data["status"] = "degraded"
                    
                    # Elevate latency and error rate for degraded services
                    pred_data["metrics"]["latency_p95"] += round(propagated_score * 300, 1)
                    pred_data["metrics"]["error_rate"] += round(propagated_score * 8.0, 2)
                    
                    queue.append((pred, propagated_score, depth + 1))

        self.fault_info = {
            "root_cause_node": target_node,
            "fault_type": fault_type,
            "injected_score": 0.98,
            "affected_node_count": len(visited),
            "propagation_path": list(visited),
            "fault_gradients": fault_gradients
        }
        return self.fault_info

    def export_neo4j_csv(self, output_dir: str):
        """Export nodes.csv and edges.csv compatible with Neo4j import."""
        os.makedirs(output_dir, exist_ok=True)
        nodes_path = os.path.join(output_dir, "nodes.csv")
        edges_path = os.path.join(output_dir, "edges.csv")

        # Nodes CSV
        with open(nodes_path, mode="w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["nodeId:ID", "name", "service_type", "tier", "anomaly_score:float", "status", ":LABEL"])
            for node_id, data in self.graph.nodes(data=True):
                writer.writerow([
                    node_id,
                    data.get("name", node_id),
                    data.get("type", "service"),
                    data.get("tier", "backend"),
                    data.get("anomaly_score", 0.05),
                    data.get("status", "healthy"),
                    "Service" if data.get("type") == "service" else "Resource"
                ])

        # Edges CSV
        with open(edges_path, mode="w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow([":START_ID", ":END_ID", "relationship_type:TYPE", "weight:float", "latency_ms:float"])
            for u, v, data in self.graph.edges(data=True):
                writer.writerow([
                    u,
                    v,
                    data.get("type", "CALLS"),
                    data.get("weight", 1.0),
                    data.get("latency_ms", 10.0)
                ])

        print(f"[✓] Exported Neo4j CSVs: {nodes_path}, {edges_path}")

    def export_json(self, output_path: str):
        """Export JSON matching GET /api/graph/topology contract."""
        os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
        
        nodes_list = []
        for node_id, data in self.graph.nodes(data=True):
            nodes_list.append({
                "id": node_id,
                "name": data.get("name", node_id),
                "type": data.get("type", "service"),
                "tier": data.get("tier", "backend"),
                "anomaly_score": round(data.get("anomaly_score", 0.05), 3),
                "status": data.get("status", "healthy"),
                "metrics": data.get("metrics", {})
            })

        edges_list = []
        for idx, (u, v, data) in enumerate(self.graph.edges(data=True)):
            edges_list.append({
                "id": f"e-{idx}-{u}-{v}",
                "source": u,
                "target": v,
                "type": data.get("type", "CALLS"),
                "weight": data.get("weight", 1.0),
                "latency_ms": data.get("latency_ms", 10.0)
            })

        payload = {
            "nodes": nodes_list,
            "edges": edges_list,
            "fault_gradients": self.fault_info.get("fault_gradients", {n: 0.05 for n in self.graph.nodes()}),
            "metadata": {
                "total_nodes": len(nodes_list),
                "total_edges": len(edges_list),
                "fault_info": self.fault_info
            }
        }

        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(payload, f, indent=2)

        print(f"[✓] Exported Topology JSON: {output_path}")
        return payload

def main():
    parser = argparse.ArgumentParser(description="GraphTriage Synthetic Topology Generator")
    parser.add_argument("--nodes", type=int, default=60, help="Number of nodes (50-500)")
    parser.add_argument("--seed", type=int, default=42, help="Random seed")
    parser.add_argument("--fault-type", type=str, default="cpu_saturation", choices=FAULT_TYPES)
    parser.add_argument("--fault-node", type=str, default="order-orchestrator", help="Target node for fault")
    parser.add_argument("--export-dir", type=str, default="output", help="Directory for output files")
    args = parser.parse_args()

    print(f"[*] Initializing GraphTriage Topology Generator ({args.nodes} nodes)...")
    generator = MicroserviceTopologyGenerator(node_count=args.nodes, seed=args.seed)
    generator.generate_topology()
    
    print(f"[*] Injecting fault '{args.fault_type}' into '{args.fault_node}'...")
    fault = generator.inject_fault(fault_type=args.fault_type, target_node=args.fault_node)
    print(f"    Root Cause Node: {fault['root_cause_node']}")
    print(f"    Affected Upstream Nodes: {fault['affected_node_count']}")

    export_dir = os.path.abspath(args.export_dir)
    generator.export_neo4j_csv(export_dir)
    json_path = os.path.join(export_dir, "topology.json")
    generator.export_json(json_path)
    print(f"[✓] Successfully generated synthetic topology.")

if __name__ == "__main__":
    main()
