#!/usr/bin/env python3
"""
GraphTriage - Multimodal Telemetry Data Generator
Generates correlated metrics, distributed traces (OpenTelemetry format),
and structured logs tied to injected microservice faults.

Author: Aarnav Mishra (PC 3 — Frontend & Evaluation Engineer)
Project: GRAPHTRIAGE
"""

import argparse
import datetime
import json
import os
import random
import uuid
from typing import Dict, List, Any

class TelemetryGenerator:
    def __init__(self, topology_path: str, window_minutes: int = 30, fault_start_minute: int = 10):
        self.topology_path = topology_path
        self.window_minutes = window_minutes
        self.fault_start_minute = min(fault_start_minute, window_minutes - 5)
        
        with open(topology_path, "r", encoding="utf-8") as f:
            self.topology = json.load(f)
            
        self.nodes = self.topology.get("nodes", [])
        self.edges = self.topology.get("edges", [])
        self.fault_info = self.topology.get("metadata", {}).get("fault_info", {})
        self.root_cause = self.fault_info.get("root_cause_node", "order-orchestrator")
        self.fault_type = self.fault_info.get("fault_type", "cpu_saturation")
        self.affected_nodes = set(self.fault_info.get("propagation_path", [self.root_cause]))
        self.fault_gradients = self.topology.get("fault_gradients", {})

    def generate_metrics(self) -> List[Dict[str, Any]]:
        """Generate time-series metrics per node with pre/post fault correlation."""
        records = []
        base_time = datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(minutes=self.window_minutes)

        for step in range(self.window_minutes):
            curr_time = (base_time + datetime.timedelta(minutes=step)).isoformat()
            is_fault_active = step >= self.fault_start_minute

            for node in self.nodes:
                node_id = node["id"]
                gradient = self.fault_gradients.get(node_id, 0.05)
                is_root = (node_id == self.root_cause)

                if not is_fault_active:
                    # Baseline steady-state
                    cpu = round(random.uniform(20.0, 40.0), 1)
                    memory = round(random.uniform(35.0, 55.0), 1)
                    latency = round(random.uniform(15.0, 35.0), 1)
                    error_rate = round(random.uniform(0.0, 0.2), 2)
                    req_rate = random.randint(80, 200)
                else:
                    # Fault injected & propagating
                    if is_root:
                        cpu = round(random.uniform(92.0, 99.5), 1)
                        memory = round(random.uniform(85.0, 98.0), 1)
                        latency = round(random.uniform(650.0, 1500.0), 1)
                        error_rate = round(random.uniform(15.0, 45.0), 2)
                        req_rate = random.randint(40, 100) # Throttled / failing
                    elif node_id in self.affected_nodes:
                        severity = gradient
                        cpu = round(random.uniform(40.0, 50.0 + severity * 35.0), 1)
                        memory = round(random.uniform(40.0, 50.0 + severity * 25.0), 1)
                        latency = round(random.uniform(30.0, 40.0 + severity * 400.0), 1)
                        error_rate = round(random.uniform(0.5, severity * 12.0), 2)
                        req_rate = random.randint(70, 180)
                    else:
                        cpu = round(random.uniform(20.0, 45.0), 1)
                        memory = round(random.uniform(35.0, 60.0), 1)
                        latency = round(random.uniform(15.0, 40.0), 1)
                        error_rate = round(random.uniform(0.0, 0.3), 2)
                        req_rate = random.randint(80, 200)

                records.append({
                    "timestamp": curr_time,
                    "service_id": node_id,
                    "tier": node.get("tier", "backend"),
                    "cpu_percent": cpu,
                    "memory_percent": memory,
                    "latency_ms": latency,
                    "error_rate_percent": error_rate,
                    "requests_per_sec": req_rate,
                    "is_fault_period": is_fault_active
                })

        return records

    def generate_traces(self, num_traces: int = 50) -> List[Dict[str, Any]]:
        """Generate OpenTelemetry-compatible distributed traces traversing services."""
        traces = []
        base_time = datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(minutes=15)
        
        # Build adjacency mapping
        adj: Dict[str, List[str]] = {}
        for edge in self.edges:
            src = edge["source"]
            tgt = edge["target"]
            adj.setdefault(src, []).append(tgt)

        gateways = [n["id"] for n in self.nodes if n.get("tier") == "gateway"] or [self.nodes[0]["id"]]

        for i in range(num_traces):
            trace_id = uuid.uuid4().hex
            start_offset_s = i * (15 * 60 // max(1, num_traces))
            trace_start = base_time + datetime.timedelta(seconds=start_offset_s)
            
            # Select root gateway
            gw = random.choice(gateways)
            spans = []
            
            root_span_id = uuid.uuid4().hex[:16]
            curr_time_ms = int(trace_start.timestamp() * 1000)
            
            # BFS path through microservices
            path = [gw]
            curr = gw
            for _ in range(random.randint(2, 5)):
                next_hops = adj.get(curr, [])
                if not next_hops:
                    break
                curr = random.choice(next_hops)
                path.append(curr)

            # Check if this trace touches the faulty root cause service
            hits_fault = (self.root_cause in path)
            total_duration = 0

            prev_span_id = None
            for idx, service in enumerate(path):
                span_id = root_span_id if idx == 0 else uuid.uuid4().hex[:16]
                is_faulty_svc = (service == self.root_cause)
                
                if is_faulty_svc:
                    span_duration = random.randint(450, 1800)
                    status_code = random.choice(["ERROR", "ERROR", "OK"])
                    http_status = 504 if status_code == "ERROR" else 200
                    tags = {
                        "http.status_code": http_status,
                        "error": status_code == "ERROR",
                        "error.type": "ServiceTimeoutException" if self.fault_type == "cascading_timeout" else "HighCPULatencyException",
                        "component": "HTTP Client",
                        "span.kind": "server"
                    }
                elif service in self.affected_nodes and hits_fault:
                    span_duration = random.randint(120, 450)
                    status_code = "ERROR" if random.random() < 0.3 else "OK"
                    http_status = 502 if status_code == "ERROR" else 200
                    tags = {
                        "http.status_code": http_status,
                        "error": status_code == "ERROR",
                        "component": "HTTP Client",
                        "span.kind": "server"
                    }
                else:
                    span_duration = random.randint(8, 45)
                    status_code = "OK"
                    http_status = 200
                    tags = {"http.status_code": 200, "error": False, "component": "HTTP Client", "span.kind": "server"}

                spans.append({
                    "span_id": span_id,
                    "parent_span_id": prev_span_id,
                    "service_name": service,
                    "operation_name": f"RPC /{service.replace('-', '_')}/process",
                    "start_time_epoch_ms": curr_time_ms + total_duration,
                    "duration_ms": span_duration,
                    "status": status_code,
                    "tags": tags
                })
                total_duration += span_duration
                prev_span_id = span_id

            traces.append({
                "trace_id": trace_id,
                "timestamp": trace_start.isoformat(),
                "total_duration_ms": total_duration,
                "status": "ERROR" if hits_fault and any(s["status"] == "ERROR" for s in spans) else "OK",
                "root_service": gw,
                "services_involved": path,
                "spans": spans
            })

        return traces

    def generate_logs(self, num_logs: int = 120) -> List[Dict[str, Any]]:
        """Generate correlated structured JSON logs."""
        logs = []
        base_time = datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(minutes=15)

        log_messages = {
            "normal": [
                "Request handled successfully with status 200",
                "Connection verified with upstream pool",
                "Cache hit for query key",
                "Successfully dispatched async notification task"
            ],
            "warning": [
                "Downstream response latency exceeding SLA (threshold: 300ms)",
                "Connection retry attempt 2 of 3 triggered",
                "Memory utilization threshold exceeded 80%",
                "Circuit breaker approaching trip threshold for destination"
            ],
            "error": [
                "Connection refused while contacting downstream dependency",
                "HTTP 504 Gateway Timeout: Read timed out after 3000ms",
                "Thread pool saturation: active threads at 100% capacity",
                "Deadlock detected in transactional database worker pool"
            ],
            "critical": [
                "FATAL: OutOfMemoryError in container runtime memory manager",
                "Critical failure in message queue consumer loop: queue exhausted",
                "Circuit breaker OPEN: all traffic rejected for service",
                "CPU starvation detected: core throttling initiated at 99.8% load"
            ]
        }

        for i in range(num_logs):
            time_offset = random.randint(0, 15 * 60)
            log_time = base_time + datetime.timedelta(seconds=time_offset)
            is_post_fault = (time_offset >= 5 * 60)

            # Pick service
            if is_post_fault and random.random() < 0.45:
                service = self.root_cause
                level = random.choices(["WARN", "ERROR", "CRITICAL"], weights=[20, 50, 30])[0]
            elif is_post_fault and random.random() < 0.35 and self.affected_nodes:
                service = random.choice(list(self.affected_nodes))
                level = random.choices(["INFO", "WARN", "ERROR"], weights=[20, 50, 30])[0]
            else:
                service = random.choice(self.nodes)["id"]
                level = random.choices(["INFO", "WARN"], weights=[90, 10])[0]

            msg_pool = {
                "INFO": log_messages["normal"],
                "WARN": log_messages["warning"],
                "ERROR": log_messages["error"],
                "CRITICAL": log_messages["critical"]
            }[level]

            entry = {
                "timestamp": log_time.isoformat(),
                "service": service,
                "level": level,
                "trace_id": uuid.uuid4().hex,
                "message": random.choice(msg_pool),
                "thread": f"worker-{random.randint(1, 8)}"
            }
            if level in ["ERROR", "CRITICAL"]:
                entry["stack_trace"] = f"org.graphtriage.exception.ServiceException: {entry['message']}\n  at {service}.handler.ProcessRequest(handler.go:142)\n  at runtime.gopark(proc.go:362)"

            logs.append(entry)

        # Sort logs chronologically
        logs.sort(key=lambda x: x["timestamp"])
        return logs

    def export_all(self, output_dir: str):
        """Export metrics, traces, and logs to JSON files."""
        os.makedirs(output_dir, exist_ok=True)

        metrics = self.generate_metrics()
        traces = self.generate_traces(num_traces=60)
        logs = self.generate_logs(num_logs=150)

        metrics_file = os.path.join(output_dir, "metrics.json")
        traces_file = os.path.join(output_dir, "traces.json")
        logs_file = os.path.join(output_dir, "logs.json")

        with open(metrics_file, "w", encoding="utf-8") as f:
            json.dump({"metrics": metrics, "count": len(metrics)}, f, indent=2)

        with open(traces_file, "w", encoding="utf-8") as f:
            json.dump({"traces": traces, "count": len(traces)}, f, indent=2)

        with open(logs_file, "w", encoding="utf-8") as f:
            json.dump({"logs": logs, "count": len(logs)}, f, indent=2)

        print(f"[✓] Exported Telemetry Data to: {output_dir}")
        print(f"    - Metrics: {len(metrics)} time points ({metrics_file})")
        print(f"    - Traces: {len(traces)} distributed traces ({traces_file})")
        print(f"    - Logs: {len(logs)} log statements ({logs_file})")

def main():
    parser = argparse.ArgumentParser(description="GraphTriage Multimodal Telemetry Generator")
    parser.add_argument("--topology", type=str, default="output/topology.json", help="Path to topology.json")
    parser.add_argument("--window-minutes", type=int, default=30, help="Observation window in minutes")
    parser.add_argument("--fault-start", type=int, default=10, help="Minute when fault occurs")
    parser.add_argument("--export-dir", type=str, default="output", help="Directory for output files")
    args = parser.parse_args()

    print(f"[*] Generating correlated multimodal telemetry from {args.topology}...")
    gen = TelemetryGenerator(topology_path=args.topology, window_minutes=args.window_minutes, fault_start_minute=args.fault_start)
    gen.export_all(args.export_dir)

if __name__ == "__main__":
    main()
