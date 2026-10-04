from __future__ import annotations
import json, re, sys
from pathlib import Path
BASE = Path(__file__).parent

def load(name):
    return json.loads((BASE/name).read_text(encoding="utf-8"))

def validate():
    roots = load("roots.json")
    mantles = load("mantles.json")
    forms = load("forms.json")
    states = load("title_state_machine.json")
    errors, warnings = [], []
    root_ids = {r["id"] for r in roots}
    mantle_ids = {m["id"] for m in mantles}
    state_ids = set(states["states"])

    if len(roots) != 72: errors.append(f"expected 72 roots, found {len(roots)}")
    if len(mantles) != 18: errors.append(f"expected 18 Great Mantles, found {len(mantles)}")
    if len(forms) != 54: errors.append(f"expected 54 Forms, found {len(forms)}")
    if len(mantles)+len(forms) != 72: errors.append("playable identity total must equal 72")

    names = [x["name"].casefold() for x in mantles] + [x["name"].casefold() for x in forms]
    if len(names) != len(set(names)): errors.append("duplicate playable identity name")

    counts = {}
    for f in forms:
        counts[f["parent"]] = counts.get(f["parent"],0)+1
        if f["parent"] not in mantle_ids: errors.append(f"{f['name']}: unknown parent {f['parent']}")
        missing = set(f["roots"]) - root_ids
        if missing: errors.append(f"{f['name']}: unknown roots {sorted(missing)}")
        bad = set(f["allowed_states"]) - state_ids
        if bad: errors.append(f"{f['name']}: unknown states {sorted(bad)}")
        for required in ("reading","title","recovery","trial","shadow","status"):
            if not f.get(required): errors.append(f"{f['name']}: missing {required}")
    for m in mantles:
        if counts.get(m["id"],0) != 3:
            errors.append(f"{m['name']}: expected 3 Forms, found {counts.get(m['id'],0)}")

    return errors, warnings

if __name__ == "__main__":
    errors, warnings = validate()
    for w in warnings: print("WARN:",w)
    for e in errors: print("ERROR:",e)
    if errors: raise SystemExit(1)
    print("PASS: 18 Great Mantles + 54 Forms = 72 playable identities")
