from __future__ import annotations

from typing import Any

from .model import ProgramAST


PROTECTED_DISSENT_PATH = ["W", "U", "G", "V", "Y"]


def has_protected_dissent_path(ast: ProgramAST) -> bool:
    path = ast.operation_path
    n = len(PROTECTED_DISSENT_PATH)
    return any(path[i:i+n] == PROTECTED_DISSENT_PATH for i in range(len(path) - n + 1))


def normalize_dissent(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    normalized: list[dict[str, Any]] = []
    for record in records:
        normalized.append({
            "parties": list(record.get("parties", [])),
            "positions": dict(record.get("positions", {})),
            "unknown_type": record.get("unknown_type", "disagreement"),
            "protected_boundaries": list(record.get("protected_boundaries", [])),
            "status": str(record.get("status", "UNRESOLVED")).upper(),
        })
    return normalized
