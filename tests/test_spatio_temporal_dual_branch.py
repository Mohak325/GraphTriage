"""
Test: Spatio-Temporal Dual-Branch CNN-Transformer & Dynamic KPI Gating
Author: Sandarbh Gupta (24BIT0506) - Subsystem 2
Paper Grounding: Paper 15 (Frontiers in AI 2025 & MDPI Appl. Sci. 2026)
"""

import pytest
import numpy as np
from src.ml_engine.models.spatio_temporal.dual_branch import DualBranchCNNTransformer


def test_dual_branch_gating_and_scoring():
    seq_len = 12
    n_features = 4
    batch_size = 10
    
    model = DualBranchCNNTransformer(seq_len=seq_len, n_features=n_features, hidden_dim=16)
    
    # 1. Clean nominal sequences
    X_clean = np.random.randn(batch_size, seq_len, n_features) * 0.5 + 20.0
    scores_clean, gates_clean, _ = model.forward(X_clean)
    
    # Assert output shapes
    assert len(scores_clean) == batch_size
    assert len(gates_clean) == batch_size
    
    # Assert Paper 15 constraint: Dynamic KPI gating strictly clamped to [0.40, 0.60]
    assert np.all(gates_clean >= 0.40), f"Gate below 0.40: {gates_clean}"
    assert np.all(gates_clean <= 0.60), f"Gate above 0.60: {gates_clean}"
    
    # Assert scores in [0, 1]
    assert np.all(scores_clean >= 0.0) and np.all(scores_clean <= 1.0)
    
    # 2. Sequence with sharp transient spike (testing CNN branch response)
    X_spike = X_clean.copy()
    X_spike[:, -1, 0] += 50.0  # abrupt spike at last time step
    scores_spike, gates_spike, _ = model.forward(X_spike)
    
    assert np.all(gates_spike >= 0.40) and np.all(gates_spike <= 0.60)
    print(f"\n[PASSED] Dual-Branch CNN-Transformer: gates={gates_spike[:3]}, scores={scores_spike[:3]}")
