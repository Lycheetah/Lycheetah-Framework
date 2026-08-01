from __future__ import annotations

from dataclasses import dataclass, asdict
from enum import Enum
import hashlib
import json
from typing import Any

from .ontology import OPERATOR_SIGNATURES


class LawStatus(str, Enum):
    PROVEN = "PROVEN"
    REFUTED = "REFUTED"
    UNDECLARED = "UNDECLARED"
    DOMAIN_DEPENDENT = "DOMAIN_DEPENDENT"
    NOT_APPLICABLE = "NOT_APPLICABLE"


@dataclass(frozen=True)
class LawRecord:
    status: LawStatus
    basis: str
    witness: str | None = None
    counterexample: str | None = None
    value: str | None = None

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["status"] = self.status.value
        return payload


@dataclass(frozen=True)
class OperatorContract:
    symbol: str
    name: str
    directionality: str
    signature: dict[str, str]
    laws: dict[str, LawRecord]
    normalization_rules: tuple[str, ...]
    prohibited_inferences: tuple[str, ...]
    semantic_boundary: str

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["laws"] = {
            name: record.to_dict() for name, record in self.laws.items()
        }
        return payload


def _law(status, basis, witness=None, counterexample=None, value=None):
    return LawRecord(
        LawStatus(status),
        basis,
        witness=witness,
        counterexample=counterexample,
        value=value,
    )


COMMON = {
    "closure": _law(
        "PROVEN",
        "Both operands require StateLike and every result is a StateLike subtype.",
        witness="type lattice and operator signatures",
    ),
    "operational_reversibility": _law(
        "DOMAIN_DEPENDENT",
        "The symbolic core does not execute domain state changes.",
    ),
    "identity_element": _law(
        "UNDECLARED",
        "No universal identity has been justified for the core operator.",
    ),
    "annihilator": _law(
        "UNDECLARED",
        "No universal annihilator has been justified for the core operator.",
    ),
}


def _laws(**updates):
    merged = dict(COMMON)
    merged.update(updates)
    return merged


OPERATOR_CONTRACTS: dict[str, OperatorContract] = {
    "⊗": OperatorContract(
        symbol="⊗",
        name="fusion",
        directionality="UNDIRECTED",
        signature=OPERATOR_SIGNATURES["⊗"],
        laws=_laws(
            commutative=_law(
                "PROVEN",
                "Canonical fusion operands are sorted by canonical form.",
                witness="A ⊗ B ≡ B ⊗ A",
            ),
            associative=_law(
                "PROVEN",
                "Nested fusion nodes flatten to one n-ary fusion.",
                witness="(A ⊗ B) ⊗ C ≡ A ⊗ (B ⊗ C)",
            ),
            idempotent=_law(
                "REFUTED",
                "Duplicate fusion operands are preserved.",
                counterexample="A ⊗ A ≢ A",
            ),
            structural_inverse=_law(
                "UNDECLARED",
                "No inverse fusion operator exists in the core.",
            ),
            termination=_law(
                "NOT_APPLICABLE",
                "Fusion does not introduce iteration.",
            ),
        ),
        normalization_rules=(
            "flatten nested fusion",
            "sort operands by canonical form",
            "preserve duplicate operands",
        ),
        prohibited_inferences=(
            "do not infer idempotence",
            "do not infer an identity element",
            "do not infer semantic blending outside an adapter",
        ),
        semantic_boundary=(
            "Fusion represents structural composition only. It does not prove "
            "compatibility, agreement, or safe merger."
        ),
    ),
    "→": OperatorContract(
        symbol="→",
        name="projection",
        directionality="DIRECTED",
        signature=OPERATOR_SIGNATURES["→"],
        laws=_laws(
            commutative=_law(
                "REFUTED",
                "Projection preserves operand order.",
                counterexample="A → B ≢ B → A",
            ),
            associative=_law(
                "PROVEN",
                "Nested projection nodes flatten into an ordered path.",
                witness="(A → B) → C ≡ A → (B → C)",
            ),
            idempotent=_law(
                "REFUTED",
                "Repeated path nodes remain explicit.",
                counterexample="A → A ≢ A",
            ),
            structural_inverse=_law(
                "UNDECLARED",
                "Reversing a path is not an equivalence rule.",
            ),
            termination=_law(
                "NOT_APPLICABLE",
                "Projection does not introduce iteration.",
            ),
        ),
        normalization_rules=(
            "flatten nested projection",
            "preserve exact left-to-right order",
            "preserve repeated states",
        ),
        prohibited_inferences=(
            "do not reverse the path",
            "do not infer causality",
            "do not infer mutation of the left operand",
        ),
        semantic_boundary=(
            "Projection is an ordered symbolic path. Domain adapters decide whether "
            "it means transition, mapping, causation, or another relation."
        ),
    ),
    "⇌": OperatorContract(
        symbol="⇌",
        name="exchange",
        directionality="SYMMETRIC",
        signature=OPERATOR_SIGNATURES["⇌"],
        laws=_laws(
            commutative=_law(
                "PROVEN",
                "Exchange operands are canonically ordered.",
                witness="A ⇌ B ≡ B ⇌ A",
            ),
            associative=_law(
                "REFUTED",
                "Nested exchange grouping remains significant.",
                counterexample="(A ⇌ B) ⇌ C ≢ A ⇌ (B ⇌ C)",
            ),
            idempotent=_law(
                "REFUTED",
                "Self-exchange remains an explicit relation.",
                counterexample="A ⇌ A ≢ A",
            ),
            structural_inverse=_law(
                "PROVEN",
                "The structural inverse of exchange is itself.",
                witness="inverse(⇌) = ⇌",
                value="SELF",
            ),
            termination=_law(
                "NOT_APPLICABLE",
                "Exchange does not introduce iteration.",
            ),
        ),
        normalization_rules=(
            "sort the two direct operands",
            "preserve nested grouping",
        ),
        prohibited_inferences=(
            "do not flatten nested exchanges",
            "do not infer operational reversibility",
            "do not infer equal value transfer",
        ),
        semantic_boundary=(
            "Exchange is structurally symmetric. Whether an actual exchange can be "
            "undone is domain-dependent."
        ),
    ),
    "⟲": OperatorContract(
        symbol="⟲",
        name="recurrence",
        directionality="DIRECTED",
        signature=OPERATOR_SIGNATURES["⟲"],
        laws=_laws(
            commutative=_law(
                "REFUTED",
                "Recurrence preserves source and recurrence target.",
                counterexample="A ⟲ B ≢ B ⟲ A",
            ),
            associative=_law(
                "REFUTED",
                "Nested recurrence grouping remains significant.",
                counterexample="(A ⟲ B) ⟲ C ≢ A ⟲ (B ⟲ C)",
            ),
            idempotent=_law(
                "REFUTED",
                "A recurrence relation is not reduced to its operand.",
                counterexample="A ⟲ A ≢ A",
            ),
            structural_inverse=_law(
                "UNDECLARED",
                "No inverse recurrence law is defined.",
            ),
            termination=_law(
                "DOMAIN_DEPENDENT",
                "The core stores recurrence structure but has no loop condition, "
                "fixed-point order, or execution model.",
            ),
        ),
        normalization_rules=(
            "preserve direction",
            "preserve grouping",
            "do not execute or unroll",
        ),
        prohibited_inferences=(
            "do not infer termination",
            "do not infer convergence",
            "do not infer a fixed point",
        ),
        semantic_boundary=(
            "Recurrence records a directed return relation. Termination and "
            "convergence require a domain adapter."
        ),
    ),
    "↯": OperatorContract(
        symbol="↯",
        name="collapse",
        directionality="DIRECTED",
        signature=OPERATOR_SIGNATURES["↯"],
        laws=_laws(
            commutative=_law(
                "REFUTED",
                "Collapse preserves source and target.",
                counterexample="A ↯ B ≢ B ↯ A",
            ),
            associative=_law(
                "REFUTED",
                "Nested collapse grouping remains significant.",
                counterexample="(A ↯ B) ↯ C ≢ A ↯ (B ↯ C)",
            ),
            idempotent=_law(
                "REFUTED",
                "A collapse relation does not reduce to its operand.",
                counterexample="A ↯ A ≢ A",
            ),
            structural_inverse=_law(
                "UNDECLARED",
                "No recovery or inverse operator is implied by collapse.",
            ),
            termination=_law(
                "NOT_APPLICABLE",
                "Collapse does not introduce iteration.",
            ),
        ),
        normalization_rules=(
            "preserve direction",
            "preserve grouping",
            "preserve explicit null target",
        ),
        prohibited_inferences=(
            "do not interpret ↯ as a decision junction",
            "do not simplify A ↯ ∅ to ∅",
            "do not infer irrecoverability outside an adapter",
        ),
        semantic_boundary=(
            "Collapse is a directed structural relation. It does not prove deletion, "
            "failure, destruction, or irreversibility."
        ),
    ),
    "↗": OperatorContract(
        symbol="↗",
        name="ascent",
        directionality="DIRECTED",
        signature=OPERATOR_SIGNATURES["↗"],
        laws=_laws(
            commutative=_law(
                "REFUTED",
                "Ascent preserves source and target.",
                counterexample="A ↗ B ≢ B ↗ A",
            ),
            associative=_law(
                "REFUTED",
                "Nested ascent grouping remains significant.",
                counterexample="(A ↗ B) ↗ C ≢ A ↗ (B ↗ C)",
            ),
            idempotent=_law(
                "REFUTED",
                "An ascent relation does not reduce to its operand.",
                counterexample="A ↗ A ≢ A",
            ),
            structural_inverse=_law(
                "UNDECLARED",
                "No descent or inverse operator is implied.",
            ),
            termination=_law(
                "NOT_APPLICABLE",
                "Ascent does not introduce iteration.",
            ),
        ),
        normalization_rules=(
            "preserve direction",
            "preserve grouping",
        ),
        prohibited_inferences=(
            "do not infer improvement",
            "do not infer monotonic progress",
            "do not infer a numerical ordering",
        ),
        semantic_boundary=(
            "Ascent is a directed structural relation. Positive value, improvement, "
            "or hierarchy are not core-language guarantees."
        ),
    ),
}


LAW_ALIASES = {
    "commutative": "commutative",
    "associative": "associative",
    "idempotent": "idempotent",
    "closed": "closure",
    "closure": "closure",
    "reversible": "operational_reversibility",
    "operational_reversibility": "operational_reversibility",
    "inverse": "structural_inverse",
    "structural_inverse": "structural_inverse",
    "identity": "identity_element",
    "identity_element": "identity_element",
    "annihilator": "annihilator",
    "terminating": "termination",
    "termination": "termination",
}


def contract_record(symbol: str) -> dict[str, Any]:
    try:
        contract = OPERATOR_CONTRACTS[symbol]
    except KeyError as exc:
        raise ValueError(f"unknown core operator {symbol!r}") from exc
    payload = contract.to_dict()
    payload["contract_hash"] = contract_hash(symbol)
    return payload


def contract_hash(symbol: str) -> str:
    contract = OPERATOR_CONTRACTS[symbol].to_dict()
    raw = json.dumps(
        contract, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def law_result(symbol: str, law_name: str) -> dict[str, Any]:
    if law_name not in LAW_ALIASES:
        raise ValueError(f"unknown operator law {law_name!r}")
    canonical_name = LAW_ALIASES[law_name]
    contract = OPERATOR_CONTRACTS[symbol]
    record = contract.laws[canonical_name]
    return {
        "operator": symbol,
        "law": canonical_name,
        **record.to_dict(),
        "contract_hash": contract_hash(symbol),
    }


def structurally_composable(first: str, second: str) -> dict[str, Any]:
    a = OPERATOR_CONTRACTS[first]
    b = OPERATOR_CONTRACTS[second]
    composable = (
        a.signature["returns"] in {
            "Fusion", "Path", "Exchange", "Recurrence", "Collapse", "Ascent"
        }
        and b.signature["left"] == "StateLike"
    )
    return {
        "first": first,
        "second": second,
        "structurally_composable": composable,
        "reason": (
            f"{first} returns {a.signature['returns']}, a StateLike subtype; "
            f"{second} accepts StateLike."
        ),
        "semantic_legality": "DOMAIN_DEPENDENT",
    }


def composition_matrix() -> dict[str, Any]:
    symbols = tuple(OPERATOR_CONTRACTS)
    cells = {
        first: {
            second: structurally_composable(first, second)
            for second in symbols
        }
        for first in symbols
    }
    return {
        "version": "0.3.0",
        "operators": list(symbols),
        "cells": cells,
        "binding_boundary": (
            "Structural closure does not prove that a composition is meaningful "
            "inside any external domain."
        ),
    }


def contracts_export() -> dict[str, Any]:
    return {
        "version": "0.3.0",
        "operators": {
            symbol: contract_record(symbol)
            for symbol in OPERATOR_CONTRACTS
        },
        "composition_matrix": composition_matrix(),
        "binding_distinctions": {
            "structural_inverse": (
                "equivalence in the symbolic representation"
            ),
            "operational_reversibility": (
                "ability to undo a domain state change"
            ),
            "identity": "no core identity element is currently declared",
            "annihilator": "no core annihilator is currently declared",
        },
    }
