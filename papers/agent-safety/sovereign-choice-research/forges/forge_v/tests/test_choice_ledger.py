"""Forge V tests against the SHA-verified upstream CommitFence source copy."""
from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
from contextlib import closing
from pathlib import Path
import multiprocessing as mp
import os
import sqlite3
import sys
import tempfile
import threading
import unittest

ROOT=Path(__file__).resolve().parents[1]
SUPPORT=ROOT/'upstream_mirror/papers/agent-safety/frontier-controls'
FENCE_DIR=SUPPORT/'01_commit_time_authority_v0_7'
sys.path.insert(0,str(SUPPORT))
sys.path.insert(0,str(FENCE_DIR))
sys.path.insert(0,str(ROOT))
from research_support import Action
from commit_fence import CommitFence, PreDispatchOnlyBaseline
from choice_ledger import AtomicChoiceLedger


def action(subject='one', *, effect_id='fx1', recipient='customer@example.test',
           principal='alice', tool='email'):
    return Action(principal=principal,tool=tool,operation='send',
        object_id='draft-1', destination=recipient,arguments={'subject':subject},
        effect_id=effect_id)


def process_revise(db_path, idx, queue):
    try:
        fence=CommitFence(db_path)
        ledger=AtomicChoiceLedger(fence)
        x=ledger.grant('alice','email', f'revision-{idx}', action(str(idx),effect_id=f'fx{idx}'))
        queue.put(('ok',x.version,x.generation))
    except BaseException as e:
        queue.put(('error',str(e)))


class AtomicLedgerTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.db=Path(self.tmp.name)/'unified.sqlite'
        self.fence=CommitFence(self.db)
        self.ledger=AtomicChoiceLedger(self.fence)

    def test_exact_endorsed_action_commits(self):
        a=action()
        x=self.ledger.grant('alice','email','send exactly this',a)
        self.assertEqual((x.version,x.generation),(1,1))
        verdict=self.ledger.issue('alice','email',a)
        self.assertTrue(verdict.allowed)
        result=self.ledger.commit(verdict.handle,a)
        self.assertEqual(result.state,'COMMITTED')
        self.assertEqual(self.fence.effect_count(),1)

    def test_no_grant_denies(self):
        self.assertEqual(self.ledger.issue('alice','email',action()).reason,'no_active_endorsement')

    def test_revision_fences_previously_issued_action(self):
        a=action(); b=action('revised',effect_id='fx2')
        self.ledger.grant('alice','email','original',a)
        handle=self.ledger.issue('alice','email',a).handle
        changed=self.ledger.grant('alice','email','revised',b)
        self.assertEqual((changed.version,changed.generation),(2,2))
        self.assertEqual(self.ledger.commit(handle,a).state,'DENY')
        self.assertFalse(self.ledger.issue('alice','email',a).allowed)
        self.assertEqual(self.ledger.commit(self.ledger.issue('alice','email',b).handle,b).state,'COMMITTED')

    def test_withdraw_no_reason_and_no_new_effect(self):
        a=action()
        self.ledger.grant('alice','email','original',a)
        h=self.ledger.issue('alice','email',a).handle
        x=self.ledger.withdraw('alice','email')
        self.assertFalse(x.active)
        self.assertEqual(x.version,2)
        self.assertEqual(self.ledger.commit(h,a).state,'DENY')
        self.assertEqual(self.fence.effect_count(),0)
        self.assertEqual(self.ledger.events()[-1]['reason_class'],'not_required')

    def test_regrant_after_withdraw_requires_new_handle(self):
        a=action()
        self.ledger.grant('alice','email','original',a)
        old=self.ledger.issue('alice','email',a).handle
        self.ledger.withdraw('alice','email')
        new=self.ledger.grant('alice','email','regrant',a)
        self.assertEqual(new.version,3)
        self.assertEqual(self.ledger.commit(old,a).state,'DENY')
        self.assertEqual(self.ledger.commit(self.ledger.issue('alice','email',a).handle,a).state,'COMMITTED')

    def test_altered_recipient_is_not_endorsed(self):
        a=action(); b=action(recipient='attacker@example.test')
        self.ledger.grant('alice','email','original',a)
        self.assertEqual(self.ledger.issue('alice','email',b).reason,'action_not_endorsed')

    def test_altered_message_is_not_endorsed(self):
        self.ledger.grant('alice','email','original',action())
        self.assertEqual(self.ledger.issue('alice','email',action('two')).reason,'action_not_endorsed')

    def test_wrong_principal_rejected(self):
        with self.assertRaises(ValueError):
            self.ledger.grant('alice','email','bad',action(principal='mallory'))

    def test_wrong_tool_scope_rejected(self):
        with self.assertRaises(ValueError):
            self.ledger.grant('alice','payment','bad',action(tool='email'))

    def test_substituted_untrusted_action_class_rejected(self):
        class Fraud: action_hash='0'*64
        with self.assertRaises(TypeError):
            self.ledger.grant('alice','email','bad',Fraud())

    def test_failed_grant_rolls_back_authority_and_journal(self):
        a=action(); b=action('new',effect_id='fx2')
        self.ledger.grant('alice','email','original',a)
        handle=self.ledger.issue('alice','email',a).handle
        with self.assertRaisesRegex(RuntimeError,'injected'):
            self.ledger.grant('alice','email','changed',b,inject_failure=True)
        x=self.ledger.current('alice','email')
        self.assertEqual((x.version,x.generation,x.action_hash),(1,1,a.action_hash))
        self.assertEqual(self.fence.state('alice','email')['generation'],1)
        self.assertEqual(self.ledger.commit(handle,a).state,'COMMITTED')
        self.assertEqual(len(self.ledger.events()),1)

    def test_failed_withdraw_rolls_back_both(self):
        a=action();self.ledger.grant('alice','email','original',a)
        handle=self.ledger.issue('alice','email',a).handle
        with self.assertRaisesRegex(RuntimeError,'injected'):
            self.ledger.withdraw('alice','email',inject_failure=True)
        self.assertTrue(self.ledger.current('alice','email').active)
        self.assertEqual(self.fence.state('alice','email')['generation'],1)
        self.assertEqual(self.ledger.commit(handle,a).state,'COMMITTED')

    def test_after_commit_withdrawal_does_not_undo_history(self):
        a=action(); self.ledger.grant('alice','email','original',a)
        h=self.ledger.issue('alice','email',a).handle
        self.assertEqual(self.ledger.commit(h,a).state,'COMMITTED')
        self.ledger.withdraw('alice','email')
        self.assertEqual(self.ledger.commit(h,a).state,'CONFIRMED')
        self.assertEqual(self.fence.effect_count(),1)

    def test_unknown_withdrawal_creates_inactive_generation(self):
        self.assertIsNone(self.ledger.withdraw('alice','email'))
        self.assertEqual(self.fence.state('alice','email'),{'generation':1,'active':False})
        self.assertIsNone(self.ledger.current('alice','email'))
        self.assertFalse(self.ledger.issue('alice','email',action()).allowed)

    def test_multi_thread_revisions_are_serial_and_gapless(self):
        def attempt(i):
            z=AtomicChoiceLedger(CommitFence(self.db))
            return z.grant('alice','email',f'v{i}',action(str(i),effect_id=f'e{i}')).version
        with ThreadPoolExecutor(max_workers=8) as pool:
            versions=list(pool.map(attempt,range(16)))
        self.assertEqual(sorted(versions),list(range(1,17)))
        self.assertEqual(self.ledger.current('alice','email').version,16)
        self.assertEqual(self.fence.state('alice','email')['generation'],16)

    def test_multiple_simultaneous_commit_attempts_one_effect(self):
        a=action();self.ledger.grant('alice','email','original',a)
        handle=self.ledger.issue('alice','email',a).handle
        def commit(_): return self.ledger.commit(handle,a).state
        with ThreadPoolExecutor(max_workers=10) as pool:
            states=list(pool.map(commit,range(20)))
        self.assertEqual(states.count('COMMITTED'),1)
        self.assertTrue(set(states)<= {'COMMITTED','CONFIRMED'})
        self.assertEqual(self.fence.effect_count(),1)

    def test_revocation_holds_write_lock_until_atomic_commit(self):
        a=action();self.ledger.grant('alice','email','original',a)
        handle=self.ledger.issue('alice','email',a).handle
        in_tx=threading.Event(); release=threading.Event(); attempting=threading.Event()
        original_write=self.ledger._write
        def paused_write(*args, **kwargs):
            original_write(*args, **kwargs)
            if args[8]=='WITHDRAW':
                in_tx.set(); self.assertTrue(release.wait(5))
        self.ledger._write=paused_write
        result={}
        def revoke():result['withdraw']=self.ledger.withdraw('alice','email')
        def commit():
            attempting.set(); result['commit']=self.ledger.commit(handle,a)
        th1=threading.Thread(target=revoke);th2=threading.Thread(target=commit)
        th1.start()
        self.assertTrue(in_tx.wait(5))
        th2.start();self.assertTrue(attempting.wait(5))
        release.set(); th1.join(5);th2.join(5)
        self.assertFalse(th1.is_alive() or th2.is_alive())
        self.assertEqual(result['commit'].state,'DENY')
        self.assertEqual(self.fence.effect_count(),0)

    def test_records_are_metadata_only_not_message_content(self):
        secret='private sample text NEVER STORE'
        a=Action(principal='alice',tool='email',operation='send',object_id='draft-1',
                 destination='customer@example.test',arguments={'body':secret}, effect_id='z')
        self.ledger.grant('alice','email','customer message',a)
        with closing(self.fence.connect()) as con:
            rows=con.execute('SELECT * FROM choice_events').fetchall()
            self.assertEqual(len(rows),1)
            self.assertNotIn(secret,str(dict(rows[0])))

    def test_hash_change_from_mutated_action_arguments_is_denied(self):
        a=action();self.ledger.grant('alice','email','initial',a)
        a.arguments['subject']='changed after approval' # dataclass frozen, nested dict not frozen
        self.assertEqual(self.ledger.issue('alice','email',a).reason,'action_not_endorsed')

    def test_fence_manual_regrant_not_considered_valid_choice(self):
        a=action();self.ledger.grant('alice','email','initial',a)
        self.fence.activate('alice','email') # trusted-boundary bypass scenario
        self.assertEqual(self.ledger.issue('alice','email',a).reason,'stale_authority_generation')
        # But direct fence.issue_handle can still bypass. Host segregation required.
        h,_=self.fence.issue_handle('alice','email',a)
        self.assertEqual(self.fence.commit(h.handle_id,a).state,'COMMITTED')

    def test_upstream_baseline_is_unsafe_for_external_ungated_provider(self):
        a=action();self.ledger.grant('alice','email','initial',a)
        h=self.ledger.issue('alice','email',a).handle
        b=PreDispatchOnlyBaseline(self.fence)
        self.assertTrue(b.precheck(h,a))
        self.ledger.withdraw('alice','email')
        # Remote external sink is outside commit-time fence and can still act.
        self.assertTrue(b.remote_commit(a))
        self.assertEqual(self.fence.effect_count(),0)

    def test_existing_upstream_audit_contains_choice_events(self):
        self.ledger.grant('alice','email','initial',action())
        self.ledger.withdraw('alice','email')
        kinds=[ev['kind'] for ev in self.fence.audit()]
        self.assertIn('CHOICE_GRANT',kinds)
        self.assertIn('CHOICE_WITHDRAW',kinds)

    def test_process_revision_serialization(self):
        # Multiprocessing tests across OS processes, not just Python threads.
        q=mp.Queue()
        workers=[mp.Process(target=process_revise,args=(str(self.db),i,q)) for i in range(6)]
        for p in workers:p.start()
        values=[q.get(timeout=10) for _ in workers]
        for p in workers:p.join(10)
        self.assertTrue(all(p.exitcode==0 for p in workers),values)
        self.assertEqual(sorted(v[1] for v in values),list(range(1,7)),values)
        self.assertEqual(self.ledger.current('alice','email').version,6)

if __name__=='__main__': unittest.main()
