"""Portable contract tests. Local FakeFence is NOT upstream CommitFence.
To test actual upstream run test_real_upstream.py inside a repo checkout.
"""
import hashlib
import json
import tempfile
import threading
import unittest
from dataclasses import dataclass
from pathlib import Path
from types import SimpleNamespace

from intent_bridge import IntentAuthorityBridge
from epistemic_boundary import assess


@dataclass(frozen=True)
class Action:
    principal: str
    effect_id: str
    target: str
    body: str

    @property
    def action_hash(self):
        raw = json.dumps(self.__dict__, sort_keys=True, separators=(",", ":"))
        return hashlib.sha256(raw.encode()).hexdigest()


class FakeFence:
    """Minimal concurrency-safe surrogate matching published upstream method shapes."""
    def __init__(self):
        self.lock = threading.RLock()
        self.scopes = {}
        self.handles = {}
        self.effects = {}
        self.on_issue = None
        self.fail_activate = False

    def state(self, principal, scope_key):
        with self.lock:
            v = self.scopes.get((principal, scope_key))
            return dict(v) if v is not None else None

    def revoke(self, principal, scope_key):
        with self.lock:
            key = (principal, scope_key)
            gen = self.scopes.get(key, {"generation": 0})["generation"] + 1
            self.scopes[key] = {"generation": gen, "active": False}
            return SimpleNamespace(generation=gen, state="REVOKED")

    def activate(self, principal, scope_key):
        if self.fail_activate:
            raise RuntimeError("injected activation failure")
        with self.lock:
            key = (principal, scope_key)
            gen = self.scopes.get(key, {"generation": 0})["generation"] + 1
            self.scopes[key] = {"generation": gen, "active": True}
            return SimpleNamespace(generation=gen, state="ACTIVE")

    def issue_handle(self, principal, scope_key, action):
        if self.on_issue is not None:
            cb, self.on_issue = self.on_issue, None
            cb()
        with self.lock:
            state = self.scopes.get((principal, scope_key))
            if not state or not state["active"]:
                return None, SimpleNamespace(reason="authority-inactive")
            handle_id = "h" + str(len(self.handles) + 1)
            self.handles[handle_id] = (principal, scope_key, state["generation"], action.action_hash)
            return SimpleNamespace(handle_id=handle_id, generation=state["generation"]), SimpleNamespace(reason="issued")

    def commit(self, handle_id, action):
        with self.lock:
            handle = self.handles.get(handle_id)
            if handle is None:
                return SimpleNamespace(state="DENY", reason="unknown-handle")
            p,s,gen,h = handle
            current = self.scopes.get((p,s))
            if action.effect_id in self.effects:
                return SimpleNamespace(state="CONFIRMED", reason="idempotent-existing-effect")
            if not current or not current["active"] or current["generation"] != gen:
                return SimpleNamespace(state="DENY", reason="stale-generation")
            if h != action.action_hash:
                return SimpleNamespace(state="DENY", reason="action-substitution")
            self.effects[action.effect_id] = h
            return SimpleNamespace(state="COMMITTED", reason="effect-committed")


class BridgeTests(unittest.TestCase):
    def setUp(self):
        self.t = tempfile.TemporaryDirectory()
        self.addCleanup(self.t.cleanup)
        self.path = Path(self.t.name)/"journal.sqlite"
        self.fence = FakeFence()
        self.bridge = IntentAuthorityBridge(self.fence, self.path)
        self.a = Action("alice", "e1", "person@sample.test", "draft 1")
        self.b = Action("alice", "e2", "person@sample.test", "draft 2")

    def grant(self, action=None):
        return self.bridge.grant("alice", "email", "Send approved email", action or self.a)

    def test_no_initial_grant(self):
        self.assertEqual(self.bridge.issue("alice", "email", self.a).reason, "no_active_endorsement")

    def test_normal_commit(self):
        self.grant()
        ticket = self.bridge.issue("alice", "email", self.a)
        self.assertTrue(ticket.allowed)
        self.assertEqual(self.bridge.commit(ticket.handle, self.a).state, "COMMITTED")

    def test_changed_intention_denies_stale_handle(self):
        self.grant()
        ticket = self.bridge.issue("alice", "email", self.a)
        self.bridge.grant("alice", "email", "Revised", self.b, reason_class="changed_mind")
        self.assertEqual(self.bridge.commit(ticket.handle, self.a).state, "DENY")
        self.assertEqual(self.bridge.issue("alice", "email", self.a).reason, "action_not_endorsed")
        fresh = self.bridge.issue("alice", "email", self.b)
        self.assertTrue(fresh.allowed)
        self.assertEqual(self.bridge.commit(fresh.handle, self.b).state, "COMMITTED")

    def test_withdraw_does_not_require_reason(self):
        self.grant()
        handle = self.bridge.issue("alice", "email", self.a).handle
        result = self.bridge.withdraw("alice", "email")
        self.assertFalse(result.active)
        self.assertEqual(self.bridge.commit(handle, self.a).state, "DENY")

    def test_revision_without_work_cannot_commit_old_action(self):
        self.grant()
        self.bridge.grant("alice", "email", "new plan", self.b)
        self.assertFalse(self.bridge.issue("alice", "email", self.a).allowed)

    def test_old_generation_not_restored_on_regrant(self):
        self.grant()
        original = self.bridge.issue("alice", "email", self.a).handle
        self.bridge.withdraw("alice", "email")
        self.grant()
        self.assertEqual(self.bridge.commit(original, self.a).state, "DENY")

    def test_existing_committed_effect_not_undone(self):
        self.grant()
        first = self.bridge.issue("alice", "email", self.a).handle
        self.assertEqual(self.bridge.commit(first, self.a).state, "COMMITTED")
        self.bridge.withdraw("alice", "email")
        self.assertEqual(len(self.fence.effects), 1)
        self.assertEqual(self.bridge.commit(first, self.a).state, "CONFIRMED")
        self.assertEqual(len(self.fence.effects), 1)

    def test_different_target_is_not_same_approval(self):
        self.grant()
        alternate = Action("alice", "e1", "wrong@sample.test", "draft 1")
        self.assertEqual(self.bridge.issue("alice", "email", alternate).reason, "action_not_endorsed")

    def test_different_payload_is_not_same_approval(self):
        self.grant()
        alternate = Action("alice", "e1", "person@sample.test", "changed body")
        self.assertEqual(self.bridge.issue("alice", "email", alternate).reason, "action_not_endorsed")

    def test_another_principal_isolated(self):
        self.grant()
        other = Action("bob", "e3", "person@sample.test", "draft 1")
        self.assertEqual(self.bridge.issue("bob", "email", other).reason, "no_active_endorsement")

    def test_scope_isolated(self):
        self.grant()
        self.assertEqual(self.bridge.issue("alice", "payments", self.a).reason, "no_active_endorsement")

    def test_version_across_restart(self):
        self.grant()
        other = IntentAuthorityBridge(self.fence, self.path)
        other.grant("alice", "email", "Revision", self.b)
        self.assertEqual(self.bridge.current("alice", "email").version, 2)

    def test_version_advanced_on_withdraw(self):
        self.grant()
        self.bridge.withdraw("alice", "email")
        self.assertEqual(self.bridge.current("alice", "email").version, 2)

    def test_generation_mismatch_fails_closed(self):
        self.grant()
        self.fence.revoke("alice", "email")
        self.assertEqual(self.bridge.issue("alice", "email", self.a).reason, "generation_not_current")

    def test_activation_failure_fails_closed(self):
        self.grant()
        self.fence.fail_activate = True
        with self.assertRaises(RuntimeError):
            self.bridge.grant("alice", "email", "New plan", self.b)
        self.assertEqual(self.bridge.issue("alice", "email", self.a).reason, "generation_not_current")

    def test_revision_mid_issue_blocks_new_generation_leak(self):
        self.grant()
        other = IntentAuthorityBridge(self.fence, self.path)
        self.fence.on_issue = lambda: other.grant("alice", "email", "revised", self.b)
        result = self.bridge.issue("alice", "email", self.a)
        self.assertFalse(result.allowed)
        self.assertEqual(result.reason, "changed_during_issue")

    def test_two_process_style_journal_serializes_versions(self):
        self.grant()
        a2 = IntentAuthorityBridge(self.fence, self.path)
        errors = []
        def advance(br, act):
            try:
                br.grant("alice", "email", "revision", act)
            except Exception as e:
                errors.append(str(e))
        th1 = threading.Thread(target=advance, args=(self.bridge,self.b))
        th2 = threading.Thread(target=advance, args=(a2,self.a))
        th1.start(); th2.start(); th1.join(); th2.join()
        self.assertFalse(errors)
        self.assertEqual(self.bridge.current("alice", "email").version, 3)
        self.assertEqual(self.bridge.current("alice", "email").generation,
                         self.fence.state("alice", "email")["generation"])

    def test_journal_events_do_not_require_private_explanation(self):
        self.grant()
        self.bridge.withdraw("alice", "email")
        history = self.bridge.event_history()
        self.assertEqual(history[-1]["reason_class"], "not_required")
        self.assertNotIn("private_reason", history[-1])

    def test_bad_payload_hash(self):
        with self.assertRaises(ValueError):
            self.grant(SimpleNamespace(action_hash="untrusted"))

    def test_missing_principal_rejected(self):
        with self.assertRaises(ValueError):
            self.bridge.grant(" ", "email", "p", self.a)

    def test_partial_grant_denies_if_activation_not_complete(self):
        self.grant()
        self.fence.revoke("alice", "email")
        # Current ledger still says active, generation mismatch prevents issuance.
        self.assertFalse(self.bridge.issue("alice", "email", self.a).allowed)

    def test_observed_compliance_not_metaphysical_freedom(self):
        result = assess(followed_original_plan=True, current_grant_valid=True,
                        action_inside_grant=True, identity_verified=True)
        self.assertEqual(result.metaphysical_free_will, "UNRESOLVED")
        self.assertIsNone(result.human_worth_score)

    def test_recorded_grant_not_informed_consent(self):
        result = assess(followed_original_plan=True, current_grant_valid=True,
                        action_inside_grant=True, identity_verified=False)
        self.assertFalse(result.observed_execution_authorised)
        self.assertTrue(result.grant_recorded)
        self.assertTrue(result.comprehension_verified.startswith("UNKNOWN"))

    def test_revised_plan_not_lack_of_free_will(self):
        result = assess(followed_original_plan=False, current_grant_valid=True,
                        action_inside_grant=True, identity_verified=True)
        self.assertTrue(result.observed_execution_authorised)
        self.assertFalse(result.plan_adherence)
        self.assertEqual(result.coercion_absent, "UNKNOWN (no inference from compliance)")

if __name__ == "__main__":
    unittest.main()
