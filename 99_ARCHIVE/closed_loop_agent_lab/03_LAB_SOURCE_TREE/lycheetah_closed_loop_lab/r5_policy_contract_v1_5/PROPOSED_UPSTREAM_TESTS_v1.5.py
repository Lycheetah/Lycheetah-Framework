"""Intended for tests/test_assurance_policy.py in a clean upstream checkout.
Not executed against the upstream package in this session.
"""
import pytest
from lycheetah.assurance import AssurancePolicy, PolicyError

@pytest.mark.parametrize(
    ("field", "bad_value"),
    [
        ("id", True),
        ("id", 123),
        ("pattern", True),
        ("pattern", 17),
        ("title", False),
        ("description", 7),
        ("status_basis", 4),
    ],
)
def test_text_rule_rejects_non_string_wire_fields(field, bad_value):
    policy = {
        "id": "test.policy",
        "version": "1",
        "text": {"rules": [{"id": "customer.test-rule", "pattern": "foo"}]},
    }
    policy["text"]["rules"][0][field] = bad_value
    with pytest.raises(PolicyError):
        AssurancePolicy.from_dict(policy)


def test_text_rule_defaults_remain_backward_compatible_when_optional_fields_omitted():
    policy = AssurancePolicy.from_dict({
        "id": "test.policy",
        "version": "1",
        "text": {"rules": [{"id": "customer.test-rule", "pattern": "foo"}]},
    })
    rule = policy.text_rules[0]
    assert rule.title == "customer.test-rule"
    assert rule.description == "Policy text rule matched"
    assert rule.status_basis == ""


def test_semantic_guards_remain_enabled_after_wire_type_validation():
    invalid_patterns = ["["]
    for pattern in invalid_patterns:
        with pytest.raises(PolicyError):
            AssurancePolicy.from_dict({
                "id": "test.policy",
                "version": "1",
                "text": {"rules": [{"id": "customer.test-rule", "pattern": pattern}]},
            })
