"""Reference design for durable authorization-to-effect handoff.

This is an executable research prototype, not the production Lycheetah runtime.
It demonstrates atomic local witness consumption + outbox insertion, durable
idempotency at a cooperating effect provider, and conservative behavior when
that provider cannot guarantee idempotency.
"""
from __future__ import annotations

import hashlib
import hmac
import json
import math
import sqlite3
import threading
import time
import uuid
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Protocol


def canonical_bytes(value: Any) -> bytes:
    def normalize(v: Any) -> Any:
        if v is None or isinstance(v, (str, bool, int)):
            return v
        if isinstance(v, float):
            if not math.isfinite(v):
                raise ValueError("non-finite numbers are prohibited")
            return v
        if isinstance(v, Mapping):
            if any(not isinstance(k, str) for k in v):
                raise ValueError("object keys must be strings")
            return {k: normalize(x) for k, x in v.items()}
        if isinstance(v, Sequence) and not isinstance(v, (str, bytes, bytearray)):
            return [normalize(x) for x in v]
        raise ValueError(f"unsupported JSON value: {type(v).__name__}")
    return json.dumps(normalize(value), ensure_ascii=False, allow_nan=False,
                      sort_keys=True, separators=(",", ":")).encode("utf-8")


def sha256_json(value: Any) -> str:
    return hashlib.sha256(canonical_bytes(value)).hexdigest()


def valid_digest(value: Any) -> bool:
    return isinstance(value, str) and len(value) == 64 and all(c in "0123456789abcdef" for c in value)


@dataclass(frozen=True)
class Requirement:
    key: str
    mode: str = "EXACT"
    required_status: str = "PASS"
    required_subject_hash: str | None = None

    def __post_init__(self) -> None:
        if not isinstance(self.key, str) or not self.key:
            raise ValueError("requirement key must be non-empty text")
        if self.mode not in {"EXACT", "SUBJECT_STATUS"}:
            raise ValueError("unsupported requirement mode")
        if not isinstance(self.required_status, str) or not self.required_status:
            raise ValueError("required status must be non-empty text")
        if self.required_subject_hash is not None and not isinstance(self.required_subject_hash, str):
            raise ValueError("subject hash must be text or null")

    def to_dict(self) -> dict[str, Any]:
        return {"key": self.key, "mode": self.mode, "required_status": self.required_status,
                "required_subject_hash": self.required_subject_hash}


@dataclass(frozen=True)
class Evidence:
    key: str
    version: str
    subject_hash: str
    value_digest: str
    status: str

    def __post_init__(self) -> None:
        for field in ("key", "version", "subject_hash", "value_digest", "status"):
            value = getattr(self, field)
            if not isinstance(value, str) or not value:
                raise ValueError(f"evidence {field} must be non-empty text")

    def to_dict(self) -> dict[str, str]:
        return {"key": self.key, "version": self.version, "subject_hash": self.subject_hash,
                "value_digest": self.value_digest, "status": self.status}


class EvidenceProvider(Protocol):
    def get_evidence(self, key: str) -> Evidence | None: ...


class MutableEvidenceStore:
    def __init__(self, records: Sequence[Evidence] = ()):
        self._lock = threading.Lock()
        self._records = {r.key: r for r in records}

    def put(self, record: Evidence) -> None:
        with self._lock:
            self._records[record.key] = record

    def get_evidence(self, key: str) -> Evidence | None:
        with self._lock:
            return self._records.get(key)


@dataclass(frozen=True)
class Receipt:
    decision: str
    policy: Mapping[str, str]
    event_sha256: str
    digest: str

    def body_dict(self) -> dict[str, Any]:
        return {"decision": self.decision, "policy": dict(self.policy), "event_sha256": self.event_sha256}

    def verify(self) -> bool:
        return hmac.compare_digest(self.digest, sha256_json(self.body_dict()))


class Runtime(Protocol):
    policy: Mapping[str, str]
    def evaluate(self, event: Mapping[str, Any]) -> Receipt: ...


class DemoRuntime:
    """Synthetic adapter only; replace with the real AssuranceRuntime at integration."""
    def __init__(self, policy: Mapping[str, str], decision: str = "ALLOW"):
        self.policy = dict(policy)
        self.decision = decision

    def evaluate(self, event: Mapping[str, Any]) -> Receipt:
        event_sha = sha256_json(event)
        body = {"decision": self.decision, "policy": dict(self.policy), "event_sha256": event_sha}
        return Receipt(self.decision, dict(self.policy), event_sha, sha256_json(body))


@dataclass(frozen=True)
class BrokerResult:
    ok: bool
    reason: str
    operation_id: str | None = None
    state: str | None = None
    replayed: bool = False


class SimulatedProcessCrash(RuntimeError):
    """Fault-injection exception used to leave durable state at a crash boundary."""


class ResponseLost(RuntimeError):
    """Provider committed a side effect, but the response was lost after commit."""


class IdempotencyConflict(RuntimeError):
    pass


class DurableActionBroker:
    """Trusted issuance + one-use admission + transactional local outbox.

    The local SQLite DB is the atomic boundary for witness consumption and
    outbox insertion. The downstream provider is a separate failure domain.
    Automatic recovery is only enabled for a provider that declares and
    implements durable idempotency by key, with payload mismatch rejection.
    """
    ENVELOPE_KEYS = {"body", "hmac_sha256"}
    BODY_KEYS = {"schema_version", "witness_id", "event_sha256", "policy",
                 "admission_receipt_sha256", "requirements_sha256", "issued_at", "expires_at", "evidence"}

    def __init__(self, db_path: str | Path, signing_key: bytes, runtime: Runtime,
                 requirements: Sequence[Requirement], evidence_provider: EvidenceProvider,
                 *, clock: Callable[[], float] = time.time, ttl_seconds: int = 60):
        if not isinstance(signing_key, bytes) or len(signing_key) < 32:
            raise ValueError("signing key must contain at least 32 bytes")
        if not requirements:
            raise ValueError("trusted requirements must not be empty")
        if isinstance(ttl_seconds, bool) or not isinstance(ttl_seconds, int) or ttl_seconds < 1:
            raise ValueError("ttl_seconds must be a positive integer")
        self.db_path = str(db_path)
        self._key = signing_key
        self.runtime = runtime
        self.requirements = tuple(requirements)
        self.provider = evidence_provider
        self.clock = clock
        self.ttl_seconds = ttl_seconds
        self._requirements_sha = sha256_json([r.to_dict() for r in self.requirements])
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
            con.execute("""CREATE TABLE IF NOT EXISTS issued (
                witness_id TEXT PRIMARY KEY, body_sha256 TEXT NOT NULL, event_sha256 TEXT NOT NULL,
                policy_sha256 TEXT NOT NULL, receipt_sha256 TEXT NOT NULL,
                requirements_sha256 TEXT NOT NULL, expires_at REAL NOT NULL, consumed_at REAL)""")
            con.execute("""CREATE TABLE IF NOT EXISTS outbox (
                operation_id TEXT PRIMARY KEY, witness_id TEXT NOT NULL UNIQUE,
                event_sha256 TEXT NOT NULL, action_json TEXT NOT NULL, action_sha256 TEXT NOT NULL,
                token_json TEXT NOT NULL,
                state TEXT NOT NULL CHECK(state IN ('PENDING','IN_FLIGHT','DONE','RECONCILE')),
                attempts INTEGER NOT NULL DEFAULT 0, created_at REAL NOT NULL,
                updated_at REAL NOT NULL, result_json TEXT, last_error TEXT,
                FOREIGN KEY(witness_id) REFERENCES issued(witness_id))""")
        finally:
            con.close()

    def _requirements_valid(self, evidence_items: Any) -> bool:
        if not isinstance(evidence_items, list) or len(evidence_items) != len(self.requirements):
            return False
        for expected, item in zip(self.requirements, evidence_items, strict=True):
            if not isinstance(item, Mapping) or set(item) != {"requirement", "admitted"}:
                return False
            if item["requirement"] != expected.to_dict():
                return False
            rec = item["admitted"]
            if not isinstance(rec, Mapping) or set(rec) != {"key", "version", "subject_hash", "value_digest", "status"}:
                return False
            if rec["key"] != expected.key or rec["status"] != expected.required_status:
                return False
            if expected.required_subject_hash is not None and rec["subject_hash"] != expected.required_subject_hash:
                return False
        return True

    @staticmethod
    def _satisfies(req: Requirement, rec: Evidence) -> bool:
        if rec.key != req.key or rec.status != req.required_status:
            return False
        return req.required_subject_hash is None or rec.subject_hash == req.required_subject_hash

    def admit(self, event: Mapping[str, Any]) -> tuple[BrokerResult, dict[str, Any] | None]:
        try:
            if not isinstance(event, Mapping) or not event:
                return BrokerResult(False, "invalid-event"), None
            event_copy = json.loads(canonical_bytes(dict(event)).decode("utf-8"))
            event_sha = sha256_json(event_copy)
            receipt = self.runtime.evaluate(event_copy)
            if not receipt.verify() or receipt.event_sha256 != event_sha:
                return BrokerResult(False, "invalid-admission-receipt"), None
            if receipt.decision != "ALLOW":
                return BrokerResult(False, "runtime-not-allow-at-admission"), None
            policy = dict(receipt.policy)
            if policy != dict(self.runtime.policy) or not valid_digest(policy.get("sha256")):
                return BrokerResult(False, "invalid-policy-identity"), None
            bound = []
            for req in self.requirements:
                rec = self.provider.get_evidence(req.key)
                if rec is None or not self._satisfies(req, rec):
                    return BrokerResult(False, f"evidence-unsatisfied:{req.key}"), None
                bound.append({"requirement": req.to_dict(), "admitted": rec.to_dict()})
            now = float(self.clock())
            wid = str(uuid.uuid4())
            body = {"schema_version":"1.1", "witness_id":wid, "event_sha256":event_sha,
                    "policy":policy, "admission_receipt_sha256":receipt.digest,
                    "requirements_sha256":self._requirements_sha, "issued_at":now,
                    "expires_at":now+self.ttl_seconds, "evidence":bound}
            body_sha = sha256_json(body)
            mac = hmac.new(self._key, body_sha.encode("ascii"), hashlib.sha256).hexdigest()
            con = self._connect()
            try:
                con.execute("INSERT INTO issued VALUES (?,?,?,?,?,?,?,NULL)",
                            (wid, body_sha, event_sha, policy["sha256"], receipt.digest,
                             self._requirements_sha, now+self.ttl_seconds))
            finally:
                con.close()
            return BrokerResult(True,"admitted",wid), {"body":body,"hmac_sha256":mac}
        except Exception:
            return BrokerResult(False,"admission-failed-closed"), None

    def _verify_token(self, token: Any, event: Mapping[str, Any], *,
                      allow_expired: bool = False,
                      allow_policy_change: bool = False) -> tuple[dict[str, Any] | None, str]:
        if not isinstance(token, Mapping) or set(token) != self.ENVELOPE_KEYS:
            return None, "invalid-token-envelope"
        body, mac = token.get("body"), token.get("hmac_sha256")
        if not isinstance(body, Mapping) or set(body) != self.BODY_KEYS:
            return None, "invalid-witness-body"
        if not isinstance(mac, str) or not valid_digest(mac):
            return None, "invalid-witness-authenticator"
        try:
            body = json.loads(canonical_bytes(dict(body)).decode("utf-8"))
            body_sha = sha256_json(body)
            event_copy = json.loads(canonical_bytes(dict(event)).decode("utf-8"))
            event_sha = sha256_json(event_copy)
        except Exception:
            return None, "invalid-json-contract"
        expected = hmac.new(self._key, body_sha.encode("ascii"), hashlib.sha256).hexdigest()
        if not hmac.compare_digest(mac, expected):
            return None, "witness-authentication-failed"
        if body["schema_version"] != "1.1":
            return None, "unsupported-witness-version"
        if body["event_sha256"] != event_sha:
            return None, "event-changed-after-admission"
        if body["requirements_sha256"] != self._requirements_sha:
            return None, "trusted-requirements-changed"
        if not isinstance(body["policy"], dict) or not valid_digest(body["policy"].get("sha256")):
            return None, "invalid-policy-identity"
        if not allow_policy_change and body["policy"] != dict(self.runtime.policy):
            return None, "policy-changed-after-admission"
        if not valid_digest(body["admission_receipt_sha256"]):
            return None, "invalid-admission-receipt-reference"
        expiry = body["expires_at"]
        if isinstance(expiry, bool) or not isinstance(expiry, (int,float)) or not math.isfinite(expiry):
            return None, "invalid-expiry"
        if not allow_expired and float(self.clock()) > expiry:
            return None, "witness-expired"
        if not self._requirements_valid(body["evidence"]):
            return None, "witness-requirement-or-evidence-invalid"
        return {**body, "_body_sha256": body_sha}, "ok"

    def _existing_operation(self, body: Mapping[str, Any], event: Mapping[str, Any]) -> BrokerResult | None:
        """Recover an already committed enqueue after the caller lost its ACK.

        This path authenticates the exact signed token and event first, then only
        returns an existing record; it never authorizes a new action. It remains
        available after token expiry or policy drift so clients can discover that
        a committed operation now needs reconciliation.
        """
        con = self._connect()
        try:
            issued = con.execute("SELECT * FROM issued WHERE witness_id=?", (body["witness_id"],)).fetchone()
            existing = con.execute("SELECT * FROM outbox WHERE witness_id=?", (body["witness_id"],)).fetchone()
            if existing is None:
                return None
            body_sha = body["_body_sha256"]
            event_sha = sha256_json(event)
            if (issued is None or issued["body_sha256"] != body_sha or
                    issued["event_sha256"] != event_sha or
                    issued["requirements_sha256"] != self._requirements_sha or
                    existing["event_sha256"] != event_sha or
                    existing["action_sha256"] != event_sha or
                    sha256_json(json.loads(existing["action_json"])) != event_sha):
                return BrokerResult(False, "existing-operation-integrity-failed",
                                    existing["operation_id"], "RECONCILE")
            return BrokerResult(True, "operation-already-enqueued", existing["operation_id"],
                                existing["state"], True)
        except (sqlite3.Error, TypeError, ValueError, KeyError):
            return BrokerResult(False, "existing-operation-lookup-failed-closed")
        finally:
            con.close()

    def authorize_and_enqueue(self, token: Any, event: Mapping[str, Any], *,
                              crash_before_commit: bool = False,
                              crash_after_commit: bool = False) -> BrokerResult:
        # Authenticate the token and bind it to the requested event first. Permit
        # an expired or stale-policy token only for lookup of an already committed
        # operation; it is not allowed to create a new outbox item.
        body, reason = self._verify_token(token, event, allow_expired=True, allow_policy_change=True)
        if body is None:
            return BrokerResult(False, reason)
        existing = self._existing_operation(body, event)
        if existing is not None:
            return existing
        if float(self.clock()) > float(body["expires_at"]):
            return BrokerResult(False, "witness-expired")
        if body["policy"] != dict(self.runtime.policy):
            return BrokerResult(False, "policy-changed-after-admission")
        try:
            event_copy = json.loads(canonical_bytes(dict(event)).decode("utf-8"))
            event_sha = sha256_json(event_copy)
            receipt = self.runtime.evaluate(event_copy)
            if not receipt.verify() or receipt.event_sha256 != event_sha:
                return BrokerResult(False, "invalid-current-receipt")
            if receipt.decision != "ALLOW":
                return BrokerResult(False, "runtime-not-allow-at-enqueue")
            if dict(receipt.policy) != dict(self.runtime.policy) or dict(receipt.policy) != body["policy"]:
                return BrokerResult(False, "policy-changed-at-enqueue")
        except Exception:
            return BrokerResult(False, "runtime-failed-closed")

        # Read the external evidence before opening the local write transaction.
        # This avoids holding SQLite's writer lock across a remote/provider call.
        # It still cannot make the external snapshot atomic with the local commit.
        for req, bound in zip(self.requirements, body["evidence"], strict=True):
            current = self.provider.get_evidence(req.key)
            if current is None:
                return BrokerResult(False, f"evidence-missing-at-enqueue:{req.key}")
            admitted = bound["admitted"]
            if req.mode == "EXACT":
                if current.to_dict() != admitted:
                    return BrokerResult(False, f"evidence-changed-at-enqueue:{req.key}")
            elif not self._satisfies(req, current):
                return BrokerResult(False, f"evidence-unsatisfied-at-enqueue:{req.key}")

        now = float(self.clock())
        action_json = canonical_bytes(event_copy).decode("utf-8")
        action_sha = sha256_json(event_copy)
        con = self._connect()
        try:
            con.execute("BEGIN IMMEDIATE")
            row = con.execute("SELECT * FROM issued WHERE witness_id=?", (body["witness_id"],)).fetchone()
            if row is None:
                con.rollback()
                return BrokerResult(False,"witness-not-issued-by-this-broker")
            if (row["body_sha256"] != body["_body_sha256"] or row["event_sha256"] != event_sha or
                row["policy_sha256"] != body["policy"].get("sha256") or
                row["receipt_sha256"] != body["admission_receipt_sha256"] or
                row["requirements_sha256"] != self._requirements_sha):
                con.rollback()
                return BrokerResult(False,"witness-registry-mismatch")
            existing = con.execute("SELECT * FROM outbox WHERE witness_id=?", (body["witness_id"],)).fetchone()
            if existing is not None:
                con.rollback()
                if existing["action_sha256"] != action_sha:
                    return BrokerResult(False,"existing-operation-payload-mismatch")
                return BrokerResult(True,"operation-already-enqueued",existing["operation_id"],existing["state"],True)
            if row["consumed_at"] is not None:
                con.rollback()
                return BrokerResult(False,"witness-already-consumed")
            if now > float(row["expires_at"]):
                con.rollback()
                return BrokerResult(False,"witness-expired")

            operation_id = str(uuid.uuid4())
            update = con.execute("UPDATE issued SET consumed_at=? WHERE witness_id=? AND consumed_at IS NULL",
                                 (now,body["witness_id"]))
            if update.rowcount != 1:
                con.rollback()
                return BrokerResult(False,"witness-already-consumed")
            con.execute("""INSERT INTO outbox
                (operation_id,witness_id,event_sha256,action_json,action_sha256,token_json,state,attempts,created_at,updated_at,result_json,last_error)
                VALUES (?,?,?,?,?,?,'PENDING',0,?,?,NULL,NULL)""",
                (operation_id,body["witness_id"],event_sha,action_json,action_sha,
                 canonical_bytes(dict(token)).decode("utf-8"),now,now))
            if crash_before_commit:
                raise SimulatedProcessCrash("crash before local commit; transaction should roll back")
            con.commit()
        except SimulatedProcessCrash:
            con.rollback()
            raise
        except sqlite3.Error:
            con.rollback()
            return BrokerResult(False,"local-transaction-failed-closed")
        finally:
            con.close()
        if crash_after_commit:
            raise SimulatedProcessCrash("local authorization/outbox committed; client acknowledgement lost")
        return BrokerResult(True,"authorized-and-enqueued",operation_id,"PENDING")

    def get_operation(self, operation_id: str) -> dict[str, Any] | None:
        con = self._connect()
        try:
            row = con.execute("SELECT * FROM outbox WHERE operation_id=?", (operation_id,)).fetchone()
            return dict(row) if row else None
        finally:
            con.close()

    def dispatch_one(self, operation_id: str, provider: Any, *,
                     crash_after_provider_commit: bool = False) -> BrokerResult:
        if not getattr(provider,"supports_idempotency",False):
            con = self._connect()
            try:
                con.execute("BEGIN IMMEDIATE")
                row=con.execute("SELECT state FROM outbox WHERE operation_id=?",(operation_id,)).fetchone()
                if row is None:
                    con.rollback(); return BrokerResult(False,"operation-not-found",operation_id)
                if row["state"] != "DONE":
                    con.execute("UPDATE outbox SET state='RECONCILE', last_error=?, updated_at=? WHERE operation_id=?",
                                ("provider-lacks-durable-idempotency",float(self.clock()),operation_id))
                con.commit()
                return BrokerResult(False,"provider-idempotency-required",operation_id,"RECONCILE")
            except sqlite3.Error:
                con.rollback(); return BrokerResult(False,"local-ledger-failed-closed",operation_id)
            finally:
                con.close()

        con = self._connect()
        try:
            con.execute("BEGIN IMMEDIATE")
            row = con.execute("SELECT * FROM outbox WHERE operation_id=?",(operation_id,)).fetchone()
            if row is None:
                con.rollback(); return BrokerResult(False,"operation-not-found",operation_id)
            state=row["state"]
            if state == "DONE":
                con.rollback(); return BrokerResult(True,"already-done",operation_id,"DONE",True)
            if state == "RECONCILE":
                con.rollback(); return BrokerResult(False,"manual-reconciliation-required",operation_id,"RECONCILE")
            if state == "PENDING":
                con.execute("UPDATE outbox SET state='IN_FLIGHT', attempts=attempts+1, updated_at=? WHERE operation_id=?",
                            (float(self.clock()),operation_id))
            elif state == "IN_FLIGHT":
                con.execute("UPDATE outbox SET attempts=attempts+1, updated_at=? WHERE operation_id=?",
                            (float(self.clock()),operation_id))
            con.commit()
            try:
                action=json.loads(row["action_json"])
                stored_token=json.loads(row["token_json"])
            except (TypeError, ValueError):
                action=None
                stored_token=None
            payload_sha=row["action_sha256"]
            stored_event_sha=row["event_sha256"]
            witness_id=row["witness_id"]
        except sqlite3.Error:
            con.rollback(); return BrokerResult(False,"local-ledger-failed-closed",operation_id)
        finally:
            con.close()

        # Validate the persisted intent before any remote side effect. Checking
        # only the provider response would detect corruption too late.
        if (not isinstance(action, Mapping) or sha256_json(action) != payload_sha or
                sha256_json(action) != stored_event_sha):
            con = self._connect()
            try:
                con.execute("UPDATE outbox SET state='RECONCILE', last_error=?, updated_at=? WHERE operation_id=? AND state='IN_FLIGHT'",
                            ("persisted-action-digest-mismatch",float(self.clock()),operation_id))
            finally:
                con.close()
            return BrokerResult(False,"persisted-action-digest-mismatch",operation_id,"RECONCILE")

        # Revalidate the saved authorization, policy and evidence immediately
        # before dispatch. This narrows but cannot eliminate cross-system TOCTOU.
        _, token_reason = self._verify_token(stored_token, action)
        if token_reason != "ok":
            con = self._connect()
            try:
                con.execute("UPDATE outbox SET state='RECONCILE', last_error=?, updated_at=? WHERE operation_id=? AND state='IN_FLIGHT'",
                            ("dispatch-"+token_reason,float(self.clock()),operation_id))
            finally:
                con.close()
            return BrokerResult(False,"dispatch-"+token_reason,operation_id,"RECONCILE")
        try:
            current_receipt = self.runtime.evaluate(action)
            runtime_ok = (current_receipt.verify() and
                          current_receipt.event_sha256 == stored_event_sha and
                          current_receipt.decision == "ALLOW" and
                          dict(current_receipt.policy) == dict(self.runtime.policy))
        except Exception:
            runtime_ok = False
        if not runtime_ok:
            con = self._connect()
            try:
                con.execute("UPDATE outbox SET state='RECONCILE', last_error=?, updated_at=? WHERE operation_id=? AND state='IN_FLIGHT'",
                            ("dispatch-runtime-not-allow",float(self.clock()),operation_id))
            finally:
                con.close()
            return BrokerResult(False,"dispatch-runtime-not-allow",operation_id,"RECONCILE")
        saved_evidence = stored_token["body"]["evidence"]
        for req, bound in zip(self.requirements, saved_evidence, strict=True):
            current = self.provider.get_evidence(req.key)
            admitted = bound["admitted"]
            good = (current is not None and
                    ((current.to_dict() == admitted) if req.mode == "EXACT" else self._satisfies(req, current)))
            if not good:
                con = self._connect()
                try:
                    con.execute("UPDATE outbox SET state='RECONCILE', last_error=?, updated_at=? WHERE operation_id=? AND state='IN_FLIGHT'",
                                ("dispatch-evidence-changed:"+req.key,float(self.clock()),operation_id))
                finally:
                    con.close()
                return BrokerResult(False,"dispatch-evidence-changed:"+req.key,operation_id,"RECONCILE")

        try:
            provider_result = provider.execute(operation_id, action)
        except Exception as exc:
            # Ambiguous provider outcome is recoverable only by replaying the same
            # idempotency key against a provider with the documented contract.
            con = self._connect()
            try:
                con.execute("UPDATE outbox SET last_error=?, updated_at=? WHERE operation_id=? AND state='IN_FLIGHT'",
                            (type(exc).__name__,float(self.clock()),operation_id))
            finally:
                con.close()
            return BrokerResult(False,"provider-outcome-unknown-safe-retry",operation_id,"IN_FLIGHT")
        if crash_after_provider_commit:
            raise SimulatedProcessCrash("provider committed; broker died before local acknowledgement")
        try:
            if (provider_result.get("request_sha256") != payload_sha or
                    provider_result.get("operation_id") != operation_id or
                    provider_result.get("accepted") is not True):
                return BrokerResult(False,"provider-result-payload-mismatch",operation_id,"IN_FLIGHT")
            con = self._connect()
            try:
                con.execute("BEGIN IMMEDIATE")
                con.execute("UPDATE outbox SET state='DONE', result_json=?, last_error=NULL, updated_at=? WHERE operation_id=? AND state='IN_FLIGHT'",
                            (canonical_bytes(provider_result).decode("utf-8"),float(self.clock()),operation_id))
                con.commit()
            finally:
                con.close()
            return BrokerResult(True,"effect-confirmed",operation_id,"DONE",bool(provider_result.get("replayed")))
        except sqlite3.Error:
            return BrokerResult(False,"provider-effect-confirmed-local-ack-failed",operation_id,"IN_FLIGHT")


class SQLiteIdempotentProvider:
    """Simulated remote provider whose dedupe key and effect share one DB txn.

    A real adapter only qualifies if the actual business mutation and durable
    idempotency record are atomic in the provider's own consistency boundary.
    """
    supports_idempotency = True

    def __init__(self, db_path: str | Path):
        self.db_path = str(db_path)
        self.drop_next_response = False
        self._init_db()

    def _connect(self) -> sqlite3.Connection:
        con=sqlite3.connect(self.db_path,timeout=10,isolation_level=None)
        con.row_factory=sqlite3.Row
        con.execute("PRAGMA busy_timeout=10000")
        return con

    def _init_db(self) -> None:
        con=self._connect()
        try:
            con.execute("PRAGMA journal_mode=WAL")
            con.execute("""CREATE TABLE IF NOT EXISTS idempotency (
                operation_id TEXT PRIMARY KEY, request_sha256 TEXT NOT NULL, result_json TEXT NOT NULL)""")
            con.execute("""CREATE TABLE IF NOT EXISTS effects (
                operation_id TEXT PRIMARY KEY, request_sha256 TEXT NOT NULL, payload_json TEXT NOT NULL,
                applied_at REAL NOT NULL)""")
        finally: con.close()

    def execute(self, operation_id: str, payload: Mapping[str, Any]) -> dict[str, Any]:
        request_sha=sha256_json(payload)
        con=self._connect()
        replayed=False
        try:
            con.execute("BEGIN IMMEDIATE")
            prior=con.execute("SELECT * FROM idempotency WHERE operation_id=?",(operation_id,)).fetchone()
            if prior is not None:
                if prior["request_sha256"] != request_sha:
                    con.rollback()
                    raise IdempotencyConflict("same operation_id was reused with a different payload")
                result=json.loads(prior["result_json"])
                replayed=True
                con.commit()
            else:
                result={"operation_id":operation_id,"request_sha256":request_sha,"accepted":True}
                con.execute("INSERT INTO effects VALUES (?,?,?,?)",
                            (operation_id,request_sha,canonical_bytes(payload).decode("utf-8"),time.time()))
                con.execute("INSERT INTO idempotency VALUES (?,?,?)",
                            (operation_id,request_sha,canonical_bytes(result).decode("utf-8")))
                con.commit()
        finally: con.close()
        result={**result,"replayed":replayed}
        if self.drop_next_response:
            self.drop_next_response=False
            raise ResponseLost("provider committed effect and dedupe record, but response was lost")
        return result

    def effect_count(self) -> int:
        con=self._connect()
        try: return int(con.execute("SELECT COUNT(*) FROM effects").fetchone()[0])
        finally: con.close()

    def effect_payloads(self) -> list[dict[str, Any]]:
        con=self._connect()
        try: return [json.loads(r[0]) for r in con.execute("SELECT payload_json FROM effects ORDER BY applied_at, operation_id")]
        finally: con.close()


class NonIdempotentProvider:
    """Unsafe baseline: every request applies again, with no durable dedupe."""
    supports_idempotency = False
    def __init__(self): self.effects: list[dict[str, Any]]=[]
    def execute(self, operation_id: str, payload: Mapping[str, Any]) -> dict[str, Any]:
        self.effects.append(dict(payload))
        return {"operation_id":operation_id,"request_sha256":sha256_json(payload),"accepted":True}


def default_policy() -> dict[str, str]:
    return {"id":"lycheetah.test-policy","version":"1","sha256":"a"*64}
