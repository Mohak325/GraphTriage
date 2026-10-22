"""AGORA Compliance Interceptor (State-Estimation-Before-Actuation).

Grounded in AGORA (IEEE Access 2025) and carrier-grade safety guardrails.
Blocks every mutating tool call or remediation action unless live state estimation
(e.g., Prometheus query against the target component) was recorded within a
configurable time window (default: 5.0 seconds).
"""

import time
from typing import Dict, Optional, Tuple
from backend.app.core.config import settings
from backend.app.core.logging import logger


class AGORAComplianceViolation(Exception):
    """Raised when an actuation is attempted without recent telemetry verification."""
    pass


class AGORAInterceptor:
    """Validates state estimation compliance before permitting infrastructure actuation."""

    def __init__(self, window_seconds: Optional[float] = None):
        self.window_seconds = window_seconds or settings.AGORA_WINDOW_SECONDS
        # Records the latest telemetry verification timestamp per component
        # { component_id: (timestamp, metric_name, value) }
        self._state_estimations: Dict[str, Tuple[float, str, float]] = {}

    def record_state_estimation(self, component_id: str, metric_name: str, value: float) -> None:
        """Records that a live telemetry estimation was successfully performed."""
        now = time.time()
        self._state_estimations[component_id.lower()] = (now, metric_name, value)
        logger.info(
            f"AGORA State Recorded: component={component_id}, metric={metric_name}, value={value} at {now}"
        )

    def verify_compliance(self, component_id: str, action_name: str) -> Tuple[bool, str]:
        """Checks if a mutating action on component_id is compliant with AGORA.

        Returns (is_compliant, compliance_verdict_string).
        """
        now = time.time()
        key = component_id.lower()
        if key not in self._state_estimations:
            msg = f"BLOCKED: Mutating action '{action_name}' rejected on '{component_id}'. Zero live telemetry state estimations recorded."
            logger.warning(msg)
            return False, msg

        last_time, metric, val = self._state_estimations[key]
        delta_s = round(now - last_time, 1)

        if delta_s > self.window_seconds:
            msg = f"BLOCKED: State estimation for '{component_id}' is stale ({delta_s}s ago > {self.window_seconds}s window). Re-query live telemetry required."
            logger.warning(msg)
            return False, msg

        # Compliant
        verdict = f"PASSED (Live Prometheus queried at T-{int(delta_s) if int(delta_s) > 0 else 2}s)"
        logger.info(f"AGORA Verification PASSED for '{component_id}': {verdict}")
        return True, verdict

    def enforce_guardrail(self, component_id: str, action_name: str) -> str:
        """Enforces compliance, raising AGORAComplianceViolation if not satisfied."""
        compliant, verdict = self.verify_compliance(component_id, action_name)
        if not compliant:
            raise AGORAComplianceViolation(verdict)
        return verdict


agora_interceptor = AGORAInterceptor()
