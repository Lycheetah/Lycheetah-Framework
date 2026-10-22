"""Identity, time and encoding refusals in the action guard, gateway and finality gate.

Each refusal sits beside a control that must still pass, so a guard that refused
everything could not satisfy this file. Reproductions: FOR-REVIEW/2026-10-22_OPUS_REVIEW/
repro_batch3.py (B01b, B02, B02b, B03, B04, B06, B07, B10).
"""
from __future__ import annotations

import pytest

from lycheetah.assurance import ActionGateway, PersistentActionGuard
from lycheetah.assurance.finality import (
    EvidenceMode,
    EvidenceRecord,
    EvidenceRequirement,
    FinalityGate,
    MappingEvidenceStore,
)
from lycheetah.assurance.models import AssuranceEvent, Phase
from lycheetah.assurance.runtime import AssuranceRuntime

ACTOR, APPROVER, SCOPE = "executor", "reviewer", "deploy:staging"
ACTION = {"op": "deploy", "target": "staging"}
SIDE_EFFECT = {"tool": "deploy.release", "target": "staging", "side_effect": True}


@pytest.fixture
def guard(tmp_path):
    return PersistentActionGuard(tmp_path / "guard.sqlite3")


def _prepared(guard, approval_id="a1", effect_id="e1", at=100):
    assert guard.issue_approval(approval_id, ACTOR, APPROVER, ACTION, SCOPE, at, at + 100).allowed
    assert guard.prepare_effect(effect_id, approval_id, ACTOR, ACTION, SCOPE, at + 1).allowed
    return effect_id


def _ledger_sound(guard):
    return (guard.verify_audit_chain()["reason"], guard.verify_state_consistency()["reason"]) == ("ok", "ok")


# SQLite stores 100.5 as REAL (replay compares int(at)) and 100.0 as INTEGER 100
# (the event hash was taken over 100.0). Either one used to brick every later claim.
@pytest.mark.parametrize("issued", [100.5, 100.0, True, "100"])
def test_non_integer_time_is_refused_before_it_reaches_the_journal(guard, issued):
    refused = guard.issue_approval("bad", ACTOR, APPROVER, ACTION, SCOPE, issued, 200)
    assert (refused.allowed, refused.reason) == (False, "invalid_timestamp")
    effect = _prepared(guard)
    assert guard.claim_dispatch(effect, 102, ACTION, guard.audit_anchor()).reason == "dispatch_claimed"
    assert _ledger_sound(guard)


def test_every_mutation_refuses_a_float_time(guard):
    effect = _prepared(guard)
    assert guard.prepare_effect("e2", "a1", ACTOR, ACTION, SCOPE, 101.5).reason == "invalid_timestamp"
    assert guard.claim_dispatch(effect, 102.5, ACTION, guard.audit_anchor()).reason == "invalid_timestamp"
    assert guard.claim_dispatch(effect, 102, ACTION, guard.audit_anchor()).allowed
    assert guard.record_result(effect, 103.5, "success", {}).reason == "invalid_timestamp"
    assert guard.record_result(effect, 103, "unknown", {"provider": "timeout"}).allowed
    evidence = {"provider_read": "committed"}
    assert guard.reconcile_effect(effect, 104.5, "success", evidence).reason == "invalid_timestamp"
    assert guard.reconcile_effect(effect, 104, "success", evidence).allowed
    with pytest.raises(ValueError):
        guard.revoke_all(ACTOR, 105.5)
    assert guard.revoke_all(ACTOR, 105) >= 0
    assert _ledger_sound(guard)


# A TEXT column stores 5 as "5"; the event hash was taken over 5.
@pytest.mark.parametrize("field", ["approval_id", "actor", "approver_id", "scope"])
def test_identifiers_must_be_non_empty_strings(guard, field):
    args = dict(approval_id="a1", actor=ACTOR, approver_id=APPROVER, action=ACTION,
                scope=SCOPE, issued_at=100, expires_at=200)
    args[field] = 5
    assert guard.issue_approval(**args).reason == "invalid_approval"
    assert _ledger_sound(guard)


def test_executor_cannot_approve_its_own_action(guard):
    refused = guard.issue_approval("a1", ACTOR, ACTOR, ACTION, SCOPE, 100, 200)
    assert (refused.allowed, refused.reason) == (False, "approver_must_differ_from_actor")
    assert not guard.prepare_effect("e1", "a1", ACTOR, ACTION, SCOPE, 101).allowed
    assert guard.issue_approval("a2", ACTOR, APPROVER, ACTION, SCOPE, 100, 200).allowed


def test_unencodable_live_action_is_a_refusal_not_a_crash(guard):
    effect = _prepared(guard)
    refused = guard.claim_dispatch(effect, 102, {"op": float("nan")}, guard.audit_anchor())
    assert (refused.allowed, refused.reason) == (False, "invalid_live_action")
    assert guard.get_effect(effect)["status"] == "PREPARED"
    assert guard.claim_dispatch(effect, 103, ACTION, guard.audit_anchor()).reason == "dispatch_claimed"


def test_non_finite_result_is_refused_and_the_effect_stays_open(guard):
    effect = _prepared(guard)
    assert guard.claim_dispatch(effect, 102, ACTION, guard.audit_anchor()).allowed
    claimed = guard.get_effect(effect)["status"]
    refused = guard.record_result(effect, 103, "success", {"latency_ms": float("nan")})
    assert (refused.allowed, refused.reason) == (False, "invalid_result_details")
    assert guard.get_effect(effect)["status"] == claimed
    assert guard.record_result(effect, 104, "success", {"latency_ms": 1.0}).allowed
    assert _ledger_sound(guard)


def test_gateway_refuses_an_executor_approving_its_own_side_effect(tmp_path):
    gw = ActionGateway.open_local(tmp_path / "gw")
    calls = []

    def executor():
        calls.append(1)
        return {"status": "success"}

    own = gw.execute(SIDE_EFFECT, "agent", SCOPE, executor=executor, approver_id="agent")
    assert (own.status, own.reason, calls) == ("BLOCKED", "approver_must_differ_from_actor", [])
    other = gw.execute(SIDE_EFFECT, "agent", SCOPE, executor=executor, approver_id="reviewer")
    assert (other.status, calls) == ("SUCCEEDED", [1])


# A blank approver used to be prepared at propose and then denied at dispatch.
@pytest.mark.parametrize("approver", ["", "   ", "policy_auto_allow"])
def test_gateway_treats_a_blank_or_reserved_approver_as_none(tmp_path, approver):
    gw = ActionGateway.open_local(tmp_path / "gw")
    gate = gw.propose(SIDE_EFFECT, "agent", SCOPE, approver_id=approver)
    assert (gate.allowed, gate.reason) == (False, "human_approval_required")
    assert gw.propose(SIDE_EFFECT, "agent", SCOPE, approver_id="reviewer").allowed


# The guard journalled NaN, the checkpoint authority refused it, and every later
# action was blocked behind an uncheckpointed tail.
def test_gateway_non_finite_result_does_not_block_later_actions(tmp_path):
    gw = ActionGateway.open_local(tmp_path / "gw")
    first = gw.execute({"tool": "notes.write", "path": "a"}, "agent", "notes",
                       executor=lambda: {"status": "success", "latency_ms": float("nan")})
    assert first.status == "UNKNOWN"
    later = gw.execute({"tool": "notes.write", "path": "b"}, "agent", "notes",
                       executor=lambda: {"status": "success"})
    assert later.status == "SUCCEEDED"


@pytest.mark.parametrize(
    "later_subject, ready, reason",
    [
        ("commit-B", False, "evidence-subject-changed-after-admission"),
        ("commit-A", True, "fresh-evidence-and-current-policy"),
    ],
)
def test_subject_status_finality_stays_bound_to_the_admitted_subject(later_subject, ready, reason):
    store = MappingEvidenceStore([EvidenceRecord("ci", "run-1", "commit-A", "d1", "PASS")])
    gate = FinalityGate(AssuranceRuntime(), store)
    event = AssuranceEvent(phase=Phase.TOOL, tool_name="deploy.release",
                           tool_arguments={"commit": "commit-A"}, scopes=(SCOPE,))
    requirement = EvidenceRequirement("ci", EvidenceMode.SUBJECT_STATUS, required_status="PASS")
    admitted = gate.admit(event, [requirement])
    assert admitted.witness is not None
    store.put(EvidenceRecord("ci", "run-2", later_subject, "d2", "PASS"))
    final = gate.finalize(admitted.witness, event)
    assert (final.ready, final.reason) == (ready, reason)
