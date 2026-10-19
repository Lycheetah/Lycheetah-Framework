import tempfile
import hashlib
import threading
import unittest
from pathlib import Path
from sovereign_choice import Request, SovereignChoice

KEY = b"demo-only-secret-not-production-use"
T = 1800000000
PAYLOAD = hashlib.sha256(b"email body version 1").hexdigest()
OTHER_PAYLOAD = hashlib.sha256(b"email body version 2").hexdigest()


class GateTests(unittest.TestCase):
    def setUp(self):
        self.g = SovereignChoice(audit_key=KEY, clock=lambda: T)
        self.g.register_owner("human")

    def tearDown(self):
        self.g.close()

    def grant(self, id="g", op="prepare_draft", resource="letter", uses=1, expires=T+100):
        return self.g.issue_grant(grant_id=id, owner="human", agent="agent", operation=op,
                                  resource=resource, expires_at=expires, max_uses=uses)

    def attempt(self, id="g", op="prepare_draft", resource="letter", request="r", approval=None,
                owner="human", agent="agent", payload=PAYLOAD):
        return self.g.decide(Request(owner, agent, id, op, resource, request, approval, payload))

    def test_01_authorized_read_or_draft_allowed(self):
        self.grant()
        self.assertEqual(self.attempt().reason, "allowed")

    def test_02_unknown_grant_denied(self):
        self.assertEqual(self.attempt().reason, "unknown_grant")

    def test_03_wrong_resource_denied(self):
        self.grant()
        self.assertEqual(self.attempt(resource="someone_else").reason, "out_of_scope")

    def test_04_wrong_operation_denied(self):
        self.grant()
        self.assertEqual(self.attempt(op="send_email").reason, "out_of_scope")

    def test_05_wrong_agent_denied(self):
        self.grant()
        self.assertEqual(self.attempt(agent="intruder").reason, "wrong_principal")

    def test_06_expired_grant_denied(self):
        self.grant(expires=T)
        self.assertEqual(self.attempt().reason, "expired_grant")

    def test_07_revoked_grant_denied(self):
        self.grant()
        self.g.revoke("human", "g")
        self.assertEqual(self.attempt().reason, "revoked")

    def test_08_revised_intent_invalidates_stale_grant(self):
        self.grant()
        self.g.revise_intent("human", reason="Changed my mind")
        self.assertEqual(self.attempt().reason, "stale_intent")
        self.grant("new")
        self.assertEqual(self.attempt(id="new", request="r2").reason, "allowed")

    def test_09_high_impact_requires_specific_approval(self):
        self.grant(op="send_email", resource="recipient@example.com")
        self.assertEqual(self.attempt(op="send_email", resource="recipient@example.com").reason,
                         "approval_required")
        # First denial consumes request id, but not grant.
        self.g.approve_once(owner="human", approval_id="a", grant_id="g", request_id="r2",
                            operation="send_email", resource="recipient@example.com", expires_at=T+10, payload_digest=PAYLOAD)
        self.assertEqual(self.attempt(op="send_email", resource="recipient@example.com",
                                      request="r2", approval="a").reason, "allowed")

    def test_10_approval_cannot_transfer_to_another_request(self):
        self.grant(op="send_email", resource="email1")
        self.g.approve_once(owner="human", approval_id="a", grant_id="g", request_id="r1",
                            operation="send_email", resource="email1", expires_at=T+10, payload_digest=PAYLOAD)
        self.assertEqual(self.attempt(op="send_email", resource="email1", request="r2",
                                      approval="a").reason, "invalid_approval")

    def test_11_revision_after_approval_revokes_both(self):
        self.grant(op="send_email", resource="email1")
        self.g.approve_once(owner="human", approval_id="a", grant_id="g", request_id="r",
                            operation="send_email", resource="email1", expires_at=T+10, payload_digest=PAYLOAD)
        self.g.revise_intent("human", reason="Not anymore")
        self.assertEqual(self.attempt(op="send_email", resource="email1", approval="a").reason,
                         "stale_intent")

    def test_12_replay_denied(self):
        self.grant(uses=2)
        self.assertTrue(self.attempt().allowed)
        self.assertEqual(self.attempt().reason, "replayed_request")

    def test_13_one_use_limit(self):
        self.grant()
        self.assertTrue(self.attempt().allowed)
        self.assertEqual(self.attempt(request="r2").reason, "exhausted_grant")

    def test_14_unknown_operation_denied(self):
        self.grant()
        self.assertEqual(self.attempt(op="custom_shell_exec").reason, "unknown_operation")

    def test_15_receipt_integrity_detects_mutation(self):
        self.grant()
        self.attempt()
        self.assertTrue(self.g.audit_ok())
        self.g.db.execute("UPDATE audit SET payload='{}' WHERE event='decision'")
        self.assertFalse(self.g.audit_ok())

    def test_16_concurrent_single_use_one_winner(self):
        self.grant(uses=1)
        answers = []
        errors = []
        lock = threading.Lock()
        def run(n):
            try:
                result = self.attempt(request=f"r{n}")
                with lock:
                    answers.append(result.allowed)
            except Exception as exc:
                with lock:
                    errors.append(exc)
        ts = [threading.Thread(target=run, args=(i,)) for i in range(8)]
        for t in ts: t.start()
        for t in ts: t.join()
        self.assertEqual(errors, [], f"Worker exceptions: {errors}")
        self.assertEqual(len(answers), 8)
        self.assertEqual(sum(answers), 1)

    def test_17_approval_expired_denied(self):
        self.grant(op="send_email", resource="email1")
        self.g.approve_once(owner="human", approval_id="a", grant_id="g", request_id="r",
                            operation="send_email", resource="email1", expires_at=T, payload_digest=PAYLOAD)
        self.assertEqual(self.attempt(op="send_email", resource="email1", approval="a").reason,
                         "invalid_approval")

    def test_18_old_approval_cannot_approve_changed_resource(self):
        self.grant(op="send_email", resource="email1")
        self.g.approve_once(owner="human", approval_id="a", grant_id="g", request_id="r",
                            operation="send_email", resource="email1", expires_at=T+10, payload_digest=PAYLOAD)
        self.assertEqual(self.attempt(op="send_email", resource="email2", approval="a").reason,
                         "out_of_scope")

    def test_19_idempotent_revocation(self):
        self.grant()
        self.assertTrue(self.g.revoke("human", "g"))
        self.assertFalse(self.g.revoke("human", "g"))

    def test_20_cannot_approve_revoked_grant(self):
        self.grant(op="send_email", resource="email1")
        self.g.revoke("human", "g")
        with self.assertRaises(ValueError):
            self.g.approve_once(owner="human", approval_id="a", grant_id="g", request_id="r",
                                operation="send_email", resource="email1", expires_at=T+10, payload_digest=PAYLOAD)

    def test_21_invalid_grant_rejected_at_creation(self):
        with self.assertRaises(ValueError):
            self.grant(op="anything")

    def test_22_grant_one_owner_not_other(self):
        self.grant()
        self.g.register_owner("other")
        self.assertEqual(self.attempt(owner="other").reason, "wrong_principal")

    def test_23_persistent_hash_chain_works_across_reopens(self):
        with tempfile.TemporaryDirectory() as temp:
            path = str(Path(temp) / "audit.db")
            a = SovereignChoice(path, audit_key=KEY)
            a.register_owner("one")
            a.close()
            b = SovereignChoice(path, audit_key=KEY)
            self.assertTrue(b.audit_ok())
            b.revise_intent("one", reason="Re-evaluate")
            self.assertTrue(b.audit_ok())
            b.close()

    def test_25_high_impact_approval_bound_to_exact_payload(self):
        self.grant(op="send_email", resource="email1")
        self.g.approve_once(owner="human", approval_id="a", grant_id="g", request_id="r",
                            operation="send_email", resource="email1", expires_at=T+10,
                            payload_digest=PAYLOAD)
        self.assertEqual(self.attempt(op="send_email", resource="email1", approval="a",
                                      payload=OTHER_PAYLOAD).reason, "invalid_approval")

    def test_26_high_impact_requires_real_digest(self):
        self.grant(op="send_email", resource="email1")
        self.assertEqual(self.attempt(op="send_email", resource="email1", payload="").reason,
                         "payload_binding_required")

    def test_27_clock_is_host_owned(self):
        self.grant(expires=T)
        self.assertEqual(self.attempt().reason, "expired_grant")

    def test_28_cross_connection_single_use_serialized(self):
        with tempfile.TemporaryDirectory() as temp:
            path = str(Path(temp) / "shared.db")
            initializer = SovereignChoice(path, audit_key=KEY, clock=lambda: T)
            initializer.register_owner("human")
            initializer.issue_grant(grant_id="once", owner="human", agent="agent",
                                    operation="prepare_draft", resource="letter",
                                    expires_at=T+20, max_uses=1)
            initializer.close()
            outcomes, errors = [], []
            guard = threading.Lock()
            def runner(i):
                try:
                    g = SovereignChoice(path, audit_key=KEY, clock=lambda: T)
                    d = g.decide(Request("human", "agent", "once", "prepare_draft",
                                         "letter", f"across-{i}"))
                    g.close()
                    with guard:
                        outcomes.append(d.allowed)
                except Exception as exc:
                    with guard:
                        errors.append(str(exc))
            threads = [threading.Thread(target=runner, args=(i,)) for i in range(6)]
            for t in threads: t.start()
            for t in threads: t.join()
            self.assertEqual(errors, [])
            self.assertEqual(len(outcomes), 6)
            self.assertEqual(sum(outcomes), 1)
            verifier = SovereignChoice(path, audit_key=KEY, clock=lambda: T)
            self.assertTrue(verifier.audit_ok())
            verifier.close()

    def test_24_revisions_not_moral_failures(self):
        self.grant()
        # Changing from 'work' to a family priority is allowed; not scored as a defect.
        self.g.revise_intent("human", reason="Care obligation became urgent")
        self.assertEqual(self.attempt().reason, "stale_intent")
        self.grant("family", op="prepare_draft", resource="family_note")
        self.assertTrue(self.attempt(id="family", resource="family_note", request="r2").allowed)


if __name__ == "__main__":
    unittest.main()
