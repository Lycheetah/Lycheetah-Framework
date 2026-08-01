from __future__ import annotations

import re
from typing import Any

from .model import ASTNode, ContextCapsule, ProgramAST
from .registry import Registry


class ParseError(ValueError):
    pass


_TOKEN_RE = re.compile(
    r"^(?P<name>[A-Za-z_][A-Za-z0-9_-]*|[A-Z])"
    r"(?:<(?P<typed>[^>]+)>)?"
    r"(?:\{(?P<payload>.*)\})?$"
)


def _split_payload(payload: str | None) -> dict[str, Any]:
    if not payload:
        return {}
    result: dict[str, Any] = {}
    positional: list[str] = []
    for raw in re.split(r"\s*,\s*", payload.strip()):
        if not raw:
            continue
        if "=" in raw:
            key, value = raw.split("=", 1)
            result[key.strip()] = value.strip()
        else:
            positional.append(raw.strip())
    if positional:
        result["values"] = positional
    return result


class Parser:
    def __init__(self, registry: Registry | None = None) -> None:
        self.registry = registry or Registry()

    def parse(self, source: str, context: ContextCapsule | None = None) -> ProgramAST:
        if not source or not source.strip():
            raise ParseError("Expression is empty")
        context = context or ContextCapsule()
        normalized = source.replace("→", "->")
        raw_tokens = [part.strip() for part in normalized.split("->") if part.strip()]
        if not raw_tokens:
            raise ParseError("No operations found")

        expanded_ops: list[tuple[str, dict[str, Any]]] = []
        expanded_from: list[str] = []

        for raw in raw_tokens:
            match = _TOKEN_RE.match(raw)
            if not match:
                raise ParseError(f"Invalid token syntax: {raw}")
            name = match.group("name").upper().replace("-", "_")
            typed = match.group("typed")
            args = _split_payload(match.group("payload"))
            if typed:
                args["type"] = typed.strip()

            if name in self.registry.seals:
                if args:
                    raise ParseError(
                        f"Seal annotations are not supported in v0.2: {raw}. "
                        "Expand the seal and annotate primitives."
                    )
                expanded_from.append(name)
                for op in self.registry.expand_seal(name, context.registry_version):
                    expanded_ops.append((op, {"expanded_from": name}))
            elif len(name) == 1 and name in self.registry.operations:
                expanded_ops.append((name, args))
            else:
                raise ParseError(f"Unknown operation or seal: {name}")

        nodes: list[ASTNode] = []
        for op, args in expanded_ops:
            spec = self.registry.operation(op)
            node_unknowns = list(context.unknowns)
            if op == "U" and args.get("type"):
                typed_unknown = str(args["type"])
                if typed_unknown not in node_unknowns:
                    node_unknowns.append(typed_unknown)
            value_flow = {}
            if op == "X":
                value_flow = {
                    "from": args.get("from"),
                    "to": args.get("to"),
                    "kind": args.get("kind") or args.get("value"),
                    "amount": float(args.get("amount", 0) or 0),
                    "unit": args.get("unit", "relative"),
                    "declared": str(args.get("declared", "true")).lower() == "true",
                    "consent": args.get("consent", ""),
                    "reversible": str(args.get("reversible", "true")).lower() == "true",
                }
            nodes.append(
                ASTNode(
                    operation=op,
                    operation_name=spec["name"],
                    input_types=list(spec["accepts"]),
                    output_type=spec["returns"],
                    arguments=args,
                    context={"domain": context.domain, "purpose": context.purpose},
                    provenance=list(context.provenance),
                    evidence=list(context.evidence),
                    unknowns=node_unknowns,
                    authority=list(context.authority),
                    invariants=list(context.invariants),
                    value_flow=value_flow,
                    consequence_horizon=context.consequence_horizon,
                    recovery=list(context.recovery),
                    version=context.registry_version,
                )
            )
        return ProgramAST(
            source=source,
            nodes=nodes,
            context=context,
            expanded_from=expanded_from,
            version=context.registry_version,
        )

    def normalize(self, ast: ProgramAST) -> str:
        parts: list[str] = []
        for node in ast.nodes:
            suffix = ""
            if node.operation == "U" and node.arguments.get("type"):
                suffix += f"<{node.arguments['type']}>"
            payload = {
                k: v
                for k, v in node.arguments.items()
                if k not in {"type", "expanded_from"}
            }
            if payload:
                body = ",".join(f"{k}={v}" for k, v in sorted(payload.items()))
                suffix += "{" + body + "}"
            parts.append(node.operation + suffix)
        return " -> ".join(parts)
