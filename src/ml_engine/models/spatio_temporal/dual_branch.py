"""
Dual-Branch CNN-Transformer with Dynamic KPI Gating (Capped at 60%)
Author: Sandarbh Gupta (24BIT0506) - Subsystem 2
Paper Grounding: Paper 15 (Frontiers in AI 2025 & MDPI Appl. Sci. 2026)
"""

import numpy as np
from typing import Tuple, Dict, Any


class DualBranchCNNTransformer:
    """
    Dual-Branch Spatio-Temporal model:
    - Branch 1: 1D Temporal CNN capturing short-term localized spikes.
    - Branch 2: Transformer self-attention capturing multi-step onset-to-recovery dynamics.
    - Dynamic KPI Gating Layer: g in [0.40, 0.60] enforcing that neither branch dominates.
    """
    def __init__(
        self,
        seq_len: int = 12,
        n_features: int = 4,
        hidden_dim: int = 16
    ):
        self.seq_len = seq_len
        self.n_features = n_features
        self.hidden_dim = hidden_dim
        
        np.random.seed(42)
        # 1D-CNN branch weights (kernel size 3)
        self.W_cnn = np.random.randn(3 * n_features, hidden_dim) * 0.1
        self.b_cnn = np.zeros(hidden_dim)
        
        # Transformer branch query/key/value weights
        self.W_q = np.random.randn(n_features, hidden_dim) * 0.1
        self.W_k = np.random.randn(n_features, hidden_dim) * 0.1
        self.W_v = np.random.randn(n_features, hidden_dim) * 0.1
        
        # Dynamic gating layer: [hidden_dim * 2] -> 1
        self.W_gate = np.random.randn(2 * hidden_dim, 1) * 0.1
        self.b_gate = np.zeros(1)
        
        # Classification head: hidden_dim -> 1
        self.W_head = np.random.randn(hidden_dim, 1) * 0.1
        self.b_head = np.zeros(1)

    def _cnn_branch(self, X: np.ndarray) -> np.ndarray:
        """
        1D temporal convolution over windows of length 3.
        X shape: (N, seq_len, n_features)
        Returns: (N, hidden_dim)
        """
        N = X.shape[0]
        # Flatten last 3 steps as receptive field
        window = X[:, -3:, :].reshape(N, -1)
        h_cnn = np.maximum(0, np.dot(window, self.W_cnn) + self.b_cnn)
        return h_cnn

    def _transformer_branch(self, X: np.ndarray) -> np.ndarray:
        """
        Self-attention pooling across sequence length.
        Returns: (N, hidden_dim)
        """
        # Linear projections
        Q = np.dot(X, self.W_q)  # (N, seq_len, hidden_dim)
        K = np.dot(X, self.W_k)
        V = np.dot(X, self.W_v)
        
        # Scaled dot-product attention
        scores = np.einsum('nij,nkj->nik', Q, K) / np.sqrt(self.hidden_dim)
        # Softmax over last dimension
        exp_s = np.exp(scores - np.max(scores, axis=-1, keepdims=True))
        attn_weights = exp_s / np.sum(exp_s, axis=-1, keepdims=True)
        
        # Attention output pooled across time
        context = np.einsum('nik,nkj->nij', attn_weights, V)
        h_trans = np.mean(context, axis=1)  # (N, hidden_dim)
        return h_trans

    def forward(self, X: np.ndarray) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """
        Executes dual branches, dynamic gating clamped to [0.4, 0.6], and outputs anomaly scores.
        """
        h_cnn = self._cnn_branch(X)
        h_trans = self._transformer_branch(X)
        
        # Concatenate features for gating
        h_cat = np.concatenate([h_cnn, h_trans], axis=1)
        raw_gate = 1.0 / (1.0 + np.exp(-(np.dot(h_cat, self.W_gate) + self.b_gate)))
        
        # Enforce Paper 15 constraint: Dynamic KPI gating capped at 60%
        g = np.clip(raw_gate, 0.40, 0.60)
        
        # Gated feature fusion
        h_fused = g * h_cnn + (1.0 - g) * h_trans
        
        # Score prediction
        logits = np.dot(h_fused, self.W_head) + self.b_head
        scores = 1.0 / (1.0 + np.exp(-logits)).squeeze()
        
        return scores, g.squeeze(), h_fused
