"""
PyTorch Deviation Network (DevNet) Student Engine
Author: Sandarbh Gupta (24BIT0506) - Subsystem 2
Paper Grounding: MNSUAD (Paper 1 - Johari et al., IEEE TMC 2025)
"""

import torch
import torch.nn as nn
import torch.optim as optim
import numpy as np
from typing import Optional, Tuple


class DevNetStudent(nn.Module):
    """
    Deviation Network (DevNet) student model built with PyTorch.
    Optimizes contrastive deviation loss:
    L(x, y) = (1 - y) * |dev(x)| + y * max(0, margin - dev(x))
    against a prior normal reference N(0, 1).
    """
    def __init__(
        self,
        input_dim: int,
        hidden_dim: int = 32,
        margin: float = 5.0,
        learning_rate: float = 0.01,
        n_epochs: int = 40
    ):
        super().__init__()
        self.input_dim = input_dim
        self.hidden_dim = hidden_dim
        self.margin = margin
        self.lr = learning_rate
        self.n_epochs = n_epochs
        
        self.net = nn.Sequential(
            nn.Linear(input_dim, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, 1)
        )
        
        self.mu_r = 0.0
        self.sigma_r = 1.0
        self.is_fitted = False

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.net(x).squeeze(-1)

    def fit(
        self,
        X_scaled: np.ndarray,
        pseudo_labels: np.ndarray,
        weights: Optional[np.ndarray] = None
    ) -> "DevNetStudent":
        """
        Trains DevNet using Adam optimizer on scaled features and teacher pseudo-labels.
        """
        if weights is None:
            weights = np.ones(len(X_scaled), dtype=np.float32)
            
        x_tensor = torch.tensor(X_scaled, dtype=torch.float32)
        y_tensor = torch.tensor(pseudo_labels, dtype=torch.float32)
        w_tensor = torch.tensor(weights, dtype=torch.float32)
        
        optimizer = optim.Adam(self.parameters(), lr=self.lr, weight_decay=1e-4)
        self.train()
        
        for epoch in range(self.n_epochs):
            optimizer.zero_grad()
            scores = self.forward(x_tensor)
            dev = (scores - self.mu_r) / self.sigma_r
            
            # DevNet contrastive loss
            loss_normal = (1.0 - y_tensor) * torch.abs(dev)
            loss_anomaly = y_tensor * torch.clamp(self.margin - dev, min=0.0)
            loss = torch.mean(w_tensor * (loss_normal + loss_anomaly))
            
            loss.backward()
            optimizer.step()
            
        self.is_fitted = True
        return self

    def predict_anomaly_scores(self, X_scaled: np.ndarray) -> np.ndarray:
        """
        Infers continuous anomaly score in [0, 1] via Sigmoid(deviation).
        """
        self.eval()
        with torch.no_grad():
            x_tensor = torch.tensor(X_scaled, dtype=torch.float32)
            scores = self.forward(x_tensor)
            dev = (scores - self.mu_r) / self.sigma_r
            prob = torch.sigmoid(dev / 2.0).numpy()
        return prob
