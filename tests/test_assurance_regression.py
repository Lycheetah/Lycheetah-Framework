import json

import pytest

from lycheetah.assurance import (
    AssurancePolicy,
    AssuranceRuntime,
    EvaluationCorpus,
    EvaluationError,
    EvaluationReport,
    RegressionGate,
    RegressionReport,
    compare_evaluations,
    evaluate_corpus,
)


def _write_cases(tmp_path, cases, name="cases.jsonl"):
    path = tmp_path / name
    path.write_text(
        "\n".join(json.dumps(case) for case in cases) + "\n",
        encoding="utf-8",
    )
    return path


def _tool_case(case_id, expected, tool_name, *, weight=1.0, tags=None):
    return {
        "id": case_id,
        "expected": expected,
        "weight": weight,
        "tags": tags or [],
        "event": {"phase": "tool", "tool_name": tool_name},
    }


def _policy(policy_id, denied=(), review=()):
    return AssurancePolicy(
        policy_id=policy_id,
        version="1",
        denied_tools=tuple(denied),
        review_tools=tuple(review),
        blocked_scopes=(),
    )


def _report(corpus, policy):
    return evaluate_corpus(AssuranceRuntime(policy), corpus)


def test_identical_reports_pass_strict_default_and_are_deterministic(tmp_path):
    corpus = EvaluationCorpus.from_jsonl(
        _write_cases(
            tmp_path,
            [_tool_case("case.safe-read", "ALLOW", "safe.read", tags=["safe"])],
        )
    )
    baseline = _report(corpus, _policy("test.same"))
    first = compare_evaluations(baseline, baseline)
    second = compare_evaluations(baseline, baseline)
    payload = first.to_dict()
    assert first.verify()
    assert first.gate_passed
    assert first.digest == second.digest
    assert payload["summary"]["changed_case_count"] == 0
    assert payload["summary"]["unchanged_case_count"] == 1
    assert payload["cases"] == []


def test_detects_safety_and_usability_regressions(tmp_path):
    corpus = EvaluationCorpus.from_jsonl(
        _write_cases(
            tmp_path,
            [
                _tool_case("case.danger", "BLOCK", "danger", weight=3.0),
                _tool_case("case.safe", "ALLOW", "safe"),
            ],
        )
    )
    baseline = _report(corpus, _policy("test.baseline", denied=("danger",)))
    candidate = _report(corpus, _policy("test.candidate", denied=("safe",)))
    report = compare_evaluations(baseline, candidate)
    summary = report.to_dict()["summary"]
    assert report.gate_passed is False
    assert summary["regressed_case_count"] == 2
    assert summary["regressed_weight"] == 4.0
    assert summary["new_under_enforcement_count"] == 1
    assert summary["new_harmful_allow_count"] == 1
    assert summary["new_false_block_count"] == 1
    assert summary["metric_deltas"]["exact_match_rate"] == -1.0
    assert {case["id"] for case in report.to_dict()["cases"]} == {
        "case.danger",
        "case.safe",
    }


def test_improvement_resolves_under_enforcement_without_failing(tmp_path):
    corpus = EvaluationCorpus.from_jsonl(
        _write_cases(
            tmp_path,
            [_tool_case("case.danger", "BLOCK", "danger")],
        )
    )
    baseline = _report(corpus, _policy("test.baseline"))
    candidate = _report(corpus, _policy("test.candidate", denied=("danger",)))
    report = compare_evaluations(baseline, candidate)
    summary = report.to_dict()["summary"]
    assert report.gate_passed
    assert summary["improved_case_count"] == 1
    assert summary["resolved_under_enforcement_count"] == 1
    assert summary["resolved_harmful_allow_count"] == 1
    assert summary["metric_deltas"]["exact_match_rate"] == 1.0


def test_cross_direction_review_change_is_a_tradeoff(tmp_path):
    corpus = EvaluationCorpus.from_jsonl(
        _write_cases(
            tmp_path,
            [_tool_case("case.review", "REVIEW", "maybe")],
        )
    )
    baseline = _report(corpus, _policy("test.baseline"))
    candidate = _report(corpus, _policy("test.candidate", denied=("maybe",)))
    report = compare_evaluations(baseline, candidate)
    changed = report.to_dict()["cases"][0]
    assert report.gate_passed is False
    assert changed["classification"] == "TRADEOFF"
    assert changed["enforcement_change"] == "INCREASED"
    assert changed["signals"] == ["RESOLVED_UNDER_ENFORCEMENT"]


def test_thresholds_can_deliberately_accept_a_known_regression(tmp_path):
    corpus = EvaluationCorpus.from_jsonl(
        _write_cases(tmp_path, [_tool_case("case.block", "BLOCK", "danger")])
    )
    baseline = _report(corpus, _policy("test.baseline", denied=("danger",)))
    candidate = _report(corpus, _policy("test.candidate"))
    gate = RegressionGate(
        max_regressed_cases=1,
        max_new_under_enforcement=1,
        max_new_harmful_allows=1,
        max_exact_match_rate_drop=1.0,
        max_macro_f1_drop=1.0,
    )
    assert compare_evaluations(baseline, candidate, gate=gate).gate_passed


def test_comparison_rejects_different_corpora(tmp_path):
    first = EvaluationCorpus.from_jsonl(
        _write_cases(
            tmp_path,
            [_tool_case("case.first", "ALLOW", "safe")],
            "first.jsonl",
        )
    )
    second = EvaluationCorpus.from_jsonl(
        _write_cases(
            tmp_path,
            [_tool_case("case.second", "ALLOW", "safe")],
            "second.jsonl",
        )
    )
    with pytest.raises(EvaluationError, match="corpus sha256 differ"):
        compare_evaluations(
            _report(first, _policy("test.first")),
            _report(second, _policy("test.second")),
        )


def test_comparison_rejects_invalid_evaluation_digest(tmp_path):
    corpus = EvaluationCorpus.from_jsonl(
        _write_cases(tmp_path, [_tool_case("case.valid", "ALLOW", "safe")])
    )
    valid = _report(corpus, _policy("test.valid"))
    invalid = EvaluationReport(body=valid.body, digest="0" * 64)
    with pytest.raises(EvaluationError, match="baseline evaluation report digest is invalid"):
        compare_evaluations(invalid, valid)


def test_comparison_rejects_self_hashed_but_inconsistent_evaluation(tmp_path):
    corpus = EvaluationCorpus.from_jsonl(
        _write_cases(tmp_path, [_tool_case("case.consistent", "ALLOW", "safe")])
    )
    valid = _report(corpus, _policy("test.consistent"))
    body = dict(valid.body)
    body["summary"] = {**body["summary"], "exact_match_count": 0}
    inconsistent = EvaluationReport.issue(body)
    assert inconsistent.verify()
    with pytest.raises(EvaluationError, match="summary exact_match_count is inconsistent"):
        compare_evaluations(inconsistent, valid)


def test_regression_report_round_trip_and_mutation_detection(tmp_path):
    corpus = EvaluationCorpus.from_jsonl(
        _write_cases(tmp_path, [_tool_case("case.roundtrip", "ALLOW", "safe")])
    )
    evaluation = _report(corpus, _policy("test.roundtrip"))
    report = compare_evaluations(evaluation, evaluation)
    path = tmp_path / "regression.json"
    path.write_text(report.to_json(), encoding="utf-8")
    loaded = RegressionReport.from_json(path)
    assert loaded.verify()
    payload = loaded.to_dict()
    payload["limitations"][0] = "Mutated but structurally valid limitation."
    path.write_text(json.dumps(payload), encoding="utf-8")
    assert RegressionReport.from_json(path).verify() is False


def test_regression_report_rejects_inconsistent_summary(tmp_path):
    corpus = EvaluationCorpus.from_jsonl(
        _write_cases(tmp_path, [_tool_case("case.semantic", "ALLOW", "safe")])
    )
    evaluation = _report(corpus, _policy("test.semantic"))
    payload = compare_evaluations(evaluation, evaluation).to_dict()
    payload["summary"]["unchanged_weight"] = 0.0
    with pytest.raises(EvaluationError, match="classification weights are inconsistent"):
        RegressionReport.from_dict(payload)


@pytest.mark.parametrize(
    "kwargs",
    [
        {"max_regressed_cases": -1},
        {"max_tradeoff_cases": True},
        {"max_new_harmful_allows": 0.5},
        {"max_exact_match_rate_drop": float("nan")},
        {"max_macro_f1_drop": 1.1},
    ],
)
def test_regression_gate_rejects_invalid_thresholds(kwargs):
    with pytest.raises(EvaluationError):
        RegressionGate(**kwargs)


def test_regression_report_loader_rejects_duplicate_keys(tmp_path):
    path = tmp_path / "duplicate.json"
    path.write_text('{"schema_version":"0.1","schema_version":"0.1"}')
    with pytest.raises(EvaluationError, match="duplicate JSON object key"):
        RegressionReport.from_json(path)
