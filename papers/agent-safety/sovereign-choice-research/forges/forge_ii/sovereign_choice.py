"""Lycheetah Sovereign Choice Protocol v0.1 — local reference simulator.

IMPORTANT: Does not execute any external action, authenticate humans, or certify
free will. A real deployment must put the owner API behind independent human
identity and authentication, isolate the gateway from the underlying tools, and
complete a security review.

Only standard-library dependencies. Python 3.10+.
"""
from __future__ import annotations

import hashlib
import hmac
import json
import sqlite3
import threading
import time
from typing import Callable
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

# Host-owned classification. Agent cannot mark a high-impact operation as low.
OPERATION_RISK = {
    "read_document": "low",
    "prepare_draft": "low",
    "summarize_document": "low",
    "send_email": "high",
    "publish_post": "high",
    "write_repository": "high",
    "transfer_money": "high",
}


def _canonical(value: dict) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


@dataclass(frozen=True)
class Request:
    owner: str
    agent: str
    grant_id: str
    operation: str
    resource: str
    request_id: str
    approval_id: Optional[str] = None
    payload_digest: str = ""  # SHA-256 of actual canonical external effect bytes, host-verifiable


@dataclass(frozen=True)
class Decision:
    allowed: bool
    reason: str
    receipt_hash: str
    intent_version: int


class SovereignChoice:
    """Serialized SQLite policy decision point; effects intentionally disabled."""

    def __init__(self, path: str | Path = ":memory:", *, audit_key: bytes,
                 clock: Optional[Callable[[], int]] = None):
        if not isinstance(audit_key, bytes) or len(audit_key) < 16:
            raise ValueError("audit_key must be at least 16 bytes (demo key is not production identity)")
        self._audit_key = audit_key
        self._clock = clock or (lambda: int(time.time()))  # clock is injected by trusted host
        self._mutex = threading.RLock()
        self.db = sqlite3.connect(str(path), isolation_level=None, timeout=10, check_same_thread=False)
        self.db.execute("PRAGMA foreign_keys=ON")
        self.db.execute("PRAGMA busy_timeout=10000")
        if str(path) != ":memory:":
            self.db.execute("PRAGMA journal_mode=WAL")
        self.db.executescript("""
        CREATE TABLE IF NOT EXISTS owners (
          owner TEXT PRIMARY KEY, intent_version INTEGER NOT NULL DEFAULT 1
        );
        CREATE TABLE IF NOT EXISTS grants (
          grant_id TEXT PRIMARY KEY, owner TEXT NOT NULL REFERENCES owners(owner),
          agent TEXT NOT NULL, operation TEXT NOT NULL, resource TEXT NOT NULL,
          intent_version INTEGER NOT NULL, expires_at INTEGER NOT NULL,
          uses_remaining INTEGER NOT NULL CHECK(uses_remaining>=0), revoked INTEGER NOT NULL DEFAULT 0
        );
        CREATE TABLE IF NOT EXISTS approvals (
          approval_id TEXT PRIMARY KEY, grant_id TEXT NOT NULL REFERENCES grants(grant_id),
          request_id TEXT NOT NULL, operation TEXT NOT NULL, resource TEXT NOT NULL,
          intent_version INTEGER NOT NULL, expires_at INTEGER NOT NULL,
          payload_digest TEXT NOT NULL,
          used INTEGER NOT NULL DEFAULT 0
        );
        CREATE TABLE IF NOT EXISTS requests (
          request_id TEXT PRIMARY KEY, grant_id TEXT NOT NULL,
          operation TEXT NOT NULL, resource TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS audit (
          seq INTEGER PRIMARY KEY AUTOINCREMENT, event TEXT NOT NULL,
          payload TEXT NOT NULL, previous_hash TEXT NOT NULL,
          hash TEXT NOT NULL, signature TEXT NOT NULL
        );
        """)

    def close(self) -> None:
        self.db.close()

    def _start(self) -> None:
        # One SQLite connection may be shared by threads, but transactions may not overlap.
        # Serialize at the Python connection boundary; SQLite also serializes writers
        # across connections via BEGIN IMMEDIATE.
        self._mutex.acquire()
        try:
            self.db.execute("BEGIN IMMEDIATE")
        except Exception:
            self._mutex.release()
            raise

    def _finish(self, success: bool = True) -> None:
        try:
            self.db.execute("COMMIT" if success else "ROLLBACK")
        finally:
            self._mutex.release()

    def _log(self, event: str, data: dict) -> str:
        previous_row = self.db.execute("SELECT hash FROM audit ORDER BY seq DESC LIMIT 1").fetchone()
        prev = previous_row[0] if previous_row else "GENESIS"
        payload = _canonical(data)
        digest = hashlib.sha256((prev + "|" + event + "|" + payload).encode("utf-8")).hexdigest()
        sig = hmac.new(self._audit_key, digest.encode("ascii"), hashlib.sha256).hexdigest()
        self.db.execute(
            "INSERT INTO audit(event,payload,previous_hash,hash,signature) VALUES (?,?,?,?,?)",
            (event, payload, prev, digest, sig),
        )
        return digest

    def _validate_id(self, value: str, label: str) -> None:
        if not isinstance(value, str) or not value.strip() or len(value) > 200:
            raise ValueError(f"{label} must be a nonempty string with at most 200 characters")

    @staticmethod
    def _validate_digest(digest: str) -> None:
        if not isinstance(digest, str) or len(digest) != 64 or any(c not in "0123456789abcdef" for c in digest):
            raise ValueError("payload_digest must be 64 lowercase hexadecimal SHA-256 characters")

    # OWNER API: host must restrict this API to authenticated, legitimately authorised humans.
    # Passing an arbitrary owner string to these methods is NOT authentication.
    def register_owner(self, owner: str) -> int:
        self._validate_id(owner, "owner")
        self._start()
        try:
            self.db.execute("INSERT OR IGNORE INTO owners(owner,intent_version) VALUES (?,1)", (owner,))
            ver = self._version(owner)
            self._log("register_owner", {"owner": owner, "intent_version": ver})
            self._finish()
            return ver
        except Exception:
            self._finish(False)
            raise

    def _version(self, owner: str) -> int:
        row = self.db.execute("SELECT intent_version FROM owners WHERE owner=?", (owner,)).fetchone()
        if row is None:
            raise ValueError("Owner unknown")
        return int(row[0])

    def revise_intent(self, owner: str, *, reason: str) -> int:
        """Invalidate all grants for this owner's previous intent version.

        Recording a reason does not prove it was free, informed or authentic.
        """
        self._validate_id(owner, "owner")
        if not isinstance(reason, str) or not reason.strip():
            raise ValueError("A reason or 'prefer not to say' must be recorded")
        self._start()
        try:
            version = self._version(owner) + 1
            self.db.execute("UPDATE owners SET intent_version=? WHERE owner=?", (version, owner))
            # Don't collect sensitive private reasons in the log. Digest only.
            reason_digest = hashlib.sha256(reason.encode("utf-8")).hexdigest()
            self._log("revise_intent", {"owner": owner, "intent_version": version,
                                        "reason_sha256": reason_digest})
            self._finish()
            return version
        except Exception:
            self._finish(False)
            raise

    def issue_grant(self, *, grant_id: str, owner: str, agent: str,
                    operation: str, resource: str, expires_at: int, max_uses: int = 1) -> int:
        for label, value in [("grant_id", grant_id), ("owner", owner), ("agent", agent),
                             ("operation", operation), ("resource", resource)]:
            self._validate_id(value, label)
        if operation not in OPERATION_RISK:
            raise ValueError("Unknown operation: deny by default")
        if type(expires_at) is not int or type(max_uses) is not int or expires_at <= 0 or max_uses < 1:
            raise ValueError("Invalid expiry or max_uses")
        self._start()
        try:
            version = self._version(owner)
            self.db.execute("""INSERT INTO grants
                (grant_id,owner,agent,operation,resource,intent_version,expires_at,uses_remaining)
                VALUES (?,?,?,?,?,?,?,?)""",
                (grant_id, owner, agent, operation, resource, version, expires_at, max_uses))
            self._log("issue_grant", {"grant_id": grant_id, "owner": owner, "agent": agent,
                                      "operation": operation, "resource": resource,
                                      "intent_version": version, "expires_at": expires_at,
                                      "max_uses": max_uses})
            self._finish()
            return version
        except Exception:
            self._finish(False)
            raise

    def revoke(self, owner: str, grant_id: str) -> bool:
        self._start()
        try:
            cursor = self.db.execute("UPDATE grants SET revoked=1 WHERE owner=? AND grant_id=? AND revoked=0",
                                     (owner, grant_id))
            changed = cursor.rowcount == 1
            self._log("revoke", {"owner": owner, "grant_id": grant_id, "changed": changed})
            self._finish()
            return changed
        except Exception:
            self._finish(False)
            raise

    def approve_once(self, *, owner: str, approval_id: str, grant_id: str, request_id: str,
                     operation: str, resource: str, expires_at: int, payload_digest: str) -> None:
        for label, value in [("approval_id", approval_id), ("request_id", request_id),
                             ("operation", operation), ("resource", resource)]:
            self._validate_id(value, label)
        if type(expires_at) is not int or expires_at <= 0:
            raise ValueError("Invalid approval expiry")
        self._validate_digest(payload_digest)
        self._start()
        try:
            row = self.db.execute("""SELECT owner,operation,resource,intent_version,revoked
                                    FROM grants WHERE grant_id=?""", (grant_id,)).fetchone()
            if row is None or row[0] != owner or row[1] != operation or row[2] != resource or row[4]:
                raise ValueError("Approval must match a currently unrevoked grant")
            if row[3] != self._version(owner):
                raise ValueError("Cannot approve against stale intent")
            self.db.execute("""INSERT INTO approvals
                (approval_id,grant_id,request_id,operation,resource,intent_version,expires_at,payload_digest)
                VALUES(?,?,?,?,?,?,?,?)""",
                (approval_id, grant_id, request_id, operation, resource, row[3], expires_at,
                 payload_digest))
            self._log("approve_once", {"approval_id": approval_id, "grant_id": grant_id,
                                       "request_id": request_id, "intent_version": row[3],
                                       "expires_at": expires_at,
                                       "payload_digest": payload_digest})
            self._finish()
        except Exception:
            self._finish(False)
            raise

    # AGENT API — safe to expose *only* this decision function, not owner methods.
    def decide(self, req: Request) -> Decision:
        """Atomically authorise or deny. Never executes the requested operation."""
        for label in ("owner", "agent", "grant_id", "operation", "resource", "request_id"):
            self._validate_id(getattr(req, label), label)
        now = self._clock()  # Never use agent-supplied clock for authorization.
        if type(now) is not int or now < 0:
            raise ValueError("Host clock returned invalid timestamp")
        self._start()
        try:
            row = self.db.execute("""SELECT owner,agent,operation,resource,intent_version,
                                  expires_at,uses_remaining,revoked FROM grants WHERE grant_id=?""",
                                  (req.grant_id,)).fetchone()
            version_row = self.db.execute("SELECT intent_version FROM owners WHERE owner=?",
                                          (req.owner,)).fetchone()
            version = int(version_row[0]) if version_row else 0
            reason = "allowed"
            if self.db.execute("SELECT 1 FROM requests WHERE request_id=?", (req.request_id,)).fetchone():
                reason = "replayed_request"
            elif req.operation not in OPERATION_RISK:
                reason = "unknown_operation"
            elif row is None:
                reason = "unknown_grant"
            elif row[0] != req.owner or row[1] != req.agent:
                reason = "wrong_principal"
            elif row[7]:
                reason = "revoked"
            elif row[4] != version:
                reason = "stale_intent"
            elif now >= row[5]:
                reason = "expired_grant"
            elif row[6] < 1:
                reason = "exhausted_grant"
            elif row[2] != req.operation or row[3] != req.resource:
                reason = "out_of_scope"
            elif OPERATION_RISK[req.operation] == "high":
                try:
                    self._validate_digest(req.payload_digest)
                except ValueError:
                    reason = "payload_binding_required"
                if reason == "allowed" and not req.approval_id:
                    reason = "approval_required"
                if reason == "allowed":
                    a = self.db.execute("""SELECT grant_id,request_id,operation,resource,
                                   intent_version,expires_at,used,payload_digest
                                   FROM approvals WHERE approval_id=?""", (req.approval_id,)).fetchone()
                    if a is None or a[0] != req.grant_id or a[1] != req.request_id or a[2] != req.operation \
                       or a[3] != req.resource or a[4] != version or a[6] or now >= a[5] \
                       or not hmac.compare_digest(a[7], req.payload_digest):
                        reason = "invalid_approval"
            allowed = reason == "allowed"
            # Replay protection is keyed by request_id, including denied attempts. Re-try with new request_id.
            self.db.execute("""INSERT OR IGNORE INTO requests(request_id,grant_id,operation,resource)
                               VALUES(?,?,?,?)""", (req.request_id, req.grant_id, req.operation, req.resource))
            if allowed:
                self.db.execute("UPDATE grants SET uses_remaining=uses_remaining-1 WHERE grant_id=?",
                                (req.grant_id,))
                if OPERATION_RISK[req.operation] == "high":
                    self.db.execute("UPDATE approvals SET used=1 WHERE approval_id=?", (req.approval_id,))
            receipt_hash = self._log("decision", {
                "request_id": req.request_id, "owner": req.owner, "agent": req.agent,
                "grant_id": req.grant_id, "operation": req.operation, "resource": req.resource,
                "intent_version": version, "at": now, "allowed": allowed,
                "payload_digest": req.payload_digest, "reason": reason,
            })
            self._finish()
            return Decision(allowed, reason, receipt_hash, version)
        except Exception:
            self._finish(False)
            raise

    def audit_ok(self) -> bool:
        prev = "GENESIS"
        for event, payload, recorded_prev, digest, signature in self.db.execute(
                "SELECT event,payload,previous_hash,hash,signature FROM audit ORDER BY seq"):
            expected = hashlib.sha256((prev + "|" + event + "|" + payload).encode("utf-8")).hexdigest()
            expected_sig = hmac.new(self._audit_key, expected.encode("ascii"), hashlib.sha256).hexdigest()
            if recorded_prev != prev or not hmac.compare_digest(digest, expected) \
               or not hmac.compare_digest(signature, expected_sig):
                return False
            prev = digest
        return True

    def audit_count(self) -> int:
        return self.db.execute("SELECT COUNT(*) FROM audit").fetchone()[0]
