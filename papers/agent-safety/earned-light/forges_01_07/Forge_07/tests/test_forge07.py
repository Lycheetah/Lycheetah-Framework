import json, sqlite3, tempfile, unittest
from pathlib import Path
from unittest.mock import patch
from sys import path
path.insert(0,str(Path(__file__).resolve().parents[1]))
import controller,provider
from lab import instance,worker,run_trial,retry_trial,restartable_provider_trial

class ProviderTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.p=str(Path(self.tmp.name)/'p.db');provider.init(self.p)
    def tearDown(self):self.tmp.cleanup()
    def test_apply_stores_one(self):
        provider.apply(self.p,'a',{'kind':'write','data':'test'});self.assertEqual(len(provider.state(self.p)['effects']),1)
    def test_duplicate_dedup(self):
        for _ in range(3):provider.apply(self.p,'a',{'kind':'write','data':'test'})
        self.assertEqual(len(provider.state(self.p)['effects']),1)
    def test_mismatched_idempotency_key_rejected(self):
        provider.apply(self.p,'a',{'kind':'write','data':'x'})
        with self.assertRaises(ValueError):provider.apply(self.p,'a',{'kind':'write','data':'y'})
    def test_naive_duplicate(self):
        provider.apply(self.p,'a',{'kind':'write','data':'test'},dedup=False)
        provider.apply(self.p,'a',{'kind':'write','data':'test'},dedup=False)
        self.assertEqual(len(provider.state(self.p)['effects']),2)
    def test_absent_operation(self):self.assertIsNone(provider.receipt(self.p,'unknown'))
    def test_write_compensation(self):
        provider.apply(self.p,'a',{'kind':'write','data':'x'})
        self.assertEqual(provider.compensate(self.p,'a','c')['status'],'restored')
        self.assertEqual(provider.state(self.p)['effects'][0]['compensated'],1)
    def test_notify_irreversible(self):
        provider.apply(self.p,'a',{'kind':'notify','data':'x'})
        self.assertEqual(provider.compensate(self.p,'a','c')['status'],'irreversible')
    def test_comp_idempotent(self):
        provider.apply(self.p,'a',{'kind':'write','data':'x'})
        self.assertEqual(provider.compensate(self.p,'a','c'),provider.compensate(self.p,'a','c'))
        self.assertEqual(len(provider.state(self.p)['compensations']),1)
    def test_comp_key_collision(self):
        provider.apply(self.p,'a',{'kind':'write','data':'x'});provider.apply(self.p,'b',{'kind':'write','data':'y'})
        provider.compensate(self.p,'a','c')
        with self.assertRaises(ValueError):provider.compensate(self.p,'b','c')
    def test_stable_operation_receipt(self):
        first=provider.apply(self.p,'a',{'kind':'write','data':'x'})
        self.assertEqual(first,provider.receipt(self.p,'a'))

class ControllerTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.p=str(Path(self.tmp.name)/'c.db');controller.start(self.p)
    def tearDown(self):self.tmp.cleanup()
    def test_start_is_proposed(self):self.assertEqual(controller.job(self.p)['status'],'proposed')
    def test_reserve_is_durable(self):
        controller.reserve(self.p);self.assertEqual(controller.job(self.p)['status'],'reserved')
    def test_revocation_blocks_new(self):
        controller.revoke(self.p);self.assertEqual(controller.reserve(self.p),'blocked')
    def test_repeated_revocation_no_grant(self):
        controller.revoke(self.p);self.assertEqual(controller.request_local_grant(self.p),0)
    def test_reserved_not_cancelled_by_revocation(self):
        controller.reserve(self.p);controller.revoke(self.p)
        self.assertEqual(controller.job(self.p)['status'],'reserved')
    def test_blocked_never_dispatched(self):
        controller.revoke(self.p);controller.reserve(self.p)
        self.assertEqual(controller.reconcile(self.p,'http://127.0.0.1:1'),'no_effect_dispatched')
    def test_proposed_unshipped(self):
        self.assertEqual(controller.reconcile(self.p,'http://127.0.0.1:1'),'not_dispatched')
    def test_mark_allowlist(self):
        with self.assertRaises(ValueError):controller.mark(self.p,evil='unexpected')
    def test_no_observer_no_certainty(self):
        controller.reserve(self.p)
        self.assertEqual(controller.reconcile(self.p,'http://127.0.0.1:1',provider_query=False),'unresolved_effect')
    def test_unreachable_provider_no_certainty(self):
        controller.reserve(self.p)
        self.assertEqual(controller.reconcile(self.p,'http://127.0.0.1:1'),'unresolved_effect')
    def test_recovery_requires_revocation(self):
        with self.assertRaises(ValueError):controller.recover(self.p,'http://127.0.0.1:1')
    def test_unmodified_job_after_failed_recovery(self):
        controller.reserve(self.p);controller.revoke(self.p)
        r=controller.recover(self.p,'http://127.0.0.1:1',provider_query=False)
        self.assertEqual(r['terminal_status'],'unresolved_effect')
    def test_after_reservation_lacks_definitive_no_effect(self):
        controller.reserve(self.p);controller.revoke(self.p)
        self.assertEqual(controller.recover(self.p,'http://127.0.0.1:1',provider_query=False)['terminal_status'],'unresolved_effect')
    def test_no_fake_independent_attestation(self):
        controller.reserve(self.p);controller.revoke(self.p)
        self.assertFalse(controller.recover(self.p,'http://127.0.0.1:1',provider_query=False)['independent_effect_proof'])

class MultiProcessTrials(unittest.TestCase):
    def test_write_after_commit_kill_restores(self):
        r=run_trial('write','after_commit_before_ack')
        self.assertEqual(r['kill_code'],73)
        self.assertEqual(r['consequences_reported'],'restored')
        self.assertEqual(r['remote_effect_count'],1)
    def test_notification_reports_irreversible(self):
        r=run_trial('notify','after_commit_before_ack')
        self.assertEqual(r['consequences_reported'],'irreversible')
    def test_unknown_fails_closed(self):
        r=run_trial('write','after_reserve_before_send')
        self.assertEqual(r['consequences_reported'],'unresolved_effect')
        self.assertEqual(r['remote_effect_count'],0)
    def test_compensation_crash_replay(self):
        r=run_trial('write','after_ack_before_return','after_compensation_before_ack')
        self.assertEqual(r['consequences_reported'],'restored')
        self.assertEqual(r['compensation_count'],1)
    def test_conventional_outbox_idempotent(self):
        r=retry_trial(True)
        self.assertEqual(r['effects'],1)
    def test_provider_outage_and_restart(self):
        r=restartable_provider_trial()
        self.assertEqual(r['during_outage'],'unresolved_effect')
        self.assertEqual(r['after_provider_restart'],'restored')
        self.assertEqual(r['remote_effects'],1)
        self.assertEqual(r['compensations'],1)
    def test_nonidempotent_retry_duplicates(self):
        r=retry_trial(False)
        self.assertEqual(r['effects'],2)

if __name__=='__main__':unittest.main()
