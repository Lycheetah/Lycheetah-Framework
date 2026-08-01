from __future__ import annotations

from dataclasses import asdict, dataclass, field
import hashlib
import json
from typing import Any

from .model import ProgramAST
from .value_ledger import normalize_value_entries
from .dissent import normalize_dissent


def _clean_text(value: str) -> str:
    return " ".join(str(value or "").strip().lower().split())


def _sorted_unique(values: list[str]) -> list[str]:
    return sorted({_clean_text(v) for v in values if _clean_text(v)})


def _canonical_dissent(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    result: list[dict[str, Any]] = []
    for item in normalize_dissent(records):
        result.append({
            "parties": sorted(_clean_text(x) for x in item["parties"]),
            "positions": {
                _clean_text(k): _clean_text(v)
                for k, v in sorted(item["positions"].items())
            },
            "unknown_type": _clean_text(item["unknown_type"]),
            "protected_boundaries": _sorted_unique(item["protected_boundaries"]),
            "status": _clean_text(item["status"]).upper(),
        })
    return sorted(result, key=lambda x: json.dumps(x, sort_keys=True))


def _canonical_value(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    result: list[dict[str, Any]] = []
    for item in normalize_value_entries(records):
        result.append({
            "source": _clean_text(item["source"]),
            "recipient": _clean_text(item["recipient"]),
            "kind": _clean_text(item["kind"]),
            "amount": round(float(item["amount"]), 8),
            "unit": _clean_text(item["unit"]),
            "declared": bool(item["declared"]),
            "consent": _clean_text(item["consent"]),
            "affected_parties": _sorted_unique(item["affected_parties"]),
            "reversible": bool(item["reversible"]),
        })
    return sorted(result, key=lambda x: json.dumps(x, sort_keys=True))


@dataclass
class DecoderPacket:
    case_id: str
    decoder_id: str
    purpose: str
    claim: str
    operation_path: list[str]
    invariants: list[str] = field(default_factory=list)
    unknowns: list[str] = field(default_factory=list)
    authority: list[str] = field(default_factory=list)
    participants: list[str] = field(default_factory=list)
    affected_parties: list[str] = field(default_factory=list)
    evidence: list[str] = field(default_factory=list)
    provenance: list[str] = field(default_factory=list)
    dissent: list[dict[str, Any]] = field(default_factory=list)
    value_ledger: list[dict[str, Any]] = field(default_factory=list)
    consequences: list[str] = field(default_factory=list)
    consequence_horizon: str = ""
    recovery: list[str] = field(default_factory=list)
    confidence: str = "unspecified"
    notes: str = ""
    schema_version: str = "0.3"

    def canonical(self) -> dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "case_id": _clean_text(self.case_id),
            "purpose": _clean_text(self.purpose),
            "claim": _clean_text(self.claim),
            "operation_path": [str(x).upper().strip() for x in self.operation_path],
            "invariants": _sorted_unique(self.invariants),
            "unknowns": _sorted_unique(self.unknowns),
            "authority": _sorted_unique(self.authority),
            "participants": _sorted_unique(self.participants),
            "affected_parties": _sorted_unique(self.affected_parties),
            "evidence": _sorted_unique(self.evidence),
            "provenance": _sorted_unique(self.provenance),
            "dissent": _canonical_dissent(self.dissent),
            "value_ledger": _canonical_value(self.value_ledger),
            "consequences": _sorted_unique(self.consequences),
            "consequence_horizon": _clean_text(self.consequence_horizon),
            "recovery": _sorted_unique(self.recovery),
        }

    def semantic_hash(self) -> str:
        payload = json.dumps(
            self.canonical(),
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
        ).encode("utf-8")
        return "lamague-packet:" + hashlib.sha256(payload).hexdigest()

    def critical_signature(self) -> dict[str, Any]:
        c = self.canonical()
        return {
            "purpose": c["purpose"],
            "invariants": c["invariants"],
            "unknowns": c["unknowns"],
            "authority": c["authority"],
            "participants": c["participants"],
            "affected_parties": c["affected_parties"],
            "dissent": c["dissent"],
            "value_ledger": c["value_ledger"],
        }

    def critical_hash(self) -> str:
        payload = json.dumps(
            self.critical_signature(),
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
        ).encode("utf-8")
        return "lamague-critical:" + hashlib.sha256(payload).hexdigest()

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "DecoderPacket":
        required = {"case_id", "decoder_id", "purpose", "claim", "operation_path"}
        missing = sorted(required - set(data))
        if missing:
            raise ValueError(f"Decoder packet missing required fields: {missing}")
        return cls(**data)

    @classmethod
    def from_ast(
        cls,
        case_id: str,
        decoder_id: str,
        ast: ProgramAST,
        confidence: str = "reference",
        notes: str = "",
    ) -> "DecoderPacket":
        ctx = ast.context
        return cls(
            case_id=case_id,
            decoder_id=decoder_id,
            purpose=ctx.purpose,
            claim=ctx.claim,
            operation_path=ast.operation_path,
            invariants=list(ctx.invariants),
            unknowns=list(ctx.unknowns),
            authority=list(ctx.authority),
            participants=list(ctx.participants),
            affected_parties=list(ctx.affected_parties),
            evidence=list(ctx.evidence),
            provenance=list(ctx.provenance),
            dissent=list(ctx.dissent),
            value_ledger=list(ctx.value_ledger),
            consequences=list(ctx.consequences),
            consequence_horizon=ctx.consequence_horizon,
            recovery=list(ctx.recovery),
            confidence=confidence,
            notes=notes,
        )
