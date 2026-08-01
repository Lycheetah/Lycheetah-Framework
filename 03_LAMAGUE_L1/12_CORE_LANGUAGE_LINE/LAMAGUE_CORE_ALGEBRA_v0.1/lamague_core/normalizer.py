from __future__ import annotations

import hashlib
from typing import Any, Callable

from .model import Atom, Binary, Expr, Reference


Normalized = tuple[Any, ...]


def normalize(expr: Expr, resolve: Callable[[str], Expr]) -> Normalized:
    if isinstance(expr, Atom):
        return ("atom", expr.name)
    if isinstance(expr, Reference):
        return normalize(resolve(expr.name), resolve)
    if not isinstance(expr, Binary):
        raise TypeError(type(expr))

    op = expr.operator
    left = normalize(expr.left, resolve)
    right = normalize(expr.right, resolve)

    if op == "⊗":
        operands = []
        def gather(node):
            if node and node[0] == "nary" and node[1] == "⊗":
                operands.extend(node[2])
            else:
                operands.append(node)
        gather(left); gather(right)
        operands = sorted(operands, key=canonical)
        return ("nary", "⊗", tuple(operands))

    if op == "→":
        operands = []
        def gather(node):
            if node and node[0] == "nary" and node[1] == "→":
                operands.extend(node[2])
            else:
                operands.append(node)
        gather(left); gather(right)
        return ("nary", "→", tuple(operands))

    if op == "⇌":
        pair = sorted((left, right), key=canonical)
        return ("binary", "⇌", pair[0], pair[1])

    return ("binary", op, left, right)


def canonical(node: Normalized) -> str:
    kind = node[0]
    if kind == "atom":
        return node[1]
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
