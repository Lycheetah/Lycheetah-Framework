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
import sqlite3
from contextlib import contextmanager
from typing import Any, Mapping

MAX_WEBHOOK_BODY_BYTES = 1024 * 1024
MAX_SIGNATURE_HEADER_CHARS = 16 * 1024
DEFAULT_TIMESTAMP_TOLERANCE_SECONDS = 300
ALLOWED_EVENT_TYPES = {"refund.created", "refund.updated", "refund.failed"}
OPERATION_METADATA_KEY = "lycheetah_operation_id"
INBOX_SCHEMA_VERSION = 1


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
        except InboxIntegrityError:
            return InboxResult(InboxAction.REJECTED, "inbox-record-authentication-failed", summary["event_id"], summary.get("operation_id"))
        except sqlite3.Error:
            return InboxResult(InboxAction.REJECTED, "inbox-durable-write-failed", summary["event_id"], summary.get("operation_id"))
        return InboxResult(InboxAction.INGESTED, "signature-valid-minimal-event-recorded", summary["event_id"], summary.get("operation_id"))

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
