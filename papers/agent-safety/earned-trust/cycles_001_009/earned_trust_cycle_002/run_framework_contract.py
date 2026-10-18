"""Real Lycheetah-Framework contract tests — RUN ONLY WITH REPO IMPORTS AVAILABLE.

Example:
  cd /path/to/Lycheetah-Framework
  PYTHONPATH=. python /path/to/run_framework_contract.py

This suite imports the ACTUAL repo FinalityGate, AssuranceRuntime, and
PersistentActionGuard. No fake/stand-in Framework classes and no live API effects.
Tested syntax locally; execution requires checkout/installed Framework package.
"""
from __future__ import annotations
import json
from pathlib import Path
import sys
import tempfile
import unittest

try:
    from lycheetah.assurance.finality import (
        EvidenceMode, EvidenceRecord, EvidenceRequirement, FinalityGate, MappingEvidenceStore,
    )
    from lycheetah.assurance.action_guard import PersistentActionGuard
    from lycheetah.assurance.models import AssuranceEvent, Phase, Disposition
    from lycheetah.assurance.policy import AssurancePolicy
    from lycheetah.assurance.runtime import AssuranceRuntime
except ImportError as error:
    raise SystemExit(
        "REQUIRES REAL FRAMEWORK CHECKOUT OR INSTALL; NO TESTS RUN. "
        "Execute from the Lycheetah-Framework root with PYTHONPATH=. "
        f"Import error: {error}"
    ) from error


class RealFrameworkContract(unittest.TestCase):
    """Fixture boundaries are real Framework classes, simulated evidence/provider."""

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.action = {"actor": "agent", "subject": "ORDER-17", "amount_cents": 1200,
                       "scope": "refund:create"}
        self.policy = AssurancePolicy(
            policy_id="earned-trust.contract", version="1.0.0",
            tool_allowlist=("refund.create",), require_approval_for_side_effects=True,
        )
        self.runtime = AssuranceRuntime(policy=self.policy)
        self.event = AssuranceEvent(
            phase=Phase.TOOL, tool_name="refund.create", tool_arguments=self.action,
            scopes=("refund:create",), side_effect=True, human_approved=True,
            event_id="fixed-proposal-1", trace_id="fixed-trace-1",
        )
        self.store = MappingEvidenceStore([
            EvidenceRecord("eligibility:ORDER-17", "1", "subject-hash:ORDER-17", "digest:1", "PASS")
        ])
        self.gate = FinalityGate(self.runtime, self.store)
        self.requirement = EvidenceRequirement(
            key="eligibility:ORDER-17", mode=EvidenceMode.SUBJECT_STATUS,
            required_status="PASS", required_subject_hash="subject-hash:ORDER-17",
        )
        self.guard = PersistentActionGuard(Path(self.temp.name) / "guard.sqlite")

    def admit(self, requirement=None):
        admission = self.gate.admit(self.event, (requirement or self.requirement,))
        self.assertEqual(admission.disposition, Disposition.ALLOW)
        self.assertIsNotNone(admission.witness)
        return admission.witness

    def _approved_effect(self):
        self.assertTrue(self.guard.issue_approval(
            "a1", "agent", "actual-human", self.action, "refund:create", 100, 200
        ).allowed)
        self.assertTrue(self.guard.prepare_effect(
            "e1", "a1", "agent", self.action, "refund:create", 110
        ).allowed)

    def test_00_action_hash_agrees_with_local_provider_format(self):
        from binding_contract import verify_action_binding
        from transactional_provider import Intent
        from lycheetah.assurance.action_guard import action_digest
        intent = Intent("e1", "a1", "agent", "ORDER-17", 1200)
        result = verify_action_binding(self.event.tool_arguments, self.action, intent)
        self.assertTrue(result.valid, result.reason)
        self.assertEqual(action_digest(self.action), result.action_sha256)

    def test_01_admission_and_finality_on_original_evidence(self):
        w = self.admit()
        finality = self.gate.finalize(w, self.event)
        self.assertTrue(finality.ready, finality.reason)

    def test_02_fail_evidence_at_finality(self):
        w = self.admit()
        self.store.put(EvidenceRecord("eligibility:ORDER-17", "2", "subject-hash:ORDER-17", "digest:2", "FAIL"))
        finality = self.gate.finalize(w, self.event)
        self.assertFalse(finality.ready)
        self.assertEqual(finality.disposition, Disposition.REVIEW)

    def test_03_wrong_subject_after_admission(self):
        w = self.admit()
        self.store.put(EvidenceRecord("eligibility:ORDER-17", "2", "WRONG-SUBJECT", "digest:2", "PASS"))
        finality = self.gate.finalize(w, self.event)
        self.assertFalse(finality.ready)

    def test_04_benign_status_revision_allowed(self):
        w = self.admit()
        self.store.put(EvidenceRecord("eligibility:ORDER-17", "2", "subject-hash:ORDER-17", "digest:2", "PASS"))
        self.assertTrue(self.gate.finalize(w, self.event).ready)

    def test_05_exact_revision_rejected(self):
        exact = EvidenceRequirement("eligibility:ORDER-17", EvidenceMode.EXACT, "PASS", "subject-hash:ORDER-17")
        w = self.admit(exact)
        self.store.put(EvidenceRecord("eligibility:ORDER-17", "2", "subject-hash:ORDER-17", "digest:2", "PASS"))
        self.assertFalse(self.gate.finalize(w, self.event).ready)

    def test_06_event_substitution_rejected(self):
        w = self.admit()
        changed = AssuranceEvent(
            phase=Phase.TOOL, tool_name="refund.create", tool_arguments={"subject":"ORDER-17", "amount_cents":1300},
            scopes=("refund:create",), side_effect=True, human_approved=True,
            event_id="fixed-proposal-1", trace_id="fixed-trace-1",
        )
        self.assertEqual(self.gate.finalize(w, changed).reason, "event-changed-after-admission")

    def test_07_policy_revision_rejected(self):
        w = self.admit()
        self.runtime.policy = AssurancePolicy(
            policy_id="earned-trust.contract", version="2.0.0",
            tool_allowlist=("refund.create",), require_approval_for_side_effects=True,
        )
        self.assertEqual(self.gate.finalize(w, self.event).reason, "policy-changed-after-admission")

    def test_08_ledger_dispatch_single_use(self):
        self._approved_effect()
        anchor = self.guard.audit_anchor()
        first = self.guard.claim_dispatch("e1", 115, self.action, expected_audit_anchor=anchor)
        self.assertTrue(first.allowed, first.reason)
        next_anchor = self.guard.audit_anchor()
        second = self.guard.claim_dispatch("e1", 116, self.action, expected_audit_anchor=next_anchor)
        self.assertFalse(second.allowed)

    def test_09_revoke_before_claim_refused(self):
        self._approved_effect()
        self.guard.revoke_all("agent", now=113)
        anchor = self.guard.audit_anchor()
        denied = self.guard.claim_dispatch("e1", 115, self.action, expected_audit_anchor=anchor)
        self.assertFalse(denied.allowed)

    def test_10_payload_swap_at_claim_refused(self):
        self._approved_effect()
        anchor = self.guard.audit_anchor()
        denied = self.guard.claim_dispatch("e1", 115, {"subject":"ORDER-17", "amount_cents":1300},
                                            expected_audit_anchor=anchor)
        self.assertFalse(denied.allowed)

    def test_11_unknown_outcome_needs_reconciliation(self):
        self._approved_effect()
        anchor = self.guard.audit_anchor()
        self.assertTrue(self.guard.claim_dispatch("e1", 115, self.action, expected_audit_anchor=anchor).allowed)
        self.assertTrue(self.guard.record_result("e1", 116, "unknown", {"provider":"timeout"}).allowed)
        self.assertEqual(self.guard.get_effect("e1")["status"], "UNKNOWN")
        self.assertFalse(self.guard.claim_dispatch("e1", 117, self.action,
                                                 expected_audit_anchor=self.guard.audit_anchor()).allowed)
        rec = self.guard.reconcile_effect("e1", 118, "success", {"provider_read":"committed"})
        self.assertTrue(rec.allowed, rec.reason)
        self.assertEqual(self.guard.get_effect("e1")["status"], "SUCCEEDED")

    def test_12_anchor_required(self):
        self._approved_effect()
        result = self.guard.claim_dispatch("e1", 115, self.action)
        self.assertFalse(result.allowed)
        self.assertEqual(result.reason, "trusted_audit_anchor_required")

    def test_13_reopen_durable_guard(self):
        self._approved_effect()
        reopened = PersistentActionGuard(Path(self.temp.name) / "guard.sqlite")
        self.assertEqual(reopened.get_effect("e1")["status"], "PREPARED")
        self.assertTrue(reopened.verify_audit_chain()["valid"])

    def test_14_composed_pre_dispatch_pass(self):
        # Joined HERE at the caller boundary: still NOT an atomic remote write.
        w = self.admit()
        self._approved_effect()
        finality = self.gate.finalize(w, self.event)
        self.assertTrue(finality.ready)
        dispatch = self.guard.claim_dispatch("e1", 115, self.action, expected_audit_anchor=self.guard.audit_anchor())
        self.assertTrue(dispatch.allowed)
        # No payment provider is invoked. A remote write would be a separate trust boundary.

    def test_15_composed_evidence_revocation_pauses(self):
        w = self.admit()
        self._approved_effect()
        self.store.put(EvidenceRecord("eligibility:ORDER-17", "2", "subject-hash:ORDER-17", "digest:2", "FAIL"))
        self.assertFalse(self.gate.finalize(w, self.event).ready)
        self.assertEqual(self.guard.get_effect("e1")["status"], "PREPARED")



    def test_16_local_revoke_after_claim_does_not_reach_unlinked_provider(self):
        # NEGATIVE CONTROL: guard and mock remote authority have separate state.
        # Not proof of a Framework flaw: the integration has no common authority link.
        from transactional_provider import ConditionalRefundProvider, Intent
        w = self.admit()
        self._approved_effect()
        self.assertTrue(self.gate.finalize(w, self.event).ready)
        self.assertTrue(self.guard.claim_dispatch("e1", 115, self.action,
                       expected_audit_anchor=self.guard.audit_anchor()).allowed)
        remote = ConditionalRefundProvider(Path(self.temp.name) / "other-authority.sqlite")
        intent = Intent("e1", "a1", "agent", "ORDER-17", 1200)
        remote.seed(intent)
        self.guard.revoke_all("agent", now=116)
        # Independent provider has NOT received revocation. It accepts the write.
        self.assertTrue(remote.commit(intent, now=117).committed)
        self.assertEqual(remote.effect_count(), 1)

    def test_17_propagated_revoke_refused_at_remote_commit(self):
        from transactional_provider import ConditionalRefundProvider, Intent
        self._approved_effect()
        self.assertTrue(self.guard.claim_dispatch("e1", 115, self.action,
                       expected_audit_anchor=self.guard.audit_anchor()).allowed)
        remote = ConditionalRefundProvider(Path(self.temp.name) / "other-authority.sqlite")
        intent = Intent("e1", "a1", "agent", "ORDER-17", 1200)
        remote.seed(intent)
        self.guard.revoke_all("agent", now=116)
        remote.change(actor="agent", revoke=True)
        self.assertEqual(remote.commit(intent, now=117).code, "REVOKED")
        self.assertEqual(remote.effect_count(), 0)

if __name__ == "__main__":
    print("REAL FRAMEWORK IMPORTS RESOLVED — running verified implementation contracts", flush=True)
    unittest.main(verbosity=2)
