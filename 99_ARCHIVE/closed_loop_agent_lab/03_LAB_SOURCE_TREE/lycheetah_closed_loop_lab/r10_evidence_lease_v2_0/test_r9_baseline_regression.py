import copy
import json
import tempfile
import threading
import unittest
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from durable_action_broker import (
    BrokerResult, DemoRuntime, DurableActionBroker, Evidence, MutableEvidenceStore,
    NonIdempotentProvider, Requirement, ResponseLost, SimulatedProcessCrash,
    SQLiteIdempotentProvider, default_policy, sha256_json,
)

KEY=b"local-test-key-for-broker-prototype-32-bytes-minimum!!"
EVENT={"tool":"refund.create","account":"acct-17","amount_minor":3200,"currency":"NZD"}
REQ=Requirement("ci.release","EXACT","PASS","release-sha-123")


class Clock:
    def __init__(self): self.value=1000.0
    def __call__(self): return self.value


class Fixture(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        root=Path(self.tmp.name)
        self.local_db=str(root/"broker.sqlite")
        self.remote_db=str(root/"remote.sqlite")
        self.clock=Clock()
        self.runtime=DemoRuntime(default_policy())
        self.evidence=MutableEvidenceStore([Evidence("ci.release","build-17","release-sha-123","build-digest-17","PASS")])
        self.broker=self.new_broker()
        self.provider=SQLiteIdempotentProvider(self.remote_db)

    def tearDown(self): self.tmp.cleanup()

    def new_broker(self):
        return DurableActionBroker(self.local_db,KEY,self.runtime,(REQ,),self.evidence,clock=self.clock,ttl_seconds=40)

    def issue(self,event=None):
        result, token=self.broker.admit(event or EVENT)
        self.assertTrue(result.ok,result.reason)
        self.assertIsNotNone(token)
        return token

    def enqueue(self,token,event=None,**kw):
        result=self.broker.authorize_and_enqueue(token,event or EVENT,**kw)
        return result

    def test_happy_path_consumes_witness_and_creates_one_effect(self):
        token=self.issue(); queued=self.enqueue(token)
        self.assertTrue(queued.ok,queued.reason); self.assertEqual(queued.state,"PENDING")
        result=self.broker.dispatch_one(queued.operation_id,self.provider)
        self.assertTrue(result.ok,result.reason); self.assertEqual(self.provider.effect_count(),1)
        self.assertEqual(self.broker.get_operation(queued.operation_id)["state"],"DONE")

    def test_crash_before_local_commit_rolls_back_consumption_and_outbox(self):
        token=self.issue()
        with self.assertRaises(SimulatedProcessCrash): self.enqueue(token,crash_before_commit=True)
        con=self.broker._connect()
        try:
            self.assertEqual(con.execute("SELECT COUNT(*) FROM outbox").fetchone()[0],0)
            self.assertIsNone(con.execute("SELECT consumed_at FROM issued WHERE witness_id=?",(token["body"]["witness_id"],)).fetchone()[0])
        finally: con.close()
        retry=self.enqueue(token); self.assertTrue(retry.ok,retry.reason)

    def test_lost_enqueue_ack_retries_to_same_operation(self):
        token=self.issue()
        with self.assertRaises(SimulatedProcessCrash): self.enqueue(token,crash_after_commit=True)
        retry=self.enqueue(token)
        self.assertTrue(retry.ok,retry.reason); self.assertTrue(retry.replayed)
        con=self.broker._connect()
        try: self.assertEqual(con.execute("SELECT COUNT(*) FROM outbox").fetchone()[0],1)
        finally: con.close()

    def test_lost_enqueue_ack_after_expiry_returns_status_but_cannot_dispatch(self):
        token=self.issue()
        with self.assertRaises(SimulatedProcessCrash): self.enqueue(token,crash_after_commit=True)
        self.clock.value += 41
        recovered=self.enqueue(token)
        self.assertTrue(recovered.ok,recovered.reason)
        self.assertTrue(recovered.replayed)
        self.assertEqual(recovered.state,"PENDING")
        refused=self.broker.dispatch_one(recovered.operation_id,self.provider)
        self.assertFalse(refused.ok); self.assertEqual(refused.state,"RECONCILE")
        self.assertEqual(self.provider.effect_count(),0)

    def test_restart_recovers_pending_outbox(self):
        token=self.issue(); queued=self.enqueue(token); self.assertTrue(queued.ok)
        broker2=self.new_broker(); provider2=SQLiteIdempotentProvider(self.remote_db)
        result=broker2.dispatch_one(queued.operation_id,provider2)
        self.assertTrue(result.ok,result.reason); self.assertEqual(provider2.effect_count(),1)

    def test_remote_commit_response_lost_retries_without_duplicate_effect(self):
        token=self.issue(); queued=self.enqueue(token)
        self.provider.drop_next_response=True
        first=self.broker.dispatch_one(queued.operation_id,self.provider)
        self.assertFalse(first.ok); self.assertEqual(first.reason,"provider-outcome-unknown-safe-retry")
        self.assertEqual(self.provider.effect_count(),1)
        replay=self.broker.dispatch_one(queued.operation_id,self.provider)
        self.assertTrue(replay.ok,replay.reason); self.assertEqual(self.provider.effect_count(),1)
        self.assertTrue(replay.replayed)

    def test_crash_after_remote_commit_before_local_ack(self):
        token=self.issue(); queued=self.enqueue(token)
        with self.assertRaises(SimulatedProcessCrash): self.broker.dispatch_one(queued.operation_id,self.provider,crash_after_provider_commit=True)
        self.assertEqual(self.provider.effect_count(),1)
        restarted=self.new_broker(); result=restarted.dispatch_one(queued.operation_id,SQLiteIdempotentProvider(self.remote_db))
        self.assertTrue(result.ok,result.reason); self.assertEqual(self.provider.effect_count(),1)

    def test_two_concurrent_dispatchers_produce_one_effect_per_operation(self):
        with ThreadPoolExecutor(max_workers=2) as pool:
            for index in range(25):
                event=dict(EVENT,stress_case=index)
                token=self.issue(event); queued=self.enqueue(token,event)
                barrier=threading.Barrier(2)
                def run():
                    barrier.wait()
                    return self.broker.dispatch_one(queued.operation_id,self.provider)
                results=list(pool.map(lambda _:run(),range(2)))
                self.assertTrue(any(x.ok for x in results),results)
                self.assertEqual(self.provider.effect_count(),index+1)

    def test_same_idempotency_key_different_payload_is_conflict(self):
        self.provider.execute("same-key",{"amount":1})
        from durable_action_broker import IdempotencyConflict
        with self.assertRaises(IdempotencyConflict): self.provider.execute("same-key",{"amount":2})
        self.assertEqual(self.provider.effect_count(),1)

    def test_non_idempotent_provider_is_not_sent_and_routes_reconcile(self):
        token=self.issue(); queued=self.enqueue(token); unsafe=NonIdempotentProvider()
        result=self.broker.dispatch_one(queued.operation_id,unsafe)
        self.assertFalse(result.ok); self.assertEqual(result.state,"RECONCILE")
        self.assertEqual(len(unsafe.effects),0)
        second=self.broker.dispatch_one(queued.operation_id,unsafe)
        self.assertEqual(second.reason,"provider-idempotency-required")
        self.assertEqual(len(unsafe.effects),0)

    def test_public_hash_forgery_fails_hmac(self):
        token=self.issue(); forged=copy.deepcopy(token)
        forged["body"]["admission_receipt_sha256"]="f"*64
        forged["hmac_sha256"]=sha256_json(forged["body"])
        result=self.enqueue(forged)
        self.assertFalse(result.ok); self.assertEqual(result.reason,"witness-authentication-failed")

    def test_action_substitution_rejected(self):
        token=self.issue(); result=self.enqueue(token,dict(EVENT,amount_minor=1))
        self.assertFalse(result.ok); self.assertEqual(result.reason,"event-changed-after-admission")

    def test_policy_change_before_enqueue_rejected(self):
        token=self.issue(); self.runtime.policy={"id":"lycheetah.test-policy","version":"2","sha256":"b"*64}
        result=self.enqueue(token)
        self.assertFalse(result.ok)

    def test_evidence_change_before_enqueue_rejected(self):
        token=self.issue(); self.evidence.put(Evidence("ci.release","build-18","release-sha-123","different-digest","PASS"))
        result=self.enqueue(token)
        self.assertFalse(result.ok); self.assertIn("evidence-changed-at-enqueue",result.reason)

    def test_runtime_review_denied(self):
        self.runtime.decision="REVIEW"; token=self.issue() if False else None
        result,token=self.broker.admit(EVENT)
        self.assertFalse(result.ok); self.assertIsNone(token)

    def test_witness_expiry_rejected(self):
        token=self.issue(); self.clock.value += 41
        result=self.enqueue(token)
        self.assertFalse(result.ok); self.assertEqual(result.reason,"witness-expired")

    def test_witness_registry_persists_across_broker_recreation(self):
        token=self.issue(); queued=self.enqueue(token)
        restarted=self.new_broker(); retry=restarted.authorize_and_enqueue(token,EVENT)
        self.assertTrue(retry.ok,retry.reason); self.assertEqual(retry.operation_id,queued.operation_id)

    def test_provider_outcome_contract_persists_result(self):
        token=self.issue(); queued=self.enqueue(token)
        a=self.provider.execute(queued.operation_id,EVENT)
        b=self.provider.execute(queued.operation_id,EVENT)
        self.assertEqual(a["request_sha256"],b["request_sha256"])
        self.assertEqual(self.provider.effect_count(),1)

    def test_naive_non_idempotent_retry_duplicates_effects(self):
        unsafe=NonIdempotentProvider()
        try:
            unsafe.execute("op-1",EVENT)
            raise SimulatedProcessCrash("pretend client lost acknowledgment")
        except SimulatedProcessCrash:
            pass
        unsafe.execute("op-1",EVENT)
        self.assertEqual(len(unsafe.effects),2)

    def test_idempotent_provider_retry_has_one_effect_for_same_failure(self):
        op="op-retry"
        self.provider.drop_next_response=True
        with self.assertRaises(ResponseLost): self.provider.execute(op,EVENT)
        result=self.provider.execute(op,EVENT)
        self.assertTrue(result["replayed"]); self.assertEqual(self.provider.effect_count(),1)

    def test_mutation_of_persisted_intent_is_reconciled_before_remote_call(self):
        token=self.issue(); queued=self.enqueue(token)
        con=self.broker._connect()
        try:
            con.execute("UPDATE outbox SET action_json=? WHERE operation_id=?",
                        (json.dumps({"tool":"payments.refund","amount_minor":999999}),queued.operation_id))
        finally: con.close()
        result=self.broker.dispatch_one(queued.operation_id,self.provider)
        self.assertFalse(result.ok)
        self.assertEqual(result.reason,"persisted-action-digest-mismatch")
        self.assertEqual(result.state,"RECONCILE")
        self.assertEqual(self.provider.effect_count(),0)

    def test_external_evidence_can_change_after_dispatch_snapshot(self):
        class MutatesAfterSnapshot(MutableEvidenceStore):
            def __init__(self, records):
                super().__init__(records); self.calls=0
            def get_evidence(self,key):
                rec=super().get_evidence(key)
                self.calls += 1
                if self.calls == 3 and key == "ci.release":
                    # Call 3 is the immediate pre-dispatch check: return PASS,
                    # then mutate backing state before the broker contacts the effect provider.
                    self.put(Evidence("ci.release","build-18","release-sha-123","build-digest-18","FAIL"))
                return rec
        evidence=MutatesAfterSnapshot([Evidence("ci.release","build-17","release-sha-123","build-digest-17","PASS")])
        broker=DurableActionBroker(self.local_db,KEY,self.runtime,(REQ,),evidence,clock=self.clock,ttl_seconds=40)
        admitted,token=broker.admit(EVENT)
        self.assertTrue(admitted.ok,admitted.reason)
        queued=broker.authorize_and_enqueue(token,EVENT)
        self.assertTrue(queued.ok,queued.reason)
        result=broker.dispatch_one(queued.operation_id,self.provider)
        self.assertTrue(result.ok,result.reason)
        self.assertEqual(evidence.get_evidence("ci.release").status,"FAIL")
        self.assertEqual(self.provider.effect_count(),1)
        # This is a demonstrated residual provider TOCTOU gap, not a security pass.

    def test_evidence_change_after_enqueue_routes_to_reconcile_before_effect(self):
        token=self.issue(); queued=self.enqueue(token)
        self.evidence.put(Evidence("ci.release","build-18","release-sha-123","build-digest-18","FAIL"))
        result=self.broker.dispatch_one(queued.operation_id,self.provider)
        self.assertFalse(result.ok); self.assertIn("dispatch-evidence-changed",result.reason)
        self.assertEqual(result.state,"RECONCILE"); self.assertEqual(self.provider.effect_count(),0)

    def test_policy_change_after_enqueue_routes_to_reconcile_before_effect(self):
        token=self.issue(); queued=self.enqueue(token)
        self.runtime.policy={"id":"lycheetah.test-policy","version":"2","sha256":"b"*64}
        result=self.broker.dispatch_one(queued.operation_id,self.provider)
        self.assertFalse(result.ok); self.assertTrue(result.reason.startswith("dispatch-policy-changed"))
        self.assertEqual(result.state,"RECONCILE"); self.assertEqual(self.provider.effect_count(),0)

    def test_runtime_decision_change_after_enqueue_routes_to_reconcile(self):
        token=self.issue(); queued=self.enqueue(token)
        self.runtime.decision="REVIEW"
        result=self.broker.dispatch_one(queued.operation_id,self.provider)
        self.assertFalse(result.ok); self.assertEqual(result.reason,"dispatch-runtime-not-allow")
        self.assertEqual(result.state,"RECONCILE"); self.assertEqual(self.provider.effect_count(),0)

    def test_expired_pending_operation_routes_to_reconcile(self):
        token=self.issue(); queued=self.enqueue(token); self.clock.value += 41
        result=self.broker.dispatch_one(queued.operation_id,self.provider)
        self.assertFalse(result.ok); self.assertEqual(result.state,"RECONCILE")
        self.assertEqual(self.provider.effect_count(),0)

    def test_repeated_dispatch_after_done_is_noop(self):
        token=self.issue(); queued=self.enqueue(token)
        self.assertTrue(self.broker.dispatch_one(queued.operation_id,self.provider).ok)
        again=self.broker.dispatch_one(queued.operation_id,self.provider)
        self.assertTrue(again.ok); self.assertEqual(again.reason,"already-done")
        self.assertEqual(self.provider.effect_count(),1)


if __name__=="__main__": unittest.main(verbosity=2)
