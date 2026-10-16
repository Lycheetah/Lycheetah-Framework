"""Minimal authenticated operation ledger for webhook reconciliation (v2.8 reference).

The ledger stores only fields needed to bind an approved refund operation to a
provider object and its latest verified observation. It does not store complete
provider responses, customer data, descriptions, or metadata maps.
"""
from __future__ import annotations

from contextlib import contextmanager
from datetime import datetime, timezone
import hashlib
import hmac
import json
import re
import sqlite3
from typing import Any, Mapping

LEDGER_TABLE = "lycheetah_refund_operation_ledger"
LEDGER_DOMAIN = b"lycheetah-refund-operation-ledger-v2.8\n"
LEDGER_FIELDS = (
    "operation_id", "account_scope", "target_type", "target_id",
    "expected_amount", "expected_currency", "livemode", "state",
    "refund_id", "refund_status", "last_event_id", "observation_sha256",
    "manual_reason", "updated_at",
)
TERMINAL_STATES = {"PROVIDER_SUCCEEDED", "PROVIDER_FAILED", "PROVIDER_CANCELED"}
VALID_STATES = {"REQUESTED", "WAITING_PROVIDER", *TERMINAL_STATES, "MANUAL"}
VALID_REFUND_STATUSES = {"pending", "requires_action", "succeeded", "failed", "canceled"}


class OperationLedgerError(ValueError):
    """Operation record is missing, inconsistent, or invalid."""


class OperationLedgerIntegrityError(OperationLedgerError):
    """A persisted operation row failed authenticated integrity checks."""


def canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, ensure_ascii=False, separators=(",", ":"), allow_nan=False)


def _epoch(now: datetime | None = None) -> int:
    value = now or datetime.now(timezone.utc)
    if value.tzinfo is None or value.utcoffset() is None:
        raise ValueError("timestamps must be timezone-aware")
    return int(value.astimezone(timezone.utc).timestamp())


def operation_row_mac(key: bytes, row: Mapping[str, Any]) -> str:
    """Domain-separated HMAC used by both ledger reader and queue finalizer."""
    body = {name: row[name] for name in LEDGER_FIELDS}
    # SQLite represents the JSON boolean livemode as an integer.
    body["livemode"] = bool(body["livemode"])
    msg = LEDGER_DOMAIN + canonical_json(body).encode("utf-8")
    return hmac.new(key, msg, hashlib.sha256).hexdigest()


def normalize_account_scope(account_scope: str) -> str:
    if account_scope == "platform":
        return account_scope
    if isinstance(account_scope, str) and re.fullmatch(r"acct_[A-Za-z0-9]+", account_scope):
        return account_scope
    raise ValueError("account_scope must be 'platform' or a Stripe acct_ identifier")


class TrustedOperationLedger:
    """Authenticated durable operation intent + minimal provider-state ledger.

    The same SQLite file as the webhook inbox is expected. The key must be
    provided by external secret management, never loaded from that database.
    """
    def __init__(self, *, path: str, integrity_key: bytes):
        if not isinstance(integrity_key, bytes) or len(integrity_key) < 32:
            raise ValueError("integrity_key must be at least 32 bytes")
        self.path = path
        self.integrity_key = integrity_key
        with self._db() as db:
            db.execute(f"""CREATE TABLE IF NOT EXISTS {LEDGER_TABLE} (
                operation_id TEXT PRIMARY KEY,
                account_scope TEXT NOT NULL,
                target_type TEXT NOT NULL,
                target_id TEXT NOT NULL,
                expected_amount INTEGER NOT NULL,
                expected_currency TEXT NOT NULL,
                livemode INTEGER NOT NULL,
                state TEXT NOT NULL,
                refund_id TEXT,
                refund_status TEXT,
                last_event_id TEXT,
                observation_sha256 TEXT,
                manual_reason TEXT,
                updated_at INTEGER NOT NULL,
                row_hmac_sha256 TEXT NOT NULL
            )""")
            cols = {row[1] for row in db.execute(f"PRAGMA table_info({LEDGER_TABLE})").fetchall()}
            required = set(LEDGER_FIELDS) | {"row_hmac_sha256"}
            if not required.issubset(cols):
                raise OperationLedgerError("operation-ledger-schema-incomplete")

    @contextmanager
    def _db(self):
        db = sqlite3.connect(self.path, timeout=10, isolation_level="DEFERRED")
        db.row_factory = sqlite3.Row
        db.execute("PRAGMA busy_timeout=10000")
        db.execute("PRAGMA synchronous=FULL")
        try:
            yield db
            db.commit()
        except Exception:
            db.rollback()
            raise
        finally:
            db.close()

    def _check(self, raw: Mapping[str, Any]) -> dict[str, Any]:
        row = dict(raw)
        supplied = row.get("row_hmac_sha256")
        if not isinstance(supplied, str) or not hmac.compare_digest(supplied, operation_row_mac(self.integrity_key, row)):
            raise OperationLedgerIntegrityError("operation-ledger-record-authentication-failed")
        row["livemode"] = bool(row["livemode"])
        row.pop("row_hmac_sha256", None)
        return row

    def _write(self, db: sqlite3.Connection, row: dict[str, Any]) -> None:
        row["row_hmac_sha256"] = operation_row_mac(self.integrity_key, row)
        cols = (*LEDGER_FIELDS, "row_hmac_sha256")
        db.execute(
            f"INSERT INTO {LEDGER_TABLE}({','.join(cols)}) VALUES({','.join('?' for _ in cols)}) "
            f"ON CONFLICT(operation_id) DO UPDATE SET " + ",".join(f"{c}=excluded.{c}" for c in cols if c != "operation_id"),
            tuple(row[c] for c in cols),
        )

    def register_operation(self, *, operation_id: str, account_scope: str,
                           target_type: str, target_id: str, amount: int,
                           currency: str, now: datetime | None = None) -> dict[str, Any]:
        if not isinstance(operation_id, str) or not re.fullmatch(r"[A-Za-z0-9._:-]{3,128}", operation_id):
            raise ValueError("operation_id is invalid")
        scope = normalize_account_scope(account_scope)
        if target_type not in {"charge", "payment_intent"}:
            raise ValueError("target_type must be charge or payment_intent")
        prefix = "ch_" if target_type == "charge" else "pi_"
        if not isinstance(target_id, str) or not re.fullmatch(prefix + r"[A-Za-z0-9_]+", target_id):
            raise ValueError("target_id does not match target_type")
        if type(amount) is not int or amount <= 0:
            raise ValueError("amount must be a positive integer")
        if not isinstance(currency, str) or not re.fullmatch(r"[a-z]{3}", currency):
            raise ValueError("currency must be a lowercase three-letter code")
        timestamp = _epoch(now)
        candidate = {
            "operation_id": operation_id, "account_scope": scope,
            "target_type": target_type, "target_id": target_id,
            "expected_amount": amount, "expected_currency": currency,
            "livemode": False, "state": "REQUESTED", "refund_id": None,
            "refund_status": None, "last_event_id": None,
            "observation_sha256": None, "manual_reason": None,
            "updated_at": timestamp,
        }
        with self._db() as db:
            db.execute("BEGIN IMMEDIATE")
            old = db.execute(f"SELECT * FROM {LEDGER_TABLE} WHERE operation_id=?", (operation_id,)).fetchone()
            if old is not None:
                existing = self._check(old)
                expected = (scope, target_type, target_id, amount, currency, False)
                actual = (existing["account_scope"], existing["target_type"], existing["target_id"],
                          existing["expected_amount"], existing["expected_currency"], existing["livemode"])
                if actual != expected:
                    raise OperationLedgerError("operation-id-reused-with-different-intent")
                return existing
            self._write(db, candidate)
        return self.get_operation(operation_id)

    def get_operation(self, operation_id: str) -> dict[str, Any] | None:
        with self._db() as db:
            raw = db.execute(f"SELECT * FROM {LEDGER_TABLE} WHERE operation_id=?", (operation_id,)).fetchone()
        return self._check(raw) if raw is not None else None

    def mark_manual(self, operation_id: str, reason: str, *, now: datetime | None = None) -> dict[str, Any]:
        if not isinstance(reason, str) or not re.fullmatch(r"[a-z0-9-]{1,64}", reason):
            raise ValueError("reason must be a sanitized lowercase code")
        timestamp = _epoch(now)
        with self._db() as db:
            db.execute("BEGIN IMMEDIATE")
            raw = db.execute(f"SELECT * FROM {LEDGER_TABLE} WHERE operation_id=?", (operation_id,)).fetchone()
            if raw is None:
                raise OperationLedgerError("operation-ledger-record-not-found")
            row = self._check(raw)
            row.update(state="MANUAL", manual_reason=reason, updated_at=timestamp)
            self._write(db, row)
        return self.get_operation(operation_id)

    def record_provider_observation(self, *, operation_id: str, event_id: str,
                                    snapshot: Mapping[str, Any], now: datetime | None = None) -> dict[str, Any]:
        """Record only validated fields; the raw provider object is never persisted."""
        if not isinstance(event_id, str) or not re.fullmatch(r"evt_[A-Za-z0-9_]+", event_id):
            raise ValueError("event_id is invalid")
        if not isinstance(snapshot, Mapping):
            raise ValueError("snapshot must be a mapping")
        status = snapshot.get("status")
        if not isinstance(status, str) or status not in VALID_REFUND_STATUSES:
            return self.mark_manual(operation_id, "provider-status-unknown", now=now)
        timestamp = _epoch(now)
        observation = {
            "id": snapshot.get("id"), "status": status,
            "charge": snapshot.get("charge"), "payment_intent": snapshot.get("payment_intent"),
            "amount": snapshot.get("amount"), "currency": snapshot.get("currency"),
            "livemode": snapshot.get("livemode"),
            "metadata_operation_id": snapshot.get("metadata_operation_id"),
        }
        observation_digest = hashlib.sha256(canonical_json(observation).encode("utf-8")).hexdigest()
        with self._db() as db:
            db.execute("BEGIN IMMEDIATE")
            raw = db.execute(f"SELECT * FROM {LEDGER_TABLE} WHERE operation_id=?", (operation_id,)).fetchone()
            if raw is None:
                raise OperationLedgerError("operation-ledger-record-not-found")
            row = self._check(raw)
            target_value = observation["charge"] if row["target_type"] == "charge" else observation["payment_intent"]
            expected_refund_prefix_ok = isinstance(observation["id"], str) and re.fullmatch(r"re_[A-Za-z0-9_]+", observation["id"])
            good = (
                expected_refund_prefix_ok
                and observation["metadata_operation_id"] == operation_id
                and target_value == row["target_id"]
                and type(observation["amount"]) is int and observation["amount"] == row["expected_amount"]
                and observation["currency"] == row["expected_currency"]
                and observation["livemode"] is False
            )
            if not good:
                row.update(state="MANUAL", manual_reason="provider-object-contract-mismatch", updated_at=timestamp)
            else:
                new_refund_id = observation["id"]
                mapped = {
                    "succeeded": "PROVIDER_SUCCEEDED", "failed": "PROVIDER_FAILED",
                    "canceled": "PROVIDER_CANCELED", "pending": "WAITING_PROVIDER",
                    "requires_action": "MANUAL",
                }[status]
                if row["refund_id"] and row["refund_id"] != new_refund_id:
                    row.update(state="MANUAL", manual_reason="multiple-provider-refund-ids", updated_at=timestamp)
                elif row["state"] == "MANUAL":
                    # Manual is sticky; successful rereads do not silently clear it.
                    row["updated_at"] = timestamp
                elif row["state"] in TERMINAL_STATES:
                    if mapped == row["state"]:
                        row.update(refund_status=status, last_event_id=event_id,
                                   observation_sha256=observation_digest, updated_at=timestamp)
                    elif mapped == "WAITING_PROVIDER":
                        row.update(state="MANUAL", manual_reason="provider-status-regressed", updated_at=timestamp)
                    else:
                        row.update(state="MANUAL", manual_reason="conflicting-terminal-provider-status", updated_at=timestamp)
                elif mapped == "MANUAL":
                    row.update(state="MANUAL", refund_id=new_refund_id, refund_status=status,
                               last_event_id=event_id, observation_sha256=observation_digest,
                               manual_reason="provider-requires-action", updated_at=timestamp)
                else:
                    row.update(state=mapped, refund_id=new_refund_id, refund_status=status,
                               last_event_id=event_id, observation_sha256=observation_digest,
                               manual_reason=None, updated_at=timestamp)
            self._write(db, row)
        return self.get_operation(operation_id)


def validate_provider_snapshot(snapshot: Mapping[str, Any], *, refund_id: str,
                               operation_id: str) -> tuple[bool, str]:
    """Strict adapter-level validation before any provider observation is trusted."""
    if not isinstance(snapshot, Mapping) or snapshot.get("object") != "refund":
        return False, "provider-object-type-invalid"
    if snapshot.get("id") != refund_id:
        return False, "provider-refund-id-mismatch"
    if type(snapshot.get("livemode")) is not bool or snapshot.get("livemode") is not False:
        return False, "provider-livemode-mismatch"
    metadata = snapshot.get("metadata")
    if not isinstance(metadata, Mapping) or metadata.get("lycheetah_operation_id") != operation_id:
        return False, "provider-operation-correlation-mismatch"
    if snapshot.get("status") not in VALID_REFUND_STATUSES:
        return False, "provider-status-unknown"
    return True, "provider-snapshot-shape-valid"
