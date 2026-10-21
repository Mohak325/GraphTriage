"""
Layer 1: Shannon Entropy Filter.
Grounding: IEEE ISCC 2025; TeleGAN-Core (Paper 4).
Filters out static, constant, or uninformative KPIs (entropy H < tau1).
Eliminates ~87.93% of invariant PM counters on 5G Core SBA.
"""

from typing import Tuple, List, Union
import numpy as np
from scipy.stats import entropy


def compute_shannon_entropy(series: Union[List[float], np.ndarray], bins: int = 50) -> float:
    """
    Computes Shannon entropy H(X) = -sum p(x) * log2(p(x)) on a continuous or discrete KPI series.
    A constant series returns H = 0.0.
    """
    arr = np.asarray(series, dtype=np.float64)
    if len(arr) == 0:
        return 0.0

    # If completely constant or near-constant, entropy is 0
    std_dev = np.std(arr)
    if np.isnan(std_dev) or std_dev < 1e-9:
        return 0.0

    # Build normalized probability distribution
    counts, _ = np.histogram(arr, bins=bins, density=True)
    probs = counts / np.sum(counts) if np.sum(counts) > 0 else np.zeros_like(counts)
    probs = probs[probs > 0]
    if len(probs) <= 1:
        return 0.0

    # Compute base-2 entropy
    return float(entropy(probs, base=2))


def filter_kpi_by_entropy(
    series: Union[List[float], np.ndarray],
    tau1: float = 0.05,
    bins: int = 50
) -> Tuple[bool, float]:
    """
    Layer 1 Filtering Decision.
    Returns (keep_kpi, entropy_value).
    If H >= tau1, the KPI contains dynamic informational entropy and is KEPT.
    If H < tau1, the KPI is considered static/invariant and is ELIMINATED.
    """
    h_val = compute_shannon_entropy(series, bins=bins)
    keep = h_val >= tau1
    return keep, h_val
