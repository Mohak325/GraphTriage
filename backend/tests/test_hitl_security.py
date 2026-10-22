"""Tests for HITL Cryptographic Approval Tokens, Expiry, and Replay Defense."""

import time
import pytest
from backend.app.core.security import HITLTokenManager


def test_token_generation_and_valid_approval():
    mgr = HITLTokenManager(secret_key="test-secret-key", expiry_minutes=10)
    token = mgr.generate_token(
        incident_id="INC-2026-0042",
        action="horizontal_scale_and_pool_patch",
        target="amf-01",
        parameters={"replicas": 4, "client_pool_size": 2048},
    )
    assert token is not None and len(token) > 20

    # Successful verification
    valid, msg, payload = mgr.verify_and_consume_token(
        token=token,
        operator_signature="NOC-OPERATOR-KEY-001",
        approve=True,
    )
    assert valid is True
    assert "APPROVED" in msg
    assert payload["incident_id"] == "INC-2026-0042"


def test_token_single_use_replay_defense():
    mgr = HITLTokenManager(secret_key="test-secret-key", expiry_minutes=10)
    token = mgr.generate_token(
        incident_id="INC-2026-0042",
        action="horizontal_scale_and_pool_patch",
        target="amf-01",
        parameters={},
    )

    # First consumption succeeds
    valid1, _, _ = mgr.verify_and_consume_token(token, "NOC-OPERATOR-SIG-1")
    assert valid1 is True

    # Replay attempt fails immediately
    valid2, msg2, _ = mgr.verify_and_consume_token(token, "NOC-OPERATOR-SIG-1")
    assert valid2 is False
    assert "already been consumed" in msg2 or "replay" in msg2.lower()


def test_token_tampering_rejected():
    mgr1 = HITLTokenManager(secret_key="secret-key-1")
    mgr2 = HITLTokenManager(secret_key="secret-key-2")

    token = mgr1.generate_token("INC-2026-0042", "scale", "amf-01", {})
    # Verify with wrong secret key
    valid, msg, _ = mgr2.verify_and_consume_token(token, "NOC-OPERATOR-SIG")
    assert valid is False
    assert "mismatch" in msg.lower() or "tampered" in msg.lower()


def test_token_expiration():
    # 0 minute expiry (expired immediately)
    mgr = HITLTokenManager(secret_key="test-secret", expiry_minutes=0)
    token = mgr.generate_token("INC-2026-0042", "scale", "amf-01", {})
    time.sleep(0.1)

    valid, msg, _ = mgr.verify_and_consume_token(token, "NOC-OPERATOR-SIG")
    assert valid is False
    assert "expired" in msg.lower()
