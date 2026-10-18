"""Synthetic sqlite integration/property probes (NOT real Framework imports)."""
import concurrent.futures
import tempfile
import unittest
from pathlib import Path

from transactional_provider import ConditionalRefundProvider, Intent, LostResponse


class ProviderTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.provider = ConditionalRefundProvider(Path(self.temp.name) / "provider.sqlite")
        self.intent = Intent("effect-1", "approval-1", "agent-1", "customer-1", 1200)
        self.provider.seed(self.intent)

    def test_valid(self):
        self.assertTrue(self.provider.commit(self.intent).committed)
        self.assertEqual(self.provider.effect_count(), 1)

    def test_double_dispatch(self):
        self.provider.commit(self.intent)
        self.assertEqual(self.provider.commit(self.intent).code, "IDEMPOTENT_REPLAY")
        self.assertEqual(self.provider.effect_count(), 1)

    def test_replay_after_revoke_is_read_not_write(self):
        self.provider.commit(self.intent)
        self.provider.change(actor="agent-1", revoke=True)
        self.assertEqual(self.provider.commit(self.intent).code, "IDEMPOTENT_REPLAY")
        self.assertEqual(self.provider.effect_count(), 1)

    def test_approval_revocation_before_write(self):
        self.provider.change(actor="agent-1", revoke=True)
        self.assertEqual(self.provider.commit(self.intent).code, "REVOKED")
        self.assertEqual(self.provider.effect_count(), 0)

    def test_eligibility_between_preview_and_commit(self):
        self.assertEqual(self.provider.preview(self.intent).code, "READY")
        self.provider.change(subject="customer-1", eligible=False)
        self.assertEqual(self.provider.commit(self.intent).code, "EVIDENCE_NOT_PASS")

    def test_evidence_missing_or_failed(self):
        self.provider.change(subject="customer-1", evidence_status="FAIL")
        self.assertEqual(self.provider.commit(self.intent).code, "EVIDENCE_NOT_PASS")

    def test_policy_change_after_preview(self):
        self.assertEqual(self.provider.preview(self.intent).code, "READY")
        self.provider.change(maximum=1000)
        self.assertEqual(self.provider.commit(self.intent).code, "POLICY_LIMIT")

    def test_wrong_amount(self):
        swapped = Intent(self.intent.effect_id, self.intent.approval_id, self.intent.actor, self.intent.subject, 1300)
        self.assertEqual(self.provider.commit(swapped).code, "INVALID_GRANT_OR_PAYLOAD")

    def test_wrong_subject(self):
        swapped = Intent(self.intent.effect_id, self.intent.approval_id, self.intent.actor, "customer-2", 1200)
        self.assertEqual(self.provider.commit(swapped).code, "INVALID_GRANT_OR_PAYLOAD")

    def test_wrong_scope(self):
        swapped = Intent(self.intent.effect_id, self.intent.approval_id, self.intent.actor, self.intent.subject, 1200, "refund:unlimited")
        self.assertEqual(self.provider.commit(swapped).code, "INVALID_GRANT_OR_PAYLOAD")

    def test_expired(self):
        self.assertEqual(self.provider.commit(self.intent, now=200).code, "EXPIRED_OR_EARLY")

    def test_early(self):
        self.assertEqual(self.provider.commit(self.intent, now=99).code, "EXPIRED_OR_EARLY")

    def test_exact_version_rejects_benign_revision(self):
        exact = Intent(self.intent.effect_id, self.intent.approval_id, self.intent.actor, self.intent.subject, 1200, expected_version=1)
        self.provider.change(subject="customer-1", eligible=True)
        self.assertEqual(self.provider.commit(exact).code, "SUBJECT_VERSION_CHANGED")
        self.assertEqual(self.provider.commit(self.intent).code, "COMMITTED")

    def test_stale_evidence_truth_gap_survives(self):
        self.provider.change(subject="customer-1", truth=False)
        self.assertFalse(self.provider.recorded_truth_for("customer-1"))
        self.assertEqual(self.provider.commit(self.intent).code, "COMMITTED")
        self.assertEqual(self.provider.effect_count(), 1)

    def test_provider_response_lost_after_write(self):
        with self.assertRaises(LostResponse):
            self.provider.commit(self.intent, lose_response=True)
        self.assertEqual(self.provider.reconcile(self.intent).code, "RECONCILED_COMMITTED")
        self.assertEqual(self.provider.commit(self.intent).code, "IDEMPOTENT_REPLAY")
        self.assertEqual(self.provider.effect_count(), 1)

    def test_provider_response_lost_before_write(self):
        self.assertEqual(self.provider.reconcile(self.intent).code, "NOT_FOUND")
        self.assertEqual(self.provider.effect_count(), 0)

    def test_collision_same_effect_id_other_payload(self):
        self.provider.commit(self.intent)
        swapped = Intent("effect-1", "approval-1", "agent-1", "customer-1", 1300)
        self.assertEqual(self.provider.commit(swapped).code, "EFFECT_ID_CONFLICT")
        self.assertEqual(self.provider.reconcile(swapped).code, "EFFECT_ID_CONFLICT")

    def test_new_effect_id_cannot_reuse_approval(self):
        self.provider.commit(self.intent)
        second = Intent("effect-2", "approval-1", "agent-1", "customer-1", 1200)
        self.assertEqual(self.provider.commit(second).code, "GRANT_ALREADY_USED")
        self.assertEqual(self.provider.effect_count(), 1)

    def test_concurrent_workers_exactly_once(self):
        with concurrent.futures.ThreadPoolExecutor(max_workers=16) as pool:
            outcomes = list(pool.map(lambda _: self.provider.commit(self.intent).code, range(32)))
        self.assertEqual(outcomes.count("COMMITTED"), 1)
        self.assertEqual(outcomes.count("IDEMPOTENT_REPLAY"), 31)
        self.assertEqual(self.provider.effect_count(), 1)

    def test_concurrent_distinct_intents_one_grant(self):
        a = self.intent
        b = Intent("effect-2", "approval-1", "agent-1", "customer-1", 1200)
        with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
            codes = list(pool.map(lambda i: self.provider.commit(i).code, [a, b]))
        self.assertEqual(codes.count("COMMITTED"), 1)
        self.assertEqual(codes.count("GRANT_ALREADY_USED"), 1)
        self.assertEqual(self.provider.effect_count(), 1)

    def test_no_approval(self):
        other = Intent("effect-3", "missing-grant", "agent-1", "customer-1", 1200)
        self.assertEqual(self.provider.commit(other).code, "INVALID_GRANT_OR_PAYLOAD")

    def test_invalid_amount(self):
        other = Intent("effect-1", "approval-1", "agent-1", "customer-1", -1)
        self.assertEqual(self.provider.commit(other).code, "INVALID_AMOUNT")

    def test_no_actual_provider_guarantees(self):
        # This is a model assertion, not a success condition: SQLite controls only its OWN DB.
        self.assertIn("sqlite", self.provider.path)


if __name__ == "__main__":
    unittest.main()
