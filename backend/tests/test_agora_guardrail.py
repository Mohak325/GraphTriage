"""Tests for AGORA Compliance Interceptor (State-Estimation-Before-Actuation)."""

import time
import pytest
from backend.app.services.agora_interceptor import AGORAInterceptor, AGORAComplianceViolation


def test_agora_blocks_when_zero_estimations():
    agora = AGORAInterceptor(window_seconds=5.0)
    compliant, verdict = agora.verify_compliance("amf-01", "scale_out")
    assert not compliant
    assert "BLOCKED" in verdict
    assert "Zero live telemetry" in verdict

    with pytest.raises(AGORAComplianceViolation):
        agora.enforce_guardrail("amf-01", "scale_out")


def test_agora_passes_when_recent_estimation():
    agora = AGORAInterceptor(window_seconds=5.0)
    agora.record_state_estimation("amf-01", "amf_active_ngap_contexts", 15420.0)

    compliant, verdict = agora.verify_compliance("amf-01", "scale_out")
    assert compliant
    assert "PASSED" in verdict
    assert "Live Prometheus queried" in verdict

    res = agora.enforce_guardrail("amf-01", "scale_out")
    assert "PASSED" in res


def test_agora_blocks_when_estimation_stale():
    agora = AGORAInterceptor(window_seconds=1.0)  # 1 second window
    agora.record_state_estimation("amf-01", "amf_active_ngap_contexts", 15420.0)
    time.sleep(1.2)  # Wait for window expiry

    compliant, verdict = agora.verify_compliance("amf-01", "scale_out")
    assert not compliant
    assert "BLOCKED" in verdict
    assert "stale" in verdict
