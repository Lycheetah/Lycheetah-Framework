"""Batch 4 reproductions: durable workflow and dispatch (RV05).

Run from the repository root (or a HEAD export): python3 FOR-REVIEW/2026-10-22_OPUS_REVIEW/repro_batch4.py
Prints one JSON object. Every probe carries `reproduced`, and a benign control
where one makes sense. Executors here only count calls; nothing touches the OS.
"""
from __future__ import annotations

import json
import sys
import tempfile
import time
from pathlib import Path

sys.path.insert(0, str(Path.cwd()))

import lycheetah  # noqa: E402
from lycheetah.assurance import ActionGateway  # noqa: E402
from lycheetah.assurance.checkpoint_authority import CheckpointError  # noqa: E402

SCOPE = "notes"
# HEAD derived approval ids from action, actor and the current second, so a retry in
# the same second collided on approval_id_exists and hid R01/R07. Cross the boundary.
SECOND = 1.1


def _counter():
    calls = []

    def executor():
        calls.append(1)
        return {"status": "success"}

    return calls, executor


def _timeout():
    raise TimeoutError("provider did not answer")


def _try_open(base):
    try:
        ActionGateway.open_local(base)
        return "opened"
    except Exception as exc:  # the probe reports whatever the reopen does
        return f"{type(exc).__name__}:{exc}"


def _reconcile(gw, effect_id, outcome, evidence):
    """Use the checkpointed path when the tree has one; otherwise the raw guard."""
    if hasattr(gw, "reconcile"):
        result = gw.reconcile(effect_id, outcome, evidence)
        return "gateway", f"{result.status}:{result.reason}"
    decision = gw.guard.reconcile_effect(effect_id, 10**10, outcome, evidence)
    return "raw_guard", decision.reason


def r01_retry_while_unknown():
    """README: 'An uncertain ... result requires reconciliation before retry.'"""
    with tempfile.TemporaryDirectory() as d:
        gw = ActionGateway.open_local(d)
        action = {"tool": "payments.charge", "amount": 5, "side_effect": True}
        first = gw.execute(action, "agent", SCOPE, executor=_timeout, approver_id="reviewer")
        time.sleep(SECOND)
        calls, executor = _counter()
        retry = gw.execute(action, "agent", SCOPE, executor=executor, approver_id="reviewer")
        other_calls, other = _counter()
        control = gw.execute({"tool": "notes.write", "path": "x"}, "agent", SCOPE, executor=other)
        return {
            "first": f"{first.status}:{first.reason}",
            "retry": f"{retry.status}:{retry.reason}",
            "retry_provider_calls": len(calls),
            "control": f"{control.status}", "control_calls": len(other_calls),
            "reproduced": len(calls) > 0,
        }


def r02_reconcile_path():
    """An UNKNOWN effect must be reconcilable without bricking the gateway."""
    with tempfile.TemporaryDirectory() as d:
        gw = ActionGateway.open_local(d)
        action = {"tool": "payments.charge", "amount": 7, "side_effect": True}
        first = gw.execute(action, "agent", SCOPE, executor=_timeout, approver_id="reviewer")
        path, reconciled = _reconcile(gw, first.effect_id, "failure",
                                      {"provider_read": "no charge found"})
        calls, executor = _counter()
        later = gw.execute({"tool": "notes.write", "path": "y"}, "agent", SCOPE, executor=executor)
        status = gw.guard.get_effect(first.effect_id)["status"]
        return {
            "path": path, "reconciled": reconciled, "effect_status": status,
            "later": f"{later.status}:{later.reason}", "later_calls": len(calls),
            "reopen": _try_open(d),
            "reproduced": path == "raw_guard" or later.status != "SUCCEEDED",
        }


def r03_outage_leaves_permanent_tail():
    """A publish failure after a local commit. Design question (P11), not patched here."""
    with tempfile.TemporaryDirectory() as d:
        gw = ActionGateway.open_local(d)
        store = gw.checkpoints
        original = store.store
        state = {"n": 0}

        def flaky(*args, **kwargs):
            state["n"] += 1
            if state["n"] == 3:  # 1 approval, 2 prepare, 3 claim
                raise CheckpointError("authority_unreachable")
            return original(*args, **kwargs)

        store.store = flaky
        calls, executor = _counter()
        first = gw.execute({"tool": "notes.write", "path": "z"}, "agent", SCOPE, executor=executor)
        store.store = original
        later_calls, later_exec = _counter()
        later = gw.execute({"tool": "notes.write", "path": "w"}, "agent", SCOPE, executor=later_exec)
        return {
            "first": f"{first.status}:{first.reason}", "first_calls": len(calls),
            "after_recovery": f"{later.status}:{later.reason}", "after_calls": len(later_calls),
            "reopen": _try_open(d),
            "reproduced": later.status == "BLOCKED",
        }


def r04_two_instances_one_ledger():
    """Two gateways on one directory, as two concurrent `lycheetah guard run` would be."""
    with tempfile.TemporaryDirectory() as d:
        a = ActionGateway.open_local(d)
        b = ActionGateway.open_local(d)
        original = b.guard.issue_approval
        inner = {}

        def interleaved(*args, **kwargs):
            # A runs a whole checkpointed mutation after B passed its checkpoint check.
            inner["a"] = a.propose({"tool": "notes.write", "path": "a"}, "agent", SCOPE)
            return original(*args, **kwargs)

        b.guard.issue_approval = interleaved
        b_gate = b.propose({"tool": "notes.write", "path": "b"}, "agent", SCOPE)
        b.guard.issue_approval = original
        calls, executor = _counter()
        later = a.execute({"tool": "notes.write", "path": "c"}, "agent", SCOPE, executor=executor)
        return {
            "a_propose": f"{inner['a'].allowed}:{inner['a'].reason}",
            "b_propose": f"{b_gate.allowed}:{b_gate.reason}",
            "later": f"{later.status}:{later.reason}", "later_calls": len(calls),
            "reopen": _try_open(d),
            "reproduced": later.status == "BLOCKED",
        }


def r04_control_sequential():
    with tempfile.TemporaryDirectory() as d:
        a = ActionGateway.open_local(d)
        b = ActionGateway.open_local(d)
        ga = a.propose({"tool": "notes.write", "path": "a"}, "agent", SCOPE)
        gb = b.propose({"tool": "notes.write", "path": "b"}, "agent", SCOPE)
        calls, executor = _counter()
        later = a.execute({"tool": "notes.write", "path": "c"}, "agent", SCOPE, executor=executor)
        return {"a": ga.reason, "b": gb.reason, "later": later.status,
                "reproduced": later.status != "SUCCEEDED"}


def r05_explicit_empty_live_action():
    with tempfile.TemporaryDirectory() as d:
        gw = ActionGateway.open_local(d)
        gate = gw.propose({"tool": "notes.write", "path": "e"}, "agent", SCOPE)
        calls, executor = _counter()
        result = gw.dispatch(gate.effect_id, executor, current_action={})
        return {"dispatch": f"{result.status}:{result.reason}", "calls": len(calls),
                "effect": gw.guard.get_effect(gate.effect_id)["status"],
                "reproduced": len(calls) > 0}


def r06_duplicate_dispatch():
    with tempfile.TemporaryDirectory() as d:
        gw = ActionGateway.open_local(d)
        gate = gw.propose({"tool": "notes.write", "path": "f"}, "agent", SCOPE)
        calls, executor = _counter()
        first = gw.dispatch(gate.effect_id, executor)
        second = gw.dispatch(gate.effect_id, executor)
        return {"first": first.status, "second": f"{second.status}:{second.reason}",
                "calls": len(calls), "reproduced": len(calls) != 1}


def r07_crash_after_claim():
    """Claim checkpointed, process dies before the provider call; reopen and look."""
    with tempfile.TemporaryDirectory() as d:
        gw = ActionGateway.open_local(d)
        action = {"tool": "deploy.release", "target": "prod", "side_effect": True}
        gate = gw.propose(action, "agent", SCOPE, approver_id="reviewer")
        claim = gw.workflow.claim_dispatch(gate.effect_id, gw.guard.get_effect(gate.effect_id)["created_at"], action)
        del gw  # the crash
        reopened = _try_open(d)
        gw2 = ActionGateway.open_local(d)
        calls, executor = _counter()
        again = gw2.dispatch(gate.effect_id, executor)
        time.sleep(SECOND)
        retry_calls, retry_exec = _counter()
        retry = gw2.execute(action, "agent", SCOPE, executor=retry_exec, approver_id="reviewer")
        return {
            "claim": f"{claim.decision.reason}:checkpointed={claim.checkpointed}",
            "reopen": reopened,
            "effect_after_crash": gw2.guard.get_effect(gate.effect_id)["status"],
            "redispatch": f"{again.status}:{again.reason}", "redispatch_calls": len(calls),
            "retry_same_action": f"{retry.status}:{retry.reason}", "retry_calls": len(retry_calls),
            "reproduced": len(calls) > 0 or len(retry_calls) > 0,
        }


if __name__ == "__main__":
    probes = {
        "R01_retry_while_unknown": r01_retry_while_unknown,
        "R02_reconcile_path": r02_reconcile_path,
        "R03_outage_leaves_permanent_tail": r03_outage_leaves_permanent_tail,
        "R04_two_instances_one_ledger": r04_two_instances_one_ledger,
        "R04_control_sequential": r04_control_sequential,
        "R05_explicit_empty_live_action": r05_explicit_empty_live_action,
        "R06_duplicate_dispatch": r06_duplicate_dispatch,
        "R07_crash_after_claim": r07_crash_after_claim,
    }
    out = {"lycheetah": lycheetah.__file__}
    for name, probe in probes.items():
        try:
            out[name] = probe()
        except Exception as exc:  # a crashing probe is a result, not a pass
            out[name] = {"crashed": f"{type(exc).__name__}: {exc}", "reproduced": None}
    print(json.dumps(out, indent=1, default=str))
