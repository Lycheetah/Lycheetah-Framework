"""Independent behavioural checks. No network access or external effects."""
from __future__ import annotations
import concurrent.futures
from contextlib import closing
import sqlite3
import tempfile
import threading
import unittest
from pathlib import Path
from choice_fence import Action, ChoiceFence
from benchmark import scenario, before_and_after_examples, KEY, START


class FenceChecks(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.clock_value = [START]
        self.fence = ChoiceFence(Path(self.temp.name) / 'c.db', key=KEY, clock=lambda: self.clock_value[0])
        self.fence.register('human')
        self.action = Action('human', 'assistant', 'send_email', 'r@example.test', 'effect-1', 'exact bytes')

    def issue(self, ticket='ticket-1', action=None, expiry=START + 300, approved=True):
        return self.fence.issue(ticket, action or self.action, expires_at=expiry,
                                explicit_human_approval=approved)

    def test_01_valid_approved_action_commits(self):
        self.issue()
        self.assertTrue(self.fence.commit('ticket-1', self.action).committed)
        self.assertEqual(self.fence.effect_count(), 1)

    def test_02_no_high_risk_approval_blocks_at_issue(self):
        with self.assertRaises(ValueError): self.issue(approved=False)

    def test_03_no_unsafe_operation(self):
        a = Action('human','assistant','delete_database','x','effect-1','text')
        with self.assertRaises(ValueError): self.issue(action=a)

    def test_04_revoked_ticket_denied_at_commit(self):
        self.issue(); self.fence.revoke('human','ticket-1')
        self.assertEqual(self.fence.commit('ticket-1',self.action).reason,'revoked')
        self.assertEqual(self.fence.effect_count(),0)

    def test_05_changed_intent_denied(self):
        self.issue(); self.fence.revise('human',reason='changed mind')
        self.assertEqual(self.fence.commit('ticket-1',self.action).reason,'stale_intent')

    def test_06_unmodified_fresh_intent_accepted(self):
        self.issue(); self.fence.revise('human',reason='changed mind')
        a = Action('human','assistant','send_email','r@example.test','new-effect','corrected')
        self.issue(ticket='new',action=a)
        self.assertTrue(self.fence.commit('new',a).committed)

    def test_07_wrong_payload_denied(self):
        self.issue(); modified = Action('human','assistant','send_email','r@example.test','effect-1','altered')
        self.assertEqual(self.fence.commit('ticket-1',modified).reason,'action_substitution')

    def test_08_wrong_agent_denied(self):
        self.issue(); modified = Action('human','other','send_email','r@example.test','effect-1','exact bytes')
        self.assertEqual(self.fence.commit('ticket-1',modified).reason,'action_substitution')

    def test_09_wrong_resource_denied(self):
        self.issue(); modified = Action('human','assistant','send_email','wrong@example.test','effect-1','exact bytes')
        self.assertEqual(self.fence.commit('ticket-1',modified).reason,'action_substitution')

    def test_10_expiry_denied_inclusive_boundary(self):
        self.issue(expiry=START+1); self.clock_value[0] = START+1
        self.assertEqual(self.fence.commit('ticket-1',self.action).reason,'expired')

    def test_11_replay_denied(self):
        self.issue(); self.assertTrue(self.fence.commit('ticket-1',self.action).committed)
        self.assertEqual(self.fence.commit('ticket-1',self.action).reason,'replayed')
        self.assertEqual(self.fence.effect_count(),1)

    def test_12_ticket_id_reuse_denied(self):
        self.issue()
        with self.assertRaises(sqlite3.IntegrityError): self.issue()

    def test_13_effect_id_reuse_denied(self):
        self.issue(); self.fence.commit('ticket-1',self.action)
        # New ticket may be issued, but cannot create a second durable effect with same id.
        self.issue(ticket='ticket-2')
        self.assertEqual(self.fence.commit('ticket-2',self.action).reason,'effect_already_exists')

    def test_14_owner_mismatch_denied(self):
        self.issue()
        fake = Action('other','assistant','send_email','r@example.test','effect-1','exact bytes')
        self.assertEqual(self.fence.commit('ticket-1',fake).reason,'wrong_owner')

    def test_15_unknown_ticket_denied(self):
        self.assertEqual(self.fence.commit('unknown',self.action).reason,'unknown_ticket')

    def test_16_audit_chain_valid(self):
        self.issue(); self.fence.commit('ticket-1',self.action)
        self.assertTrue(self.fence.audit_ok())

    def test_17_audit_mutation_detected(self):
        self.issue()
        with closing(self.fence.connect()) as cx:
            cx.execute("UPDATE audit SET detail='{}' WHERE seq=(SELECT MAX(seq) FROM audit)")
        self.assertFalse(self.fence.audit_ok())

    def test_18_after_commit_revoke_does_not_undo_effect(self):
        self.issue(); self.fence.commit('ticket-1',self.action)
        self.fence.revoke('human','ticket-1')
        self.assertEqual(self.fence.effect_count(),1)

    def test_19_low_impact_explicit_approval_not_required(self):
        a=Action('human','assistant','prepare_draft','draft','draft-1','body')
        self.issue(action=a,approved=False)
        self.assertTrue(self.fence.commit('ticket-1',a).committed)

    def test_20_invalid_clock_fails(self):
        self.clock_value[0]='agent controlled time'
        with self.assertRaises(ValueError): self.issue()

    def test_21_parallel_commits_exactly_once(self):
        self.issue()
        barrier=threading.Barrier(12)
        def worker(i):
            barrier.wait(timeout=10)
            return self.fence.commit('ticket-1',self.action).committed
        with concurrent.futures.ThreadPoolExecutor(max_workers=12) as pool:
            results=list(pool.map(worker, range(12)))
        self.assertEqual(sum(results),1)
        self.assertEqual(self.fence.effect_count(),1)
        self.assertTrue(self.fence.audit_ok())

    def test_22_revocation_first_order_prevents_effect(self):
        self.issue(); self.fence.revoke('human','ticket-1')
        self.assertFalse(self.fence.commit('ticket-1',self.action).committed)

    def test_23_commit_first_order_cannot_be_reversed(self):
        self.issue(); self.assertTrue(self.fence.commit('ticket-1',self.action).committed)
        self.fence.revise('human',reason='later revision')
        self.assertEqual(self.fence.effect_count(),1)

    def test_24_no_ownership_claim_for_reason(self):
        self.issue(); self.fence.revise('human',reason='rest is my legitimate choice')
        self.assertEqual(self.fence.commit('ticket-1',self.action).reason,'stale_intent')

    def test_25_revocation_wrong_owner_does_not_revoke(self):
        self.issue(); self.assertFalse(self.fence.revoke('wrong','ticket-1'))
        self.assertTrue(self.fence.commit('ticket-1',self.action).committed)

    def test_26_new_intent_new_ticket_no_stale_rights(self):
        self.issue(); self.fence.revise('human',reason='new plan')
        new=Action('human','assistant','prepare_draft','draft','effect-new','the new plan')
        self.issue('new-ticket',new, approved=False)
        self.assertFalse(self.fence.commit('ticket-1', self.action).committed)
        self.assertTrue(self.fence.commit('new-ticket', new).committed)

    def test_27_comparison_revoke(self): self.assertTrue(scenario('revoke')['safety_property_pass'])
    def test_28_comparison_change_intent(self): self.assertTrue(scenario('change_intent')['safety_property_pass'])
    def test_29_comparison_expiry(self): self.assertTrue(scenario('expiry')['safety_property_pass'])
    def test_30_comparison_payload(self): self.assertTrue(scenario('payload_substitution')['safety_property_pass'])
    def test_31_comparison_recipient(self): self.assertTrue(scenario('recipient_substitution')['safety_property_pass'])
    def test_32_comparison_agent(self): self.assertTrue(scenario('agent_substitution')['safety_property_pass'])
    def test_33_inflight_revocation_before_commit(self):
        self.issue()
        released = threading.Event()
        continue_commit = threading.Event()
        result = []
        def worker():
            result.append(('predispatch', self.fence.precheck('ticket-1', self.action)))
            released.set()
            if not continue_commit.wait(10):
                raise RuntimeError('event timed out')
            result.append(('final', self.fence.commit('ticket-1', self.action).reason))
        thread = threading.Thread(target=worker)
        thread.start()
        try:
            self.assertTrue(released.wait(10))
            self.fence.revoke('human','ticket-1')
        finally:
            continue_commit.set()
            thread.join(timeout=10)
        self.assertEqual(result, [('predispatch','allowed'),('final','revoked')])
        self.assertEqual(self.fence.effect_count(),0)

    def test_34_inflight_revision_before_commit(self):
        self.issue()
        released = threading.Event()
        continue_commit = threading.Event()
        result = []
        def worker():
            result.append(self.fence.precheck('ticket-1', self.action))
            released.set()
            if not continue_commit.wait(10):
                raise RuntimeError('event timed out')
            result.append(self.fence.commit('ticket-1', self.action).reason)
        thread = threading.Thread(target=worker)
        thread.start()
        try:
            self.assertTrue(released.wait(10))
            self.fence.revise('human', reason='Cancel original goal')
        finally:
            continue_commit.set()
            thread.join(timeout=10)
        self.assertEqual(result,['allowed','stale_intent'])
        self.assertEqual(self.fence.effect_count(),0)

    def test_35_unanchored_audit_suffix_truncation_not_detected(self):
        # Deliberately demonstrates a LIMITATION: a shorter valid prefix
        # cannot be detected without an externally anchored expected head.
        self.issue()
        with closing(self.fence.connect()) as cx:
            cx.execute("DELETE FROM audit WHERE seq=(SELECT MAX(seq) FROM audit)")
        self.assertTrue(self.fence.audit_ok())

    def test_36_authorized_but_unwise_action_not_safety_screened(self):
        # Deliberately demonstrates a GAP: authorization != harmlessness.
        a=Action('human','assistant','send_email','r@example.test',
                 'unwise','hypothetical inappropriate content')
        self.issue('unwise-ticket',a,approved=True)
        self.assertTrue(self.fence.commit('unwise-ticket',a).committed)

    def test_37_before_after_boundary(self):
        cases=before_and_after_examples()
        self.assertTrue(cases[0]['committed'])
        self.assertFalse(cases[1]['committed'])
        self.assertTrue(cases[2]['committed'])
        self.assertEqual(cases[3]['count'],2)


if __name__=='__main__': unittest.main()
