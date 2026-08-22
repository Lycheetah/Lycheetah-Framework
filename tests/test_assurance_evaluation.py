import json
from pathlib import Path

import pytest

from lycheetah.assurance import (
    AssuranceEvent,
    AssurancePolicy,
    AssuranceRuntime,
    EvaluationCorpus,
    EvaluationError,
    EvaluationGate,
    EvaluationReport,
    evaluate_corpus,
)


ROOT = Path(__file__).resolve().parents[1]


def _write_cases(tmp_path, cases):
    path = tmp_path / "cases.jsonl"
    path.write_text(
        "\n".join(json.dumps(case) for case in cases) + "\n",
        encoding="utf-8",
    )
    return path


def _tool_case(case_id, expected, tool_name, *, weight=1.0, **event):
    return {
        "id": case_id,
        "expected": expected,
        "weight": weight,
        "event": {
            "phase": "tool",
            "tool_name": tool_name,
            "tool_arguments": {},
            **event,
        },
    }


def test_customer_support_example_is_exact_and_private():
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
    payload = report.to_dict()
    assert report.verify()
    assert report.gate_passed
    assert payload["summary"]["exact_match_rate"] == 1.0
    assert payload["summary"]["macro_f1"] == 1.0
    assert payload["summary"]["review_count"] == 3
    assert payload["corpus"]["case_count"] == 6
    assert "[EXAMPLE_CREDENTIAL]" not in report.to_json()


def test_under_and_over_enforcement_metrics(tmp_path):
    corpus = EvaluationCorpus.from_jsonl(
        _write_cases(
            tmp_path,
            [
                _tool_case("case.harmful-allow", "BLOCK", "order.read"),
                _tool_case("case.false-block", "ALLOW", "shell_exec"),
            ],
        )
    )
    report = evaluate_corpus(AssuranceRuntime(), corpus)
    summary = report.to_dict()["summary"]
    assert summary["exact_match_count"] == 0
    assert summary["under_enforcement_count"] == 1
    assert summary["over_enforcement_count"] == 1
    assert summary["harmful_allow_count"] == 1
    assert summary["false_block_count"] == 1
    assert summary["under_enforcement_rate"] == 0.5
    assert summary["over_enforcement_rate"] == 0.5


def test_case_weights_drive_primary_rates(tmp_path):
    corpus = EvaluationCorpus.from_jsonl(
        _write_cases(
            tmp_path,
            [
                _tool_case(
                    "case.weighted-under", "BLOCK", "order.read", weight=3.0
                ),
                _tool_case("case.exact-allow", "ALLOW", "order.read"),
            ],
        )
    )
    summary = evaluate_corpus(AssuranceRuntime(), corpus).to_dict()["summary"]
    assert summary["under_enforcement_count"] == 1
    assert summary["under_enforcement_rate"] == 0.75
    assert summary["exact_match_rate"] == 0.25


def test_gate_fails_on_configured_thresholds(tmp_path):
    corpus = EvaluationCorpus.from_jsonl(
        _write_cases(
            tmp_path,
            [_tool_case("case.harmful-allow", "BLOCK", "order.read")],
        )
    )
    report = evaluate_corpus(
        AssuranceRuntime(),
        corpus,
        gate=EvaluationGate(
            require_exact_match=True,
            max_under_enforcement_rate=0.0,
            max_harmful_allows=0,
            min_macro_f1=1.0,
        ),
    )
    gate = report.to_dict()["gate"]
    assert report.gate_passed is False
    assert len(gate["failures"]) == 4


def test_unconfigured_gate_is_report_only(tmp_path):
    corpus = EvaluationCorpus.from_jsonl(
        _write_cases(
            tmp_path,
            [_tool_case("case.mismatch", "BLOCK", "order.read")],
        )
    )
    gate = evaluate_corpus(AssuranceRuntime(), corpus).to_dict()["gate"]
    assert gate["configured"] is False
    assert gate["passed"] is True


def test_report_is_deterministic_for_same_policy_and_corpus(tmp_path):
    corpus = EvaluationCorpus.from_jsonl(
        _write_cases(
            tmp_path,
            [_tool_case("case.stable", "ALLOW", "order.read")],
        )
    )
    first = evaluate_corpus(AssuranceRuntime(), corpus)
    second = evaluate_corpus(AssuranceRuntime(), corpus)
    assert first.digest == second.digest
    assert first.to_dict() == second.to_dict()


def test_report_round_trip_and_mutation_detection(tmp_path):
    corpus = EvaluationCorpus.from_jsonl(
        _write_cases(
            tmp_path,
            [_tool_case("case.report-roundtrip", "ALLOW", "order.read")],
        )
    )
    report = evaluate_corpus(AssuranceRuntime(), corpus)
    path = tmp_path / "report.json"
    path.write_text(report.to_json(), encoding="utf-8")
    loaded = EvaluationReport.from_json(path)
    assert loaded.verify()
    payload = loaded.to_dict()
    payload["summary"]["exact_match_count"] = 0
    path.write_text(json.dumps(payload), encoding="utf-8")
    assert EvaluationReport.from_json(path).verify() is False


def test_report_loader_rejects_duplicate_keys(tmp_path):
    path = tmp_path / "duplicate-report.json"
    path.write_text('{"schema_version":"0.1","schema_version":"0.1"}', encoding="utf-8")
    with pytest.raises(EvaluationError, match="duplicate JSON object key"):
        EvaluationReport.from_json(path)


def test_corpus_digest_ignores_json_whitespace(tmp_path):
    case = _tool_case("case.spacing", "ALLOW", "order.read")
    compact = tmp_path / "compact.jsonl"
    pretty = tmp_path / "pretty.jsonl"
    compact.write_text(json.dumps(case, separators=(",", ":")) + "\n", encoding="utf-8")
    pretty.write_text(json.dumps(case, indent=2) + "\n", encoding="utf-8")
    first = EvaluationCorpus.from_jsonl(compact)
    with pytest.raises(EvaluationError, match="line 1"):
        EvaluationCorpus.from_jsonl(pretty)
    normalized = tmp_path / "normalized.jsonl"
    normalized.write_text("  " + json.dumps(case) + "  \n", encoding="utf-8")
    assert first.digest == EvaluationCorpus.from_jsonl(normalized).digest


@pytest.mark.parametrize(
    "line,error",
    [
        ("", "contains no cases"),
        ('{"id":"case.duplicate-key","id":"case.other","expected":"ALLOW","event":{"phase":"tool","tool_name":"x"}}', "duplicate JSON object key"),
        ('{"id":"case.unknown","expected":"ALLOW","event":{"phase":"tool","tool_name":"x"},"surprise":1}', "unknown fields"),
        ('{"id":"case.bad-bool","expected":"ALLOW","event":{"phase":"tool","tool_name":"x","side_effect":"false"}}', "must be a boolean"),
        ('{"id":"case.bad-weight","expected":"ALLOW","weight":true,"event":{"phase":"tool","tool_name":"x"}}', "weight must be"),
        ('{"id":"case.bad-tags","expected":"ALLOW","tags":["x","x"],"event":{"phase":"tool","tool_name":"x"}}', "must not contain duplicates"),
    ],
)
def test_corpus_rejects_ambiguous_or_unknown_data(tmp_path, line, error):
    path = tmp_path / "invalid.jsonl"
    path.write_text(line + ("\n" if line else ""), encoding="utf-8")
    with pytest.raises(EvaluationError, match=error):
        EvaluationCorpus.from_jsonl(path)


def test_corpus_rejects_duplicate_case_ids(tmp_path):
    case = _tool_case("case.duplicate", "ALLOW", "order.read")
    with pytest.raises(EvaluationError, match="duplicate evaluation case id"):
        EvaluationCorpus.from_jsonl(_write_cases(tmp_path, [case, case]))


@pytest.mark.parametrize(
    "kwargs",
    [
        {"max_under_enforcement_rate": -0.1},
        {"max_under_enforcement_rate": float("nan")},
        {"max_harmful_allows": -1},
        {"max_false_blocks": 1.5},
        {"min_macro_f1": 1.1},
        {"require_exact_match": "true"},
    ],
)
def test_gate_rejects_invalid_thresholds(kwargs):
    with pytest.raises(EvaluationError):
        EvaluationGate(**kwargs)


def test_event_from_dict_is_strict():
    with pytest.raises(ValueError, match="unknown fields"):
        AssuranceEvent.from_dict(
            {"phase": "tool", "tool_name": "demo", "unexpected": True}
        )
    with pytest.raises(TypeError, match="side_effect"):
        AssuranceEvent.from_dict(
            {"phase": "tool", "tool_name": "demo", "side_effect": "false"}
        )
