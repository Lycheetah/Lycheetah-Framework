"""Original, local deterministic and concurrent tests. No live provider effects."""
import concurrent.futures
import json
import multiprocessing
import os
import sqlite3
import tempfile
import unittest
from pathlib import Path
from dispatch_fence import Fence

KEYS=dict(approval_key=b'H'*32,auditor_key=b'A'*32,
          reviewer_keys={'north':('north-org',b'N'*32),'south':('south-org',b'S'*32),
                         'north-alt':('north-org',b'Z'*32)},fence_key=b'F'*32,
          source_parents={'origin-crm':(), 'witness-1':('origin-crm',),
                          'witness-2':('origin-crm',), 'unrelated-root':()})
ACTION={'tool':'refund.create','subject':'fictitious-001','amount_cents':1250}

def seed(f):
    f.update_evidence('refund-eligibility',1,'PASS','fictitious-001')
    body=f.approval_body('approval-1','agent-1',ACTION,'refund:create',200)
    assert f.approve(body,f.sign_approval(body))
    assert f.prepare('effect-1','approval-1',ACTION,'refund:create',
                     ['origin-crm','witness-1','witness-2'],{'refund-eligibility':1})
    return f.witness('effect-1')

def process_worker(path, start, queue):
    f=Fence(path,**KEYS)
    start.wait(10)
    w=f.witness('effect-1')
    if w is None:
        queue.put('not_prepared')
    else:
        queue.put(f.claim('effect-1',ACTION,w,120).reason)


class FenceTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.path=Path(self.temp.name)/'fence.sqlite'
        self.f=Fence(self.path,**KEYS)
        self.w=seed(self.f)

    def claim(self, w=None, action=ACTION, now=120):
        return self.f.claim('effect-1',action,self.w if w is None else w,now)

    def challenge(self,source='origin-crm',nonce='challenge-1'):
        b=self.f.challenge_body(source,nonce)
        return self.f.challenge(b,self.f.sign_challenge(b))

    def test_happy_path(self):
        result=self.claim();self.assertTrue(result.allowed)
        self.assertEqual(result.state,'DISPATCHING')
        self.assertTrue(self.f.result('effect-1','SUCCEEDED',{'provider':'local-sim'}))
        self.assertEqual(self.f.state('effect-1')['status'],'SUCCEEDED')

    def test_admission_snapshot_stale_after_challenge(self):
        self.assertTrue(self.challenge())
        d=self.claim()
        self.assertFalse(d.allowed)
        self.assertEqual(d.reason,'stale-governance')
        self.assertEqual(self.f.state('effect-1')['status'],'PREPARED')

    def test_even_refreshed_snapshot_cannot_pass_challenge(self):
        self.challenge()
        new=self.f.witness('effect-1')
        self.assertEqual(self.claim(new).reason,'source-challenged')

    def test_unrelated_challenge_stales_cached_witness_conservatively(self):
        self.challenge('unrelated-root')
        self.assertEqual(self.claim().reason,'stale-governance')
        self.assertTrue(self.claim(self.f.witness('effect-1')).allowed)

    def test_bad_challenge_signature_is_not_applied(self):
        b=self.f.challenge_body('origin-crm','fail-sig')
        self.assertFalse(self.f.challenge(b,'0'*64))
        self.assertTrue(self.claim().allowed)

    def test_challenge_replay_refused(self):
        self.assertTrue(self.challenge());self.assertFalse(self.challenge())

    def test_approval_revoked_before_claim(self):
        self.f.revoke('agent-1')
        self.assertEqual(self.claim().reason,'revoked')

    def test_reissue_of_snapshot_cannot_override_revocation(self):
        self.f.revoke('agent-1')
        self.assertEqual(self.claim(self.f.witness('effect-1')).reason,'approval-invalid')

    def test_expiry(self):
        self.assertEqual(self.claim(now=200).reason,'approval-invalid')

    def test_event_action_substitution(self):
        altered={**ACTION,'amount_cents':12500}
        self.assertEqual(self.claim(action=altered).reason,'action-substitution')

    def test_tampered_witness(self):
        w={'body':dict(self.w['body']),'seal':self.w['seal']}
        w['body']['action_hash']='0'*64
        self.assertEqual(self.claim(w).reason,'bad-witness-seal')

    def test_other_effect_witness_mismatch(self):
        w={'body':dict(self.w['body']),'seal':self.w['seal']}
        w['body']['effect_id']='other'
        self.assertEqual(self.claim(w).reason,'bad-witness-seal')

    def test_evidence_status_invalidation(self):
        self.f.update_evidence('refund-eligibility',2,'FAIL','fictitious-001')
        self.assertEqual(self.claim().reason,'evidence-stale')
        self.assertEqual(self.claim(self.f.witness('effect-1')).reason,'evidence-stale')

    def test_evidence_revision_update_pass_still_blocks_old_requirement(self):
        self.f.update_evidence('refund-eligibility',2,'PASS','fictitious-001')
        self.assertEqual(self.claim(self.f.witness('effect-1')).reason,'evidence-stale')

    def test_evidence_replay_revision_refused(self):
        self.assertFalse(self.f.update_evidence('refund-eligibility',1,'PASS','x'))

    def test_replay_after_dispatch_refused(self):
        self.assertTrue(self.claim().allowed)
        self.assertEqual(self.claim().reason,'effect-already-claimed')

    def test_challenge_after_dispatch_does_not_magic_rollback(self):
        self.assertTrue(self.claim().allowed)
        self.assertTrue(self.challenge())
        self.assertEqual(self.f.state('effect-1')['status'],'DISPATCHING')
        self.assertTrue(self.f.result('effect-1','UNKNOWN',{'note':'timeout'}))
        self.assertEqual(self.f.state('effect-1')['status'],'UNKNOWN')

    def test_unknown_must_not_retry_claim(self):
        self.assertTrue(self.claim().allowed)
        self.f.result('effect-1','UNKNOWN')
        self.assertEqual(self.claim().reason,'effect-already-claimed')

    def test_no_unclaimed_result(self):
        self.assertFalse(self.f.result('effect-1','SUCCEEDED'))

    def test_no_duplicate_approval(self):
        body=self.f.approval_body('approval-1','agent-1',ACTION,'refund:create',200)
        self.assertFalse(self.f.approve(body,self.f.sign_approval(body)))

    def test_approval_signature_required(self):
        body=self.f.approval_body('approval-2','agent-1',ACTION,'refund:create',200)
        self.assertFalse(self.f.approve(body,'0'*64))

    def test_approval_one_time_effect(self):
        self.assertFalse(self.f.prepare('effect-2','approval-1',ACTION,'refund:create',
                                        ['origin-crm'],{'refund-eligibility':1}))

    def test_resolution_needs_distinct_organizations(self):
        self.challenge()
        b=self.f.resolution_body('origin-crm','resolve-1')
        self.assertFalse(self.f.resolve(b,[self.f.sign_resolution(b,'north'),self.f.sign_resolution(b,'north-alt')]))
        self.assertTrue(self.f.resolve(b,[self.f.sign_resolution(b,'north'),self.f.sign_resolution(b,'south')]))
        self.assertEqual(self.claim().reason,'stale-governance')
        self.assertTrue(self.claim(self.f.witness('effect-1')).allowed)

    def test_resolution_wrong_secret(self):
        self.challenge()
        b=self.f.resolution_body('origin-crm','resolve-1')
        self.assertFalse(self.f.resolve(b,[self.f.sign_resolution(b,'north'),{'reviewer':'south','mac':'x'*64}]))

    def test_audit_validation(self):
        self.assertTrue(self.f.verify_audit())
        with sqlite3.connect(self.path) as c:
            c.execute("UPDATE audit SET detail='{}' WHERE kind='PREPARED'")
        c.close()
        self.assertFalse(self.f.verify_audit())

    def test_serialize_across_two_instances(self):
        f2=Fence(self.path,**KEYS)
        self.assertTrue(self.claim().allowed)
        self.assertEqual(f2.claim('effect-1',ACTION,self.w,120).reason,'effect-already-claimed')

    def test_concurrent_threads_single_claim(self):
        with concurrent.futures.ThreadPoolExecutor(max_workers=16) as ex:
            decisions=list(ex.map(lambda _:self.claim(),range(32)))
        self.assertEqual(sum(d.allowed for d in decisions),1)
        self.assertEqual(sum(d.reason=='effect-already-claimed' for d in decisions),31)

    def test_serialized_challenge_race(self):
        # Repeat each race on a fresh shared SQLite DB: either CHALLENGE first,
        # or CLAIM first. Never allow CLAIM if CHALLENGE is already in history.
        for run in range(20):
            with tempfile.TemporaryDirectory() as td:
                f=Fence(Path(td)/'race.sqlite',**KEYS)
                w=seed(f)
                def a():return f.claim('effect-1',ACTION,w,120)
                def b():
                    body=f.challenge_body('origin-crm','race-'+str(run))
                    return f.challenge(body,f.sign_challenge(body))
                with concurrent.futures.ThreadPoolExecutor(max_workers=2) as ex:
                    future_a=ex.submit(a);future_b=ex.submit(b)
                    decision=future_a.result();self.assertTrue(future_b.result())
                events=f.audit_events()
                dispatch=[e for e in events if e['kind']=='DISPATCH_CLAIMED']
                challenge=[e for e in events if e['kind']=='CHALLENGE']
                self.assertEqual(bool(dispatch),decision.allowed)
                if dispatch:self.assertLess(dispatch[0]['seq'],challenge[0]['seq'])
                self.assertTrue(f.verify_audit())

    def test_after_challenge_new_snapshot_still_frozen(self):
        self.challenge()
        self.assertEqual(self.claim(self.f.witness('effect-1')).reason,'source-challenged')

    def test_missing_effect(self):
        self.assertEqual(self.f.claim('other',ACTION,self.w,120).reason,'missing-effect')

    def test_missing_witness(self):
        self.assertEqual(self.f.claim('effect-1',ACTION,None,120).reason,'missing-witness')

    def test_all_stages_audited(self):
        self.claim();self.f.result('effect-1','SUCCEEDED')
        self.assertTrue(self.f.verify_audit())
        events=[r['kind'] for r in self.f.audit_events()]
        self.assertIn('PREPARED',events)
        self.assertIn('DISPATCH_CLAIMED',events)
        self.assertIn('RESULT',events)

    def test_process_contenders_one_winner(self):
        ctx=multiprocessing.get_context('spawn')
        start=ctx.Event();q=ctx.Queue();workers=[ctx.Process(target=process_worker,args=(self.path,start,q)) for _ in range(8)]
        for p in workers:p.start()
        start.set()
        outcomes=[q.get(timeout=25) for _ in workers]
        for p in workers:p.join(timeout=25);self.assertEqual(p.exitcode,0)
        self.assertEqual(outcomes.count('locally-dispatchable'),1)
        self.assertTrue(set(outcomes)<={'locally-dispatchable','effect-already-claimed','not_prepared'})
        self.assertTrue(self.f.verify_audit())

    def test_transitive_dependency_challenge(self):
        # Even if the caller lists only the witnesses, the configured graph
        # forces the original CRM into the dispatch dependencies.
        with tempfile.TemporaryDirectory() as td:
            f=Fence(Path(td)/'lineage.sqlite',**KEYS)
            f.update_evidence('eligibility',1,'PASS','fictitious-001')
            body=f.approval_body('approval','agent',ACTION,'refund:create',200)
            self.assertTrue(f.approve(body,f.sign_approval(body)))
            self.assertTrue(f.prepare('effect','approval',ACTION,'refund:create',
                                      ['witness-1','witness-2'],{'eligibility':1}))
            w=f.witness('effect')
            challenge=f.challenge_body('origin-crm','closure-1')
            self.assertTrue(f.challenge(challenge,f.sign_challenge(challenge)))
            self.assertEqual(f.claim('effect',ACTION,w,120).reason,'stale-governance')
            self.assertEqual(f.claim('effect',ACTION,f.witness('effect'),120).reason,'source-challenged')

    def test_unregistered_source_refused(self):
        self.assertFalse(self.f.prepare('another','approval-1',ACTION,'refund:create',
                                         ['not-known'],{'refund-eligibility':1}))

    def test_wrong_subject_evidence_refused_at_prepare(self):
        self.f.update_evidence('unrelated',1,'PASS','someone-else')
        self.assertFalse(self.f.prepare('another','approval-1',ACTION,'refund:create',
                                        ['witness-1'],{'unrelated':1}))

    def test_wrong_subject_evidence_refused_at_dispatch(self):
        self.f.update_evidence('refund-eligibility',2,'PASS','someone-else')
        self.assertEqual(self.claim(self.f.witness('effect-1')).reason,'evidence-stale')

    def test_challenge_nonexistent_source_refused(self):
        self.assertFalse(self.challenge('unknown-source'))

    def test_graph_change_on_reopen_refused(self):
        changed=dict(KEYS)
        changed['source_parents']={'origin-crm':(),'witness-1':(), 'witness-2':(), 'unrelated-root':()}
        with self.assertRaisesRegex(ValueError,'source graph differs'):
            Fence(self.path,**changed)

    def test_cyclic_graph_refused(self):
        changed=dict(KEYS)
        changed['source_parents']={'witness-1':('witness-2',),'witness-2':('witness-1',)}
        with self.assertRaisesRegex(ValueError,'cycle'):
            Fence(Path(self.temp.name)/'cyclic.sqlite',**changed)

    def test_tampered_audit_prevents_dispatch(self):
        with sqlite3.connect(self.path) as c:
            c.execute("UPDATE audit SET detail='{}' WHERE kind='PREPARED'")
        c.close()
        self.assertEqual(self.claim().reason,'audit-corrupted')

    def test_false_trusted_evidence_negative_control(self):
        # Intentionally wrong source assertion: every guard can pass, harm is
        # possible because this lab has no independent ground-truth sensor.
        self.assertTrue(self.claim().allowed)
        independent_truth=False
        self.assertFalse(independent_truth)


if __name__=='__main__':
    unittest.main()
