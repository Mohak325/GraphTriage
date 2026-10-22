"""
Synthetic Telemetry & Contamination Generator (5% Contamination Baseline)
Author: Sandarbh Gupta (24BIT0506) - Subsystem 2
Paper Grounding: MNSUAD (Paper 1 - Johari et al., IEEE TMC 2025)
"""

import numpy as np
import pandas as pd
from typing import Tuple, Dict, Any, List, Optional


def generate_clean_telemetry(
    n_samples: int = 1000,
    n_features: int = 10,
    seed: int = 42
) -> np.ndarray:
    """
    Generates clean stationary multivariate metric time-series (e.g. 5GC / VNF KPIs).
    """
    np.random.seed(seed)
    time = np.linspace(0, 50, n_samples)
    data = np.zeros((n_samples, n_features))
    
    for i in range(n_features):
        freq = 0.1 + 0.05 * (i % 3)
        trend = 0.02 * time
        seasonal = 2.0 * np.sin(freq * time + i)
        noise = np.random.normal(0, 0.3, n_samples)
        data[:, i] = 20.0 + trend + seasonal + noise
        
    return data


def inject_unlabeled_contamination(
    data: np.ndarray,
    contamination_rate: float = 0.05,
    seed: int = 42
) -> Tuple[np.ndarray, np.ndarray]:
    """
    Injects up to 5.0% unlabeled anomalous contamination into historical baseline data.
    Simulates Vodafone NFV production dataset conditions (Paper 1).
    """
    np.random.seed(seed)
    n_samples, n_features = data.shape
    n_anomalies = int(n_samples * contamination_rate)
    
    contaminated_data = data.copy()
    anomaly_indices = np.random.choice(n_samples, size=n_anomalies, replace=False)
    true_anomaly_mask = np.zeros(n_samples, dtype=bool)
    true_anomaly_mask[anomaly_indices] = True
    
    for idx in anomaly_indices:
        anomaly_type = np.random.choice(["spike", "shift", "noise_burst"])
        target_features = np.random.choice(n_features, size=min(3, n_features), replace=False)
        
        if anomaly_type == "spike":
            contaminated_data[idx, target_features] += np.random.uniform(8.0, 15.0, size=len(target_features))
        elif anomaly_type == "shift":
            contaminated_data[idx, target_features] -= np.random.uniform(5.0, 10.0, size=len(target_features))
        else:
            contaminated_data[idx, target_features] += np.random.normal(0, 5.0, size=len(target_features))
            
    return contaminated_data, true_anomaly_mask


def generate_5gc_component_telemetry(
    components: List[str] = ["amf-01", "smf-02", "upf-edge-3", "router-core-2"],
    n_steps: int = 120,
    faulty_component: Optional[str] = "amf-01",
    seed: int = 42
) -> Dict[str, pd.DataFrame]:
    """
    Generates synchronized multivariate time series for 5GC network functions,
    injecting a root cause fault on `faulty_component` at t=80..120.
    """
    np.random.seed(seed)
    telemetry = {}
    
    for comp in components:
        t = np.arange(n_steps)
        # Standardized 5GC KPIs normalized to nominal ranges
        cpu = 25.0 + 3.0 * np.sin(t * 0.1) + np.random.normal(0, 1.0, n_steps)
        mem = 40.0 + 0.02 * t + np.random.normal(0, 0.5, n_steps)
        net_io = 50.0 + 5.0 * np.cos(t * 0.05) + np.random.normal(0, 2.0, n_steps)
        errors = np.random.poisson(0.1, n_steps).astype(float)
        
        # Inject realistic fault on faulty_component
        if faulty_component and comp == faulty_component:
            # High severity failure on faulty component: CPU saturation and error storm
            cpu[80:] += np.linspace(30, 65, n_steps - 80)
            errors[80:] += np.random.poisson(15.0, n_steps - 80)
            net_io[80:] *= 0.1
            
        df = pd.DataFrame({
            "timestamp": pd.date_range("2026-10-15 14:00:00", periods=n_steps, freq="5s"),
            "component": comp,
            "cpu_saturation": np.clip(cpu, 0, 100),
            "memory_usage": np.clip(mem, 0, 100),
            "network_io_mbps": np.maximum(0, net_io),
            "http_5xx_errors": np.maximum(0, errors)
        })
        telemetry[comp] = df
        
    return telemetry
