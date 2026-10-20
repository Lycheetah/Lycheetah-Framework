"""Gateway regressions for checkpoint continuity and current-policy attribution."""

from dataclasses import replace
from unittest.mock import Mock, patch

import pytest

from lycheetah.assurance import ActionGateway
from lycheetah.assurance.checkpoint_authority import CheckpointError


@pytest.fixture
def gateway(tmp_path):
    return ActionGateway.open_local(tmp_path)


ACTION = {"tool": "echo", "message": "local fixture"}


def test_uncheckpointed_tail_blocks_dispatch(gateway):
    gate = gateway.propose(ACTION, "agent", "fixture:echo")
    checkpoint = gateway._get_latest_checkpoint()
    gateway.guard.revoke_all("unrelated-actor", 1)
    execute = Mock(return_value={"status": "success"})
    result = gateway.dispatch(gate.effect_id, execute)
    assert not result.provider_called
    execute.assert_not_called()
    assert gateway._get_latest_checkpoint() == checkpoint


def test_failed_checkpoint_is_not_blessed_by_a_later_proposal(gateway):
    checkpoint = gateway._get_latest_checkpoint()
    with patch.object(gateway.checkpoints, "store", side_effect=CheckpointError("offline")):
        try:
            gateway.propose(ACTION, "agent", "fixture:echo", approval_id="first", effect_id="first")
        except CheckpointError:
            pass  # Legacy path raised after its local write.
    assert gateway.guard.audit_anchor()["event_count"] > checkpoint["event_count"]
    later = gateway.propose(ACTION, "agent", "fixture:echo", approval_id="later", effect_id="later")
    assert not later.allowed
    assert gateway._get_latest_checkpoint() == checkpoint


def test_restart_does_not_bootstrap_a_dirty_tail(gateway, tmp_path):
    gateway.guard.revoke_all("agent", 1)
    with pytest.raises(RuntimeError, match="synchron|checkpoint"):
        ActionGateway.open_local(tmp_path)


def test_explicit_empty_live_action_is_not_replaced_by_approved_action(gateway):
    gate = gateway.propose(ACTION, "agent", "fixture:echo")
    execute = Mock(return_value={"status": "success"})
    result = gateway.dispatch(gate.effect_id, execute, current_action={})
    assert not result.provider_called
    assert result.reason == "live_state_mismatch"
    execute.assert_not_called()


def test_newly_denied_tool_is_rechecked_before_dispatch(gateway):
    gate = gateway.propose(ACTION, "agent", "fixture:echo")
    gateway.policy = replace(gateway.policy, denied_tools=("echo",))
    execute = Mock(return_value={"status": "success"})
    result = gateway.dispatch(gate.effect_id, execute)
    assert not result.provider_called
    assert result.reason == "policy_blocked"
    execute.assert_not_called()


def test_receipt_names_the_policy_actually_evaluated(gateway):
    evaluated = gateway.policy

    def execute():
        gateway.policy = replace(evaluated, policy_id="fixture.changed-during-call")
        return {"status": "success"}

    result = gateway.execute(ACTION, "agent", "fixture:echo", execute)
    assert result.status == "SUCCEEDED"
    assert result.receipt.policy["sha256"] == evaluated.digest


def test_synchronized_dispatch_still_executes_once(gateway):
    gate = gateway.propose(ACTION, "agent", "fixture:echo")
    execute = Mock(return_value={"status": "success"})
    assert gateway.dispatch(gate.effect_id, execute).status == "SUCCEEDED"
    assert not gateway.dispatch(gate.effect_id, execute).provider_called
    execute.assert_called_once()


def test_uncheckpointed_dispatch_claim_never_reaches_executor(gateway):
    gate = gateway.propose(ACTION, "agent", "fixture:echo")
    execute = Mock(return_value={"status": "success"})
    with patch.object(gateway.checkpoints, "store", side_effect=CheckpointError("offline")):
        result = gateway.dispatch(gate.effect_id, execute)
    assert not result.provider_called
    execute.assert_not_called()


def test_result_checkpoint_failure_reports_unknown_after_executor(gateway):
    gate = gateway.propose(ACTION, "agent", "fixture:echo")

    def execute():
        gateway.checkpoints.store = Mock(side_effect=CheckpointError("offline"))
        return {"status": "success", "fixture": "performed"}

    result = gateway.dispatch(gate.effect_id, execute)
    assert result.provider_called and result.status == "UNKNOWN"
    assert result.receipt is None
    assert result.result["fixture"] == "performed"


def test_new_review_requirement_does_not_turn_auto_allow_into_human_approval(gateway):
    gate = gateway.propose(ACTION, "agent", "fixture:echo")
    gateway.policy = replace(gateway.policy, review_tools=("echo",))
    execute = Mock(return_value={"status": "success"})
    result = gateway.dispatch(gate.effect_id, execute)
    assert not result.provider_called
    assert result.reason == "human_approval_required"
    execute.assert_not_called()
