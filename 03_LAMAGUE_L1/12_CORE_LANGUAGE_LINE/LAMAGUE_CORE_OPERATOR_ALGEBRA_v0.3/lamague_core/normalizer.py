from __future__ import annotations

import hashlib
from typing import Any, Callable

from .model import Atom, Binary, Expr, ModifiedAtom, Reference


Normalized = tuple[Any, ...]


def normalize_with_trace(
    expr: Expr,
    resolve: Callable[[str], Expr],
) -> tuple[Normalized, list[dict[str, Any]]]:
    trace: list[dict[str, Any]] = []

    def walk(node: Expr) -> Normalized:
        if isinstance(node, Atom):
            return ("atom", node.name)

        if isinstance(node, ModifiedAtom):
            trace.append({
                "rule": "DERIVED_ATOM_DECOMPOSITION",
                "surface": node.name,
                "base": node.base.name,
                "modifier": node.modifier,
            })
            return ("modified", node.modifier, walk(node.base))

        if isinstance(node, Reference):
            resolved = resolve(node.name)
            trace.append({
                "rule": "REFERENCE_EXPANSION",
                "reference": node.name,
            })
            return walk(resolved)

        if not isinstance(node, Binary):
            raise TypeError(type(node))

        op = node.operator
        left = walk(node.left)
        right = walk(node.right)

        if op == "⊗":
            operands = []
            flattened = False

            def gather(value):
                nonlocal flattened
                if value and value[0] == "nary" and value[1] == "⊗":
                    flattened = True
                    operands.extend(value[2])
                else:
                    operands.append(value)

            gather(left)
            gather(right)
            if flattened:
                trace.append({"rule": "FUSION_ASSOCIATIVE_FLATTEN"})

            before = tuple(operands)
            operands = sorted(operands, key=canonical)
            if tuple(operands) != before:
                trace.append({"rule": "FUSION_COMMUTATIVE_SORT"})

            return ("nary", "⊗", tuple(operands))

        if op == "→":
            operands = []
            flattened = False

            def gather(value):
                nonlocal flattened
                if value and value[0] == "nary" and value[1] == "→":
                    flattened = True
                    operands.extend(value[2])
                else:
                    operands.append(value)

            gather(left)
            gather(right)
            if flattened:
                trace.append({"rule": "PROJECTION_ASSOCIATIVE_FLATTEN"})
            return ("nary", "→", tuple(operands))

        if op == "⇌":
            pair = (left, right)
            ordered = tuple(sorted(pair, key=canonical))
            if ordered != pair:
                trace.append({"rule": "EXCHANGE_SYMMETRIC_ORDER"})
            return ("binary", "⇌", ordered[0], ordered[1])

        # Directed operators retain exact grouping and order.
        return ("binary", op, left, right)

    return walk(expr), trace


def normalize(expr: Expr, resolve: Callable[[str], Expr]) -> Normalized:
    return normalize_with_trace(expr, resolve)[0]


def canonical(node: Normalized) -> str:
    kind = node[0]
    if kind == "atom":
        return node[1]
    if kind == "modified":
        modifier, base = node[1], node[2]
        base_text = canonical(base)
        if modifier == "↑":
            return f"{base_text}↑"
        if modifier == "inv":
            return f"{base_text}_inv"
        return f"{modifier}({base_text})"
    if kind == "nary":
        op = node[1]
        return "(" + f" {op} ".join(canonical(x) for x in node[2]) + ")"
    if kind == "binary":
        return f"({canonical(node[2])} {node[1]} {canonical(node[3])})"
    raise ValueError(node)


def semantic_hash(node: Normalized) -> str:
    return hashlib.sha256(canonical(node).encode("utf-8")).hexdigest()


def equivalent(a: Expr, b: Expr, resolve: Callable[[str], Expr]) -> bool:
    return normalize(a, resolve) == normalize(b, resolve)
