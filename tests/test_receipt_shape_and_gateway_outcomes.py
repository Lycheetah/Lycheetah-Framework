"""Receipts are well-formed when they verify; gateway outcomes never overclaim."""

import copy

import pytest

from lycheetah.assurance import ActionGateway, Disposition
from lycheetah.assurance.jsonutil import sha256_json
from lycheetah.assurance.policy import PolicyError, TextRule
from lycheetah.assurance.receipt import AssuranceReceipt


ACTION = {"tool": "echo", "message": "local fixture", "side_effect": False}


def _receipt_dict(tmp_path):
    gateway = ActionGateway.open_local(tmp_path)
    result = gateway.execute(ACTION, "worker", "local:echo", lambda: {"status": "success"})
    return result.receipt.to_dict()


def _with_recomputed_digest(data):
    # Anyone can recompute an unsealed digest, so it cannot be what keeps a bad body out.
    data["integrity"]["digest"] = sha256_json({k: v for k, v in data.items() if k != "integrity"})
    return AssuranceReceipt.from_dict(data)


@pytest.mark.parametrize(
    "mutate",
    [
        lambda d: d.__setitem__("issued_at", "next tuesday"),
        lambda d: d.__setitem__("lineage", {}),
        lambda d: d["lineage"].__setitem__("previous_receipt_sha256", "not-a-digest"),
        lambda d: d["lineage"].__setitem__("trace_id", 7),
        lambda d: d.__setitem__("event", {}),
        lambda d: d["event"].__setitem__("phase", "telepathy"),
        lambda d: d.__setitem__("policy", {}),
        lambda d: d["policy"].__setitem__("sha256", "x"),
    ],
    ids=[
        "issued_at",
        "lineage_empty",
        "previous_digest",
        "trace_id",
        "event_empty",
        "event_phase",
        "policy_empty",
        "policy_digest",
    ],
)
def test_verify_rejects_a_body_the_published_schema_rejects(tmp_path, mutate):
    data = _receipt_dict(tmp_path)
    assert _with_recomputed_digest(copy.deepcopy(data)).verify().valid
    mutate(data)
    assert not _with_recomputed_digest(data).verify().valid


@pytest.mark.parametrize("seal", [None, {"algorithm": "hmac-sha256", "key_id": "k", "value": "0" * 64}])
def test_verify_returns_a_verdict_for_a_non_ascii_digest(tmp_path, seal):
    data = _receipt_dict(tmp_path)
    data["integrity"]["digest"] = "é" * 64
    data["integrity"]["seal"] = seal
    report = AssuranceReceipt.from_dict(data).verify(b"key" if seal else None)
    assert not report.valid
    assert "integrity.digest must be 64 lowercase hexadecimal characters" in report.errors


@pytest.mark.parametrize(
    "field, value",
    [("id", 12345), ("pattern", None), ("title", None), ("description", 7), ("status_basis", None)],
)
def test_text_rule_refuses_non_string_fields(field, value):
    data = TextRule("fixture.rule", "fixture", "Fixture", "Fixture rule").to_dict()
    with pytest.raises(PolicyError):
        TextRule.from_dict({**data, field: value})


def test_text_rule_constructor_refuses_non_string_title():
    with pytest.raises(PolicyError):
        TextRule("fixture.rule", "fixture", None, "Fixture rule")


@pytest.mark.parametrize("answer", [{"status": "pending"}, {"status": "accepted"}, {}])
def test_unrecognised_executor_status_is_uncertain_not_failed(tmp_path, answer):
    gateway = ActionGateway.open_local(tmp_path)
    action = {"tool": "payments.charge", "amount": 9, "side_effect": True}
    first = gateway.execute(action, "worker", "local:pay", lambda: answer, approver_id="reviewer")
    assert (first.status, first.reason) == ("UNKNOWN", "uncertain_outcome")
    assert gateway.guard.get_effect(first.effect_id)["status"] == "UNKNOWN"
    calls = []
    retry = gateway.execute(
        action, "worker", "local:pay", lambda: calls.append(1) or {"status": "success"},
        approver_id="reviewer",
    )
    assert (retry.status, retry.reason) == ("BLOCKED", "prior_effect_unresolved")
    assert calls == []


def test_gateway_receipt_keeps_the_runtime_caveats(tmp_path):
    gateway = ActionGateway.open_local(tmp_path)
    result = gateway.execute(
        ACTION, "worker", "local:echo", lambda: {"status": "success"}, approver_id="reviewer"
    )
    limitations = result.receipt.limitations
    assert result.receipt.event["human_approved"] is True
    assert any("caller-declared" in item for item in limitations)
    assert any("HMAC is required" in item for item in limitations)
    assert "local_execution_cell_boundary" in limitations
    assert result.receipt.verify().valid


@pytest.mark.parametrize(
    "command",
    [
        "rm -rf /",
        "rm -fr /",
        "rm -r -f /",
        "rm -rf  /",
        "rm --recursive --force /",
        "rm -rf --no-preserve-root /",
        "sudo /bin/rm -Rf /etc",
        "rm -rf ~",
        "rm -rf /tmp/cache",
        ["rm", "-fr", "/"],
        ":(){ :|:& };:",
        ":() { :|:& }; :",
        "bomb(){ bomb|bomb& };bomb",
    ],
)
def test_destructive_tripwire_ignores_spelling(tmp_path, command):
    gateway = ActionGateway.open_local(tmp_path)
    disposition, findings = gateway.evaluate_policy(
        {"tool": "ops.run", "command": command}, "local:ops", "worker"
    )
    assert disposition == Disposition.BLOCK
    assert [f.finding_id for f in findings] == ["destructive_command_prohibited"]


@pytest.mark.parametrize(
    "command", ["rm -rf ./build", "rm -f /tmp/one-file", "ls -r /", "echo rm", "grep -r x ."]
)
def test_destructive_tripwire_leaves_ordinary_commands_to_policy(tmp_path, command):
    gateway = ActionGateway.open_local(tmp_path)
    disposition, findings = gateway.evaluate_policy(
        {"tool": "ops.run", "command": command}, "local:ops", "worker"
    )
    assert "destructive_command_prohibited" not in [f.finding_id for f in findings]
    assert disposition == Disposition.ALLOW
