import unittest
from datetime import datetime, timedelta, timezone

try:  # Package import from the lab root, or direct execution from this folder.
    from .stripe_refund_recovery import (
        ObservedOutcome, RecoveryAction, RefundListPage, RefundOperation,
        build_refund_request, decide_recovery, match_reconciled_refunds,
        operation_fingerprint, new_operation_identity,
    )
except ImportError:
    from stripe_refund_recovery import (
        ObservedOutcome, RecoveryAction, RefundListPage, RefundOperation,
        build_refund_request, decide_recovery, match_reconciled_refunds,
        operation_fingerprint, new_operation_identity,
    )

NOW = datetime(2026, 10, 17, 0, 0, tzinfo=timezone.utc)


def payload(amount=2500):
    return build_refund_request(
        operation_id="op-001", idempotency_key="lyc-refund-key-001",
        charge="ch_test", amount=amount, reason="requested_by_customer",
    )


def recovery_context(**overrides):
    values = dict(
        retry_idempotency_key="lyc-refund-key-001", retry_payload=payload(),
        current_account_scope="acct_test", current_livemode=False,
        current_api_version="test-fixture-v1",
    )
    values.update(overrides)
    return values


def operation(age_hours=1, **overrides):
    created = NOW - timedelta(hours=age_hours)
    request_payload = payload()
    values = dict(
        operation_id="op-001", idempotency_key="lyc-refund-key-001",
        created_at=created, account_scope="acct_test", livemode=False,
        api_version="test-fixture-v1", charge="ch_test", payment_intent=None,
        amount=2500, expected_currency="usd",
        request_fingerprint_sha256=operation_fingerprint(
            account_scope="acct_test", livemode=False,
            api_version="test-fixture-v1", payload=request_payload,
        ),
    )
    values.update(overrides)
    return RefundOperation(**values)


def refund(**overrides):
    value = {
        "id": "re_test123", "object": "refund", "amount": 2500,
        "charge": "ch_test", "payment_intent": "pi_test", "currency": "usd",
        "metadata": {"lycheetah_operation_id": "op-001"}, "status": "succeeded",
    }
    value.update(overrides)
    return value


def listing(items, *, has_more=False, requested_after=None):
    return [RefundListPage(requested_after, {"object": "list", "has_more": has_more, "data": items})]


def reconcile(op, pages, **overrides):
    context = dict(current_account_scope="acct_test", current_livemode=False, current_api_version="test-fixture-v1")
    context.update(overrides)
    return match_reconciled_refunds(op, pages, **context)


class StripeRefundPolicyTests(unittest.TestCase):
    def test_payload_includes_operation_correlation(self):
        payload = build_refund_request(operation_id="abc", idempotency_key="k", charge="ch", amount=3)
        self.assertEqual(payload["metadata"]["lycheetah_operation_id"], "abc")

    def test_new_operation_identity_is_random_non_pii_and_within_key_limit(self):
        op1, key1 = new_operation_identity()
        op2, key2 = new_operation_identity()
        self.assertNotEqual(op1, op2)
        self.assertNotEqual(key1, key2)
        self.assertLessEqual(len(key1), 255)
        self.assertNotIn("@", key1)

    def test_payload_requires_exactly_one_target(self):
        with self.assertRaises(ValueError):
            build_refund_request(operation_id="abc", idempotency_key="k", charge="ch", payment_intent="pi")

    def test_target_values_must_be_nonempty_strings(self):
        for kwargs in ({"charge": ["ch"]}, {"payment_intent": 7}, {"charge": ""}):
            with self.subTest(kwargs=kwargs), self.assertRaises(ValueError):
                build_refund_request(operation_id="abc", idempotency_key="k", **kwargs)

    def test_payload_amount_must_be_positive_integer_not_bool(self):
        for bad in (0, -1, True, 1.5):
            with self.subTest(bad=bad), self.assertRaises(ValueError):
                build_refund_request(operation_id="abc", idempotency_key="k", charge="ch", amount=bad)

    def test_reserved_operation_metadata_cannot_be_overridden(self):
        with self.assertRaises(ValueError):
            build_refund_request(operation_id="abc", idempotency_key="k", charge="ch", additional_metadata={"lycheetah_operation_id":"other"})

    def test_metadata_count_and_sizes_checked(self):
        with self.assertRaises(ValueError):
            build_refund_request(operation_id="abc", idempotency_key="k", charge="ch", additional_metadata={f"k{i}": "v" for i in range(50)})
        with self.assertRaises(ValueError):
            build_refund_request(operation_id="abc", idempotency_key="k", charge="ch", additional_metadata={"x"*41: "v"})

    def test_fingerprint_binds_account_mode_version_endpoint_payload(self):
        payload = build_refund_request(operation_id="abc", idempotency_key="k", charge="ch", amount=3)
        base = operation_fingerprint(account_scope="acct", livemode=False, api_version="v1", payload=payload)
        self.assertNotEqual(base, operation_fingerprint(account_scope="acct2", livemode=False, api_version="v1", payload=payload))
        self.assertNotEqual(base, operation_fingerprint(account_scope="acct", livemode=True, api_version="v1", payload=payload))
        self.assertNotEqual(base, operation_fingerprint(account_scope="acct", livemode=False, api_version="v2", payload=payload))
        self.assertNotEqual(base, operation_fingerprint(account_scope="acct", livemode=False, api_version="v1", payload={**payload, "amount":4}))

    def test_network_timeout_inside_conservative_window_retries_same_key(self):
        result = decide_recovery(operation(), now=NOW, observed=ObservedOutcome.NETWORK_OUTCOME_UNKNOWN, retry_idempotency_key="lyc-refund-key-001", retry_payload=payload(), current_account_scope="acct_test", current_livemode=False, current_api_version="test-fixture-v1")
        self.assertEqual(result.action, RecoveryAction.RETRY_SAME_KEY)

    def test_concurrent_idempotency_conflict_inside_window_retries_same_key(self):
        result = decide_recovery(operation(), now=NOW, observed=ObservedOutcome.CONCURRENT_IDEMPOTENCY_CONFLICT, retry_idempotency_key="lyc-refund-key-001", retry_payload=payload(), current_account_scope="acct_test", current_livemode=False, current_api_version="test-fixture-v1")
        self.assertEqual(result.action, RecoveryAction.RETRY_SAME_KEY)

    def test_stored_500_never_implies_not_executed(self):
        result = decide_recovery(operation(), now=NOW, observed=ObservedOutcome.STORED_SERVER_ERROR, retry_idempotency_key="lyc-refund-key-001", retry_payload=payload(), current_account_scope="acct_test", current_livemode=False, current_api_version="test-fixture-v1")
        self.assertEqual(result.action, RecoveryAction.RECONCILE)

    def test_key_age_near_conservative_cutoff_requires_reconciliation(self):
        op = operation(age_hours=23)
        result = decide_recovery(op, now=NOW, observed=ObservedOutcome.NETWORK_OUTCOME_UNKNOWN, retry_idempotency_key="lyc-refund-key-001", retry_payload=payload(), current_account_scope="acct_test", current_livemode=False, current_api_version="test-fixture-v1")
        self.assertEqual(result.action, RecoveryAction.RECONCILE)

    def test_key_age_just_inside_cutoff_can_retry_same_key(self):
        op = operation(created_at=NOW - timedelta(hours=22, minutes=59))
        result = decide_recovery(op, now=NOW, observed=ObservedOutcome.NETWORK_OUTCOME_UNKNOWN, retry_idempotency_key="lyc-refund-key-001", retry_payload=payload(), current_account_scope="acct_test", current_livemode=False, current_api_version="test-fixture-v1")
        self.assertEqual(result.action, RecoveryAction.RETRY_SAME_KEY)

    def test_past_key_window_requires_reconciliation(self):
        op = operation(age_hours=30)
        result = decide_recovery(op, now=NOW, observed=ObservedOutcome.NETWORK_OUTCOME_UNKNOWN, retry_idempotency_key="lyc-refund-key-001", retry_payload=payload(), current_account_scope="acct_test", current_livemode=False, current_api_version="test-fixture-v1")
        self.assertEqual(result.action, RecoveryAction.RECONCILE)

    def test_changed_payload_never_retries_same_key(self):
        result = decide_recovery(operation(), now=NOW, observed=ObservedOutcome.NETWORK_OUTCOME_UNKNOWN, retry_idempotency_key="lyc-refund-key-001", retry_payload=payload(amount=3000), current_account_scope="acct_test", current_livemode=False, current_api_version="test-fixture-v1")
        self.assertEqual(result.action, RecoveryAction.RECONCILE)

    def test_legacy_caller_supplied_match_booleans_are_not_accepted(self):
        with self.assertRaises(TypeError):
            decide_recovery(operation(), now=NOW, observed=ObservedOutcome.NETWORK_OUTCOME_UNKNOWN, exact_persisted_payload_reused=True, provider_account_matches=True, provider_mode_matches=True)

    def test_noncanonical_retry_payload_fails_closed(self):
        result = decide_recovery(operation(), now=NOW, observed=ObservedOutcome.NETWORK_OUTCOME_UNKNOWN, **recovery_context(retry_payload={"bad": float("nan")}))
        self.assertEqual(result.action, RecoveryAction.RECONCILE)

    def test_wrong_account_or_mode_never_retries(self):
        for kwargs in (
            {"current_account_scope": "acct_other"},
            {"current_livemode": True},
        ):
            changed = recovery_context(**kwargs)
            result = decide_recovery(operation(), now=NOW, observed=ObservedOutcome.NETWORK_OUTCOME_UNKNOWN, **changed)
            self.assertEqual(result.action, RecoveryAction.RECONCILE)

    def test_changed_api_version_requires_reconciliation(self):
        result = decide_recovery(operation(), now=NOW, observed=ObservedOutcome.NETWORK_OUTCOME_UNKNOWN, **recovery_context(current_api_version="test-fixture-v2"))
        self.assertEqual(result.action, RecoveryAction.RECONCILE)

    def test_changed_idempotency_key_requires_reconciliation(self):
        result = decide_recovery(operation(), now=NOW, observed=ObservedOutcome.NETWORK_OUTCOME_UNKNOWN, **recovery_context(retry_idempotency_key="a-new-key"))
        self.assertEqual(result.action, RecoveryAction.RECONCILE)

    def test_future_created_at_requires_reconciliation(self):
        op = operation(created_at=NOW + timedelta(seconds=1))
        result = decide_recovery(op, now=NOW, observed=ObservedOutcome.NETWORK_OUTCOME_UNKNOWN, retry_idempotency_key="lyc-refund-key-001", retry_payload=payload(), current_account_scope="acct_test", current_livemode=False, current_api_version="test-fixture-v1")
        self.assertEqual(result.action, RecoveryAction.RECONCILE)

    def test_one_correlated_success_is_accepted(self):
        result = reconcile(operation(), listing([refund()]))
        self.assertEqual(result.action, RecoveryAction.ACCEPT_SUCCEEDED)
        self.assertEqual(result.matched_refund_id, "re_test123")

    def test_no_match_never_proves_no_effect(self):
        result = reconcile(operation(), listing([]))
        self.assertEqual(result.action, RecoveryAction.RECONCILE)

    def test_unrelated_operation_metadata_is_not_a_match(self):
        candidate = refund(metadata={"lycheetah_operation_id": "another-operation"})
        result = reconcile(operation(), listing([candidate]))
        self.assertEqual(result.action, RecoveryAction.RECONCILE)
        self.assertEqual(result.reason, "no-correlated-refund-found; absence-is-not-proof-of-no-effect")

    def test_full_refund_without_explicit_amount_can_match_unique_operation(self):
        op = operation(amount=None)
        result = reconcile(op, listing([refund()]))
        self.assertEqual(result.action, RecoveryAction.ACCEPT_SUCCEEDED)

    def test_incomplete_pagination_requires_reconciliation(self):
        result = reconcile(operation(), listing([refund()], has_more=True))
        self.assertEqual(result.action, RecoveryAction.RECONCILE)

    def test_valid_cursor_chain_across_two_pages_can_find_refund(self):
        first = RefundListPage(None, {"object": "list", "has_more": True, "data": [refund(id="re_other", metadata={"lycheetah_operation_id": "other"})]})
        second = RefundListPage("re_other", {"object": "list", "has_more": False, "data": [refund()]})
        result = reconcile(operation(), [first, second])
        self.assertEqual(result.action, RecoveryAction.ACCEPT_SUCCEEDED)

    def test_invalid_cursor_chain_requires_reconciliation(self):
        first = RefundListPage(None, {"object": "list", "has_more": True, "data": [refund(id="re_other", metadata={"lycheetah_operation_id": "other"})]})
        second = RefundListPage("wrong_cursor", {"object": "list", "has_more": False, "data": [refund()]})
        result = reconcile(operation(), [first, second])
        self.assertEqual(result.action, RecoveryAction.RECONCILE)

    def test_correlated_non_refund_object_requires_reconciliation(self):
        result = reconcile(operation(), listing([refund(object="charge")]))
        self.assertEqual(result.action, RecoveryAction.RECONCILE)

    def test_wrong_scope_mode_or_api_version_on_reconciliation_fails_closed(self):
        checks = (
            {"current_account_scope": "acct_other"},
            {"current_livemode": True},
            {"current_api_version": "different-version"},
        )
        for context in checks:
            result = reconcile(operation(), listing([refund()]), **context)
            self.assertEqual(result.action, RecoveryAction.RECONCILE)

    def test_duplicate_object_ids_across_pages_require_reconciliation(self):
        first = RefundListPage(None, {"object": "list", "has_more": True, "data": [refund(id="re_dup", metadata={"lycheetah_operation_id": "other"})]})
        second = RefundListPage("re_dup", {"object": "list", "has_more": False, "data": [refund(id="re_dup")]})
        result = reconcile(operation(), [first, second])
        self.assertEqual(result.action, RecoveryAction.RECONCILE)

    def test_duplicate_correlations_require_reconciliation(self):
        result = reconcile(operation(), listing([refund(), refund(id="re_test456")]))
        self.assertEqual(result.action, RecoveryAction.RECONCILE)

    def test_amount_target_and_currency_must_match(self):
        for candidate in (refund(amount=2499), refund(charge="ch_other"), refund(currency="eur")):
            result = reconcile(operation(), listing([candidate]))
            self.assertEqual(result.action, RecoveryAction.RECONCILE)

    def test_pending_refund_is_not_recreated(self):
        result = reconcile(operation(), listing([refund(status="pending")]))
        self.assertEqual(result.action, RecoveryAction.WAIT_FOR_PROVIDER)

    def test_requires_action_is_not_recreated(self):
        result = reconcile(operation(), listing([refund(status="requires_action")]))
        self.assertEqual(result.action, RecoveryAction.WAIT_FOR_PROVIDER)

    def test_failed_refund_requires_new_approval(self):
        result = reconcile(operation(), listing([refund(status="failed")]))
        self.assertEqual(result.action, RecoveryAction.NEW_APPROVAL_REQUIRED)

    def test_canceled_refund_requires_new_approval(self):
        result = reconcile(operation(), listing([refund(status="canceled")]))
        self.assertEqual(result.action, RecoveryAction.NEW_APPROVAL_REQUIRED)

    def test_missing_identifier_or_unknown_status_requires_reconciliation(self):
        self.assertEqual(reconcile(operation(), listing([refund(id=None)])).action, RecoveryAction.RECONCILE)
        self.assertEqual(reconcile(operation(), listing([refund(status="mystery")])).action, RecoveryAction.RECONCILE)

    def test_metadata_tag_alone_not_enough(self):
        result = reconcile(operation(), listing([refund(currency="nzd", amount=999)]))
        self.assertEqual(result.action, RecoveryAction.RECONCILE)

if __name__ == "__main__":
    unittest.main(verbosity=2)
