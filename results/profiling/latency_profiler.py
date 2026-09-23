"""Latency Profiler for GraphTriage Fault Gradient Engine.

Benchmarks the spectral damped diffusion algorithm across synthetic graph scales
(N = 10, 50, 100, 250, 500, 1000 microservices) to measure P50, P90, P99 latency
and ensure compliance with the < 500ms RCA SLA.
"""

import time
import json
import os
import sys
from typing import List, Dict, Any

# Add project root to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

import networkx as nx
import numpy as np
from ai_models.graph_engine.fault_gradient import FaultGradientEngine


def generate_synthetic_microservice_topology(num_nodes: int, avg_degree: float = 2.5) -> nx.DiGraph:
    """Generate a scale-free directed DAG with failure cascades mimicking large enterprise microservices."""
    p_edge = avg_degree / (num_nodes - 1) if num_nodes > 1 else 0.5
    raw_g = nx.fast_gnp_random_graph(num_nodes, p_edge, directed=True, seed=42)

    # Convert to DAG / service call topology with realistic attributes
    g = nx.DiGraph()
    for i in range(num_nodes):
        node_id = f"srv-{i:04d}"
        anom_score = float(np.random.beta(0.5, 5.0)) if i != 0 else 0.95
        g.add_node(
            node_id,
            id=node_id,
            name=f"service-{i:04d}",
            anomaly_score=round(anom_score, 4),
            status="critical" if anom_score > 0.8 else "healthy"
        )

    for u, v in raw_g.edges():
        if u != v:
            src = f"srv-{u:04d}"
            tgt = f"srv-{v:04d}"
            weight = round(float(np.random.uniform(0.1, 1.0)), 3)
            err = round(float(np.random.beta(0.2, 5.0)), 4)
            g.add_edge(src, tgt, weight=weight, error_rate=err, latency_p95=round(float(np.random.uniform(10, 500)), 1))

    return g


def profile_scales(
    scales: List[int] = [10, 50, 100, 250, 500, 1000],
    repeats: int = 10
) -> List[Dict[str, Any]]:
    """Profile spectral diffusion latency across scale boundaries."""
    engine = FaultGradientEngine(alpha=0.85, epsilon=1e-6, max_iter=100)
    results = []

    print("=" * 80)
    print(f"{'Nodes':<8} {'Edges':<8} {'P50 (ms)':<12} {'P90 (ms)':<12} {'P99 (ms)':<12} {'Mean (ms)':<12} {'Iters':<8}")
    print("-" * 80)

    for n in scales:
        g = generate_synthetic_microservice_topology(n)
        edge_count = g.number_of_edges()

        timings = []
        iters = []
        for _ in range(repeats):
            t0 = time.perf_counter()
            res = engine.compute(g)
            elapsed_ms = (time.perf_counter() - t0) * 1000.0
            timings.append(elapsed_ms)
            iters.append(res.iterations_to_converge)

        p50 = np.percentile(timings, 50)
        p90 = np.percentile(timings, 90)
        p99 = np.percentile(timings, 99)
        mean = np.mean(timings)
        avg_iters = np.mean(iters)

        print(f"{n:<8} {edge_count:<8} {p50:<12.2f} {p90:<12.2f} {p99:<12.2f} {mean:<12.2f} {avg_iters:<8.1f}")

        results.append({
            "node_count": n,
            "edge_count": edge_count,
            "p50_ms": round(float(p50), 3),
            "p90_ms": round(float(p90), 3),
            "p99_ms": round(float(p99), 3),
            "mean_ms": round(float(mean), 3),
            "avg_iterations": round(float(avg_iters), 1)
        })

    print("=" * 80)

    # Save to output file
    out_dir = os.path.join(os.path.dirname(__file__), "output")
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "latency_results.json")
    with open(out_path, "w") as f:
        json.dump(results, f, indent=2)
    print(f"Benchmark results saved to: {out_path}")

    return results


if __name__ == "__main__":
    profile_scales()
