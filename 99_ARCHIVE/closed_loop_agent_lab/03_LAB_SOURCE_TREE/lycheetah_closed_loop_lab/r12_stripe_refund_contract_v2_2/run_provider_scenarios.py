"""Emit deterministic offline Stripe refund recovery scenarios; no network calls."""
from datetime import datetime, timedelta, timezone
import json
from stripe_refund_recovery import (
    ObservedOutcome, RefundListPage, RefundOperation, build_refund_request,
    decide_recovery, match_reconciled_refunds, operation_fingerprint,
)

now = datetime(2026, 10, 17, 0, 0, tzinfo=timezone.utc)
payload = build_refund_request(
    operation_id="op-001", idempotency_key="lyc-refund-key-001",
    charge="ch_test", amount=2500, reason="requested_by_customer",
)
op = RefundOperation(
    operation_id="op-001", idempotency_key="lyc-refund-key-001",
    created_at=now - timedelta(hours=2), account_scope="acct_test", livemode=False,
    api_version="test-fixture-v1", charge="ch_test", payment_intent=None,
    amount=2500, expected_currency="usd",
    request_fingerprint_sha256=operation_fingerprint(
        account_scope="acct_test", livemode=False,
        api_version="test-fixture-v1", payload=payload,
    ),
)
base = dict(
    retry_idempotency_key="lyc-refund-key-001", retry_payload=payload,
    current_account_scope="acct_test", current_livemode=False,
    current_api_version="test-fixture-v1",
)
refund = {
    "id": "re_fixture_001", "object": "refund", "amount": 2500,
    "charge": "ch_test", "payment_intent": "pi_fixture", "currency": "usd",
    "metadata": {"lycheetah_operation_id": "op-001"}, "status": "succeeded",
}
results = {
    "scope": "offline deterministic fixtures only; no Stripe SDK or API call",
    "scenarios": [
        {"name": "unknown-network-outcome-at-2h", "decision": decide_recovery(op, now=now, observed=ObservedOutcome.NETWORK_OUTCOME_UNKNOWN, **base).to_dict()},
        {"name": "stored-500", "decision": decide_recovery(op, now=now, observed=ObservedOutcome.STORED_SERVER_ERROR, **base).to_dict()},
        {"name": "unknown-outcome-at-23h", "decision": decide_recovery(RefundOperation(**{**op.__dict__, "created_at":now-timedelta(hours=23)}), now=now, observed=ObservedOutcome.NETWORK_OUTCOME_UNKNOWN, **base).to_dict()},
        {"name": "unique-matching-success-after-listing", "decision": match_reconciled_refunds(op, [RefundListPage(None, {"object":"list", "has_more":False, "data":[refund]})], current_account_scope="acct_test", current_livemode=False, current_api_version="test-fixture-v1").to_dict()},
        {"name": "no-match-after-listing", "decision": match_reconciled_refunds(op, [RefundListPage(None, {"object":"list", "has_more":False, "data":[]})], current_account_scope="acct_test", current_livemode=False, current_api_version="test-fixture-v1").to_dict()},
        {"name": "duplicate-operation-tags", "decision": match_reconciled_refunds(op, [RefundListPage(None, {"object":"list", "has_more":False, "data":[refund, {**refund,"id":"re_fixture_002"}]})], current_account_scope="acct_test", current_livemode=False, current_api_version="test-fixture-v1").to_dict()},
        {"name": "listing-pagination-incomplete", "decision": match_reconciled_refunds(op, [RefundListPage(None, {"object":"list", "has_more":True, "data":[refund]})], current_account_scope="acct_test", current_livemode=False, current_api_version="test-fixture-v1").to_dict()},
    ],
}
print(json.dumps(results, indent=2, sort_keys=True))
