from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .errors import SemanticError
from .model import Atom, Binary, Expr, Program, Reference, Sort, WarningRecord, expr_to_dict
from .normalizer import canonical, equivalent, normalize, semantic_hash

OUTPUT_SORT = {
    "⊗": Sort.FUSION,
    "→": Sort.PATH,
    "⇌": Sort.EXCHANGE,
    "⟲": Sort.RECURRENCE,
    "↯": Sort.COLLAPSE,
    "↗": Sort.ASCENT,
}


@dataclass(frozen=True)
class Macro:
    level: str
    expression: Expr
    normalized: tuple


class Runtime:
    def __init__(self, warnings: list[WarningRecord] | None = None):
        self.bindings: dict[str, Expr] = {}
        self.invariants: dict[str, Expr] = {}
        self.macros: dict[str, Macro] = {}
        self.requirements: list[tuple] = []
        self.prohibitions: list[tuple] = []
        self.checks: list[dict[str, Any]] = []
        self.expressions: list[tuple] = []
        self.warnings = warnings or []

    def resolve(self, name: str, stack: tuple[str, ...] = ()) -> Expr:
        if name in stack:
            raise SemanticError(f"cyclic reference: {' -> '.join(stack + (name,))}")
        if name in self.bindings:
            return self.bindings[name]
        if name in self.invariants:
            return self.invariants[name]
        if name in self.macros:
            return self.macros[name].expression
        raise SemanticError(f"unknown reference {name!r}")

    def infer(self, expr: Expr, stack: tuple[str, ...] = ()) -> Sort:
        if isinstance(expr, Atom):
            return expr.sort
        if isinstance(expr, Reference):
            if expr.name in stack:
                raise SemanticError(f"cyclic reference involving {expr.name!r}")
            return self.infer(self.resolve(expr.name, stack), stack + (expr.name,))
        if isinstance(expr, Binary):
            left_sort = self.infer(expr.left, stack)
            right_sort = self.infer(expr.right, stack)
            if left_sort == Sort.REFERENCE or right_sort == Sort.REFERENCE:
                raise SemanticError("unresolved reference")
            return OUTPUT_SORT[expr.operator]
        raise SemanticError(f"unsupported expression {type(expr)!r}")

    def bind(self, namespace: str, name: str, expr: Expr):
        if name in self.bindings or name in self.invariants or name in self.macros:
            raise SemanticError(f"name {name!r} is immutable and already defined")
        self.infer(expr)
        getattr(self, namespace)[name] = expr

    def execute(self, program: Program) -> dict[str, Any]:
        statement_results = []
        for stmt in program.statements:
            if stmt.kind == "let":
                self.bind("bindings", stmt.name, stmt.expression)
                n = normalize(stmt.expression, self.resolve)
                statement_results.append({"kind": "let", "name": stmt.name, "sort": self.infer(stmt.expression).value, "normal_form": canonical(n)})
            elif stmt.kind == "invariant":
                self.bind("invariants", stmt.name, stmt.expression)
                n = normalize(stmt.expression, self.resolve)
                statement_results.append({"kind": "invariant", "name": stmt.name, "normal_form": canonical(n), "semantic_hash": semantic_hash(n)})
            elif stmt.kind == "macro":
                if stmt.name in self.bindings or stmt.name in self.invariants or stmt.name in self.macros:
                    raise SemanticError(f"name {stmt.name!r} is immutable and already defined")
                self.infer(stmt.expression)
                n = normalize(stmt.expression, self.resolve)
                self.macros[stmt.name] = Macro(stmt.level, stmt.expression, n)
                statement_results.append({"kind": "macro", "name": stmt.name, "level": stmt.level, "normal_form": canonical(n), "compression": self._compression_report(stmt.name, n)})
            elif stmt.kind == "require":
                self.infer(stmt.expression)
                n = normalize(stmt.expression, self.resolve)
                self.requirements.append(n)
                statement_results.append({"kind": "require", "normal_form": canonical(n), "semantic_hash": semantic_hash(n)})
            elif stmt.kind == "forbid":
                self.infer(stmt.expression)
                n = normalize(stmt.expression, self.resolve)
                self.prohibitions.append(n)
                statement_results.append({"kind": "forbid", "normal_form": canonical(n), "semantic_hash": semantic_hash(n)})
            elif stmt.kind == "check":
                self.infer(stmt.expression); self.infer(stmt.expression_b)
                result = equivalent(stmt.expression, stmt.expression_b, self.resolve)
                record = {"kind": "equivalence", "equivalent": result, "left": canonical(normalize(stmt.expression, self.resolve)), "right": canonical(normalize(stmt.expression_b, self.resolve))}
                self.checks.append(record)
                statement_results.append(record)
            elif stmt.kind == "expression":
                self.infer(stmt.expression)
                n = normalize(stmt.expression, self.resolve)
                self.expressions.append(n)
                statement_results.append({"kind": "expression", "sort": self.infer(stmt.expression).value, "normal_form": canonical(n), "semantic_hash": semantic_hash(n)})
            else:
                raise SemanticError(f"unknown statement kind {stmt.kind}")

        return {
            "lamague_core_version": "0.1.0",
            "status": "ACCEPTED",
            "statements": statement_results,
            "bindings": {k: canonical(normalize(v, self.resolve)) for k, v in self.bindings.items()},
            "invariants": {k: canonical(normalize(v, self.resolve)) for k, v in self.invariants.items()},
            "requirements": [canonical(x) for x in self.requirements],
            "prohibitions": [canonical(x) for x in self.prohibitions],
            "macros": {k: {"level": v.level, "normal_form": canonical(v.normalized), "compression": self._compression_report(k, v.normalized)} for k, v in self.macros.items()},
            "checks": self.checks,
            "expressions": [canonical(x) for x in self.expressions],
            "warnings": [w.__dict__ for w in self.warnings],
            "claim_boundary": [
                "parsing does not prove truth",
                "core tests do not validate any domain adapter",
                "macro expansion is lossless AST aliasing, not unrestricted natural-language compression",
                "LAMAGUE Core is not an alignment or physical-theory guarantee",
            ],
        }

    @staticmethod
    def _compression_report(name: str, normalized: tuple) -> dict[str, Any]:
        expanded = canonical(normalized)
        return {
            "expanded_characters": len(expanded),
            "macro_characters": len(name),
            "character_ratio": round(len(expanded) / max(1, len(name)), 6),
            "expanded_tokens": len(expanded.replace("(", " ").replace(")", " ").split()),
            "macro_tokens": 1,
            "roundtrip_law": "expand(macro) = normalized_expression",
        }
