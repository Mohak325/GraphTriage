"""
Pretrained ML Model Loader & Persistence Engine
Subsystem 2: ML Detection, Graph Dependency & RCA Engine
Author: Sandarbh Gupta (24BIT0506)

Loads pre-trained model artifacts exported from Google Colab or local training runs:
- rca_classifier.joblib: Top-1 >= 82% Multi-Modal Service Localizer
- fault_classifier.joblib: 11-class Fault Type Classifier
- mnsuad_pipeline.joblib: Teacher-Student Contamination-Resilient Detector
- telegan_core.joblib: Dual-Autoencoder GAN with Gap Penalty
- trans_gnn.joblib: 2-Layer GCN for Invocation Graph Localization
- metadata.json: Service & Fault vocabs, feature names, benchmark scorecard
"""

import os
import json
import joblib
from typing import Dict, Any, Optional
import numpy as np
from structlog import get_logger

logger = get_logger()

DEFAULT_MODELS_DIR = os.path.join(os.path.dirname(__file__), "saved_models")


class PretrainedRcaModelRegistry:
    """Registry to load, cache, and serve all exported pre-trained RCA models."""

    def __init__(self, models_dir: str = DEFAULT_MODELS_DIR):
        self.models_dir = os.path.abspath(models_dir)
        self.rca_classifier = None
        self.fault_classifier = None
        self.mnsuad_pipeline = None
        self.telegan_core = None
        self.trans_gnn = None
        self.metadata: Dict[str, Any] = {}
        self.is_loaded = False

    def is_available(self) -> bool:
        """Returns True if the saved_models folder contains essential exported models."""
        required_files = ["rca_classifier.joblib", "metadata.json"]
        return all(os.path.exists(os.path.join(self.models_dir, f)) for f in required_files)

    def load(self) -> bool:
        """Loads all exported model artifacts from the saved_models directory."""
        if not self.is_available():
            logger.warning("Saved model directory does not contain complete artifacts", path=self.models_dir)
            return False

        try:
            logger.info("Loading pre-trained ML models from disk...", path=self.models_dir)
            
            # Load metadata
            meta_path = os.path.join(self.models_dir, "metadata.json")
            with open(meta_path, "r", encoding="utf-8") as f:
                self.metadata = json.load(f)

            # Load Classifiers
            rca_path = os.path.join(self.models_dir, "rca_classifier.joblib")
            if os.path.exists(rca_path):
                self.rca_classifier = joblib.load(rca_path)

            fault_path = os.path.join(self.models_dir, "fault_classifier.joblib")
            if os.path.exists(fault_path):
                self.fault_classifier = joblib.load(fault_path)

            # Load Anomaly Detectors
            mnsuad_path = os.path.join(self.models_dir, "mnsuad_pipeline.joblib")
            if os.path.exists(mnsuad_path):
                self.mnsuad_pipeline = joblib.load(mnsuad_path)

            telegan_path = os.path.join(self.models_dir, "telegan_core.joblib")
            if os.path.exists(telegan_path):
                self.telegan_core = joblib.load(telegan_path)

            trans_gnn_path = os.path.join(self.models_dir, "trans_gnn.joblib")
            if os.path.exists(trans_gnn_path):
                self.trans_gnn = joblib.load(trans_gnn_path)

            self.is_loaded = True
            logger.info("Successfully loaded all pre-trained RCA models!", 
                        services=len(self.metadata.get("service_vocab", [])),
                        faults=len(self.metadata.get("fault_vocab", [])))
            return True

        except Exception as exc:
            logger.error("Failed to load pre-trained models from disk", error=str(exc))
            self.is_loaded = False
            return False

    def predict_root_cause(self, feature_vector: np.ndarray) -> Dict[str, Any]:
        """Predicts the root-cause service with ranked probabilities."""
        if not self.is_loaded or self.rca_classifier is None:
            raise RuntimeError("Pre-trained RCA model is not loaded.")
        
        vec = feature_vector.reshape(1, -1) if feature_vector.ndim == 1 else feature_vector
        probs = self.rca_classifier.predict_proba(vec)[0]
        vocab = self.metadata.get("service_vocab", [])
        
        ranked_indices = np.argsort(probs)[::-1]
        ranked_candidates = [
            {"service": vocab[i] if i < len(vocab) else f"service_{i}", "confidence": float(probs[i])}
            for i in ranked_indices
        ]
        return {
            "top_1_service": ranked_candidates[0]["service"],
            "top_1_confidence": ranked_candidates[0]["confidence"],
            "ranked_candidates": ranked_candidates
        }

    def predict_fault_type(self, feature_vector: np.ndarray) -> Dict[str, Any]:
        """Predicts fault type classification."""
        if not self.is_loaded or self.fault_classifier is None:
            raise RuntimeError("Pre-trained Fault model is not loaded.")
        
        vec = feature_vector.reshape(1, -1) if feature_vector.ndim == 1 else feature_vector
        probs = self.fault_classifier.predict_proba(vec)[0]
        vocab = self.metadata.get("fault_vocab", [])
        
        top_idx = int(np.argmax(probs))
        fault_name = vocab[top_idx] if top_idx < len(vocab) else f"fault_{top_idx}"
        return {
            "fault_type": fault_name,
            "confidence": float(probs[top_idx])
        }
