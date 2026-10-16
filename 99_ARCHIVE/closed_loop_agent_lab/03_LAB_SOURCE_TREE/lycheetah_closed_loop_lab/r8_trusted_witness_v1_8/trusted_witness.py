"""Reference design for provenance-bound, one-use admission witnesses.

This is a standalone prototype inspired by the inspected Lycheetah Assurance
FinalityGate contract. It is NOT the upstream implementation and is not a
production-ready effect broker. See README.md for the threat model and limits.
"""
from __future__ import annotations

import hashlib
import hmac
import json
import math
import sqlite3
import time
import uuid
from collections.abc import Mapping as MappingABC, Sequence as SequenceABC
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Mapping, Protocol


def _jsonable(value: Any) -> Any:
    """Match the project's strict JSON value rules for this prototype."""
    if value is None or isinstance(value, (str, bool, int)):
        return value
    if isinstance(value, float):
        if not math.isfinite(value):
            raise ValueError("non-finite numbers are not valid JSON contract values")
        return value
    if isinstance(value, MappingABC):
        out = {}
        for key, item in value.items():
            if not isinstance(key, str):
                raise ValueError("object keys must be strings")
            out[key] = _jsonable(item)
        return out
    if isinstance(value, SequenceABC) and not isinstance(value, (str, bytes, bytearray)):
        return [_jsonable(item) for item in value]
    raise ValueError(f"unsupported JSON contract type: {type(value).__name__}")


def canonical_bytes(value: Any) -> bytes:
    return json.dumps(_jsonable(value), ensure_ascii=False, allow_nan=False, sort_keys=True,
                      separators=(",", ":")).encode("utf-8")


def sha256_json(value: Any) -> str:
    return hashlib.sha256(canonical_bytes(value)).hexdigest()


def _is_sha256(value: Any) -> bool:
    return (isinstance(value, str) and len(value) == 64 and
            all(c in "0123456789abcdef" for c in value))


@dataclass(frozen=True)
class EvidenceRequirement:
    key: str
    mode: str = "SUBJECT_STATUS"  # EXACT or SUBJECT_STATUS
    required_status: str = "PASS"
    required_subject_hash: str | None = None

    def __post_init__(self) -> None:
        if not isinstance(self.key, str) or not self.key:
            raise ValueError("requirement key must be non-empty text")
        if self.mode not in ("EXACT", "SUBJECT_STATUS"):
            raise ValueError("requirement mode must be EXACT or SUBJECT_STATUS")
        if not isinstance(self.required_status, str) or not self.required_status:
            raise ValueError("required_status must be non-empty text")
        if self.required_subject_hash is not None and (
            not isinstance(self.required_subject_hash, str) or not self.required_subject_hash
        ):
            raise ValueError("required_subject_hash must be non-empty text or null")

    def to_dict(self) -> dict[str, Any]:
        return {"key": self.key, "mode": self.mode,
                "required_status": self.required_status,
                "required_subject_hash": self.required_subject_hash}


@dataclass(frozen=True)
class EvidenceRecord:
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
        return {"key": self.key, "version": self.version,
                "subject_hash": self.subject_hash, "value_digest": self.value_digest,
                "status": self.status}


class EvidenceProvider(Protocol):
    def get_evidence(self, key: str) -> EvidenceRecord | None: ...


@dataclass(frozen=True)
class DecisionReceipt:
    """Tiny adapter contract used in tests; replace with the real runtime receipt."""
    decision: str
    policy: Mapping[str, str]
    event_sha256: str
    digest: str

    def body_dict(self) -> dict[str, Any]:
        return {"decision": self.decision, "policy": dict(self.policy),
                "event_sha256": self.event_sha256}

    def verify(self) -> bool:
        return hmac.compare_digest(self.digest, sha256_json(self.body_dict()))


class Runtime(Protocol):
    policy: Mapping[str, str]
    def evaluate(self, event: Mapping[str, Any]) -> DecisionReceipt: ...


class ToyRuntime:
    """Test runtime only. Production adapter must call AssuranceRuntime itself."""
    def __init__(self, policy: Mapping[str, str], decision: str = "ALLOW"):
        self.policy = dict(policy)
        self.decision = decision

    def evaluate(self, event: Mapping[str, Any]) -> DecisionReceipt:
        body = {"decision": self.decision, "policy": dict(self.policy),
                "event_sha256": sha256_json(event)}
        return DecisionReceipt(self.decision, dict(self.policy), body["event_sha256"],
                              sha256_json(body))


@dataclass(frozen=True)
class GateResult:
    ready: bool
    reason: str
    witness_id: str | None = None


class TrustedWitnessGate:
    """HMAC-authenticated witness plus durable registry and atomic one-use consume.

    Security boundary: `required_evidence` and `runtime` are configured by the
    trusted host. Callers cannot select weaker requirements per finalization.
    The SQLite database must be protected against untrusted writes.
    """
    TOKEN_KEYS = {"body", "hmac_sha256"}
    BODY_KEYS = {"schema_version", "witness_id", "event_sha256", "policy",
                 "admission_receipt_sha256", "requirements_sha256", "issued_at",
                 "expires_at", "evidence"}

    def __init__(self, db_path: str | Path, signing_key: bytes, runtime: Runtime,
                 required_evidence: tuple[EvidenceRequirement, ...],
                 provider: EvidenceProvider, *, clock: Callable[[], float] = time.time,
                 ttl_seconds: int = 60):
        if not isinstance(signing_key, bytes) or len(signing_key) < 32:
            raise ValueError("signing key must be at least 32 bytes")
        if not isinstance(ttl_seconds, int) or isinstance(ttl_seconds, bool) or ttl_seconds < 1:
            raise ValueError("ttl_seconds must be a positive integer")
        if not required_evidence:
            raise ValueError("trusted required_evidence must not be empty")
        self.db_path = str(db_path)
        self._key = signing_key
        self.runtime = runtime
        self.required_evidence = tuple(required_evidence)
        self.provider = provider
        self.clock = clock
        self.ttl_seconds = ttl_seconds
        self._requirements_sha = sha256_json([r.to_dict() for r in self.required_evidence])
        self._init_db()

    def _connect(self) -> sqlite3.Connection:
        con = sqlite3.connect(self.db_path, timeout=10.0, isolation_level=None)
        con.row_factory = sqlite3.Row
        con.execute("PRAGMA busy_timeout=10000")
        return con

    def _init_db(self) -> None:
        con = self._connect()
        try:
            con.execute("""CREATE TABLE IF NOT EXISTS issued_witnesses (
                witness_id TEXT PRIMARY KEY,
                body_sha256 TEXT NOT NULL,
                event_sha256 TEXT NOT NULL,
                policy_sha256 TEXT NOT NULL,
                admission_receipt_sha256 TEXT NOT NULL,
                requirements_sha256 TEXT NOT NULL,
                expires_at REAL NOT NULL,
                consumed_at REAL NULL
            )""")
        finally:
            con.close()

    def admit(self, event: Mapping[str, Any]) -> tuple[GateResult, dict[str, Any] | None]:
        if not isinstance(event, Mapping) or not event:
            return GateResult(False, "invalid-event"), None
        try:
            event_copy = json.loads(canonical_bytes(dict(event)).decode("utf-8"))
            event_sha = sha256_json(event_copy)
            receipt = self.runtime.evaluate(event_copy)
            if not receipt.verify():
                return GateResult(False, "admission-receipt-invalid"), None
            if receipt.event_sha256 != event_sha:
                return GateResult(False, "admission-receipt-event-mismatch"), None
            if receipt.decision != "ALLOW":
                return GateResult(False, "runtime-not-allow-at-admission"), None
            policy = dict(receipt.policy)
            if policy != dict(self.runtime.policy) or not _is_sha256(policy.get("sha256")):
                return GateResult(False, "invalid-policy-identity"), None

            bound = []
            for requirement in self.required_evidence:
                record = self.provider.get_evidence(requirement.key)
                if record is None or not self._satisfies(requirement, record):
                    return GateResult(False, f"required-evidence-unsatisfied:{requirement.key}"), None
                bound.append({"requirement": requirement.to_dict(), "admitted": record.to_dict()})

            now = float(self.clock())
            witness_id = str(uuid.uuid4())
            body = {"schema_version": "1.0", "witness_id": witness_id,
                    "event_sha256": event_sha, "policy": policy,
                    "admission_receipt_sha256": receipt.digest,
                    "requirements_sha256": self._requirements_sha,
                    "issued_at": now, "expires_at": now + self.ttl_seconds,
                    "evidence": bound}
            body_sha = sha256_json(body)
            signature = hmac.new(self._key, body_sha.encode("ascii"), hashlib.sha256).hexdigest()
            con = self._connect()
            try:
                con.execute("INSERT INTO issued_witnesses VALUES (?, ?, ?, ?, ?, ?, ?, NULL)",
                    (witness_id, body_sha, event_sha, policy["sha256"], receipt.digest,
                     self._requirements_sha, now + self.ttl_seconds))
            finally:
                con.close()
            return GateResult(True, "admitted", witness_id), {"body": body, "hmac_sha256": signature}
        except Exception:
            return GateResult(False, "admission-failed-closed"), None

    @staticmethod
    def _satisfies(requirement: EvidenceRequirement, record: EvidenceRecord) -> bool:
        if record.key != requirement.key:
            return False
        if requirement.mode == "EXACT":
            # At admission, records are accepted only when the stated predicate also holds.
            return (record.status == requirement.required_status and
                    (requirement.required_subject_hash is None or
                     record.subject_hash == requirement.required_subject_hash))
        return (record.status == requirement.required_status and
                (requirement.required_subject_hash is None or
                 record.subject_hash == requirement.required_subject_hash))

    def finalize(self, token: Any, event: Mapping[str, Any]) -> GateResult:
        if not isinstance(token, Mapping) or set(token) != self.TOKEN_KEYS:
            return GateResult(False, "invalid-token-envelope")
        body, signature = token.get("body"), token.get("hmac_sha256")
        if not isinstance(body, Mapping) or set(body) != self.BODY_KEYS:
            return GateResult(False, "invalid-witness-body")
        if not isinstance(signature, str) or not _is_sha256(signature):
            return GateResult(False, "invalid-witness-authenticator")
        try:
            body_dict = dict(body)
            body_sha = sha256_json(body_dict)
        except (TypeError, ValueError, OverflowError):
            return GateResult(False, "invalid-witness-encoding")
        expected_mac = hmac.new(self._key, body_sha.encode("ascii"), hashlib.sha256).hexdigest()
        if not hmac.compare_digest(signature, expected_mac):
            return GateResult(False, "witness-authentication-failed")
        witness_id = body_dict.get("witness_id")
        if not isinstance(witness_id, str):
            return GateResult(False, "invalid-witness-id")
        expires = body_dict.get("expires_at")
        if isinstance(expires, bool) or not isinstance(expires, (int, float)) or not math.isfinite(expires):
            return GateResult(False, "invalid-expiry")
        try:
            event_copy = json.loads(canonical_bytes(dict(event)).decode("utf-8"))
            event_sha = sha256_json(event_copy)
        except (TypeError, ValueError, OverflowError):
            return GateResult(False, "invalid-event")
        if body_dict.get("schema_version") != "1.0":
            return GateResult(False, "unsupported-witness-version")
        if body_dict.get("event_sha256") != event_sha:
            return GateResult(False, "event-changed-after-admission")
        if body_dict.get("requirements_sha256") != self._requirements_sha:
            return GateResult(False, "trusted-requirements-changed")
        if body_dict.get("policy") != dict(self.runtime.policy):
            return GateResult(False, "policy-changed-after-admission")
        if not _is_sha256(body_dict.get("admission_receipt_sha256")):
            return GateResult(False, "invalid-admission-receipt-reference")
        evidence = body_dict.get("evidence")
        if not isinstance(evidence, list) or len(evidence) != len(self.required_evidence):
            return GateResult(False, "witness-evidence-shape-mismatch")
        if any(not isinstance(item, Mapping) for item in evidence):
            return GateResult(False, "invalid-bound-evidence")
        for item in evidence:
            if set(item) != {"requirement", "admitted"}:
                return GateResult(False, "invalid-bound-evidence")


        # Real runtime must be evaluated inside the same trusted service path.
        # This second receipt is bound to the exact action and current policy.
        try:
            receipt = self.runtime.evaluate(event_copy)
            if not receipt.verify() or receipt.event_sha256 != event_sha:
                return GateResult(False, "finality-receipt-invalid")
            if receipt.decision != "ALLOW":
                return GateResult(False, "runtime-not-allow-at-finality")
            if dict(receipt.policy) != dict(self.runtime.policy):
                return GateResult(False, "finality-policy-mismatch")
        except Exception:
            return GateResult(False, "finality-runtime-failed-closed")

        now = float(self.clock())
        con = self._connect()
        try:
            con.execute("BEGIN IMMEDIATE")
            row = con.execute("SELECT * FROM issued_witnesses WHERE witness_id=?", (witness_id,)).fetchone()
            if row is None:
                con.rollback()
                return GateResult(False, "witness-not-issued-by-this-gate", witness_id)
            # Database record is the provenance anchor; a public hash alone is not.
            if (row["body_sha256"] != body_sha or row["event_sha256"] != event_sha or
                row["policy_sha256"] != dict(self.runtime.policy).get("sha256") or
                row["admission_receipt_sha256"] != body_dict.get("admission_receipt_sha256") or
                row["requirements_sha256"] != self._requirements_sha):
                con.rollback()
                return GateResult(False, "witness-registry-mismatch", witness_id)
            if row["consumed_at"] is not None:
                con.rollback()
                return GateResult(False, "witness-already-consumed", witness_id)
            if now > float(row["expires_at"]):
                con.rollback()
                return GateResult(False, "witness-expired", witness_id)

            # Re-read required evidence while the one-use registry transaction is
            # held, as close as this adapter can get to authorization consumption.
            # External providers must offer their own version/lease transaction if
            # they need stronger atomicity than a pre-consumption recheck.
            try:
                for expected_req, item in zip(self.required_evidence, evidence, strict=True):
                    if item["requirement"] != expected_req.to_dict():
                        con.rollback()
                        return GateResult(False, "witness-requirement-substitution", witness_id)
                    rec = item["admitted"]
                    if not isinstance(rec, Mapping) or set(rec) != {"key", "version", "subject_hash", "value_digest", "status"}:
                        con.rollback()
                        return GateResult(False, "invalid-admitted-evidence", witness_id)
                    current = self.provider.get_evidence(expected_req.key)
                    if current is None:
                        con.rollback()
                        return GateResult(False, "required-evidence-missing-at-finality", witness_id)
                    if expected_req.mode == "EXACT":
                        if current.to_dict() != dict(rec):
                            con.rollback()
                            return GateResult(False, "exact-evidence-changed-after-admission", witness_id)
                    elif not self._satisfies(expected_req, current):
                        con.rollback()
                        return GateResult(False, "evidence-predicate-false-at-finality", witness_id)
            except Exception:
                con.rollback()
                return GateResult(False, "evidence-provider-failure-failed-closed", witness_id)

            if now > float(row["expires_at"]):
                con.rollback()
                return GateResult(False, "witness-expired", witness_id)
            cur = con.execute("UPDATE issued_witnesses SET consumed_at=? WHERE witness_id=? AND consumed_at IS NULL",
                              (now, witness_id))
            if cur.rowcount != 1:
                con.rollback()
                return GateResult(False, "witness-already-consumed", witness_id)
            con.commit()
            return GateResult(True, "authenticated-fresh-evidence-single-use", witness_id)
        except sqlite3.Error:
            con.rollback()
            return GateResult(False, "witness-ledger-error-failed-closed", witness_id)
        finally:
            con.close()
