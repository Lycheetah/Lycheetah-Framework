import json
from importlib.resources import files

import jsonschema

from lycheetah.assurance import AssuranceRuntime, default_policy


def _schema(name):
    path = files("lycheetah.assurance").joinpath("schemas", name)
    return json.loads(path.read_text(encoding="utf-8"))


def test_default_policy_conforms_to_packaged_schema():
    jsonschema.Draft202012Validator(_schema("policy.schema.json")).validate(
        default_policy().to_dict()
    )


def test_receipt_conforms_to_packaged_schema():
    receipt = AssuranceRuntime().evaluate_tool(
        "cancel_order", {"order_id": 8}, side_effect=True
    )
    jsonschema.Draft202012Validator(_schema("receipt.schema.json")).validate(
        receipt.to_dict()
    )
