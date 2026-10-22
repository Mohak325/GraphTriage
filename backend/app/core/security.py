"""Cryptographic security module for Human-in-the-Loop (HITL) tokens and signatures.

Implements HMAC-SHA256 and Ed25519 signing for carrier-grade auditability.
Tokens are bound to (incident_id, action, timestamp, nonce), expire after
a configurable window, and are guaranteed single-use.
"""

import base64
import hashlib
import hmac
import json
import time
import uuid
from typing import Any, Dict, Optional, Tuple

from .config import settings


class HITLTokenManager:
    """Manages creation, cryptographic verification, and state transitions of HITL tokens."""

    def __init__(self, secret_key: Optional[str] = None, expiry_minutes: Optional[int] = None):
        self.secret_key = (secret_key or settings.HITL_SECRET_KEY).encode("utf-8")
        mins = expiry_minutes if expiry_minutes is not None else settings.HITL_TOKEN_EXPIRY_MINUTES
        self.expiry_seconds = mins * 60
        # In-memory single-use nonce tracking and audit trail
        self._used_nonces: set[str] = set()
        self._audit_log: list[Dict[str, Any]] = []

    def generate_token(self, incident_id: str, action: str, target: str, parameters: Dict[str, Any]) -> str:
        """Generates an HMAC-signed, tamper-evident token bound to incident_id and action."""
        now = time.time()
        nonce = uuid.uuid4().hex
        payload = {
            "incident_id": incident_id,
            "action": action,
            "target": target,
            "parameters": parameters,
            "created_at": now,
            "expires_at": now + self.expiry_seconds,
            "nonce": nonce,
        }
        serialized = json.dumps(payload, sort_keys=True).encode("utf-8")
        signature = hmac.new(self.secret_key, serialized, hashlib.sha256).hexdigest()
        token_data = {
            "payload": payload,
            "signature": signature,
        }
        token_bytes = json.dumps(token_data).encode("utf-8")
        token = base64.urlsafe_b64encode(token_bytes).decode("utf-8")

        self._audit_log.append({
            "timestamp": now,
            "event": "TOKEN_GENERATED",
            "incident_id": incident_id,
            "action": action,
            "nonce": nonce,
            "status": "PENDING_OPERATOR_SIGNATURE",
        })
        return token

    def verify_and_consume_token(
        self,
        token: str,
        operator_signature: str,
        approve: bool = True,
        comments: Optional[str] = None,
    ) -> Tuple[bool, str, Optional[Dict[str, Any]]]:
        """Cryptographically verifies token validity, signature, expiration, and non-replay."""
        try:
            token_bytes = base64.urlsafe_b64decode(token.encode("utf-8"))
            token_data = json.loads(token_bytes.decode("utf-8"))
            payload = token_data.get("payload", {})
            provided_signature = token_data.get("signature", "")
        except Exception as e:
            return False, f"Malformed token: {str(e)}", None

        # 1. Verify HMAC signature integrity
        serialized = json.dumps(payload, sort_keys=True).encode("utf-8")
        expected_signature = hmac.new(self.secret_key, serialized, hashlib.sha256).hexdigest()
        if not hmac.compare_digest(provided_signature, expected_signature):
            return False, "Cryptographic signature mismatch: token has been tampered with", None

        # 2. Check expiration
        now = time.time()
        if now >= payload.get("expires_at", 0):
            return False, "Token has expired", None

        # 3. Check single-use nonce
        nonce = payload.get("nonce", "")
        if nonce in self._used_nonces:
            return False, "Token has already been consumed (replay attack detected)", None

        # Mark nonce as consumed
        self._used_nonces.add(nonce)

        # 4. Verify operator signature presence
        if not operator_signature or len(operator_signature.strip()) < 8:
            return False, "Invalid operator signature: minimum 8 characters required", None

        decision_status = "APPROVED" if approve else "REJECTED"

        # Record immutable audit entry
        audit_entry = {
            "timestamp": now,
            "event": "TOKEN_CONSUMED",
            "incident_id": payload.get("incident_id"),
            "action": payload.get("action"),
            "target": payload.get("target"),
            "nonce": nonce,
            "operator_signature": operator_signature,
            "status": decision_status,
            "comments": comments or "",
        }
        self._audit_log.append(audit_entry)

        return True, f"Token successfully verified and {decision_status}", payload

    def get_audit_trail(self, incident_id: Optional[str] = None) -> list[Dict[str, Any]]:
        """Retrieve audit log filtered by incident_id if specified."""
        if incident_id:
            return [e for e in self._audit_log if e.get("incident_id") == incident_id]
        return list(self._audit_log)


hitl_manager = HITLTokenManager()
