import json
import tempfile
import threading
import unittest
from pathlib import Path

from provider_contract import (
    AtomicConditionalProvider, CheckThenActProvider, ConditionDenied,
    IdempotencyConflict, InjectedCrash, NonIdempotentProvider, ResponseLost,
)
from model_check import VALID, evaluate_atomic, evaluate_split


class ProviderContractTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.path = Path(self.tmp.name) / "provider.db"
        self.provider = AtomicConditionalProvider(self.path)
        self.provider.set_condition("release", "v1", "PASS")
        self.payload = {"artifact": "sha256:abc", "environment": "staging"}

    def tearDown(self):
        self.tmp.cleanup()

    def test_atomic_provider_accepts_matching_condition(self):
        result = self.provider.execute("op-1", self.payload, condition_key="release", required_status="PASS", required_version="v1")
        self.assertTrue(result["accepted"])
        self.assertFalse(result["replayed"])
        self.assertEqual(1, self.provider.effect_count())

    def test_failed_condition_rejected_without_effect(self):
        self.provider.set_condition("release", "v2", "FAIL")
        with self.assertRaises(ConditionDenied):
            self.provider.execute("op-1", self.payload, condition_key="release", required_status="PASS")
        self.assertEqual(0, self.provider.effect_count())

    def test_version_bound_predicate_rejects_newer_version(self):
        self.provider.set_condition("release", "v2", "PASS")
        with self.assertRaises(ConditionDenied):
            self.provider.execute("op-1", self.payload, condition_key="release", required_status="PASS", required_version="v1")
        self.assertEqual(0, self.provider.effect_count())

    def test_same_key_same_payload_recovers_result(self):
        first = self.provider.execute("op-1", self.payload, condition_key="release", required_status="PASS")
        retry = self.provider.execute("op-1", self.payload, condition_key="release", required_status="FAIL")
        self.assertEqual(first["operation_id"], retry["operation_id"])
        self.assertEqual(1, self.provider.effect_count())
        self.assertFalse(first["replayed"])
        self.assertTrue(retry["replayed"])

    def test_same_key_different_payload_conflicts(self):
        self.provider.execute("op-1", self.payload, condition_key="release", required_status="PASS")
        with self.assertRaises(IdempotencyConflict):
            self.provider.execute("op-1", {**self.payload, "environment": "production"}, condition_key="release", required_status="PASS")
        self.assertEqual(1, self.provider.effect_count())

    def test_response_lost_after_commit_is_recoverable(self):
        self.provider.drop_next_response = True
        with self.assertRaises(ResponseLost):
            self.provider.execute("op-1", self.payload, condition_key="release", required_status="PASS")
        # Recreate the adapter object to exercise persisted provider state.
        recovered = AtomicConditionalProvider(self.path)
        value = recovered.lookup("op-1", self.payload)
        self.assertIsNotNone(value)
        self.assertEqual(1, recovered.effect_count())

    def test_crash_before_commit_rolls_back(self):
        self.provider.crash_before_commit = True
        with self.assertRaises(InjectedCrash):
            self.provider.execute("op-1", self.payload, condition_key="release", required_status="PASS")
        self.assertEqual(0, self.provider.effect_count())
        retry = self.provider.execute("op-1", self.payload, condition_key="release", required_status="PASS")
        self.assertTrue(retry["accepted"])
        self.assertEqual(1, self.provider.effect_count())

    def test_duplicate_calls_linearize_to_one_effect(self):
        barrier = threading.Barrier(3)
        results, errors = [], []
        def run():
            barrier.wait()
            try:
                results.append(self.provider.execute("op-race", self.payload, condition_key="release", required_status="PASS"))
            except Exception as exc:
                errors.append(exc)
        ts = [threading.Thread(target=run) for _ in range(2)]
        [t.start() for t in ts]
        barrier.wait()
        [t.join() for t in ts]
        self.assertEqual([], errors)
        self.assertEqual(2, len(results))
        self.assertEqual(1, self.provider.effect_count("op-race"))

    def test_concurrent_condition_update_never_allows_false_at_commit(self):
        for i in range(12):
            path = Path(self.tmp.name) / f"race-{i}.db"
            p = AtomicConditionalProvider(path)
            p.set_condition("release", "v1", "PASS")
            barrier = threading.Barrier(3)
            result, errors = [], []
            def action():
                barrier.wait()
                try:
                    result.append(p.execute("op", self.payload, condition_key="release", required_status="PASS"))
                except ConditionDenied:
                    result.append(None)
                except Exception as exc:
                    errors.append(exc)
            def update():
                barrier.wait()
                p.set_condition("release", "v2", "FAIL")
            a, b = threading.Thread(target=action), threading.Thread(target=update)
            a.start(); b.start(); barrier.wait(); a.join(); b.join()
            self.assertEqual([], errors)
            committed = p.lookup("op", self.payload)
            final = p.get_condition("release")
            if committed is not None:
                self.assertEqual("PASS", committed["condition_status"])
                self.assertEqual("FAIL", final["status"])
            else:
                self.assertEqual(0, p.effect_count())
                self.assertEqual("FAIL", final["status"])

    def test_retry_result_survives_condition_revocation_after_effect(self):
        self.provider.execute("op-1", self.payload, condition_key="release", required_status="PASS")
        self.provider.set_condition("release", "v2", "FAIL")
        # This is result recovery, not a new effect; the committed result must remain queryable.
        value = self.provider.lookup("op-1", self.payload)
        self.assertIsNotNone(value)
        self.assertEqual(1, self.provider.effect_count())

    def test_split_check_then_act_control_exposes_stale_evidence(self):
        p = CheckThenActProvider()
        p.after_check = lambda: p.set_condition("v2", "FAIL")
        result = p.execute("op-1", self.payload, required_status="PASS")
        self.assertEqual("PASS", result["condition_status"])
        self.assertEqual("FAIL", p.condition["status"])
        self.assertEqual(1, p.effect_count())

    def test_non_idempotent_retry_duplicates_control_effect(self):
        p = NonIdempotentProvider()
        p.drop_next_response = True
        with self.assertRaises(ResponseLost):
            p.execute("op-1", self.payload)
        p.execute("op-1", self.payload)
        self.assertEqual(2, p.effect_count())

    def test_ordered_schedule_model_finds_split_check_violation(self):
        split = [evaluate_split(p) for p in VALID]
        atomic = [evaluate_atomic(p) for p in VALID]
        self.assertGreaterEqual(sum(x["safety_violation"] for x in split), 1)
        self.assertEqual(0, sum(x["safety_violation"] for x in atomic))

    def test_atomic_provider_claims_contract_capabilities(self):
        self.assertTrue(self.provider.supports_durable_idempotency)
        self.assertTrue(self.provider.supports_atomic_condition)
        self.assertTrue(self.provider.supports_lookup)

    def test_negative_controls_do_not_claim_atomic_condition(self):
        self.assertFalse(CheckThenActProvider.supports_atomic_condition)
        self.assertFalse(NonIdempotentProvider.supports_durable_idempotency)


if __name__ == "__main__":
    unittest.main(verbosity=2)
