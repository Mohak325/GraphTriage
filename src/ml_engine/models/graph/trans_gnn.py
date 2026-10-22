"""
transGNN: Graph Convolutional Network for Service Failure Localization
Author: Sandarbh Gupta (24BIT0506) - Subsystem 2
Paper Grounding: DTFL (Paper 2 - Guo et al., IEEE TCC 2023)
"""

import numpy as np
from typing import List, Dict, Any, Tuple


class TransGNNModel:
    """
    transGNN model implementing:
    - Node representation fusing metric statistics and log text embeddings.
    - 2-layer Graph Convolution (GCN) over normalized invocation graph A_norm.
    - Node-level anomaly scoring for Service Function Chains (SFC) and microservices.
    """
    def __init__(
        self,
        in_dim: int = 8,
        hidden_dim: int = 16,
        learning_rate: float = 0.01,
        n_epochs: int = 60
    ):
        self.in_dim = in_dim
        self.hidden_dim = hidden_dim
        self.lr = learning_rate
        self.n_epochs = n_epochs
        
        # Layer 1 weights: (in_dim -> hidden_dim)
        np.random.seed(42)
        self.W0 = np.random.randn(in_dim, hidden_dim) * np.sqrt(2.0 / in_dim)
        self.b0 = np.zeros(hidden_dim)
        
        # Layer 2 weights: (hidden_dim -> 1)
        self.W1 = np.random.randn(hidden_dim, 1) * np.sqrt(2.0 / hidden_dim)
        self.b1 = np.zeros(1)
        self.is_fitted = False

    def forward(self, X: np.ndarray, A_norm: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """
        GCN Layer 1: H1 = ReLU(A_norm * X * W0 + b0)
        GCN Layer 2: Out = Sigmoid(A_norm * H1 * W1 + b1)
        """
        # Layer 1
        AX = np.dot(A_norm, X)
        H1 = np.maximum(0, np.dot(AX, self.W0) + self.b0)
        
        # Layer 2
        AH1 = np.dot(A_norm, H1)
        logits = np.dot(AH1, self.W1) + self.b1
        scores = 1.0 / (1.0 + np.exp(-logits)).squeeze()
        return H1, scores

    def fit(self, X_train: np.ndarray, A_norm: np.ndarray, y_train: np.ndarray) -> "TransGNNModel":
        """
        Trains GCN using Binary Cross-Entropy loss over node anomaly ground truth.
        """
        N = len(y_train)
        for epoch in range(self.n_epochs):
            H1, scores = self.forward(X_train, A_norm)
            
            # Loss gradient: dL/dlogits = (scores - y) / N
            grad_logits = ((scores - y_train) / N)[:, np.newaxis]
            
            AH1 = np.dot(A_norm, H1)
            grad_W1 = np.dot(AH1.T, grad_logits)
            grad_b1 = np.sum(grad_logits, axis=0)
            
            grad_AH1 = np.dot(grad_logits, self.W1.T)
            grad_H1 = np.dot(A_norm.T, grad_AH1)
            grad_H1[H1 <= 0] = 0  # ReLU derivative
            
            AX = np.dot(A_norm, X_train)
            grad_W0 = np.dot(AX.T, grad_H1)
            grad_b0 = np.sum(grad_H1, axis=0)
            
            # Gradient descent
            self.W1 -= self.lr * np.clip(grad_W1, -2.0, 2.0)
            self.b1 -= self.lr * np.clip(grad_b1, -2.0, 2.0)
            self.W0 -= self.lr * np.clip(grad_W0, -2.0, 2.0)
            self.b0 -= self.lr * np.clip(grad_b0, -2.0, 2.0)
            
        self.is_fitted = True
        return self

    def predict_node_anomalies(self, X: np.ndarray, A_norm: np.ndarray) -> np.ndarray:
        """
        Infers continuous anomaly probability for each service node.
        """
        _, scores = self.forward(X, A_norm)
        return scores
