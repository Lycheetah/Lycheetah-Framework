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
import re
import sqlite3
from contextlib import contextmanager
from typing import Any, Mapping
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode, urlparse, parse_qs
from urllib.request import Request, HTTPRedirectHandler, build_opener

OPERATION_METADATA_KEY = "lycheetah_operation_id"
API_CONTRACT = "stripe-api-v1-refunds-test-adapter-2026-10-17"
AUTOMATED_RETRY_CUTOFF_SECONDS = 23 * 60 * 60


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


class StoreIntegrityError(ValueError):
    """Persisted operation record failed local HMAC authentication."""
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
    if amount is not None and (type(amount) is not int or amount <= 0):
        raise ValueError("amount must be a positive integer in minor units")
    if reason is not None and reason not in {"duplicate", "fraudulent", "requested_by_customer"}:
        raise ValueError("unsupported refund reason")
    md = dict(metadata or {})
    if any(not isinstance(k, str) or not isinstance(v, str) for k, v in md.items()):
        raise ValueError("metadata keys and values must be strings")
    if OPERATION_METADATA_KEY in md:
        raise ValueError("reserved operation metadata key cannot be overridden")
    md[OPERATION_METADATA_KEY] = operation_id
    if len(md) > 50 or any(not k or len(k) > 40 or "[" in k or "]" in k or len(v) > 500 for k, v in md.items()):
        raise ValueError("metadata exceeds supported Stripe shape limits")
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
        if not isinstance(idempotency_key, str) or not idempotency_key or len(idempotency_key) > 255:
            raise ValueError("idempotency key must be 1..255 characters")
        if not re.fullmatch(r"[a-z]{3}", expected_currency):
            raise ValueError("expected_currency must be a lowercase 3-letter code")
        metadata = payload.get("metadata")
        if not isinstance(metadata, Mapping) or metadata.get(OPERATION_METADATA_KEY) != operation_id:
            raise ValueError("payload must carry the matching operation metadata")
        targets = [(k, payload.get(k)) for k in ("charge", "payment_intent") if k in payload]
        if len(targets) != 1 or not isinstance(targets[0][1], str) or not targets[0][1]:
            raise ValueError("payload must identify exactly one charge or PaymentIntent")
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
                 timeout_seconds: float = 5.0):
        if not isinstance(secret_key, str) or not secret_key.startswith("sk_test_"):
            raise UnsafeConfiguration("test adapter accepts only sk_test_ keys")
        parsed = urlparse(base_url)
        if parsed.scheme != "https":
            loopback = parsed.hostname in {"127.0.0.1", "localhost", "::1"}
            if not (allow_loopback_http and loopback and parsed.scheme == "http"):
                raise UnsafeConfiguration("remote API must use HTTPS; HTTP allowed only for explicit loopback simulator")
        elif parsed.hostname != "api.stripe.com" and not allow_custom_https_endpoint:
            raise UnsafeConfiguration("HTTPS endpoint must be api.stripe.com unless a custom endpoint is explicitly approved")
        if parsed.path not in {"", "/"} or parsed.username or parsed.password or parsed.query or parsed.fragment:
            raise UnsafeConfiguration("base_url must be the root origin without credentials, path, query, or fragment")
        if not isinstance(timeout_seconds, (int, float)) or isinstance(timeout_seconds, bool) or timeout_seconds <= 0:
            raise UnsafeConfiguration("timeout_seconds must be a positive number")
        if stripe_account is not None and not re.fullmatch(r"acct_[A-Za-z0-9]+", stripe_account):
            raise UnsafeConfiguration("stripe_account must be a Stripe account ID")
        if not isinstance(account_scope, str) or not account_scope or not isinstance(api_version, str) or not api_version:
            raise UnsafeConfiguration("account_scope and API version must be explicit")
        self.store = store
        self.secret_key = secret_key
        self.base_url = base_url.rstrip("/")
        self.account_scope = account_scope
        self.stripe_account = stripe_account
        self.api_version = api_version
        self.timeout_seconds = timeout_seconds
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

    def _persist_result(self, operation_id: str, *, state: str, status: int | None,
                        response: Mapping[str, Any] | None, now: datetime) -> bool:
        try:
            self.store.set_result(operation_id, state=state, status=status, response=response, now=now)
            return True
        except (StoreIntegrityError, KeyError):
            return False

    def _headers(self, idempotency_key: str | None = None) -> dict[str,str]:
        headers = {"Authorization": f"Bearer {self.secret_key}", "Stripe-Version": self.api_version,
                   "Accept": "application/json", "User-Agent": "Lycheetah-Stripe-Test-Contract/2.3"}
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
                status, raw = resp.status, resp.read()
        except HTTPError as exc:
            status, raw = exc.code, exc.read()
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

    def dispatch(self, operation_id: str, *, now: datetime | None = None) -> Result:
        now = self._validate_now(now)
        try:
            op = self.store.get(operation_id)
        except (StoreIntegrityError, KeyError):
            return Result(Action.RECONCILE,"durable-operation-record-authentication-failed")
        error = self._check_snapshot(op)
        if error:
            return Result(Action.RECONCILE,error)
        if op["state"] not in {"READY","UNKNOWN","CONFLICT"}:
            return Result(Action.RECONCILE,"operation-state-not-dispatchable")
        # The READY state indicates intent was durably inserted before this network call.
        try:
            status, body = self._request("POST","/v1/refunds",payload=op["payload"],
                                         idempotency_key=op["idempotency_key"])
        except TransportOutcomeUnknown as exc:
            if not self._persist_result(operation_id,state="UNKNOWN",status=None,response=None,now=now):
                return Result(Action.RECONCILE,"local-ledger-authentication-failed-after-unknown-provider-outcome")
            return Result(Action.RECONCILE,str(exc))
        if status == 409 and isinstance(body,Mapping) and isinstance(body.get("error"),Mapping) and body["error"].get("code") == "idempotency_key_in_use":
            if not self._persist_result(operation_id,state="CONFLICT",status=status,response=body,now=now):
                return Result(Action.RECONCILE,"local-ledger-authentication-failed-after-provider-conflict",http_status=status)
            return Result(Action.RETRY_SAME_KEY,"provider-reports-concurrent-same-key-operation",http_status=status)
        if status >= 500:
            if not self._persist_result(operation_id,state="AMBIGUOUS_5XX",status=status,response=body,now=now):
                return Result(Action.RECONCILE,"local-ledger-authentication-failed-after-provider-error",http_status=status)
            return Result(Action.RECONCILE,"API-v1-may-cache-server-error; do-not-blindly-retry",http_status=status)
        if status < 200 or status >= 300 or not isinstance(body,Mapping):
            if not self._persist_result(operation_id,state="RECONCILE",status=status,response=body,now=now):
                return Result(Action.RECONCILE,"local-ledger-authentication-failed-after-provider-response",http_status=status)
            return Result(Action.RECONCILE,"provider-rejected-request-or-response-invalid",http_status=status)
        classified = self._classify_refund(op,body,status)
        state = {Action.SUCCEEDED:"SUCCEEDED",Action.WAIT_FOR_PROVIDER:"WAITING",Action.NEW_APPROVAL_REQUIRED:"NEW_APPROVAL_REQUIRED"}.get(classified.action,"RECONCILE")
        if not self._persist_result(operation_id,state=state,status=status,response=body,now=now):
            return Result(Action.RECONCILE,"local-ledger-authentication-failed-after-provider-response; outcome-may-have-committed",http_status=status)
        return classified

    def recover(self, operation_id: str, *, now: datetime | None = None) -> Result:
        now = self._validate_now(now)
        try:
            op = self.store.get(operation_id)
        except (StoreIntegrityError, KeyError):
            return Result(Action.RECONCILE,"durable-operation-record-authentication-failed")
        error = self._check_snapshot(op)
        if error:
            return Result(Action.RECONCILE,error)
        if op["state"] in {"SUCCEEDED","WAITING","NEW_APPROVAL_REQUIRED"}:
            if op["state"] == "SUCCEEDED":
                return Result(Action.SUCCEEDED,"stored-success",(op["provider_response"] or {}).get("id"),op["last_http_status"])
            if op["state"] == "WAITING":
                return Result(Action.WAIT_FOR_PROVIDER,"stored-nonterminal-provider-state",(op["provider_response"] or {}).get("id"),op["last_http_status"])
            return Result(Action.NEW_APPROVAL_REQUIRED,"stored-terminal-failure",(op["provider_response"] or {}).get("id"),op["last_http_status"])
        if op["state"] in {"AMBIGUOUS_5XX", "RECONCILE"}:
            return self.reconcile(operation_id, now=now)
        age = (now.astimezone(timezone.utc) - op["created_at_dt"].astimezone(timezone.utc)).total_seconds()
        if age < 0 or age >= AUTOMATED_RETRY_CUTOFF_SECONDS:
            return self.reconcile(operation_id, now=now)
        if op["state"] not in {"UNKNOWN","CONFLICT","READY"}:
            return Result(Action.RECONCILE,"operation-state-not-recoverable")
        # Explicit recovery reuses the persisted bytes+key, never caller-provided replacements.
        return self.dispatch(operation_id, now=now)

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
                  page_limit: int = 100, max_pages: int = 100) -> Result:
        now=self._validate_now(now)
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
        return self._classify_refund(op,matches[0],200)
