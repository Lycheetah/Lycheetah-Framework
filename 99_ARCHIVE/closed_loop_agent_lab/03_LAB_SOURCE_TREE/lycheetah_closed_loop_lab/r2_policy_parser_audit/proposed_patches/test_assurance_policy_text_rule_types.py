"""Regression tests for strict JSON types in policy text-rule parsing.

Intended to be copied into tests/ after applying strict_text_rule_parser.patch
on the matching Lycheetah-Framework source revision.
"""
import pytest

from lycheetah.assurance import AssurancePolicy, PolicyError

BASE_RULE = {"id": "customer.rule-01", "pattern": r"\bhello\b"}
BAD_JSON_VALUES = [None, True, 17, 3.5, ["ordinary"], {"ordinary": "value"}]
FIELDS = ("id", "pattern", "title", "description")


@pytest.mark.parametrize("field", FIELDS)
@pytest.mark.parametrize("bad_value", BAD_JSON_VALUES, ids=lambda value: repr(value))
def test_policy_loader_rejects_non_string_text_rule_fields(field, bad_value):
    rule = dict(BASE_RULE)
    rule[field] = bad_value
    policy = {
        "id": "test.policy",
        "version": "1",
        "text": {"rules": [rule]},
    }
    with pytest.raises(PolicyError):
        AssurancePolicy.from_dict(policy)


def test_policy_loader_preserves_valid_explicit_strings():
    rule = {
        **BASE_RULE,
        "title": "Human-readable title",
        "description": "A valid description.",
    }
    loaded = AssurancePolicy.from_dict(
        {"id": "test.policy", "version": "1", "text": {"rules": [rule]}}
    )
    parsed = loaded.text_rules[0]
    assert parsed.rule_id == rule["id"]
    assert parsed.pattern == rule["pattern"]
    assert parsed.title == rule["title"]
    assert parsed.description == rule["description"]


def test_policy_loader_preserves_existing_text_rule_defaults():
    loaded = AssurancePolicy.from_dict(
        {
            "id": "test.policy",
            "version": "1",
            "text": {"rules": [dict(BASE_RULE)]},
        }
    )
    parsed = loaded.text_rules[0]
    assert parsed.title == BASE_RULE["id"]
    assert parsed.description == "Policy text rule matched"
