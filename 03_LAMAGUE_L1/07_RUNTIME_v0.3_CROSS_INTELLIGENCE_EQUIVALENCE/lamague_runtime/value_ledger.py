from __future__ import annotations

from typing import Any


def normalize_value_entries(entries: list[dict[str, Any]]) -> list[dict[str, Any]]:
    normalized: list[dict[str, Any]] = []
    for entry in entries:
        normalized.append({
            "source": entry.get("source") or entry.get("from") or "",
            "recipient": entry.get("recipient") or entry.get("to") or "",
            "kind": entry.get("kind") or entry.get("value") or "unspecified",
            "amount": float(entry.get("amount", 0) or 0),
            "unit": entry.get("unit", "relative"),
            "declared": bool(entry.get("declared", True)),
            "consent": entry.get("consent", ""),
            "affected_parties": list(entry.get("affected_parties", [])),
            "reversible": bool(entry.get("reversible", True)),
        })
    return normalized


def hidden_extraction(entries: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [
        entry for entry in normalize_value_entries(entries)
        if not entry["declared"] or not entry["consent"]
    ]
