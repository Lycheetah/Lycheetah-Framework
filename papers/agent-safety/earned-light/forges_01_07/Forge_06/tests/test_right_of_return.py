import tempfile, pathlib, unittest, sys, secrets
from contextlib import closing
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
from right_of_return import (ReturnController,SimulatedProvider,sign_operator_request,
    Rejected,Conflict,UnknownEffect,SnapshotBaseline)


class RightOfReturnTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        root=pathlib.Path(self.tmp.name)
        self.provider=SimulatedProvider(root/'provider.sqlite')
        self.secret=b'test-only-unshared-signing-material'
        self.ctrl=ReturnController(root/'controller.sqlite',self.provider,self.secret,clock=lambda:100)
        self.ctrl.grant('delegation-1',['write','notify'])
        self.provider.seed('policy',{'state':'original'})

    def req(self,action,delegation='delegation-1',nonce=None,secret=None,expires=200):
        return sign_operator_request(secret or self.secret,action,delegation,nonce=nonce or secrets.token_hex(16),expires=expires)

    def write(self,op='w1',value='ai-version',key='policy'):
        item=self.provider.current(key)
        self.ctrl.propose('delegation-1',op,'write',key,{'state':value},item['version'] if item else None)
        return self.ctrl.dispatch(op)

    def revoke(self): self.ctrl.revoke('delegation-1',self.req('revoke'))
    def return_own(self): return self.ctrl.return_to_human('delegation-1',self.req('return'))

    def test_single_recovery(self):
        self.write();self.revoke()
        result=self.return_own()
        self.assertEqual(result[0]['status'],'restored')
        self.assertEqual(self.provider.current('policy')['value'],{'state':'original'})

    def test_multiple_recovery_reverse_sequence(self):
        self.write('w1','first');self.write('w2','second');self.revoke()
        self.assertEqual([r['status'] for r in self.return_own()],['restored','restored'])
        self.assertEqual(self.provider.current('policy')['value'],{'state':'original'})

    def test_partial_recovers_prior_key_when_other_conflicted(self):
        self.provider.seed('hours',{'state':'9to5'})
        self.write('w1','first');self.write('w2','later','hours')
        self.provider.human_write('hours',{'state':'human'})
        self.revoke()
        statuses={r['op_id']:r['status'] for r in self.return_own()}
        self.assertEqual(statuses,{'w1':'restored','w2':'conflict'})
        self.assertEqual(self.provider.current('hours')['value'],{'state':'human'})

    def test_human_intervened_same_value_detected(self):
        self.write();self.provider.human_write('policy',{'state':'ai-version'});self.revoke()
        self.assertEqual(self.return_own()[0]['status'],'conflict')

    def test_notification_irreversible(self):
        self.ctrl.propose('delegation-1','n1','notify','subscriber@example.test',{'message':'hello'})
        self.assertEqual(self.ctrl.dispatch('n1'),'confirmed')
        self.revoke()
        self.assertEqual(self.return_own()[0]['status'],'irreversible')
        with closing(__import__('sqlite3').connect(self.provider.path)) as c:
            self.assertEqual(c.execute('select count(*) from outbound').fetchone()[0],1)

    def test_expired_operator_request_rejected(self):
        self.assertRaises(Rejected,self.ctrl.revoke,'delegation-1',self.req('revoke',expires=99))

    def test_bad_mac_rejected(self):
        self.assertRaises(Rejected,self.ctrl.revoke,'delegation-1',self.req('revoke',secret=b'bad key'))

    def test_operator_action_mismatch(self):
        self.assertRaises(Rejected,self.ctrl.revoke,'delegation-1',self.req('return'))

    def test_operator_target_mismatch(self):
        self.assertRaises(Rejected,self.ctrl.revoke,'delegation-1',self.req('revoke',delegation='other'))

    def test_operator_nonce_replay(self):
        token=self.req('revoke')
        self.ctrl.revoke('delegation-1',token)
        self.assertRaises(Rejected,self.ctrl.revoke,'delegation-1',token)

    def test_recovery_requires_revocation(self):
        self.write()
        self.assertRaises(Rejected,self.ctrl.return_to_human,'delegation-1',self.req('return'))

    def test_propose_after_revocation_rejected(self):
        self.revoke()
        self.assertRaises(Rejected,self.ctrl.propose,'delegation-1','x','write','policy',{})

    def test_dispatch_after_revocation_blocked(self):
        self.ctrl.propose('delegation-1','x','write','policy',{},0)
        self.revoke()
        self.assertEqual(self.ctrl.dispatch('x'),'blocked')
        self.assertIsNone(self.provider.receipt('x'))
        self.assertEqual(self.return_own()[0]['status'],'no_effect_dispatched')

    def test_inflight_can_commit_after_revocation(self):
        self.ctrl.propose('delegation-1','x','write','policy',{'state':'later'},0)
        status=self.ctrl.dispatch('x',after_reservation=self.revoke)
        self.assertEqual(status,'confirmed')
        self.assertEqual(self.return_own()[0]['status'],'restored')

    def test_lost_ack_reconciles_before_return(self):
        self.ctrl.propose('delegation-1','x','write','policy',{'state':'later'},0)
        self.assertEqual(self.ctrl.dispatch('x',simulate_lost_ack=True),'uncertain')
        self.revoke()
        self.assertEqual(self.return_own()[0]['status'],'restored')

    def test_unobserved_effect_not_declared_safe(self):
        self.ctrl.propose('delegation-1','x','write','policy',{'state':'later'},0)
        self.ctrl.dispatch('x',simulate_lost_ack=True)
        # provider unobservable: no receipt is not proof that effects did not happen
        prior=self.provider.receipt
        self.provider.receipt=lambda _:None
        self.revoke()
        self.assertEqual(self.return_own()[0]['status'],'unresolved_effect')
        self.provider.receipt=prior

    def test_idempotent_provider_apply(self):
        a=self.provider.apply('direct','write','policy',{'state':'abc'},0)
        b=self.provider.apply('direct','write','policy',{'state':'abc'},0)
        self.assertEqual(a,b)
        self.assertEqual(self.provider.current('policy')['version'],1)

    def test_idempotency_key_collision_rejected(self):
        self.provider.apply('direct','write','policy',{'state':'abc'},0)
        self.assertRaises(Conflict,self.provider.apply,'direct','write','policy',{'state':'different'},0)

    def test_compensation_retry_same_id(self):
        self.write();self.revoke()
        self.assertEqual(self.return_own()[0]['status'],'restored')
        self.assertEqual(self.return_own()[0]['status'],'restored')

    def test_created_record_removed(self):
        self.write('w1','born',key='new')
        self.revoke()
        self.assertEqual(self.return_own()[0]['status'],'restored')
        self.assertIsNone(self.provider.current('new'))

    def test_stale_write_not_applied(self):
        self.ctrl.propose('delegation-1','x','write','policy',{'state':'bad'},100)
        self.assertRaises(Conflict,self.ctrl.dispatch,'x')
        self.revoke()
        self.assertEqual(self.return_own()[0]['status'],'unresolved_effect')

    def test_idempotent_notification(self):
        a=self.provider.apply('notify1','notify','test@example.test',{'message':'hi'})
        b=self.provider.apply('notify1','notify','test@example.test',{'message':'hi'})
        self.assertEqual(a,b)
        with closing(__import__('sqlite3').connect(self.provider.path)) as c:
            self.assertEqual(c.execute('select count(*) from outbound').fetchone()[0],1)

    def test_snapshot_baseline_overwrites_third_party_update(self):
        self.write();self.provider.human_write('policy',{'state':'human'})
        SnapshotBaseline.undo(self.provider,'policy',{'state':'original'})
        self.assertEqual(self.provider.current('policy')['value'],{'state':'original'})
        # demonstrates negative control's flaw, not improved performance vs strong CAS baseline

    def test_provider_unavailable_in_reconciliation_not_silent(self):
        self.ctrl.propose('delegation-1','x','notify','someone',{'message':'hi'})
        self.ctrl.dispatch('x',simulate_lost_ack=True)
        original=self.provider.receipt
        def offline(_):raise OSError('simulated provider outage')
        self.provider.receipt=offline
        self.revoke()
        self.assertEqual(self.return_own()[0]['status'],'unresolved_effect')
        self.provider.receipt=original

    def test_invalid_grant_scope(self):
        self.assertRaises(Rejected,self.ctrl.grant,'bad',['delete_all'])

    def test_out_of_scope_action(self):
        self.ctrl.grant('writes-only',['write'])
        self.assertRaises(Rejected,self.ctrl.propose,'writes-only','x','notify','address',{'message':'hi'})


    def test_provider_error_during_compensation_reported_unresolved(self):
        self.write();self.revoke()
        prior=self.provider.compensate
        def unavailable(*args): raise TimeoutError('unreachable')
        self.provider.compensate=unavailable
        self.assertEqual(self.return_own()[0]['status'],'unresolved_effect')
        self.provider.compensate=prior
        self.assertEqual(self.return_own()[0]['status'],'restored')

    def test_compromised_operator_key_can_forge_authorization(self):
        # Failure Museum: compromise of the local signing secret defeats its guarantee.
        forged=sign_operator_request(self.secret,'revoke','delegation-1',nonce='forged',expires=200)
        self.ctrl.revoke('delegation-1',forged)
        self.assertRaises(Rejected,self.ctrl.propose,'delegation-1','unwanted','write','policy',{})

    def test_two_compensations_when_intermediate_human_edit_same_value(self):
        self.write('first','a');self.write('second','b')
        self.provider.human_write('policy',{'state':'b'})
        self.revoke()
        statuses=[r['status'] for r in self.return_own()]
        self.assertEqual(statuses,['conflict','conflict'])

    def test_return_keeps_newer_human_update_even_without_value_difference(self):
        self.write('first','a')
        self.provider.human_write('policy',{'state':'original'})
        self.revoke()
        self.assertEqual(self.return_own()[0]['status'],'conflict')
        self.assertEqual(self.provider.current('policy')['value'],{'state':'original'})

if __name__=='__main__': unittest.main()
