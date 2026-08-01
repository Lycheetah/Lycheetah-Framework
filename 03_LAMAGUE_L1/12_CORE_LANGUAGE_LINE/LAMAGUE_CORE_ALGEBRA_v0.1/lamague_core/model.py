from __future__ import annotations

from dataclasses import dataclass, field, asdict
from enum import Enum
from typing import Any, Optional


class Sort(str, Enum):
    INVARIANT = "Invariant"
    FIELD = "Field"
    FUSION = "Fusion"
    PATH = "Path"
    EXCHANGE = "Exchange"
    RECURRENCE = "Recurrence"
    COLLAPSE = "Collapse"
    ASCENT = "Ascent"
    REFERENCE = "Reference"


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
    sort: Sort = Sort.FIELD


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


@dataclass(frozen=True)
class Program:
    statements: tuple[Statement, ...]


def expr_to_dict(expr: Expr) -> dict[str, Any]:
    if isinstance(expr, Atom):
        return {"kind": "Atom", "name": expr.name, "sort": expr.sort.value, "raw": expr.raw}
    if isinstance(expr, Reference):
        return {"kind": "Reference", "name": expr.name, "raw": expr.raw}
    if isinstance(expr, Binary):
        return {
            "kind": "Binary", "operator": expr.operator, "raw": expr.raw,
            "left": expr_to_dict(expr.left), "right": expr_to_dict(expr.right)
        }
    raise TypeError(f"unsupported expression: {type(expr)!r}")


def statement_to_dict(stmt: Statement) -> dict[str, Any]:
    return {
        "kind": stmt.kind,
        "name": stmt.name,
        "level": stmt.level,
        "expression": expr_to_dict(stmt.expression) if stmt.expression else None,
        "expression_b": expr_to_dict(stmt.expression_b) if stmt.expression_b else None,
    }
