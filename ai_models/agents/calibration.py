from typing import Dict

from ai_models.models import RCAOutput

class ConfidenceCalibrator:
    def __init__(
        self,
        base_weight: float = 0.5,
        evidence_weight: float = 0.3,
        counterfactual_weight: float = 0.2
    ):
        self.base_weight = base_weight
        self.evidence_weight = evidence_weight
        self.counterfactual_weight = counterfactual_weight

    def calibrate(self, rca_output: RCAOutput, fault_scores: Dict[str, float] | None = None) -> float:
        evidence_score = 0.0
        if rca_output.evidence_chain:
            evidence_score = min(1.0, len(rca_output.evidence_chain) / 5.0)
            
        if fault_scores and rca_output.root_cause_node in fault_scores:
            evidence_score = (evidence_score + fault_scores[rca_output.root_cause_node]) / 2.0

        counterfactual_score = 0.0
        if rca_output.counterfactual_results:
            passed = sum(1 for cf in rca_output.counterfactual_results if cf.passed)
            total = len(rca_output.counterfactual_results)
            counterfactual_score = passed / total if total > 0 else 0.0

        calibrated = (
            rca_output.confidence * self.base_weight +
            evidence_score * self.evidence_weight +
            counterfactual_score * self.counterfactual_weight
        )
        
        return min(1.0, max(0.0, calibrated))
