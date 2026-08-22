"""Strict, provider-neutral regression evaluation for assurance policies.

Status: [SCAFFOLD]. The harness measures decisions on caller-labelled cases. It
does not establish that the labels are correct or that results generalise beyond
the supplied corpus.
"""

from __future__ import annotations

import json
import math
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping, Optional, Sequence

from .jsonutil import jsonable, sha256_json
from .models import AssuranceEvent, DISPOSITION_ORDER, Disposition
from .runtime import ASSURANCE_VERSION, AssuranceRuntime


EVALUATION_SCHEMA_VERSION = "0.1"
MAX_CASES = 100_000
MAX_LINE_CHARACTERS = 2_000_000
MAX_REPORT_CHARACTERS = 50_000_000
MAX_TAGS_PER_CASE = 64
MAX_RATIONALE_CHARACTERS = 4_000
_CASE_ID = re.compile(r"[A-Za-z0-9][A-Za-z0-9._:-]{2,127}")
_LABELS = tuple(Disposition)


class EvaluationError(ValueError):
    """Raised when an evaluation corpus or gate cannot be accepted safely."""


@dataclass(frozen=True)
class EvaluationCase:
    """One labelled event in a regression corpus."""

    case_id: str
    expected: Disposition
    event: AssuranceEvent
    weight: float = 1.0
    tags: tuple[str, ...] = ()
    rationale: str = ""

    def __post_init__(self) -> None:
        if not isinstance(self.case_id, str) or not _CASE_ID.fullmatch(self.case_id):
            raise EvaluationError(f"invalid evaluation case id: {self.case_id!r}")
        object.__setattr__(self, "expected", Disposition(self.expected))
        if not isinstance(self.event, AssuranceEvent):
            raise EvaluationError("evaluation case event must be an AssuranceEvent")
        if (
            isinstance(self.weight, bool)
            or not isinstance(self.weight, (int, float))
            or not math.isfinite(self.weight)
            or not 0.0 < self.weight <= 1_000_000.0
        ):
            raise EvaluationError("evaluation case weight must be in (0, 1000000]")
        object.__setattr__(self, "weight", float(self.weight))
        if not isinstance(self.tags, tuple):
            raise EvaluationError("evaluation case tags must be an array")
        if len(self.tags) > MAX_TAGS_PER_CASE:
            raise EvaluationError(
                f"evaluation case tags exceed {MAX_TAGS_PER_CASE} entries"
            )
        if any(
            not isinstance(tag, str) or not tag or len(tag) > 128
            for tag in self.tags
        ):
            raise EvaluationError("evaluation case tags must be non-empty strings <=128 characters")
        if len(self.tags) != len(set(self.tags)):
            raise EvaluationError("evaluation case tags must not contain duplicates")
        if not isinstance(self.rationale, str):
            raise EvaluationError("evaluation case rationale must be a string")
        if len(self.rationale) > MAX_RATIONALE_CHARACTERS:
            raise EvaluationError(
                f"evaluation case rationale exceeds {MAX_RATIONALE_CHARACTERS} characters"
            )

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> "EvaluationCase":
        if not isinstance(data, Mapping):
            raise EvaluationError("evaluation case must be a JSON object")
        allowed = {"id", "expected", "event", "weight", "tags", "rationale"}
        unknown = sorted(str(key) for key in data if key not in allowed)
        missing = sorted({"id", "expected", "event"}.difference(data))
        if missing:
            raise EvaluationError(
                "evaluation case missing required fields: " + ", ".join(missing)
            )
        if unknown:
            raise EvaluationError(
                "evaluation case contains unknown fields: " + ", ".join(unknown)
            )
        if not isinstance(data["id"], str) or not isinstance(data["expected"], str):
            raise EvaluationError("evaluation case id and expected must be strings")
        event = data["event"]
        if not isinstance(event, Mapping):
            raise EvaluationError("evaluation case event must be a JSON object")
        phase = event.get("phase")
        if phase == "tool" and "tool_name" not in event:
            raise EvaluationError("tool evaluation event requires tool_name")
        if phase in ("input", "output") and "content" not in event:
            raise EvaluationError("text evaluation event requires content")
        tags = data.get("tags", [])
        if not isinstance(tags, list):
            raise EvaluationError("evaluation case tags must be an array")
        return cls(
            case_id=data["id"],
            expected=Disposition(data["expected"]),
            event=AssuranceEvent.from_dict(event),
            weight=data.get("weight", 1.0),
            tags=tuple(tags),
            rationale=data.get("rationale", ""),
        )

    def canonical_dict(self) -> dict[str, Any]:
        """Decision-relevant normalized representation used for corpus hashing."""

        event: dict[str, Any] = {
            "phase": self.event.phase.value,
            "context": jsonable(self.event.context),
            "metadata": jsonable(self.event.metadata),
        }
        if self.event.phase.value in ("input", "output"):
            event["content"] = self.event.content
        else:
            event.update(
                {
                    "tool_name": self.event.tool_name,
                    "tool_arguments": jsonable(self.event.tool_arguments),
                    "scopes": list(self.event.scopes),
                    "side_effect": self.event.side_effect,
                    "human_approved": self.event.human_approved,
                }
            )
        return {
            "id": self.case_id,
            "expected": self.expected.value,
            "event": event,
            "weight": self.weight,
            "tags": list(self.tags),
        }


@dataclass(frozen=True)
class EvaluationCorpus:
    """A validated set of uniquely identified evaluation cases."""

    cases: tuple[EvaluationCase, ...]
    digest: str
    source_name: str

    @classmethod
    def from_jsonl(cls, path: str | Path) -> "EvaluationCorpus":
        source = Path(path)
        cases: list[EvaluationCase] = []
        seen: set[str] = set()
        try:
            handle = source.open("r", encoding="utf-8")
        except OSError as exc:
            raise EvaluationError(f"cannot read evaluation corpus {source}: {exc}") from exc
        with handle:
            for line_number, line in enumerate(handle, start=1):
                if len(line) > MAX_LINE_CHARACTERS:
                    raise EvaluationError(
                        f"evaluation corpus line {line_number} exceeds "
                        f"{MAX_LINE_CHARACTERS} characters"
                    )
                if not line.strip():
                    continue
                if len(cases) >= MAX_CASES:
                    raise EvaluationError(
                        f"evaluation corpus exceeds {MAX_CASES} cases"
                    )
                try:
                    data = json.loads(line, object_pairs_hook=_unique_object)
                except (json.JSONDecodeError, EvaluationError) as exc:
                    raise EvaluationError(
                        f"invalid evaluation corpus line {line_number}: {exc}"
                    ) from exc
                try:
                    case = EvaluationCase.from_dict(data)
                except (EvaluationError, TypeError, ValueError) as exc:
                    raise EvaluationError(
                        f"invalid evaluation corpus line {line_number}: {exc}"
                    ) from exc
                if case.case_id in seen:
                    raise EvaluationError(
                        f"duplicate evaluation case id {case.case_id!r} "
                        f"at line {line_number}"
                    )
                seen.add(case.case_id)
                cases.append(case)
        if not cases:
            raise EvaluationError("evaluation corpus contains no cases")
        normalized = [case.canonical_dict() for case in cases]
        return cls(
            cases=tuple(cases),
            digest=sha256_json(normalized),
            source_name=source.name,
        )


@dataclass(frozen=True)
class EvaluationGate:
    """Optional CI thresholds. Unconfigured fields do not affect the result."""

    require_exact_match: bool = False
    max_under_enforcement_rate: Optional[float] = None
    max_harmful_allows: Optional[int] = None
    max_false_blocks: Optional[int] = None
    min_macro_f1: Optional[float] = None

    def __post_init__(self) -> None:
        if type(self.require_exact_match) is not bool:
            raise EvaluationError("require_exact_match must be a boolean")
        for name in ("max_under_enforcement_rate", "min_macro_f1"):
            value = getattr(self, name)
            if value is not None and (
                isinstance(value, bool)
                or not isinstance(value, (int, float))
                or not math.isfinite(value)
                or not 0.0 <= value <= 1.0
            ):
                raise EvaluationError(f"{name} must be in [0, 1]")
        for name in ("max_harmful_allows", "max_false_blocks"):
            value = getattr(self, name)
            if value is not None and (
                isinstance(value, bool) or not isinstance(value, int) or value < 0
            ):
                raise EvaluationError(f"{name} must be a non-negative integer")

    @property
    def configured(self) -> bool:
        return self.require_exact_match or any(
            value is not None
            for value in (
                self.max_under_enforcement_rate,
                self.max_harmful_allows,
                self.max_false_blocks,
                self.min_macro_f1,
            )
        )

    def assess(self, summary: Mapping[str, Any]) -> dict[str, Any]:
        failures: list[str] = []
        if self.require_exact_match and summary["exact_match_rate"] < 1.0:
            failures.append("exact_match_rate is below 1.0")
        if (
            self.max_under_enforcement_rate is not None
            and summary["under_enforcement_rate"]
            > self.max_under_enforcement_rate
        ):
            failures.append(
                "under_enforcement_rate exceeds "
                f"{self.max_under_enforcement_rate}"
            )
        if (
            self.max_harmful_allows is not None
            and summary["harmful_allow_count"] > self.max_harmful_allows
        ):
            failures.append(
                f"harmful_allow_count exceeds {self.max_harmful_allows}"
            )
        if (
            self.max_false_blocks is not None
            and summary["false_block_count"] > self.max_false_blocks
        ):
            failures.append(f"false_block_count exceeds {self.max_false_blocks}")
        if (
            self.min_macro_f1 is not None
            and summary["macro_f1"] < self.min_macro_f1
        ):
            failures.append(f"macro_f1 is below {self.min_macro_f1}")
        return {
            "configured": self.configured,
            "passed": not failures,
            "thresholds": {
                "require_exact_match": self.require_exact_match,
                "max_under_enforcement_rate": self.max_under_enforcement_rate,
                "max_harmful_allows": self.max_harmful_allows,
                "max_false_blocks": self.max_false_blocks,
                "min_macro_f1": self.min_macro_f1,
            },
            "failures": failures,
        }


@dataclass(frozen=True)
class EvaluationReport:
    """Deterministic, privacy-minimised report for one policy/corpus pair."""

    body: Mapping[str, Any]
    digest: str

    @classmethod
    def issue(cls, body: Mapping[str, Any]) -> "EvaluationReport":
        normalized = jsonable(body)
        return cls(body=normalized, digest=sha256_json(normalized))

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> "EvaluationReport":
        if not isinstance(data, Mapping):
            raise EvaluationError("evaluation report must be a JSON object")
        body_fields = {
            "schema_version",
            "status",
            "runtime",
            "policy",
            "corpus",
            "summary",
            "confusion_matrix",
            "per_class",
            "cases",
            "gate",
            "limitations",
        }
        allowed = body_fields | {"integrity"}
        missing = sorted(allowed.difference(data))
        unknown = sorted(str(key) for key in data if key not in allowed)
        if missing:
            raise EvaluationError(
                "evaluation report missing required fields: " + ", ".join(missing)
            )
        if unknown:
            raise EvaluationError(
                "evaluation report contains unknown fields: " + ", ".join(unknown)
            )
        integrity = data["integrity"]
        if not isinstance(integrity, Mapping):
            raise EvaluationError("evaluation report integrity must be an object")
        if set(integrity) != {"algorithm", "canonicalization", "digest"}:
            raise EvaluationError("evaluation report integrity fields are invalid")
        if integrity["algorithm"] != "sha256":
            raise EvaluationError("evaluation report integrity algorithm must be sha256")
        if integrity["canonicalization"] != "lycheetah-json-v1":
            raise EvaluationError(
                "evaluation report canonicalization must be lycheetah-json-v1"
            )
        digest = integrity["digest"]
        if not isinstance(digest, str) or not re.fullmatch(r"[0-9a-f]{64}", digest):
            raise EvaluationError(
                "evaluation report digest must be 64 lowercase hexadecimal characters"
            )
        body = {key: data[key] for key in body_fields}
        if body["schema_version"] != EVALUATION_SCHEMA_VERSION:
            raise EvaluationError(
                f"unsupported evaluation schema_version {body['schema_version']!r}"
            )
        if body["status"] != "SCAFFOLD":
            raise EvaluationError("evaluation report status must be SCAFFOLD")
        return cls(body=jsonable(body), digest=digest)

    @classmethod
    def from_json(cls, path: str | Path) -> "EvaluationReport":
        source = Path(path)
        try:
            text = source.read_text(encoding="utf-8")
        except OSError as exc:
            raise EvaluationError(f"cannot read evaluation report {source}: {exc}") from exc
        if len(text) > MAX_REPORT_CHARACTERS:
            raise EvaluationError(
                f"evaluation report exceeds {MAX_REPORT_CHARACTERS} characters"
            )
        try:
            data = json.loads(text, object_pairs_hook=_unique_object)
        except (json.JSONDecodeError, EvaluationError) as exc:
            raise EvaluationError(f"invalid evaluation report JSON: {exc}") from exc
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


def evaluate_corpus(
    runtime: AssuranceRuntime,
    corpus: EvaluationCorpus,
    *,
    gate: Optional[EvaluationGate] = None,
) -> EvaluationReport:
    """Evaluate every case and return a deterministic aggregate report."""

    if not isinstance(runtime, AssuranceRuntime):
        raise EvaluationError("runtime must be an AssuranceRuntime")
    if not isinstance(corpus, EvaluationCorpus):
        raise EvaluationError("corpus must be an EvaluationCorpus")
    active_gate = gate or EvaluationGate()
    confusion_counts = _empty_matrix(0)
    confusion_weights = _empty_matrix(0.0)
    outcomes: list[dict[str, Any]] = []

    for case in corpus.cases:
        receipt = runtime.evaluate(case.event)
        actual = receipt.decision
        confusion_counts[case.expected.value][actual.value] += 1
        confusion_weights[case.expected.value][actual.value] += case.weight
        order_delta = DISPOSITION_ORDER[actual] - DISPOSITION_ORDER[case.expected]
        outcomes.append(
            {
                "id": case.case_id,
                "expected": case.expected.value,
                "actual": actual.value,
                "exact_match": actual == case.expected,
                "direction": "EXACT" if order_delta == 0 else (
                    "OVER" if order_delta > 0 else "UNDER"
                ),
                "weight": case.weight,
                "tags": list(case.tags),
                "subject_sha256": receipt.event["subject"]["sha256"],
                "findings": [
                    {
                        "id": finding.finding_id,
                        "effective_disposition": finding.effective_disposition.value,
                        "claim_status": finding.claim_status.value,
                        "deterministic": finding.deterministic,
                    }
                    for finding in receipt.findings
                ],
            }
        )

    summary, per_class = _metrics(confusion_counts, confusion_weights)
    gate_result = active_gate.assess(summary)
    body = {
        "schema_version": EVALUATION_SCHEMA_VERSION,
        "status": "SCAFFOLD",
        "runtime": {
            "name": "lycheetah-assurance",
            "version": ASSURANCE_VERSION,
        },
        "policy": {
            "id": runtime.policy.policy_id,
            "version": runtime.policy.version,
            "sha256": runtime.policy.digest,
        },
        "corpus": {
            "source_name": corpus.source_name,
            "sha256": corpus.digest,
            "case_count": len(corpus.cases),
            "total_weight": sum(case.weight for case in corpus.cases),
            "tags": sorted({tag for case in corpus.cases for tag in case.tags}),
        },
        "summary": summary,
        "confusion_matrix": {
            "orientation": "expected_rows_actual_columns",
            "counts": confusion_counts,
            "weighted": confusion_weights,
        },
        "per_class": per_class,
        "cases": outcomes,
        "gate": gate_result,
        "limitations": [
            "Expected dispositions are caller-supplied labels, not independently established ground truth.",
            "Results describe this exact corpus, policy, and runtime version and do not establish out-of-sample safety or calibration.",
            "A decision match does not prove that the underlying event is harmless, harmful, lawful, or correctly labelled.",
            "The report excludes raw event content and tool arguments; subject hashes support joining to separately governed evidence.",
        ],
    }
    return EvaluationReport.issue(body)


def _metrics(
    counts: Mapping[str, Mapping[str, int]],
    weights: Mapping[str, Mapping[str, float]],
) -> tuple[dict[str, Any], dict[str, Any]]:
    total_count = sum(sum(row.values()) for row in counts.values())
    total_weight = sum(sum(row.values()) for row in weights.values())
    exact_count = sum(counts[label.value][label.value] for label in _LABELS)
    exact_weight = sum(weights[label.value][label.value] for label in _LABELS)
    under_count = 0
    under_weight = 0.0
    over_count = 0
    over_weight = 0.0
    for expected in _LABELS:
        for actual in _LABELS:
            if DISPOSITION_ORDER[actual] < DISPOSITION_ORDER[expected]:
                under_count += counts[expected.value][actual.value]
                under_weight += weights[expected.value][actual.value]
            elif DISPOSITION_ORDER[actual] > DISPOSITION_ORDER[expected]:
                over_count += counts[expected.value][actual.value]
                over_weight += weights[expected.value][actual.value]

    per_class: dict[str, Any] = {}
    f1_values: list[float] = []
    for label in _LABELS:
        value = label.value
        true_positive = weights[value][value]
        support = sum(weights[value].values())
        predicted = sum(weights[expected.value][value] for expected in _LABELS)
        precision = true_positive / predicted if predicted else 0.0
        recall = true_positive / support if support else None
        f1 = (
            2.0 * precision * recall / (precision + recall)
            if recall is not None and precision + recall > 0.0
            else 0.0
        )
        if support:
            f1_values.append(f1)
        per_class[value] = {
            "support_count": sum(counts[value].values()),
            "support_weight": support,
            "predicted_weight": predicted,
            "precision": precision,
            "recall": recall,
            "f1": f1,
        }

    review_count = sum(counts[expected.value]["REVIEW"] for expected in _LABELS)
    review_weight = sum(weights[expected.value]["REVIEW"] for expected in _LABELS)
    summary = {
        "case_count": total_count,
        "total_weight": total_weight,
        "exact_match_count": exact_count,
        "exact_match_rate": exact_weight / total_weight,
        "under_enforcement_count": under_count,
        "under_enforcement_rate": under_weight / total_weight,
        "over_enforcement_count": over_count,
        "over_enforcement_rate": over_weight / total_weight,
        "harmful_allow_count": counts["BLOCK"]["ALLOW"],
        "harmful_allow_weight": weights["BLOCK"]["ALLOW"],
        "false_block_count": counts["ALLOW"]["BLOCK"],
        "false_block_weight": weights["ALLOW"]["BLOCK"],
        "review_count": review_count,
        "review_rate": review_weight / total_weight,
        "macro_f1": sum(f1_values) / len(f1_values),
    }
    return summary, per_class


def _empty_matrix(zero: int | float) -> dict[str, dict[str, Any]]:
    return {
        expected.value: {actual.value: zero for actual in _LABELS}
        for expected in _LABELS
    }


def _unique_object(pairs: Sequence[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise EvaluationError(f"duplicate JSON object key {key!r}")
        result[key] = value
    return result
