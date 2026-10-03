from concurrent.futures import ThreadPoolExecutor
from dataclasses import replace
import unittest

from safety_sim.authority import CapabilityAuthority, ConventionalACL
from safety_sim.fixtures import fresh
from safety_sim.model import Action, State, digest


ARMS = (CapabilityAuthority, ConventionalACL)


class BrokerTests(unittest.TestCase):
    def each_arm(self, body):
        for arm in ARMS:
            with self.subTest(arm=arm.label):
                body(fresh(arm))

    def test_valid_draft_changes_actual_document(self):
        def exercise(f):
            result = f.broker.submit(f.session, f.root, f.draft(), witness=f.witness)
            self.assertEqual(result.state, State.CONFIRMED)
            self.assertEqual(f.service.snapshot("draft").content, f.artifact.display)
            self.assertEqual(f.service.snapshot("draft").revision, 1)
            self.assertEqual(len(f.service.effects()), 1)
        self.each_arm(exercise)

    def test_valid_private_send_to_allowed_reader(self):
        def exercise(f):
            result = f.broker.submit(f.session, f.root, f.send(object_id="secret"))
            self.assertEqual(result.state, State.CONFIRMED)
            self.assertEqual(f.service.effects()[0].payload, "SYNTHETIC_PRIVATE_RECORD")
        self.each_arm(exercise)

    def test_document_readers_override_broader_grant_sinks(self):
        def exercise(f):
            result = f.broker.submit(f.session, f.root,
                                    f.send(object_id="secret", recipient="guest"))
            self.assertEqual(result.state, State.REJECTED)
            self.assertEqual(f.service.effects(), ())
        self.each_arm(exercise)

    def test_negative_control_can_disclose_if_broker_is_bypassed(self):
        f = fresh()
        # A trusted experiment intentionally bypasses the assumed mediation boundary.
        receipt = f.service.dispatch(f.send(object_id="secret", recipient="guest"))
        self.assertEqual(receipt.recipient, "guest")
        self.assertEqual(receipt.payload, "SYNTHETIC_PRIVATE_RECORD")
        self.assertEqual(f.authority.events(), ())

    def test_unknown_classification_is_unresolved_not_public(self):
        def exercise(f):
            f.service.replace_document("public", classification="UNRECOGNISED")
            result = f.broker.submit(f.session, f.root, f.send())
            self.assertEqual(result.state, State.UNRESOLVED)
            self.assertEqual(f.service.effects(), ())
        self.each_arm(exercise)

    def test_grant_is_bound_to_authenticated_principal(self):
        def exercise(f):
            session = f.authority.open_session("other")
            result = f.broker.submit(session, f.root, f.send())
            self.assertEqual(result.state, State.REJECTED)
            self.assertEqual(f.service.effects(), ())
        self.each_arm(exercise)

    def test_user_name_is_not_an_authenticated_session(self):
        def exercise(f):
            self.assertEqual(f.broker.submit("owner", f.root, f.send()).state, State.REJECTED)
            self.assertEqual(f.service.effects(), ())
        self.each_arm(exercise)

    def test_evidence_witness_does_not_grant_action_authority(self):
        def exercise(f):
            result = f.broker.submit(f.session, f.witness, f.draft(), witness=f.witness)
            self.assertEqual(result.state, State.REJECTED)
            self.assertEqual(f.service.effects(), ())
        self.each_arm(exercise)

    def test_missing_evidence_preserves_draft(self):
        def exercise(f):
            result = f.broker.submit(f.session, f.root, f.draft())
            self.assertEqual(result.state, State.UNRESOLVED)
            self.assertEqual(f.service.snapshot("draft").content, "UNEDITED")
        self.each_arm(exercise)

    def test_send_cannot_attach_an_unchecked_alternate_payload(self):
        def exercise(f):
            action = replace(f.send(), artifact=f.artifact)
            self.assertEqual(f.broker.submit(f.session, f.root, action).state, State.REJECTED)
            self.assertEqual(f.service.effects(), ())
        self.each_arm(exercise)

    def test_repeated_effect_identifier_does_not_repeat_effect(self):
        def exercise(f):
            action = f.send()
            first = f.broker.submit(f.session, f.root, action)
            second = f.broker.submit(f.session, f.root, action)
            self.assertEqual(first, second)
            self.assertEqual(len(f.service.effects()), 1)
            self.assertEqual(sum(x.spent for x in f.broker.ledger.accounts().values()), 1)
            self.assertEqual(sum(x.kind == "ADMIT" for x in f.authority.events()), 1)
        self.each_arm(exercise)

    def test_reused_identifier_with_changed_request_is_rejected(self):
        def exercise(f):
            action = f.send()
            f.broker.submit(f.session, f.root, action)
            changed = replace(action, recipient="guest")
            self.assertEqual(f.broker.submit(f.session, f.root, changed).state, State.REJECTED)
            self.assertEqual(len(f.service.effects()), 1)
        self.each_arm(exercise)

    def test_stale_object_revision_is_rejected_before_admission(self):
        def exercise(f):
            action = f.send()
            f.service.replace_document("public", content="NEW")
            self.assertEqual(f.broker.submit(f.session, f.root, action).state, State.REJECTED)
            self.assertEqual(f.authority.events(), ())
        self.each_arm(exercise)

    def test_object_substitution_after_admission_cannot_change_checked_effect(self):
        def exercise(f):
            f.broker.before_dispatch = lambda _: f.service.replace_document("public",
                content="NEW", classification="PRIVATE")
            result = f.broker.submit(f.session, f.root, f.send())
            self.assertEqual(result.state, State.FAILED)
            self.assertEqual(f.service.effects(), ())
            self.assertTrue(all(x.spent == x.reserved == 0 for x in f.broker.ledger.accounts().values()))
        self.each_arm(exercise)

    def test_known_preacceptance_failure_releases_reservation(self):
        def exercise(f):
            action = f.send()
            f.service.inject_fault(action.effect_id, "FAIL_BEFORE_ACCEPT")
            result = f.broker.submit(f.session, f.root, action)
            self.assertEqual(result.state, State.FAILED)
            self.assertEqual(f.service.effects(), ())
            self.assertTrue(all(x.spent == x.reserved == 0 for x in f.broker.ledger.accounts().values()))
            self.assertEqual(f.broker.submit(f.session, f.root, f.send("next")).state,
                             State.CONFIRMED)
        self.each_arm(exercise)

    def test_timeout_after_acceptance_keeps_reservation_and_reconciles_once(self):
        def exercise(f):
            action = f.send()
            f.service.inject_fault(action.effect_id, "TIMEOUT_AFTER_ACCEPT")
            result = f.broker.submit(f.session, f.root, action)
            self.assertEqual(result.state, State.UNKNOWN)
            self.assertEqual(len(f.service.effects()), 1)
            self.assertTrue(all(x.spent == 0 and x.reserved == 1 for x in f.broker.ledger.accounts().values()))
            self.assertEqual(f.broker.submit(f.session, f.root, action).state, State.UNKNOWN)
            self.assertEqual(f.broker.reconcile(f.session, action.effect_id).state, State.CONFIRMED)
            self.assertEqual(f.broker.reconcile(f.session, action.effect_id).state, State.CONFIRMED)
            self.assertEqual(len(f.service.effects()), 1)
            self.assertTrue(all(x.spent == 1 and x.reserved == 0 for x in f.broker.ledger.accounts().values()))
        self.each_arm(exercise)

    def test_no_receipt_is_not_proof_of_no_effect(self):
        for arm in ARMS:
            with self.subTest(arm=arm.label):
                f = fresh(arm, budget=1)
                action = f.send()
                f.service.inject_fault(action.effect_id, "CRASH_BEFORE_ACCEPT")
                f.broker.submit(f.session, f.root, action)
                self.assertEqual(f.broker.reconcile(f.session, action.effect_id).state, State.UNKNOWN)
                self.assertEqual(f.broker.submit(f.session, f.root, f.send("next")).state, State.REJECTED)
                self.assertTrue(all(x.reserved == 1 for x in f.broker.ledger.accounts().values()))

    def test_revocation_does_not_prevent_reconciling_previous_effect(self):
        def exercise(f):
            action = f.send()
            f.service.inject_fault(action.effect_id, "TIMEOUT_AFTER_ACCEPT")
            f.broker.submit(f.session, f.root, action)
            f.authority.revoke(f.root)
            self.assertEqual(f.broker.reconcile(f.session, action.effect_id).state, State.CONFIRMED)
            self.assertEqual(f.broker.submit(f.session, f.root, f.send("next")).state, State.REJECTED)
            self.assertEqual(len(f.service.effects()), 1)
        self.each_arm(exercise)

    def test_another_principal_cannot_reconcile_owners_effect(self):
        def exercise(f):
            action = f.send()
            f.service.inject_fault(action.effect_id, "TIMEOUT_AFTER_ACCEPT")
            f.broker.submit(f.session, f.root, action)
            other = f.authority.open_session("other")
            self.assertEqual(f.broker.reconcile(other, action.effect_id).state, State.REJECTED)
            self.assertTrue(all(x.reserved == 1 for x in f.broker.ledger.accounts().values()))
        self.each_arm(exercise)

    def test_concurrent_replays_have_one_admission_and_one_effect(self):
        def exercise(f):
            action = f.send()
            with ThreadPoolExecutor(max_workers=8) as pool:
                results = list(pool.map(lambda _: f.broker.submit(f.session, f.root, action), range(24)))
            self.assertTrue(all(x.state in {State.ADMITTED, State.DISPATCHED, State.CONFIRMED} for x in results))
            self.assertEqual(len(f.service.effects()), 1)
            self.assertEqual(sum(x.kind == "ADMIT" for x in f.authority.events()), 1)
        self.each_arm(exercise)

    def test_charge_limit_cannot_be_lower_than_known_adapter_cost(self):
        def exercise(f):
            result = f.broker.submit(f.session, f.root, f.send(charge_limit=0))
            self.assertEqual(result.state, State.REJECTED)
            self.assertEqual(f.service.effects(), ())
        self.each_arm(exercise)

    def test_action_rejects_negative_boolean_fractional_and_nonfinite_limits(self):
        f = fresh()
        for value in (-1, True, 0.5, float("nan"), float("inf")):
            with self.subTest(value=value):
                with self.assertRaises(ValueError):
                    replace(f.send(), charge_limit=value)
                with self.assertRaises(ValueError):
                    replace(f.send(), expected_revision=value)

    def test_malformed_untyped_request_is_rejected_without_effect(self):
        f = fresh()
        result = f.broker.submit(f.session, f.root, {"operation": "send_document"})
        self.assertEqual(result.state, State.REJECTED)
        self.assertEqual(f.service.effects(), ())

    def test_malformed_reconciliation_identifier_is_rejected(self):
        f = fresh()
        for value in ({}, None, ""):
            self.assertEqual(f.broker.reconcile(f.session, value).state, State.REJECTED)

    def test_canonical_digest_handles_all_string_codepoints(self):
        f = fresh()
        self.assertEqual(len(digest(replace(f.send(), effect_id="\ud800"))), 64)


if __name__ == "__main__":
    unittest.main()
