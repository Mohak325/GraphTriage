"""
Layer 2: Stochastic Pattern Noise Decomposition.
Grounding: IEEE ISCC 2025; TeleGAN-Core (Paper 4).
Decomposes non-stationary telemetry into Trend, Seasonal, and Residual components.
Filters out volatile white noise / meaningless jitter while preserving legitimate anomaly spikes.
"""

from typing import Tuple, Union, List
import numpy as np
import pandas as pd
from statsmodels.tsa.seasonal import STL


def decompose_and_filter_noise(
    series: Union[List[float], np.ndarray, pd.Series],
    period: int = 24,
    noise_ratio_threshold: float = 0.95,
    min_length: int = 48
) -> Tuple[bool, float, dict]:
    """
    Evaluates whether a time-series is dominated by pure stochastic noise with no structural signal.
    Returns:
        (keep_kpi, noise_ratio, components_dict)
    
    If noise_ratio >= noise_ratio_threshold (e.g. > 95% variance is pure unstructured white noise),
    the KPI can be filtered out. Otherwise it contains valid structural signal or trend/seasonality.
    """
    arr = np.asarray(series, dtype=np.float64)
    total_std = float(np.std(arr))

    # If length is insufficient for STL or variation is near zero, use variance-ratio heuristic
    if len(arr) < min_length or total_std < 1e-9:
        # Check simple first-difference variance vs raw variance
        diff_var = float(np.var(np.diff(arr))) if len(arr) > 1 else 0.0
        raw_var = float(np.var(arr)) if len(arr) > 0 else 0.0
        ratio = (diff_var / (2.0 * raw_var + 1e-9)) if raw_var > 0 else 0.0
        keep = ratio < noise_ratio_threshold
        return keep, ratio, {"trend": arr, "seasonal": np.zeros_like(arr), "resid": np.zeros_like(arr)}

    try:
        # Fit Loess STL decomposition
        stl = STL(arr, period=period, robust=True)
        res = stl.fit()
        resid_std = float(np.std(res.resid))
        noise_ratio = resid_std / (total_std + 1e-9)

        # Retain if it has structural signal (noise_ratio < threshold)
        keep = noise_ratio < noise_ratio_threshold
        return keep, noise_ratio, {
            "trend": res.trend,
            "seasonal": res.seasonal,
            "resid": res.resid
        }
    except Exception:
        # Graceful fallback: retain KPI if decomposition encounters singularity
        return True, 0.5, {}
