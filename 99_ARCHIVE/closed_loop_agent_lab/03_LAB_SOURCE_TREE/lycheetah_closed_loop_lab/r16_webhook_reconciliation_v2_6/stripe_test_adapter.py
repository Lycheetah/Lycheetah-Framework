"""Test-mode-only Stripe Refund HTTP adapter for adversarial contract tests.

No live-mode keys are accepted. Local HTTP is accepted only when explicitly
configured and pointed at a loopback address. This is a reference adapter, not
an officially supported Stripe SDK and not a production-certified payment path.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum
import hashlib
import hmac
import http.client
import json
import math
import re
import sqlite3
from contextlib import contextmanager
from typing import Any, Mapping
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode, urlparse, parse_qs
from urllib.request import Request, HTTPRedirectHandler, build_opener

OPERATION_METADATA_KEY = "lycheetah_operation_id"
API_CONTRACT = "stripe-api-v1-refunds-test-adapter-2026-10-17-r2.5"
AUTOMATED_RETRY_CUTOFF_SECONDS = 23 * 60 * 60
MAX_PROVIDER_RESPONSE_BYTES = 5 * 1024 * 1024


class Action(str, Enum):
    SUCCEEDED = "SUCCEEDED"
    WAIT_FOR_PROVIDER = "WAIT_FOR_PROVIDER"
    RETRY_SAME_KEY = "RETRY_SAME_KEY"
    RECONCILE = "RECONCILE"
    NEW_APPROVAL_REQUIRED = "NEW_APPROVAL_REQUIRED"


@dataclass(frozen=True)
class Result:
    action: Action
    reason: str
    refund_id: str | None = None
    http_status: int | None = None

    def to_dict(self) -> dict[str, Any]:
        return {"action": self.action.value, "reason": self.reason,
                "refund_id": self.refund_id, "http_status": self.http_status}


class UnsafeConfiguration(ValueError):
    pass


class TransportOutcomeUnknown(OSError):
    pass


class _ProviderResponseTooLarge(Exception):
    """Internal sentinel: preserve uncertainty without retaining an oversized body."""
    pass


class StoreIntegrityError(ValueError):
    """Persisted operation record failed local HMAC authentication."""
    pass


class StoreStateTransitionError(ValueError):
    """A stale concurrent result tried to downgrade a confirmed local state."""
    pass


class _NoRedirect(HTTPRedirectHandler):
    """Do not forward authorization headers to redirects; treat redirects as contract failure."""
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


def _now_iso(dt: datetime | None = None) -> str:
    dt = dt or datetime.now(timezone.utc)
    if dt.tzinfo is None or dt.utcoffset() is None:
        raise ValueError("timestamps must be timezone-aware")
    return dt.astimezone(timezone.utc).isoformat(timespec="microseconds")


def canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, ensure_ascii=False,
                      separators=(",", ":"), allow_nan=False)


def sha256_hex(value: Any) -> str:
    if isinstance(value, str):
        body = value.encode("utf-8")
    else:
        body = canonical_json(value).encode("utf-8")
    return hashlib.sha256(body).hexdigest()


def request_fingerprint(*, account_scope: str, stripe_account: str | None,
                         api_version: str, payload: Mapping[str, Any], expected_currency: str) -> str:
    if not account_scope or not isinstance(account_scope, str):
        raise ValueError("account_scope must be explicit")
    if stripe_account is not None and (not isinstance(stripe_account, str) or not stripe_account.startswith("acct_")):
        raise ValueError("stripe_account must be a Stripe account ID or null")
    if not isinstance(api_version, str) or not api_version:
        raise ValueError("API version must be explicit")
    if not isinstance(payload, Mapping):
        raise ValueError("payload must be an object")
    if not isinstance(expected_currency, str) or not re.fullmatch(r"[a-z]{3}", expected_currency):
        raise ValueError("expected_currency must be a lowercase 3-letter code")
    return sha256_hex({"contract": API_CONTRACT, "endpoint": "POST /v1/refunds",
                       "account_scope": account_scope, "stripe_account": stripe_account,
                       "livemode": False, "api_version": api_version,
                       "expected_currency": expected_currency, "payload": payload})


def build_payload(*, operation_id: str, charge: str | None = None,
                  payment_intent: str | None = None, amount: int | None = None,
                  reason: str | None = None, metadata: Mapping[str, str] | None = None) -> dict[str, Any]:
    if not isinstance(operation_id, str) or not operation_id:
        raise ValueError("operation_id is required")
    if bool(charge) == bool(payment_intent):
        raise ValueError("exactly one of charge or payment_intent is required")
    target = charge if charge is not None else payment_intent
    if not isinstance(target, str) or not target:
        raise ValueError("refund target must be a non-empty string")
    expected_prefix = "ch_" if charge is not None else "pi_"
    if not re.fullmatch(re.escape(expected_prefix) + r"[A-Za-z0-9_]+", target):
        raise ValueError(f"refund target must be a valid {expected_prefix[:-1]}_ identifier")
    if amount is not None and (type(amount) is not int or amount <= 0):
        raise ValueError("amount must be a positive integer in minor units")
    if reason is not None and reason not in {"duplicate", "fraudulent", "requested_by_customer"}:
        raise ValueError("unsupported refund reason")
    # This reference adapter deliberately keeps caller-supplied metadata disabled.
    # The exact request body must be retained for safe idempotent recovery; persisting
    # arbitrary metadata can therefore persist PII/secrets. Correlation needs only this
    # opaque operation id. A future extension must use a reviewed allow-list and an
    # explicit data-retention contract, not silently accept arbitrary strings.
    if metadata:
        raise ValueError("custom Stripe metadata is disabled in the recovery adapter")
    md = {OPERATION_METADATA_KEY: operation_id}
    out: dict[str, Any] = {"metadata": md, "charge" if charge is not None else "payment_intent": target}
    if amount is not None:
        out["amount"] = amount
    if reason is not None:
        out["reason"] = reason
    return out


def _encode_form(payload: Mapping[str, Any]) -> bytes:
    fields: list[tuple[str, str]] = []
    for key, value in payload.items():
        if key == "metadata":
            if not isinstance(value, Mapping):
                raise ValueError("metadata must be an object")
            fields.extend((f"metadata[{k}]", str(v)) for k, v in value.items())
        elif type(value) is bool:
            fields.append((key, "true" if value else "false"))
        else:
            fields.append((key, str(value)))
    return urlencode(fields).encode("utf-8")


def _decode_json(raw: bytes) -> Mapping[str, Any] | None:
    try:
        obj = json.loads(raw.decode("utf-8"))
        return obj if isinstance(obj, Mapping) else None
    except (UnicodeDecodeError, json.JSONDecodeError):
        return None


class DurableOperationStore:
    """SQLite intent log authenticated with a local HMAC key.

    The HMAC key must be kept outside the database (for example in a secret
    manager). HMAC detects out-of-process record tampering when the key remains
    secret; it does not protect against compromise of the process or key itself.
    """
    def __init__(self, path: str, *, integrity_key: bytes):
        if not isinstance(integrity_key, bytes) or len(integrity_key) < 32:
            raise ValueError("integrity_key must be at least 32 secret bytes")
        self.path = path
        self.integrity_key = integrity_key
        with self._db() as db:
            db.execute("""CREATE TABLE IF NOT EXISTS refund_ops (
                operation_id TEXT PRIMARY KEY,
                idempotency_key TEXT UNIQUE NOT NULL,
                created_at TEXT NOT NULL,
                account_scope TEXT NOT NULL,
                stripe_account TEXT,
                api_version TEXT NOT NULL,
                charge TEXT,
                payment_intent TEXT,
                amount INTEGER,
                expected_currency TEXT NOT NULL,
                payload_json TEXT NOT NULL,
                request_sha256 TEXT NOT NULL,
                state TEXT NOT NULL,
                last_http_status INTEGER,
                provider_response_json TEXT,
                updated_at TEXT NOT NULL,
                row_hmac_sha256 TEXT NOT NULL
            )""")
            columns = {row[1] for row in db.execute("PRAGMA table_info(refund_ops)").fetchall()}
            required = {"operation_id", "idempotency_key", "created_at", "account_scope", "stripe_account",
                        "api_version", "charge", "payment_intent", "amount", "expected_currency",
                        "payload_json", "request_sha256", "state", "last_http_status",
                        "provider_response_json", "updated_at", "row_hmac_sha256"}
            if not required.issubset(columns):
                raise UnsafeConfiguration("operation database schema is older or incomplete; explicit migration is required")

    @contextmanager
    def _db(self):
        db = sqlite3.connect(self.path, timeout=10, isolation_level="DEFERRED")
        db.row_factory = sqlite3.Row
        db.execute("PRAGMA busy_timeout=10000")
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
        fields = ("operation_id", "idempotency_key", "created_at", "account_scope",
                  "stripe_account", "api_version", "charge", "payment_intent", "amount",
                  "expected_currency", "payload_json", "request_sha256", "state",
                  "last_http_status", "provider_response_json", "updated_at")
        return {field: row[field] for field in fields}

    def _mac(self, row: Mapping[str, Any]) -> str:
        body = canonical_json(self._authenticated_fields(row)).encode("utf-8")
        return hmac.new(self.integrity_key, body, hashlib.sha256).hexdigest()

    def prepare(self, *, operation_id: str, idempotency_key: str, created_at: datetime,
                account_scope: str, stripe_account: str | None, api_version: str,
                payload: Mapping[str, Any], expected_currency: str) -> None:
        if not re.fullmatch(r"[A-Za-z0-9._:-]{3,128}", operation_id):
            raise ValueError("operation_id must be a stable non-PII identifier")
        if not isinstance(idempotency_key, str) or not re.fullmatch(r"[!-~]{1,255}", idempotency_key):
            raise ValueError("idempotency key must be 1..255 visible ASCII characters without whitespace")
        if not re.fullmatch(r"[a-z]{3}", expected_currency):
            raise ValueError("expected_currency must be a lowercase 3-letter code")
        allowed_payload_fields = {"charge", "payment_intent", "amount", "reason", "metadata"}
        unknown_payload_fields = set(payload).difference(allowed_payload_fields)
        if unknown_payload_fields:
            raise ValueError("payload contains unsupported fields; use only reviewed refund parameters")
        metadata = payload.get("metadata")
        if (not isinstance(metadata, Mapping)
                or set(metadata) != {OPERATION_METADATA_KEY}
                or metadata.get(OPERATION_METADATA_KEY) != operation_id):
            raise ValueError("payload must carry only the matching Lycheetah operation metadata")
        targets = [(k, payload.get(k)) for k in ("charge", "payment_intent") if k in payload]
        if len(targets) != 1 or not isinstance(targets[0][1], str) or not targets[0][1]:
            raise ValueError("payload must identify exactly one charge or PaymentIntent")
        target_pattern = r"ch_[A-Za-z0-9_]+" if targets[0][0] == "charge" else r"pi_[A-Za-z0-9_]+"
        if not re.fullmatch(target_pattern, targets[0][1]):
            raise ValueError("payload target identifier has an invalid path-safe shape")
        amount = payload.get("amount")
        if amount is not None and (type(amount) is not int or amount <= 0):
            raise ValueError("amount must be a positive integer or absent")
        payload_json = canonical_json(payload)
        fp = request_fingerprint(account_scope=account_scope, stripe_account=stripe_account,
                                 api_version=api_version, payload=payload, expected_currency=expected_currency)
        stamp = _now_iso(created_at)
        body = {"operation_id":operation_id,"idempotency_key":idempotency_key,"created_at":stamp,
                "account_scope":account_scope,"stripe_account":stripe_account,"api_version":api_version,
                "charge":payload.get("charge"),"payment_intent":payload.get("payment_intent"),
                "amount":amount,"expected_currency":expected_currency,"payload_json":payload_json,
                "request_sha256":fp,"state":"READY","last_http_status":None,
                "provider_response_json":None,"updated_at":stamp}
        mac = self._mac(body)
        with self._db() as db:
            db.execute("BEGIN IMMEDIATE")
            db.execute("""INSERT INTO refund_ops(
                operation_id,idempotency_key,created_at,account_scope,stripe_account,api_version,
                charge,payment_intent,amount,expected_currency,payload_json,request_sha256,state,
                last_http_status,provider_response_json,updated_at,row_hmac_sha256)
                VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                (operation_id,idempotency_key,stamp,account_scope,stripe_account,api_version,
                 payload.get("charge"),payload.get("payment_intent"),amount,expected_currency,
                 payload_json,fp,"READY",None,None,stamp,mac))

    def get(self, operation_id: str) -> dict[str, Any]:
        with self._db() as db:
            row = db.execute("SELECT * FROM refund_ops WHERE operation_id=?", (operation_id,)).fetchone()
        if row is None:
            raise KeyError(f"unknown operation_id: {operation_id}")
        raw = dict(row)
        expected_mac = self._mac(raw)
        if not hmac.compare_digest(str(raw.get("row_hmac_sha256", "")), expected_mac):
            raise StoreIntegrityError("durable-operation-record-authentication-failed")
        out = raw
        out["payload"] = _decode_json(out.pop("payload_json").encode("utf-8"))
        response_json = out.pop("provider_response_json")
        out["provider_response"] = _decode_json(response_json.encode("utf-8")) if response_json else None
        out["created_at_dt"] = datetime.fromisoformat(out["created_at"])
        return out

    @staticmethod
    def _allowed_transition(old_state: str, new_state: str) -> bool:
        # This is a monotonic lifecycle contract, not merely a terminal-state guard.
        # A READY record must not be writable directly to SUCCEEDED by a generic updater.
        allowed = {
            "READY": {"READY", "PRECHECK_FAILED", "RECONCILE"},
            "IN_FLIGHT": {"UNKNOWN", "CONFLICT", "AMBIGUOUS_5XX", "RECONCILE", "SUCCEEDED", "WAITING", "NEW_APPROVAL_REQUIRED"},
            "UNKNOWN": {"UNKNOWN", "CONFLICT", "AMBIGUOUS_5XX", "RECONCILE", "SUCCEEDED", "WAITING", "NEW_APPROVAL_REQUIRED"},
            "CONFLICT": {"CONFLICT", "UNKNOWN", "AMBIGUOUS_5XX", "RECONCILE", "SUCCEEDED", "WAITING", "NEW_APPROVAL_REQUIRED"},
            "AMBIGUOUS_5XX": {"AMBIGUOUS_5XX", "RECONCILE", "SUCCEEDED", "WAITING", "NEW_APPROVAL_REQUIRED"},
            "RECONCILE": {"RECONCILE", "SUCCEEDED", "WAITING", "NEW_APPROVAL_REQUIRED"},
            "WAITING": {"WAITING", "SUCCEEDED", "NEW_APPROVAL_REQUIRED", "RECONCILE"},
            "SUCCEEDED": {"SUCCEEDED"},
            "NEW_APPROVAL_REQUIRED": {"NEW_APPROVAL_REQUIRED"},
            "PRECHECK_FAILED": {"PRECHECK_FAILED"},
        }
        return new_state in allowed.get(old_state, set())

    def claim_ready_for_dispatch(self, operation_id: str, *, now: datetime) -> bool:
        """Atomically claim a READY operation so only one local worker starts the POST."""
        updated_at = _now_iso(now)
        with self._db() as db:
            db.execute("BEGIN IMMEDIATE")
            old = db.execute("SELECT * FROM refund_ops WHERE operation_id=?", (operation_id,)).fetchone()
            if old is None:
                raise KeyError(f"unknown operation_id: {operation_id}")
            fields = dict(old)
            if not hmac.compare_digest(str(fields.get("row_hmac_sha256", "")), self._mac(fields)):
                raise StoreIntegrityError("durable-operation-record-authentication-failed")
            if fields["state"] != "READY":
                return False
            fields.update(state="IN_FLIGHT", last_http_status=None,
                          provider_response_json=None, updated_at=updated_at)
            mac = self._mac(fields)
            cursor = db.execute("""UPDATE refund_ops SET state='IN_FLIGHT',last_http_status=NULL,
                provider_response_json=NULL,updated_at=?,row_hmac_sha256=?
                WHERE operation_id=? AND state='READY'""", (updated_at, mac, operation_id))
            return cursor.rowcount == 1

    def set_result(self, operation_id: str, *, state: str, status: int | None,
                   response: Mapping[str, Any] | None, now: datetime) -> None:
        raw_response = canonical_json(response) if response is not None else None
        updated_at = _now_iso(now)
        with self._db() as db:
            db.execute("BEGIN IMMEDIATE")
            old = db.execute("SELECT * FROM refund_ops WHERE operation_id=?", (operation_id,)).fetchone()
            if old is None:
                raise KeyError(f"unknown operation_id: {operation_id}")
            fields = dict(old)
            if not hmac.compare_digest(str(fields.get("row_hmac_sha256", "")), self._mac(fields)):
                raise StoreIntegrityError("durable-operation-record-authentication-failed")
            old_state = fields["state"]
            if not self._allowed_transition(old_state, state):
                raise StoreStateTransitionError(f"refusing-state-regression:{old_state}->{state}")
            fields.update(state=state,last_http_status=status,provider_response_json=raw_response,updated_at=updated_at)
            mac = self._mac(fields)
            db.execute("""UPDATE refund_ops SET state=?,last_http_status=?,provider_response_json=?,
                updated_at=?,row_hmac_sha256=? WHERE operation_id=?""",
                (state,status,raw_response,updated_at,mac,operation_id))


class StripeTestModeRefundClient:
    """Conservative test-mode client. Refuses live keys and non-TLS remote URLs."""
    def __init__(self, *, store: DurableOperationStore, secret_key: str,
                 base_url: str = "https://api.stripe.com", account_scope: str,
                 stripe_account: str | None = None, api_version: str,
                 allow_loopback_http: bool = False, allow_custom_https_endpoint: bool = False,
                 allow_test_clock_override: bool = False, timeout_seconds: float = 5.0):
        if type(allow_loopback_http) is not bool or type(allow_custom_https_endpoint) is not bool or type(allow_test_clock_override) is not bool:
            raise UnsafeConfiguration("endpoint and clock override flags must be explicit booleans")
        if not isinstance(secret_key, str) or not re.fullmatch(r"sk_test_[A-Za-z0-9_]+", secret_key):
            raise UnsafeConfiguration("test adapter accepts only well-formed sk_test_ keys")
        parsed = urlparse(base_url)
        try:
            port = parsed.port
        except ValueError:
            raise UnsafeConfiguration("base_url contains an invalid port") from None
        if parsed.hostname == "api.stripe.com" and port not in (None, 443):
            raise UnsafeConfiguration("official Stripe hostname must use the default HTTPS port")
        if parsed.scheme != "https":
            loopback = parsed.hostname in {"127.0.0.1", "localhost", "::1"}
            if not (allow_loopback_http and loopback and parsed.scheme == "http"):
                raise UnsafeConfiguration("remote API must use HTTPS; HTTP allowed only for explicit loopback simulator")
        elif parsed.hostname != "api.stripe.com" and not allow_custom_https_endpoint:
            raise UnsafeConfiguration("HTTPS endpoint must be api.stripe.com unless a custom endpoint is explicitly approved")
        if parsed.path not in {"", "/"} or parsed.username or parsed.password or parsed.query or parsed.fragment:
            raise UnsafeConfiguration("base_url must be the root origin without credentials, path, query, or fragment")
        if (not isinstance(timeout_seconds, (int, float)) or isinstance(timeout_seconds, bool)
                or not math.isfinite(float(timeout_seconds)) or timeout_seconds <= 0):
            raise UnsafeConfiguration("timeout_seconds must be a finite positive number")
        if stripe_account is not None and not re.fullmatch(r"acct_[A-Za-z0-9]+", stripe_account):
            raise UnsafeConfiguration("stripe_account must be a Stripe account ID")
        if not isinstance(account_scope, str) or not account_scope:
            raise UnsafeConfiguration("account_scope must be explicit")
        if (not isinstance(api_version, str) or not api_version
                or any(ord(ch) < 33 or ord(ch) == 127 for ch in api_version)):
            raise UnsafeConfiguration("API version must be explicit and contain no whitespace/control characters")
        self.store = store
        self.secret_key = secret_key
        self.base_url = base_url.rstrip("/")
        self.account_scope = account_scope
        self.stripe_account = stripe_account
        self.api_version = api_version
        self.timeout_seconds = timeout_seconds
        # Supplying per-call timestamps can bypass freshness cutoffs if accidentally
        # exposed by an application. It is disabled unless a test harness opts in.
        self.allow_test_clock_override = bool(allow_test_clock_override)
        self._opener = build_opener(_NoRedirect())

    def prepare_refund(self, *, operation_id: str, idempotency_key: str, created_at: datetime,
                       charge: str | None = None, payment_intent: str | None = None,
                       amount: int | None = None, reason: str | None = None,
                       expected_currency: str = "usd", metadata: Mapping[str,str] | None = None) -> None:
        payload = build_payload(operation_id=operation_id, charge=charge, payment_intent=payment_intent,
                                amount=amount, reason=reason, metadata=metadata)
        self.store.prepare(operation_id=operation_id,idempotency_key=idempotency_key,created_at=created_at,
                           account_scope=self.account_scope,stripe_account=self.stripe_account,
                           api_version=self.api_version,payload=payload,expected_currency=expected_currency)

    @staticmethod
    def _validate_now(now: datetime | None) -> datetime:
        if now is None:
            return datetime.now(timezone.utc)
        if not isinstance(now, datetime) or now.tzinfo is None or now.utcoffset() is None:
            raise ValueError("now must be timezone-aware")
        return now

    def _resolve_public_now(self, now: datetime | None) -> datetime:
        if now is not None and not self.allow_test_clock_override:
            raise UnsafeConfiguration(
                "per-call clock override is test-only; use the system clock in normal operation"
            )
        return self._validate_now(now)

    def _persist_result(self, operation_id: str, *, state: str, status: int | None,
                        response: Mapping[str, Any] | None, now: datetime) -> bool:
        try:
            self.store.set_result(operation_id, state=state, status=status, response=response, now=now)
            return True
        except (StoreIntegrityError, StoreStateTransitionError, KeyError):
            return False

    def _headers(self, idempotency_key: str | None = None) -> dict[str,str]:
        headers = {"Authorization": f"Bearer {self.secret_key}", "Stripe-Version": self.api_version,
                   "Accept": "application/json", "User-Agent": "Lycheetah-Stripe-Test-Contract/2.5"}
        if self.stripe_account:
            headers["Stripe-Account"] = self.stripe_account
        if idempotency_key:
            headers["Idempotency-Key"] = idempotency_key
        return headers

    def _request(self, method: str, path: str, *, payload: Mapping[str,Any] | None = None,
                 query: Mapping[str,Any] | None = None, idempotency_key: str | None = None) -> tuple[int, Mapping[str,Any] | None]:
        url = self.base_url + path
        if query:
            url += "?" + urlencode(query)
        data = _encode_form(payload) if payload is not None else None
        headers = self._headers(idempotency_key)
        if data is not None:
            headers["Content-Type"] = "application/x-www-form-urlencoded"
        req = Request(url, data=data, headers=headers, method=method)
        try:
            with self._opener.open(req, timeout=self.timeout_seconds) as resp:
                status, raw = resp.status, resp.read(MAX_PROVIDER_RESPONSE_BYTES + 1)
                if len(raw) > MAX_PROVIDER_RESPONSE_BYTES:
                    raise _ProviderResponseTooLarge()
        except HTTPError as exc:
            status, raw = exc.code, exc.read(MAX_PROVIDER_RESPONSE_BYTES + 1)
            if len(raw) > MAX_PROVIDER_RESPONSE_BYTES:
                raise TransportOutcomeUnknown("provider-response-exceeded-size-limit") from None
        except _ProviderResponseTooLarge:
            # A POST might already have committed. The caller records UNKNOWN and
            # follows read-only reconciliation / same-key recovery; never parse/store it.
            raise TransportOutcomeUnknown("provider-response-exceeded-size-limit") from None
        except (URLError, TimeoutError, OSError, http.client.HTTPException) as exc:
            # Do not include exception text: it may embed request URLs or sensitive data.
            raise TransportOutcomeUnknown(f"transport outcome unknown ({type(exc).__name__})") from None
        return status, _decode_json(raw)

    def _check_snapshot(self, op: Mapping[str,Any]) -> str | None:
        if op["account_scope"] != self.account_scope or op["stripe_account"] != self.stripe_account:
            return "provider-account-scope-changed"
        if op["api_version"] != self.api_version:
            return "provider-api-version-changed"
        payload = op["payload"]
        if not isinstance(payload, Mapping):
            return "persisted-payload-not-object"
        try:
            current = request_fingerprint(account_scope=op["account_scope"], stripe_account=op["stripe_account"],
                                          api_version=op["api_version"], payload=payload,
                                          expected_currency=op["expected_currency"])
        except (TypeError, ValueError):
            return "persisted-payload-not-canonical"
        if not hmac.compare_digest(current, op["request_sha256"]):
            return "persisted-payload-fingerprint-mismatch"
        if payload.get("metadata",{}).get(OPERATION_METADATA_KEY) != op["operation_id"]:
            return "persisted-operation-correlation-mismatch"
        return None

    @staticmethod
    def _safe_target_summary(body: Mapping[str, Any] | None) -> Mapping[str, Any] | None:
        """Persist only non-sensitive fields needed to explain a failed preflight."""
        if not isinstance(body, Mapping):
            return None
        out: dict[str, Any] = {}
        for key in ("id", "object", "currency", "status"):
            if isinstance(body.get(key), str):
                out[key] = body[key]
        for key in ("livemode", "paid", "captured", "refunded"):
            if type(body.get(key)) is bool:
                out[key] = body[key]
        for key in ("amount", "amount_refunded", "amount_received"):
            if type(body.get(key)) is int:
                out[key] = body[key]
        return out

    @staticmethod
    def _safe_refund_summary(refund: Mapping[str, Any] | None) -> Mapping[str, Any] | None:
        """Store only the bounded, validated fields used by recovery classification.

        Refund objects may contain provider-specific data unrelated to this control
        loop. The local ledger needs only identity, target, amount/currency/status,
        mode and Lycheetah's operation-correlation key.
        """
        if not isinstance(refund, Mapping):
            return None
        out: dict[str, Any] = {}
        for key in ("id", "object", "charge", "payment_intent", "currency", "status"):
            if isinstance(refund.get(key), str):
                out[key] = refund[key]
        if type(refund.get("amount")) is int:
            out["amount"] = refund["amount"]
        if type(refund.get("livemode")) is bool:
            out["livemode"] = refund["livemode"]
        metadata = refund.get("metadata")
        if isinstance(metadata, Mapping) and isinstance(metadata.get(OPERATION_METADATA_KEY), str):
            out["metadata"] = {OPERATION_METADATA_KEY: metadata[OPERATION_METADATA_KEY]}
        return out

    @staticmethod
    def _safe_error_summary(body: Mapping[str, Any] | None) -> Mapping[str, Any] | None:
        """Avoid persisting provider error messages, URLs, request logs or arbitrary fields."""
        if not isinstance(body, Mapping) or not isinstance(body.get("error"), Mapping):
            return None
        error = body["error"]
        safe: dict[str, str] = {}
        for key in ("type", "code", "param", "decline_code"):
            if isinstance(error.get(key), str):
                safe[key] = error[key]
        return {"error": safe} if safe else None

    def _preflight_target(self, op: Mapping[str, Any]) -> tuple[str | None, int | None, Mapping[str, Any] | None, bool]:
        """Validate immutable target identity/mode/currency before the first refund POST.

        Returns (reason, HTTP status, body, retryable_transport_or_service_failure).
        This does not atomically reserve refundable balance; Stripe remains the final
        authority for amount/race constraints.
        """
        payload = op["payload"]
        target_key = "charge" if "charge" in payload else "payment_intent"
        target_id = payload[target_key]
        resource_type = "charges" if target_key == "charge" else "payment_intents"
        expected_object = "charge" if target_key == "charge" else "payment_intent"
        try:
            status, body = self._request("GET", f"/v1/{resource_type}/{target_id}")
        except TransportOutcomeUnknown:
            return "target-preflight-transport-outcome-unknown; refund POST was not sent", None, None, True
        if status in {408, 425, 429} or status >= 500:
            return "target-preflight-provider-unavailable; refund POST was not sent", status, body, True
        if status < 200 or status >= 300 or not isinstance(body, Mapping):
            return "target-preflight-resource-unavailable-or-response-invalid; refund POST was not sent", status, body, True
        if body.get("object") != expected_object or body.get("id") != target_id:
            return "target-preflight-resource-identity-mismatch", status, body, False
        if body.get("livemode") is not False:
            return "target-preflight-resource-not-explicitly-test-mode", status, body, False
        if body.get("currency") != op["expected_currency"]:
            return "target-preflight-currency-mismatch", status, body, False
        amount = payload.get("amount")
        if target_key == "charge":
            if body.get("paid") is not True or body.get("captured") is not True:
                return "target-preflight-charge-not-paid-and-captured", status, body, False
            total = body.get("amount")
            refunded = body.get("amount_refunded")
            if type(total) is not int or type(refunded) is not int or total <= 0 or refunded < 0 or refunded > total:
                return "target-preflight-charge-amount-fields-invalid", status, body, False
            remaining = total - refunded
            if remaining <= 0:
                return "target-preflight-charge-has-no-refundable-balance", status, body, False
            if amount is not None and amount > remaining:
                return "target-preflight-request-exceeds-remaining-charge-balance", status, body, False
        else:
            if body.get("status") != "succeeded":
                return "target-preflight-payment-intent-not-succeeded", status, body, False
            received = body.get("amount_received")
            if type(received) is not int or received <= 0:
                return "target-preflight-payment-intent-has-no-received-funds", status, body, False
            if amount is not None and amount > received:
                return "target-preflight-request-exceeds-payment-intent-received-amount", status, body, False
        return None, status, body, False

    def dispatch(self, operation_id: str, *, now: datetime | None = None) -> Result:
        """Perform the first dispatch only; use recover() for any uncertain/repeated send.

        The retry-window check lives here as well as in recover(), so callers cannot
        bypass the cutoff by directly invoking dispatch on an old persisted row.
        """
        now = self._resolve_public_now(now)
        return self._dispatch_persisted(operation_id, now=now, recovery=False)

    def _dispatch_persisted(self, operation_id: str, *, now: datetime, recovery: bool) -> Result:
        try:
            op = self.store.get(operation_id)
        except (StoreIntegrityError, KeyError):
            return Result(Action.RECONCILE, "durable-operation-record-authentication-failed")
        error = self._check_snapshot(op)
        if error:
            return Result(Action.RECONCILE, error)

        state = op["state"]
        if state not in {"READY", "IN_FLIGHT", "UNKNOWN", "CONFLICT"}:
            return Result(Action.RECONCILE, "operation-state-not-dispatchable")
        age = (now.astimezone(timezone.utc) - op["created_at_dt"].astimezone(timezone.utc)).total_seconds()
        if age < 0:
            return Result(Action.RECONCILE, "operation-created-in-future")
        if age >= AUTOMATED_RETRY_CUTOFF_SECONDS:
            # Even a READY/IN_FLIGHT row might be a crash-recovery artifact. Never
            # send a POST past the local cutoff; reconcile by read-only lookups.
            return self._reconcile_at(operation_id, now=now)
        if not recovery and state != "READY":
            return Result(Action.RECONCILE, "non-ready-operation-must-use-recover-path")

        # READY means no dispatch marker was durably written yet. Validate the
        # target object before the first POST; IN_FLIGHT/UNKNOWN/CONFLICT use the
        # same saved request+key because a provider effect may already exist.
        if state == "READY":
            reason, preflight_status, preflight_body, retryable = self._preflight_target(op)
            if reason:
                if not retryable:
                    if not self._persist_result(operation_id, state="PRECHECK_FAILED", status=preflight_status,
                                                response=self._safe_target_summary(preflight_body), now=now):
                        return Result(Action.RECONCILE, "local-ledger-update-rejected-after-target-preflight", http_status=preflight_status)
                    return Result(Action.NEW_APPROVAL_REQUIRED, reason, http_status=preflight_status)
                return Result(Action.RECONCILE, reason, http_status=preflight_status)
            try:
                claimed = self.store.claim_ready_for_dispatch(operation_id, now=now)
            except (StoreIntegrityError, KeyError):
                return Result(Action.RECONCILE, "local-ledger-update-rejected-before-provider-post")
            if not claimed:
                return Result(Action.RECONCILE, "dispatch-claim-lost-to-concurrent-worker")
            # Reload the authenticated in-flight row before sending the request.
            try:
                op = self.store.get(operation_id)
            except (StoreIntegrityError, KeyError):
                return Result(Action.RECONCILE, "durable-operation-record-authentication-failed-before-provider-post")
            error = self._check_snapshot(op)
            if error:
                return Result(Action.RECONCILE, error)
        # Intent and IN_FLIGHT marker are durably stored before this network call.
        try:
            status, body = self._request("POST", "/v1/refunds", payload=op["payload"],
                                         idempotency_key=op["idempotency_key"])
        except TransportOutcomeUnknown as exc:
            if not self._persist_result(operation_id, state="UNKNOWN", status=None, response=None, now=now):
                return Result(Action.RECONCILE, "local-ledger-update-rejected-after-unknown-provider-outcome")
            return Result(Action.RECONCILE, str(exc))
        if status == 409 and isinstance(body, Mapping) and isinstance(body.get("error"), Mapping) and body["error"].get("code") == "idempotency_key_in_use":
            if not self._persist_result(operation_id, state="CONFLICT", status=status, response=self._safe_error_summary(body), now=now):
                return Result(Action.RECONCILE, "local-ledger-update-rejected-after-provider-conflict", http_status=status)
            return Result(Action.RETRY_SAME_KEY, "provider-reports-concurrent-same-key-operation", http_status=status)
        if status >= 500:
            if not self._persist_result(operation_id, state="AMBIGUOUS_5XX", status=status, response=self._safe_error_summary(body), now=now):
                return Result(Action.RECONCILE, "local-ledger-update-rejected-after-provider-error", http_status=status)
            return Result(Action.RECONCILE, "API-v1-may-cache-server-error; do-not-blindly-retry", http_status=status)
        if status < 200 or status >= 300 or not isinstance(body, Mapping):
            if not self._persist_result(operation_id, state="RECONCILE", status=status, response=self._safe_error_summary(body), now=now):
                return Result(Action.RECONCILE, "local-ledger-update-rejected-after-provider-response", http_status=status)
            return Result(Action.RECONCILE, "provider-rejected-request-or-response-invalid", http_status=status)
        classified = self._classify_refund(op, body, status)
        state_for_action = {Action.SUCCEEDED: "SUCCEEDED", Action.WAIT_FOR_PROVIDER: "WAITING",
                            Action.NEW_APPROVAL_REQUIRED: "NEW_APPROVAL_REQUIRED"}.get(classified.action, "RECONCILE")
        if not self._persist_result(operation_id, state=state_for_action, status=status,
                                    response=self._safe_refund_summary(body), now=now):
            return Result(Action.RECONCILE, "local-ledger-update-rejected-after-provider-response; outcome-may-have-committed", http_status=status)
        return classified

    def recover(self, operation_id: str, *, now: datetime | None = None) -> Result:
        now = self._resolve_public_now(now)
        try:
            op = self.store.get(operation_id)
        except (StoreIntegrityError, KeyError):
            return Result(Action.RECONCILE, "durable-operation-record-authentication-failed")
        error = self._check_snapshot(op)
        if error:
            return Result(Action.RECONCILE, error)
        state = op["state"]
        if state == "PRECHECK_FAILED":
            return Result(Action.NEW_APPROVAL_REQUIRED,
                          "target-preflight-failed; no refund POST was sent; use a new reviewed operation")
        if state in {"SUCCEEDED", "NEW_APPROVAL_REQUIRED"}:
            response = op.get("provider_response")
            if not isinstance(response, Mapping) or type(op.get("last_http_status")) is not int:
                return Result(Action.RECONCILE, "terminal-state-missing-authenticated-provider-response")
            classified = self._classify_refund(op, response, op["last_http_status"])
            expected_state = {Action.SUCCEEDED: "SUCCEEDED", Action.NEW_APPROVAL_REQUIRED: "NEW_APPROVAL_REQUIRED"}.get(classified.action)
            if expected_state != state:
                return Result(Action.RECONCILE, "stored-state-provider-response-classification-mismatch")
            return classified
        if state == "WAITING":
            response = op.get("provider_response")
            if not isinstance(response, Mapping) or type(op.get("last_http_status")) is not int:
                return Result(Action.RECONCILE, "waiting-state-missing-authenticated-provider-response")
            classification = self._classify_refund(op, response, op["last_http_status"])
            if classification.action != Action.WAIT_FOR_PROVIDER:
                return Result(Action.RECONCILE, "stored-waiting-state-provider-response-mismatch")
            # Nonterminal provider state must be polled/reconciled, not returned forever.
            return self._reconcile_at(operation_id, now=now)
        if state in {"AMBIGUOUS_5XX", "RECONCILE"}:
            return self._reconcile_at(operation_id, now=now)
        if state not in {"READY", "IN_FLIGHT", "UNKNOWN", "CONFLICT"}:
            return Result(Action.RECONCILE, "operation-state-not-recoverable")
        age = (now.astimezone(timezone.utc) - op["created_at_dt"].astimezone(timezone.utc)).total_seconds()
        if age < 0:
            return Result(Action.RECONCILE, "operation-created-in-future")
        if age >= AUTOMATED_RETRY_CUTOFF_SECONDS:
            return self._reconcile_at(operation_id, now=now)
        return self._dispatch_persisted(operation_id, now=now, recovery=True)

    def _classify_refund(self, op: Mapping[str,Any], refund: Mapping[str,Any], status: int) -> Result:
        if refund.get("object") != "refund" or not isinstance(refund.get("id"),str) or not refund.get("id"):
            return Result(Action.RECONCILE,"provider-response-is-not-a-valid-refund-object",http_status=status)
        payload=op["payload"]
        if not isinstance(refund.get("metadata"),Mapping) or refund["metadata"].get(OPERATION_METADATA_KEY) != op["operation_id"]:
            return Result(Action.RECONCILE,"provider-refund-correlation-metadata-mismatch",http_status=status)
        key = "charge" if "charge" in payload else "payment_intent"
        if refund.get(key) != payload.get(key):
            return Result(Action.RECONCILE,"provider-refund-target-mismatch",http_status=status)
        if "amount" in payload and refund.get("amount") != payload["amount"]:
            return Result(Action.RECONCILE,"provider-refund-amount-mismatch",http_status=status)
        if refund.get("currency") != op["expected_currency"]:
            return Result(Action.RECONCILE,"provider-refund-currency-mismatch",http_status=status)
        if refund.get("livemode") is not False:
            return Result(Action.RECONCILE,"provider-response-missing-explicit-test-mode-marker",http_status=status)
        status_value=refund.get("status")
        if status_value == "succeeded":
            return Result(Action.SUCCEEDED,"provider-confirmed-matching-refund",refund["id"],status)
        if status_value in {"pending","requires_action"}:
            return Result(Action.WAIT_FOR_PROVIDER,"refund-exists-but-is-not-terminal-success",refund["id"],status)
        if status_value in {"failed","canceled"}:
            return Result(Action.NEW_APPROVAL_REQUIRED,"refund-failed-or-canceled; new effect requires new approval",refund["id"],status)
        return Result(Action.RECONCILE,"unknown-or-missing-refund-status",refund["id"],status)

    def reconcile(self, operation_id: str, *, now: datetime | None = None,
                  page_limit: int = 10, max_pages: int = 100) -> Result:
        now = self._resolve_public_now(now)
        return self._reconcile_at(operation_id, now=now, page_limit=page_limit, max_pages=max_pages)

    def _reconcile_at(self, operation_id: str, *, now: datetime,
                      page_limit: int = 10, max_pages: int = 100) -> Result:
        if type(page_limit) is not int or not 1 <= page_limit <= 100:
            raise ValueError("page_limit must be an integer from 1 through 100")
        if type(max_pages) is not int or not 1 <= max_pages <= 1000:
            raise ValueError("max_pages must be an integer from 1 through 1000")
        try:
            op=self.store.get(operation_id)
        except (StoreIntegrityError, KeyError):
            return Result(Action.RECONCILE,"durable-operation-record-authentication-failed")
        error=self._check_snapshot(op)
        if error:
            return Result(Action.RECONCILE,error)
        payload=op["payload"]
        target_key = "charge" if "charge" in payload else "payment_intent"
        query: dict[str,Any]={target_key:payload[target_key],"limit":page_limit}
        cursor=None
        seen:set[str]=set()
        matches:list[Mapping[str,Any]]=[]
        pages_read=0
        while True:
            if pages_read >= max_pages:
                return Result(Action.RECONCILE,"refund-list-max-page-budget-reached")
            pages_read += 1
            q=dict(query)
            if cursor is not None:
                q["starting_after"]=cursor
            try:
                status,body=self._request("GET","/v1/refunds",query=q)
            except TransportOutcomeUnknown as exc:
                return Result(Action.RECONCILE,str(exc))
            if status < 200 or status >= 300 or not isinstance(body,Mapping):
                return Result(Action.RECONCILE,"refund-list-request-failed-or-response-invalid",http_status=status)
            if body.get("object") != "list" or type(body.get("has_more")) is not bool or not isinstance(body.get("data"),list):
                return Result(Action.RECONCILE,"refund-list-envelope-invalid",http_status=status)
            items=body["data"]
            for item in items:
                if not isinstance(item,Mapping) or not isinstance(item.get("id"),str) or not item.get("id"):
                    return Result(Action.RECONCILE,"refund-list-item-invalid",http_status=status)
                if item["id"] in seen:
                    return Result(Action.RECONCILE,"refund-list-duplicate-id",http_status=status)
                seen.add(item["id"])
                md=item.get("metadata")
                if isinstance(md,Mapping) and md.get(OPERATION_METADATA_KEY)==op["operation_id"]:
                    matches.append(item)
            if body["has_more"]:
                if not items:
                    return Result(Action.RECONCILE,"refund-list-has-more-with-empty-page",http_status=status)
                next_cursor=items[-1]["id"]
                if next_cursor == cursor:
                    return Result(Action.RECONCILE,"refund-list-cursor-did-not-advance",http_status=status)
                cursor=next_cursor
                continue
            break
        if len(matches)==0:
            return Result(Action.RECONCILE,"no-correlated-refund-found; absence-is-not-proof-of-no-effect")
        if len(matches)>1:
            return Result(Action.RECONCILE,"multiple-refunds-share-operation-correlation")
        classified = self._classify_refund(op, matches[0], 200)
        state_for_action = {Action.SUCCEEDED: "SUCCEEDED", Action.WAIT_FOR_PROVIDER: "WAITING",
                            Action.NEW_APPROVAL_REQUIRED: "NEW_APPROVAL_REQUIRED"}.get(classified.action)
        if state_for_action is not None:
            if not self._persist_result(operation_id, state=state_for_action, status=200,
                                         response=self._safe_refund_summary(matches[0]), now=now):
                return Result(Action.RECONCILE, "local-ledger-update-rejected-after-provider-reconciliation", http_status=200)
        return classified
