"""Gateway receipts preserve evaluated policy separately from execution outcome."""

import json
from dataclasses import replace
from importlib.resources import files
from unittest.mock import Mock

import jsonschema
import pytest

from lycheetah.assurance import ActionGateway, AssurancePolicy, Disposition
from lycheetah.assurance.models import Phase
from lycheetah.assurance.policy import TextRule


ACTION = {"tool": "echo", "message": "local fixture", "side_effect": False}


def _assert_receipt(result, decision=Disposition.ALLOW):
    assert result.receipt is not None
    assert result.receipt.decision == decision
    report = result.receipt.verify()
    assert report.valid, report.errors
    schema = json.loads(
        files("lycheetah.assurance").joinpath("schemas", "receipt.schema.json").read_text()
    )
    jsonschema.Draft202012Validator(schema).validate(result.receipt.to_dict())
    assert result.receipt.metrics["execution_status"] == result.status


@pytest.mark.parametrize("outcome", ["success", "failure", "timeout", "exception"])
def test_execution_outcome_does_not_replace_policy_decision(tmp_path, outcome):
    gateway = ActionGateway.open_local(tmp_path)

    def execute():
        if outcome == "timeout":
            raise TimeoutError("fixture timeout")
        if outcome == "exception":
            raise RuntimeError("fixture exception")
        return {"status": outcome}

    result = gateway.execute(ACTION, "worker", "local:echo", execute)
    assert (
        result.status
        == {
            "success": "SUCCEEDED",
            "failure": "FAILED",
            "timeout": "UNKNOWN",
            "exception": "UNKNOWN",
        }[outcome]
    )
    assert result.provider_called
    _assert_receipt(result)


def test_approved_review_tool_preserves_review_policy_decision(tmp_path):
    gateway = ActionGateway.open_local(tmp_path, policy=AssurancePolicy(review_tools=("echo",)))
    result = gateway.execute(
        ACTION, "worker", "local:echo", lambda: {"status": "success"}, approver_id="reviewer"
    )
    assert result.status == "SUCCEEDED"
    _assert_receipt(result, Disposition.REVIEW)
    assert result.receipt.event["human_approved"] is True


@pytest.mark.parametrize("approver", [None, "reviewer"])
def test_event_binds_declared_action_and_honest_approval_metadata(tmp_path, approver):
    gateway = ActionGateway.open_local(tmp_path)
    result = gateway.execute(
        ACTION, "worker", "local:echo", lambda: {"status": "success"}, approver_id=approver
    )
    event = result.receipt.event
    assert event["side_effect"] is False
    assert event["human_approved"] is (True if approver else None)
    assert event["scopes"] == ["local:echo"]
    assert event["actor"] == "worker"
    assert event["action_hash"] == result.action_hash
    assert event["approver_id"] == approver
    _assert_receipt(result)


def test_receipt_mutation_is_detected(tmp_path):
    gateway = ActionGateway.open_local(tmp_path)
    result = gateway.execute(ACTION, "worker", "local:echo", lambda: {"status": "success"})
    receipt = result.receipt
    assert receipt.verify().valid
    changed = replace(receipt, event={**receipt.event, "actor": "substituted"})
    assert not changed.verify().valid


@pytest.mark.parametrize("change", ["policy", "action"])
def test_denied_dispatch_never_calls_executor_or_mints_execution_receipt(tmp_path, change):
    gateway = ActionGateway.open_local(tmp_path)
    gate = gateway.propose(ACTION, "worker", "local:echo")
    assert gate.allowed
    current_action = ACTION
    if change == "policy":
        gateway.policy = replace(gateway.policy, denied_tools=("echo",))
    else:
        current_action = {**ACTION, "message": "changed"}
    execute = Mock(return_value={"status": "success"})
    result = gateway.dispatch(gate.effect_id, execute, current_action=current_action)
    assert result.status == "DENIED"
    assert not result.provider_called
    assert result.receipt is None
    execute.assert_not_called()


@pytest.mark.parametrize(
    "field",
    ["denied_tools", "review_tools", "tool_allowlist", "blocked_scopes", "sensitive_argument_keys"],
)
def test_policy_constructor_normalizes_and_detaches_pattern_lists(field):
    source = ["fixture"]
    policy = AssurancePolicy(**{field: source})
    original = policy.digest
    source.append("changed")
    assert getattr(policy, field) == ("fixture",)
    assert policy.digest == original


def test_text_rule_phases_and_policy_rules_are_immutable_snapshots():
    phases = [Phase.INPUT]
    rule = TextRule("fixture.rule", "fixture", "Fixture", "Fixture rule", phases=phases)
    rules = [rule]
    policy = AssurancePolicy(text_rules=rules)
    original = policy.digest
    phases.append(Phase.OUTPUT)
    rules.clear()
    assert rule.phases == (Phase.INPUT,)
    assert policy.text_rules == (rule,)
    assert policy.digest == original


def test_receipt_policy_is_not_rewritten_by_constructor_list_mutation(tmp_path):
    denied = []
    policy = AssurancePolicy(denied_tools=denied)
    original = policy.digest
    gateway = ActionGateway.open_local(tmp_path, policy=policy)

    def execute():
        denied.append("echo")
        return {"status": "success"}

    result = gateway.execute(ACTION, "worker", "local:echo", execute)
    assert result.receipt.policy["sha256"] == original


def test_receipt_keeps_policy_snapshot_when_callback_replaces_current_policy(tmp_path):
    gateway = ActionGateway.open_local(tmp_path)
    evaluated = gateway.policy

    def execute():
        gateway.policy = replace(evaluated, denied_tools=("echo",), version="changed")
        return {"status": "success"}

    result = gateway.execute(ACTION, "worker", "local:echo", execute)
    assert result.receipt.policy["sha256"] == evaluated.digest
    assert gateway.policy.digest != evaluated.digest
