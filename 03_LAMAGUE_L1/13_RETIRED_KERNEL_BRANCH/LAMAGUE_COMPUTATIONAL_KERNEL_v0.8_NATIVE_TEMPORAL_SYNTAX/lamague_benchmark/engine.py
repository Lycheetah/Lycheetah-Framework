from __future__ import annotations

from dataclasses import dataclass, asdict
from enum import Enum
from typing import Any
import json


class EquivalenceClass(str, Enum):
    EXACT_EQUIVALENT = "EXACT_EQUIVALENT"
    INVARIANT_EQUIVALENT = "INVARIANT_EQUIVALENT"
    PARTIAL_EQUIVALENT = "PARTIAL_EQUIVALENT"
    UNSAFE_COLLAPSE = "UNSAFE_COLLAPSE"
    DIVERGENT = "DIVERGENT"
    UNDECODABLE = "UNDECODABLE"


CRITICAL_FIELDS = (
    "unknowns",
    "invariants",
    "authority",
    "affected_parties",
    "dissent",
    "value_flows",
    "recoveries",
)
SECONDARY_FIELDS = ("evidence", "boundaries", "participants", "provenance")


def _normalise_item(item: Any) -> str:
    if isinstance(item, dict):
        return json.dumps(item, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return str(item).strip()


def _field_set(packet: dict[str, Any], field: str) -> set[str]:
    value = packet.get(field, [])
    if value is None:
        return set()
    if not isinstance(value, list):
        raise TypeError(f"Field {field} must be a list")
    return {_normalise_item(x) for x in value}


def canonical_packet(packet: dict[str, Any]) -> str:
    return json.dumps(packet, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


@dataclass(frozen=True)
class FieldComparison:
    field: str
    reference_count: int
    candidate_count: int
    preserved: tuple[str, ...]
    lost: tuple[str, ...]
    added: tuple[str, ...]
    recall: float
    precision: float

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class ComparisonResult:
    case_id: str
    candidate_id: str
    classification: EquivalenceClass
    critical_recall: float
    secondary_recall: float
    lost_critical: tuple[str, ...]
    added_critical: tuple[str, ...]
    field_results: tuple[FieldComparison, ...]
    explanation: str

    def to_dict(self) -> dict[str, Any]:
        d = asdict(self)
        d["classification"] = self.classification.value
        return d


def _compare_field(reference: dict[str, Any], candidate: dict[str, Any], field: str) -> FieldComparison:
    r = _field_set(reference, field)
    c = _field_set(candidate, field)
    preserved = tuple(sorted(r & c))
    lost = tuple(sorted(r - c))
    added = tuple(sorted(c - r))
    recall = 1.0 if not r else len(preserved) / len(r)
    precision = 1.0 if not c else len(preserved) / len(c)
    return FieldComparison(field, len(r), len(c), preserved, lost, added, recall, precision)


def compare(reference: dict[str, Any], candidate: dict[str, Any]) -> ComparisonResult:
    case_id = str(reference.get("case_id", ""))
    candidate_id = str(candidate.get("candidate_id", ""))
    required = {"case_id", "claim", *CRITICAL_FIELDS, *SECONDARY_FIELDS}
    if not isinstance(candidate, dict) or any(k not in candidate for k in required):
        return ComparisonResult(
            case_id, candidate_id, EquivalenceClass.UNDECODABLE,
            0.0, 0.0, tuple(CRITICAL_FIELDS), (), (),
            "Candidate packet is missing required structure."
        )
    try:
        fields = tuple(_compare_field(reference, candidate, f) for f in CRITICAL_FIELDS + SECONDARY_FIELDS)
    except (TypeError, ValueError):
        return ComparisonResult(
            case_id, candidate_id, EquivalenceClass.UNDECODABLE,
            0.0, 0.0, tuple(CRITICAL_FIELDS), (), (),
            "Candidate packet contains an invalid field type."
        )

    critical = fields[:len(CRITICAL_FIELDS)]
    secondary = fields[len(CRITICAL_FIELDS):]
    critical_recall = sum(x.recall for x in critical) / len(critical)
    secondary_recall = sum(x.recall for x in secondary) / len(secondary)
    lost_critical = tuple(f"{x.field}:{v}" for x in critical for v in x.lost)
    added_critical = tuple(f"{x.field}:{v}" for x in critical for v in x.added)

    ref_invariants = _field_set(reference, "invariants")
    cand_invariants = _field_set(candidate, "invariants")
    purpose_changed = reference.get("purpose") != candidate.get("purpose")
    invariant_changed = bool(ref_invariants - cand_invariants) and bool(cand_invariants - ref_invariants)
    identity_mismatch = reference.get("semantic_identity") != candidate.get("semantic_identity")

    if invariant_changed or (identity_mismatch and purpose_changed):
        cls = EquivalenceClass.DIVERGENT
        explanation = "Protected purpose or invariant structure changed."
    elif lost_critical:
        cls = EquivalenceClass.UNSAFE_COLLAPSE
        explanation = "Candidate silently lost one or more protected semantic fields."
    elif canonical_packet({k:v for k,v in candidate.items() if k not in {"candidate_id", "expected_class"}}) == canonical_packet(reference):
        cls = EquivalenceClass.EXACT_EQUIVALENT
        explanation = "Candidate is canonically identical to the reference packet."
    elif critical_recall == 1.0 and not added_critical:
        if secondary_recall == 1.0:
            cls = EquivalenceClass.INVARIANT_EQUIVALENT
            explanation = "Protected meaning is preserved despite noncritical wording or ordering differences."
        else:
            cls = EquivalenceClass.PARTIAL_EQUIVALENT
            explanation = "Protected meaning survives, but secondary context is incomplete."
    else:
        cls = EquivalenceClass.PARTIAL_EQUIVALENT
        explanation = "Candidate preserves only part of the reference structure."

    return ComparisonResult(
        case_id, candidate_id, cls, critical_recall, secondary_recall,
        lost_critical, added_critical, fields, explanation
    )
