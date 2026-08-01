from __future__ import annotations

import hashlib
from typing import Any

from .normalizer import Normalized, canonical


def semantic_graph(root: Normalized) -> dict[str, Any]:
    nodes: dict[str, dict] = {}
    edges: list[dict] = []

    def visit(node: Normalized) -> str:
        text = canonical(node)
        node_id = hashlib.sha256(text.encode("utf-8")).hexdigest()[:16]
        kind = node[0]

        if node_id in nodes:
            return node_id

        if kind == "atom":
            nodes[node_id] = {
                "id": node_id,
                "kind": "Atom",
                "label": node[1],
                "canonical": text,
            }
        elif kind == "modified":
            nodes[node_id] = {
                "id": node_id,
                "kind": "Modifier",
                "label": node[1],
                "canonical": text,
            }
            child_id = visit(node[2])
            edges.append(
                {"from": node_id, "to": child_id, "position": 0, "role": "base"}
            )
        else:
            nodes[node_id] = {
                "id": node_id,
                "kind": "Operator",
                "label": node[1],
                "canonical": text,
            }
            children = node[2] if kind == "nary" else (node[2], node[3])
            for index, child in enumerate(children):
                child_id = visit(child)
                edges.append(
                    {"from": node_id, "to": child_id, "position": index}
                )
        return node_id

    root_id = visit(root)
    return {
        "root": root_id,
        "nodes": sorted(nodes.values(), key=lambda x: x["id"]),
        "edges": sorted(
            edges,
            key=lambda x: (
                x["from"],
                x["position"],
                x["to"],
                x.get("role", ""),
            ),
        ),
    }
