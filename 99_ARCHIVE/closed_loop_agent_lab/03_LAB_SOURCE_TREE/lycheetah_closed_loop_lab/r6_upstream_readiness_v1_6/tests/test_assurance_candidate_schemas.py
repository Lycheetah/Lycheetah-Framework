"""Checks that installed strict candidate schemas preserve normal generated data."""
import json
from importlib.resources import files
from pathlib import Path

import jsonschema
import pytest

from lycheetah.assurance import AssurancePolicy, AssuranceRuntime, PolicyError


def _schema(name):
    path = files("lycheetah.assurance").joinpath("schemas", name)
    return json.loads(path.read_text(encoding="utf-8"))


def test_default_policy_conforms_to_candidate_schema():
    schema = _schema("policy.schema.json")
    jsonschema.Draft202012Validator(schema).validate(AssurancePolicy().to_dict())


def test_generated_receipt_conforms_to_candidate_schema():
    receipt = AssuranceRuntime().evaluate_tool("lookup_order", {"order_id": 7})
    jsonschema.Draft202012Validator(_schema("receipt.schema.json")).validate(receipt.to_dict())


def test_schema_rejects_non_string_policy_rule_pattern():
    schema = _schema("policy.schema.json")
    payload = {"id": "test.policy", "version": "1", "text": {"rules": [{"id": "test.rule", "pattern": True}]}}
    with pytest.raises(jsonschema.ValidationError):
        jsonschema.Draft202012Validator(schema).validate(payload)


def test_schema_rejects_unknown_finding_property():
    schema = _schema("receipt.schema.json")
    receipt = AssuranceRuntime().evaluate_tool("lookup_order", {"order_id": 7}).to_dict()
    receipt["findings"][0]["untrusted_extension"] = True
    with pytest.raises(jsonschema.ValidationError):
        jsonschema.Draft202012Validator(schema).validate(receipt)


def test_schema_rejects_unknown_control_property():
    schema = _schema("receipt.schema.json")
    receipt = AssuranceRuntime().evaluate_tool("lookup_order", {"order_id": 7}).to_dict()
    receipt["findings"][0]["controls"] = [{"framework": "f", "control_id": "c", "title": "t", "extra": 1}]
    with pytest.raises(jsonschema.ValidationError):
        jsonschema.Draft202012Validator(schema).validate(receipt)


def test_policy_parser_still_rejects_invalid_regex():
    payload = {"id": "test.policy", "version": "1", "text": {"rules": [{"id": "test.rule", "pattern": "["}]}}
    with pytest.raises(PolicyError):
        AssurancePolicy.from_dict(payload)
