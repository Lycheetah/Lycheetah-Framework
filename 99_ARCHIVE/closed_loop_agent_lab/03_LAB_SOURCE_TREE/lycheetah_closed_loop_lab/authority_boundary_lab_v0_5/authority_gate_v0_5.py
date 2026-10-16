"""Reference prototype: approval bound to a host-owned dispatch registry.

Research scaffold only. It binds an action to a registered dispatcher identity
and version, so a caller cannot choose an arbitrary execution callback at the
moment of use. It does NOT authenticate the human, protect the key from a model
process, or make a remote effect atomic with the local nonce claim.
"""
from __future__ import annotations

import base64
import hashlib
import hmac
import json
import math
import secrets
import sqlite3
import time
from contextlib import closing
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable, Iterable, Mapping

SCHEMA_VERSION = "lycheetah-approval/0.2"
MAX_TTL_SECONDS = 600


def _canonical_bytes(value: Any) -> bytes:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    ).encode("utf-8")


def _b64u(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode("ascii")


def _unb64u(value: str) -> bytes:
    if not isinstance(value, str) or not value:
        raise ValueError("empty token segment")
    return base64.urlsafe_b64decode(value + "=" * (-len(value) % 4))


def _valid_sha256(value: str, name: str) -> None:
    if not isinstance(value, str) or len(value) != 64:
        raise ValueError(f"{name} must be a 64-character SHA-256 hex digest")
    try:
        int(value, 16)
    except ValueError as exc:
        raise ValueError(f"{name} must be hexadecimal") from exc


@dataclass(frozen=True)
class ActionIntent:
    """Frozen canonical snapshot of the action and trusted dispatch destination."""
    agent_id: str
    operation_id: str
    tool_name: str
    arguments: Mapping[str, Any]
    scopes: tuple[str, ...]
    workspace_id: str
    dispatcher_id: str
    dispatcher_version: str
    side_effect: bool = True
    _canonical: str = field(default="", init=False, repr=False, compare=False)

    def __post_init__(self) -> None:
        for name in (
            "agent_id", "operation_id", "tool_name", "workspace_id", "dispatcher_id", "dispatcher_version"
        ):
            value = getattr(self, name)
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"{name} must be a non-empty string")
        if not isinstance(self.scopes, tuple) or any(
            not isinstance(item, str) or not item for item in self.scopes
        ):
            raise ValueError("scopes must be a tuple of non-empty strings")
        if self.side_effect is not True:
            raise ValueError("this prototype only gates consequential actions")
        if not isinstance(self.arguments, Mapping):
            raise ValueError("arguments must be a JSON-compatible mapping")
        body = {
            "agent_id": self.agent_id,
            "operation_id": self.operation_id,
            "tool_name": self.tool_name,
            "arguments": self.arguments,
            "scopes": list(self.scopes),
            "workspace_id": self.workspace_id,
            "dispatcher_id": self.dispatcher_id,
            "dispatcher_version": self.dispatcher_version,
            "side_effect": self.side_effect,
        }
        canonical = _canonical_bytes(body).decode("utf-8")
        object.__setattr__(self, "_canonical", canonical)

    @property
    def digest(self) -> str:
        return hashlib.sha256(self._canonical.encode("utf-8")).hexdigest()

    def execution_payload(self) -> dict[str, Any]:
        """Return a fresh JSON copy of the exact approved snapshot."""
        return json.loads(self._canonical)


class GateDenied(RuntimeError):
    def __init__(self, reason: str):
        self.reason = reason
        super().__init__(reason)


@dataclass(frozen=True)
class RegisteredDispatcher:
    """Trusted host-configuration entry; version must change with semantics."""
    tool_name: str
    dispatcher_id: str
    version: str
    handler: Callable[[dict[str, Any]], Any] = field(compare=False, repr=False)

    def __post_init__(self) -> None:
        for name in ("tool_name", "dispatcher_id", "version"):
            value = getattr(self, name)
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"{name} must be non-empty")
        if not callable(self.handler):
            raise ValueError("handler must be callable")


class DispatchRegistry:
    """Host-owned allowlisted route table; never built from agent-provided data."""
    def __init__(self, dispatchers: Iterable[RegisteredDispatcher]):
        items = list(dispatchers)
        self._items: dict[str, RegisteredDispatcher] = {}
        for item in items:
            if item.tool_name in self._items:
                raise ValueError(f"duplicate dispatcher tool name: {item.tool_name}")
            self._items[item.tool_name] = item

    def make_intent(
        self,
        *,
        agent_id: str,
        tool_name: str,
        arguments: Mapping[str, Any],
        scopes: tuple[str, ...],
        workspace_id: str,
    ) -> ActionIntent:
        target = self._items.get(tool_name)
        if target is None:
            raise GateDenied("tool-not-registered")
        return ActionIntent(
            agent_id=agent_id,
            operation_id=secrets.token_hex(16),
            tool_name=tool_name,
            arguments=arguments,
            scopes=scopes,
            workspace_id=workspace_id,
            dispatcher_id=target.dispatcher_id,
            dispatcher_version=target.version,
            side_effect=True,
        )

    def resolve(self, action: ActionIntent) -> RegisteredDispatcher:
        target = self._items.get(action.tool_name)
        if target is None:
            raise GateDenied("tool-not-registered")
        if (action.dispatcher_id, action.dispatcher_version) != (
            target.dispatcher_id, target.version
        ):
            raise GateDenied("dispatcher-binding-changed")
        return target


class ApprovalAuthority:
    """Token issuer, which must sit behind an authenticated trusted-host API."""
    def __init__(
        self, secret_key: bytes, *, audience_id: str, clock: Callable[[], float] = time.time
    ):
        if not isinstance(secret_key, bytes) or len(secret_key) < 32:
            raise ValueError("secret_key must be at least 32 bytes")
        if not isinstance(audience_id, str) or not audience_id.strip():
            raise ValueError("audience_id must be non-empty")
        if not callable(clock):
            raise TypeError("clock must be a trusted host callable")
        self._key = secret_key
        self.audience_id = audience_id
        self._clock = clock

    def issue(
        self,
        action: ActionIntent,
        *,
        policy_sha256: str,
        reviewer_id: str,
        approval_ref: str,
        ttl_seconds: int = 120,
    ) -> str:
        _valid_sha256(policy_sha256, "policy_sha256")
        if not isinstance(reviewer_id, str) or not reviewer_id.strip():
            raise ValueError("reviewer_id must be non-empty")
        if not isinstance(approval_ref, str) or not approval_ref.strip():
            raise ValueError("approval_ref must be non-empty")
        if type(ttl_seconds) is not int or not (1 <= ttl_seconds <= MAX_TTL_SECONDS):
            raise ValueError(f"ttl_seconds must be between 1 and {MAX_TTL_SECONDS}")
        try:
            issued_at = float(self._clock())
        except Exception as exc:
            raise ValueError("trusted clock unavailable") from exc
        if not math.isfinite(issued_at):
            raise ValueError("issued time must be finite")
        payload = {
            "schema": SCHEMA_VERSION,
            "audience_id": self.audience_id,
            "nonce": secrets.token_hex(16),
            "action_sha256": action.digest,
            "dispatcher_id": action.dispatcher_id,
            "dispatcher_version": action.dispatcher_version,
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
    """Verify, consume, then dispatch only via host-owned trusted services.

    The authoritative policy digest and clock are loaded through dependencies
    installed at construction; callers cannot override either per operation.
    Nonce claims are atomic within one SQLite database. A failure after claim
    requires provider-state reconciliation; the token must not be retried.
    """
    def __init__(
        self,
        secret_key: bytes,
        db_path: str | Path,
        registry: DispatchRegistry,
        *,
        audience_id: str,
        policy_provider: Callable[[], str],
        clock: Callable[[], float] = time.time,
    ):
        if not isinstance(secret_key, bytes) or len(secret_key) < 32:
            raise ValueError("secret_key must be at least 32 bytes")
        if not isinstance(registry, DispatchRegistry):
            raise TypeError("registry must be a host-owned DispatchRegistry")
        if not isinstance(audience_id, str) or not audience_id.strip():
            raise ValueError("audience_id must be non-empty")
        if not callable(policy_provider) or not callable(clock):
            raise TypeError("policy_provider and clock must be trusted host callables")
        self._key = secret_key
        self.db_path = str(db_path)
        self.registry = registry
        self.audience_id = audience_id
        self._policy_provider = policy_provider
        self._clock = clock
        with closing(sqlite3.connect(self.db_path)) as db:
            db.execute(
                "CREATE TABLE IF NOT EXISTS consumed_approvals ("
                "nonce TEXT PRIMARY KEY, action_sha256 TEXT NOT NULL, "
                "policy_sha256 TEXT NOT NULL, consumed_at REAL NOT NULL)"
            )
            db.execute(
                "CREATE TABLE IF NOT EXISTS revoked_approvals ("
                "nonce TEXT PRIMARY KEY, revoked_at REAL NOT NULL, reason TEXT NOT NULL)"
            )
            db.commit()

    def revoke(self, token: str, *, reason: str = "operator-revoked") -> None:
        """Revoke a valid token before dispatch using the same local authority DB.

        The caller must be an authenticated trusted operator. This method does
        not infer or authenticate the identity of whoever requests revocation.
        """
        if not isinstance(reason, str) or not reason.strip():
            raise ValueError("revocation reason must be non-empty")
        payload = self._verify_token(token)
        try:
            revoked_at = float(self._clock())
        except Exception as exc:
            raise GateDenied("clock-source-unavailable") from exc
        if not math.isfinite(revoked_at):
            raise GateDenied("clock-value-invalid")
        try:
            with closing(sqlite3.connect(self.db_path, timeout=10, isolation_level=None)) as db:
                db.execute("BEGIN IMMEDIATE")
                db.execute(
                    "INSERT OR IGNORE INTO revoked_approvals (nonce, revoked_at, reason) VALUES (?, ?, ?)",
                    (payload["nonce"], revoked_at, reason.strip()),
                )
                db.execute("COMMIT")
        except sqlite3.OperationalError as exc:
            raise GateDenied("revocation-store-unavailable") from exc

    def execute(self, token: str | None, action: ActionIntent) -> Any:
        payload = self._verify_token(token)
        try:
            current_time = float(self._clock())
        except Exception as exc:
            raise GateDenied("clock-source-unavailable") from exc
        if not math.isfinite(current_time):
            raise GateDenied("clock-value-invalid")
        try:
            current_policy_sha256 = self._policy_provider()
            _valid_sha256(current_policy_sha256, "current_policy_sha256")
        except Exception as exc:
            raise GateDenied("policy-source-unavailable-or-invalid") from exc
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
        if payload["dispatcher_id"] != action.dispatcher_id or payload["dispatcher_version"] != action.dispatcher_version:
            raise GateDenied("token-dispatcher-mismatch")
        if payload["policy_sha256"] != current_policy_sha256:
            raise GateDenied("policy-changed")

        # Resolve the executable target from trusted config, not a caller callback.
        target = self.registry.resolve(action)
        try:
            with closing(sqlite3.connect(self.db_path, timeout=10, isolation_level=None)) as db:
                db.execute("BEGIN IMMEDIATE")
                try:
                    revoked = db.execute(
                        "SELECT 1 FROM revoked_approvals WHERE nonce = ?", (payload["nonce"],)
                    ).fetchone()
                    if revoked is not None:
                        db.execute("ROLLBACK")
                        raise GateDenied("token-revoked")
                    db.execute(
                        "INSERT INTO consumed_approvals "
                        "(nonce, action_sha256, policy_sha256, consumed_at) VALUES (?, ?, ?, ?)",
                        (payload["nonce"], action.digest, current_policy_sha256, current_time),
                    )
                    db.execute("COMMIT")
                except Exception:
                    # ROLLBACK can itself fail if we already rolled back above.
                    try:
                        db.execute("ROLLBACK")
                    except sqlite3.Error:
                        pass
                    raise
        except sqlite3.IntegrityError as exc:
            raise GateDenied("token-replayed") from exc
        except sqlite3.OperationalError as exc:
            raise GateDenied("nonce-store-unavailable") from exc

        try:
            return target.handler(action.execution_payload())
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
            "schema", "audience_id", "nonce", "action_sha256", "dispatcher_id",
            "dispatcher_version", "policy_sha256", "issued_at", "expires_at",
            "reviewer_id", "approval_ref",
        }
        if not isinstance(payload, dict) or set(payload) != required:
            raise GateDenied("token-schema-invalid")
        if payload["schema"] != SCHEMA_VERSION:
            raise GateDenied("token-version-unsupported")
        if payload["audience_id"] != self.audience_id:
            raise GateDenied("token-audience-mismatch")
        for name in (
            "audience_id", "nonce", "action_sha256", "dispatcher_id", "dispatcher_version",
            "policy_sha256", "reviewer_id", "approval_ref",
        ):
            if not isinstance(payload[name], str) or not payload[name]:
                raise GateDenied("token-field-invalid")
        if type(payload["issued_at"]) not in (int, float) or type(payload["expires_at"]) not in (int, float):
            raise GateDenied("token-time-invalid")
        if not math.isfinite(float(payload["issued_at"])) or not math.isfinite(float(payload["expires_at"])):
            raise GateDenied("token-time-invalid")
        try:
            _valid_sha256(payload["action_sha256"], "action_sha256")
            _valid_sha256(payload["policy_sha256"], "policy_sha256")
        except ValueError as exc:
            raise GateDenied("token-digest-invalid") from exc
        return payload
