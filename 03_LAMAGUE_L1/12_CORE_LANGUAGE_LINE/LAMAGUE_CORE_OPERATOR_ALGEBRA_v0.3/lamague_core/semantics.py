from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .errors import SemanticError
from .model import Atom, Binary, Expr, ModifiedAtom, Program, Reference, WarningRecord
from .normalizer import (
    canonical,
    equivalent,
    normalize,
    normalize_with_trace,
    semantic_hash,
)
from .contracts import (
    contract_record,
    law_result,
    structurally_composable,
)
from .ontology import (
    CoreType,
    OPERATOR_SIGNATURES,
    OPERATOR_TYPES,
    TYPE_NAMES,
    all_supertypes,
    is_subtype,
    ontology_record,
    parse_type,
)


@dataclass(frozen=True)
class Macro:
    level: str
    expression: Expr
    normalized: tuple
    core_type: CoreType


class Runtime:
    def __init__(self, warnings: list[WarningRecord] | None = None):
        self.bindings: dict[str, Expr] = {}
        self.binding_types: dict[str, CoreType] = {}
        self.invariants: dict[str, Expr] = {}
        self.invariant_types: dict[str, CoreType] = {}
        self.macros: dict[str, Macro] = {}
        self.requirements: list[tuple] = []
        self.prohibitions: list[tuple] = []
        self.checks: list[dict[str, Any]] = []
        self.descriptions: list[dict[str, Any]] = []
        self.expressions: list[tuple] = []
        self.warnings = warnings or []

    def resolve(self, name: str, stack: tuple[str, ...] = ()) -> Expr:
        if name in stack:
            raise SemanticError(
                f"cyclic reference: {' -> '.join(stack + (name,))}"
            )
        if name in self.bindings:
            return self.bindings[name]
        if name in self.invariants:
            return self.invariants[name]
        if name in self.macros:
            return self.macros[name].expression
        raise SemanticError(f"unknown reference {name!r}")

    def infer(self, expr: Expr, stack: tuple[str, ...] = ()) -> CoreType:
        if isinstance(expr, Atom):
            return expr.core_type

        if isinstance(expr, ModifiedAtom):
            base_type = self.infer(expr.base, stack)
            if expr.modifier == "↑" and not is_subtype(base_type, CoreType.FIELD):
                raise SemanticError("ascent modifier ↑ requires a Field base")
            if expr.modifier == "inv" and not is_subtype(
                base_type, CoreType.FIELD
            ):
                raise SemanticError("invariant modifier inv requires a Field base")
            return expr.core_type

        if isinstance(expr, Reference):
            if expr.name in stack:
                raise SemanticError(
                    f"cyclic reference involving {expr.name!r}"
                )
            return self.infer(
                self.resolve(expr.name, stack), stack + (expr.name,)
            )

        if isinstance(expr, Binary):
            left_type = self.infer(expr.left, stack)
            right_type = self.infer(expr.right, stack)
            signature = OPERATOR_SIGNATURES[expr.operator]
            required_left = parse_type(signature["left"])
            required_right = parse_type(signature["right"])
            if not is_subtype(left_type, required_left):
                raise SemanticError(
                    f"operator {expr.operator} requires left operand "
                    f"{required_left.value}; got {left_type.value}"
                )
            if not is_subtype(right_type, required_right):
                raise SemanticError(
                    f"operator {expr.operator} requires right operand "
                    f"{required_right.value}; got {right_type.value}"
                )
            return OPERATOR_TYPES[expr.operator]

        raise SemanticError(f"unsupported expression {type(expr)!r}")

    def assert_annotation(
        self, actual: CoreType, annotation: str | None, context: str
    ):
        if annotation is None:
            return
        expected = parse_type(annotation)
        if not is_subtype(actual, expected):
            raise SemanticError(
                f"{context} declared as {expected.value} but expression "
                f"has type {actual.value}"
            )

    def bind(
        self,
        namespace: str,
        type_namespace: str,
        name: str,
        expr: Expr,
        annotation: str | None = None,
    ):
        if (
            name in self.bindings
            or name in self.invariants
            or name in self.macros
        ):
            raise SemanticError(
                f"name {name!r} is immutable and already defined"
            )
        actual = self.infer(expr)
        self.assert_annotation(actual, annotation, f"name {name!r}")
        getattr(self, namespace)[name] = expr
        getattr(self, type_namespace)[name] = actual

    @staticmethod
    def type_description(core_type: CoreType) -> dict[str, Any]:
        return {
            "type": core_type.value,
            "supertypes": sorted(
                t.value for t in all_supertypes(core_type)
            ),
        }

    def describe(self, expr: Expr) -> dict[str, Any]:
        actual = self.infer(expr)
        normalized, rewrite_trace = normalize_with_trace(expr, self.resolve)
        record: dict[str, Any] = {
            "normal_form": canonical(normalized),
            "semantic_hash": semantic_hash(normalized),
            **self.type_description(actual),
            "rewrite_trace": rewrite_trace,
        }
        if isinstance(expr, Atom):
            record["ontology"] = ontology_record(expr.name)
        elif isinstance(expr, ModifiedAtom):
            record["ontology"] = ontology_record(expr.name)
            record["decomposition"] = {
                "base": expr.base.name,
                "modifier": expr.modifier,
            }
        elif isinstance(expr, Binary):
            record["operator"] = expr.operator
            record["signature"] = OPERATOR_SIGNATURES[expr.operator]
            record["left_type"] = self.infer(expr.left).value
            record["right_type"] = self.infer(expr.right).value
        elif isinstance(expr, Reference):
            record["reference"] = expr.name
            record["resolved"] = canonical(normalized)
        return record

    def execute(self, program: Program) -> dict[str, Any]:
        statement_results = []

        for stmt in program.statements:
            if stmt.kind == "let":
                self.bind(
                    "bindings",
                    "binding_types",
                    stmt.name,
                    stmt.expression,
                    stmt.type_name,
                )
                n = normalize(stmt.expression, self.resolve)
                actual = self.infer(stmt.expression)
                statement_results.append(
                    {
                        "kind": "let",
                        "name": stmt.name,
                        "declared_type": stmt.type_name,
                        "type": actual.value,
                        "normal_form": canonical(n),
                    }
                )

            elif stmt.kind == "invariant":
                self.bind(
                    "invariants",
                    "invariant_types",
                    stmt.name,
                    stmt.expression,
                    stmt.type_name,
                )
                n = normalize(stmt.expression, self.resolve)
                actual = self.infer(stmt.expression)
                statement_results.append(
                    {
                        "kind": "invariant",
                        "name": stmt.name,
                        "declared_type": stmt.type_name,
                        "type": actual.value,
                        "normal_form": canonical(n),
                        "semantic_hash": semantic_hash(n),
                    }
                )

            elif stmt.kind == "macro":
                if (
                    stmt.name in self.bindings
                    or stmt.name in self.invariants
                    or stmt.name in self.macros
                ):
                    raise SemanticError(
                        f"name {stmt.name!r} is immutable and already defined"
                    )
                actual = self.infer(stmt.expression)
                self.assert_annotation(
                    actual, stmt.type_name, f"macro {stmt.name!r}"
                )
                n = normalize(stmt.expression, self.resolve)
                self.macros[stmt.name] = Macro(
                    stmt.level, stmt.expression, n, actual
                )
                statement_results.append(
                    {
                        "kind": "macro",
                        "name": stmt.name,
                        "level": stmt.level,
                        "declared_type": stmt.type_name,
                        "type": actual.value,
                        "normal_form": canonical(n),
                        "compression": self._compression_report(
                            stmt.name, n
                        ),
                    }
                )

            elif stmt.kind == "require":
                actual = self.infer(stmt.expression)
                n = normalize(stmt.expression, self.resolve)
                self.requirements.append(n)
                statement_results.append(
                    {
                        "kind": "require",
                        "type": actual.value,
                        "normal_form": canonical(n),
                        "semantic_hash": semantic_hash(n),
                    }
                )

            elif stmt.kind == "forbid":
                actual = self.infer(stmt.expression)
                n = normalize(stmt.expression, self.resolve)
                self.prohibitions.append(n)
                statement_results.append(
                    {
                        "kind": "forbid",
                        "type": actual.value,
                        "normal_form": canonical(n),
                        "semantic_hash": semantic_hash(n),
                    }
                )

            elif stmt.kind == "check":
                self.infer(stmt.expression)
                self.infer(stmt.expression_b)
                left_normal, left_trace = normalize_with_trace(
                    stmt.expression, self.resolve
                )
                right_normal, right_trace = normalize_with_trace(
                    stmt.expression_b, self.resolve
                )
                result = left_normal == right_normal
                record = {
                    "kind": "equivalence",
                    "equivalent": result,
                    "method": "canonical_normal_form",
                    "left": canonical(left_normal),
                    "right": canonical(right_normal),
                    "left_rewrite_trace": left_trace,
                    "right_rewrite_trace": right_trace,
                }
                self.checks.append(record)
                statement_results.append(record)

            elif stmt.kind == "type_check":
                actual = self.infer(stmt.expression)
                expected = parse_type(stmt.type_name)
                result = is_subtype(actual, expected)
                record = {
                    "kind": "type_check",
                    "matches": result,
                    "actual": actual.value,
                    "expected": expected.value,
                    "normal_form": canonical(
                        normalize(stmt.expression, self.resolve)
                    ),
                }
                self.checks.append(record)
                statement_results.append(record)

            elif stmt.kind == "subtype_check":
                actual = parse_type(stmt.type_name)
                expected = parse_type(stmt.type_name_b)
                result = is_subtype(actual, expected)
                record = {
                    "kind": "subtype_check",
                    "is_subtype": result,
                    "actual": actual.value,
                    "expected": expected.value,
                }
                self.checks.append(record)
                statement_results.append(record)

            elif stmt.kind == "law_check":
                try:
                    record = {
                        "kind": "operator_law",
                        **law_result(stmt.operator, stmt.property_name),
                    }
                except ValueError as exc:
                    raise SemanticError(str(exc)) from exc
                self.checks.append(record)
                statement_results.append(record)

            elif stmt.kind == "composition_check":
                try:
                    record = {
                        "kind": "operator_composition",
                        **structurally_composable(
                            stmt.operator, stmt.operator_b
                        ),
                    }
                except KeyError as exc:
                    raise SemanticError(
                        f"unknown core operator {exc.args[0]!r}"
                    ) from exc
                self.checks.append(record)
                statement_results.append(record)

            elif stmt.kind == "describe_operator":
                try:
                    record = {
                        "kind": "operator_contract",
                        **contract_record(stmt.operator),
                    }
                except ValueError as exc:
                    raise SemanticError(str(exc)) from exc
                self.descriptions.append(record)
                statement_results.append(record)

            elif stmt.kind == "describe":
                record = {"kind": "describe", **self.describe(stmt.expression)}
                self.descriptions.append(record)
                statement_results.append(record)

            elif stmt.kind == "expression":
                actual = self.infer(stmt.expression)
                n = normalize(stmt.expression, self.resolve)
                self.expressions.append(n)
                statement_results.append(
                    {
                        "kind": "expression",
                        "type": actual.value,
                        "normal_form": canonical(n),
                        "semantic_hash": semantic_hash(n),
                    }
                )

            else:
                raise SemanticError(
                    f"unknown statement kind {stmt.kind}"
                )

        return {
            "lamague_core_version": "0.3.0",
            "status": "ACCEPTED",
            "statements": statement_results,
            "bindings": {
                k: {
                    "type": self.binding_types[k].value,
                    "normal_form": canonical(normalize(v, self.resolve)),
                }
                for k, v in self.bindings.items()
            },
            "invariants": {
                k: {
                    "type": self.invariant_types[k].value,
                    "normal_form": canonical(normalize(v, self.resolve)),
                }
                for k, v in self.invariants.items()
            },
            "requirements": [canonical(x) for x in self.requirements],
            "prohibitions": [canonical(x) for x in self.prohibitions],
            "macros": {
                k: {
                    "level": v.level,
                    "type": v.core_type.value,
                    "normal_form": canonical(v.normalized),
                    "compression": self._compression_report(
                        k, v.normalized
                    ),
                }
                for k, v in self.macros.items()
            },
            "checks": self.checks,
            "descriptions": self.descriptions,
            "expressions": [canonical(x) for x in self.expressions],
            "warnings": [w.__dict__ for w in self.warnings],
            "operator_contract_lock": {
                "identity_elements_declared": False,
                "annihilators_declared": False,
                "structural_inverse_separated_from_operational_reversibility": True,
                "recurrence_termination": "DOMAIN_DEPENDENT",
                "null_simplification_forbidden": True,
            },
            "ontology_lock": {
                "null_is_not_missing": True,
                "phi_ascent_is_derived": True,
                "psi_invariant_is_derived": True,
                "domain_adapters_absent": True,
            },
            "claim_boundary": [
                "parsing does not prove truth",
                "type validity does not prove domain validity",
                "∅ is intentional null and never means missing evidence",
                "core tests do not validate any domain adapter",
                "macro expansion is lossless AST aliasing, not unrestricted natural-language compression",
                "operator contracts describe symbolic structure, not domain execution",
                "no universal identity or annihilator is currently declared",
                "structural symmetry does not prove operational reversibility",
                "recurrence does not imply termination or convergence",
                "LAMAGUE Core is not an alignment or physical-theory guarantee",
            ],
        }

    @staticmethod
    def _compression_report(
        name: str, normalized: tuple
    ) -> dict[str, Any]:
        expanded = canonical(normalized)
        return {
            "expanded_characters": len(expanded),
            "macro_characters": len(name),
            "character_ratio": round(
                len(expanded) / max(1, len(name)), 6
            ),
            "expanded_tokens": len(
                expanded.replace("(", " ").replace(")", " ").split()
            ),
            "macro_tokens": 1,
            "roundtrip_law": (
                "expand(macro) = normalized_expression"
            ),
        }
