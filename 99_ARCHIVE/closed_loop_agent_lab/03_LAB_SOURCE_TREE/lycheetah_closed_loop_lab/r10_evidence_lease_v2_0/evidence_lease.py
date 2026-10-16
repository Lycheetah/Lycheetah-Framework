"""Provider-cooperative, version-bound evidence leases for the R10 lab.

A dispatch token is short-lived. Once claimed IN_FLIGHT, the lease pins the
associated evidence until the provider outcome is confirmed or reconciled, even
after token TTL. This is a reference implementation, not a distributed transaction
or an upstream Lycheetah component.
"""
from __future__ import annotations

import hashlib
import hmac
import json
import sqlite3
import time
import uuid
from collections.abc import Callable, Mapping, Sequence
from pathlib import Path
from typing import Any

from durable_action_broker import (
    DefinitiveDispatchDenial,
    Evidence,
    IdempotencyConflict,
    Requirement,
    ResponseLost,
    canonical_bytes,
    sha256_json,
)


class EvidenceLocked(RuntimeError):
    """The current evidence is protected by an active authorization lease."""


class LeaseUnavailable(DefinitiveDispatchDenial):
    """No lease could be acquired; this dispatch is known not to have executed."""


class LeaseRejected(DefinitiveDispatchDenial):
    """The provider rejected the lease before applying any effect."""


class LeaseExpired(LeaseRejected):
    pass


def _token_mac(body: Mapping[str, Any], key: bytes) -> str:
    return hmac.new(key, sha256_json(body).encode("ascii"), hashlib.sha256).hexdigest()


def _satisfies(req: Requirement, record: Evidence) -> bool:
    return (record.key == req.key and record.status == req.required_status and
            (req.required_subject_hash is None or record.subject_hash == req.required_subject_hash))


class SQLiteEvidenceLeaseAuthority:
    """Evidence store with atomic lease issuance and write blocking while leased."""
    TOKEN_KEYS = {"body", "hmac_sha256"}
    BODY_KEYS = {"schema_version", "lease_id", "operation_id", "action_sha256",
                 "requirements_sha256", "issued_at", "expires_at", "evidence"}

    def __init__(self, db_path: str | Path, signing_key: bytes, *,
                 clock: Callable[[], float] = time.time, lease_seconds: int = 15):
        if not isinstance(signing_key, bytes) or len(signing_key) < 32:
            raise ValueError("lease signing key must contain at least 32 bytes")
        if isinstance(lease_seconds, bool) or not isinstance(lease_seconds, int) or lease_seconds < 1:
            raise ValueError("lease_seconds must be a positive integer")
        self.db_path = str(db_path)
        self._key = signing_key
        self.clock = clock
        self.lease_seconds = lease_seconds
        self._init_db()

    def _connect(self) -> sqlite3.Connection:
        con = sqlite3.connect(self.db_path, timeout=10, isolation_level=None)
        con.row_factory = sqlite3.Row
        con.execute("PRAGMA busy_timeout=10000")
        con.execute("PRAGMA foreign_keys=ON")
        return con

    def _init_db(self) -> None:
        con = self._connect()
        try:
            con.execute("PRAGMA journal_mode=WAL")
            con.execute("""CREATE TABLE IF NOT EXISTS evidence (
                key TEXT PRIMARY KEY, version TEXT NOT NULL, subject_hash TEXT NOT NULL,
                value_digest TEXT NOT NULL, status TEXT NOT NULL)""")
            con.execute("""CREATE TABLE IF NOT EXISTS leases (
                lease_id TEXT PRIMARY KEY, operation_id TEXT NOT NULL, action_sha256 TEXT NOT NULL,
                requirements_sha256 TEXT NOT NULL, body_json TEXT NOT NULL, token_json TEXT NOT NULL,
                issued_at REAL NOT NULL, expires_at REAL NOT NULL,
                state TEXT NOT NULL CHECK(state IN ('ACTIVE','IN_FLIGHT','RELEASED','EXPIRED')))""")
            con.execute("CREATE INDEX IF NOT EXISTS leases_by_operation ON leases(operation_id, issued_at)")
            con.execute("""CREATE TABLE IF NOT EXISTS lease_evidence (
                lease_id TEXT NOT NULL REFERENCES leases(lease_id), evidence_key TEXT NOT NULL,
                PRIMARY KEY(lease_id, evidence_key))""")
            con.execute("CREATE INDEX IF NOT EXISTS lease_evidence_by_key ON lease_evidence(evidence_key)")
        finally:
            con.close()

    @staticmethod
    def _row_to_evidence(row: sqlite3.Row | None) -> Evidence | None:
        if row is None:
            return None
        return Evidence(row["key"], row["version"], row["subject_hash"], row["value_digest"], row["status"])

    def get_evidence(self, key: str) -> Evidence | None:
        con = self._connect()
        try:
            row = con.execute("SELECT * FROM evidence WHERE key=?", (key,)).fetchone()
            return self._row_to_evidence(row)
        finally:
            con.close()

    def put(self, record: Evidence) -> None:
        """Refuse writes for active leases and for pinned in-flight leases even past TTL."""
        con = self._connect()
        try:
            con.execute("BEGIN IMMEDIATE")
            now = float(self.clock())
            con.execute("UPDATE leases SET state='EXPIRED' WHERE state='ACTIVE' AND expires_at<=?", (now,))
            active = con.execute("""SELECT l.lease_id FROM leases l
                JOIN lease_evidence le ON le.lease_id=l.lease_id
                WHERE le.evidence_key=? AND (l.state='IN_FLIGHT' OR (l.state='ACTIVE' AND l.expires_at>?)) LIMIT 1""",
                (record.key, now)).fetchone()
            if active is not None:
                con.rollback()
                raise EvidenceLocked(f"evidence {record.key!r} is protected by an active lease")
            con.execute("""INSERT INTO evidence(key,version,subject_hash,value_digest,status)
                VALUES(?,?,?,?,?) ON CONFLICT(key) DO UPDATE SET version=excluded.version,
                subject_hash=excluded.subject_hash,value_digest=excluded.value_digest,status=excluded.status""",
                (record.key, record.version, record.subject_hash, record.value_digest, record.status))
            con.commit()
        except EvidenceLocked:
            raise
        except sqlite3.Error:
            con.rollback()
            raise
        finally:
            con.close()

    def acquire_lease(self, operation_id: str, action_sha256: str,
                      requirements: Sequence[Requirement], admitted_items: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
        """Atomically validate evidence snapshots and lock every required evidence key."""
        if not operation_id or not isinstance(operation_id, str):
            raise ValueError("operation_id must be non-empty text")
        if not isinstance(action_sha256, str) or len(action_sha256) != 64:
            raise ValueError("action_sha256 must be a SHA-256 hex digest")
        if not requirements or len(requirements) != len(admitted_items):
            raise LeaseUnavailable("trusted-requirement-count-mismatch")
        requirement_hash = sha256_json([r.to_dict() for r in requirements])
        con = self._connect()
        try:
            con.execute("BEGIN IMMEDIATE")
            now = float(self.clock())
            con.execute("UPDATE leases SET state='EXPIRED' WHERE state='ACTIVE' AND expires_at<=?", (now,))
            same_op = con.execute("SELECT * FROM leases WHERE operation_id=? AND state IN ('ACTIVE','IN_FLIGHT') ORDER BY issued_at DESC",
                                  (operation_id,)).fetchall()
            for existing in same_op:
                if existing["state"] == 'IN_FLIGHT' or existing["expires_at"] > now:
                    if (existing["action_sha256"] != action_sha256 or
                            existing["requirements_sha256"] != requirement_hash):
                        con.rollback()
                        raise LeaseUnavailable("operation-already-has-differently-bound-lease")
                    token = json.loads(existing["token_json"])
                    con.commit()
                    return token

            bound: list[dict[str, Any]] = []
            for req, item in zip(requirements, admitted_items, strict=True):
                if not isinstance(item, Mapping) or set(item) != {"requirement", "admitted"}:
                    con.rollback()
                    raise LeaseUnavailable("malformed-admitted-evidence")
                if item["requirement"] != req.to_dict() or not isinstance(item["admitted"], Mapping):
                    con.rollback()
                    raise LeaseUnavailable("trusted-requirement-mismatch")
                admitted = dict(item["admitted"])
                row = con.execute("SELECT * FROM evidence WHERE key=?", (req.key,)).fetchone()
                current = self._row_to_evidence(row)
                if current is None or not _satisfies(req, current):
                    con.rollback()
                    raise LeaseUnavailable("evidence-predicate-false-at-lease")
                if req.mode == "EXACT" and current.to_dict() != admitted:
                    con.rollback()
                    raise LeaseUnavailable("exact-evidence-changed-before-lease")
                bound.append({"requirement": req.to_dict(), "admitted": current.to_dict()})

            lease_id = str(uuid.uuid4())
            expires = now + self.lease_seconds
            body = {"schema_version": "1.0", "lease_id": lease_id,
                    "operation_id": operation_id, "action_sha256": action_sha256,
                    "requirements_sha256": requirement_hash, "issued_at": now,
                    "expires_at": expires, "evidence": bound}
            token = {"body": body, "hmac_sha256": _token_mac(body, self._key)}
            token_json = canonical_bytes(token).decode("utf-8")
            con.execute("INSERT INTO leases VALUES(?,?,?,?,?,?,?,?,?)",
                        (lease_id, operation_id, action_sha256, requirement_hash,
                         canonical_bytes(body).decode("utf-8"), token_json, now, expires, "ACTIVE"))
            for item in bound:
                con.execute("INSERT INTO lease_evidence VALUES(?,?)", (lease_id, item["requirement"]["key"]))
            con.commit()
            return token
        except (LeaseUnavailable, EvidenceLocked):
            if con.in_transaction:
                con.rollback()
            raise
        except sqlite3.Error:
            if con.in_transaction:
                con.rollback()
            raise
        finally:
            con.close()

    def begin_execution(self, token: Mapping[str, Any]) -> None:
        """Pin a lease before the first provider call. IN_FLIGHT leases stay locked
        after nominal expiry until the provider outcome is reconciled."""
        body = token.get("body") if isinstance(token, Mapping) else None
        if not isinstance(body, Mapping) or not isinstance(body.get("lease_id"), str):
            raise LeaseUnavailable("invalid-lease-token-before-start")
        valid_mac = isinstance(token.get("hmac_sha256"), str) and hmac.compare_digest(
            token["hmac_sha256"], _token_mac(body, self._key))
        if not valid_mac:
            raise LeaseUnavailable("invalid-lease-authenticator-before-start")
        con = self._connect()
        try:
            con.execute("BEGIN IMMEDIATE")
            now = float(self.clock())
            row = con.execute("SELECT * FROM leases WHERE lease_id=?", (body["lease_id"],)).fetchone()
            if row is None or row["state"] not in ("ACTIVE", "IN_FLIGHT"):
                con.rollback()
                raise LeaseUnavailable("lease-not-available-for-execution")
            if row["token_json"] != canonical_bytes(dict(token)).decode("utf-8"):
                con.rollback()
                raise LeaseUnavailable("lease-token-not-current")
            if row["expires_at"] <= now:
                if row["state"] == "ACTIVE":
                    con.execute("UPDATE leases SET state='EXPIRED' WHERE lease_id=? AND state='ACTIVE'", (body["lease_id"],))
                    con.commit()
                else:
                    con.rollback()
                raise LeaseUnavailable("lease-expired-before-execution-start")
            if row["state"] == "ACTIVE":
                con.execute("UPDATE leases SET state='IN_FLIGHT' WHERE lease_id=? AND state='ACTIVE'", (body["lease_id"],))
            con.commit()
        except LeaseUnavailable:
            if con.in_transaction:
                con.rollback()
            raise
        except sqlite3.Error:
            if con.in_transaction:
                con.rollback()
            raise
        finally:
            con.close()

    def renew_in_flight(self, operation_id: str, action_sha256: str) -> dict[str, Any]:
        """Renew a pinned lease for a safe same-operation retry. The lease stays IN_FLIGHT."""
        con = self._connect()
        try:
            con.execute("BEGIN IMMEDIATE")
            row = con.execute("""SELECT * FROM leases WHERE operation_id=? AND action_sha256=?
                AND state='IN_FLIGHT' ORDER BY issued_at DESC LIMIT 1""",
                (operation_id, action_sha256)).fetchone()
            if row is None:
                con.rollback()
                raise LeaseUnavailable("no-pinned-lease-to-renew")
            now = float(self.clock())
            body = json.loads(row["body_json"])
            body["issued_at"] = now
            body["expires_at"] = now + self.lease_seconds
            token = {"body": body, "hmac_sha256": _token_mac(body, self._key)}
            con.execute("UPDATE leases SET body_json=?, token_json=?, issued_at=?, expires_at=? WHERE lease_id=? AND state='IN_FLIGHT'",
                        (canonical_bytes(body).decode("utf-8"), canonical_bytes(token).decode("utf-8"),
                         now, body["expires_at"], row["lease_id"]))
            con.commit()
            return token
        except LeaseUnavailable:
            if con.in_transaction:
                con.rollback()
            raise
        except sqlite3.Error:
            if con.in_transaction:
                con.rollback()
            raise
        finally:
            con.close()

    def verify_token(self, token: Any, operation_id: str, action_sha256: str) -> tuple[bool, str]:
        if not isinstance(token, Mapping) or set(token) != self.TOKEN_KEYS:
            return False, "invalid-lease-envelope"
        body, mac = token.get("body"), token.get("hmac_sha256")
        if not isinstance(body, Mapping) or set(body) != self.BODY_KEYS:
            return False, "invalid-lease-body"
        if not isinstance(mac, str) or len(mac) != 64:
            return False, "invalid-lease-authenticator"
        try:
            expected_mac = _token_mac(body, self._key)
            expiry, issued = float(body["expires_at"]), float(body["issued_at"])
        except (KeyError, TypeError, ValueError, OverflowError):
            return False, "invalid-lease-fields"
        if not hmac.compare_digest(mac, expected_mac):
            return False, "lease-authentication-failed"
        if body.get("schema_version") != "1.0":
            return False, "unsupported-lease-version"
        if body.get("operation_id") != operation_id or body.get("action_sha256") != action_sha256:
            return False, "lease-action-binding-mismatch"
        if not (issued <= float(self.clock()) < expiry):
            return False, "lease-expired-or-not-yet-valid"
        if not isinstance(body.get("evidence"), list) or not body["evidence"]:
            return False, "lease-has-no-evidence"
        return True, "ok"

    def active_token_for_operation(self, operation_id: str, action_sha256: str) -> dict[str, Any] | None:
        con = self._connect()
        try:
            now = float(self.clock())
            con.execute("UPDATE leases SET state='EXPIRED' WHERE state='ACTIVE' AND expires_at<=?", (now,))
            row = con.execute("""SELECT token_json FROM leases WHERE operation_id=? AND action_sha256=?
                AND (state='IN_FLIGHT' OR (state='ACTIVE' AND expires_at>?))
                ORDER BY issued_at DESC LIMIT 1""",
                (operation_id, action_sha256, now)).fetchone()
            return json.loads(row["token_json"]) if row else None
        finally:
            con.close()

    def token_for_operation(self, operation_id: str, action_sha256: str) -> dict[str, Any] | None:
        """Return the latest token even if expired, for lookup/recovery bookkeeping only."""
        con = self._connect()
        try:
            row = con.execute("SELECT token_json FROM leases WHERE operation_id=? AND action_sha256=? ORDER BY issued_at DESC LIMIT 1",
                              (operation_id, action_sha256)).fetchone()
            return json.loads(row["token_json"]) if row else None
        finally:
            con.close()

    def release(self, token: Mapping[str, Any]) -> None:
        body = token.get("body") if isinstance(token, Mapping) else None
        if not isinstance(body, Mapping) or not isinstance(body.get("lease_id"), str):
            return
        if not hmac.compare_digest(str(token.get("hmac_sha256", "")), _token_mac(body, self._key)):
            return
        con = self._connect()
        try:
            con.execute("UPDATE leases SET state='RELEASED' WHERE lease_id=? AND state IN ('ACTIVE','IN_FLIGHT')",
                        (body["lease_id"],))
        finally:
            con.close()

    def active_lease_count(self, key: str | None = None) -> int:
        con = self._connect()
        try:
            now = float(self.clock())
            if key is None:
                return int(con.execute("SELECT COUNT(*) FROM leases WHERE state='IN_FLIGHT' OR (state='ACTIVE' AND expires_at>?)", (now,)).fetchone()[0])
            return int(con.execute("""SELECT COUNT(*) FROM leases l JOIN lease_evidence le ON le.lease_id=l.lease_id
                WHERE le.evidence_key=? AND (l.state='IN_FLIGHT' OR (l.state='ACTIVE' AND l.expires_at>?))""", (key, now)).fetchone()[0])
        finally:
            con.close()


class SQLiteLeasedEffectProvider:
    """Mock remote provider; dedupe record and simulated business effect share one transaction."""
    supports_idempotency = True

    def __init__(self, db_path: str | Path, lease_authority: SQLiteEvidenceLeaseAuthority,
                 *, clock: Callable[[], float] = time.time):
        self.db_path = str(db_path)
        self.authority = lease_authority
        self.clock = clock
        self.drop_next_response = False
        self.before_lease_validation: Callable[[], None] | None = None
        self.before_effect_commit: Callable[[], None] | None = None
        self._init_db()

    def _connect(self) -> sqlite3.Connection:
        con = sqlite3.connect(self.db_path, timeout=10, isolation_level=None)
        con.row_factory = sqlite3.Row
        con.execute("PRAGMA busy_timeout=10000")
        return con

    def _init_db(self) -> None:
        con = self._connect()
        try:
            con.execute("PRAGMA journal_mode=WAL")
            con.execute("""CREATE TABLE IF NOT EXISTS effects (
                operation_id TEXT PRIMARY KEY, request_sha256 TEXT NOT NULL,
                payload_json TEXT NOT NULL, result_json TEXT NOT NULL, applied_at REAL NOT NULL)""")
        finally:
            con.close()

    def lookup(self, operation_id: str, payload: Mapping[str, Any]) -> dict[str, Any] | None:
        request_sha = sha256_json(payload)
        con = self._connect()
        try:
            row = con.execute("SELECT * FROM effects WHERE operation_id=?", (operation_id,)).fetchone()
            if row is None:
                return None
            if row["request_sha256"] != request_sha:
                raise IdempotencyConflict("operation ID already bound to another payload")
            return {**json.loads(row["result_json"]), "replayed": True}
        finally:
            con.close()

    def execute(self, operation_id: str, payload: Mapping[str, Any], lease_token: Mapping[str, Any]) -> dict[str, Any]:
        request_sha = sha256_json(payload)
        con = self._connect()
        try:
            con.execute("BEGIN IMMEDIATE")
            prior = con.execute("SELECT * FROM effects WHERE operation_id=?", (operation_id,)).fetchone()
            if prior is not None:
                if prior["request_sha256"] != request_sha:
                    con.rollback()
                    raise IdempotencyConflict("operation ID already bound to another payload")
                result = {**json.loads(prior["result_json"]), "replayed": True}
                con.commit()
                return result

            if self.before_lease_validation is not None:
                self.before_lease_validation()
            valid, reason = self.authority.verify_token(lease_token, operation_id, request_sha)
            if not valid:
                con.rollback()
                if reason == "lease-expired-or-not-yet-valid":
                    raise LeaseExpired(reason)
                raise LeaseRejected(reason)
            if self.before_effect_commit is not None:
                self.before_effect_commit()

            # Linearization point of the simulated remote effect. In a real
            # provider, the precondition must be evaluated as part of the same
            # transaction that commits its business mutation or under a provider
            # contract that guarantees the evidence lease remains valid.
            result = {"operation_id": operation_id, "request_sha256": request_sha,
                      "accepted": True, "lease_id": lease_token["body"]["lease_id"]}
            con.execute("INSERT INTO effects VALUES(?,?,?,?,?)",
                        (operation_id, request_sha, canonical_bytes(payload).decode("utf-8"),
                         canonical_bytes(result).decode("utf-8"), float(self.clock())))
            con.commit()
        except (LeaseRejected, IdempotencyConflict):
            if con.in_transaction:
                con.rollback()
            raise
        except sqlite3.Error:
            if con.in_transaction:
                con.rollback()
            raise
        finally:
            con.close()
        returned = {**result, "replayed": False}
        if self.drop_next_response:
            self.drop_next_response = False
            raise ResponseLost("provider committed effect and idempotency record, but response was lost")
        return returned

    def effect_count(self) -> int:
        con = self._connect()
        try:
            return int(con.execute("SELECT COUNT(*) FROM effects").fetchone()[0])
        finally:
            con.close()


class LeaseAwareEffectAdapter:
    """Broker-facing adapter: recover known results first, else lease before effect."""
    supports_idempotency = True

    def __init__(self, authority: SQLiteEvidenceLeaseAuthority, provider: SQLiteLeasedEffectProvider,
                 requirements: Sequence[Requirement], operation_lookup: Callable[[str], Mapping[str, Any] | None]):
        self.authority = authority
        self.provider = provider
        self.requirements = tuple(requirements)
        self.operation_lookup = operation_lookup
        self.before_acquire: Callable[[str, Mapping[str, Any]], None] | None = None
        self.after_acquire: Callable[[str, Mapping[str, Any]], None] | None = None

    def lookup(self, operation_id: str, payload: Mapping[str, Any]) -> dict[str, Any] | None:
        try:
            cached = self.provider.lookup(operation_id, payload)
        except IdempotencyConflict as exc:
            raise DefinitiveDispatchDenial("provider-idempotency-conflict") from exc
        if cached is not None:
            token = self.authority.token_for_operation(operation_id, sha256_json(payload))
            if token is not None:
                self.authority.release(token)
        return cached

    def _admitted_items(self, operation_id: str) -> list[Mapping[str, Any]]:
        op = self.operation_lookup(operation_id)
        if not op:
            raise LeaseUnavailable("operation-record-missing")
        try:
            token = json.loads(op["token_json"])
            items = token["body"]["evidence"]
        except (KeyError, TypeError, ValueError) as exc:
            raise LeaseUnavailable("persisted-admission-evidence-invalid") from exc
        if not isinstance(items, list):
            raise LeaseUnavailable("persisted-admission-evidence-invalid")
        return items

    def execute(self, operation_id: str, payload: Mapping[str, Any]) -> dict[str, Any]:
        action_sha = sha256_json(payload)
        # The broker already performs a lookup before current-policy/evidence
        # checks. Retain this second lookup to close the gap if a result commits
        # between the broker's first lookup and this call.
        cached = self.lookup(operation_id, payload)
        if cached is not None:
            return cached

        admitted_items = self._admitted_items(operation_id)
        if self.before_acquire is not None:
            self.before_acquire(operation_id, payload)
        existing = self.authority.active_token_for_operation(operation_id, action_sha)
        token = existing or self.authority.acquire_lease(
            operation_id, action_sha, self.requirements, admitted_items)
        if token["body"]["expires_at"] <= float(self.authority.clock()) and token["body"]["lease_id"]:
            # An IN_FLIGHT lease may outlive its initial token TTL; renew the signed
            # dispatch token without unlocking the evidence. An expired ACTIVE lease
            # has not been claimed yet, so it can be re-acquired after rechecking evidence.
            try:
                token = self.authority.renew_in_flight(operation_id, action_sha)
            except LeaseUnavailable:
                token = self.authority.acquire_lease(
                    operation_id, action_sha, self.requirements, admitted_items)
        if self.after_acquire is not None:
            self.after_acquire(operation_id, payload)
        self.authority.begin_execution(token)

        try:
            result = self.provider.execute(operation_id, payload, token)
        except ResponseLost:
            # Do not release: the remote effect may have committed. A retry first
            # looks up the provider's durable idempotency record, then releases.
            raise
        except LeaseExpired:
            # Provider transaction observed no previous effect and definitely
            # refused this attempt. Retire expired lease; make one fresh attempt
            # under a newly acquired lease if the admitted evidence still holds.
            retry_token = self.authority.renew_in_flight(operation_id, action_sha)
            self.authority.begin_execution(retry_token)
            try:
                result = self.provider.execute(operation_id, payload, retry_token)
            except ResponseLost:
                raise
            except Exception:
                raise
            else:
                self.authority.release(retry_token)
                return result
        except DefinitiveDispatchDenial:
            raise
        except Exception:
            # Outcome may be ambiguous. Keep the lease until expiration and retry
            # the same idempotency key; do not release on an unknown outcome.
            raise
        else:
            self.authority.release(token)
            return result
