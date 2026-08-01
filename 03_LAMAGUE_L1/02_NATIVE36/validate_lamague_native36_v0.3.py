#!/usr/bin/env python3
"""Validate the LAMAGUE Native-36 v0.3 machine registry."""

from __future__ import annotations
import json
import sys
from pathlib import Path

REQUIRED = {
    "token","token_id","name","class","canon_status","primitive_status",
    "spoken_form","type_signature","accepts","returns","arity","preconditions",
    "preserves","failure_modes","recovery","radical_provenance","visual_logic",
    "examples","glyph_svg"
}

def validate(path: Path) -> list[str]:
    data = json.loads(path.read_text(encoding="utf-8"))
    errors: list[str] = []
    glyphs = data.get("base_glyphs", [])
    expected = list("0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ")

    if [g.get("token") for g in glyphs] != expected:
        errors.append("Base token order or membership is not exactly 0-9A-Z.")

    ids = [g.get("token_id") for g in glyphs]
    if len(ids) != len(set(ids)):
        errors.append("Duplicate token_id detected.")

    pua = [g.get("experimental_pua") for g in glyphs]
    if len(pua) != len(set(pua)):
        errors.append("Duplicate experimental PUA mapping detected.")

    for g in glyphs:
        missing = sorted(REQUIRED - set(g))
        if missing:
            errors.append(f"{g.get('token','?')}: missing fields {missing}")
        arity = g.get("arity", {})
        if arity.get("min", 0) > arity.get("max", 0):
            errors.append(f"{g.get('token','?')}: invalid arity range")
        if not g.get("radical_provenance"):
            errors.append(f"{g.get('token','?')}: radical provenance empty")
        if not g.get("failure_modes"):
            errors.append(f"{g.get('token','?')}: failure modes empty")

    valid_tokens = set(expected)
    for seal in data.get("compound_seals", []):
        unknown = [t for t in seal.get("expansion", []) if t not in valid_tokens]
        if unknown:
            errors.append(f"{seal.get('seal_id','?')}: unknown expansion tokens {unknown}")
        if seal.get("operation_count") != len(seal.get("expansion", [])):
            errors.append(f"{seal.get('seal_id','?')}: operation count mismatch")

    return errors

def main() -> int:
    path = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("LAMAGUE_NATIVE36_v0.3_MACHINE_CANON_REGISTRY.json")
    errors = validate(path)
    if errors:
        print("INVALID")
        for error in errors:
            print("-", error)
        return 1
    print("VALID")
    print("36 base tokens and compound seals passed registry integrity checks.")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
