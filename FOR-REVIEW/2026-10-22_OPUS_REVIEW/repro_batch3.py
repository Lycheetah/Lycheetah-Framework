"""Batch 3 reproductions: the persistent action guard (RV04).

Run from the repository root:  python3 FOR-REVIEW/2026-10-22_OPUS_REVIEW/repro_batch3.py

Each probe returns a dict with a `reproduced` flag, and the guard's own
verdicts beside it. A benign control runs next to each defect probe and must
not reproduce. Every database lives in a temporary directory.
"""

from __future__ import annotations

import json
import sqlite3
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from lycheetah.assurance.action_guard import PersistentActionGuard  # noqa: E402

ACTOR, APPROVER, SCOPE = "executor", "mac", "deploy:staging"
ACTION = {"op": "deploy", "target": "staging"}


def _guard(tmp):
    return PersistentActionGuard(Path(tmp) / "guard.db")


def _approve(g, approval_id, issued=100, expires=200, approver=APPROVER):
    return g.issue_approval(approval_id, ACTOR, approver, ACTION, SCOPE, issued, expires)


def _dispatched(g, approval_id, effect_id, at):
    _approve(g, approval_id, issued=at)
    g.prepare_effect(effect_id, approval_id, ACTOR, ACTION, SCOPE, at + 1)
    return g.claim_dispatch(effect_id, at + 2, ACTION, g.audit_anchor())


def provider_result_bricks_ledger(value):
    """A non-finite number in a provider result breaks journal replay for every effect."""
    with tempfile.TemporaryDirectory() as tmp:
        g = _guard(tmp)
        _dispatched(g, "a1", "e1", 100)
        recorded = g.record_result("e1", 103, "success", {"latency_ms": value})
        _approve(g, "a2", issued=104)
        g.prepare_effect("e2", "a2", ACTOR, ACTION, SCOPE, 105)
        state = g.verify_state_consistency()
        claim = g.claim_dispatch("e2", 106, ACTION, g.audit_anchor())
        return {"recorded": recorded.reason, "state": state["reason"],
                "unrelated_claim": claim.reason,
                "reproduced": claim.reason == "ledger_state_inconsistent"}


def fractional_time_bricks_ledger(issued):
    """A float timestamp is accepted at issuance and then breaks replay or the hash chain.

    SQLite keeps 100.5 as REAL (replay compares int(at) and fails) and stores 100.0
    as INTEGER 100 (the hash was taken over 100.0, so the chain no longer verifies).
    """
    with tempfile.TemporaryDirectory() as tmp:
        g = _guard(tmp)
        issued_decision = g.issue_approval("a1", ACTOR, APPROVER, ACTION, SCOPE, issued, 200)
        _approve(g, "a2")
        g.prepare_effect("e2", "a2", ACTOR, ACTION, SCOPE, 110)
        chain = g.verify_audit_chain()
        state = g.verify_state_consistency()
        try:
            claim = g.claim_dispatch("e2", 111, ACTION, g.audit_anchor()).reason
        except RuntimeError as exc:
            claim = f"raised: {exc}"
        return {"issued": issued_decision.reason, "chain": chain["reason"],
                "state": state["reason"], "unrelated_claim": claim,
                "reproduced": issued_decision.allowed and claim != "dispatch_claimed"}


def non_string_identity_breaks_chain(actor):
    """A TEXT column stores 5 as "5"; the event hash was taken over 5."""
    with tempfile.TemporaryDirectory() as tmp:
        g = _guard(tmp)
        issued = g.issue_approval("a1", actor, APPROVER, ACTION, SCOPE, 100, 200)
        chain = g.verify_audit_chain()
        return {"actor": repr(actor), "issued": issued.reason, "chain": chain["reason"],
                "reproduced": issued.allowed and not chain["valid"]}


def self_approval(approver):
    """The docstring promises a distinct approver; the executor can approve itself."""
    with tempfile.TemporaryDirectory() as tmp:
        g = _guard(tmp)
        issued = _approve(g, "a1", approver=approver)
        g.prepare_effect("e1", "a1", ACTOR, ACTION, SCOPE, 110)
        claim = g.claim_dispatch("e1", 111, ACTION, g.audit_anchor())
        return {"approver": approver, "issued": issued.reason, "claim": claim.reason,
                "reproduced": approver == ACTOR and claim.allowed}


def unserialisable_live_action():
    """claim_dispatch raises instead of returning a refusal for an unencodable live action."""
    with tempfile.TemporaryDirectory() as tmp:
        g = _guard(tmp)
        _approve(g, "a1")
        g.prepare_effect("e1", "a1", ACTOR, ACTION, SCOPE, 110)
        try:
            outcome = g.claim_dispatch("e1", 111, {"op": float("nan")}, g.audit_anchor()).reason
        except Exception as exc:  # the probe reports the raise, it does not hide it
            outcome = f"raised {type(exc).__name__}"
        return {"claim": outcome, "status_after": g.get_effect("e1")["status"],
                "reproduced": outcome.startswith("raised")}


def stale_anchor_replay(fresh_anchor):
    """A database writer truncates the journal tail and re-dispatches a finished effect.

    With an anchor taken before the first dispatch the replay passes every check.
    With an anchor taken after the result, the truncation is detected.
    """
    with tempfile.TemporaryDirectory() as tmp:
        g = _guard(tmp)
        _approve(g, "a1")
        g.prepare_effect("e1", "a1", ACTOR, ACTION, SCOPE, 110)
        stale = g.audit_anchor()
        first = g.claim_dispatch("e1", 111, ACTION, stale)
        g.record_result("e1", 112, "success", {"ok": True})
        anchor = g.audit_anchor() if fresh_anchor else stale
        with sqlite3.connect(g.db_path) as c:
            c.execute("DELETE FROM audit WHERE seq>?", (stale["last_seq"],))
            c.execute("UPDATE sqlite_sequence SET seq=? WHERE name='audit'", (stale["last_seq"],))
            c.execute("UPDATE effects SET status='PREPARED', updated_at=created_at, "
                      "result_json=NULL, reason=NULL WHERE effect_id='e1'")
        second = g.claim_dispatch("e1", 113, ACTION, anchor)
        return {"anchor": "after result" if fresh_anchor else "before dispatch",
                "first": first.reason, "replay": second.reason,
                "reproduced": second.allowed}


def expiry_window(prepare_at, claim_at):
    """Approval issued at 100, expiring at 200: preparing or claiming outside it must fail."""
    with tempfile.TemporaryDirectory() as tmp:
        g = _guard(tmp)
        _approve(g, "a1")
        prep = g.prepare_effect("e1", "a1", ACTOR, ACTION, SCOPE, prepare_at)
        claim = g.claim_dispatch("e1", claim_at, ACTION, g.audit_anchor()) if prep.allowed else None
        outside = not (100 <= prepare_at < 200 and 100 <= claim_at < 200)
        return {"prepare_at": prepare_at, "claim_at": claim_at, "prepare": prep.reason,
                "claim": claim and claim.reason,
                "reproduced": outside and claim is not None and claim.allowed}


def substitution(kind):
    """Change one bound field between approval, preparation and dispatch."""
    other = {"op": "deploy", "target": "production"}
    with tempfile.TemporaryDirectory() as tmp:
        g = _guard(tmp)
        _approve(g, "a1")
        actor = "intruder" if kind == "actor" else ACTOR
        scope = "deploy:production" if kind == "scope" else SCOPE
        action = other if kind == "action" else ACTION
        live = other if kind == "live action" else ACTION
        prep = g.prepare_effect("e1", "a1", actor, action, scope, 110)
        claim = g.claim_dispatch("e1", 111, live, g.audit_anchor()) if prep.allowed else None
        return {"changed": kind, "prepare": prep.reason, "claim": claim and claim.reason,
                "reproduced": kind != "nothing" and claim is not None and claim.allowed}


def approval_reuse():
    """One approval, two effects: the second preparation must be refused."""
    with tempfile.TemporaryDirectory() as tmp:
        g = _guard(tmp)
        _approve(g, "a1")
        first = g.prepare_effect("e1", "a1", ACTOR, ACTION, SCOPE, 110)
        second = g.prepare_effect("e2", "a1", ACTOR, ACTION, SCOPE, 111)
        return {"first": first.reason, "second": second.reason, "reproduced": second.allowed}


def revocation_timing(when):
    """Revocation must stop a prepared effect; it cannot recall one already dispatched."""
    with tempfile.TemporaryDirectory() as tmp:
        g = _guard(tmp)
        _approve(g, "a1")
        g.prepare_effect("e1", "a1", ACTOR, ACTION, SCOPE, 110)
        if when == "before claim":
            g.revoke_all(ACTOR, 111)
        claim = g.claim_dispatch("e1", 112, ACTION, g.audit_anchor())
        recorded = None
        if when == "after claim":
            g.revoke_all(ACTOR, 113)
            recorded = g.record_result("e1", 114, "success", {"ok": True}).reason
        fresh = _approve(g, "a2", issued=115, expires=300)
        return {"revoked": when, "claim": claim.reason, "result_after_revoke": recorded,
                "new_approval_after_revoke": fresh.reason,
                "reproduced": when == "before claim" and claim.allowed}


def _gateway(tmp):
    from lycheetah.assurance.gateway import ActionGateway

    return ActionGateway.open_local(Path(tmp) / "gw")


def gateway_self_approval(approver):
    """A side-effecting action needs approval; the gateway accepts any declared approver."""
    with tempfile.TemporaryDirectory() as tmp:
        gw = _gateway(tmp)
        action = {"tool": "deploy.release", "target": "staging", "side_effect": True}
        result = gw.execute(action, "agent", "deploy:staging",
                            executor=lambda: {"status": "success"}, approver_id=approver)
        return {"approver": approver, "status": result.status, "reason": result.reason,
                "reproduced": approver == "agent" and result.status == "SUCCEEDED"}


def gateway_empty_approver():
    """An empty approver passes propose as approved, then dispatch treats it as absent."""
    with tempfile.TemporaryDirectory() as tmp:
        gw = _gateway(tmp)
        action = {"tool": "deploy.release", "target": "staging", "side_effect": True}
        gate = gw.propose(action, "agent", "deploy:staging", approver_id="")
        result = gw.dispatch(gate.effect_id, lambda: {"status": "success"}) if gate.allowed else None
        return {"propose": gate.reason, "dispatch": result and result.reason,
                "reproduced": gate.allowed and result is not None and result.status == "DENIED"}


def gateway_command_screen():
    """Propose only, never dispatch: what the substring screen blocks and lets through."""
    commands = ["rm -rf /", "rm -r -f /", "rm -fr /", "find / -delete", "rm -rf /tmp/build-cache"]
    with tempfile.TemporaryDirectory() as tmp:
        gw = _gateway(tmp)
        out = {c: gw.propose({"command": c}, "agent", "ops").reason for c in commands}
    passed = [c for c in commands[1:4] if out[c] == "prepared"]
    return {"verdicts": out, "destructive_prepared": passed,
            "false_positive": out["rm -rf /tmp/build-cache"] == "policy_blocked",
            "reproduced": bool(passed)}


def gateway_unencodable_result():
    """The provider ran, its result cannot be stored, and dispatch raises instead of UNKNOWN."""
    with tempfile.TemporaryDirectory() as tmp:
        gw = _gateway(tmp)
        calls = []

        def executor():
            calls.append(1)
            return {"status": "success", "handle": object()}

        try:
            result = gw.execute({"tool": "notes.write"}, "agent", "notes", executor=executor)
            outcome = f"{result.status}:{result.reason}"
        except Exception as exc:  # reported, not hidden
            outcome = f"raised {type(exc).__name__}"
        effects = gw.guard.audit_events()
        return {"provider_calls": len(calls), "outcome": outcome,
                "last_event": effects[-1]["event"] if effects else None,
                "reproduced": bool(calls) and outcome.startswith("raised")}


def gateway_nonfinite_result(latency):
    """The guard journals NaN; the checkpoint authority refuses it; every later action blocks."""
    with tempfile.TemporaryDirectory() as tmp:
        gw = _gateway(tmp)
        first = gw.execute({"tool": "notes.write", "path": "a"}, "agent", "notes",
                           executor=lambda: {"status": "success", "latency_ms": latency})
        later = gw.execute({"tool": "notes.write", "path": "b"}, "agent", "notes",
                           executor=lambda: {"status": "success"})
        return {"latency": repr(latency), "first": f"{first.status}:{first.reason}",
                "later_unrelated": f"{later.status}:{later.reason}",
                "reproduced": later.status != "SUCCEEDED"}


def gateway_colocated_authority_replay(roll_back_authority):
    """open_local keeps the signing key and checkpoint store beside the ledger.

    Truncating the ledger alone is caught by the signed checkpoint. A writer who
    can also delete the newest checkpoint rows rolls the authority back with it.
    """
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp) / "gw"
        gw = _gateway(tmp)
        calls = []

        def executor():
            calls.append(1)
            return {"status": "success"}

        gate = gw.propose({"tool": "notes.write", "path": "a.txt"}, "agent", "notes")
        anchor = gw.guard.audit_anchor()
        generation = gw._get_latest_checkpoint()["generation"]
        first = gw.dispatch(gate.effect_id, executor)
        with sqlite3.connect(root / "ledger" / "guard.sqlite3") as c:
            c.execute("DELETE FROM audit WHERE seq>?", (anchor["last_seq"],))
            c.execute("UPDATE sqlite_sequence SET seq=? WHERE name='audit'", (anchor["last_seq"],))
            c.execute("UPDATE effects SET status='PREPARED', updated_at=created_at, "
                      "result_json=NULL, reason=NULL WHERE effect_id=?", (gate.effect_id,))
        if roll_back_authority:
            with sqlite3.connect(root / "authority" / "authority.sqlite3") as c:
                c.execute("DELETE FROM checkpoint_history WHERE generation>?", (generation,))
        try:
            second = gw.dispatch(gate.effect_id, executor)
            replay = f"{second.status}:{second.reason}"
        except Exception as exc:
            replay = f"raised {type(exc).__name__}: {exc}"
        return {"authority_rolled_back": roll_back_authority, "first": first.status,
                "replay": replay, "provider_calls": len(calls),
                "reproduced": len(calls) == 2}


def finality_subject_swap(bind_subject):
    """Finality accepts a PASS about a different subject unless the requirement pins one."""
    from lycheetah.assurance.finality import (EvidenceRecord, EvidenceRequirement,
                                              FinalityGate, MappingEvidenceStore)
    from lycheetah.assurance.models import AssuranceEvent, Phase
    from lycheetah.assurance.runtime import AssuranceRuntime

    store = MappingEvidenceStore([EvidenceRecord("ci", "run-1", "commit-A", "d1", "PASS")])
    gate = FinalityGate(AssuranceRuntime(), store)
    event = AssuranceEvent(phase=Phase.TOOL, tool_name="deploy.release",
                           tool_arguments={"commit": "commit-A"}, scopes=("deploy:staging",))
    requirement = EvidenceRequirement("ci", required_subject_hash="commit-A" if bind_subject else None)
    admitted = gate.admit(event, [requirement])
    store.put(EvidenceRecord("ci", "run-2", "commit-B", "d2", "PASS"))
    final = gate.finalize(admitted.witness, event) if admitted.witness else None
    return {"subject_pinned": bind_subject, "admit": admitted.reason,
            "finalize": final and final.reason,
            "reproduced": final is not None and final.ready}


if __name__ == "__main__":
    results = {
        "B01 NaN provider result bricks every later claim": provider_result_bricks_ledger(float("nan")),
        "B01 control: finite provider result": provider_result_bricks_ledger(1.0),
        "B02 fractional timestamp bricks every later claim": fractional_time_bricks_ledger(100.5),
        "B02 integral float timestamp breaks the hash chain": fractional_time_bricks_ledger(100.0),
        "B02 control: integer timestamp": fractional_time_bricks_ledger(100),
        "B02b non-string identity breaks the hash chain": non_string_identity_breaks_chain(5),
        "B02b control: string identity": non_string_identity_breaks_chain(ACTOR),
        "B01b gateway: NaN provider result blocks every later action": gateway_nonfinite_result(float("nan")),
        "B01b control: finite provider result": gateway_nonfinite_result(1.0),
        "B03 executor approves itself": self_approval(ACTOR),
        "B03 control: distinct approver": self_approval(APPROVER),
        "B04 unencodable live action raises": unserialisable_live_action(),
        "B11 prepare before issuance": expiry_window(50, 111),
        "B11 prepare at expiry": expiry_window(200, 201),
        "B11 claim at expiry": expiry_window(110, 200),
        "B11 control: inside the window": expiry_window(110, 111),
        "B12 actor substituted at prepare": substitution("actor"),
        "B12 scope substituted at prepare": substitution("scope"),
        "B12 action substituted at prepare": substitution("action"),
        "B12 live action substituted at claim": substitution("live action"),
        "B12 control: nothing substituted": substitution("nothing"),
        "B13 one approval, two effects": approval_reuse(),
        "B14 revoked before claim": revocation_timing("before claim"),
        "B14 revoked after claim (post-dispatch limit)": revocation_timing("after claim"),
        "B05 stale anchor allows tail-truncation replay": stale_anchor_replay(fresh_anchor=False),
        "B05 control: fresh anchor detects it": stale_anchor_replay(fresh_anchor=True),
        "B05b open_local: ledger and authority rolled back together": gateway_colocated_authority_replay(True),
        "B05b control: ledger alone rolled back": gateway_colocated_authority_replay(False),
        "B06 gateway: executor approves its own side effect": gateway_self_approval("agent"),
        "B06 control: no approver": gateway_self_approval(None),
        "B07 gateway: empty approver approved then denied": gateway_empty_approver(),
        "B08 gateway: substring command screen": gateway_command_screen(),
        "B09 gateway: unencodable provider result": gateway_unencodable_result(),
        "B10 finality accepts a PASS for another subject": finality_subject_swap(False),
        "B10 control: subject pinned": finality_subject_swap(True),
    }
    print(json.dumps(results, indent=2, default=str))
