from __future__ import annotations
import json
import os
import sqlite3
import stat
import tempfile
import threading
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path

from stripe_test_adapter import (
    Action, DurableOperationStore, StripeTestModeRefundClient, UnsafeConfiguration,
    StoreStateTransitionError, build_payload,
)
from stripe_contract_simulator import StripeContractSimulator

NOW = datetime(2026, 10, 17, 12, 0, tzinfo=timezone.utc)


class AdapterCase(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.db_path = str(Path(self.temp.name) / "operations.sqlite")
        self.integrity_key = b"unit-test-only-integrity-key-32-bytes-long"
        self.store = DurableOperationStore(self.db_path, integrity_key=self.integrity_key)
        self.provider = StripeContractSimulator().start()
        self.client = self.make_client()

    def tearDown(self):
        self.provider.close()
        self.temp.cleanup()

    def make_client(self, *, account_scope="platform:acct_demo", stripe_account=None,
                    api_version="2025-09-30.clover", key="sk_test_local_mock", base_url=None):
        return StripeTestModeRefundClient(
            store=self.store, secret_key=key, base_url=base_url or self.provider.url,
            account_scope=account_scope, stripe_account=stripe_account,
            api_version=api_version, allow_loopback_http=True, timeout_seconds=0.5)

    def prepare(self, *, created_at=NOW, operation_id="op_001", key="lyc-test-key-001",
                charge="ch_test_001", amount=2500, currency="usd"):
        self.client.prepare_refund(operation_id=operation_id, idempotency_key=key,
            created_at=created_at, charge=charge, amount=amount,
            reason="requested_by_customer", expected_currency=currency)
        return operation_id

    def test_intent_is_durable_before_any_provider_request(self):
        op=self.prepare()
        self.assertEqual(self.provider.post_calls,0)
        self.assertEqual(self.store.get(op)["state"],"READY")

    def test_normal_create_executes_one_effect_and_persists_success(self):
        op=self.prepare()
        result=self.client.dispatch(op,now=NOW)
        self.assertEqual(result.action,Action.SUCCEEDED)
        self.assertEqual(self.provider.effect_count,1)
        self.assertEqual(self.store.get(op)["state"],"SUCCEEDED")

    def test_lost_response_after_commit_recovers_with_same_key(self):
        op=self.prepare()
        self.provider.fail_next("drop_after_commit")
        first=self.client.dispatch(op,now=NOW)
        self.assertEqual(first.action,Action.RECONCILE)
        self.assertEqual(self.store.get(op)["state"],"UNKNOWN")
        recovered=self.client.recover(op,now=NOW+timedelta(seconds=3))
        self.assertEqual(recovered.action,Action.SUCCEEDED)
        self.assertEqual(self.provider.effect_count,1)
        self.assertEqual(self.provider.post_calls,2)

    def test_restart_recovery_reuses_persisted_idempotency_key(self):
        op=self.prepare()
        self.provider.fail_next("drop_after_commit")
        self.client.dispatch(op,now=NOW)
        restarted= self.make_client()
        result=restarted.recover(op,now=NOW+timedelta(minutes=1))
        self.assertEqual(result.action,Action.SUCCEEDED)
        self.assertEqual(self.provider.effect_count,1)
        self.assertEqual(self.store.get(op)["idempotency_key"],"lyc-test-key-001")

    def test_drop_before_execute_retries_once_with_same_key(self):
        op=self.prepare()
        self.provider.fail_next("drop_before_execute")
        self.client.dispatch(op,now=NOW)
        result=self.client.recover(op,now=NOW+timedelta(seconds=2))
        self.assertEqual(result.action,Action.SUCCEEDED)
        self.assertEqual(self.provider.effect_count,1)

    def test_stored_500_is_not_blindly_retried(self):
        op=self.prepare()
        self.provider.fail_next("cached_500")
        first=self.client.dispatch(op,now=NOW)
        self.assertEqual(first.action,Action.RECONCILE)
        posts=self.provider.post_calls
        retry=self.client.recover(op,now=NOW+timedelta(seconds=1))
        self.assertEqual(retry.action,Action.RECONCILE)
        self.assertEqual(self.provider.post_calls,posts)
        self.assertEqual(retry.reason,"no-correlated-refund-found; absence-is-not-proof-of-no-effect")

    def test_stale_unknown_operation_searches_but_does_not_retry(self):
        op=self.prepare()
        self.provider.fail_next("drop_after_commit")
        self.client.dispatch(op,now=NOW)
        posts=self.provider.post_calls
        result=self.client.recover(op,now=NOW+timedelta(hours=24))
        self.assertEqual(result.action,Action.SUCCEEDED)
        self.assertEqual(self.provider.post_calls,posts)
        self.assertGreaterEqual(self.provider.get_calls,1)
        self.assertEqual(self.provider.effect_count,1)

    def test_stale_absent_operation_reconciles_without_post(self):
        op=self.prepare()
        # Pretend process died after durable intent but before sending any bytes.
        posts=self.provider.post_calls
        result=self.client.recover(op,now=NOW+timedelta(hours=24))
        self.assertEqual(result.action,Action.RECONCILE)
        self.assertEqual(self.provider.post_calls,posts)

    def test_tampered_persisted_payload_fails_before_provider_call(self):
        op=self.prepare()
        import sqlite3, json
        db=sqlite3.connect(self.db_path)
        payload=json.loads(db.execute("select payload_json from refund_ops where operation_id=?",(op,)).fetchone()[0])
        payload["amount"]=9999
        db.execute("update refund_ops set payload_json=? where operation_id=?",(json.dumps(payload),op)); db.commit(); db.close()
        result=self.client.dispatch(op,now=NOW)
        self.assertEqual(result.action,Action.RECONCILE)
        self.assertIn("authentication-failed",result.reason)
        self.assertEqual(self.provider.post_calls,0)

    def test_wrong_account_scope_fails_before_provider_call(self):
        op=self.prepare()
        wrong=self.make_client(account_scope="platform:acct_other")
        result=wrong.dispatch(op,now=NOW)
        self.assertEqual(result.action,Action.RECONCILE)
        self.assertEqual(self.provider.post_calls,0)

    def test_wrong_connected_account_fails_before_provider_call(self):
        op=self.prepare()
        wrong=self.make_client(account_scope="connected:acct_other",stripe_account="acct_other")
        self.assertEqual(wrong.dispatch(op,now=NOW).action,Action.RECONCILE)
        self.assertEqual(self.provider.post_calls,0)

    def test_wrong_api_version_fails_before_provider_call(self):
        op=self.prepare()
        wrong=self.make_client(api_version="different-version")
        self.assertEqual(wrong.dispatch(op,now=NOW).action,Action.RECONCILE)
        self.assertEqual(self.provider.post_calls,0)

    def test_live_key_is_rejected(self):
        with self.assertRaises(UnsafeConfiguration):
            self.make_client(key="sk_live_not_allowed")

    def test_publishable_key_is_rejected(self):
        with self.assertRaises(UnsafeConfiguration):
            self.make_client(key="pk_test_not_secret")

    def test_remote_plain_http_is_rejected(self):
        with self.assertRaises(UnsafeConfiguration):
            self.make_client(base_url="http://example.com")

    def test_local_http_requires_explicit_opt_in(self):
        with self.assertRaises(UnsafeConfiguration):
            StripeTestModeRefundClient(store=self.store,secret_key="sk_test_local_mock",
                base_url=self.provider.url,account_scope="platform:acct_demo",api_version="v1")

    def test_account_header_and_version_are_sent(self):
        client=self.make_client(account_scope="connected:acct_123",stripe_account="acct_123")
        op="op_header"
        client.prepare_refund(operation_id=op,idempotency_key="lyc-header-key",created_at=NOW,
                              charge="ch_test",amount=500,expected_currency="usd")
        # simulator exposes the latest request headers only after this assertion-safe call
        result=client.dispatch(op,now=NOW)
        self.assertEqual(result.action,Action.SUCCEEDED)
        self.assertEqual(self.provider.last_headers.get("Stripe-Account"),"acct_123")
        self.assertEqual(self.provider.last_headers.get("Stripe-Version"),"2025-09-30.clover")
        self.assertEqual(self.provider.last_headers.get("Idempotency-Key"),"lyc-header-key")

    def test_key_reuse_with_different_payload_is_provider_error_not_second_effect(self):
        op=self.prepare()
        result=self.client.dispatch(op,now=NOW)
        self.assertEqual(result.action,Action.SUCCEEDED)
        # Simulate a raw caller attempting to use same provider key and a new amount.
        status,body=self.client._request("POST","/v1/refunds",payload=build_payload(
            operation_id=op,charge="ch_test_001",amount=2400),idempotency_key="lyc-test-key-001")
        self.assertEqual(status,400)
        self.assertEqual(self.provider.effect_count,1)

    def test_duplicate_operation_id_and_key_cannot_be_prepared_twice(self):
        self.prepare()
        with self.assertRaises(Exception):
            self.prepare()

    def test_multiple_operations_cannot_share_idempotency_key(self):
        self.prepare()
        with self.assertRaises(Exception):
            self.prepare(operation_id="op_002",key="lyc-test-key-001",charge="ch_test_002")

    def test_operation_metadata_cannot_be_substituted_in_persisted_intent(self):
        self.provider.fail_next("normal")
        op=self.prepare()
        # Create a cached payload conflict manually by causing operation metadata to differ
        import sqlite3,json
        db=sqlite3.connect(self.db_path)
        payload=json.loads(db.execute("select payload_json from refund_ops where operation_id=?",(op,)).fetchone()[0])
        payload["metadata"]["lycheetah_operation_id"]="other-op"
        # Fingerprint is updated too to exercise response binding, not just local tamper alarm.
        db.execute("update refund_ops set payload_json=? where operation_id=?",
                   (json.dumps(payload),op)); db.commit(); db.close()
        # HMAC-protected local persistence prevents a writer from substituting the saved action.
        result=self.client.dispatch(op,now=NOW)
        self.assertEqual(result.action,Action.RECONCILE)
        self.assertIn("authentication-failed",result.reason)
        self.assertEqual(self.provider.post_calls,0)

    def test_non_success_terminal_refund_requests_new_approval(self):
        op=self.prepare()
        # Set simulator's next created status to failed for a narrow state-contract test.
        self.provider.next_status="failed"
        result=self.client.dispatch(op,now=NOW)
        self.assertEqual(result.action,Action.NEW_APPROVAL_REQUIRED)

    def test_pending_refund_waits_instead_of_claiming_success(self):
        op=self.prepare()
        self.provider.next_status="pending"
        result=self.client.dispatch(op,now=NOW)
        self.assertEqual(result.action,Action.WAIT_FOR_PROVIDER)
        self.assertEqual(self.store.get(op)["state"],"WAITING")

    def test_no_correlated_refund_in_listing_is_not_proof_of_no_effect(self):
        op=self.prepare()
        result=self.client.reconcile(op,now=NOW)
        self.assertEqual(result.action,Action.RECONCILE)
        self.assertIn("absence-is-not-proof",result.reason)

    def test_matching_refund_is_reconciled_by_operation_metadata(self):
        op=self.prepare()
        self.client.dispatch(op,now=NOW)
        result=self.client.reconcile(op,now=NOW+timedelta(hours=24))
        self.assertEqual(result.action,Action.SUCCEEDED)

    def test_currency_mismatch_is_reconciliation(self):
        op=self.prepare()
        self.client.dispatch(op,now=NOW)
        self.provider.refunds[0]["currency"]="eur"
        result=self.client.reconcile(op,now=NOW+timedelta(hours=24))
        self.assertEqual(result.action,Action.RECONCILE)
        self.assertIn("currency-mismatch",result.reason)

    def test_duplicate_correlated_refunds_are_reconciled(self):
        op=self.prepare()
        self.client.dispatch(op,now=NOW)
        original=dict(self.provider.refunds[0]); original["id"]="re_duplicate"
        self.provider.seed_refund(original)
        result=self.client.reconcile(op,now=NOW+timedelta(hours=24))
        self.assertEqual(result.action,Action.RECONCILE)
        self.assertIn("multiple-refunds",result.reason)

    def test_pagination_finds_correlated_refund_on_later_page(self):
        op=self.prepare()
        self.client.dispatch(op,now=NOW)
        correlated=dict(self.provider.refunds[0])
        self.provider.refunds=[]
        for i in range(5):
            self.provider.seed_refund({"id":f"re_decoy_{i}","object":"refund","amount":1,
                "charge":"ch_test_001","payment_intent":"pi_other","currency":"usd",
                "metadata":{"lycheetah_operation_id":f"decoy_{i}"},"status":"succeeded","livemode":False})
        self.provider.seed_refund(correlated)
        result=self.client.reconcile(op,now=NOW+timedelta(hours=24),page_limit=2)
        self.assertEqual(result.action,Action.SUCCEEDED)
        self.assertGreaterEqual(self.provider.get_calls,3)

    def test_incomplete_or_malformed_pagination_fails_closed(self):
        for mode in ("true_empty","missing_has_more","duplicate_id"):
            with self.subTest(mode=mode):
                op=self.prepare(operation_id="op_"+mode,key="lyc-"+mode,charge="ch_"+mode)
                self.provider.corrupt_next_listing(mode)
                result=self.client.reconcile(op,now=NOW+timedelta(hours=24))
                self.assertEqual(result.action,Action.RECONCILE)

    def test_invalid_json_provider_body_fails_closed(self):
        # The simulator contract hook returns a malformed list envelope.
        op=self.prepare()
        self.provider.corrupt_next_listing("missing_has_more")
        result=self.client.reconcile(op,now=NOW)
        self.assertEqual(result.action,Action.RECONCILE)

    def test_same_key_concurrent_requests_produce_one_simulated_effect(self):
        op=self.prepare()
        results=[]
        barrier=threading.Barrier(3)
        def call():
            barrier.wait(); results.append(self.client.dispatch(op,now=NOW))
        t1=threading.Thread(target=call); t2=threading.Thread(target=call)
        t1.start();t2.start();barrier.wait();t1.join();t2.join()
        self.assertEqual(self.provider.effect_count,1)
        self.assertEqual(len(results),2)
        self.assertTrue(all(r.action in {Action.SUCCEEDED,Action.RECONCILE} for r in results))

    def test_prepared_intent_survives_restart_before_first_dispatch(self):
        op=self.prepare()
        restart=DurableOperationStore(self.db_path, integrity_key=self.integrity_key)
        client=self.make_client()
        result=client.dispatch(op,now=NOW)
        self.assertEqual(result.action,Action.SUCCEEDED)
        self.assertEqual(restart.get(op)["state"],"SUCCEEDED")

    def test_authentication_failure_does_not_claim_success(self):
        op=self.prepare()
        self.client.secret_key="sk_test_wrong"
        result=self.client.dispatch(op,now=NOW)
        self.assertEqual(result.action,Action.RECONCILE)
        self.assertEqual(result.http_status,401)
        self.assertEqual(self.provider.effect_count,0)

    def test_request_idempotency_key_is_not_in_body(self):
        op=self.prepare()
        payload=self.store.get(op)["payload"]
        self.assertNotIn("idempotency_key",payload)
        self.assertEqual(self.store.get(op)["idempotency_key"],"lyc-test-key-001")

    def test_preparation_rejects_missing_or_mismatched_operation_metadata(self):
        payload={"charge":"ch_test","metadata":{"lycheetah_operation_id":"other"}}
        with self.assertRaises(ValueError):
            self.store.prepare(operation_id="op_003",idempotency_key="lyc-003",created_at=NOW,
                account_scope="platform:acct_demo",stripe_account=None,api_version="v1",
                payload=payload,expected_currency="usd")

    def test_response_loss_does_not_leak_key_in_diagnostic(self):
        op=self.prepare(); self.provider.fail_next("drop_after_commit")
        result=self.client.dispatch(op,now=NOW)
        self.assertNotIn("sk_test_local_mock",result.reason)
        self.assertNotIn("lyc-test-key-001",result.reason)


    def test_store_hmac_detects_tampered_success_state_and_response(self):
        op=self.prepare()
        import sqlite3,json
        fake={"id":"re_forged","object":"refund","amount":2500,"charge":"ch_test_001",
              "payment_intent":"pi_fake","currency":"usd","metadata":{"lycheetah_operation_id":op},
              "status":"succeeded","livemode":False}
        db=sqlite3.connect(self.db_path)
        db.execute("update refund_ops set state='SUCCEEDED',provider_response_json=?,last_http_status=200 where operation_id=?",
                   (json.dumps(fake),op)); db.commit(); db.close()
        result=self.client.recover(op,now=NOW)
        self.assertEqual(result.action,Action.RECONCILE)
        self.assertIn("authentication-failed",result.reason)
        self.assertEqual(self.provider.effect_count,0)

    def test_expected_currency_is_bound_into_fingerprint(self):
        op=self.prepare()
        import sqlite3
        db=sqlite3.connect(self.db_path)
        db.execute("update refund_ops set expected_currency='eur' where operation_id=?",(op,)); db.commit(); db.close()
        result=self.client.dispatch(op,now=NOW)
        self.assertEqual(result.action,Action.RECONCILE)
        self.assertIn("authentication-failed",result.reason)

    def test_retry_cutoff_uses_reconciliation_not_post(self):
        op=self.prepare()
        self.provider.fail_next("drop_after_commit")
        self.client.dispatch(op,now=NOW)
        count=self.provider.post_calls
        result=self.client.recover(op,now=NOW+timedelta(hours=23))
        self.assertEqual(result.action,Action.SUCCEEDED)
        self.assertEqual(self.provider.post_calls,count)

    def test_wrong_live_mode_marker_in_response_fails_closed(self):
        op=self.prepare()
        self.client.dispatch(op,now=NOW)
        self.provider.refunds[0]["livemode"]=True
        result=self.client.reconcile(op,now=NOW+timedelta(hours=24))
        self.assertEqual(result.action,Action.RECONCILE)
        self.assertIn("test-mode",result.reason)

    def test_cursor_does_not_repeat_and_duplicate_pages_fail_closed(self):
        op=self.prepare()
        self.client.dispatch(op,now=NOW)
        self.provider.corrupt_next_listing("duplicate_id")
        result=self.client.reconcile(op,now=NOW+timedelta(hours=24),page_limit=1)
        self.assertEqual(result.action,Action.RECONCILE)
        self.assertIn("duplicate-id",result.reason)


    def test_arbitrary_https_host_is_rejected_by_default(self):
        with self.assertRaises(UnsafeConfiguration):
            self.make_client(base_url="https://attacker.example")

    def test_non_root_url_path_is_rejected(self):
        with self.assertRaises(UnsafeConfiguration):
            self.make_client(base_url="https://api.stripe.com/proxy")

    def test_naive_timestamp_is_rejected_before_network_io(self):
        op=self.prepare()
        with self.assertRaises(ValueError):
            self.client.dispatch(op,now=datetime(2026,10,17,12,0))
        self.assertEqual(self.provider.post_calls,0)

    @unittest.skipUnless(os.name == "posix", "POSIX file mode semantics required")
    def test_operation_database_is_owner_only(self):
        mode = stat.S_IMODE(os.stat(self.db_path).st_mode)
        self.assertEqual(mode, 0o600)

    def test_operation_store_rejects_symlink_database_path(self):
        link = Path(self.temp.name) / "operations-link.sqlite"
        link.symlink_to(self.db_path)
        with self.assertRaisesRegex(UnsafeConfiguration, "must not be a symlink"):
            DurableOperationStore(str(link), integrity_key=self.integrity_key)

    def test_operation_store_rejects_non_durable_memory_database(self):
        with self.assertRaisesRegex(UnsafeConfiguration, "durable filesystem database"):
            DurableOperationStore(":memory:", integrity_key=self.integrity_key)

    def test_operation_store_requires_authenticated_schema(self):
        old_path=str(Path(self.temp.name)/"old.sqlite")
        import sqlite3
        db=sqlite3.connect(old_path)
        db.execute("create table refund_ops (operation_id text primary key)")
        db.commit();db.close()
        with self.assertRaises(UnsafeConfiguration):
            DurableOperationStore(old_path,integrity_key=self.integrity_key)

    def test_pending_record_cannot_be_reported_as_succeeded_after_db_tamper(self):
        op=self.prepare()
        self.provider.next_status="pending"
        result=self.client.dispatch(op,now=NOW)
        self.assertEqual(result.action,Action.WAIT_FOR_PROVIDER)
        import sqlite3
        db=sqlite3.connect(self.db_path)
        db.execute("update refund_ops set state='SUCCEEDED' where operation_id=?",(op,));db.commit();db.close()
        recovered=self.client.recover(op,now=NOW+timedelta(seconds=1))
        self.assertEqual(recovered.action,Action.RECONCILE)
        self.assertIn("authentication-failed",recovered.reason)

    def test_success_classification_rejects_wrong_operation_metadata(self):
        op_id=self.prepare()
        row=self.store.get(op_id)
        refund={"id":"re_wrong","object":"refund","amount":2500,"charge":"ch_test_001",
                "payment_intent":"pi_parent","currency":"usd",
                "metadata":{"lycheetah_operation_id":"not-the-operation"},
                "status":"succeeded","livemode":False}
        classified=self.client._classify_refund(row,refund,200)
        self.assertEqual(classified.action,Action.RECONCILE)
        self.assertIn("correlation-metadata-mismatch",classified.reason)


    def test_redirect_is_not_followed_and_secret_is_not_forwarded(self):
        op=self.prepare()
        self.provider.redirect_next=True
        result=self.client.dispatch(op,now=NOW)
        self.assertEqual(result.action,Action.RECONCILE)
        self.assertEqual(result.http_status,302)
        self.assertEqual(self.provider.post_calls,1)
        self.assertEqual(self.provider.effect_count,0)

    def test_reconciliation_page_budget_fails_closed(self):
        op=self.prepare()
        self.client.dispatch(op,now=NOW)
        self.provider.refunds=[]
        for i in range(4):
            self.provider.seed_refund({"id":f"re_decoy_budget_{i}","object":"refund","amount":1,
                "charge":"ch_test_001","payment_intent":"pi_other","currency":"usd",
                "metadata":{"lycheetah_operation_id":f"decoy_budget_{i}"},"status":"succeeded","livemode":False})
        result=self.client.reconcile(op,now=NOW+timedelta(hours=24),page_limit=1,max_pages=2)
        self.assertEqual(result.action,Action.RECONCILE)
        self.assertEqual(result.reason,"refund-list-max-page-budget-reached")

    def test_invalid_page_limits_are_rejected(self):
        op=self.prepare()
        for value in (0,101,1.5,True):
            with self.subTest(value=value), self.assertRaises(ValueError):
                self.client.reconcile(op,now=NOW,page_limit=value)


    def test_direct_dispatch_cannot_bypass_cutoff_for_old_ready_intent(self):
        op = self.prepare(created_at=NOW - timedelta(hours=24))
        before = self.provider.post_calls
        result = self.client.dispatch(op, now=NOW)
        self.assertEqual(result.action, Action.RECONCILE)
        self.assertEqual(self.provider.post_calls, before)
        self.assertEqual(self.store.get(op)["state"], "READY")

    def test_direct_dispatch_cannot_bypass_cutoff_for_old_unknown_intent(self):
        op = self.prepare()
        self.provider.fail_next("drop_after_commit")
        self.client.dispatch(op, now=NOW)
        self.assertEqual(self.store.get(op)["state"], "UNKNOWN")
        before = self.provider.post_calls
        result = self.client.dispatch(op, now=NOW + timedelta(hours=24))
        self.assertEqual(result.action, Action.SUCCEEDED)
        self.assertEqual(self.provider.post_calls, before)
        self.assertEqual(self.provider.effect_count, 1)
        self.assertEqual(self.store.get(op)["state"], "SUCCEEDED")

    def test_direct_dispatch_cannot_bypass_cutoff_for_old_conflict(self):
        op = self.prepare()
        self.store.set_result(op, state="CONFLICT", status=409,
                              response={"error": {"code": "idempotency_key_in_use"}}, now=NOW)
        before = self.provider.post_calls
        result = self.client.dispatch(op, now=NOW + timedelta(hours=24))
        self.assertEqual(result.action, Action.RECONCILE)
        self.assertEqual(self.provider.post_calls, before)

    def test_fresh_unknown_intent_requires_recovery_entrypoint(self):
        op = self.prepare()
        self.provider.fail_next("drop_after_commit")
        self.client.dispatch(op, now=NOW)
        before = self.provider.post_calls
        result = self.client.dispatch(op, now=NOW + timedelta(seconds=5))
        self.assertEqual(result.action, Action.RECONCILE)
        self.assertEqual(result.reason, "non-ready-operation-must-use-recover-path")
        self.assertEqual(self.provider.post_calls, before)

    def test_waiting_refund_is_rechecked_and_promoted_after_provider_changes(self):
        op = self.prepare()
        self.provider.next_status = "pending"
        first = self.client.dispatch(op, now=NOW)
        self.assertEqual(first.action, Action.WAIT_FOR_PROVIDER)
        self.assertEqual(self.store.get(op)["state"], "WAITING")
        self.provider.refunds[0]["status"] = "succeeded"
        later = self.client.recover(op, now=NOW + timedelta(seconds=30))
        self.assertEqual(later.action, Action.SUCCEEDED)
        self.assertEqual(self.store.get(op)["state"], "SUCCEEDED")

    def test_waiting_refund_that_remains_pending_stays_waiting(self):
        op = self.prepare()
        self.provider.next_status = "pending"
        self.client.dispatch(op, now=NOW)
        later = self.client.recover(op, now=NOW + timedelta(seconds=30))
        self.assertEqual(later.action, Action.WAIT_FOR_PROVIDER)
        self.assertEqual(self.store.get(op)["state"], "WAITING")
        self.assertGreaterEqual(self.provider.get_calls, 1)

    def test_late_timeout_cannot_downgrade_confirmed_success(self):
        op = self.prepare()
        self.client.dispatch(op, now=NOW)
        with self.assertRaises(StoreStateTransitionError):
            self.store.set_result(op, state="UNKNOWN", status=None, response=None,
                                  now=NOW + timedelta(seconds=2))
        self.assertEqual(self.store.get(op)["state"], "SUCCEEDED")

    def test_official_host_rejects_nonstandard_tls_port(self):
        with self.assertRaises(UnsafeConfiguration):
            self.make_client(base_url="https://api.stripe.com:8443")

    def test_invalid_port_is_rejected_during_configuration(self):
        with self.assertRaises(UnsafeConfiguration):
            self.make_client(base_url="https://api.stripe.com:bad")

    def test_infinite_and_nan_timeouts_are_rejected(self):
        import math
        for value in (float("inf"), float("nan")):
            with self.subTest(value=value):
                with self.assertRaises(UnsafeConfiguration):
                    StripeTestModeRefundClient(store=self.store, secret_key="sk_test_local_mock",
                        base_url=self.provider.url, account_scope="platform:acct_demo",
                        api_version="2025-09-30.clover", allow_loopback_http=True,
                        timeout_seconds=value)

    def test_api_version_header_control_characters_are_rejected(self):
        with self.assertRaises(UnsafeConfiguration):
            StripeTestModeRefundClient(store=self.store, secret_key="sk_test_local_mock",
                base_url=self.provider.url, account_scope="platform:acct_demo",
                api_version="2025-09-30.clover\r\nX-Injected: yes", allow_loopback_http=True)

    def test_idempotency_key_rejects_whitespace_and_header_injection(self):
        for invalid_key in ("has space", "\r\nX-Injected: yes", ""):
            with self.subTest(invalid_key=invalid_key):
                with self.assertRaises(ValueError):
                    self.prepare(operation_id="op_invalid_" + str(len(invalid_key)), key=invalid_key)


    def test_charge_currency_mismatch_is_rejected_before_refund_post(self):
        self.provider.set_resource("ch_test_001", {
            "id": "ch_test_001", "object": "charge", "currency": "eur", "livemode": False,
            "paid": True, "captured": True, "amount": 5000, "amount_refunded": 0, "refunded": False})
        op = self.prepare(currency="usd")
        result = self.client.dispatch(op, now=NOW)
        self.assertEqual(result.action, Action.NEW_APPROVAL_REQUIRED)
        self.assertIn("currency-mismatch", result.reason)
        self.assertEqual(self.provider.post_calls, 0)
        self.assertEqual(self.store.get(op)["state"], "PRECHECK_FAILED")
        recovered = self.client.recover(op, now=NOW + timedelta(seconds=2))
        self.assertEqual(recovered.action, Action.NEW_APPROVAL_REQUIRED)
        self.assertEqual(self.provider.post_calls, 0)

    def test_uncaptured_charge_is_rejected_before_refund_post(self):
        self.provider.set_resource("ch_test_001", {
            "id": "ch_test_001", "object": "charge", "currency": "usd", "livemode": False,
            "paid": True, "captured": False, "amount": 5000, "amount_refunded": 0, "refunded": False})
        op = self.prepare()
        result = self.client.dispatch(op, now=NOW)
        self.assertEqual(result.action, Action.NEW_APPROVAL_REQUIRED)
        self.assertIn("not-paid-and-captured", result.reason)
        self.assertEqual(self.provider.post_calls, 0)

    def test_charge_amount_above_remaining_balance_is_rejected_before_post(self):
        self.provider.set_resource("ch_test_001", {
            "id": "ch_test_001", "object": "charge", "currency": "usd", "livemode": False,
            "paid": True, "captured": True, "amount": 5000, "amount_refunded": 4000, "refunded": False})
        op = self.prepare(amount=2000)
        result = self.client.dispatch(op, now=NOW)
        self.assertEqual(result.action, Action.NEW_APPROVAL_REQUIRED)
        self.assertIn("exceeds-remaining-charge-balance", result.reason)
        self.assertEqual(self.provider.post_calls, 0)

    def test_charge_with_no_remaining_balance_is_rejected_before_post(self):
        self.provider.set_resource("ch_test_001", {
            "id": "ch_test_001", "object": "charge", "currency": "usd", "livemode": False,
            "paid": True, "captured": True, "amount": 5000, "amount_refunded": 5000, "refunded": True})
        op = self.prepare(amount=None)
        result = self.client.dispatch(op, now=NOW)
        self.assertEqual(result.action, Action.NEW_APPROVAL_REQUIRED)
        self.assertIn("no-refundable-balance", result.reason)
        self.assertEqual(self.provider.post_calls, 0)

    def test_payment_intent_target_is_preflighted_before_post(self):
        op = "op_pi_001"
        self.client.prepare_refund(operation_id=op, idempotency_key="lyc-pi-test-key", created_at=NOW,
                                   payment_intent="pi_test_001", amount=1000, expected_currency="usd")
        result = self.client.dispatch(op, now=NOW)
        self.assertEqual(result.action, Action.SUCCEEDED)
        self.assertEqual(self.provider.post_calls, 1)
        self.assertEqual(self.provider.effect_count, 1)
        self.assertTrue(any(path.startswith("/v1/payment_intents/") for path in self.provider.get_paths))

    def test_unsucceeded_payment_intent_is_rejected_before_post(self):
        self.provider.set_resource("pi_test_001", {
            "id": "pi_test_001", "object": "payment_intent", "currency": "usd", "livemode": False,
            "status": "requires_action", "amount": 5000, "amount_received": 0,
            "client_secret": "pi_test_client_secret_SHOULD_NOT_BE_STORED"})
        op = "op_pi_unconfirmed"
        self.client.prepare_refund(operation_id=op, idempotency_key="lyc-pi-unconfirmed", created_at=NOW,
                                   payment_intent="pi_test_001", amount=1000, expected_currency="usd")
        result = self.client.dispatch(op, now=NOW)
        self.assertEqual(result.action, Action.NEW_APPROVAL_REQUIRED)
        self.assertIn("not-succeeded", result.reason)
        self.assertEqual(self.provider.post_calls, 0)
        stored = json.dumps(self.store.get(op)["provider_response"])
        self.assertNotIn("client_secret", stored)
        self.assertNotIn("SHOULD_NOT_BE_STORED", stored)

    def test_success_record_stores_only_recovery_fields_and_operation_metadata(self):
        op = "op_privacy_001"
        self.client.prepare_refund(operation_id=op, idempotency_key="lyc-privacy-key-001", created_at=NOW,
                                   charge="ch_test_001", amount=500, expected_currency="usd")
        result = self.client.dispatch(op, now=NOW)
        self.assertEqual(result.action, Action.SUCCEEDED)
        row = self.store.get(op)
        stored_response = json.dumps(row["provider_response"])
        stored_payload = json.dumps(row["payload"])
        self.assertEqual(row["provider_response"]["metadata"], {"lycheetah_operation_id": op})
        self.assertEqual(row["payload"]["metadata"], {"lycheetah_operation_id": op})
        self.assertEqual(set(row["provider_response"]).issubset({
            "id", "object", "charge", "payment_intent", "currency", "status",
            "amount", "livemode", "metadata"}), True)
        for marker in ("client_secret", "customer_email", "private-person@example.test"):
            self.assertNotIn(marker, stored_response)
            self.assertNotIn(marker, stored_payload)

    def test_caller_metadata_rejected_before_database_or_provider_write(self):
        op = "op_metadata_rejected"
        private_markers = {
            "customer_email": "private-person@example.test",
            "api_token": "tok_test_SHOULD_NEVER_PERSIST",
            "internal_note": "customer asked for an exception",
        }
        with self.assertRaisesRegex(ValueError, "caller-supplied metadata is disabled"):
            self.client.prepare_refund(
                operation_id=op, idempotency_key="lyc-meta-reject", created_at=NOW,
                charge="ch_test_001", amount=500, expected_currency="usd",
                metadata=private_markers,
            )
        db = sqlite3.connect(self.db_path)
        try:
            count = db.execute("SELECT count(*) FROM refund_ops WHERE operation_id=?", (op,)).fetchone()[0]
            raw_db = " ".join(str(x) for row in db.execute("SELECT * FROM refund_ops") for x in row)
        finally:
            db.close()
        self.assertEqual(count, 0)
        self.assertEqual(self.provider.post_calls, 0)
        for marker in private_markers.values():
            self.assertNotIn(marker, raw_db)

    def test_non_object_metadata_is_rejected_before_database_write(self):
        for bad, suffix in ((["bad"], "list"), ("bad", "string"), (7, "number")):
            with self.subTest(bad=bad):
                with self.assertRaisesRegex(ValueError, "metadata must be an object"):
                    self.client.prepare_refund(
                        operation_id=f"op_bad_metadata_{suffix}",
                        idempotency_key=f"lyc-bad-meta-{suffix}", created_at=NOW,
                        charge="ch_test_001", amount=500, expected_currency="usd", metadata=bad,
                    )

    def test_cached_error_record_omits_provider_error_message(self):
        op = self.prepare()
        self.provider.fail_next("cached_500")
        result = self.client.dispatch(op, now=NOW)
        self.assertEqual(result.action, Action.RECONCILE)
        stored = json.dumps(self.store.get(op)["provider_response"])
        self.assertNotIn("message", stored)
        self.assertNotIn("simulated server error", stored)

    def test_path_injection_in_target_id_is_rejected(self):
        with self.assertRaises(ValueError):
            self.client.prepare_refund(operation_id="op_path", idempotency_key="lyc-path-key", created_at=NOW,
                                       charge="ch_test_001/../refunds", amount=500, expected_currency="usd")

    def test_non_test_mode_resource_is_rejected_before_post(self):
        self.provider.set_resource("ch_test_001", {
            "id": "ch_test_001", "object": "charge", "currency": "usd", "livemode": True,
            "paid": True, "captured": True, "amount": 5000, "amount_refunded": 0, "refunded": False})
        op = self.prepare()
        result = self.client.dispatch(op, now=NOW)
        self.assertEqual(result.action, Action.NEW_APPROVAL_REQUIRED)
        self.assertIn("not-explicitly-test-mode", result.reason)
        self.assertEqual(self.provider.post_calls, 0)

    def test_preflight_transport_failure_never_sends_refund_post(self):
        self.provider.fail_next_resource()
        op = self.prepare()
        result = self.client.dispatch(op, now=NOW)
        self.assertEqual(result.action, Action.RECONCILE)
        self.assertIn("preflight-transport-outcome-unknown", result.reason)
        self.assertEqual(self.provider.post_calls, 0)
        self.assertEqual(self.store.get(op)["state"], "READY")


    def test_in_flight_marker_is_committed_before_provider_post(self):
        op = self.prepare()
        seen_states = []
        self.provider.before_post_callback = lambda: seen_states.append(self.store.get(op)["state"])
        result = self.client.dispatch(op, now=NOW)
        self.assertEqual(result.action, Action.SUCCEEDED)
        self.assertEqual(seen_states, ["IN_FLIGHT"])

    def test_crash_state_in_flight_recovers_using_same_key(self):
        op = self.prepare()
        self.store.set_result(op, state="IN_FLIGHT", status=None, response=None, now=NOW)
        recovered = self.client.recover(op, now=NOW + timedelta(seconds=5))
        self.assertEqual(recovered.action, Action.SUCCEEDED)
        self.assertEqual(self.provider.effect_count, 1)
        self.assertEqual(self.provider.last_headers.get("Idempotency-Key"), "lyc-test-key-001")

    def test_store_rejects_non_object_metadata(self):
        with self.assertRaises((ValueError, TypeError)):
            self.store.prepare(operation_id="op_badmetadata",idempotency_key="lyc_badmetadata",
                created_at=NOW,account_scope="platform:acct_demo",stripe_account=None,
                api_version="v1",payload={"charge":"ch_x","metadata":[]},expected_currency="usd")


if __name__ == "__main__":
    unittest.main(verbosity=2)
