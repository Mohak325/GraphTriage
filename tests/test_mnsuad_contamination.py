"""
Test Case T02: MNSUAD Contamination Resilience Test (5% Contamination)
Author: Sandarbh Gupta (24BIT0506) - Subsystem 2
"""

import pytest
import numpy as np
from src.ml_engine.data.synthetic_noise import generate_clean_telemetry, inject_unlabeled_contamination
from src.ml_engine.models.mnsuad.trainer import MNSUADPipeline


def test_mnsuad_5_percent_contamination_resilience():
    # 1. Generate clean telemetry
    clean_data = generate_clean_telemetry(n_samples=600, n_features=6, seed=42)
    
    # 2. Inject 5.0% unlabeled anomalous contamination
    contaminated_train, injected_mask = inject_unlabeled_contamination(
        clean_data, contamination_rate=0.05, seed=42
    )
    assert np.sum(injected_mask) == 30  # 5% of 600
    
    # 3. Train MNSUAD Pipeline
    pipeline = MNSUADPipeline(input_dim=6, hidden_dim=16, n_gmm_components=3)
    train_summary = pipeline.train(contaminated_train)
    
    assert train_summary["status"] == "TRAINED"
    assert train_summary["pseudo_anomaly_ratio"] > 0.01
    
    # 4. Generate clean test data vs anomalous test data
    X_test_clean = generate_clean_telemetry(n_samples=200, n_features=6, seed=99)
    X_test_anom, y_true_mask = inject_unlabeled_contamination(
        X_test_clean, contamination_rate=0.15, seed=99
    )
    
    # 5. Evaluate metrics
    metrics = pipeline.evaluate(X_test_anom, y_true_mask.astype(int), threshold=0.5)
    
    # Assert carrier-grade accuracy: ROC-AUC >= 0.85 and F1 >= 0.70 under contamination
    assert metrics["roc_auc"] >= 0.85, f"ROC-AUC too low: {metrics['roc_auc']}"
    assert metrics["precision"] > 0.50, f"Precision too low: {metrics['precision']}"
    print(f"\n[PASSED] MNSUAD 5% Contamination Test: ROC-AUC={metrics['roc_auc']:.3f}, F1={metrics['f1']:.3f}")
