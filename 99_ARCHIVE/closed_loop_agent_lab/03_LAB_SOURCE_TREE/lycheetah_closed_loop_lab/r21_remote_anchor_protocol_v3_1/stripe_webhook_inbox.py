"""Authenticated, privacy-minimized Stripe refund webhook inbox (reference).

This module is deliberately an inbox + reconciliation signal, not a payment
state machine. A verified webhook is never sufficient by itself to mark a
refund successful; callers must retrieve current provider state before terminal
state changes. Use official Stripe SDKs in production after reviewing this
reference implementation and its threat model.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum
import hashlib
import hmac
import json
import re
import secrets
import sqlite3
from contextlib import contextmanager
from typing import Any, Mapping

from operation_ledger import LEDGER_TABLE, TERMINAL_STATES, operation_row_mac

MAX_WEBHOOK_BODY_BYTES = 1024 * 1024
MAX_SIGNATURE_HEADER_CHARS = 16 * 1024
DEFAULT_TIMESTAMP_TOLERANCE_SECONDS = 300
ALLOWED_EVENT_TYPES = {"refund.created", "refund.updated", "refund.failed"}
OPERATION_METADATA_KEY = "lycheetah_operation_id"
INBOX_SCHEMA_VERSION = 1
RECONCILIATION_QUEUE_SCHEMA_VERSION = 1
MAX_RECONCILIATION_ATTEMPTS = 8
MAX_RECONCILIATION_LEASE_SECONDS = 3600
MAX_RECONCILIATION_RETRY_SECONDS = 86400


class InboxAction(str, Enum):
    INGESTED = "INGESTED"
    DUPLICATE = "DUPLICATE"
    REJECTED = "REJECTED"
    RETRIEVE_CURRENT_PROVIDER_STATE = "RETRIEVE_CURRENT_PROVIDER_STATE"
    MANUAL_RECONCILIATION = "MANUAL_RECONCILIATION"
    NO_CORRELATED_EVENT = "NO_CORRELATED_EVENT"


@dataclass(frozen=True)
class InboxResult:
    action: InboxAction
    reason: str
    event_id: str | None = None
    operation_id: str | None = None
    refund_id: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {"action": self.action.value, "reason": self.reason,
                "event_id": self.event_id, "operation_id": self.operation_id,
                "refund_id": self.refund_id}


class WebhookVerificationError(ValueError):
    """Webhook signature, timestamp, encoding, or payload contract failure."""


class InboxIntegrityError(ValueError):
    """A persisted inbox row failed local HMAC verification."""


class ReconciliationQueueError(ValueError):
    """Invalid reconciliation queue transition or stale worker claim."""


@dataclass(frozen=True)
class ReconciliationJobResult:
    event_id: str
    state: str
    reason: str
    attempts: int
    available_at: int

    def to_dict(self) -> dict[str, Any]:
        return {
            "event_id": self.event_id,
            "state": self.state,
            "reason": self.reason,
            "attempts": self.attempts,
            "available_at": self.available_at,
        }


def _canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, ensure_ascii=False,
                      separators=(",", ":"), allow_nan=False)


def _sha256(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def _parse_stripe_signature(header: str) -> tuple[int, tuple[str, ...]]:
    if not isinstance(header, str) or not header or len(header) > MAX_SIGNATURE_HEADER_CHARS:
        raise WebhookVerificationError("signature-header-invalid")
    timestamp_values: list[str] = []
    v1_values: list[str] = []
    for component in header.split(","):
        key, sep, value = component.strip().partition("=")
        if not sep or not key or not value:
            raise WebhookVerificationError("signature-header-invalid")
        if key == "t":
            timestamp_values.append(value)
        elif key == "v1":
            if not re.fullmatch(r"[0-9a-fA-F]{64}", value):
                raise WebhookVerificationError("signature-v1-invalid")
            v1_values.append(value.lower())
        # Other version tokens (for example v0 during transitions) are ignored.
    if len(timestamp_values) != 1 or not re.fullmatch(r"[0-9]{1,16}", timestamp_values[0]):
        raise WebhookVerificationError("signature-timestamp-invalid")
    if not v1_values:
        raise WebhookVerificationError("signature-v1-missing")
    return int(timestamp_values[0]), tuple(v1_values)


def _strict_json_loads(raw: bytes) -> Mapping[str, Any]:
    try:
        text = raw.decode("utf-8", errors="strict")
    except UnicodeDecodeError:
        raise WebhookVerificationError("payload-not-valid-utf8") from None

    def no_duplicate_keys(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
        out: dict[str, Any] = {}
        for key, value in pairs:
            if key in out:
                raise WebhookVerificationError("payload-contains-duplicate-json-key")
            out[key] = value
        return out

    def reject_constant(_value: str) -> None:
        raise WebhookVerificationError("payload-contains-nonstandard-number")

    try:
        value = json.loads(text, object_pairs_hook=no_duplicate_keys,
                           parse_constant=reject_constant)
    except WebhookVerificationError:
        raise
    except (json.JSONDecodeError, ValueError):
        raise WebhookVerificationError("payload-json-invalid") from None
    if not isinstance(value, Mapping):
        raise WebhookVerificationError("payload-root-must-be-object")
    return value


def _validate_and_minimize_event(event: Mapping[str, Any], *,
                                 expected_account: str | None) -> dict[str, Any]:
    if event.get("object") != "event":
        raise WebhookVerificationError("event-object-type-invalid")
    event_id = event.get("id")
    if not isinstance(event_id, str) or not re.fullmatch(r"evt_[A-Za-z0-9_]+", event_id):
        raise WebhookVerificationError("event-id-invalid")
    event_type = event.get("type")
    if not isinstance(event_type, str) or event_type not in ALLOWED_EVENT_TYPES:
        raise WebhookVerificationError("event-type-not-allowed")
    created = event.get("created")
    if type(created) is not int or created < 0:
        raise WebhookVerificationError("event-created-invalid")
    if event.get("livemode") is not False:
        raise WebhookVerificationError("event-not-explicitly-test-mode")

    event_account = event.get("account")
    if expected_account is None:
        if event_account not in (None, ""):
            raise WebhookVerificationError("connected-account-event-not-allowed-on-platform-inbox")
        event_account = None
    else:
        if not isinstance(expected_account, str) or not re.fullmatch(r"acct_[A-Za-z0-9]+", expected_account):
            raise WebhookVerificationError("configured-connected-account-invalid")
        if event_account != expected_account:
            raise WebhookVerificationError("event-connected-account-mismatch")

    data = event.get("data")
    if not isinstance(data, Mapping) or not isinstance(data.get("object"), Mapping):
        raise WebhookVerificationError("event-data-object-invalid")
    refund = data["object"]
    if refund.get("object") != "refund":
        raise WebhookVerificationError("event-data-object-not-refund")
    refund_id = refund.get("id")
    if not isinstance(refund_id, str) or not re.fullmatch(r"re_[A-Za-z0-9_]+", refund_id):
        raise WebhookVerificationError("refund-id-invalid")
    charge = refund.get("charge")
    payment_intent = refund.get("payment_intent")
    if charge is not None and (not isinstance(charge, str) or not re.fullmatch(r"ch_[A-Za-z0-9_]+", charge)):
        raise WebhookVerificationError("refund-charge-id-invalid")
    if payment_intent is not None and (not isinstance(payment_intent, str) or not re.fullmatch(r"pi_[A-Za-z0-9_]+", payment_intent)):
        raise WebhookVerificationError("refund-payment-intent-id-invalid")
    if not charge and not payment_intent:
        raise WebhookVerificationError("refund-target-missing")
    amount = refund.get("amount")
    if type(amount) is not int or amount <= 0:
        raise WebhookVerificationError("refund-amount-invalid")
    currency = refund.get("currency")
    if not isinstance(currency, str) or not re.fullmatch(r"[a-z]{3}", currency):
        raise WebhookVerificationError("refund-currency-invalid")
    if refund.get("livemode") is not False:
        raise WebhookVerificationError("refund-not-explicitly-test-mode")
    status = refund.get("status")
    if not isinstance(status, str) or not status:
        raise WebhookVerificationError("refund-status-missing")
    if event_type == "refund.failed" and status != "failed":
        raise WebhookVerificationError("refund-failed-event-status-mismatch")

    metadata = refund.get("metadata")
    operation_id: str | None = None
    if isinstance(metadata, Mapping):
        candidate = metadata.get(OPERATION_METADATA_KEY)
        if isinstance(candidate, str) and re.fullmatch(r"[A-Za-z0-9._:-]{3,128}", candidate):
            operation_id = candidate

    # Persist only fields needed to route a reconciliation. Intentionally do not
    # retain raw event JSON, previous_attributes, customer/payment-method details,
    # descriptions, arbitrary metadata, or any secret-like provider fields.
    return {
        "event_id": event_id,
        "event_type": event_type,
        "event_created": created,
        "event_account": event_account,
        "refund_id": refund_id,
        "charge": charge,
        "payment_intent": payment_intent,
        "amount": amount,
        "currency": currency,
        "refund_status": status,
        "operation_id": operation_id,
        "livemode": False,
    }


class StripeWebhookInbox:
    """Verify Stripe snapshot-event signatures and store a minimal authenticated inbox.

    `endpoint_secrets` supports current and previous endpoint-secret labels during
    rotation. Values must be actual `whsec_...` endpoint secrets from a secret
    manager. Do not print or commit them. The optional test clock is disabled by
    default so production callers cannot inject per-request freshness timestamps.
    """

    def __init__(self, *, path: str, integrity_key: bytes,
                 endpoint_secrets: Mapping[str, str], expected_account: str | None = None,
                 timestamp_tolerance_seconds: int = DEFAULT_TIMESTAMP_TOLERANCE_SECONDS,
                 allow_test_clock_override: bool = False):
        if not isinstance(integrity_key, bytes) or len(integrity_key) < 32:
            raise ValueError("integrity_key must be at least 32 bytes")
        if not isinstance(endpoint_secrets, Mapping) or not endpoint_secrets:
            raise ValueError("at least one labeled endpoint secret is required")
        clean_secrets: dict[str, str] = {}
        for label, secret in endpoint_secrets.items():
            if not isinstance(label, str) or not re.fullmatch(r"[A-Za-z0-9._:-]{1,64}", label):
                raise ValueError("endpoint-secret labels must be stable non-secret identifiers")
            if not isinstance(secret, str) or not secret.startswith("whsec_") or len(secret) < 20:
                raise ValueError("endpoint secrets must be non-empty Stripe whsec_ secrets")
            clean_secrets[label] = secret
        if expected_account is not None and (not isinstance(expected_account, str) or not re.fullmatch(r"acct_[A-Za-z0-9]+", expected_account)):
            raise ValueError("expected_account must be a Stripe account id or None")
        if type(timestamp_tolerance_seconds) is not int or not 1 <= timestamp_tolerance_seconds <= 3600:
            raise ValueError("timestamp tolerance must be an integer from 1 through 3600 seconds")
        if type(allow_test_clock_override) is not bool:
            raise ValueError("allow_test_clock_override must be an actual boolean")

        self.path = path
        self.integrity_key = integrity_key
        self.endpoint_secrets = clean_secrets
        self.expected_account = expected_account
        self.timestamp_tolerance_seconds = timestamp_tolerance_seconds
        self.allow_test_clock_override = allow_test_clock_override
        with self._db() as db:
            db.execute("""CREATE TABLE IF NOT EXISTS stripe_webhook_inbox (
                event_id TEXT PRIMARY KEY,
                event_type TEXT NOT NULL,
                event_created INTEGER NOT NULL,
                event_account TEXT,
                refund_id TEXT NOT NULL,
                charge TEXT,
                payment_intent TEXT,
                amount INTEGER NOT NULL,
                currency TEXT NOT NULL,
                refund_status TEXT NOT NULL,
                operation_id TEXT,
                livemode INTEGER NOT NULL,
                payload_sha256 TEXT NOT NULL,
                signature_timestamp INTEGER NOT NULL,
                signing_secret_label TEXT NOT NULL,
                received_at TEXT NOT NULL,
                row_hmac_sha256 TEXT NOT NULL
            )""")
            columns = {row[1] for row in db.execute("PRAGMA table_info(stripe_webhook_inbox)").fetchall()}
            required = {"event_id", "event_type", "event_created", "event_account", "refund_id",
                        "charge", "payment_intent", "amount", "currency", "refund_status",
                        "operation_id", "livemode", "payload_sha256", "signature_timestamp",
                        "signing_secret_label", "received_at", "row_hmac_sha256"}
            if not required.issubset(columns):
                raise ValueError("webhook inbox schema is incomplete; explicit migration required")
            # Additive migration: an existing authenticated inbox remains intact,
            # while the work queue is created alongside it. Ingest inserts the
            # event and its reconciliation job in one SQLite transaction.
            db.execute("""CREATE TABLE IF NOT EXISTS stripe_reconciliation_jobs (
                event_id TEXT PRIMARY KEY,
                operation_id TEXT,
                refund_id TEXT NOT NULL,
                event_account TEXT,
                charge TEXT,
                payment_intent TEXT,
                amount INTEGER NOT NULL,
                currency TEXT NOT NULL,
                state TEXT NOT NULL,
                attempts INTEGER NOT NULL,
                available_at INTEGER NOT NULL,
                claimed_by TEXT,
                claim_token_sha256 TEXT,
                lease_until INTEGER,
                last_error_code TEXT,
                created_at INTEGER NOT NULL,
                updated_at INTEGER NOT NULL,
                row_hmac_sha256 TEXT NOT NULL
            )""")
            db.execute("CREATE INDEX IF NOT EXISTS idx_reconciliation_jobs_ready "
                       "ON stripe_reconciliation_jobs(state, available_at, created_at)")
            queue_columns = {row[1] for row in db.execute(
                "PRAGMA table_info(stripe_reconciliation_jobs)").fetchall()}
            queue_required = {"event_id", "operation_id", "refund_id", "event_account",
                "charge", "payment_intent", "amount", "currency", "state", "attempts",
                "available_at", "claimed_by", "claim_token_sha256", "lease_until",
                "last_error_code", "created_at", "updated_at", "row_hmac_sha256"}
            if not queue_required.issubset(queue_columns):
                raise ValueError("reconciliation queue schema is incomplete; explicit migration required")

            # Backfill v2.6 inbox rows when upgrading an older database. Verify
            # each source-row HMAC first; never turn untrusted legacy state into
            # a trusted pending job. Existing job states are preserved.
            legacy_rows = db.execute("SELECT * FROM stripe_webhook_inbox").fetchall()
            for legacy_raw in legacy_rows:
                legacy = dict(legacy_raw)
                supplied_mac = legacy.get("row_hmac_sha256")
                if not isinstance(supplied_mac, str) or not hmac.compare_digest(
                    supplied_mac, self._mac(legacy)
                ):
                    raise InboxIntegrityError("cannot backfill queue from unauthenticated inbox row")
                if db.execute("SELECT 1 FROM stripe_reconciliation_jobs WHERE event_id=?",
                              (legacy["event_id"],)).fetchone() is not None:
                    continue
                try:
                    received_at = datetime.fromisoformat(str(legacy["received_at"]))
                    if received_at.tzinfo is None or received_at.utcoffset() is None:
                        raise ValueError("timezone missing")
                    created_epoch = int(received_at.astimezone(timezone.utc).timestamp())
                except (TypeError, ValueError, OverflowError):
                    raise ValueError("legacy inbox received_at is invalid; explicit migration required") from None
                job = {
                    "event_id": legacy["event_id"],
                    "operation_id": legacy["operation_id"],
                    "refund_id": legacy["refund_id"],
                    "event_account": legacy["event_account"],
                    "charge": legacy["charge"],
                    "payment_intent": legacy["payment_intent"],
                    "amount": legacy["amount"],
                    "currency": legacy["currency"],
                    "state": "PENDING" if legacy["operation_id"] else "MANUAL",
                    "attempts": 0,
                    "available_at": created_epoch,
                    "claimed_by": None,
                    "claim_token_sha256": None,
                    "lease_until": None,
                    "last_error_code": None if legacy["operation_id"] else "missing-operation-correlation",
                    "created_at": created_epoch,
                    "updated_at": created_epoch,
                }
                job["row_hmac_sha256"] = self._job_mac(job)
                job_columns = tuple(job.keys())
                job_placeholders = ",".join("?" for _ in job_columns)
                db.execute(
                    f"INSERT INTO stripe_reconciliation_jobs({','.join(job_columns)}) "
                    f"VALUES({job_placeholders})",
                    tuple(job[name] for name in job_columns),
                )

            # v2.8 upgrade guard: historical v2.7 DONE flags were accepted from a
            # caller's disposition without an authenticated terminal operation
            # ledger. Demote those unproven completions to MANUAL. A valid v2.8
            # terminal record must be bound to the exact event and refund.
            legacy_done = db.execute(
                "SELECT * FROM stripe_reconciliation_jobs WHERE state='DONE'"
            ).fetchall()
            if legacy_done:
                migration_epoch = int(datetime.now(timezone.utc).timestamp())
                for raw_done in legacy_done:
                    job = self._check_job(raw_done)
                    try:
                        self._require_terminal_operation_ledger(db, job)
                    except ReconciliationQueueError:
                        job.update(
                            state="MANUAL", claimed_by=None, claim_token_sha256=None,
                            lease_until=None, last_error_code="legacy-done-unproven",
                            updated_at=migration_epoch,
                        )
                        job["row_hmac_sha256"] = self._job_mac(job)
                        db.execute("""UPDATE stripe_reconciliation_jobs SET state=?, claimed_by=?,
                            claim_token_sha256=?, lease_until=?, last_error_code=?, updated_at=?,
                            row_hmac_sha256=? WHERE event_id=?""",
                            (job["state"], job["claimed_by"], job["claim_token_sha256"],
                             job["lease_until"], job["last_error_code"], job["updated_at"],
                             job["row_hmac_sha256"], job["event_id"]))

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

    @staticmethod
    def _authenticated_fields(row: Mapping[str, Any]) -> dict[str, Any]:
        fields = ("event_id", "event_type", "event_created", "event_account", "refund_id",
                  "charge", "payment_intent", "amount", "currency", "refund_status",
                  "operation_id", "livemode", "payload_sha256", "signature_timestamp",
                  "signing_secret_label", "received_at")
        out = {name: row[name] for name in fields}
        # SQLite stores bools in INTEGER columns and returns 0/1. Normalize the
        # signed record representation to JSON booleans before authenticating.
        if "livemode" in out:
            out["livemode"] = bool(out["livemode"])
        return out

    def _mac(self, row: Mapping[str, Any]) -> str:
        return hmac.new(self.integrity_key,
                        _canonical_json(self._authenticated_fields(row)).encode("utf-8"),
                        hashlib.sha256).hexdigest()

    @staticmethod
    def _job_authenticated_fields(row: Mapping[str, Any]) -> dict[str, Any]:
        names = ("event_id", "operation_id", "refund_id", "event_account", "charge",
                 "payment_intent", "amount", "currency", "state", "attempts",
                 "available_at", "claimed_by", "claim_token_sha256", "lease_until",
                 "last_error_code", "created_at", "updated_at")
        return {name: row[name] for name in names}

    def _job_mac(self, row: Mapping[str, Any]) -> str:
        return hmac.new(self.integrity_key,
                        _canonical_json(self._job_authenticated_fields(row)).encode("utf-8"),
                        hashlib.sha256).hexdigest()

    def _check_job(self, row: Mapping[str, Any]) -> dict[str, Any]:
        value = dict(row)
        supplied = value.get("row_hmac_sha256")
        if not isinstance(supplied, str) or not hmac.compare_digest(supplied, self._job_mac(value)):
            raise InboxIntegrityError("reconciliation-job-authentication-failed")
        return value

    @staticmethod
    def _public_job(row: Mapping[str, Any], claim_token: str | None = None) -> dict[str, Any]:
        value = dict(row)
        value.pop("row_hmac_sha256", None)
        # Only the SHA-256 digest is stored. Never reveal it through the public API.
        value.pop("claim_token_sha256", None)
        if claim_token is not None:
            value["claim_token"] = claim_token
        return value

    def _resolve_now(self, now: datetime | None) -> datetime:
        if now is not None and not self.allow_test_clock_override:
            raise ValueError("per-call clock override is test-only")
        current = now if now is not None else datetime.now(timezone.utc)
        if not isinstance(current, datetime) or current.tzinfo is None or current.utcoffset() is None:
            raise ValueError("clock must return a timezone-aware datetime")
        return current.astimezone(timezone.utc)

    def _verify_signature(self, raw_body: bytes, signature_header: str,
                          now: datetime) -> tuple[int, str]:
        if not isinstance(raw_body, bytes) or not raw_body:
            raise WebhookVerificationError("raw-body-required")
        if len(raw_body) > MAX_WEBHOOK_BODY_BYTES:
            raise WebhookVerificationError("payload-too-large")
        timestamp, signatures = _parse_stripe_signature(signature_header)
        signed_at = datetime.fromtimestamp(timestamp, tz=timezone.utc)
        if abs((now - signed_at).total_seconds()) > self.timestamp_tolerance_seconds:
            raise WebhookVerificationError("signature-timestamp-outside-tolerance")
        message = str(timestamp).encode("ascii") + b"." + raw_body
        matched_label: str | None = None
        for label, secret in self.endpoint_secrets.items():
            expected = hmac.new(secret.encode("utf-8"), message, hashlib.sha256).hexdigest()
            for received in signatures:
                if hmac.compare_digest(expected, received):
                    matched_label = label
        if matched_label is None:
            raise WebhookVerificationError("signature-mismatch")
        return timestamp, matched_label

    def ingest(self, raw_body: bytes, signature_header: str, *, now: datetime | None = None) -> InboxResult:
        current = self._resolve_now(now)
        try:
            signature_timestamp, secret_label = self._verify_signature(raw_body, signature_header, current)
            event = _strict_json_loads(raw_body)
            summary = _validate_and_minimize_event(event, expected_account=self.expected_account)
        except (WebhookVerificationError, OverflowError, OSError, ValueError) as exc:
            # Generic validation errors only; never echo body, signature, or secret.
            return InboxResult(InboxAction.REJECTED, str(exc) if isinstance(exc, WebhookVerificationError) else "webhook-validation-failed")

        received_at = current.isoformat(timespec="microseconds")
        body_hash = _sha256(raw_body)
        row = {**summary, "payload_sha256": body_hash,
               "signature_timestamp": signature_timestamp,
               "signing_secret_label": secret_label, "received_at": received_at}
        row_mac = self._mac(row)
        row["row_hmac_sha256"] = row_mac

        try:
            with self._db() as db:
                db.execute("BEGIN IMMEDIATE")
                existing = db.execute("SELECT * FROM stripe_webhook_inbox WHERE event_id=?", (summary["event_id"],)).fetchone()
                if existing is not None:
                    existing_map = dict(existing)
                    if not hmac.compare_digest(str(existing_map.get("row_hmac_sha256", "")), self._mac(existing_map)):
                        raise InboxIntegrityError("inbox-record-authentication-failed")
                    if existing_map["payload_sha256"] == body_hash:
                        return InboxResult(InboxAction.DUPLICATE, "event-already-inbox-recorded", summary["event_id"], summary.get("operation_id"))
                    return InboxResult(InboxAction.REJECTED, "event-id-reused-with-different-payload", summary["event_id"], summary.get("operation_id"))
                columns = tuple(row.keys())
                placeholders = ",".join("?" for _ in columns)
                db.execute(f"INSERT INTO stripe_webhook_inbox({','.join(columns)}) VALUES({placeholders})",
                           tuple(row[name] for name in columns))
                # Event receipt and its durable reconciliation task commit or roll
                # back together. An event without correlation is preserved as a
                # manual-reconciliation item instead of silently disappearing.
                now_epoch = int(current.timestamp())
                job = {
                    "event_id": summary["event_id"],
                    "operation_id": summary.get("operation_id"),
                    "refund_id": summary["refund_id"],
                    "event_account": summary.get("event_account"),
                    "charge": summary.get("charge"),
                    "payment_intent": summary.get("payment_intent"),
                    "amount": summary["amount"],
                    "currency": summary["currency"],
                    "state": "PENDING" if summary.get("operation_id") else "MANUAL",
                    "attempts": 0,
                    "available_at": now_epoch,
                    "claimed_by": None,
                    "claim_token_sha256": None,
                    "lease_until": None,
                    "last_error_code": None if summary.get("operation_id") else "missing-operation-correlation",
                    "created_at": now_epoch,
                    "updated_at": now_epoch,
                }
                job["row_hmac_sha256"] = self._job_mac(job)
                job_columns = tuple(job.keys())
                job_placeholders = ",".join("?" for _ in job_columns)
                db.execute(
                    f"INSERT INTO stripe_reconciliation_jobs({','.join(job_columns)}) "
                    f"VALUES({job_placeholders})",
                    tuple(job[name] for name in job_columns),
                )
        except InboxIntegrityError:
            return InboxResult(InboxAction.REJECTED, "inbox-record-authentication-failed", summary["event_id"], summary.get("operation_id"))
        except sqlite3.Error:
            return InboxResult(InboxAction.REJECTED, "inbox-durable-write-failed", summary["event_id"], summary.get("operation_id"))
        return InboxResult(InboxAction.INGESTED, "signature-valid-minimal-event-recorded", summary["event_id"], summary.get("operation_id"))

    def claim_reconciliation_jobs(self, *, worker_id: str, limit: int = 10,
                                  lease_seconds: int = 60,
                                  now: datetime | None = None) -> list[dict[str, Any]]:
        """Atomically lease ready jobs; expired leases are recovered first.

        The returned claim_token is a one-time capability. Persist only its digest.
        Multiple workers share SQLite's write lock, so a job is issued to at most
        one current lease holder. Expired jobs may be reclaimed because handlers
        perform read-only provider retrieval and local reconciliation, not a fresh
        refund POST.
        """
        if not isinstance(worker_id, str) or not re.fullmatch(r"[A-Za-z0-9._:-]{3,128}", worker_id):
            raise ValueError("worker_id is invalid")
        if type(limit) is not int or not 1 <= limit <= 100:
            raise ValueError("limit must be an integer from 1 through 100")
        if type(lease_seconds) is not int or not 1 <= lease_seconds <= MAX_RECONCILIATION_LEASE_SECONDS:
            raise ValueError("lease_seconds is outside the allowed range")
        now_epoch = int(self._resolve_now(now).timestamp())
        claimed: list[dict[str, Any]] = []
        with self._db() as db:
            db.execute("BEGIN IMMEDIATE")
            expired = db.execute(
                "SELECT * FROM stripe_reconciliation_jobs WHERE state='CLAIMED' AND lease_until<=?",
                (now_epoch,),
            ).fetchall()
            for raw in expired:
                job = self._check_job(raw)
                if job.get("event_account") != self.expected_account:
                    job.update(state="MANUAL", claimed_by=None, claim_token_sha256=None,
                               lease_until=None, last_error_code="inbox-account-scope-mismatch",
                               updated_at=now_epoch)
                elif int(job["attempts"]) >= MAX_RECONCILIATION_ATTEMPTS:
                    job.update(state="MANUAL", claimed_by=None, claim_token_sha256=None,
                               lease_until=None, last_error_code="lease-expired-max-attempts",
                               updated_at=now_epoch)
                else:
                    job.update(state="PENDING", available_at=now_epoch, claimed_by=None,
                               claim_token_sha256=None, lease_until=None,
                               last_error_code="worker-lease-expired", updated_at=now_epoch)
                job["row_hmac_sha256"] = self._job_mac(job)
                db.execute("""UPDATE stripe_reconciliation_jobs SET state=?, available_at=?,
                    claimed_by=?, claim_token_sha256=?, lease_until=?, last_error_code=?,
                    updated_at=?, row_hmac_sha256=? WHERE event_id=?""",
                    (job["state"], job["available_at"], job["claimed_by"],
                     job["claim_token_sha256"], job["lease_until"], job["last_error_code"],
                     job["updated_at"], job["row_hmac_sha256"], job["event_id"]))

            candidates = db.execute("""SELECT * FROM stripe_reconciliation_jobs
                WHERE state='PENDING' AND available_at<=?
                ORDER BY available_at, created_at, event_id LIMIT ?""",
                (now_epoch, limit)).fetchall()
            for raw in candidates:
                job = self._check_job(raw)
                if job.get("event_account") != self.expected_account:
                    # Database reuse under a different platform/Connect account
                    # configuration must not route previously accepted work.
                    job.update(state="MANUAL", last_error_code="inbox-account-scope-mismatch",
                               updated_at=now_epoch)
                    job["row_hmac_sha256"] = self._job_mac(job)
                    db.execute("UPDATE stripe_reconciliation_jobs SET state=?, last_error_code=?, updated_at=?, row_hmac_sha256=? WHERE event_id=?",
                               (job["state"], job["last_error_code"], job["updated_at"],
                                job["row_hmac_sha256"], job["event_id"]))
                    continue
                if not job.get("operation_id"):
                    # Defensive consistency check: uncorrelated work is never dispatched.
                    job.update(state="MANUAL", last_error_code="missing-operation-correlation",
                               updated_at=now_epoch)
                    job["row_hmac_sha256"] = self._job_mac(job)
                    db.execute("UPDATE stripe_reconciliation_jobs SET state=?, last_error_code=?, updated_at=?, row_hmac_sha256=? WHERE event_id=?",
                               (job["state"], job["last_error_code"], job["updated_at"],
                                job["row_hmac_sha256"], job["event_id"]))
                    continue
                token = secrets.token_urlsafe(32)
                job.update(state="CLAIMED", attempts=int(job["attempts"]) + 1,
                           claimed_by=worker_id,
                           claim_token_sha256=hashlib.sha256(token.encode("ascii")).hexdigest(),
                           lease_until=now_epoch + lease_seconds,
                           last_error_code=None, updated_at=now_epoch)
                job["row_hmac_sha256"] = self._job_mac(job)
                db.execute("""UPDATE stripe_reconciliation_jobs SET state=?, attempts=?, claimed_by=?,
                    claim_token_sha256=?, lease_until=?, last_error_code=?, updated_at=?, row_hmac_sha256=?
                    WHERE event_id=?""",
                    (job["state"], job["attempts"], job["claimed_by"], job["claim_token_sha256"],
                     job["lease_until"], job["last_error_code"], job["updated_at"],
                     job["row_hmac_sha256"], job["event_id"]))
                claimed.append(self._public_job(job, token))
        return claimed

    def _require_terminal_operation_ledger(self, db: sqlite3.Connection,
                                           job: Mapping[str, Any]) -> None:
        """Require authenticated terminal provider state before a queue job can be DONE.

        A worker's string disposition is not proof. The operation ledger shares
        the same durable SQLite authority and integrity key, and must already
        contain a terminal current-provider observation for this exact operation.
        """
        if not job.get("operation_id"):
            raise ReconciliationQueueError("reconciled-job-missing-operation-correlation")
        exists = db.execute(
            "SELECT 1 FROM sqlite_master WHERE type='table' AND name=?", (LEDGER_TABLE,)
        ).fetchone()
        if exists is None:
            raise ReconciliationQueueError("operation-ledger-required-before-reconciliation")
        raw = db.execute(
            f"SELECT * FROM {LEDGER_TABLE} WHERE operation_id=?", (job["operation_id"],)
        ).fetchone()
        if raw is None:
            raise ReconciliationQueueError("operation-ledger-record-required-before-reconciliation")
        row = dict(raw)
        supplied = row.get("row_hmac_sha256")
        if not isinstance(supplied, str) or not hmac.compare_digest(
            supplied, operation_row_mac(self.integrity_key, row)
        ):
            raise InboxIntegrityError("operation-ledger-record-authentication-failed")
        expected_account = "platform" if job.get("event_account") is None else job.get("event_account")
        if (
            row.get("operation_id") != job.get("operation_id")
            or row.get("account_scope") != expected_account
            or bool(row.get("livemode")) is not False
            or row.get("expected_amount") != job.get("amount")
            or row.get("expected_currency") != job.get("currency")
            or row.get("refund_id") != job.get("refund_id")
            or row.get("last_event_id") != job.get("event_id")
            or row.get("state") not in TERMINAL_STATES
            or not isinstance(row.get("observation_sha256"), str)
            or not re.fullmatch(r"[a-f0-9]{64}", row.get("observation_sha256", ""))
        ):
            raise ReconciliationQueueError("operation-ledger-terminal-evidence-mismatch")
        target_type = row.get("target_type")
        target_id = row.get("target_id")
        if target_type == "charge":
            target_ok = job.get("charge") == target_id
        elif target_type == "payment_intent":
            target_ok = job.get("payment_intent") == target_id
        else:
            target_ok = False
        status_for_state = {
            "PROVIDER_SUCCEEDED": "succeeded",
            "PROVIDER_FAILED": "failed",
            "PROVIDER_CANCELED": "canceled",
        }
        if not target_ok or row.get("refund_status") != status_for_state.get(row.get("state")):
            raise ReconciliationQueueError("operation-ledger-target-or-status-mismatch")

    def finish_reconciliation_job(self, *, event_id: str, worker_id: str,
                                  claim_token: str, disposition: str,
                                  now: datetime | None = None,
                                  retry_after_seconds: int = 30,
                                  reason_code: str | None = None) -> ReconciliationJobResult:
        """Finish a leased task without ever taking webhook status as truth.

        disposition is RECONCILED only after the trusted worker has retrieved the
        current provider resource and durably recorded its own decision. RETRY is
        for transient retrieval failures. MANUAL is a sticky human-reconciliation
        state. This method records queue processing, not refund success.
        """
        if disposition not in {"RECONCILED", "RETRY", "MANUAL"}:
            raise ValueError("disposition must be RECONCILED, RETRY, or MANUAL")
        if not isinstance(event_id, str) or not re.fullmatch(r"evt_[A-Za-z0-9_]+", event_id):
            raise ValueError("event_id is invalid")
        if not isinstance(worker_id, str) or not re.fullmatch(r"[A-Za-z0-9._:-]{3,128}", worker_id):
            raise ValueError("worker_id is invalid")
        if not isinstance(claim_token, str) or len(claim_token) < 32:
            raise ValueError("claim_token is invalid")
        if disposition == "RETRY" and (type(retry_after_seconds) is not int or not 1 <= retry_after_seconds <= MAX_RECONCILIATION_RETRY_SECONDS):
            raise ValueError("retry_after_seconds is outside the allowed range")
        if reason_code is not None and (not isinstance(reason_code, str) or not re.fullmatch(r"[a-z0-9-]{1,64}", reason_code)):
            raise ValueError("reason_code must be a sanitized lowercase code")

        now_epoch = int(self._resolve_now(now).timestamp())
        token_digest = hashlib.sha256(claim_token.encode("ascii", errors="strict")).hexdigest()
        with self._db() as db:
            db.execute("BEGIN IMMEDIATE")
            raw = db.execute("SELECT * FROM stripe_reconciliation_jobs WHERE event_id=?", (event_id,)).fetchone()
            if raw is None:
                raise ReconciliationQueueError("reconciliation-job-not-found")
            job = self._check_job(raw)
            if job["state"] != "CLAIMED":
                raise ReconciliationQueueError("reconciliation-job-not-claimed")
            if job["claimed_by"] != worker_id or not hmac.compare_digest(str(job["claim_token_sha256"] or ""), token_digest):
                raise ReconciliationQueueError("reconciliation-claim-mismatch")
            if job["lease_until"] is None or int(job["lease_until"]) <= now_epoch:
                raise ReconciliationQueueError("reconciliation-lease-expired")
            if job.get("event_account") != self.expected_account:
                raise ReconciliationQueueError("reconciliation-account-scope-mismatch")

            if disposition == "RECONCILED":
                self._require_terminal_operation_ledger(db, job)
                state, available_at, error_code = "DONE", int(job["available_at"]), None
            elif disposition == "MANUAL" or int(job["attempts"]) >= MAX_RECONCILIATION_ATTEMPTS:
                state, available_at = "MANUAL", int(job["available_at"])
                if int(job["attempts"]) >= MAX_RECONCILIATION_ATTEMPTS and disposition == "RETRY":
                    error_code = "max-attempts-exhausted"
                else:
                    error_code = reason_code or "manual-reconciliation-required"
            else:
                state, available_at = "PENDING", now_epoch + retry_after_seconds
                error_code = reason_code or "transient-reconciliation-failure"
            job.update(state=state, available_at=available_at, claimed_by=None,
                       claim_token_sha256=None, lease_until=None, last_error_code=error_code,
                       updated_at=now_epoch)
            job["row_hmac_sha256"] = self._job_mac(job)
            db.execute("""UPDATE stripe_reconciliation_jobs SET state=?, available_at=?, claimed_by=?,
                claim_token_sha256=?, lease_until=?, last_error_code=?, updated_at=?, row_hmac_sha256=?
                WHERE event_id=?""",
                (job["state"], job["available_at"], job["claimed_by"], job["claim_token_sha256"],
                 job["lease_until"], job["last_error_code"], job["updated_at"],
                 job["row_hmac_sha256"], job["event_id"]))
        return ReconciliationJobResult(event_id, state, error_code or "reconciliation-work-recorded",
                                       int(job["attempts"]), int(available_at))

    def get_reconciliation_job(self, event_id: str) -> dict[str, Any] | None:
        with self._db() as db:
            row = db.execute("SELECT * FROM stripe_reconciliation_jobs WHERE event_id=?", (event_id,)).fetchone()
        if row is None:
            return None
        return self._public_job(self._check_job(row))

    def list_reconciliation_jobs(self, *, state: str | None = None,
                                 operation_id: str | None = None) -> list[dict[str, Any]]:
        allowed_states = {"PENDING", "CLAIMED", "DONE", "MANUAL"}
        if state is not None and state not in allowed_states:
            raise ValueError("state is invalid")
        if operation_id is not None and (not isinstance(operation_id, str) or not re.fullmatch(r"[A-Za-z0-9._:-]{3,128}", operation_id)):
            raise ValueError("operation_id is invalid")
        query = "SELECT * FROM stripe_reconciliation_jobs"
        clauses: list[str] = []
        params: list[Any] = []
        if state is not None:
            clauses.append("state=?"); params.append(state)
        if operation_id is not None:
            clauses.append("operation_id=?"); params.append(operation_id)
        if clauses:
            query += " WHERE " + " AND ".join(clauses)
        query += " ORDER BY created_at,event_id"
        with self._db() as db:
            rows = db.execute(query, tuple(params)).fetchall()
        return [self._public_job(self._check_job(row)) for row in rows]

    def get(self, event_id: str) -> dict[str, Any] | None:
        with self._db() as db:
            row = db.execute("SELECT * FROM stripe_webhook_inbox WHERE event_id=?", (event_id,)).fetchone()
        if row is None:
            return None
        value = dict(row)
        if not hmac.compare_digest(str(value.get("row_hmac_sha256", "")), self._mac(value)):
            raise InboxIntegrityError("inbox-record-authentication-failed")
        # Do not surface the row HMAC itself through the public summary.
        value.pop("row_hmac_sha256", None)
        return value

    def find_by_operation(self, operation_id: str) -> list[dict[str, Any]]:
        if not isinstance(operation_id, str) or not re.fullmatch(r"[A-Za-z0-9._:-]{3,128}", operation_id):
            raise ValueError("operation_id is invalid")
        with self._db() as db:
            rows = db.execute("SELECT * FROM stripe_webhook_inbox WHERE operation_id=? ORDER BY received_at,event_id", (operation_id,)).fetchall()
        output: list[dict[str, Any]] = []
        for row in rows:
            value = dict(row)
            if not hmac.compare_digest(str(value.get("row_hmac_sha256", "")), self._mac(value)):
                raise InboxIntegrityError("inbox-record-authentication-failed")
            value.pop("row_hmac_sha256", None)
            output.append(value)
        return output

    def reconciliation_hint(self, *, operation_id: str, expected_target: str,
                            expected_amount: int | None, expected_currency: str) -> InboxResult:
        """Use a webhook only as a signal to retrieve current provider state.

        A correlated, shape-matching event never means refund success. Events may
        be delivered more than once or out of order, so the action is only to fetch
        the refund by ID and revalidate the current object through authenticated API.
        """
        if not isinstance(expected_target, str) or not re.fullmatch(r"(?:ch|pi)_[A-Za-z0-9_]+", expected_target):
            raise ValueError("expected_target must be a Charge or PaymentIntent identifier")
        if expected_amount is not None and (type(expected_amount) is not int or expected_amount <= 0):
            raise ValueError("expected_amount must be a positive integer or None")
        if not isinstance(expected_currency, str) or not re.fullmatch(r"[a-z]{3}", expected_currency):
            raise ValueError("expected_currency must be a lowercase three-letter code")
        rows = self.find_by_operation(operation_id)
        if not rows:
            return InboxResult(InboxAction.NO_CORRELATED_EVENT, "no-correlated-webhook-event", operation_id=operation_id)
        refunds = {row["refund_id"] for row in rows}
        if len(refunds) != 1:
            return InboxResult(InboxAction.MANUAL_RECONCILIATION, "multiple-refund-ids-correlated-to-one-operation", operation_id=operation_id)
        matching_refund = next(iter(refunds))
        for row in rows:
            if row["event_account"] != self.expected_account:
                return InboxResult(InboxAction.MANUAL_RECONCILIATION,
                                   "webhook-account-scope-does-not-match-configured-inbox",
                                   row["event_id"], operation_id)
            actual_targets = {value for value in (row["charge"], row["payment_intent"]) if value}
            if expected_target not in actual_targets:
                return InboxResult(InboxAction.MANUAL_RECONCILIATION, "webhook-target-does-not-match-persisted-operation", row["event_id"], operation_id)
            if row["currency"] != expected_currency:
                return InboxResult(InboxAction.MANUAL_RECONCILIATION, "webhook-currency-does-not-match-persisted-operation", row["event_id"], operation_id)
            if expected_amount is not None and row["amount"] != expected_amount:
                return InboxResult(InboxAction.MANUAL_RECONCILIATION, "webhook-amount-does-not-match-persisted-operation", row["event_id"], operation_id)
        return InboxResult(InboxAction.RETRIEVE_CURRENT_PROVIDER_STATE,
                           "verified-webhook-is-only-a-reconciliation-signal",
                           event_id=rows[-1]["event_id"], operation_id=operation_id,
                           refund_id=matching_refund)
