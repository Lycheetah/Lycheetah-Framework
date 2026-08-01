from __future__ import annotations

from enum import Enum
from typing import Iterable


class CoreType(str, Enum):
    STATE_LIKE = "StateLike"
    FIELD = "Field"
    MODIFIED_FIELD = "ModifiedField"
    INVARIANT = "Invariant"
    INVARIANT_MARKER = "InvariantMarker"
    INVARIANT_FIELD = "InvariantField"
    NULL_STATE = "NullState"
    COMPOSITE = "Composite"
    FUSION = "Fusion"
    PATH = "Path"
    EXCHANGE = "Exchange"
    RECURRENCE = "Recurrence"
    COLLAPSE = "Collapse"
    ASCENT = "Ascent"
    REFERENCE = "Reference"


TYPE_PARENTS: dict[CoreType, frozenset[CoreType]] = {
    CoreType.STATE_LIKE: frozenset(),
    CoreType.FIELD: frozenset({CoreType.STATE_LIKE}),
    CoreType.MODIFIED_FIELD: frozenset({CoreType.FIELD}),
    CoreType.INVARIANT: frozenset({CoreType.STATE_LIKE}),
    CoreType.INVARIANT_MARKER: frozenset({CoreType.INVARIANT}),
    # Ψ_inv is intentionally both a field and an invariant.
    CoreType.INVARIANT_FIELD: frozenset({CoreType.FIELD, CoreType.INVARIANT}),
    # ∅ remains historically I-class while being semantically distinct from missing data.
    CoreType.NULL_STATE: frozenset({CoreType.INVARIANT}),
    CoreType.COMPOSITE: frozenset({CoreType.STATE_LIKE}),
    CoreType.FUSION: frozenset({CoreType.COMPOSITE}),
    CoreType.PATH: frozenset({CoreType.COMPOSITE}),
    CoreType.EXCHANGE: frozenset({CoreType.COMPOSITE}),
    CoreType.RECURRENCE: frozenset({CoreType.COMPOSITE}),
    CoreType.COLLAPSE: frozenset({CoreType.COMPOSITE}),
    CoreType.ASCENT: frozenset({CoreType.COMPOSITE}),
    CoreType.REFERENCE: frozenset(),
}


TYPE_NAMES: dict[str, CoreType] = {t.value: t for t in CoreType}


ATOM_ONTOLOGY = {
    "Ao": {
        "type": CoreType.FIELD,
        "historical_class": "F-class",
        "role": "anchor",
        "definition": "anchor field",
        "primitive": True,
    },
    "Φ": {
        "type": CoreType.FIELD,
        "historical_class": "F-class",
        "role": "orientation",
        "definition": "orientation field",
        "primitive": True,
    },
    "Ψ": {
        "type": CoreType.FIELD,
        "historical_class": "F-class",
        "role": "contextual",
        "definition": "generic contextual fold/drift field",
        "primitive": True,
    },
    "S": {
        "type": CoreType.FIELD,
        "historical_class": "F-class",
        "role": "entropy_uncertainty",
        "definition": "entropy or uncertainty field",
        "primitive": True,
    },
    "Δ": {
        "type": CoreType.FIELD,
        "historical_class": "F-class",
        "role": "variation",
        "definition": "variation field",
        "primitive": True,
    },
    "⟟": {
        "type": CoreType.INVARIANT_MARKER,
        "historical_class": "I-class",
        "role": "fixed_point",
        "definition": "fixed-point marker",
        "primitive": True,
    },
    "∅": {
        "type": CoreType.NULL_STATE,
        "historical_class": "I-class",
        "role": "intentional_null",
        "definition": "intentional null or zero-node state; never means missing evidence",
        "primitive": True,
    },
    "⟐": {
        "type": CoreType.INVARIANT_MARKER,
        "historical_class": "I-class",
        "role": "stable_triad",
        "definition": "stable-triad marker",
        "primitive": True,
    },
    "⟁": {
        "type": CoreType.INVARIANT_MARKER,
        "historical_class": "I-class",
        "role": "integrity",
        "definition": "integrity marker",
        "primitive": True,
    },
    "∞": {
        "type": CoreType.INVARIANT_MARKER,
        "historical_class": "I-class",
        "role": "closed_cycle",
        "definition": "closed-cycle marker",
        "primitive": True,
    },
}

DERIVED_ONTOLOGY = {
    "Φ↑": {
        "type": CoreType.MODIFIED_FIELD,
        "historical_class": "F-class",
        "role": "oriented_ascent",
        "definition": "orientation field modified by ascent",
        "primitive": False,
        "base": "Φ",
        "modifier": "↑",
    },
    "Ψ_inv": {
        "type": CoreType.INVARIANT_FIELD,
        "historical_class": "I/F bridge",
        "role": "invariant_trajectory",
        "definition": "contextual Ψ field qualified as invariant",
        "primitive": False,
        "base": "Ψ",
        "modifier": "inv",
    },
}

OPERATOR_TYPES = {
    "⊗": CoreType.FUSION,
    "→": CoreType.PATH,
    "⇌": CoreType.EXCHANGE,
    "⟲": CoreType.RECURRENCE,
    "↯": CoreType.COLLAPSE,
    "↗": CoreType.ASCENT,
}

OPERATOR_SIGNATURES = {
    op: {
        "left": CoreType.STATE_LIKE.value,
        "right": CoreType.STATE_LIKE.value,
        "returns": result.value,
    }
    for op, result in OPERATOR_TYPES.items()
}


def parse_type(name: str) -> CoreType:
    try:
        return TYPE_NAMES[name]
    except KeyError as exc:
        raise ValueError(f"unknown LAMAGUE core type {name!r}") from exc


def direct_parents(core_type: CoreType) -> frozenset[CoreType]:
    return TYPE_PARENTS[core_type]


def all_supertypes(core_type: CoreType) -> frozenset[CoreType]:
    seen: set[CoreType] = set()
    stack = list(direct_parents(core_type))
    while stack:
        current = stack.pop()
        if current in seen:
            continue
        seen.add(current)
        stack.extend(direct_parents(current))
    return frozenset(seen)


def is_subtype(actual: CoreType, expected: CoreType) -> bool:
    return actual == expected or expected in all_supertypes(actual)


def ontology_record(symbol: str) -> dict:
    if symbol in ATOM_ONTOLOGY:
        item = dict(ATOM_ONTOLOGY[symbol])
    elif symbol in DERIVED_ONTOLOGY:
        item = dict(DERIVED_ONTOLOGY[symbol])
    else:
        raise KeyError(symbol)
    item["type"] = item["type"].value
    item["supertypes"] = sorted(t.value for t in all_supertypes(parse_type(item["type"])))
    return item


def ontology_export() -> dict:
    return {
        "version": "0.2.0",
        "primitive_atoms": {k: ontology_record(k) for k in ATOM_ONTOLOGY},
        "derived_atoms": {k: ontology_record(k) for k in DERIVED_ONTOLOGY},
        "type_parents": {
            t.value: sorted(parent.value for parent in parents)
            for t, parents in TYPE_PARENTS.items()
        },
        "operator_signatures": OPERATOR_SIGNATURES,
        "binding_distinctions": {
            "null": "∅ is an intentional null state",
            "missing": "missing or unavailable evidence is not represented by ∅ in the core",
            "error": "invalid syntax or typing produces a rejected result, not ∅",
            "contradiction": "contradiction is not silently collapsed to ∅",
        },
    }
