"""Durable dispatch: unresolved outcomes, reconciliation and two writers on one ledger.

Each refusal sits beside a control that must still pass. Reproductions:
FOR-REVIEW/2026-10-22_OPUS_REVIEW/repro_batch4.py (R01, R02, R04, R07).
"""
from __future__ import annotations

import time

import pytest

from lycheetah.assurance import ActionGateway
from lycheetah.cli import guard_cli

SCOPE = "notes"
CHARGE = {"tool": "payments.charge", "amount": 5, "side_effect": True}
EVIDENCE = {"provider_read": "ledger row 42"}


def _counting():
    calls = []

    def executor():
        calls.append(1)
        return {"status": "success"}

    return calls, executor


def _timeout():
    raise TimeoutError("provider did not answer")


@pytest.fixture
def gateway(tmp_path):
    return ActionGateway.open_local(tmp_path)


def _unknown(gateway, action=CHARGE):
    first = gateway.execute(action, "agent", SCOPE, executor=_timeout, approver_id="reviewer")
    assert first.status == "UNKNOWN"
    return first


def test_retry_while_outcome_unknown_never_reaches_the_provider(gateway):
    first = _unknown(gateway)
    calls, executor = _counting()
    retry = gateway.execute(CHARGE, "agent", SCOPE, executor=executor, approver_id="reviewer")
    assert (retry.status, retry.reason, calls) == ("BLOCKED", "prior_effect_unresolved", [])
    assert retry.effect_id == first.effect_id  # the effect an operator must reconcile
    other_calls, other = _counting()
    control = gateway.execute({"tool": "notes.write", "path": "x"}, "agent", SCOPE, executor=other)
    assert (control.status, other_calls) == ("SUCCEEDED", [1])


@pytest.mark.parametrize("outcome, settled", [("failure", "FAILED"), ("success", "SUCCEEDED")])
def test_reconcile_settles_an_unknown_effect_through_the_checkpoint(
    gateway, tmp_path, outcome, settled
):
    first = _unknown(gateway)
    result = gateway.reconcile(first.effect_id, outcome, EVIDENCE)
    assert (result.status, result.reason, result.provider_called) == (settled, "reconciled", False)
    assert gateway.guard.get_effect(first.effect_id)["status"] == settled
    assert gateway.workflow.synchronize_status()["synchronized"]
    ActionGateway.open_local(tmp_path)  # a dirty tail refuses to reopen
    calls, executor = _counting()
    later = gateway.execute({"tool": "notes.write", "path": "y"}, "agent", SCOPE, executor=executor)
    assert (later.status, calls) == ("SUCCEEDED", [1])


def test_a_reconciled_failure_allows_the_same_action_again(gateway):
    first = _unknown(gateway)
    assert gateway.reconcile(first.effect_id, "failure", EVIDENCE).reason == "reconciled"
    calls, executor = _counting()
    retry = gateway.execute(CHARGE, "agent", SCOPE, executor=executor, approver_id="reviewer")
    assert (retry.status, calls) == ("SUCCEEDED", [1])


def test_reconcile_refuses_an_effect_that_is_not_unresolved(gateway):
    calls, executor = _counting()
    done = gateway.execute({"tool": "notes.write", "path": "z"}, "agent", SCOPE, executor=executor)
    refused = gateway.reconcile(done.effect_id, "failure", EVIDENCE)
    assert refused.status == "DENIED"
    assert gateway.guard.get_effect(done.effect_id)["status"] == "SUCCEEDED"
    missing = gateway.reconcile("no-such-effect", "failure", EVIDENCE)
    assert (missing.status, missing.reason) == ("DENIED", "missing_effect")
    assert gateway.workflow.synchronize_status()["synchronized"]


def test_a_claim_interrupted_by_a_crash_blocks_the_same_action_until_reconciled(tmp_path):
    gateway = ActionGateway.open_local(tmp_path)
    action = {"tool": "deploy.release", "target": "prod", "side_effect": True}
    gate = gateway.propose(action, "agent", SCOPE, approver_id="reviewer")
    created = gateway.guard.get_effect(gate.effect_id)["created_at"]
    assert gateway.workflow.claim_dispatch(gate.effect_id, created, action).checkpointed
    del gateway  # the process dies before the provider call
    reopened = ActionGateway.open_local(tmp_path)
    calls, executor = _counting()
    retry = reopened.execute(action, "agent", SCOPE, executor=executor, approver_id="reviewer")
    assert (retry.status, retry.reason, calls) == ("BLOCKED", "prior_effect_unresolved", [])
    settled = reopened.reconcile(gate.effect_id, "failure", {"provider_read": "no release"})
    assert settled.reason == "reconciled"
    again = reopened.execute(action, "agent", SCOPE, executor=executor, approver_id="reviewer")
    assert (again.status, calls) == ("SUCCEEDED", [1])


def test_two_gateways_on_one_ledger_do_not_brick_it(tmp_path):
    a = ActionGateway.open_local(tmp_path)
    b = ActionGateway.open_local(tmp_path)
    inner = {}
    original = b.guard.issue_approval

    def interleaved(*args, **kwargs):
        # A completes a checkpointed write after B passed its own checkpoint check.
        inner["a"] = a.propose({"tool": "notes.write", "path": "a"}, "agent", SCOPE)
        return original(*args, **kwargs)

    b.guard.issue_approval = interleaved
    stale = b.propose({"tool": "notes.write", "path": "b"}, "agent", SCOPE)
    b.guard.issue_approval = original
    assert inner["a"].allowed
    assert (stale.allowed, stale.reason) == (False, "audit_checkpoint_stale")
    assert b.propose({"tool": "notes.write", "path": "b"}, "agent", SCOPE).allowed
    calls, executor = _counting()
    later = a.execute({"tool": "notes.write", "path": "c"}, "agent", SCOPE, executor=executor)
    assert (later.status, calls) == ("SUCCEEDED", [1])
    ActionGateway.open_local(tmp_path)


def test_a_stale_revocation_is_refused_without_writing(tmp_path):
    a = ActionGateway.open_local(tmp_path)
    b = ActionGateway.open_local(tmp_path)
    original = b.guard.revoke_all

    def interleaved(*args, **kwargs):
        a.propose({"tool": "notes.write", "path": "a"}, "agent", SCOPE)
        return original(*args, **kwargs)

    b.guard.revoke_all = interleaved
    stale = b.workflow.revoke_all("agent", int(time.time()))
    b.guard.revoke_all = original
    assert (stale.decision.allowed, stale.decision.reason) == (False, "audit_checkpoint_stale")
    assert b.workflow.synchronize_status()["synchronized"]
    assert b.workflow.revoke_all("agent", int(time.time())).decision.allowed
    assert b.workflow.synchronize_status()["synchronized"]


def test_cli_reconcile_settles_the_effect_named_by_the_unknown_result(tmp_path, capsys):
    gateway = ActionGateway.open_local(tmp_path)
    first = _unknown(gateway)
    del gateway
    args = ["reconcile", first.effect_id, "--outcome", "failure",
            "--evidence", '{"provider_read": "no charge found"}', "--dir", str(tmp_path)]
    with pytest.raises(SystemExit) as settled:
        guard_cli(args)
    assert settled.value.code == 0
    assert '"reason": "reconciled"' in capsys.readouterr().out
    with pytest.raises(SystemExit) as again:
        guard_cli(args)
    assert again.value.code == 1
    assert '"status": "DENIED"' in capsys.readouterr().out
