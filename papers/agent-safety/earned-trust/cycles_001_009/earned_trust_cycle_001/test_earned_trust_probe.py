import unittest
from earned_trust_probe import (
    Action, World, SCENARIOS, STRATEGIES, run_one, run_all,
    audit_chain, audit_chain_verify, Observation, finality_ready,
)


class ProbeTests(unittest.TestCase):
    def test_twenty_cases(self):
        self.assertEqual(len(SCENARIOS), 20)

    def test_four_controls(self):
        self.assertEqual(len(STRATEGIES), 4)

    def test_initial_permission(self):
        w, a = World(), Action()
        w.approved_hash = a.hash
        self.assertTrue(w.current_permission(a))

    def test_changed_action_requires_reapproval(self):
        w, a = World(), Action()
        w.approved_hash = a.hash
        self.assertFalse(w.current_permission(Action(amount_cents=9000)))

    def test_invalid_amount_rejected(self):
        w, a = World(), Action(amount_cents=0)
        w.approved_hash = a.hash
        self.assertFalse(w.current_permission(a))

    def test_provider_idempotency(self):
        w, a = World(), Action()
        w.approved_hash = a.hash
        self.assertTrue(w.conditional_commit(a))
        self.assertFalse(w.conditional_commit(a))
        self.assertEqual(w.effects, 1)

    def test_benign_evidence_revision_allowed(self):
        row = run_one(SCENARIOS[1], 'conditional_provider')
        self.assertTrue(row.performed)
        self.assertTrue(row.safe_at_commit)

    def test_finality_does_not_cover_later_revoke(self):
        case = next(c for c in SCENARIOS if c.name == 'eligibility_revoked_between_finality_commit')
        row = run_one(case, 'finality_recheck')
        self.assertTrue(row.performed)
        self.assertFalse(row.safe_at_commit)

    def test_conditional_commit_covers_later_revoke(self):
        case = next(c for c in SCENARIOS if c.name == 'eligibility_revoked_between_finality_commit')
        row = run_one(case, 'conditional_provider')
        self.assertFalse(row.performed)
        self.assertFalse(row.safe_at_commit)

    def test_conventional_baseline_parity(self):
        for case in SCENARIOS:
            self.assertEqual(run_one(case, 'conditional_provider').performed,
                             run_one(case, 'conventional_atomic').performed)

    def test_provider_catches_all_observable_stale_cases(self):
        for case in SCENARIOS:
            if 'evidence_lies' not in case.name:
                self.assertTrue(run_one(case, 'conditional_provider').correct, case.name)

    def test_conventional_matches_same_observable_boundary(self):
        for case in SCENARIOS:
            if 'evidence_lies' not in case.name:
                self.assertTrue(run_one(case, 'conventional_atomic').correct, case.name)

    def test_false_evidence_cannot_be_fixed_by_atomicity(self):
        for case in SCENARIOS:
            if 'evidence_lies' in case.name:
                row = run_one(case, 'conditional_provider')
                self.assertTrue(row.performed)
                self.assertFalse(row.safe_at_commit)

    def test_policy_change_after_finality(self):
        case = next(c for c in SCENARIOS if c.name == 'policy_lowered_between_finality_commit')
        self.assertFalse(run_one(case, 'conditional_provider').performed)
        self.assertTrue(run_one(case, 'finality_recheck').performed)

    def test_replay_after_finality(self):
        case = next(c for c in SCENARIOS if c.name == 'already_processed_between_finality_commit')
        self.assertFalse(run_one(case, 'conditional_provider').performed)
        self.assertTrue(run_one(case, 'admission_only').performed)

    def test_subject_swap_after_finality(self):
        case = next(c for c in SCENARIOS if c.name == 'evidence_subject_swapped_between_finality_commit')
        self.assertFalse(run_one(case, 'conditional_provider').performed)

    def test_admission_snapshot_not_permit(self):
        w, a = World(), Action()
        w.approved_hash = a.hash
        admitted = w.read_snapshot(a)
        w.approved_hash = 'revoked'
        self.assertFalse(finality_ready(w, a, admitted))

    def test_audit_chain_detects_payload_flip(self):
        obs = [Observation('a','b',True,True,True,'ok')]
        chain = audit_chain(obs)
        self.assertTrue(audit_chain_verify(chain))
        chain[0]['performed'] = False
        self.assertFalse(audit_chain_verify(chain))

    def test_audit_chain_detects_truncation_only_with_external_anchor(self):
        obs = [Observation('a','b',True,True,True,'ok'),
               Observation('c','d',False,False,True,'ok')]
        chain = audit_chain(obs)
        # Important negative control: without trusted tail, truncation is invisible.
        self.assertTrue(audit_chain_verify(chain[:-1]))

    def test_reporting_counts(self):
        result = run_all()
        self.assertEqual(result['observation_count'], 80)
        self.assertTrue(result['audit_chain_valid'])


if __name__ == '__main__':
    unittest.main(verbosity=2)
