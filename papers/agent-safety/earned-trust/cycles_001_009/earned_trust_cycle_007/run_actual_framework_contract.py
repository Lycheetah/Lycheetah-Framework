"""Real-code import-required tests for a pinned Lycheetah-Framework checkout.

No fake fallback. If `lycheetah` is missing, prints NOT EXECUTED and exits 4.
This suite tests each REAL framework class in a sequential handoff, NOT an
atomic joint transaction or a completed C007 integration.
"""
from __future__ import annotations
import tempfile
import unittest
from pathlib import Path

try:
    from lycheetah.assurance.models import AssuranceEvent, Phase, Disposition
    from lycheetah.assurance.policy import AssurancePolicy
    from lycheetah.assurance.runtime import AssuranceRuntime
    from lycheetah.assurance.finality import FinalityGate, MappingEvidenceStore, EvidenceRecord, EvidenceRequirement
    from lycheetah.assurance.action_guard import PersistentActionGuard
except (ModuleNotFoundError, ImportError) as exc:
    if __name__ == '__main__':
        print('NOT EXECUTED — requires the real Lycheetah-Framework package:',exc)
        raise SystemExit(4)
    raise

ACTION={'tool':'refund.create','subject':'fictional-001','amount_cents':1250}

class ActualFrameworkSequentialContract(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
        self.policy=AssurancePolicy(policy_id='earnedtrust.c007',version='0.1.0',
                            tool_allowlist=('refund.create',),require_approval_for_side_effects=True)
        self.event=AssuranceEvent(phase=Phase.TOOL,tool_name='refund.create',tool_arguments=ACTION,
                                 scopes=('refund:create',),side_effect=True,human_approved=True,
                                 event_id='C007-E1',trace_id='C007-T1')
        self.store=MappingEvidenceStore([EvidenceRecord('eligibility','1','fictional-001','digest-1','PASS')])
        self.gate=FinalityGate(AssuranceRuntime(self.policy),self.store)
        self.guard=PersistentActionGuard(Path(self.tmp.name)/'guard.sqlite')
        self.admission=self.gate.admit(self.event,[EvidenceRequirement('eligibility',required_subject_hash='fictional-001')])
        self.assertEqual(self.admission.disposition,Disposition.ALLOW)
        self.assertIsNotNone(self.admission.witness)
        self.assertTrue(self.guard.issue_approval('approval-1','agent','fixture-human',ACTION,'refund:create',100,200).allowed)
        self.assertTrue(self.guard.prepare_effect('effect-1','approval-1','agent',ACTION,'refund:create',110).allowed)

    def test_real_finality_detects_changed_status(self):
        self.store.put(EvidenceRecord('eligibility','2','fictional-001','digest-2','FAIL'))
        d=self.gate.finalize(self.admission.witness,self.event)
        self.assertFalse(d.ready)
        self.assertEqual(d.disposition,Disposition.REVIEW)
        self.assertEqual(self.guard.get_effect('effect-1')['status'],'PREPARED')

    def test_real_guard_catches_revocation_after_finality(self):
        d=self.gate.finalize(self.admission.witness,self.event)
        self.assertTrue(d.ready)
        self.guard.revoke_all('agent',114)
        # No change to finality's external evidence; real Action Guard must still
        # reject the now-revoked approval at its own claim boundary.
        claimed=self.guard.claim_dispatch('effect-1',115,ACTION,expected_audit_anchor=self.guard.audit_anchor())
        self.assertFalse(claimed.allowed)
        self.assertEqual(self.guard.get_effect('effect-1')['status'],'CANCELLED')

    def test_real_guard_single_use_claim(self):
        self.assertTrue(self.gate.finalize(self.admission.witness,self.event).ready)
        first=self.guard.claim_dispatch('effect-1',115,ACTION,expected_audit_anchor=self.guard.audit_anchor())
        self.assertTrue(first.allowed)
        second=self.guard.claim_dispatch('effect-1',116,ACTION,expected_audit_anchor=self.guard.audit_anchor())
        self.assertFalse(second.allowed)
        self.assertEqual(self.guard.get_effect('effect-1')['status'],'DISPATCHING')

    def test_real_finality_does_not_reverse_claimed_dispatch(self):
        first=self.guard.claim_dispatch('effect-1',115,ACTION,expected_audit_anchor=self.guard.audit_anchor())
        self.assertTrue(first.allowed)
        self.store.put(EvidenceRecord('eligibility','2','fictional-001','digest-2','FAIL'))
        self.assertFalse(self.gate.finalize(self.admission.witness,self.event).ready)
        self.assertEqual(self.guard.get_effect('effect-1')['status'],'DISPATCHING')

if __name__=='__main__':unittest.main()
