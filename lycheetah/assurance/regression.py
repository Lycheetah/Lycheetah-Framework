"""Deterministic same-corpus comparison for assurance evaluation reports.

Status: [SCAFFOLD]. A regression report measures changes relative to a supplied
baseline. It does not establish that the baseline labels, policy, or decisions
are correct, safe, lawful, representative, or independently approved.
"""

from __future__ import annotations

import json
import math
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping, Optional, Sequence

from .evaluation import (
    EvaluationError,
    EvaluationReport,
    MAX_REPORT_CHARACTERS,
    _metrics,
)
from .jsonutil import jsonable, sha256_json
from .models import DISPOSITION_ORDER, Disposition


REGRESSION_SCHEMA_VERSION = "0.1"
_SHA256 = re.compile(r"[0-9a-f]{64}")
_CLASSIFICATIONS = {"UNCHANGED", "IMPROVED", "REGRESSED", "TRADEOFF"}
_ENFORCEMENT_CHANGES = {"UNCHANGED", "INCREASED", "DECREASED"}
_SIGNALS = {
    "NEW_UNDER_ENFORCEMENT",
    "RESOLVED_UNDER_ENFORCEMENT",
    "NEW_HARMFUL_ALLOW",
    "RESOLVED_HARMFUL_ALLOW",
    "NEW_FALSE_BLOCK",
    "RESOLVED_FALSE_BLOCK",
}
_SUMMARY_FIELDS = {
    "case_count",
    "changed_case_count",
    "unchanged_case_count",
    "unchanged_weight",
    "improved_case_count",
    "improved_weight",
    "regressed_case_count",
    "regressed_weight",
    "tradeoff_case_count",
    "tradeoff_weight",
    "new_under_enforcement_count",
    "resolved_under_enforcement_count",
    "new_harmful_allow_count",
    "resolved_harmful_allow_count",
    "new_false_block_count",
    "resolved_false_block_count",
    "metric_deltas",
}
_METRIC_DELTA_FIELDS = {
    "exact_match_rate",
    "under_enforcement_rate",
    "over_enforcement_rate",
    "review_rate",
    "macro_f1",
    "harmful_allow_count",
    "false_block_count",
}
_THRESHOLD_FIELDS = {
    "max_regressed_cases",
    "max_tradeoff_cases",
    "max_new_under_enforcement",
    "max_new_harmful_allows",
    "max_new_false_blocks",
    "max_exact_match_rate_drop",
    "max_macro_f1_drop",
}
_EVALUATION_SUMMARY_FIELDS = {
    "case_count",
    "total_weight",
    "exact_match_count",
    "exact_match_rate",
    "under_enforcement_count",
    "under_enforcement_rate",
    "over_enforcement_count",
    "over_enforcement_rate",
    "harmful_allow_count",
    "harmful_allow_weight",
    "false_block_count",
    "false_block_weight",
    "review_count",
    "review_rate",
    "macro_f1",
}
_EVALUATION_CASE_FIELDS = {
    "id",
    "expected",
    "actual",
    "exact_match",
    "direction",
    "weight",
    "tags",
    "subject_sha256",
    "findings",
}


@dataclass(frozen=True)
class RegressionGate:
    """Strict-by-default limits for a baseline-to-candidate comparison."""

    max_regressed_cases: int = 0
    max_tradeoff_cases: int = 0
    max_new_under_enforcement: int = 0
    max_new_harmful_allows: int = 0
    max_new_false_blocks: int = 0
    max_exact_match_rate_drop: float = 0.0
    max_macro_f1_drop: float = 0.0

    def __post_init__(self) -> None:
        for name in (
            "max_regressed_cases",
            "max_tradeoff_cases",
            "max_new_under_enforcement",
            "max_new_harmful_allows",
            "max_new_false_blocks",
        ):
            value = getattr(self, name)
            if isinstance(value, bool) or not isinstance(value, int) or value < 0:
                raise EvaluationError(f"{name} must be a non-negative integer")
        for name in ("max_exact_match_rate_drop", "max_macro_f1_drop"):
            value = getattr(self, name)
            if (
                isinstance(value, bool)
                or not isinstance(value, (int, float))
                or not math.isfinite(value)
                or not 0.0 <= value <= 1.0
            ):
                raise EvaluationError(f"{name} must be in [0, 1]")
            object.__setattr__(self, name, float(value))

    def assess(self, summary: Mapping[str, Any]) -> dict[str, Any]:
        """Apply thresholds to a validated comparison summary."""

        failures: list[str] = []
        count_limits = (
            ("regressed_case_count", "max_regressed_cases"),
            ("tradeoff_case_count", "max_tradeoff_cases"),
            ("new_under_enforcement_count", "max_new_under_enforcement"),
            ("new_harmful_allow_count", "max_new_harmful_allows"),
            ("new_false_block_count", "max_new_false_blocks"),
        )
        for metric, threshold in count_limits:
            if summary[metric] > getattr(self, threshold):
                failures.append(f"{metric} exceeds {getattr(self, threshold)}")

        deltas = summary["metric_deltas"]
        if deltas["exact_match_rate"] < -self.max_exact_match_rate_drop:
            failures.append(
                "exact_match_rate drop exceeds "
                f"{self.max_exact_match_rate_drop}"
            )
        if deltas["macro_f1"] < -self.max_macro_f1_drop:
            failures.append(
                f"macro_f1 drop exceeds {self.max_macro_f1_drop}"
            )
        return {
            "configured": True,
            "passed": not failures,
            "thresholds": {
                name: getattr(self, name) for name in sorted(_THRESHOLD_FIELDS)
            },
            "failures": failures,
        }


@dataclass(frozen=True)
class RegressionReport:
    """Integrity-protected, privacy-minimised evaluation comparison."""

    body: Mapping[str, Any]
    digest: str

    @classmethod
    def issue(cls, body: Mapping[str, Any]) -> "RegressionReport":
        normalized = jsonable(body)
        _validate_regression_body(normalized)
        return cls(body=normalized, digest=sha256_json(normalized))

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> "RegressionReport":
        if not isinstance(data, Mapping):
            raise EvaluationError("regression report must be a JSON object")
        body_fields = {
            "schema_version",
            "status",
            "baseline",
            "candidate",
            "corpus",
            "summary",
            "cases",
            "gate",
            "limitations",
        }
        allowed = body_fields | {"integrity"}
        _require_exact_fields(data, allowed, "regression report")
        integrity = _require_mapping(data["integrity"], "regression report integrity")
        _require_exact_fields(
            integrity,
            {"algorithm", "canonicalization", "digest"},
            "regression report integrity",
        )
        if integrity["algorithm"] != "sha256":
            raise EvaluationError("regression report integrity algorithm must be sha256")
        if integrity["canonicalization"] != "lycheetah-json-v1":
            raise EvaluationError(
                "regression report canonicalization must be lycheetah-json-v1"
            )
        digest = integrity["digest"]
        if not isinstance(digest, str) or not _SHA256.fullmatch(digest):
            raise EvaluationError(
                "regression report digest must be 64 lowercase hexadecimal characters"
            )
        body = {key: data[key] for key in body_fields}
        normalized = jsonable(body)
        _validate_regression_body(normalized)
        return cls(body=normalized, digest=digest)

    @classmethod
    def from_json(cls, path: str | Path) -> "RegressionReport":
        source = Path(path)
        try:
            text = source.read_text(encoding="utf-8")
        except OSError as exc:
            raise EvaluationError(f"cannot read regression report {source}: {exc}") from exc
        if len(text) > MAX_REPORT_CHARACTERS:
            raise EvaluationError(
                f"regression report exceeds {MAX_REPORT_CHARACTERS} characters"
            )
        try:
            data = json.loads(text, object_pairs_hook=_unique_object)
        except (json.JSONDecodeError, EvaluationError) as exc:
            raise EvaluationError(f"invalid regression report JSON: {exc}") from exc
        return cls.from_dict(data)

    def to_dict(self) -> dict[str, Any]:
        return {
            **jsonable(self.body),
            "integrity": {
                "algorithm": "sha256",
                "canonicalization": "lycheetah-json-v1",
                "digest": self.digest,
            },
        }

    def to_json(self, *, indent: Optional[int] = 2) -> str:
        return json.dumps(
            self.to_dict(),
            ensure_ascii=False,
            allow_nan=False,
            sort_keys=indent is None,
            separators=(",", ":") if indent is None else None,
            indent=indent,
        )

    def verify(self) -> bool:
        return self.digest == sha256_json(self.body)

    @property
    def gate_passed(self) -> bool:
        return bool(self.body["gate"]["passed"])


def compare_evaluations(
    baseline: EvaluationReport,
    candidate: EvaluationReport,
    *,
    gate: Optional[RegressionGate] = None,
) -> RegressionReport:
    """Compare two valid reports for the same normalized evaluation corpus."""

    baseline_view = _evaluation_view(baseline, "baseline")
    candidate_view = _evaluation_view(candidate, "candidate")
    if baseline_view["corpus"]["sha256"] != candidate_view["corpus"]["sha256"]:
        raise EvaluationError(
            "baseline and candidate corpus sha256 differ; regenerate or explicitly "
            "review the baseline instead of comparing unlike corpora"
        )
    if baseline_view["corpus"]["case_count"] != candidate_view["corpus"]["case_count"]:
        raise EvaluationError("baseline and candidate corpus case counts differ")
    if set(baseline_view["cases"]) != set(candidate_view["cases"]):
        raise EvaluationError("baseline and candidate case identifiers differ")

    counters: dict[str, int] = {
        "unchanged_case_count": 0,
        "improved_case_count": 0,
        "regressed_case_count": 0,
        "tradeoff_case_count": 0,
        "new_under_enforcement_count": 0,
        "resolved_under_enforcement_count": 0,
        "new_harmful_allow_count": 0,
        "resolved_harmful_allow_count": 0,
        "new_false_block_count": 0,
        "resolved_false_block_count": 0,
    }
    weights = {
        "unchanged_weight": 0.0,
        "improved_weight": 0.0,
        "regressed_weight": 0.0,
        "tradeoff_weight": 0.0,
    }
    changed_cases: list[dict[str, Any]] = []

    for case_id in sorted(baseline_view["cases"]):
        base_case = baseline_view["cases"][case_id]
        candidate_case = candidate_view["cases"][case_id]
        _require_case_identity(base_case, candidate_case, case_id)
        expected = Disposition(base_case["expected"])
        baseline_actual = Disposition(base_case["actual"])
        candidate_actual = Disposition(candidate_case["actual"])
        classification = _classify_change(expected, baseline_actual, candidate_actual)
        counters[f"{classification.lower()}_case_count"] += 1
        weights[f"{classification.lower()}_weight"] += base_case["weight"]

        signals = _change_signals(expected, baseline_actual, candidate_actual)
        for signal in signals:
            counters[f"{signal.lower()}_count"] += 1
        if classification == "UNCHANGED":
            continue
        rank_delta = (
            DISPOSITION_ORDER[candidate_actual] - DISPOSITION_ORDER[baseline_actual]
        )
        changed_cases.append(
            {
                "id": case_id,
                "expected": expected.value,
                "baseline_actual": baseline_actual.value,
                "candidate_actual": candidate_actual.value,
                "classification": classification,
                "enforcement_change": (
                    "INCREASED" if rank_delta > 0 else "DECREASED"
                ),
                "weight": base_case["weight"],
                "tags": list(base_case["tags"]),
                "subject_sha256": base_case["subject_sha256"],
                "signals": signals,
            }
        )

    baseline_summary = baseline_view["summary"]
    candidate_summary = candidate_view["summary"]
    deltas = {
        key: candidate_summary[key] - baseline_summary[key]
        for key in (
            "exact_match_rate",
            "under_enforcement_rate",
            "over_enforcement_rate",
            "review_rate",
            "macro_f1",
            "harmful_allow_count",
            "false_block_count",
        )
    }
    summary = {
        "case_count": baseline_view["corpus"]["case_count"],
        "changed_case_count": len(changed_cases),
        **counters,
        **weights,
        "metric_deltas": deltas,
    }
    active_gate = gate or RegressionGate()
    body = {
        "schema_version": REGRESSION_SCHEMA_VERSION,
        "status": "SCAFFOLD",
        "baseline": _report_reference(baseline, baseline_view),
        "candidate": _report_reference(candidate, candidate_view),
        "corpus": candidate_view["corpus"],
        "summary": summary,
        "cases": changed_cases,
        "gate": active_gate.assess(summary),
        "limitations": [
            "The comparison inherits caller-supplied labels and does not establish ground truth.",
            "A baseline is a change reference, not evidence that its policy or decisions are safe, lawful, calibrated, or approved.",
            "The report compares one identical normalized corpus and does not establish out-of-sample performance or statistical significance.",
            "More restrictive and less restrictive decisions can create different harms; TRADEOFF cases require human review.",
            "Raw event content and tool arguments remain excluded; case identifiers, tags, and subject hashes still require appropriate governance.",
        ],
    }
    return RegressionReport.issue(body)


def _evaluation_view(report: EvaluationReport, label: str) -> dict[str, Any]:
    if not isinstance(report, EvaluationReport):
        raise EvaluationError(f"{label} must be an EvaluationReport")
    if not report.verify():
        raise EvaluationError(f"{label} evaluation report digest is invalid")
    body = _require_mapping(report.body, f"{label} evaluation report body")
    runtime = _require_mapping(body.get("runtime"), f"{label} runtime")
    _require_exact_fields(runtime, {"name", "version"}, f"{label} runtime")
    for field in ("name", "version"):
        _require_non_empty_string(runtime[field], f"{label} runtime {field}")

    policy = _require_mapping(body.get("policy"), f"{label} policy")
    _require_exact_fields(policy, {"id", "version", "sha256"}, f"{label} policy")
    _require_non_empty_string(policy["id"], f"{label} policy id")
    _require_non_empty_string(policy["version"], f"{label} policy version")
    _require_sha256(policy["sha256"], f"{label} policy sha256")

    corpus = _require_mapping(body.get("corpus"), f"{label} corpus")
    _require_exact_fields(
        corpus,
        {"source_name", "sha256", "case_count", "total_weight", "tags"},
        f"{label} corpus",
    )
    _require_non_empty_string(corpus["source_name"], f"{label} corpus source_name")
    _require_sha256(corpus["sha256"], f"{label} corpus sha256")
    case_count = _require_non_negative_int(corpus["case_count"], f"{label} case_count")
    if case_count == 0:
        raise EvaluationError(f"{label} corpus case_count must be positive")
    total_weight = _require_positive_number(
        corpus["total_weight"], f"{label} corpus total_weight"
    )
    tags = _require_string_list(corpus["tags"], f"{label} corpus tags", unique=True)

    summary = _require_mapping(body.get("summary"), f"{label} summary")
    _require_exact_fields(summary, _EVALUATION_SUMMARY_FIELDS, f"{label} summary")
    for field in (
        "exact_match_rate",
        "under_enforcement_rate",
        "over_enforcement_rate",
        "review_rate",
        "macro_f1",
    ):
        _require_rate(summary.get(field), f"{label} summary {field}")
    for field in (
        "case_count",
        "under_enforcement_count",
        "over_enforcement_count",
        "harmful_allow_count",
        "false_block_count",
    ):
        _require_non_negative_int(summary.get(field), f"{label} summary {field}")
    if summary["case_count"] != case_count:
        raise EvaluationError(f"{label} summary and corpus case_count differ")

    cases_raw = body.get("cases")
    if not isinstance(cases_raw, list):
        raise EvaluationError(f"{label} cases must be an array")
    if len(cases_raw) != case_count:
        raise EvaluationError(f"{label} cases length does not match corpus case_count")
    cases: dict[str, dict[str, Any]] = {}
    confusion_counts = {
        expected.value: {actual.value: 0 for actual in Disposition}
        for expected in Disposition
    }
    confusion_weights = {
        expected.value: {actual.value: 0.0 for actual in Disposition}
        for expected in Disposition
    }
    for index, item in enumerate(cases_raw):
        case = _require_mapping(item, f"{label} case {index}")
        _require_exact_fields(case, _EVALUATION_CASE_FIELDS, f"{label} case {index}")
        case_id = _require_non_empty_string(case.get("id"), f"{label} case id")
        if case_id in cases:
            raise EvaluationError(f"{label} contains duplicate case id {case_id!r}")
        expected = _require_disposition(case.get("expected"), f"{label} {case_id} expected")
        actual = _require_disposition(case.get("actual"), f"{label} {case_id} actual")
        direction = case.get("direction")
        expected_direction = _direction(expected, actual)
        if direction != expected_direction:
            raise EvaluationError(
                f"{label} {case_id} direction is inconsistent with expected and actual"
            )
        exact_match = case.get("exact_match")
        if type(exact_match) is not bool or exact_match is not (expected == actual):
            raise EvaluationError(f"{label} {case_id} exact_match is inconsistent")
        weight = _require_positive_number(case.get("weight"), f"{label} {case_id} weight")
        case_tags = _require_string_list(
            case.get("tags"), f"{label} {case_id} tags", unique=True
        )
        subject_sha256 = _require_sha256(
            case.get("subject_sha256"), f"{label} {case_id} subject_sha256"
        )
        if not isinstance(case["findings"], list):
            raise EvaluationError(f"{label} {case_id} findings must be an array")
        confusion_counts[expected.value][actual.value] += 1
        confusion_weights[expected.value][actual.value] += weight
        cases[case_id] = {
            "id": case_id,
            "expected": expected.value,
            "actual": actual.value,
            "weight": weight,
            "tags": case_tags,
            "subject_sha256": subject_sha256,
        }

    recomputed_summary, _ = _metrics(confusion_counts, confusion_weights)
    for field, recomputed in recomputed_summary.items():
        supplied = summary[field]
        if isinstance(recomputed, float):
            if (
                isinstance(supplied, bool)
                or not isinstance(supplied, (int, float))
                or not math.isfinite(supplied)
                or not math.isclose(
                    float(supplied), recomputed, rel_tol=0.0, abs_tol=1e-12
                )
            ):
                raise EvaluationError(f"{label} summary {field} is inconsistent")
        elif supplied != recomputed:
            raise EvaluationError(f"{label} summary {field} is inconsistent")
    if not math.isclose(
        total_weight,
        recomputed_summary["total_weight"],
        rel_tol=0.0,
        abs_tol=1e-12,
    ):
        raise EvaluationError(f"{label} corpus total_weight is inconsistent")
    observed_tags = sorted({tag for case in cases.values() for tag in case["tags"]})
    if tags != observed_tags:
        raise EvaluationError(f"{label} corpus tags are inconsistent")

    return {
        "runtime": dict(runtime),
        "policy": dict(policy),
        "corpus": {
            "source_name": corpus["source_name"],
            "sha256": corpus["sha256"],
            "case_count": case_count,
            "total_weight": total_weight,
            "tags": tags,
        },
        "summary": dict(summary),
        "cases": cases,
    }


def _require_case_identity(
    baseline: Mapping[str, Any], candidate: Mapping[str, Any], case_id: str
) -> None:
    for field in ("expected", "weight", "tags", "subject_sha256"):
        if baseline[field] != candidate[field]:
            raise EvaluationError(
                f"baseline and candidate case {case_id!r} differ on {field}"
            )


def _classify_change(
    expected: Disposition,
    baseline: Disposition,
    candidate: Disposition,
) -> str:
    if baseline == candidate:
        return "UNCHANGED"
    if candidate == expected:
        return "IMPROVED"
    if baseline == expected:
        return "REGRESSED"
    baseline_delta = DISPOSITION_ORDER[baseline] - DISPOSITION_ORDER[expected]
    candidate_delta = DISPOSITION_ORDER[candidate] - DISPOSITION_ORDER[expected]
    if baseline_delta * candidate_delta < 0:
        return "TRADEOFF"
    if abs(candidate_delta) < abs(baseline_delta):
        return "IMPROVED"
    return "REGRESSED"


def _change_signals(
    expected: Disposition,
    baseline: Disposition,
    candidate: Disposition,
) -> list[str]:
    baseline_under = DISPOSITION_ORDER[baseline] < DISPOSITION_ORDER[expected]
    candidate_under = DISPOSITION_ORDER[candidate] < DISPOSITION_ORDER[expected]
    baseline_harmful_allow = expected is Disposition.BLOCK and baseline is Disposition.ALLOW
    candidate_harmful_allow = expected is Disposition.BLOCK and candidate is Disposition.ALLOW
    baseline_false_block = expected is Disposition.ALLOW and baseline is Disposition.BLOCK
    candidate_false_block = expected is Disposition.ALLOW and candidate is Disposition.BLOCK
    signals: list[str] = []
    if candidate_under and not baseline_under:
        signals.append("NEW_UNDER_ENFORCEMENT")
    if baseline_under and not candidate_under:
        signals.append("RESOLVED_UNDER_ENFORCEMENT")
    if candidate_harmful_allow and not baseline_harmful_allow:
        signals.append("NEW_HARMFUL_ALLOW")
    if baseline_harmful_allow and not candidate_harmful_allow:
        signals.append("RESOLVED_HARMFUL_ALLOW")
    if candidate_false_block and not baseline_false_block:
        signals.append("NEW_FALSE_BLOCK")
    if baseline_false_block and not candidate_false_block:
        signals.append("RESOLVED_FALSE_BLOCK")
    return signals


def _report_reference(
    report: EvaluationReport, view: Mapping[str, Any]
) -> dict[str, Any]:
    return {
        "report_sha256": report.digest,
        "runtime": view["runtime"],
        "policy": view["policy"],
    }


def _validate_regression_body(body: Mapping[str, Any]) -> None:
    if body.get("schema_version") != REGRESSION_SCHEMA_VERSION:
        raise EvaluationError(
            f"unsupported regression schema_version {body.get('schema_version')!r}"
        )
    if body.get("status") != "SCAFFOLD":
        raise EvaluationError("regression report status must be SCAFFOLD")
    for label in ("baseline", "candidate"):
        reference = _require_mapping(body.get(label), f"regression {label}")
        _require_exact_fields(
            reference, {"report_sha256", "runtime", "policy"}, f"regression {label}"
        )
        _require_sha256(reference["report_sha256"], f"regression {label} report_sha256")
        runtime = _require_mapping(reference["runtime"], f"regression {label} runtime")
        _require_exact_fields(runtime, {"name", "version"}, f"regression {label} runtime")
        _require_non_empty_string(runtime["name"], f"regression {label} runtime name")
        _require_non_empty_string(runtime["version"], f"regression {label} runtime version")
        policy = _require_mapping(reference["policy"], f"regression {label} policy")
        _require_exact_fields(policy, {"id", "version", "sha256"}, f"regression {label} policy")
        _require_non_empty_string(policy["id"], f"regression {label} policy id")
        _require_non_empty_string(policy["version"], f"regression {label} policy version")
        _require_sha256(policy["sha256"], f"regression {label} policy sha256")

    corpus = _require_mapping(body.get("corpus"), "regression corpus")
    _require_exact_fields(
        corpus,
        {"source_name", "sha256", "case_count", "total_weight", "tags"},
        "regression corpus",
    )
    _require_non_empty_string(corpus["source_name"], "regression corpus source_name")
    _require_sha256(corpus["sha256"], "regression corpus sha256")
    case_count = _require_non_negative_int(corpus["case_count"], "regression case_count")
    if case_count == 0:
        raise EvaluationError("regression corpus case_count must be positive")
    _require_positive_number(corpus["total_weight"], "regression corpus total_weight")
    _require_string_list(corpus["tags"], "regression corpus tags", unique=True)

    summary = _require_mapping(body.get("summary"), "regression summary")
    _require_exact_fields(summary, _SUMMARY_FIELDS, "regression summary")
    for field in _SUMMARY_FIELDS - {"metric_deltas"} - {
        "unchanged_weight",
        "improved_weight",
        "regressed_weight",
        "tradeoff_weight",
    }:
        _require_non_negative_int(summary[field], f"regression summary {field}")
    for field in (
        "unchanged_weight",
        "improved_weight",
        "regressed_weight",
        "tradeoff_weight",
    ):
        _require_non_negative_number(summary[field], f"regression summary {field}")
    if summary["case_count"] != case_count:
        raise EvaluationError("regression summary and corpus case_count differ")
    if (
        summary["changed_case_count"] + summary["unchanged_case_count"]
        != case_count
    ):
        raise EvaluationError("regression changed and unchanged counts are inconsistent")
    if (
        summary["improved_case_count"]
        + summary["regressed_case_count"]
        + summary["tradeoff_case_count"]
        != summary["changed_case_count"]
    ):
        raise EvaluationError("regression classification counts are inconsistent")
    deltas = _require_mapping(summary["metric_deltas"], "regression metric_deltas")
    _require_exact_fields(deltas, _METRIC_DELTA_FIELDS, "regression metric_deltas")
    for field, value in deltas.items():
        _require_finite_number(value, f"regression metric delta {field}")

    cases = body.get("cases")
    if not isinstance(cases, list):
        raise EvaluationError("regression cases must be an array")
    if len(cases) != summary["changed_case_count"]:
        raise EvaluationError("regression cases length does not match changed_case_count")
    seen: set[str] = set()
    seen_ids: list[str] = []
    observed_counts = {
        "improved_case_count": 0,
        "regressed_case_count": 0,
        "tradeoff_case_count": 0,
    }
    observed_weights = {
        "improved_weight": 0.0,
        "regressed_weight": 0.0,
        "tradeoff_weight": 0.0,
    }
    observed_signals = {
        "new_under_enforcement_count": 0,
        "resolved_under_enforcement_count": 0,
        "new_harmful_allow_count": 0,
        "resolved_harmful_allow_count": 0,
        "new_false_block_count": 0,
        "resolved_false_block_count": 0,
    }
    for index, item in enumerate(cases):
        case = _require_mapping(item, f"regression case {index}")
        fields = {
            "id",
            "expected",
            "baseline_actual",
            "candidate_actual",
            "classification",
            "enforcement_change",
            "weight",
            "tags",
            "subject_sha256",
            "signals",
        }
        _require_exact_fields(case, fields, f"regression case {index}")
        case_id = _require_non_empty_string(case["id"], f"regression case {index} id")
        if case_id in seen:
            raise EvaluationError(f"regression contains duplicate case id {case_id!r}")
        seen.add(case_id)
        seen_ids.append(case_id)
        expected = _require_disposition(
            case["expected"], f"regression {case_id} expected"
        )
        baseline_actual = _require_disposition(
            case["baseline_actual"], f"regression {case_id} baseline_actual"
        )
        candidate_actual = _require_disposition(
            case["candidate_actual"], f"regression {case_id} candidate_actual"
        )
        if case["classification"] not in _CLASSIFICATIONS - {"UNCHANGED"}:
            raise EvaluationError(f"regression {case_id} classification is invalid")
        expected_classification = _classify_change(
            expected, baseline_actual, candidate_actual
        )
        if case["classification"] != expected_classification:
            raise EvaluationError(
                f"regression {case_id} classification is inconsistent"
            )
        if case["enforcement_change"] not in _ENFORCEMENT_CHANGES - {"UNCHANGED"}:
            raise EvaluationError(f"regression {case_id} enforcement_change is invalid")
        rank_delta = (
            DISPOSITION_ORDER[candidate_actual] - DISPOSITION_ORDER[baseline_actual]
        )
        expected_change = "INCREASED" if rank_delta > 0 else "DECREASED"
        if case["enforcement_change"] != expected_change:
            raise EvaluationError(
                f"regression {case_id} enforcement_change is inconsistent"
            )
        weight = _require_positive_number(
            case["weight"], f"regression {case_id} weight"
        )
        _require_string_list(case["tags"], f"regression {case_id} tags", unique=True)
        _require_sha256(case["subject_sha256"], f"regression {case_id} subject_sha256")
        signals = _require_string_list(
            case["signals"], f"regression {case_id} signals", unique=True
        )
        if any(signal not in _SIGNALS for signal in signals):
            raise EvaluationError(f"regression {case_id} contains an invalid signal")
        if signals != _change_signals(expected, baseline_actual, candidate_actual):
            raise EvaluationError(f"regression {case_id} signals are inconsistent")
        classification_key = case["classification"].lower()
        observed_counts[f"{classification_key}_case_count"] += 1
        observed_weights[f"{classification_key}_weight"] += weight
        for signal in signals:
            observed_signals[f"{signal.lower()}_count"] += 1

    if seen_ids != sorted(seen_ids):
        raise EvaluationError("regression cases must be sorted by id")
    for field, value in {**observed_counts, **observed_signals}.items():
        if summary[field] != value:
            raise EvaluationError(f"regression summary {field} is inconsistent")
    for field, value in observed_weights.items():
        if not math.isclose(summary[field], value, rel_tol=0.0, abs_tol=1e-12):
            raise EvaluationError(f"regression summary {field} is inconsistent")
    total_classified_weight = sum(
        summary[field]
        for field in (
            "unchanged_weight",
            "improved_weight",
            "regressed_weight",
            "tradeoff_weight",
        )
    )
    if not math.isclose(
        total_classified_weight,
        corpus["total_weight"],
        rel_tol=0.0,
        abs_tol=1e-12,
    ):
        raise EvaluationError("regression classification weights are inconsistent")

    gate = _require_mapping(body.get("gate"), "regression gate")
    _require_exact_fields(gate, {"configured", "passed", "thresholds", "failures"}, "regression gate")
    if type(gate["configured"]) is not bool or type(gate["passed"]) is not bool:
        raise EvaluationError("regression gate configured and passed must be booleans")
    thresholds = _require_mapping(gate["thresholds"], "regression thresholds")
    _require_exact_fields(thresholds, _THRESHOLD_FIELDS, "regression thresholds")
    for field in _THRESHOLD_FIELDS - {
        "max_exact_match_rate_drop",
        "max_macro_f1_drop",
    }:
        _require_non_negative_int(thresholds[field], f"regression threshold {field}")
    for field in ("max_exact_match_rate_drop", "max_macro_f1_drop"):
        _require_rate(thresholds[field], f"regression threshold {field}")
    _require_string_list(gate["failures"], "regression gate failures", unique=True)
    expected_gate = RegressionGate(**thresholds).assess(summary)
    if dict(gate) != expected_gate:
        raise EvaluationError("regression gate result is inconsistent with thresholds")
    limitations = _require_string_list(
        body.get("limitations"), "regression limitations", unique=True
    )
    if not limitations:
        raise EvaluationError("regression limitations must not be empty")


def _direction(expected: Disposition, actual: Disposition) -> str:
    delta = DISPOSITION_ORDER[actual] - DISPOSITION_ORDER[expected]
    return "EXACT" if delta == 0 else ("OVER" if delta > 0 else "UNDER")


def _require_mapping(value: Any, label: str) -> Mapping[str, Any]:
    if not isinstance(value, Mapping):
        raise EvaluationError(f"{label} must be an object")
    return value


def _require_exact_fields(
    value: Mapping[str, Any], fields: set[str], label: str
) -> None:
    missing = sorted(fields.difference(value))
    unknown = sorted(str(key) for key in value if key not in fields)
    if missing:
        raise EvaluationError(f"{label} missing required fields: {', '.join(missing)}")
    if unknown:
        raise EvaluationError(f"{label} contains unknown fields: {', '.join(unknown)}")


def _require_non_empty_string(value: Any, label: str) -> str:
    if not isinstance(value, str) or not value:
        raise EvaluationError(f"{label} must be a non-empty string")
    return value


def _require_sha256(value: Any, label: str) -> str:
    if not isinstance(value, str) or not _SHA256.fullmatch(value):
        raise EvaluationError(f"{label} must be 64 lowercase hexadecimal characters")
    return value


def _require_non_negative_int(value: Any, label: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        raise EvaluationError(f"{label} must be a non-negative integer")
    return value


def _require_finite_number(value: Any, label: str) -> float:
    if (
        isinstance(value, bool)
        or not isinstance(value, (int, float))
        or not math.isfinite(value)
    ):
        raise EvaluationError(f"{label} must be a finite number")
    return float(value)


def _require_non_negative_number(value: Any, label: str) -> float:
    number = _require_finite_number(value, label)
    if number < 0.0:
        raise EvaluationError(f"{label} must be non-negative")
    return number


def _require_positive_number(value: Any, label: str) -> float:
    number = _require_finite_number(value, label)
    if number <= 0.0:
        raise EvaluationError(f"{label} must be positive")
    return number


def _require_rate(value: Any, label: str) -> float:
    number = _require_finite_number(value, label)
    if not 0.0 <= number <= 1.0:
        raise EvaluationError(f"{label} must be in [0, 1]")
    return number


def _require_disposition(value: Any, label: str) -> Disposition:
    if not isinstance(value, str):
        raise EvaluationError(f"{label} must be a disposition string")
    try:
        return Disposition(value)
    except ValueError as exc:
        raise EvaluationError(f"{label} must be ALLOW, REVIEW, or BLOCK") from exc


def _require_string_list(value: Any, label: str, *, unique: bool) -> list[str]:
    if not isinstance(value, list) or any(
        not isinstance(item, str) or not item for item in value
    ):
        raise EvaluationError(f"{label} must be an array of non-empty strings")
    if unique and len(value) != len(set(value)):
        raise EvaluationError(f"{label} must not contain duplicates")
    return list(value)


def _unique_object(pairs: Sequence[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise EvaluationError(f"duplicate JSON object key {key!r}")
        result[key] = value
    return result
