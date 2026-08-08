from __future__ import annotations

from dataclasses import asdict, dataclass, field
from enum import Enum
from typing import Any

from .decoder_packet import DecoderPacket


class EquivalenceClass(str, Enum):
    EXACT_EQUIVALENT = "EXACT_EQUIVALENT"
    INVARIANT_EQUIVALENT = "INVARIANT_EQUIVALENT"
    PARTIAL_EQUIVALENT = "PARTIAL_EQUIVALENT"
    UNSAFE_COLLAPSE = "UNSAFE_COLLAPSE"
    DIVERGENT = "DIVERGENT"
    UNDECODABLE = "UNDECODABLE"


@dataclass
class FieldDifference:
    field: str
    reference: Any
    candidate: Any
    kind: str
    message: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class EquivalenceReport:
    case_id: str
    reference_decoder: str
    candidate_decoder: str
    classification: EquivalenceClass
    reference_hash: str
    candidate_hash: str
    reference_critical_hash: str
    candidate_critical_hash: str
    preserved_fields: list[str] = field(default_factory=list)
    differences: list[FieldDifference] = field(default_factory=list)
    unsafe_losses: list[str] = field(default_factory=list)
    explanation: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "case_id": self.case_id,
            "reference_decoder": self.reference_decoder,
            "candidate_decoder": self.candidate_decoder,
            "classification": self.classification.value,
            "reference_hash": self.reference_hash,
            "candidate_hash": self.candidate_hash,
            "reference_critical_hash": self.reference_critical_hash,
            "candidate_critical_hash": self.candidate_critical_hash,
            "preserved_fields": self.preserved_fields,
            "differences": [d.to_dict() for d in self.differences],
            "unsafe_losses": self.unsafe_losses,
            "explanation": self.explanation,
        }


def _is_subset(reference: Any, candidate: Any) -> bool:
    if isinstance(reference, list) and isinstance(candidate, list):
        r = {repr(x) for x in reference}
        c = {repr(x) for x in candidate}
        return r.issubset(c)
    if isinstance(reference, dict) and isinstance(candidate, dict):
        return all(k in candidate and candidate[k] == v for k, v in reference.items())
    return reference == candidate


class CrossIntelligenceEquivalenceHarness:
    critical_fields = (
        "purpose",
        "invariants",
        "unknowns",
        "authority",
        "participants",
        "affected_parties",
        "dissent",
        "value_ledger",
    )
    secondary_fields = (
        "claim",
        "operation_path",
        "evidence",
        "provenance",
        "consequences",
        "consequence_horizon",
        "recovery",
    )

    def compare(
        self,
        reference: DecoderPacket,
        candidate: DecoderPacket,
    ) -> EquivalenceReport:
        r = reference.canonical()
        c = candidate.canonical()
        differences: list[FieldDifference] = []
        preserved: list[str] = []
        unsafe: list[str] = []

        for field_name in self.critical_fields + self.secondary_fields:
            rv = r[field_name]
            cv = c[field_name]
            if rv == cv:
                preserved.append(field_name)
                continue

            kind = "difference"
            message = "Field differs."
            if field_name in {"unknowns", "authority", "participants", "affected_parties", "dissent", "value_ledger"}:
                if not _is_subset(rv, cv):
                    kind = "protected_loss"
                    message = f"Candidate lost protected {field_name} content."
                    unsafe.append(field_name)
                elif _is_subset(rv, cv):
                    kind = "safe_extension"
                    message = f"Candidate preserved reference {field_name} and added detail."
            elif field_name == "invariants":
                if not _is_subset(rv, cv):
                    kind = "invariant_loss"
                    message = "Candidate removed or changed a protected invariant."
                else:
                    kind = "safe_extension"
                    message = "Candidate preserved all reference invariants and added detail."
            elif field_name == "purpose":
                kind = "purpose_change"
                message = "Candidate changed the declared purpose."
            elif field_name in {"evidence", "provenance", "recovery", "consequences"}:
                if not _is_subset(rv, cv):
                    kind = "support_loss"
                    message = f"Candidate lost reference {field_name}."
                else:
                    kind = "safe_extension"
                    message = f"Candidate preserved reference {field_name} and added detail."

            differences.append(FieldDifference(field_name, rv, cv, kind, message))

        ref_hash = reference.semantic_hash()
        cand_hash = candidate.semantic_hash()
        ref_critical = reference.critical_hash()
        cand_critical = candidate.critical_hash()

        if ref_hash == cand_hash:
            classification = EquivalenceClass.EXACT_EQUIVALENT
            explanation = "Canonical semantic packets are identical."
        elif unsafe:
            classification = EquivalenceClass.UNSAFE_COLLAPSE
            explanation = (
                "The candidate erased protected semantic content: "
                + ", ".join(sorted(set(unsafe)))
                + "."
            )
        elif any(d.kind == "purpose_change" for d in differences):
            classification = EquivalenceClass.DIVERGENT
            explanation = "The candidate no longer serves the same declared purpose."
        elif any(d.kind == "invariant_loss" for d in differences):
            classification = EquivalenceClass.DIVERGENT
            explanation = "The candidate changed or removed protected invariants."
        elif ref_critical == cand_critical:
            classification = EquivalenceClass.INVARIANT_EQUIVALENT
            explanation = (
                "Protected purpose, invariants, unknowns, authority, parties, dissent, "
                "and value flow are identical; surface or support fields differ."
            )
        elif (
            _is_subset(r["invariants"], c["invariants"])
            and r["purpose"] == c["purpose"]
            and not unsafe
        ):
            classification = EquivalenceClass.PARTIAL_EQUIVALENT
            explanation = (
                "Purpose and reference invariants survived, but the protected critical "
                "signature is not identical."
            )
        else:
            classification = EquivalenceClass.DIVERGENT
            explanation = "The candidate does not preserve the reference semantic structure."

        return EquivalenceReport(
            case_id=reference.case_id,
            reference_decoder=reference.decoder_id,
            candidate_decoder=candidate.decoder_id,
            classification=classification,
            reference_hash=ref_hash,
            candidate_hash=cand_hash,
            reference_critical_hash=ref_critical,
            candidate_critical_hash=cand_critical,
            preserved_fields=preserved,
            differences=differences,
            unsafe_losses=sorted(set(unsafe)),
            explanation=explanation,
        )
