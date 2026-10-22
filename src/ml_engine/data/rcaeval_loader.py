"""
RCAEval Dataset Local Loader & Graph Adapter
Author: Sandarbh Gupta (24BIT0506) - Subsystem 2
Reference: Pham et al. (ACM WWW 2025) RCAEval: A Benchmark for Root Cause Analysis
"""

import os
from typing import Dict, Any, List, Optional
import pandas as pd
import numpy as np


class RcaEvalCase:
    """
    Encapsulates a single RCAEval failure case containing:
    - Multi-modal metrics dataframe
    - Log text lines / templates
    - Distributed trace spans (caller-callee)
    - Ground truth root cause service
    """
    def __init__(
        self,
        case_id: str,
        system_name: str,  # train-ticket | social-network | online-boutique
        fault_type: str,   # pod_kill | cpu_stress | memory_leak | network_delay
        root_cause_service: str,
        metrics_df: pd.DataFrame,
        traces_df: pd.DataFrame,
        logs: List[str]
    ):
        self.case_id = case_id
        self.system_name = system_name
        self.fault_type = fault_type
        self.root_cause_service = root_cause_service
        self.metrics_df = metrics_df
        self.traces_df = traces_df
        self.logs = logs

    def get_service_list(self) -> List[str]:
        if "service" in self.metrics_df.columns:
            return sorted(self.metrics_df["service"].unique().tolist())
        elif "service_name" in self.traces_df.columns:
            return sorted(self.traces_df["service_name"].unique().tolist())
        return [self.root_cause_service]


class RcaEvalLoader:
    """
    Local loader for RCAEval benchmark datasets. Can load from local files or synthesize
    standard-compliant benchmark cases offline.
    """
    def __init__(self, base_dir: str = "data/rcaeval"):
        self.base_dir = base_dir

    def create_mock_case(
        self,
        case_id: str = "CASE-TT-001",
        system_name: str = "train-ticket",
        fault_type: str = "cpu_stress",
        root_cause_service: str = "ts-order-service"
    ) -> RcaEvalCase:
        """
        Synthesizes a realistic RCAEval benchmark incident case with metrics, traces, and logs.
        """
        services = [
            "ts-ui-dashboard",
            "ts-order-service",
            "ts-payment-service",
            "ts-station-service",
            "ts-ticketinfo-service"
        ]
        
        # 1. Metrics: 60 time points per service
        records = []
        for s in services:
            for t in range(60):
                is_fault = (s == root_cause_service and t >= 30)
                cpu = 20.0 + np.random.normal(0, 2.0)
                mem = 35.0 + np.random.normal(0, 1.0)
                latency = 45.0 + np.random.normal(0, 5.0)
                
                if is_fault:
                    cpu += 65.0  # high CPU stress
                    latency += 180.0  # latency spillover
                
                records.append({
                    "timestamp": t,
                    "service": s,
                    "cpu_usage": max(0, min(100, cpu)),
                    "memory_usage": max(0, min(100, mem)),
                    "latency_ms": max(0, latency),
                    "error_count": 5 if is_fault else 0
                })
        metrics_df = pd.DataFrame(records)
        
        # 2. Distributed Traces: UI -> Order -> Payment
        trace_records = [
            {"trace_id": "tr-01", "span_id": "sp-1", "parent_span_id": None, "service_name": "ts-ui-dashboard", "duration_ms": 250.0, "status_code": 200},
            {"trace_id": "tr-01", "span_id": "sp-2", "parent_span_id": "sp-1", "service_name": "ts-order-service", "duration_ms": 220.0, "status_code": 500},
            {"trace_id": "tr-01", "span_id": "sp-3", "parent_span_id": "sp-2", "service_name": "ts-payment-service", "duration_ms": 30.0, "status_code": 200},
            {"trace_id": "tr-02", "span_id": "sp-4", "parent_span_id": None, "service_name": "ts-ui-dashboard", "duration_ms": 190.0, "status_code": 200},
            {"trace_id": "tr-02", "span_id": "sp-5", "parent_span_id": "sp-4", "service_name": "ts-station-service", "duration_ms": 40.0, "status_code": 200},
        ]
        traces_df = pd.DataFrame(trace_records)
        
        # 3. Logs
        logs = [
            f"[INFO] ts-ui-dashboard: HTTP GET /order/create received",
            f"[ERROR] {root_cause_service}: Thread pool exhausted - CPU utilization > 95%",
            f"[WARN] {root_cause_service}: Upstream call timeout to payment gateway",
            f"[INFO] ts-station-service: Route query completed in 32ms"
        ]
        
        return RcaEvalCase(
            case_id=case_id,
            system_name=system_name,
            fault_type=fault_type,
            root_cause_service=root_cause_service,
            metrics_df=metrics_df,
            traces_df=traces_df,
            logs=logs
        )
