"""
Service-Oriented Metric Preprocessing (SOMP) Engine.
Grounding: Paper 4 (TeleGAN-Core, Issa et al., IEEE Access 2026).
- Guaranteed Counter Reset Safety: transforms cumulative counters into delta intervals (x'_t = x_t - x_{t-1}).
- Eliminates negative spikes caused by container restarts, pod crashes, or 32/64-bit integer overflow.
- Gauge Aggregation: robust mean / median temporal pooling.
"""

from typing import Tuple, List, Optional, Dict
import numpy as np


class SOMPNormalizer:
    """
    Stateful Service-Oriented Metric Preprocessing Normalizer.
    Tracks previous counter values per (source_component, metric_name).
    """

    def __init__(self, default_counter_max: int = 2**32):
        self.default_counter_max = default_counter_max
        # Memory map: (component, metric) -> last_observed_raw_value
        self._counter_state: Dict[Tuple[str, str], float] = {}

    def compute_counter_delta(
        self,
        component_id: str,
        metric_name: str,
        current_value: float,
        counter_max: Optional[int] = None
    ) -> Tuple[float, bool]:
        """
        Processes a monotonic counter reading and computes interval delta x'_t.
        Returns:
            (delta_value, reset_flag)
        
        Guarantees:
            delta_value >= 0.0 (Zero negative spikes).
        """
        key = (component_id, metric_name)
        c_max = counter_max or self.default_counter_max

        if key not in self._counter_state:
            # First observation: delta is 0 or initial value
            self._counter_state[key] = current_value
            return 0.0, False

        prev_val = self._counter_state[key]
        self._counter_state[key] = current_value

        if current_value >= prev_val:
            # Normal monotonic progression
            delta = current_value - prev_val
            return float(delta), False
        else:
            # Counter wrap-around or pod reboot/reset
            # Check if this looks like a standard 32-bit or 64-bit wrap-around
            if prev_val > (c_max * 0.9):
                # Modular integer wrap-around recovery
                delta = float((c_max - prev_val) + current_value)
            else:
                # Fresh container/pod reset: assume restart from zero
                delta = float(current_value)

            # Safety enforcement: ensure no negative value escapes
            safe_delta = max(0.0, delta)
            return safe_delta, True

    def reset_state(self, component_id: Optional[str] = None):
        """Clears state for testing or container lifecycle termination."""
        if component_id is None:
            self._counter_state.clear()
        else:
            keys_to_del = [k for k in self._counter_state if k[0] == component_id]
            for k in keys_to_del:
                del self._counter_state[k]

    @staticmethod
    def aggregate_gauge(
        values: List[float],
        method: str = "mean"
    ) -> float:
        """
        Aggregates gauge readings across a temporal interval.
        Supported methods: 'mean', 'median', 'p95', 'max'.
        """
        arr = np.asarray(values, dtype=np.float64)
        if len(arr) == 0:
            return 0.0

        if method == "median":
            return float(np.median(arr))
        elif method == "p95":
            return float(np.percentile(arr, 95))
        elif method == "max":
            return float(np.max(arr))
        else:
            return float(np.mean(arr))
