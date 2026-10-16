import copy
import json
import tempfile
import threading
import unittest
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from durable_action_broker import (
    BrokerResult, DemoRuntime, DurableActionBroker, Evidence, IdempotencyConflict, Requirement,
    ResponseLost, SimulatedProcessCrash, default_policy, sha256_json,
)
from evidence_lease import (
    EvidenceLocked, LeaseAwareEffectAdapter, LeaseExpired, LeaseRejected,
    LeaseUnavailable, SQLiteEvidenceLeaseAuthority, SQLiteLeasedEffectProvider,
)

WITNESS_KEY = b"research-witness-key-32-bytes-minimum-0000000000"
LEASE_KEY = b"research-evidence-lease-key-32-bytes-minimum-000000"
EVENT = {"tool": "release.promote", "artifact": "release-sha-123", "environment": "staging"}
REQ = Requirement("ci.release", "EXACT", "PASS", "release-sha-123")
PASS = Evidence("ci.release", "build-17", "release-sha-123", "build-digest-17", "PASS")
FAIL = Evidence("ci.release", "build-18", "release-sha-123", "build-digest-18", "FAIL")


class Clock:
    def __init__(self):
        self.value = 1000.0
    def __call__(self):
        return self.value


class Fixture(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        root = Path(self.tmp.name)
        self.clock = Clock()
        self.authority = SQLiteEvidenceLeaseAuthority(
            root / "evidence.sqlite", LEASE_KEY, clock=self.clock, lease_seconds=10)
        self.authority.put(PASS)
        self.runtime = DemoRuntime(default_policy())
        self.broker = DurableActionBroker(
            root / "broker.sqlite", WITNESS_KEY, self.runtime, (REQ,),
            self.authority, clock=self.clock, ttl_seconds=60)
        self.effect_provider = SQLiteLeasedEffectProvider(
            root / "effect-provider.sqlite", self.authority, clock=self.clock)
        self.adapter = LeaseAwareEffectAdapter(
            self.authority, self.effect_provider, (REQ,), self.broker.get_operation)

    def tearDown(self):
        self.tmp.cleanup()

    def issue(self, event=None):
        result, token = self.broker.admit(event or EVENT)
        self.assertTrue(result.ok, result.reason)
        return token

    def enqueue(self, event=None):
        event = event or EVENT
        token = self.issue(event)
        result = self.broker.authorize_and_enqueue(token, event)
        self.assertTrue(result.ok, result.reason)
        return result.operation_id

    def dispatch(self, opid):
        return self.broker.dispatch_one(opid, self.adapter)

    def test_happy_path_leases_evidence_and_applies_one_effect(self):
        opid = self.enqueue()
        result = self.dispatch(opid)
        self.assertTrue(result.ok, result.reason)
        self.assertEqual(result.state, "DONE")
        self.assertEqual(self.effect_provider.effect_count(), 1)
        self.assertEqual(self.authority.active_lease_count(), 0)

    def test_evidence_update_winning_before_lease_causes_fail_closed(self):
        opid = self.enqueue()
        self.adapter.before_acquire = lambda _op, _payload: self.authority.put(FAIL)
        result = self.dispatch(opid)
        self.assertFalse(result.ok)
        self.assertEqual(result.state, "RECONCILE")
        self.assertEqual(result.reason, "definitive-dispatch-denial")
        self.assertEqual(self.effect_provider.effect_count(), 0)
        self.assertEqual(self.authority.get_evidence("ci.release"), FAIL)

    def test_lease_winning_before_evidence_update_blocks_update_until_effect(self):
        opid = self.enqueue()
        observed = []
        def after_lease(_op, _payload):
            try:
                self.authority.put(FAIL)
            except EvidenceLocked:
                observed.append("blocked")
            else:
                observed.append("unexpected-update")
        self.adapter.after_acquire = after_lease
        result = self.dispatch(opid)
        self.assertTrue(result.ok, result.reason)
        self.assertEqual(observed, ["blocked"])
        self.assertEqual(self.authority.get_evidence("ci.release"), PASS)
        self.assertEqual(self.effect_provider.effect_count(), 1)
        self.authority.put(FAIL)  # release after confirmed outcome unlocks writes
        self.assertEqual(self.authority.get_evidence("ci.release"), FAIL)

    def test_snapshot_to_lease_race_never_executes_against_false_predicate(self):
        """Run 30 deterministic two-order races: update-first or lease-first."""
        outcomes = {"lease_denied": 0, "mutation_blocked": 0}
        for i in range(30):
            if i % 2 == 0:
                # Update is linearized before the adapter's atomic lease acquisition.
                opid = self.enqueue(dict(EVENT, race=i))
                self.adapter.before_acquire = lambda _op, _payload: self.authority.put(FAIL)
                res = self.dispatch(opid)
                self.assertFalse(res.ok)
                self.assertEqual(res.state, "RECONCILE")
                self.assertEqual(self.effect_provider.effect_count(), i // 2)
                outcomes["lease_denied"] += 1
                self.authority.put(Evidence("ci.release", f"build-{i+20}", "release-sha-123", f"digest-{i+20}", "PASS"))
            else:
                # Lease is linearized before the update; that update must block.
                opid = self.enqueue(dict(EVENT, race=i))
                blocked = []
                def hook(_op, _payload):
                    try: self.authority.put(FAIL)
                    except EvidenceLocked: blocked.append(True)
                self.adapter.before_acquire = None
                self.adapter.after_acquire = hook
                res = self.dispatch(opid)
                self.assertTrue(res.ok, res.reason)
                self.assertEqual(blocked, [True])
                self.assertEqual(self.effect_provider.effect_count(), i // 2 + 1)
                outcomes["mutation_blocked"] += 1
                self.authority.put(Evidence("ci.release", f"build-{i+20}", "release-sha-123", f"digest-{i+20}", "PASS"))
        self.assertEqual(outcomes, {"lease_denied": 15, "mutation_blocked": 15})

    def test_response_lost_keeps_lease_until_recovery(self):
        opid = self.enqueue()
        self.effect_provider.drop_next_response = True
        first = self.dispatch(opid)
        self.assertFalse(first.ok)
        self.assertEqual(first.reason, "provider-outcome-unknown-safe-retry")
        self.assertEqual(self.effect_provider.effect_count(), 1)
        self.assertEqual(self.authority.active_lease_count("ci.release"), 1)
        with self.assertRaises(EvidenceLocked):
            self.authority.put(FAIL)
        retry = self.dispatch(opid)
        self.assertTrue(retry.ok, retry.reason)
        self.assertEqual(self.effect_provider.effect_count(), 1)
        self.assertEqual(self.authority.active_lease_count(), 0)

    def test_committed_effect_is_reconciled_before_evidence_recheck(self):
        opid = self.enqueue()
        self.effect_provider.drop_next_response = True
        first = self.dispatch(opid)
        self.assertFalse(first.ok)
        self.clock.value += 11  # token expires, but in-flight evidence stays pinned
        with self.assertRaises(EvidenceLocked):
            self.authority.put(FAIL)
        second = self.dispatch(opid)
        self.assertTrue(second.ok, second.reason)
        self.assertEqual(second.reason, "effect-confirmed-from-provider-record")
        self.assertEqual(second.state, "DONE")
        self.assertEqual(self.effect_provider.effect_count(), 1)
        self.authority.put(FAIL)  # now the committed outcome is known and the lease is released

    def test_expiry_between_claim_and_provider_validation_renews_without_unlock(self):
        opid = self.enqueue()
        called = []
        def expire_once():
            if not called:
                self.clock.value += 11
                called.append("expired-before-validation")
                # The lease is already IN_FLIGHT, so even after token expiry the
                # authority must not allow its evidence to change during renewal.
                with self.assertRaises(EvidenceLocked):
                    self.authority.put(FAIL)
            else:
                return
        self.effect_provider.before_lease_validation = expire_once
        result = self.dispatch(opid)
        self.assertTrue(result.ok, result.reason)
        self.assertEqual(called, ["expired-before-validation"])
        self.assertEqual(self.effect_provider.effect_count(), 1)
        self.assertEqual(self.authority.active_lease_count("ci.release"), 0)
        self.authority.put(FAIL)

    def test_inflight_lease_pins_evidence_when_provider_call_outlives_token_ttl(self):
        opid = self.enqueue()
        attempted = []
        def delayed_commit_boundary():
            # The provider has already validated a token and entered its simulated
            # effect transaction. Let wall time jump past the token TTL before commit.
            self.clock.value += 11
            try:
                self.authority.put(FAIL)
            except EvidenceLocked:
                attempted.append("still-pinned")
            else:
                attempted.append("unsafe-unlock")
        self.effect_provider.before_effect_commit = delayed_commit_boundary
        result = self.dispatch(opid)
        self.assertTrue(result.ok, result.reason)
        self.assertEqual(attempted, ["still-pinned"])
        self.assertEqual(self.effect_provider.effect_count(), 1)
        self.assertEqual(self.authority.active_lease_count("ci.release"), 0)
        self.authority.put(FAIL)

    def test_expired_lease_cannot_start_new_effect(self):
        opid = self.enqueue()
        record = self.broker.get_operation(opid)
        token = json.loads(record["token_json"])
        lease = self.authority.acquire_lease(opid, sha256_json(EVENT), (REQ,), token["body"]["evidence"])
        self.clock.value += 10
        with self.assertRaises(LeaseExpired):
            self.effect_provider.execute(opid, EVENT, lease)
        self.assertEqual(self.effect_provider.effect_count(), 0)

    def test_real_sqlite_race_linearizes_update_or_lease_never_both(self):
        outcomes = {"update_won": 0, "lease_won": 0}
        for i in range(30):
            key = f"race.evidence.{i}"
            req = Requirement(key, "EXACT", "PASS", f"subject-{i}")
            admitted = Evidence(key, f"v-{i}", f"subject-{i}", f"digest-{i}", "PASS")
            changed = Evidence(key, f"v-{i}-next", f"subject-{i}", f"digest-{i}-next", "FAIL")
            self.authority.put(admitted)
            barrier = threading.Barrier(2)
            result = {}
            op_id = f"race-op-{i}"
            action_hash = sha256_json({"operation": i})
            items = [{"requirement": req.to_dict(), "admitted": admitted.to_dict()}]

            def update():
                barrier.wait()
                try:
                    self.authority.put(changed)
                    result["update"] = "applied"
                except EvidenceLocked:
                    result["update"] = "blocked"

            def lease():
                barrier.wait()
                try:
                    result["lease_token"] = self.authority.acquire_lease(op_id, action_hash, (req,), items)
                    result["lease"] = "issued"
                except LeaseUnavailable:
                    result["lease"] = "denied"

            with ThreadPoolExecutor(max_workers=2) as pool:
                f1 = pool.submit(update)
                f2 = pool.submit(lease)
                f1.result(); f2.result()

            if result["lease"] == "issued":
                self.assertEqual(result["update"], "blocked")
                self.assertEqual(self.authority.get_evidence(key), admitted)
                self.authority.release(result["lease_token"])
                outcomes["lease_won"] += 1
            else:
                self.assertEqual(result["update"], "applied")
                self.assertEqual(self.authority.get_evidence(key), changed)
                outcomes["update_won"] += 1
        self.assertEqual(sum(outcomes.values()), 30)

    def test_subject_status_mode_allows_new_version_when_predicate_remains_true(self):
        subject_req = Requirement("ci.release", "SUBJECT_STATUS", "PASS", "release-sha-123")
        subject_broker = DurableActionBroker(
            Path(self.tmp.name) / "subject-broker.sqlite", WITNESS_KEY, self.runtime,
            (subject_req,), self.authority, clock=self.clock, ttl_seconds=60)
        result, token = subject_broker.admit(EVENT)
        self.assertTrue(result.ok, result.reason)
        queued = subject_broker.authorize_and_enqueue(token, EVENT)
        self.assertTrue(queued.ok, queued.reason)
        self.authority.put(Evidence("ci.release", "build-18", "release-sha-123", "new-digest", "PASS"))
        adapter = LeaseAwareEffectAdapter(
            self.authority, self.effect_provider, (subject_req,), subject_broker.get_operation)
        dispatched = subject_broker.dispatch_one(queued.operation_id, adapter)
        self.assertTrue(dispatched.ok, dispatched.reason)
        self.assertEqual(self.effect_provider.effect_count(), 1)
        self.assertEqual(self.authority.get_evidence("ci.release").version, "build-18")

    def test_lease_token_and_database_survive_authority_recreation(self):
        opid = self.enqueue()
        op = self.broker.get_operation(opid)
        witness = json.loads(op["token_json"])
        lease = self.authority.acquire_lease(opid, sha256_json(EVENT), (REQ,), witness["body"]["evidence"])
        restarted = SQLiteEvidenceLeaseAuthority(
            self.authority.db_path, LEASE_KEY, clock=self.clock, lease_seconds=10)
        with self.assertRaises(EvidenceLocked):
            restarted.put(FAIL)
        self.assertEqual(restarted.active_lease_count("ci.release"), 1)
        restarted.release(lease)
        restarted.put(FAIL)
        self.assertEqual(restarted.get_evidence("ci.release"), FAIL)

    def test_tampered_lease_hmac_rejected_before_effect(self):
        opid = self.enqueue()
        record = self.broker.get_operation(opid)
        token = json.loads(record["token_json"])
        lease = self.authority.acquire_lease(opid, sha256_json(EVENT), (REQ,), token["body"]["evidence"])
        forged = copy.deepcopy(lease)
        forged["body"]["evidence"][0]["admitted"]["status"] = "FAIL"
        forged["body"]["expires_at"] += 100
        with self.assertRaises(LeaseRejected):
            self.effect_provider.execute(opid, EVENT, forged)
        self.assertEqual(self.effect_provider.effect_count(), 0)

    def test_action_substitution_rejected_before_effect(self):
        opid = self.enqueue()
        record = self.broker.get_operation(opid)
        token = json.loads(record["token_json"])
        lease = self.authority.acquire_lease(opid, sha256_json(EVENT), (REQ,), token["body"]["evidence"])
        with self.assertRaises(LeaseRejected):
            self.effect_provider.execute(opid, dict(EVENT, environment="production"), lease)
        self.assertEqual(self.effect_provider.effect_count(), 0)

    def test_operation_id_substitution_rejected_before_effect(self):
        opid = self.enqueue()
        record = self.broker.get_operation(opid)
        token = json.loads(record["token_json"])
        lease = self.authority.acquire_lease(opid, sha256_json(EVENT), (REQ,), token["body"]["evidence"])
        with self.assertRaises(LeaseRejected):
            self.effect_provider.execute("another-operation", EVENT, lease)
        self.assertEqual(self.effect_provider.effect_count(), 0)

    def test_provider_idempotency_cache_returns_committed_result_even_after_lease_expiry(self):
        opid = self.enqueue()
        self.effect_provider.drop_next_response = True
        with self.assertRaises(ResponseLost):
            self.adapter.execute(opid, EVENT)
        self.clock.value += 20
        with self.assertRaises(EvidenceLocked):
            self.authority.put(FAIL)
        cached = self.adapter.lookup(opid, EVENT)
        self.assertIsNotNone(cached)
        self.assertTrue(cached["replayed"])
        self.authority.put(FAIL)
        self.assertEqual(self.effect_provider.effect_count(), 1)

    def test_same_operation_different_payload_is_never_replayed(self):
        opid = self.enqueue()
        self.assertTrue(self.dispatch(opid).ok)
        altered = dict(EVENT, environment="production")
        with self.assertRaises(IdempotencyConflict):
            self.effect_provider.lookup(opid, altered)
        self.assertEqual(self.effect_provider.effect_count(), 1)

    def test_multiple_requirements_are_leased_atomically(self):
        req2 = Requirement("ci.security", "EXACT", "PASS", "release-sha-123")
        opid = self.enqueue()
        record = self.broker.get_operation(opid)
        token = json.loads(record["token_json"])
        admitted_items = list(token["body"]["evidence"]) + [{
            "requirement": req2.to_dict(),
            "admitted": Evidence("ci.security", "security-build-1", "release-sha-123", "sec-digest-1", "PASS").to_dict(),
        }]
        with self.assertRaises(LeaseUnavailable):
            self.authority.acquire_lease(opid, sha256_json(EVENT), (REQ, req2), admitted_items)
        self.assertEqual(self.authority.active_lease_count(), 0)
        # Failed multi-key acquisition did not lock even the first key.
        self.authority.put(FAIL)
        self.assertEqual(self.authority.get_evidence("ci.release"), FAIL)

    def test_all_keys_remain_locked_until_all_leases_release(self):
        op1 = self.enqueue(dict(EVENT, operation=1))
        op2 = self.enqueue(dict(EVENT, operation=2))
        t1 = json.loads(self.broker.get_operation(op1)["token_json"])
        t2 = json.loads(self.broker.get_operation(op2)["token_json"])
        lease1 = self.authority.acquire_lease(op1, sha256_json(dict(EVENT, operation=1)), (REQ,), t1["body"]["evidence"])
        lease2 = self.authority.acquire_lease(op2, sha256_json(dict(EVENT, operation=2)), (REQ,), t2["body"]["evidence"])
        self.assertEqual(self.authority.active_lease_count("ci.release"), 2)
        self.authority.release(lease1)
        with self.assertRaises(EvidenceLocked): self.authority.put(FAIL)
        self.authority.release(lease2)
        self.authority.put(FAIL)

    def test_concurrent_dispatchers_create_one_effect(self):
        opid = self.enqueue()
        barrier = threading.Barrier(2)
        def run():
            barrier.wait()
            return self.dispatch(opid)
        with ThreadPoolExecutor(max_workers=2) as pool:
            results = list(pool.map(lambda _: run(), range(2)))
        self.assertTrue(any(x.ok for x in results), results)
        self.assertEqual(self.effect_provider.effect_count(), 1)
        row = self.broker.get_operation(opid)
        self.assertEqual(row["state"], "DONE")

    def test_evidence_update_after_confirmed_success_is_allowed(self):
        opid = self.enqueue()
        self.assertTrue(self.dispatch(opid).ok)
        self.authority.put(FAIL)
        self.assertEqual(self.authority.get_evidence("ci.release"), FAIL)

    def test_idempotent_retry_after_crash_recovers_once(self):
        opid = self.enqueue()
        self.effect_provider.drop_next_response = True
        first = self.dispatch(opid)
        self.assertFalse(first.ok)
        restarted_authority = SQLiteEvidenceLeaseAuthority(
            self.authority.db_path, LEASE_KEY, clock=self.clock, lease_seconds=10)
        restarted_provider = SQLiteLeasedEffectProvider(
            self.effect_provider.db_path, restarted_authority, clock=self.clock)
        restarted_adapter = LeaseAwareEffectAdapter(
            restarted_authority, restarted_provider, (REQ,), self.broker.get_operation)
        second = self.broker.dispatch_one(opid, restarted_adapter)
        self.assertTrue(second.ok, second.reason)
        self.assertEqual(restarted_provider.effect_count(), 1)


if __name__ == "__main__":
    unittest.main(verbosity=2)
