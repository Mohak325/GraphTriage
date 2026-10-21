"""
Test Suite for 3-Layer KPI Filter and SOMP Normalization Engine.
Grounding: IEEE ISCC 2025 & Paper 4 (TeleGAN-Core).
"""

import numpy as np
import pandas as pd
import pytest

from src.hygiene.entropy_filter import compute_shannon_entropy, filter_kpi_by_entropy
from src.hygiene.noise_decomposition import decompose_and_filter_noise
from src.hygiene.correlation_consolidator import consolidate_correlated_kpis
from src.hygiene.somp_normalizer import SOMPNormalizer
from src.hygiene.pipeline import TelemetryHygienePipeline


def test_shannon_entropy_constant_series_dropped():
    # Completely constant series has zero entropy
    constant_series = np.array([42.0] * 100)
    keep, h = filter_kpi_by_entropy(constant_series, tau1=0.05)
    assert keep is False
    assert h == 0.0


def test_shannon_entropy_dynamic_series_kept():
    # Dynamic sinusoidal / gaussian series has high entropy
    np.random.seed(42)
    dynamic_series = np.sin(np.linspace(0, 20, 100)) + np.random.normal(0, 0.2, 100)
    keep, h = filter_kpi_by_entropy(dynamic_series, tau1=0.05)
    assert keep is True
    assert h > 0.5


def test_correlation_consolidator_removes_collinear():
    # Create two nearly identical KPIs (r > 0.99) and one independent KPI
    np.random.seed(42)
    base = np.random.rand(100)
    collinear = base * 2.0 + np.random.normal(0, 0.001, 100)
    independent = np.random.rand(100)

    df = pd.DataFrame({
        "packets_sent": base,
        "bytes_sent": collinear,
        "temperature": independent
    })

    kept, dropped, mapping = consolidate_correlated_kpis(df, tau3=0.95)

    assert len(kept) == 2
    assert len(dropped) == 1
    assert "temperature" in kept
    assert dropped[0] in ["packets_sent", "bytes_sent"]


def test_somp_monotonic_counter_and_reset_safety():
    normalizer = SOMPNormalizer(default_counter_max=2**32)
    comp = "amf-01"
    metric = "requests_total"

    # Step 1: initial baseline
    d1, r1 = normalizer.compute_counter_delta(comp, metric, 1000.0)
    assert d1 == 0.0
    assert r1 is False

    # Step 2: normal increment
    d2, r2 = normalizer.compute_counter_delta(comp, metric, 1250.0)
    assert d2 == 250.0
    assert r2 is False

    # Step 3: Container restart / reboot (counter drops from 1250 to 50)
    d3, r3 = normalizer.compute_counter_delta(comp, metric, 50.0)
    # MUST NOT be negative!
    assert d3 >= 0.0
    assert r3 is True
    assert d3 == 50.0


def test_somp_modular_integer_wrap_around():
    normalizer = SOMPNormalizer(default_counter_max=1000)
    comp = "upf-01"
    metric = "bytes_total"

    # Set initial near max
    normalizer.compute_counter_delta(comp, metric, 950.0)

    # Wrap around to 30
    delta, reset = normalizer.compute_counter_delta(comp, metric, 30.0)
    # Expected: (1000 - 950) + 30 = 80
    assert delta == 80.0
    assert reset is True


def test_somp_gauge_aggregation():
    values = [10.0, 20.0, 30.0, 40.0, 50.0]
    assert SOMPNormalizer.aggregate_gauge(values, method="mean") == 30.0
    assert SOMPNormalizer.aggregate_gauge(values, method="median") == 30.0
    assert SOMPNormalizer.aggregate_gauge(values, method="max") == 50.0


def test_integrated_hygiene_pipeline():
    np.random.seed(42)
    n_steps = 100

    # Build matrix with:
    # 5 constant KPIs
    # 3 collinear pairs (6 KPIs)
    # 2 informative dynamic KPIs
    data = {}
    for i in range(5):
        data[f"static_kpi_{i}"] = np.array([10.0] * n_steps)

    for i in range(3):
        base = np.sin(np.linspace(0, 10, n_steps)) + np.random.normal(0, 0.05, n_steps)
        data[f"dyn_kpi_{i}_a"] = base
        data[f"dyn_kpi_{i}_b"] = base * 1.5 + np.random.normal(0, 0.001, n_steps)

    data["cpu_load"] = np.random.uniform(20, 80, n_steps)
    data["mem_load"] = np.random.uniform(40, 90, n_steps)

    df_raw = pd.DataFrame(data)
    initial_count = df_raw.shape[1]  # 5 + 6 + 2 = 13

    pipeline = TelemetryHygienePipeline(tau1_entropy=0.05, tau3_correlation=0.95)
    result = pipeline.process_kpi_matrix(df_raw)

    assert result["initial_kpi_count"] == 13
    # All 5 static KPIs must be eliminated
    for i in range(5):
        assert f"static_kpi_{i}" in result["entropy_dropped"]

    # Redundancy in collinear pairs must be eliminated
    assert len(result["collinear_dropped"]) >= 2
    # Elimination ratio should be significant (>50% on this synthetic test)
    assert result["elimination_ratio"] > 0.50
    assert not result["filtered_df"].empty
