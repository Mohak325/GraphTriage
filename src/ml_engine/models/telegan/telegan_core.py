"""
TeleGAN-Core: Dual-Autoencoder GAN with Critic Reconstruction Gap Penalty
Author: Sandarbh Gupta (24BIT0506) - Subsystem 2
Paper Grounding: TeleGAN-Core (Paper 4 - Issa et al., IEEE Access 2026)
"""

import numpy as np
from typing import Dict, Any, Tuple


class TeleGANCore:
    """
    TeleGAN-Core implementation:
    - Generator Autoencoder G(x): Learns nominal temporal pattern reconstruction.
    - Critic Autoencoder C(x): Reconstructs the generator output G(x).
    - Reconstruction Gap Penalty: L_gap = ||x - G(x)|| - ||G(x) - C(G(x))||.
    Suppresses false alarms and eliminates alert fatigue on 5GC SBA metrics.
    """
    def __init__(
        self,
        n_features: int,
        latent_dim: int = 16,
        learning_rate: float = 0.005,
        n_epochs: int = 40
    ):
        self.n_features = n_features
        self.latent_dim = latent_dim
        self.lr = learning_rate
        self.n_epochs = n_epochs
        
        # Generator weights: Enc_G (n_features -> latent_dim), Dec_G (latent_dim -> n_features)
        np.random.seed(42)
        self.W_enc_g = np.random.randn(n_features, latent_dim) * 0.1
        self.b_enc_g = np.zeros(latent_dim)
        self.W_dec_g = np.random.randn(latent_dim, n_features) * 0.1
        self.b_dec_g = np.zeros(n_features)
        
        # Critic weights: Enc_C (n_features -> latent_dim), Dec_C (latent_dim -> n_features)
        self.W_enc_c = np.random.randn(n_features, latent_dim) * 0.1
        self.b_enc_c = np.zeros(latent_dim)
        self.W_dec_c = np.random.randn(latent_dim, n_features) * 0.1
        self.b_dec_c = np.zeros(n_features)
        
        self.is_fitted = False
        self.baseline_gap_mean = 0.0
        self.baseline_gap_std = 1.0

    def _forward_generator(self, X: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        z_g = np.tanh(np.dot(X, self.W_enc_g) + self.b_enc_g)
        x_recon_g = np.dot(z_g, self.W_dec_g) + self.b_dec_g
        return z_g, x_recon_g

    def _forward_critic(self, X: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        z_c = np.tanh(np.dot(X, self.W_enc_c) + self.b_enc_c)
        x_recon_c = np.dot(z_c, self.W_dec_c) + self.b_dec_c
        return z_c, x_recon_c

    def fit(self, X_train: np.ndarray) -> "TeleGANCore":
        """
        Fits Generator and Critic autoencoders jointly on training baseline.
        """
        N = len(X_train)
        for epoch in range(self.n_epochs):
            # 1. Forward G
            z_g, x_recon_g = self._forward_generator(X_train)
            err_g = x_recon_g - X_train  # (N, D)
            
            # 2. Forward C on G's output
            z_c, x_recon_c = self._forward_critic(x_recon_g)
            err_c = x_recon_c - x_recon_g  # (N, D)
            
            # Gradients for Critic
            grad_c_out = err_c / N
            grad_W_dec_c = np.dot(z_c.T, grad_c_out)
            grad_b_dec_c = np.mean(grad_c_out, axis=0)
            grad_z_c = np.dot(grad_c_out, self.W_dec_c.T) * (1 - z_c**2)
            grad_W_enc_c = np.dot(x_recon_g.T, grad_z_c)
            grad_b_enc_c = np.mean(grad_z_c, axis=0)
            
            # Gradients for Generator
            grad_g_out = (err_g - 0.2 * err_c) / N
            grad_W_dec_g = np.dot(z_g.T, grad_g_out)
            grad_b_dec_g = np.mean(grad_g_out, axis=0)
            grad_z_g = np.dot(grad_g_out, self.W_dec_g.T) * (1 - z_g**2)
            grad_W_enc_g = np.dot(X_train.T, grad_z_g)
            grad_b_enc_g = np.mean(grad_z_g, axis=0)
            
            # SGD update
            self.W_dec_c -= self.lr * grad_W_dec_c
            self.b_dec_c -= self.lr * grad_b_dec_c
            self.W_enc_c -= self.lr * grad_W_enc_c
            self.b_enc_c -= self.lr * grad_b_enc_c
            
            self.W_dec_g -= self.lr * grad_W_dec_g
            self.b_dec_g -= self.lr * grad_b_dec_g
            self.W_enc_g -= self.lr * grad_W_enc_g
            self.b_enc_g -= self.lr * grad_b_enc_g
            
        # Calibrate baseline gap distribution
        _, x_recon_g = self._forward_generator(X_train)
        _, x_recon_c = self._forward_critic(x_recon_g)
        
        l_g = np.linalg.norm(X_train - x_recon_g, axis=1)
        l_c = np.linalg.norm(x_recon_g - x_recon_c, axis=1)
        gaps = np.abs(l_g - l_c)
        
        self.baseline_gap_mean = float(np.mean(gaps))
        self.baseline_gap_std = float(np.std(gaps)) + 1e-6
        self.is_fitted = True
        return self

    def compute_anomaly_scores(self, X: np.ndarray) -> np.ndarray:
        """
        Computes normalized anomaly score based on the critic reconstruction gap penalty.
        """
        if not self.is_fitted:
            raise RuntimeError("TeleGANCore must be fitted before computing anomaly scores.")
        _, x_recon_g = self._forward_generator(X)
        _, x_recon_c = self._forward_critic(x_recon_g)
        
        l_g = np.linalg.norm(X - x_recon_g, axis=1)
        l_c = np.linalg.norm(x_recon_g - x_recon_c, axis=1)
        gaps = np.abs(l_g - l_c)
        
        # Z-score normalization
        z_scores = (gaps - self.baseline_gap_mean) / self.baseline_gap_std
        # Sigmoid scaling
        scores = 1.0 / (1.0 + np.exp(-z_scores))
        return scores
