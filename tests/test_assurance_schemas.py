import json
from importlib.resources import files
from pathlib import Path

import jsonschema

from lycheetah.assurance import (
    AssurancePolicy,
    AssuranceRuntime,
    EvaluationCorpus,
    EvaluationGate,
    EvaluationReport,
    compare_evaluations,
    default_policy,
    evaluate_corpus,
)


ROOT = Path(__file__).resolve().parents[1]


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


def test_example_evaluation_cases_conform_to_packaged_schema():
    validator = jsonschema.Draft202012Validator(
        _schema("evaluation-case.schema.json")
    )
    path = ROOT / "examples/assurance/customer_support_eval.jsonl"
    for line in path.read_text(encoding="utf-8").splitlines():
        validator.validate(json.loads(line))


def test_evaluation_report_conforms_to_packaged_schema():
    policy = AssurancePolicy.from_json(
        ROOT / "examples/assurance/customer_support_policy.json"
    )
    corpus = EvaluationCorpus.from_jsonl(
        ROOT / "examples/assurance/customer_support_eval.jsonl"
    )
    report = evaluate_corpus(
        AssuranceRuntime(policy),
        corpus,
        gate=EvaluationGate(require_exact_match=True),
    )
    jsonschema.Draft202012Validator(
        _schema("evaluation-report.schema.json")
    ).validate(report.to_dict())


def test_committed_baseline_is_valid_and_conforms_to_schema():
    report = EvaluationReport.from_json(
        ROOT / "examples/assurance/customer_support_baseline.eval.json"
    )
    assert report.verify()
    jsonschema.Draft202012Validator(
        _schema("evaluation-report.schema.json")
    ).validate(report.to_dict())


def test_regression_report_conforms_to_packaged_schema():
    policy = AssurancePolicy.from_json(
        ROOT / "examples/assurance/customer_support_policy.json"
    )
    corpus = EvaluationCorpus.from_jsonl(
        ROOT / "examples/assurance/customer_support_eval.jsonl"
    )
    evaluation = evaluate_corpus(AssuranceRuntime(policy), corpus)
    regression = compare_evaluations(evaluation, evaluation)
    jsonschema.Draft202012Validator(
        _schema("evaluation-regression-report.schema.json")
    ).validate(regression.to_dict())
