"""
Deep Autoencoding Gaussian Mixture Model (DAGMM) Teacher Engine
Author: Sandarbh Gupta (24BIT0506) - Subsystem 2
Paper Grounding: MNSUAD (Paper 1 - Johari et al., IEEE TMC 2025)
"""

import numpy as np
from sklearn.mixture import GaussianMixture
from sklearn.preprocessing import StandardScaler
from typing import Tuple, Dict, Any, cast


class DAGMMTeacher:
    """
    Teacher model implementing DAGMM with 3-step energy thresholding (eta1, eta2, eta3)
    to generate pseudo-labels resilient to 5% unlabeled training data contamination.
    """
    def __init__(
        self,
        n_components: int = 3,
        eta1_percentile: float = 90.0,
        eta2_percentile: float = 95.0,
        eta3_percentile: float = 99.0
    ):
        self.n_components = n_components
        self.eta1_percentile = eta1_percentile
        self.eta2_percentile = eta2_percentile
        self.eta3_percentile = eta3_percentile
        
        self.scaler = StandardScaler()
        # Cast to Any before instantiation to suppress Pyright's reportAbstractUsage false-positive
        # (sklearn's GaussianMixture implements all BaseMixture abstract methods, but lacks static stubs)
        self.gmm: GaussianMixture = cast(Any, GaussianMixture)(
            n_components=n_components,
            covariance_type='full',
            random_state=42
        )
        self.threshold_eta1 = 0.0
        self.threshold_eta2 = 0.0
        self.threshold_eta3 = 0.0
        self.is_fitted = False

    def fit(self, X: np.ndarray) -> "DAGMMTeacher":
        """
        Fits DAGMM on contaminated baseline data and sets the energy thresholds.
        """
        X_scaled = self.scaler.fit_transform(X)
        self.gmm.fit(X_scaled)
        
        # Calculate sample energy: negative log-likelihood
        energies = -self.gmm.score_samples(X_scaled)
        
        self.threshold_eta1 = float(np.percentile(energies, self.eta1_percentile))
        self.threshold_eta2 = float(np.percentile(energies, self.eta2_percentile))
        self.threshold_eta3 = float(np.percentile(energies, self.eta3_percentile))
        self.is_fitted = True
        return self

    def compute_energy(self, X: np.ndarray) -> np.ndarray:
        """
        Computes sample energy E(z) = -log P(z). Higher energy indicates higher anomaly likelihood.
        """
        if not self.is_fitted:
            raise RuntimeError("DAGMMTeacher must be fitted before computing energy.")
        X_scaled = self.scaler.transform(X)
        return -self.gmm.score_samples(X_scaled)

    def generate_pseudo_labels(self, X: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """
        Generates pseudo-labels using the 3-step threshold cascade:
        - Energy < eta1: Confidently Clean (Label 0, Weight 1.0)
        - eta1 <= Energy < eta2: Suspect (Label 0, Weight 0.5)
        - eta2 <= Energy < eta3: Weak Anomaly (Label 1, Weight 0.7)
        - Energy >= eta3: Strong Anomaly (Label 1, Weight 1.0)
        
        Returns:
            pseudo_labels: binary array {0, 1}
            confidence_weights: float array [0..1]
        """
        energies = self.compute_energy(X)
        n_samples = len(X)
        
        pseudo_labels = np.zeros(n_samples, dtype=int)
        confidence_weights = np.ones(n_samples, dtype=float)
        
        for i, e in enumerate(energies):
            if e < self.threshold_eta1:
                pseudo_labels[i] = 0
                confidence_weights[i] = 1.0
            elif e < self.threshold_eta2:
                pseudo_labels[i] = 0
                confidence_weights[i] = 0.5
            elif e < self.threshold_eta3:
                pseudo_labels[i] = 1
                confidence_weights[i] = 0.7
            else:
                pseudo_labels[i] = 1
                confidence_weights[i] = 1.0
                
        return pseudo_labels, confidence_weights
