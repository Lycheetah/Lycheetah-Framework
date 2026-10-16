"""Regression tests for exact JSON types at the policy text-rule boundary."""
import pytest

from lycheetah.assurance import AssurancePolicy, PolicyError


def _payload():
    return {
        "id": "test.policy",
        "version": "1",
        "text": {
            "rules": [{
                "id": "test.rule",
                "pattern": r"\\bexample\\b",
                "title": "Example rule",
                "description": "Synthetic rule for parser regression testing.",
                "status_basis": "Fixture-only evidence basis.",
            }]
        },
    }


@pytest.mark.parametrize(
    "field,bad_value",
    [
        ("id", True), ("id", 17),
        ("pattern", False), ("pattern", 17),
        ("title", True), ("title", 17),
        ("description", False), ("description", 17),
        ("status_basis", True), ("status_basis", 17),
    ],
)
def test_text_rule_rejects_non_string_wire_types(field, bad_value):
    payload = _payload()
    payload["text"]["rules"][0][field] = bad_value
    with pytest.raises(PolicyError):
        AssurancePolicy.from_dict(payload)


def test_text_rule_valid_wire_types_round_trip_without_coercion():
    payload = _payload()
    policy = AssurancePolicy.from_dict(payload)
    restored = AssurancePolicy.from_dict(policy.to_dict())
    assert restored.digest == policy.digest
    assert restored.text_rules[0].pattern == payload["text"]["rules"][0]["pattern"]


def test_omitted_optional_text_fields_keep_existing_defaults():
    payload = _payload()
    payload["text"]["rules"] = [{"id": "test.rule", "pattern": "example"}]
    rule = AssurancePolicy.from_dict(payload).text_rules[0]
    assert rule.title == "test.rule"
    assert rule.description == "Policy text rule matched"
    assert rule.status_basis == ""
