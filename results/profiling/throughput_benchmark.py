"""Throughput Benchmark for GraphTriage Ingestion & Query APIs.

Measures requests-per-second (RPS) throughput and latency percentiles under concurrent load
for telemetry ingestion and Cytoscape topology retrieval.
"""

import time
import json
import os
import sys
import concurrent.futures
from typing import Dict, Any, List

# Add project root to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from fastapi.testclient import TestClient
from backend.main import app


def benchmark_endpoint(
    client: TestClient,
    method: str,
    path: str,
    payload: Any = None,
    total_requests: int = 200,
    concurrency: int = 10
) -> Dict[str, Any]:
    """Execute concurrent requests against FastAPI endpoint using worker thread pool."""
    latencies = []

    def _make_call():
        t0 = time.perf_counter()
        if method == "GET":
            resp = client.get(path)
        else:
            resp = client.post(path, json=payload)
        elapsed_ms = (time.perf_counter() - t0) * 1000.0
        return resp.status_code, elapsed_ms

    wall_start = time.perf_counter()
    with concurrent.futures.ThreadPoolExecutor(max_workers=concurrency) as executor:
        futures = [executor.submit(_make_call) for _ in range(total_requests)]
        for f in concurrent.futures.as_completed(futures):
            code, el = f.result()
            latencies.append(el)

    total_wall_time = time.perf_counter() - wall_start
    rps = total_requests / total_wall_time if total_wall_time > 0 else 0

    import numpy as np
    p50 = float(np.percentile(latencies, 50))
    p90 = float(np.percentile(latencies, 90))
    p99 = float(np.percentile(latencies, 99))

    return {
        "endpoint": path,
        "method": method,
        "total_requests": total_requests,
        "concurrency": concurrency,
        "wall_time_sec": round(total_wall_time, 3),
        "rps": round(rps, 2),
        "p50_ms": round(p50, 2),
        "p90_ms": round(p90, 2),
        "p99_ms": round(p99, 2)
    }


def run_all_benchmarks():
    client = TestClient(app)
    results = []

    print("=" * 80)
    print("GRAPHTRIAGE — API Throughput & Latency Benchmarks")
    print("=" * 80)

    # 1. Topology retrieval
    print("Benchmarking: GET /api/graph/topology...")
    res_topo = benchmark_endpoint(client, "GET", "/api/graph/topology", total_requests=100, concurrency=10)
    results.append(res_topo)

    # 2. Fault heatmap
    print("Benchmarking: GET /api/graph/heatmap...")
    res_heat = benchmark_endpoint(client, "GET", "/api/graph/heatmap", total_requests=100, concurrency=10)
    results.append(res_heat)

    # 3. Metric ingestion batch
    metric_batch = {
        "batch": [
            {"service_id": f"srv-service-{i}", "metric_name": "latency_p95", "value": 120.5 + i}
            for i in range(20)
        ]
    }
    print("Benchmarking: POST /api/ingest/metrics (20 points/batch)...")
    res_metric = benchmark_endpoint(client, "POST", "/api/ingest/metrics", payload=metric_batch, total_requests=100, concurrency=10)
    results.append(res_metric)

    print("-" * 80)
    print(f"{'Endpoint':<30} {'RPS':<10} {'P50 (ms)':<12} {'P90 (ms)':<12} {'P99 (ms)':<12}")
    print("-" * 80)
    for r in results:
        print(f"{r['endpoint']:<30} {r['rps']:<10.1f} {r['p50_ms']:<12.2f} {r['p90_ms']:<12.2f} {r['p99_ms']:<12.2f}")
    print("=" * 80)

    out_dir = os.path.join(os.path.dirname(__file__), "output")
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "throughput_results.json")
    with open(out_path, "w") as f:
        json.dump(results, f, indent=2)
    print(f"Results saved to: {out_path}")


if __name__ == "__main__":
    run_all_benchmarks()
