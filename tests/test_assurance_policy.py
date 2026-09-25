import json

import pytest

from lycheetah.assurance import (
    AssurancePolicy,
    AssuranceRuntime,
    ClaimStatus,
    Disposition,
    PolicyError,
    Severity,
    TextRule,
)


def _rule(**overrides):
    values = {
        "rule_id": "customer.no-unreviewed-guarantees",
        "pattern": r"\bguarantee\b",
        "title": "Guarantee requires review",
        "description": "Customer-facing guarantees require evidence.",
        "requested_disposition": Disposition.BLOCK,
        "claim_status": ClaimStatus.SCAFFOLD,
        "deterministic": False,
        "severity": Severity.HIGH,
    }
    values.update(overrides)
    return TextRule(**values)


def test_policy_digest_changes_with_policy_content():
    first = AssurancePolicy(policy_id="test.policy", version="1", denied_tools=("shell",))
    second = AssurancePolicy(policy_id="test.policy", version="1", denied_tools=("shell*",))
    assert first.digest != second.digest


def test_policy_round_trip_preserves_digest():
    policy = AssurancePolicy(
        policy_id="test.policy",
        version="7",
        denied_tools=("shell*",),
        text_rules=(_rule(),),
    )
    assert AssurancePolicy.from_dict(policy.to_dict()).digest == policy.digest


def test_policy_loads_from_json(tmp_path):
    path = tmp_path / "policy.json"
    policy = AssurancePolicy(policy_id="test.policy", version="1")
    path.write_text(json.dumps(policy.to_dict()), encoding="utf-8")
    assert AssurancePolicy.from_json(path).digest == policy.digest


def test_invalid_regex_fails_visibly():
    with pytest.raises(PolicyError):
        _rule(pattern="[")


def test_active_rule_requires_status_basis():
    with pytest.raises(PolicyError):
        _rule(claim_status=ClaimStatus.ACTIVE, deterministic=True)


def test_scaffold_rule_cannot_hard_block():
    runtime = AssuranceRuntime(AssurancePolicy(policy_id="test.policy", text_rules=(_rule(),)))
    receipt = runtime.evaluate_text("We guarantee the result.")
    finding = next(item for item in receipt.findings if item.finding_id.startswith("POLICY:"))
    assert finding.requested_disposition == Disposition.BLOCK
    assert finding.effective_disposition == Disposition.REVIEW
    assert receipt.decision == Disposition.REVIEW


def test_conjecture_rule_is_observe_only():
    rule = _rule(claim_status=ClaimStatus.CONJECTURE)
    runtime = AssuranceRuntime(
        AssurancePolicy(
            policy_id="test.policy",
            aura_review_below_percent=0,
            manipulation_review_threshold=1,
            text_rules=(rule,),
        )
    )
    receipt = runtime.evaluate_text("The guarantee word appears in a neutral test.")
    finding = next(item for item in receipt.findings if item.finding_id.startswith("POLICY:"))
    assert finding.effective_disposition == Disposition.ALLOW
    assert receipt.decision == Disposition.ALLOW


def test_active_deterministic_policy_rule_can_block():
    rule = _rule(
        claim_status=ClaimStatus.ACTIVE,
        deterministic=True,
        status_basis="Approved customer communications policy CC-12.",
    )
    runtime = AssuranceRuntime(
        AssurancePolicy(
            policy_id="test.policy",
            aura_review_below_percent=0,
            manipulation_review_threshold=1,
            text_rules=(rule,),
        )
    )
    receipt = runtime.evaluate_text("We guarantee the result.")
    assert receipt.decision == Disposition.BLOCK


def test_active_inferential_rule_is_still_capped_at_review():
    rule = _rule(
        claim_status=ClaimStatus.ACTIVE,
        deterministic=False,
        status_basis="Measured only on bounded corpus v3.",
    )
    runtime = AssuranceRuntime(AssurancePolicy(policy_id="test.policy", text_rules=(rule,)))
    receipt = runtime.evaluate_text("We guarantee the result.")
    finding = next(item for item in receipt.findings if item.finding_id.startswith("POLICY:"))
    assert finding.effective_disposition == Disposition.REVIEW


@pytest.mark.parametrize(
    "policy",
    [
        {"id": "test.strict", "version": "1", "unknown": True},
        {
            "id": "test.strict",
            "version": "1",
            "privacy": {"capture_content": "false"},
        },
        {
            "id": "test.strict",
            "version": "1",
            "tools": {"allowlist": "order.read"},
        },
        {
            "id": "test.strict",
            "version": "1",
            "text": {"manipulation_review_threshold": float("nan")},
        },
        {
            "id": "test.strict",
            "version": "1",
            "text": {"max_text_characters": "20000"},
        },
    ],
)
def test_policy_parser_rejects_ambiguous_or_unknown_values(policy):
    with pytest.raises(PolicyError):
        AssurancePolicy.from_dict(policy)


def test_policy_parser_requires_identity_and_version():
    with pytest.raises(PolicyError):
        AssurancePolicy.from_dict({"id": "test.strict"})
