"""
MNSUAD Unified Pipeline Trainer & Evaluator
Author: Sandarbh Gupta (24BIT0506) - Subsystem 2
Paper Grounding: MNSUAD (Paper 1 - Johari et al., IEEE TMC 2025)
"""

import numpy as np
from typing import Dict, Any, Tuple
from sklearn.metrics import f1_score, roc_auc_score, precision_score, recall_score
from .dagmm import DAGMMTeacher
from .transformer_devnet import DevNetStudent


class MNSUADPipeline:
    """
    End-to-End MNSUAD Framework:
    1. Fits DAGMM Teacher on contaminated historical telemetry.
    2. Filters out up to 5% contamination via 3 energy thresholds (eta1, eta2, eta3).
    3. Produces pseudo-labels and confidence weights.
    4. Trains PyTorch DevNet Student on pseudo-labeled scaled representations.
    5. Evaluates and scores unseen online incidents.
    """
    def __init__(
        self,
        input_dim: int,
        hidden_dim: int = 32,
        n_gmm_components: int = 3
    ):
        self.input_dim = input_dim
        self.teacher = DAGMMTeacher(n_components=n_gmm_components)
        self.student = DevNetStudent(input_dim=input_dim, hidden_dim=hidden_dim)
        self.is_trained = False

    def train(self, X_contaminated_train: np.ndarray) -> Dict[str, Any]:
        """
        Trains the full MNSUAD pipeline on contaminated training data.
        """
        # Step 1: Fit Teacher
        self.teacher.fit(X_contaminated_train)
        
        # Step 2: Generate pseudo labels
        pseudo_labels, weights = self.teacher.generate_pseudo_labels(X_contaminated_train)
        
        # Step 3: Fit Student on scaled features
        X_scaled = self.teacher.scaler.transform(X_contaminated_train)
        self.student.fit(X_scaled, pseudo_labels, weights)
        self.is_trained = True
        
        pseudo_anomaly_ratio = float(np.mean(pseudo_labels))
        return {
            "status": "TRAINED",
            "pseudo_anomaly_ratio": pseudo_anomaly_ratio,
            "teacher_thresholds": {
                "eta1": self.teacher.threshold_eta1,
                "eta2": self.teacher.threshold_eta2,
                "eta3": self.teacher.threshold_eta3,
            }
        }

    def predict_scores(self, X_test: np.ndarray) -> np.ndarray:
        """
        Infers continuous anomaly scores in [0, 1] fusing Teacher energy and Student DevNet.
        """
        if not self.is_trained:
            raise RuntimeError("Pipeline must be trained before inference.")
        X_scaled = self.teacher.scaler.transform(X_test)
        student_scores = self.student.predict_anomaly_scores(X_scaled)
        
        energies = self.teacher.compute_energy(X_test)
        denom = (self.teacher.threshold_eta3 - self.teacher.threshold_eta1) + 1e-6
        energy_norm = (energies - self.teacher.threshold_eta1) / denom
        teacher_prob = 1.0 / (1.0 + np.exp(-energy_norm))
        
        # Weighted ensemble according to MNSUAD
        return 0.5 * teacher_prob + 0.5 * student_scores

    def evaluate(self, X_test: np.ndarray, y_true: np.ndarray, threshold: float = 0.5) -> Dict[str, float]:
        """
        Computes F1-score, Precision, Recall, and ROC-AUC.
        """
        scores = self.predict_scores(X_test)
        preds = (scores >= threshold).astype(int)
        
        return {
            "f1": float(f1_score(y_true, preds, zero_division=0)),
            "precision": float(precision_score(y_true, preds, zero_division=0)),
            "recall": float(recall_score(y_true, preds, zero_division=0)),
            "roc_auc": float(roc_auc_score(y_true, scores)) if len(np.unique(y_true)) > 1 else 1.0
        }
