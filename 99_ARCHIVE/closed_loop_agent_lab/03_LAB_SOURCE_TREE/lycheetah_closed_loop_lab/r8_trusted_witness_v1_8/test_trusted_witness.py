import copy
import json
import tempfile
import threading
import unittest
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from trusted_witness import (EvidenceRecord, EvidenceRequirement, TrustedWitnessGate,
                             ToyRuntime, sha256_json)


class Provider:
    def __init__(self, records):
        self.records = {x.key: x for x in records}
        self.lock = threading.Lock()
    def get_evidence(self, key):
        with self.lock:
            return self.records.get(key)
    def put(self, record):
        with self.lock:
            self.records[record.key] = record


class Clock:
    def __init__(self, value=1000.0): self.value = value
    def __call__(self): return self.value


class MutateAfterFinalityReadProvider(Provider):
    """Exhibits the remaining external-provider TOCTOU boundary intentionally."""
    def __init__(self, records):
        super().__init__(records)
        self.calls = 0
    def get_evidence(self, key):
        with self.lock:
            record = self.records.get(key)
            self.calls += 1
            # Call 1 is admission. On call 2 finality receives a PASS snapshot,
            # but the external provider state changes just after returning it.
            if self.calls == 2 and key == "required-ci":
                self.records[key] = EvidenceRecord("required-ci", "5", "artifact-A", "build-778", "FAIL")
            return record


class TrustedWitnessTests(unittest.TestCase):
    def setUp(self):
        self.td = tempfile.TemporaryDirectory()
        self.db = str(Path(self.td.name) / "witnesses.sqlite")
        self.clock = Clock()
        self.policy = {"id":"test.policy", "version":"1", "sha256":"a"*64}
        self.runtime = ToyRuntime(self.policy)
        self.req = EvidenceRequirement("required-ci", "EXACT", "PASS", "artifact-A")
        self.provider = Provider([EvidenceRecord("required-ci","4","artifact-A","build-777","PASS"),
                                  EvidenceRecord("weak-local","1","artifact-A","unchecked","PASS")])
        self.gate = TrustedWitnessGate(self.db, b"test-only-key-32-bytes-minimum!!", self.runtime,
                                       (self.req,), self.provider, clock=self.clock, ttl_seconds=30)
        self.event = {"tool":"deploy.promote", "artifact":"artifact-A", "release":"r7"}
    def tearDown(self): self.td.cleanup()
    def issue(self):
        result, token = self.gate.admit(self.event)
        self.assertTrue(result.ready, result.reason)
        self.assertIsNotNone(token)
        return token

    def test_honest_witness_can_finalize(self):
        token = self.issue()
        result = self.gate.finalize(token, self.event)
        self.assertTrue(result.ready, result.reason)

    def test_public_digest_cannot_replace_hmac_after_requirement_substitution(self):
        token = self.issue()
        forged = copy.deepcopy(token)
        forged["body"]["evidence"][0]["requirement"] = {
            "key":"weak-local", "mode":"SUBJECT_STATUS", "required_status":"PASS",
            "required_subject_hash":"artifact-A"}
        forged["body"]["evidence"][0]["admitted"] = self.provider.get_evidence("weak-local").to_dict()
        forged["body"]["admission_receipt_sha256"] = "f"*64
        forged["hmac_sha256"] = sha256_json(forged["body"])  # public hash, not HMAC
        result = self.gate.finalize(forged, self.event)
        self.assertFalse(result.ready)
        self.assertEqual(result.reason, "witness-authentication-failed")

    def test_forgery_cannot_be_transferred_to_another_gate(self):
        token = self.issue()
        other_db = str(Path(self.td.name) / "other.sqlite")
        other = TrustedWitnessGate(other_db, b"another-test-only-key-32-bytes-minimum!!", self.runtime,
                                   (self.req,), self.provider, clock=self.clock)
        result = other.finalize(token, self.event)
        self.assertFalse(result.ready)
        self.assertEqual(result.reason, "witness-authentication-failed")

    def test_action_substitution_rejected(self):
        token = self.issue()
        changed = dict(self.event, release="r8")
        result = self.gate.finalize(token, changed)
        self.assertFalse(result.ready)
        self.assertEqual(result.reason, "event-changed-after-admission")

    def test_changed_exact_evidence_rejected(self):
        token = self.issue()
        self.provider.put(EvidenceRecord("required-ci","5","artifact-A","build-778","PASS"))
        result = self.gate.finalize(token, self.event)
        self.assertFalse(result.ready)
        self.assertEqual(result.reason, "exact-evidence-changed-after-admission")

    def test_failed_evidence_rejected(self):
        token = self.issue()
        self.provider.put(EvidenceRecord("required-ci","5","artifact-A","build-778","FAIL"))
        result = self.gate.finalize(token, self.event)
        self.assertFalse(result.ready)
        self.assertEqual(result.reason, "exact-evidence-changed-after-admission")

    def test_expiry_rejected(self):
        token = self.issue()
        self.clock.value += 31
        result = self.gate.finalize(token, self.event)
        self.assertFalse(result.ready)
        self.assertEqual(result.reason, "witness-expired")

    def test_witness_is_single_use(self):
        token = self.issue()
        self.assertTrue(self.gate.finalize(token, self.event).ready)
        second = self.gate.finalize(token, self.event)
        self.assertFalse(second.ready)
        self.assertEqual(second.reason, "witness-already-consumed")

    def test_requirements_are_not_caller_selectable_at_admission(self):
        # Public API has no requirements parameter; caller cannot request weak-local.
        result, token = self.gate.admit(self.event)
        self.assertTrue(result.ready)
        self.assertEqual(token["body"]["evidence"][0]["requirement"], self.req.to_dict())

    def test_concurrent_finalize_allows_exactly_one_consumer(self):
        # Repeat to exercise SQLite's write-lock/conditional-update path under races.
        with ThreadPoolExecutor(max_workers=2) as pool:
            for _ in range(25):
                token = self.issue()
                barrier = threading.Barrier(2)
                def call():
                    barrier.wait()
                    return self.gate.finalize(token, self.event)
                results = list(pool.map(lambda _: call(), range(2)))
                self.assertEqual(sum(r.ready for r in results), 1, results)
                self.assertEqual(sum(r.reason == "witness-already-consumed" for r in results), 1, results)

    def test_witness_registry_survives_gate_object_recreation(self):
        token = self.issue()
        restarted = TrustedWitnessGate(self.db, b"test-only-key-32-bytes-minimum!!", self.runtime,
                                       (self.req,), self.provider, clock=self.clock, ttl_seconds=30)
        self.assertTrue(restarted.finalize(token, self.event).ready)
        replay = self.gate.finalize(token, self.event)
        self.assertFalse(replay.ready)
        self.assertEqual(replay.reason, "witness-already-consumed")

    def test_policy_change_after_admission_rejected(self):
        token = self.issue()
        self.runtime.policy = {"id":"test.policy", "version":"2", "sha256":"b"*64}
        result = self.gate.finalize(token, self.event)
        self.assertFalse(result.ready)
        self.assertEqual(result.reason, "policy-changed-after-admission")

    def test_malformed_token_rejected(self):
        token = self.issue()
        token["untrusted_extension"] = True
        result = self.gate.finalize(token, self.event)
        self.assertFalse(result.ready)
        self.assertEqual(result.reason, "invalid-token-envelope")

    def test_runtime_review_fails_closed_at_admission(self):
        self.runtime.decision = "REVIEW"
        result, token = self.gate.admit(self.event)
        self.assertFalse(result.ready)
        self.assertIsNone(token)
        self.assertEqual(result.reason, "runtime-not-allow-at-admission")

    def test_non_finite_event_fails_closed(self):
        result, token = self.gate.admit({"tool":"deploy", "value":float("nan")})
        self.assertFalse(result.ready)
        self.assertIsNone(token)

    def test_documented_external_provider_toctou_remains_open(self):
        # This is an intentional limitation demonstration, not a security pass:
        # a separate evidence provider can change after returning its snapshot.
        special_provider = MutateAfterFinalityReadProvider([
            EvidenceRecord("required-ci", "4", "artifact-A", "build-777", "PASS")])
        gate = TrustedWitnessGate(self.db, b"test-only-key-32-bytes-minimum!!", self.runtime,
                                  (self.req,), special_provider, clock=self.clock)
        result, token = gate.admit(self.event)
        self.assertTrue(result.ready, result.reason)
        final = gate.finalize(token, self.event)
        self.assertTrue(final.ready, final.reason)  # snapshot was still PASS
        self.assertEqual(special_provider.get_evidence("required-ci").status, "FAIL")


if __name__ == "__main__": unittest.main(verbosity=2)
