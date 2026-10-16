import unittest
from recovery_policy import (ProviderContractProfile, LookupState, RecoveryDecision,
                             classify_ambiguous_recovery)

class RecoveryPolicyTests(unittest.TestCase):
    def setUp(self):
        self.good = ProviderContractProfile("Fixture", "deploy.create", True, True, 86400, True, True)

    def classify(self, **kwargs):
        return classify_ambiguous_recovery(profile=kwargs.pop("profile", self.good), **kwargs)

    def test_definitive_not_found_retries_same_key_inside_window(self):
        self.assertEqual(RecoveryDecision.RETRY_SAME_KEY, self.classify(lookup_state=LookupState.DEFINITIVE_NOT_FOUND, elapsed_seconds=60))

    def test_committed_result_uses_authoritative_lookup(self):
        self.assertEqual(RecoveryDecision.ACCEPT_STORED_RESULT, self.classify(lookup_state=LookupState.COMMITTED, elapsed_seconds=90000, lookup_operation_id_matches=True, lookup_payload_sha256_matches=True))

    def test_unavailable_or_ambiguous_lookup_requires_reconciliation(self):
        self.assertEqual(RecoveryDecision.RECONCILE, self.classify(lookup_state=LookupState.UNKNOWN, elapsed_seconds=10))

    def test_unknown_lookup_capability_cannot_assert_commit(self):
        p = ProviderContractProfile("Fixture", "op", True, True, 86400, False, True)
        self.assertEqual(RecoveryDecision.RECONCILE, self.classify(profile=p, lookup_state=LookupState.COMMITTED, elapsed_seconds=1, lookup_operation_id_matches=True, lookup_payload_sha256_matches=True))

    def test_ttl_boundary_requires_reconciliation(self):
        self.assertEqual(RecoveryDecision.RECONCILE, self.classify(lookup_state=LookupState.DEFINITIVE_NOT_FOUND, elapsed_seconds=86400))

    def test_unknown_retention_requires_reconciliation(self):
        p = ProviderContractProfile("Fixture", "op", True, True, None, True, True)
        self.assertEqual(RecoveryDecision.RECONCILE, self.classify(profile=p, lookup_state=LookupState.DEFINITIVE_NOT_FOUND, elapsed_seconds=10))

    def test_non_idempotent_provider_never_blindly_retries(self):
        p = ProviderContractProfile("Fixture", "op", False, False, None, False, False)
        self.assertEqual(RecoveryDecision.RECONCILE, self.classify(profile=p, lookup_state=LookupState.DEFINITIVE_NOT_FOUND, elapsed_seconds=1))

    def test_payload_mismatch_not_bound_requires_reconciliation(self):
        p = ProviderContractProfile("Fixture", "op", True, False, 86400, True, True)
        self.assertEqual(RecoveryDecision.RECONCILE, self.classify(profile=p, lookup_state=LookupState.DEFINITIVE_NOT_FOUND, elapsed_seconds=1))

    def test_condition_check_not_atomic_requires_reconciliation(self):
        p = ProviderContractProfile("Fixture", "op", True, True, 86400, True, False)
        self.assertEqual(RecoveryDecision.RECONCILE, self.classify(profile=p, lookup_state=LookupState.DEFINITIVE_NOT_FOUND, elapsed_seconds=1, condition_sensitive=True))

    def test_read_only_operation_need_not_require_condition_atomicity(self):
        p = ProviderContractProfile("Fixture", "read.lookup", True, True, 86400, True, False)
        self.assertEqual(RecoveryDecision.RETRY_SAME_KEY, self.classify(profile=p, lookup_state=LookupState.DEFINITIVE_NOT_FOUND, elapsed_seconds=1, condition_sensitive=False))


    def test_committed_result_with_wrong_payload_binding_requires_reconciliation(self):
        self.assertEqual(RecoveryDecision.RECONCILE, self.classify(
            lookup_state=LookupState.COMMITTED, elapsed_seconds=5,
            lookup_operation_id_matches=True, lookup_payload_sha256_matches=False))

    def test_committed_result_without_explicit_identity_binding_requires_reconciliation(self):
        self.assertEqual(RecoveryDecision.RECONCILE, self.classify(
            lookup_state=LookupState.COMMITTED, elapsed_seconds=5))

    def test_non_authoritative_not_found_requires_reconciliation(self):
        p = ProviderContractProfile("Fixture", "op", True, True, 86400, False, True)
        self.assertEqual(RecoveryDecision.RECONCILE, self.classify(
            profile=p, lookup_state=LookupState.DEFINITIVE_NOT_FOUND, elapsed_seconds=5))

    def test_negative_elapsed_is_rejected(self):
        with self.assertRaises(ValueError):
            self.classify(lookup_state=LookupState.UNKNOWN, elapsed_seconds=-1)

if __name__ == "__main__":
    unittest.main(verbosity=2)
