"""Upstream regression tests for strict TextRule string-field typing.

Apply only alongside strict_text_rule_parser_v1_2.patch on the matching source
revision. These tests intentionally cover both policy deserialization and direct
TextRule construction because the dataclass is public and can be instantiated
without going through AssurancePolicy.from_dict.
"""
import pytest

from lycheetah.assurance import AssurancePolicy, PolicyError, TextRule

BASE_RULE = {"id": "customer.rule-01", "pattern": r"\bhello\b"}
BAD_JSON_VALUES = [None, True, 17, 3.5, ["ordinary"], {"ordinary": "value"}]
JSON_FIELDS = ("id", "pattern", "title", "description", "status_basis")
CONSTRUCTOR_FIELDS = ("rule_id", "pattern", "title", "description", "status_basis")


@pytest.mark.parametrize("field", JSON_FIELDS)
@pytest.mark.parametrize("bad_value", BAD_JSON_VALUES, ids=lambda value: repr(value))
def test_policy_loader_rejects_non_string_text_rule_fields(field, bad_value):
    rule = dict(BASE_RULE)
    rule[field] = bad_value
    with pytest.raises(PolicyError):
        AssurancePolicy.from_dict({"id": "test.policy", "version": "1", "text": {"rules": [rule]}})


@pytest.mark.parametrize("field", CONSTRUCTOR_FIELDS)
@pytest.mark.parametrize("bad_value", BAD_JSON_VALUES, ids=lambda value: repr(value))
def test_direct_text_rule_constructor_rejects_non_string_text_fields(field, bad_value):
    values = {
        "rule_id": BASE_RULE["id"],
        "pattern": BASE_RULE["pattern"],
        "title": "Example title",
        "description": "Example description",
        "status_basis": "",
    }
    values[field] = bad_value
    with pytest.raises(PolicyError):
        TextRule(**values)


def test_policy_loader_preserves_valid_explicit_strings():
    rule = {
        **BASE_RULE,
        "title": "Human-readable title",
        "description": "A valid description.",
        "status_basis": "Approved policy PR-17.",
    }
    loaded = AssurancePolicy.from_dict({"id": "test.policy", "version": "1", "text": {"rules": [rule]}})
    parsed = loaded.text_rules[0]
    assert parsed.rule_id == rule["id"]
    assert parsed.pattern == rule["pattern"]
    assert parsed.title == rule["title"]
    assert parsed.description == rule["description"]
    assert parsed.status_basis == rule["status_basis"]


def test_policy_loader_preserves_existing_text_rule_defaults():
    loaded = AssurancePolicy.from_dict({"id": "test.policy", "version": "1", "text": {"rules": [dict(BASE_RULE)]}})
    parsed = loaded.text_rules[0]
    assert parsed.title == BASE_RULE["id"]
    assert parsed.description == "Policy text rule matched"
    assert parsed.status_basis == ""
