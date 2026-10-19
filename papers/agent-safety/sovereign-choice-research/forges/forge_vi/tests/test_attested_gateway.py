"""Synthetic local security-contract tests. Not evidence of real human consent."""
from __future__ import annotations
import base64
import copy
import secrets
import tempfile
import threading
import unittest
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[
 str(ROOT/'code'),
 str(ROOT.parent/'sovereign_choice_forge_v'),
 str(ROOT/'upstream_mirror'/'papers'/'agent-safety'/'frontier-controls'/'01_commit_time_authority_v0_7'),
 str(ROOT/'upstream_mirror'/'papers'/'agent-safety'/'frontier-controls'),
]
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from attested_gateway import AttestedChoiceGateway, SCHEMA, canonical_json
from research_support import Action

NOW=1792290000

class GatewayTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.db=Path(self.tmp.name)/'choice.sqlite'
        self.secret=Ed25519PrivateKey.generate()   # Test fixture ONLY. The production signer MUST be isolated.
        self.alien=Ed25519PrivateKey.generate()
        self.clock=[NOW]
        self.keys={'alice-key':('alice',self.secret.public_key())}
        self.g=AttestedChoiceGateway(self.db,self.keys,clock=lambda:self.clock[0])
        self.a=self.action()

    def action(self, principal='alice',tool='email.send',destination='trusted@example.org',args=None,effect_id='effect-1'):
        return Action(principal=principal,tool=tool,operation='send',object_id='message-1',
                      destination=destination,arguments=args or {'subject':'Test', 'body':'Hi'},effect_id=effect_id)
    def message(self,kind='APPROVE',version=0,action=None, principal='alice', scope='email.send', nonce=None):
        action=self.a if action is None else action
        return {'schema':SCHEMA,'kind':kind,'key_id':'alice-key', 'principal':principal,
                'scope_key':scope,'expected_version':version,
                'nonce':nonce or secrets.token_hex(16),'issued_at':self.clock[0],
                'expires_at':self.clock[0]+120,
                'purpose':'Send this approved message' if kind=='APPROVE' else '',
                'action_hash':action.action_hash if kind=='APPROVE' else ''}
    def sign(self,m,secret=None):
        return base64.b64encode((secret or self.secret).sign(canonical_json(m))).decode('ascii')
    def approve(self,action=None, version=0):
        a=action or self.a
        m=self.message(version=version,action=a)
        return self.g.submit(m,self.sign(m),a)
    def withdraw(self, version=1):
        m=self.message(kind='WITHDRAW',version=version)
        return self.g.submit(m,self.sign(m))

    def test_unsigned_action_denied(self):
        self.assertEqual(self.g.dispatch(self.a).reason,'no_signed_approval')
    def test_valid_signature_approval_dispatch(self):
        self.assertTrue(self.approve().accepted)
        r=self.g.dispatch(self.a)
        self.assertTrue(r.accepted); self.assertEqual(r.effect_state,'COMMITTED')
        self.assertEqual(self.g._fence.effect_count(),1)
    def test_wrong_signer_cannot_approve(self):
        m=self.message()
        with self.assertRaisesRegex(ValueError,'invalid_signature'):
            self.g.submit(m,self.sign(m,self.alien),self.a)
        self.assertEqual(self.g._fence.effect_count(),0)
    def test_tampered_message_rejected(self):
        m=self.message(); sig=self.sign(m)
        m['purpose']='Please send extra copies'
        with self.assertRaisesRegex(ValueError,'invalid_signature'): self.g.submit(m,sig,self.a)
    def test_wrong_action_rejected(self):
        m=self.message(); b=self.action(destination='wrong@example.org')
        self.assertEqual(self.g.submit(m,self.sign(m),b).reason,'signed_action_mismatch')
    def test_modified_body_after_approval_denied(self):
        self.approve()
        b=self.action(args={'subject':'Test', 'body':'Different'})
        self.assertEqual(self.g.dispatch(b).reason,'action_not_endorsed')
        self.assertTrue(self.g.dispatch(self.a).accepted)
    def test_replay_signature_rejected(self):
        m=self.message();sig=self.sign(m)
        self.assertTrue(self.g.submit(m,sig,self.a).accepted)
        self.assertFalse(self.g.submit(m,sig,self.a).accepted)
    def test_signed_withdrawal_prevents_action(self):
        self.approve(); self.assertTrue(self.withdraw().accepted)
        self.assertFalse(self.g.dispatch(self.a).accepted)
        self.assertEqual(self.g._fence.effect_count(),0)
    def test_old_signature_cannot_regrant(self):
        m=self.message();sig=self.sign(m)
        self.g.submit(m,sig,self.a); self.withdraw()
        self.assertFalse(self.g.submit(m,sig,self.a).accepted)
    def test_revision_blocks_old_action_new_allowed(self):
        self.approve()
        new=self.action(args={'subject':'New','body':'Just a draft'},effect_id='effect-new')
        self.assertTrue(self.approve(new,version=1).accepted)
        self.assertFalse(self.g.dispatch(self.a).accepted)
        self.assertTrue(self.g.dispatch(new).accepted)
    def test_expired_submission_denied(self):
        m=self.message();sig=self.sign(m);self.clock[0]+=130
        with self.assertRaisesRegex(ValueError,'approval_not_in_valid_time_window'):
            self.g.submit(m,sig,self.a)
    def test_expired_dispatch_denied(self):
        self.approve();self.clock[0]+=130
        self.assertEqual(self.g.dispatch(self.a).reason,'approval_expired')
    def test_signed_approval_not_issued_in_future(self):
        m=self.message();m['issued_at']+=40;m['expires_at']+=40
        with self.assertRaisesRegex(ValueError,'approval_not_in_valid_time_window'):
            self.g.submit(m,self.sign(m),self.a)
    def test_noncanonical_fields_rejected(self):
        m=self.message();m['surprise']='admin'
        with self.assertRaisesRegex(ValueError,'invalid_message_fields'): self.g.submit(m,self.sign(m),self.a)
    def test_principal_swap_rejected(self):
        m=self.message(principal='bob')
        with self.assertRaisesRegex(ValueError,'unrecognised_principal_key'):
            self.g.submit(m,self.sign(m),self.a)
    def test_action_wrong_principal_rejected(self):
        m=self.message()
        with self.assertRaises(ValueError): self.g.submit(m,self.sign(m),self.action(principal='bob'))
    def test_scope_mismatch_rejected(self):
        m=self.message(scope='payment.send')
        with self.assertRaises(ValueError):self.g.submit(m,self.sign(m),self.a)
    def test_wrong_version_rejected(self):
        self.approve()
        m=self.message(version=0)
        self.assertEqual(self.g.submit(m,self.sign(m),self.a).reason,'stale_expected_version')
    def test_rollback_choice_authority_and_signed_receipt(self):
        m=self.message()
        with self.assertRaisesRegex(RuntimeError,'simulated_precommit_failure'):
            self.g.submit(m,self.sign(m),self.a,inject_failure=True)
        self.assertIsNone(self.g._ledger.current('alice','email.send'))
        self.assertIsNone(self.g._fence.state('alice','email.send'))
        self.assertEqual(len(self.g.records()),0)
        self.assertTrue(self.g.submit(m,self.sign(m),self.a).accepted)
    def test_out_of_band_authority_change_fail_closed(self):
        self.approve();self.g._fence.revoke('alice','email.send')
        m=self.message(version=1)
        self.assertEqual(self.g.submit(m,self.sign(m),self.a).reason,'out_of_band_authority_change')
        self.assertFalse(self.g.dispatch(self.a).accepted)
    def test_replay_after_restart(self):
        m=self.message();sig=self.sign(m);self.g.submit(m,sig,self.a)
        restarted=AttestedChoiceGateway(self.db,self.keys,clock=lambda:self.clock[0])
        self.assertFalse(restarted.submit(m,sig,self.a).accepted)
    def test_two_concurrent_approvals_exactly_one_wins(self):
        m1=self.message(); m2=self.message(); results=[]; lock=threading.Lock()
        def run(m):
            r=self.g.submit(m,self.sign(m),self.a)
            with lock: results.append(r.accepted)
        t1=threading.Thread(target=run,args=(m1,));t2=threading.Thread(target=run,args=(m2,))
        t1.start();t2.start();t1.join();t2.join()
        self.assertEqual(sorted(results),[False,True])
        self.assertEqual(len(self.g.records()),1)
    def test_local_commit_revoke_ordering(self):
        self.approve()
        v=self.g._ledger.issue('alice','email.send',self.a)
        self.assertTrue(v.allowed)
        self.withdraw()
        result=self.g._ledger.commit(v.handle,self.a)
        self.assertEqual(result.state,'DENY')
        self.assertEqual(self.g._fence.effect_count(),0)
    def test_finality_guard_blocks_expiry_between_check_and_commit(self):
        self.approve()
        original=self.g._ledger.issue
        def issue_and_elapse(principal,scope,action):
            result=original(principal,scope,action)
            self.clock[0]+=200
            return result
        self.g._ledger.issue=issue_and_elapse
        self.assertEqual(self.g.dispatch(self.a).reason,'attestation_invalid_at_finality')
        self.assertEqual(self.g._fence.effect_count(),0)

    def test_negative_control_without_finality_guard_allows_expired(self):
        weak = AttestedChoiceGateway(Path(self.tmp.name)/'weak.sqlite',self.keys,
                                     clock=lambda:self.clock[0],enforce_finality_guard=False)
        m=self.message()
        self.assertTrue(weak.submit(m,self.sign(m),self.a).accepted)
        original=weak._ledger.issue
        def issue_and_elapse(principal,scope,action):
            result=original(principal,scope,action)
            self.clock[0]+=200
            return result
        weak._ledger.issue=issue_and_elapse
        self.assertTrue(weak.dispatch(self.a).accepted)
        self.assertEqual(weak._fence.effect_count(),1)

    def test_complete_effect_not_undone(self):
        self.approve();self.assertTrue(self.g.dispatch(self.a).accepted)
        self.withdraw();self.assertFalse(self.g.dispatch(self.a).accepted)
        self.assertEqual(self.g._fence.effect_count(),1)
    def test_raw_fence_bypass_now_blocked_by_finality_trigger(self):
        self.g._fence.activate('alice','email.send')
        h,_=self.g._fence.issue_handle('alice','email.send',self.a)
        with self.assertRaisesRegex(Exception,'attestation_invalid_at_finality'):
            self.g._fence.commit(h.handle_id,self.a)
        self.assertEqual(self.g._fence.effect_count(),0)

    def test_negative_control_privileged_database_can_remove_guard(self):
        # An attacker with trusted DB DDL privileges can disable the trigger.
        with self.g._fence.connect() as con:
            con.execute('DROP TRIGGER attested_effect_finality_guard')
        self.g._fence.activate('alice','email.send')
        h,_=self.g._fence.issue_handle('alice','email.send',self.a)
        self.assertEqual(self.g._fence.commit(h.handle_id,self.a).state,'COMMITTED')
        self.assertEqual(self.g._fence.effect_count(),1)

    def test_signed_but_uninformed_is_not_detected(self):
        # An 'unread' signature is indistinguishable to the code: social consent is separate.
        m=self.message();m['purpose']='Person signed without reading an opaque dialog'
        self.assertTrue(self.g.submit(m,self.sign(m),self.a).accepted)
        self.assertEqual(len(self.g.records()),1)

if __name__=='__main__':unittest.main()
