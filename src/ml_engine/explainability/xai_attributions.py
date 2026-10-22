"""
Explainable AI (XAI) Attribution Engine: Mask Permutation & Feature Attributions
Author: Sandarbh Gupta (24BIT0506) - Subsystem 2
Paper Grounding: Papers 1 & 13 (Wang et al., IEEE OJ-COMS 2024 / Johari et al., 2025)
"""

from typing import List, Dict, Any, Callable
import numpy as np


class XaiExplainer:
    """
    XAI Explainer computing feature attributions via Mask Permutation.
    Measures anomaly score degradation when individual metric series are perturbed/masked.
    Generates structured XAI attributions conforming to Contract 2.
    """
    def __init__(self, n_permutations: int = 5):
        self.n_permutations = n_permutations

    def compute_attributions(
        self,
        X_sample: np.ndarray,
        feature_names: List[str],
        score_func: Callable[[np.ndarray], float]
    ) -> List[Dict[str, Any]]:
        """
        Computes SHAP-like attribution values for each KPI feature.
        """
        base_score = score_func(X_sample)
        attributions = []
        
        n_features = len(feature_names)
        for i, name in enumerate(feature_names):
            impacts = []
            for _ in range(self.n_permutations):
                # Create perturbed copy with zeroed / shuffled feature
                X_perturbed = X_sample.copy()
                if len(X_perturbed.shape) == 1:
                    X_perturbed[i] = 0.0
                else:
                    X_perturbed[:, i] = 0.0
                    
                perturbed_score = score_func(X_perturbed)
                # Feature importance = drop in anomaly score when feature is removed
                impact = max(0.0, base_score - perturbed_score)
                impacts.append(impact)
                
            mean_impact = float(np.mean(impacts))
            attributions.append({"kpi": name, "shap_value": round(mean_impact, 4)})
            
        # Normalize sum of values if positive
        total = sum(item["shap_value"] for item in attributions)
        if total > 0:
            for item in attributions:
                item["shap_value"] = round(item["shap_value"] / total, 3)
                
        # Sort descending by shap_value
        attributions.sort(key=lambda x: x["shap_value"], reverse=True)
        return attributions
