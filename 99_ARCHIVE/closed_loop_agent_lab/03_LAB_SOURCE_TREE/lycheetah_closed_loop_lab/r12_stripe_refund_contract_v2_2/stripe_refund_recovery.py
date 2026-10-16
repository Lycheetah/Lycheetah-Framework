"""Offline recovery policy for Stripe API v1 refund creation.

This module performs no network requests and imports no Stripe SDK. It encodes a
conservative decision policy based on the documented API v1 idempotency contract.
It does not assert that Stripe atomically enforces Lycheetah's external evidence
or authorization predicates at the refund-commit boundary.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum
import hashlib
import hmac
import json
import re
import uuid
from typing import Any, Mapping, Sequence

CONTRACT_ID = "stripe-api-v1-refunds-2026-10-17"
DOCUMENTED_PRUNE_FLOOR_SECONDS = 24 * 60 * 60
# Deliberate margin: stop automated retry before the documented minimum window.
AUTOMATED_RETRY_CUTOFF_SECONDS = 23 * 60 * 60
OPERATION_METADATA_KEY = "lycheetah_operation_id"


class RecoveryAction(str, Enum):
    RETRY_SAME_KEY = "RETRY_SAME_KEY"
    ACCEPT_SUCCEEDED = "ACCEPT_SUCCEEDED"
    WAIT_FOR_PROVIDER = "WAIT_FOR_PROVIDER"
    NEW_APPROVAL_REQUIRED = "NEW_APPROVAL_REQUIRED"
    RECONCILE = "RECONCILE"


class ObservedOutcome(str, Enum):
    NETWORK_OUTCOME_UNKNOWN = "NETWORK_OUTCOME_UNKNOWN"
    CONCURRENT_IDEMPOTENCY_CONFLICT = "CONCURRENT_IDEMPOTENCY_CONFLICT"
    STORED_SERVER_ERROR = "STORED_SERVER_ERROR"
    AUTHORITATIVE_RESPONSE = "AUTHORITATIVE_RESPONSE"


@dataclass(frozen=True)
class RefundOperation:
    operation_id: str
    idempotency_key: str
    created_at: datetime
    account_scope: str
    livemode: bool
    api_version: str
    charge: str | None
    payment_intent: str | None
    amount: int | None
    expected_currency: str
    request_fingerprint_sha256: str

    def __post_init__(self) -> None:
        if not self.operation_id or not isinstance(self.operation_id, str):
            raise ValueError("operation_id must be a non-empty string")
        if not isinstance(self.idempotency_key, str) or not self.idempotency_key or len(self.idempotency_key) > 255:
            raise ValueError("idempotency_key must be a string of 1..255 characters")
        if not isinstance(self.created_at, datetime) or self.created_at.tzinfo is None:
            raise ValueError("created_at must be timezone-aware")
        if self.charge is not None and (not isinstance(self.charge, str) or not self.charge):
            raise ValueError("charge must be a non-empty string when supplied")
        if self.payment_intent is not None and (not isinstance(self.payment_intent, str) or not self.payment_intent):
            raise ValueError("payment_intent must be a non-empty string when supplied")
        if bool(self.charge) == bool(self.payment_intent):
            raise ValueError("exactly one of charge or payment_intent is required")
        if self.amount is not None and (type(self.amount) is not int or self.amount <= 0):
            raise ValueError("amount must be a positive integer in minor currency units")
        if not re.fullmatch(r"[a-f0-9]{64}", self.request_fingerprint_sha256):
            raise ValueError("request_fingerprint_sha256 must be a lowercase SHA-256 hex digest")
        if not isinstance(self.expected_currency, str) or not re.fullmatch(r"[a-z]{3}", self.expected_currency):
            raise ValueError("expected_currency must be a lowercase 3-letter currency code")
        if type(self.livemode) is not bool:
            raise ValueError("livemode must be a boolean")
        if not isinstance(self.account_scope, str) or not self.account_scope or not isinstance(self.api_version, str) or not self.api_version:
            raise ValueError("account_scope and api_version must be explicit strings")


@dataclass(frozen=True)
class RefundListPage:
    """One provider list response and the cursor actually sent for that request."""
    requested_starting_after: str | None
    response: Mapping[str, Any]


@dataclass(frozen=True)
class RecoveryDecision:
    action: RecoveryAction
    reason: str
    automated: bool
    matched_refund_id: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "action": self.action.value,
            "reason": self.reason,
            "automated": self.automated,
            "matched_refund_id": self.matched_refund_id,
        }


def canonical_sha256(value: Any) -> str:
    data = json.dumps(value, sort_keys=True, ensure_ascii=False, separators=(",", ":"), allow_nan=False).encode("utf-8")
    return hashlib.sha256(data).hexdigest()


def new_operation_identity() -> tuple[str, str]:
    """Return fresh non-PII identifiers to persist before any network call.

    The idempotency key must be stored durably and reused as-is after recovery;
    never call this helper to regenerate a key for an already-created operation.
    """
    operation_id = str(uuid.uuid4())
    return operation_id, f"lyc-refund-{uuid.uuid4()}"


def build_refund_request(
    *, operation_id: str, idempotency_key: str,
    charge: str | None = None, payment_intent: str | None = None,
    amount: int | None = None, reason: str | None = None,
    additional_metadata: Mapping[str, str] | None = None,
) -> dict[str, Any]:
    """Build the immutable v1 refund request payload. Caller must persist it."""
    if charge is not None and (not isinstance(charge, str) or not charge):
        raise ValueError("charge must be a non-empty string when supplied")
    if payment_intent is not None and (not isinstance(payment_intent, str) or not payment_intent):
        raise ValueError("payment_intent must be a non-empty string when supplied")
    if bool(charge) == bool(payment_intent):
        raise ValueError("exactly one of charge or payment_intent is required")
    if not isinstance(operation_id, str) or not operation_id:
        raise ValueError("operation_id must be a non-empty string")
    if not isinstance(idempotency_key, str) or not idempotency_key or len(idempotency_key) > 255:
        raise ValueError("idempotency_key must be a string of 1..255 characters")
    if amount is not None and (type(amount) is not int or amount <= 0):
        raise ValueError("amount must be a positive integer in minor currency units")
    if reason is not None and reason not in {"duplicate", "fraudulent", "requested_by_customer"}:
        raise ValueError("unsupported Stripe refund reason")
    metadata = dict(additional_metadata or {})
    if any(not isinstance(k, str) or not isinstance(v, str) for k, v in metadata.items()):
        raise ValueError("metadata keys and values must be strings")
    if OPERATION_METADATA_KEY in metadata:
        raise ValueError("reserved operation metadata key cannot be overridden")
    if len(metadata) + 1 > 50:
        raise ValueError("Stripe metadata allows at most 50 keys")
    if any(len(k) > 40 or "[" in k or "]" in k or len(v) > 500 for k, v in metadata.items()):
        raise ValueError("metadata keys/values exceed documented shape constraints")
    metadata[OPERATION_METADATA_KEY] = operation_id
    if len(OPERATION_METADATA_KEY) > 40 or len(operation_id) > 500:
        raise ValueError("operation metadata does not fit Stripe's metadata limits")
    payload: dict[str, Any] = {"metadata": metadata}
    payload["charge" if charge else "payment_intent"] = charge or payment_intent
    if amount is not None:
        payload["amount"] = amount
    if reason is not None:
        payload["reason"] = reason
    # Idempotency key is an HTTP header, intentionally not included in body hash.
    return payload


def operation_fingerprint(*, account_scope: str, livemode: bool, api_version: str, payload: Mapping[str, Any]) -> str:
    """Bind durable local operation identity to tenant/mode/API version/body."""
    if not isinstance(account_scope, str) or not account_scope:
        raise ValueError("account_scope must be a non-empty string")
    if type(livemode) is not bool:
        raise ValueError("livemode must be a boolean")
    if not isinstance(api_version, str) or not api_version:
        raise ValueError("api_version must be a non-empty string")
    if not isinstance(payload, Mapping):
        raise ValueError("payload must be a mapping")
    return canonical_sha256({
        "contract": CONTRACT_ID,
        "account_scope": account_scope,
        "livemode": livemode,
        "api_version": api_version,
        "endpoint": "POST /v1/refunds",
        "payload": payload,
    })


def decide_recovery(
    operation: RefundOperation,
    *,
    now: datetime,
    observed: ObservedOutcome,
    retry_idempotency_key: str,
    retry_payload: Mapping[str, Any],
    current_account_scope: str,
    current_livemode: bool,
    current_api_version: str,
) -> RecoveryDecision:
    """Compute request/context identity; never trust caller-supplied match booleans.

    The caller must pass the exact payload snapshot it intends to send. The
    dispatch layer should persist and send that same immutable snapshot rather
    than rebuilding/mutating it after this decision.
    """
    if not isinstance(now, datetime) or now.tzinfo is None:
        raise ValueError("now must be timezone-aware")
    if not isinstance(current_account_scope, str) or not current_account_scope:
        return RecoveryDecision(RecoveryAction.RECONCILE, "missing-current-provider-account-scope", False)
    if type(current_livemode) is not bool:
        return RecoveryDecision(RecoveryAction.RECONCILE, "invalid-current-provider-mode", False)
    if not isinstance(current_api_version, str) or not current_api_version:
        return RecoveryDecision(RecoveryAction.RECONCILE, "missing-current-api-version", False)
    if not isinstance(retry_idempotency_key, str) or retry_idempotency_key != operation.idempotency_key:
        return RecoveryDecision(RecoveryAction.RECONCILE, "idempotency-key-differs-from-persisted-operation", False)
    if current_account_scope != operation.account_scope:
        return RecoveryDecision(RecoveryAction.RECONCILE, "provider-account-scope-mismatch", False)
    if current_livemode is not operation.livemode:
        return RecoveryDecision(RecoveryAction.RECONCILE, "provider-live-test-mode-mismatch", False)
    if current_api_version != operation.api_version:
        return RecoveryDecision(RecoveryAction.RECONCILE, "provider-api-version-mismatch", False)
    try:
        retry_fingerprint = operation_fingerprint(
            account_scope=current_account_scope,
            livemode=current_livemode,
            api_version=current_api_version,
            payload=retry_payload,
        )
    except (TypeError, ValueError):
        return RecoveryDecision(RecoveryAction.RECONCILE, "retry-payload-not-canonical-json", False)
    if not hmac.compare_digest(retry_fingerprint, operation.request_fingerprint_sha256):
        return RecoveryDecision(RecoveryAction.RECONCILE, "retry-payload-fingerprint-mismatch", False)
    age = (now.astimezone(timezone.utc) - operation.created_at.astimezone(timezone.utc)).total_seconds()
    if age < 0:
        return RecoveryDecision(RecoveryAction.RECONCILE, "operation-created-in-the-future-relative-to-clock", False)
    if age >= AUTOMATED_RETRY_CUTOFF_SECONDS:
        return RecoveryDecision(RecoveryAction.RECONCILE, "approaching-or-past-idempotency-pruning-window", False)
    if observed == ObservedOutcome.STORED_SERVER_ERROR:
        # API v1 stores/replays the first server result, including 500.
        return RecoveryDecision(RecoveryAction.RECONCILE, "same-key-may-replay-stored-server-error; effect-state-not-inferred", False)
    if observed in {ObservedOutcome.NETWORK_OUTCOME_UNKNOWN, ObservedOutcome.CONCURRENT_IDEMPOTENCY_CONFLICT}:
        return RecoveryDecision(RecoveryAction.RETRY_SAME_KEY, "inside-conservative-key-window; exact-same-request-only", True)
    return RecoveryDecision(RecoveryAction.RECONCILE, "outcome-class-not-safe-for-automatic-retry", False)


def _flatten_complete_refund_pages(pages: Sequence[RefundListPage]) -> tuple[list[Mapping[str, Any]] | None, str | None]:
    if not pages:
        return None, "refund-list-has-no-pages"
    all_items: list[Mapping[str, Any]] = []
    expected_cursor: str | None = None
    seen_ids: set[str] = set()
    for index, page in enumerate(pages):
        if not isinstance(page, RefundListPage):
            return None, "refund-list-page-envelope-invalid"
        if page.requested_starting_after != expected_cursor:
            return None, "refund-list-cursor-chain-invalid"
        response = page.response
        if not isinstance(response, Mapping) or response.get("object") != "list":
            return None, "refund-list-response-shape-invalid"
        data = response.get("data")
        has_more = response.get("has_more")
        if not isinstance(data, list) or type(has_more) is not bool:
            return None, "refund-list-pagination-fields-invalid"
        for item in data:
            if not isinstance(item, Mapping) or not isinstance(item.get("id"), str) or not item.get("id"):
                return None, "refund-list-item-shape-invalid"
            if item["id"] in seen_ids:
                return None, "refund-list-duplicate-object-id"
            seen_ids.add(item["id"])
        all_items.extend(data)
        if index < len(pages) - 1:
            if not has_more:
                return None, "refund-list-has-unexpected-extra-page"
            if not data:
                return None, "refund-list-page-with-more-has-no-cursor-item"
            expected_cursor = data[-1]["id"]
        elif has_more:
            return None, "refund-list-pagination-incomplete"
    return all_items, None


def match_reconciled_refunds(
    operation: RefundOperation,
    pages: Sequence[RefundListPage],
    *,
    current_account_scope: str,
    current_livemode: bool,
    current_api_version: str,
) -> RecoveryDecision:
    """Classify an explicitly cursor-linked, fully paginated refund listing.

    A bare ``listing_complete=True`` switch is intentionally not accepted. The
    helper checks the response list markers, has_more flags, page order, and
    starting_after cursor chain. It still cannot prove provider strong
    consistency for an empty listing, so no match is always inconclusive.
    """
    if current_account_scope != operation.account_scope:
        return RecoveryDecision(RecoveryAction.RECONCILE, "reconciliation-account-scope-mismatch", False)
    if type(current_livemode) is not bool or current_livemode is not operation.livemode:
        return RecoveryDecision(RecoveryAction.RECONCILE, "reconciliation-live-test-mode-mismatch", False)
    if current_api_version != operation.api_version:
        return RecoveryDecision(RecoveryAction.RECONCILE, "reconciliation-api-version-mismatch", False)
    refunds, error = _flatten_complete_refund_pages(pages)
    if error is not None or refunds is None:
        return RecoveryDecision(RecoveryAction.RECONCILE, error or "refund-list-incomplete", False)
    tagged = [r for r in refunds if isinstance(r.get("metadata"), Mapping) and r["metadata"].get(OPERATION_METADATA_KEY) == operation.operation_id]
    if not tagged:
        return RecoveryDecision(RecoveryAction.RECONCILE, "no-correlated-refund-found; absence-is-not-proof-of-no-effect", False)
    if len(tagged) != 1:
        return RecoveryDecision(RecoveryAction.RECONCILE, "multiple-refunds-correlate-to-one-operation-id", False)
    refund = tagged[0]
    if refund.get("object") != "refund":
        return RecoveryDecision(RecoveryAction.RECONCILE, "correlated-object-is-not-a-refund", False)
    expected_target = operation.charge if operation.charge else operation.payment_intent
    target_value = refund.get("charge") if operation.charge else refund.get("payment_intent")
    if target_value != expected_target:
        return RecoveryDecision(RecoveryAction.RECONCILE, "correlation-metadata-target-mismatch", False)
    if operation.amount is not None and refund.get("amount") != operation.amount:
        return RecoveryDecision(RecoveryAction.RECONCILE, "correlation-metadata-amount-mismatch", False)
    if refund.get("currency") != operation.expected_currency:
        return RecoveryDecision(RecoveryAction.RECONCILE, "correlation-metadata-currency-mismatch", False)
    rid = refund.get("id")
    status = refund.get("status")
    if status == "succeeded":
        return RecoveryDecision(RecoveryAction.ACCEPT_SUCCEEDED, "unique-correlated-refund-matches-payload", False, rid)
    if status in {"pending", "requires_action"}:
        return RecoveryDecision(RecoveryAction.WAIT_FOR_PROVIDER, "correlated-refund-exists-but-is-not-terminal-success", False, rid)
    if status in {"failed", "canceled"}:
        return RecoveryDecision(RecoveryAction.NEW_APPROVAL_REQUIRED, "correlated-refund-is-terminal-failure; a new operation needs a new approval", False, rid)
    return RecoveryDecision(RecoveryAction.RECONCILE, "unknown-or-missing-refund-status", False, rid)

