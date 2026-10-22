"""Dual-branch spatio-temporal CNN-Transformer model."""
from src.ml_engine.models.spatio_temporal.dual_branch import DualBranchCNNTransformer

SpatioTemporalDualBranch = DualBranchCNNTransformer

__all__ = ["DualBranchCNNTransformer", "SpatioTemporalDualBranch"]
