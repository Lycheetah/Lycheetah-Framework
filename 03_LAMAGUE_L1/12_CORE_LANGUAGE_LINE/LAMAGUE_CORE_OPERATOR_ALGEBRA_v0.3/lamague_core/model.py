from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Optional

from .ontology import CoreType


@dataclass(frozen=True)
class WarningRecord:
    code: str
    message: str
    raw: str
    canonical: str
    line: int
    column: int


@dataclass(frozen=True)
class Token:
    kind: str
    value: str
    raw: str
    line: int
    column: int


@dataclass(frozen=True)
class Expr:
    raw: Optional[str] = None


@dataclass(frozen=True)
class Atom(Expr):
    name: str = ""
    core_type: CoreType = CoreType.FIELD
    role: str = ""


@dataclass(frozen=True)
class ModifiedAtom(Expr):
    name: str = ""
    base: Atom = field(default_factory=Atom)
    modifier: str = ""
    core_type: CoreType = CoreType.MODIFIED_FIELD
    role: str = ""


@dataclass(frozen=True)
class Reference(Expr):
    name: str = ""


@dataclass(frozen=True)
class Binary(Expr):
    operator: str = ""
    left: Expr = field(default_factory=Expr)
    right: Expr = field(default_factory=Expr)


@dataclass(frozen=True)
class Statement:
    kind: str
    name: Optional[str] = None
    expression: Optional[Expr] = None
    expression_b: Optional[Expr] = None
    level: Optional[str] = None
    type_name: Optional[str] = None
    type_name_b: Optional[str] = None
    operator: Optional[str] = None
    operator_b: Optional[str] = None
    property_name: Optional[str] = None


@dataclass(frozen=True)
class Program:
    statements: tuple[Statement, ...]


def expr_to_dict(expr: Expr) -> dict[str, Any]:
    if isinstance(expr, Atom):
        return {
            "kind": "Atom",
            "name": expr.name,
            "core_type": expr.core_type.value,
            "role": expr.role,
            "raw": expr.raw,
        }
    if isinstance(expr, ModifiedAtom):
        return {
            "kind": "ModifiedAtom",
            "name": expr.name,
            "base": expr_to_dict(expr.base),
            "modifier": expr.modifier,
            "core_type": expr.core_type.value,
            "role": expr.role,
            "raw": expr.raw,
        }
    if isinstance(expr, Reference):
        return {"kind": "Reference", "name": expr.name, "raw": expr.raw}
    if isinstance(expr, Binary):
        return {
            "kind": "Binary",
            "operator": expr.operator,
            "raw": expr.raw,
            "left": expr_to_dict(expr.left),
            "right": expr_to_dict(expr.right),
        }
    raise TypeError(f"unsupported expression: {type(expr)!r}")


def statement_to_dict(stmt: Statement) -> dict[str, Any]:
    return {
        "kind": stmt.kind,
        "name": stmt.name,
        "level": stmt.level,
        "type_name": stmt.type_name,
        "type_name_b": stmt.type_name_b,
        "operator": stmt.operator,
        "operator_b": stmt.operator_b,
        "property_name": stmt.property_name,
        "expression": expr_to_dict(stmt.expression) if stmt.expression else None,
        "expression_b": expr_to_dict(stmt.expression_b) if stmt.expression_b else None,
    }
