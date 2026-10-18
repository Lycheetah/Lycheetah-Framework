import copy
import json
import os
from pathlib import Path
import sqlite3
import subprocess
import sys
import tempfile
import threading
import unittest
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
from multiprocessing import get_context
from upstream_dispatch_fence import _ClosingConnection

from lab_fixture import ACTION, authority,provider,setup_effect
from crashsafe_authority import SimulatedIdempotentProvider

HERE=Path(__file__).resolve().parent

def race_worker(args):
    db,which,effect_id,action=args
    f=authority(db)
    if which=='challenge':
        b=f.challenge_body('crm','nonce-'+effect_id)
        return {'type':'challenge','allowed':f.challenge(b,f.sign_challenge(b))}
    w=f.witness(effect_id)
    return {'type':'reserve','allowed':bool(w and f.reserve_send(effect_id,action,w,50).allowed)}

class AuthorityTests(unittest.TestCase):
    def setUp(self):
        self.t=tempfile.TemporaryDirectory()
        self.addCleanup(self.t.cleanup)
        self.db=str(Path(self.t.name)/'auth.db')
        self.providerdb=str(Path(self.t.name)/'provider.db')
        self.f=authority(self.db)
        self.p=provider(self.providerdb)
        self.w=setup_effect(self.f)

    def worker(self,mode,eid='effect-001'):
        return subprocess.run([sys.executable,str(HERE/'crash_worker.py'),self.db,self.providerdb,mode,eid],cwd=HERE,capture_output=True,text=True,timeout=20)

    def test_happy_path(self):
        r=self.f.reserve_send('effect-001',ACTION,self.w,50)
        self.assertTrue(r.allowed);self.assertEqual(r.state,'SENDING')
        res=self.p.apply('effect-001',ACTION)
        self.assertTrue(self.f.acknowledge('effect-001',res))
        self.assertEqual(self.f.state_pair('effect-001')['outbox']['state'],'ACKED')
        self.assertEqual(self.p.count(),1)
    def test_double_enqueue(self): self.assertFalse(self.f.enqueue('effect-001'))
    def test_replay_reservation_refused(self):
        self.assertTrue(self.f.reserve_send('effect-001',ACTION,self.w,50).allowed)
        self.assertFalse(self.f.reserve_send('effect-001',ACTION,self.w,50).allowed)
        self.assertEqual(self.f.state_pair('effect-001')['outbox']['attempt'],1)
    def test_challenge_prevents_reserve(self):
        b=self.f.challenge_body('crm','nc1')
        self.assertTrue(self.f.challenge(b,self.f.sign_challenge(b)))
        self.assertFalse(self.f.reserve_send('effect-001',ACTION,self.w,50).allowed)
        self.assertEqual(self.f.state_pair('effect-001')['outbox']['state'],'PENDING')
    def test_fresh_witness_does_not_override_open_challenge(self):
        b=self.f.challenge_body('crm','nc1');self.assertTrue(self.f.challenge(b,self.f.sign_challenge(b)))
        w=self.f.witness('effect-001')
        self.assertEqual(self.f.reserve_send('effect-001',ACTION,w,50).reason,'source-challenged')
    def test_unrelated_challenge_invalidates_cached_witness(self):
        b=self.f.challenge_body('merchant','nc1');self.assertTrue(self.f.challenge(b,self.f.sign_challenge(b)))
        self.assertFalse(self.f.reserve_send('effect-001',ACTION,self.w,50).allowed)
        self.assertTrue(self.f.reserve_send('effect-001',ACTION,self.f.witness('effect-001'),50).allowed)
    def test_revocation(self):
        self.f.revoke('agent')
        self.assertFalse(self.f.reserve_send('effect-001',ACTION,self.f.witness('effect-001'),50).allowed)
    def test_expiry(self): self.assertEqual(self.f.reserve_send('effect-001',ACTION,self.w,10000).reason,'approval-invalid')
    def test_evidence_changed(self):
        self.f.update_evidence('eligibility',2,'FAIL',ACTION['subject'])
        self.assertFalse(self.f.reserve_send('effect-001',ACTION,self.w,50).allowed)
    def test_subject_changed(self):
        bad=dict(ACTION,subject='customer-999')
        self.assertEqual(self.f.reserve_send('effect-001',bad,self.w,50).reason,'action-substitution')
    def test_witness_seal_wrong(self):
        w=copy.deepcopy(self.w);w['seal']='0'*64
        self.assertEqual(self.f.reserve_send('effect-001',ACTION,w,50).reason,'bad-witness-seal')
    def test_unknown_effect_not_queued(self):
        self.assertFalse(self.f.enqueue('nonexistent'))
    def test_multiple_authority_instances_share_outbox(self):
        self.assertFalse(authority(self.db).enqueue('effect-001'))
        self.assertTrue(authority(self.db).reserve_send('effect-001',ACTION,self.w,50).allowed)
    def test_recover_no_pending_sends(self): self.assertEqual(self.f.recover(),0)
    def test_recover_sending_as_unknown(self):
        self.f.reserve_send('effect-001',ACTION,self.w,50)
        self.assertEqual(self.f.recover(),1)
        state=self.f.state_pair('effect-001')
        self.assertEqual((state['effect'],state['outbox']['state']),('UNKNOWN','UNKNOWN'))
        self.assertEqual(self.f.recover(),0)
        self.assertFalse(self.f.reserve_send('effect-001',ACTION,self.w,50).allowed)
    def test_absence_at_provider_does_not_establish_safe_retry(self):
        self.f.reserve_send('effect-001',ACTION,self.w,50);self.f.recover()
        self.assertIsNone(self.p.lookup('effect-001'))
        self.assertEqual(self.f.state_pair('effect-001')['outbox']['state'],'UNKNOWN')
    def test_reconcile_after_unknown(self):
        self.f.reserve_send('effect-001',ACTION,self.w,50)
        self.p.apply('effect-001',ACTION)
        self.f.recover()
        self.assertTrue(self.f.acknowledge('effect-001',self.p.lookup('effect-001')))
        self.assertEqual(self.f.state_pair('effect-001')['effect'],'SUCCEEDED')
    def test_reconcile_without_evidence_refused(self):
        self.f.reserve_send('effect-001',ACTION,self.w,50);self.f.recover()
        self.assertFalse(self.f.acknowledge('effect-001',{}))
    def test_reconcile_mismatched_effect_refused(self):
        self.f.reserve_send('effect-001',ACTION,self.w,50);self.f.recover()
        self.assertFalse(self.f.acknowledge('effect-001',{'effect_id':'different','outcome':'SUCCEEDED'}))
    def test_provider_idempotence(self):
        self.assertTrue(self.p.apply('effect-001',ACTION)['created'])
        self.assertFalse(self.p.apply('effect-001',ACTION)['created'])
        self.assertEqual(self.p.count(),1)
    def test_provider_reused_key_changed_action(self):
        self.p.apply('effect-001',ACTION)
        self.assertEqual(self.p.apply('effect-001',dict(ACTION,refund_cents=2000))['outcome'],'REJECTED_MISMATCH')
        self.assertEqual(self.p.count(),1)
    def test_unsigned_success_receipt_rejected(self):
        self.f.reserve_send('effect-001',ACTION,self.w,50)
        self.assertFalse(self.f.acknowledge('effect-001',{'effect_id':'effect-001','outcome':'SUCCEEDED','action_hash':'a'*64}))
    def test_tampered_signed_receipt_rejected(self):
        self.f.reserve_send('effect-001',ACTION,self.w,50)
        receipt=self.p.apply('effect-001',ACTION)
        receipt['outcome']='FAILED'
        self.assertFalse(self.f.acknowledge('effect-001',receipt))
    def test_mismatched_signed_action_receipt_rejected(self):
        from lab_fixture import K_P
        from upstream_dispatch_fence import mac
        self.f.reserve_send('effect-001',ACTION,self.w,50)
        body={'effect_id':'effect-001','outcome':'SUCCEEDED','action_hash':'a'*64}
        receipt={**body,'signature':mac(K_P,body)}
        self.assertFalse(self.f.acknowledge('effect-001',receipt))
    def test_wrong_provider_signing_key_rejected(self):
        from upstream_dispatch_fence import mac
        self.f.reserve_send('effect-001',ACTION,self.w,50)
        receipt=self.p.apply('effect-001',ACTION)
        body={k:receipt[k] for k in ('effect_id','outcome','action_hash')}
        receipt['signature']=mac(b'Z'*32,body)
        self.assertFalse(self.f.acknowledge('effect-001',receipt))
    def test_ack_duplicate_refused(self):
        self.f.reserve_send('effect-001',ACTION,self.w,50)
        r=self.p.apply('effect-001',ACTION)
        self.assertTrue(self.f.acknowledge('effect-001',r))
        self.assertFalse(self.f.acknowledge('effect-001',r))
    def test_replay_by_rewriting_materialized_state_is_detected(self):
        self.assertTrue(self.f.reserve_send('effect-001',ACTION,self.w,50).allowed)
        with sqlite3.connect(self.db,factory=_ClosingConnection) as c:
            c.execute("UPDATE outbox SET state='PENDING',attempt=0,reserve_audit_seq=NULL WHERE effect_id='effect-001'")
            c.execute("UPDATE effects SET status='PREPARED',dispatch_seq=NULL WHERE effect_id='effect-001'")
        self.assertTrue(self.f.verify_audit())
        self.assertFalse(self.f.verify_state_consistency())
        self.assertEqual(self.f.reserve_send('effect-001',ACTION,self.w,50).reason,'state-inconsistent')
    def test_forged_ack_by_editing_materialized_state_is_detected(self):
        self.assertTrue(self.f.reserve_send('effect-001',ACTION,self.w,50).allowed)
        with sqlite3.connect(self.db,factory=_ClosingConnection) as c:
            c.execute("UPDATE outbox SET state='ACKED' WHERE effect_id='effect-001'")
            c.execute("UPDATE effects SET status='SUCCEEDED' WHERE effect_id='effect-001'")
        self.assertFalse(self.f.verify_state_consistency())
    def test_missing_outbox_row_after_enqueue_is_detected(self):
        with sqlite3.connect(self.db,factory=_ClosingConnection) as c:
            c.execute("DELETE FROM outbox WHERE effect_id='effect-001'")
        self.assertFalse(self.f.verify_state_consistency())
        self.assertFalse(self.f.enqueue('effect-001'))
    def test_corrupted_attempt_counter_detected(self):
        with sqlite3.connect(self.db,factory=_ClosingConnection) as c:
            c.execute("UPDATE outbox SET attempt=1 WHERE effect_id='effect-001'")
        self.assertFalse(self.f.verify_state_consistency())
        self.assertEqual(self.f.reserve_send('effect-001',ACTION,self.w,50).reason,'state-inconsistent')
    def test_audit_tampering_stops_reserve(self):
        with sqlite3.connect(self.db,factory=_ClosingConnection) as c: c.execute("UPDATE audit SET kind='FORGED' WHERE seq=1")
        self.assertEqual(self.f.reserve_send('effect-001',ACTION,self.w,50).reason,'audit-corrupted')
    def test_bad_actor_authority_cannot_pass(self):
        self.f.revoke('agent');self.assertFalse(self.f.reserve_send('effect-001',ACTION,self.w,50).allowed)
    def test_crash_after_reserve(self):
        p=self.worker('crash-after-reserve');self.assertEqual(p.returncode,90,p.stderr)
        f=authority(self.db);self.assertEqual(f.state_pair('effect-001')['outbox']['state'],'SENDING')
        self.assertEqual(f.recover(),1)
        self.assertEqual(f.state_pair('effect-001')['outbox']['state'],'UNKNOWN')
        self.assertIsNone(self.p.lookup('effect-001'))
    def test_crash_after_provider_commit(self):
        p=self.worker('crash-after-provider-commit');self.assertEqual(p.returncode,91,p.stderr)
        self.assertEqual(self.p.count(),1)
        f=authority(self.db);self.assertEqual(f.recover(),1)
        self.assertTrue(f.acknowledge('effect-001',self.p.lookup('effect-001')))
        self.assertEqual(self.p.count(),1)
    def test_crash_after_challenge_commit(self):
        p=self.worker('crash-after-challenge-commit');self.assertEqual(p.returncode,93,p.stderr)
        self.assertFalse(authority(self.db).reserve_send('effect-001',ACTION,self.w,50).allowed)
    def test_crash_mid_challenge_transaction_rolls_back(self):
        p=self.worker('crash-during-challenge-transaction');self.assertEqual(p.returncode,94,p.stderr)
        f=authority(self.db);self.assertTrue(f.verify_audit())
        self.assertTrue(f.reserve_send('effect-001',ACTION,self.w,50).allowed)
    def test_crash_recovery_not_silent_retry(self):
        p=self.worker('crash-after-provider-commit');self.assertEqual(p.returncode,91,p.stderr)
        f=authority(self.db);f.recover()
        self.assertFalse(f.reserve_send('effect-001',ACTION,self.w,50).allowed)
        self.assertEqual(self.p.count(),1)
    def test_challenge_after_reservation_not_retroactive(self):
        self.assertTrue(self.f.reserve_send('effect-001',ACTION,self.w,50).allowed)
        b=self.f.challenge_body('crm','nc-late');self.assertTrue(self.f.challenge(b,self.f.sign_challenge(b)))
        self.assertEqual(self.p.apply('effect-001',ACTION)['outcome'],'SUCCEEDED')
    def test_false_trusted_evidence_negative_control(self):
        # Eligibility was actually false; caller-signed PASS was trusted and passed.
        truth={'eligible':False}
        self.assertFalse(truth['eligible'])
        self.assertTrue(self.f.reserve_send('effect-001',ACTION,self.w,50).allowed)
        self.assertEqual(self.p.apply('effect-001',ACTION)['outcome'],'SUCCEEDED')
    def test_false_metadata_claim_no_automatic_truth_assurance(self):
        self.assertEqual(self.f.state_pair('effect-001')['outbox']['state'],'PENDING')
        self.assertIsNone(self.p.lookup('effect-001'))
    def test_concurrent_threads_single_reservation(self):
        with ThreadPoolExecutor(max_workers=8) as ex:
            outputs=list(ex.map(lambda _: self.f.reserve_send('effect-001',ACTION,self.w,50).allowed,range(16)))
        self.assertEqual(outputs.count(True),1)
        self.assertEqual(self.f.state_pair('effect-001')['outbox']['attempt'],1)
    def test_cross_process_single_reservation(self):
        jobs=[(self.db,'reserve','effect-001',ACTION)]*8
        with ProcessPoolExecutor(max_workers=8,mp_context=get_context('spawn')) as pool: r=list(pool.map(race_worker,jobs))
        self.assertEqual(sum(x['allowed'] for x in r),1)
    def test_cross_process_challenge_reservation_order(self):
        # Fixed ledger order per trial: a claim cannot follow an earlier committed challenge.
        for i in range(6):
            p=Path(self.t.name)/f'race_{i}.db';f=authority(str(p));w=setup_effect(f,effect_id='racefx')
            jobs=[(str(p),'reserve','racefx',ACTION),(str(p),'challenge','racefx',ACTION)]
            with ProcessPoolExecutor(max_workers=2,mp_context=get_context('spawn')) as pool: x=list(pool.map(race_worker,jobs))
            audit=f.audit_events()
            kind=[z['kind'] for z in audit]
            if 'SEND_RESERVED' in kind and 'CHALLENGE' in kind:
                self.assertLess(kind.index('SEND_RESERVED'),kind.index('CHALLENGE'))
            self.assertTrue(any(y['allowed'] for y in x))
    def test_outbox_mutation_can_be_detected_by_review(self):
        # Negative audit design limit: audit chain alone doesn't attest mutable outbox state.
        with sqlite3.connect(self.db,factory=_ClosingConnection) as c:
            c.execute("UPDATE outbox SET attempt=1 WHERE effect_id='effect-001'")
        self.assertTrue(self.f.verify_audit())
        self.assertFalse(self.f.verify_state_consistency())
        self.assertFalse(self.f.reserve_send('effect-001',ACTION,self.w,50).allowed)
    def test_source_graph_mismatch_rejected(self):
        from lab_fixture import K_A,K_C,K_F,K_P,REVIEWERS
        from crashsafe_authority import CrashSafeAuthority
        with self.assertRaises(ValueError):
            CrashSafeAuthority(self.db,provider_receipt_key=K_P,approval_key=K_A,auditor_key=K_C,
                reviewer_keys=REVIEWERS,fence_key=K_F,source_parents={'crm':(),'merchant':()})
    def test_completed_provider_result_state_consistent(self):
        self.f.reserve_send('effect-001',ACTION,self.w,50)
        self.f.acknowledge('effect-001',self.p.apply('effect-001',ACTION))
        self.assertTrue(self.f.verify_audit())
        self.assertEqual(self.f.state_pair('effect-001')['effect'],'SUCCEEDED')

if __name__=='__main__': unittest.main()
