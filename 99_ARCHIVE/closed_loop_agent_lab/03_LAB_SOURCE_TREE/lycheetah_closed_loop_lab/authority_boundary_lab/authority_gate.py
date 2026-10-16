"""Reference prototype: host-owned, action-bound, one-use approvals.

This is a local research scaffold, not a production authorization service.
The authority key must be inaccessible to the model/agent process, and the
trusted host must authenticate the human before calling ApprovalAuthority.issue.
"""
from __future__ import annotations

import base64
import hashlib
import hmac
import json
import secrets
import sqlite3
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Mapping

SCHEMA_VERSION = "lycheetah-approval/0.1"
MAX_TTL_SECONDS = 600


def _canonical_bytes(value: Any) -> bytes:
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=False,
        allow_nan=False,
    ).encode("utf-8")


def _b64u(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode("ascii")


def _unb64u(value: str) -> bytes:
    if not isinstance(value, str) or not value:
        raise ValueError("empty token segment")
    return base64.urlsafe_b64decode(value + "=" * (-len(value) % 4))


@dataclass(frozen=True)
class ActionIntent:
    """Immutable snapshot of the action approved and later dispatched.

    Arguments are snapshotted to canonical JSON at construction, so later
    mutation of the caller's source dict cannot silently change the dispatch.
    """
    agent_id: str
    tool_name: str
    arguments: Mapping[str, Any]
    scopes: tuple[str, ...]
    workspace_id: str
    side_effect: bool = True
    _canonical: str = ""

    def __post_init__(self) -> None:
        for name in ("agent_id", "tool_name", "workspace_id"):
            value = getattr(self, name)
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"{name} must be a non-empty string")
        if not self.side_effect:
            raise ValueError("this prototype only gates consequential actions")
        if not isinstance(self.scopes, tuple) or any(not isinstance(x, str) or not x for x in self.scopes):
            raise ValueError("scopes must be a tuple of non-empty strings")
        # Snapshot only JSON-compatible content; actual execution uses this snapshot.
        body = {
            "agent_id": self.agent_id,
            "tool_name": self.tool_name,
            "arguments": self.arguments,
            "scopes": list(self.scopes),
            "workspace_id": self.workspace_id,
            "side_effect": self.side_effect,
        }
        canonical = _canonical_bytes(body).decode("utf-8")
        object.__setattr__(self, "_canonical", canonical)

    @property
    def digest(self) -> str:
        return hashlib.sha256(self._canonical.encode("utf-8")).hexdigest()

    def execution_payload(self) -> dict[str, Any]:
        """Return a fresh decoded copy of the immutable, digest-bound intent."""
        return json.loads(self._canonical)


class GateDenied(RuntimeError):
    def __init__(self, reason: str):
        self.reason = reason
        super().__init__(reason)


class ApprovalAuthority:
    """Issues signed approvals; MUST live behind a trusted host boundary."""
    def __init__(self, secret_key: bytes):
        if not isinstance(secret_key, bytes) or len(secret_key) < 32:
            raise ValueError("secret_key must be at least 32 bytes")
        self._key = secret_key

    def issue(
        self,
        action: ActionIntent,
        *,
        policy_sha256: str,
        reviewer_id: str,
        approval_ref: str,
        ttl_seconds: int = 120,
        now: float | None = None,
    ) -> str:
        """Issue after the host has independently authenticated approval.

        This method itself does not authenticate reviewer_id or approval_ref.
        That is a deployment integration responsibility, not a model claim.
        """
        if not isinstance(policy_sha256, str) or len(policy_sha256) != 64:
            raise ValueError("policy_sha256 must be a 64-character SHA-256 hex digest")
        try:
            int(policy_sha256, 16)
        except ValueError as exc:
            raise ValueError("policy_sha256 must be hexadecimal") from exc
        if not reviewer_id or not approval_ref:
            raise ValueError("reviewer_id and approval_ref must be non-empty")
        if not isinstance(ttl_seconds, int) or not (1 <= ttl_seconds <= MAX_TTL_SECONDS):
            raise ValueError(f"ttl_seconds must be between 1 and {MAX_TTL_SECONDS}")
        issued_at = float(time.time() if now is None else now)
        payload = {
            "schema": SCHEMA_VERSION,
            "nonce": secrets.token_hex(16),
            "action_sha256": action.digest,
            "policy_sha256": policy_sha256,
            "issued_at": issued_at,
            "expires_at": issued_at + ttl_seconds,
            "reviewer_id": reviewer_id,
            "approval_ref": approval_ref,
        }
        body = _canonical_bytes(payload)
        signature = hmac.new(self._key, body, hashlib.sha256).digest()
        return f"{_b64u(body)}.{_b64u(signature)}"


class ConsequenceGate:
    """Verify, bind, and consume one approval token before dispatch.

    SQLite nonce claims are atomic in a single local database. This does not
    make a remote effect atomic with the claim and does not replace provider-side
    idempotency/reconciliation for uncertain outcomes.
    """
    def __init__(self, secret_key: bytes, db_path: str | Path):
        if not isinstance(secret_key, bytes) or len(secret_key) < 32:
            raise ValueError("secret_key must be at least 32 bytes")
        self._key = secret_key
        self.db_path = str(db_path)
        with sqlite3.connect(self.db_path) as db:
            db.execute(
                "CREATE TABLE IF NOT EXISTS consumed_approvals ("
                "nonce TEXT PRIMARY KEY, action_sha256 TEXT NOT NULL, "
                "policy_sha256 TEXT NOT NULL, consumed_at REAL NOT NULL)"
            )

    def execute(
        self,
        token: str | None,
        action: ActionIntent,
        *,
        current_policy_sha256: str,
        effect: Callable[[dict[str, Any]], Any],
        now: float | None = None,
    ) -> Any:
        payload = self._verify_token(token)
        current_time = float(time.time() if now is None else now)
        if payload["issued_at"] > current_time:
            raise GateDenied("token-not-yet-valid")
        if payload["expires_at"] <= current_time:
            raise GateDenied("token-expired")
        if payload["expires_at"] <= payload["issued_at"] or (
            payload["expires_at"] - payload["issued_at"] > MAX_TTL_SECONDS
        ):
            raise GateDenied("invalid-token-lifetime")
        if payload["action_sha256"] != action.digest:
            raise GateDenied("action-mismatch")
        if payload["policy_sha256"] != current_policy_sha256:
            raise GateDenied("policy-changed")

        # Claim before effect: at-most-once dispatch intent. Do not retry this
        # token on uncertain effect failure; reconcile provider state instead.
        try:
            with sqlite3.connect(self.db_path, timeout=10, isolation_level=None) as db:
                db.execute("BEGIN IMMEDIATE")
                db.execute(
                    "INSERT INTO consumed_approvals "
                    "(nonce, action_sha256, policy_sha256, consumed_at) VALUES (?, ?, ?, ?)",
                    (payload["nonce"], action.digest, current_policy_sha256, current_time),
                )
                db.execute("COMMIT")
        except sqlite3.IntegrityError as exc:
            raise GateDenied("token-replayed") from exc
        except sqlite3.OperationalError as exc:
            raise GateDenied("nonce-store-unavailable") from exc

        try:
            # The executor receives the frozen, verified snapshot, not a mutable source dict.
            return effect(action.execution_payload())
        except Exception as exc:
            raise GateDenied("effect-error-token-consumed-reconcile-before-retry") from exc

    def _verify_token(self, token: str | None) -> dict[str, Any]:
        if not isinstance(token, str) or token.count(".") != 1:
            raise GateDenied("approval-token-required-or-malformed")
        body_part, signature_part = token.split(".", 1)
        try:
            body = _unb64u(body_part)
            signature = _unb64u(signature_part)
            payload = json.loads(body.decode("utf-8"))
        except Exception as exc:
            raise GateDenied("approval-token-malformed") from exc
        expected = hmac.new(self._key, body, hashlib.sha256).digest()
        if not hmac.compare_digest(signature, expected):
            raise GateDenied("token-authentication-failed")
        required = {
            "schema", "nonce", "action_sha256", "policy_sha256", "issued_at",
            "expires_at", "reviewer_id", "approval_ref",
        }
        if not isinstance(payload, dict) or set(payload) != required:
            raise GateDenied("token-schema-invalid")
        if payload["schema"] != SCHEMA_VERSION:
            raise GateDenied("token-version-unsupported")
        for name in ("nonce", "action_sha256", "policy_sha256", "reviewer_id", "approval_ref"):
            if not isinstance(payload[name], str) or not payload[name]:
                raise GateDenied("token-field-invalid")
        if type(payload["issued_at"]) not in (float, int) or type(payload["expires_at"]) not in (float, int):
            raise GateDenied("token-time-invalid")
        return payload
