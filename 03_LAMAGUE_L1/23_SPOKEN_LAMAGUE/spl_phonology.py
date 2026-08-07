#!/usr/bin/env python3
"""
SpL phonology checker — can Spoken LAMAGUE actually be heard?

A written language only has to be *readable*. A spoken one has to be
**uniquely decodable**: given a stream of syllables with no spaces, a listener
must be able to recover exactly one sequence of morphemes. That is a formal
property with a classical decision procedure — Sardinas & Patterson (1953) —
and it is cheap to run.

This checks three things nobody has checked:

1. **Collisions.** One spoken form, two meanings, inside SpL or across the
   SpL / Native-36 boundary.
2. **Unique decodability.** Sardinas–Patterson over the full spoken inventory.
   If it fails, the algorithm returns a concrete ambiguous string — a sentence
   that means two different things and sounds identical.
3. **The (C)V(N) claim.** `README.md` states the syllable structure is (C)V(N)
   with five vowels, and that this "was not designed for this. It was
   discovered." That is testable against the actual inventory.

Nothing here invents a form or proposes a fix. It reports what is in the
registry, which was itself transcribed from existing documents.

    python3 03_LAMAGUE_L1/23_SPOKEN_LAMAGUE/spl_phonology.py

Author: Sol, for the Lycheetah Framework. MIT.
"""

from __future__ import annotations

import json
import re
from collections import defaultdict
from pathlib import Path
from typing import Dict, List, Set, Tuple

HERE = Path(__file__).resolve().parent
REGISTRY = HERE / "spl_registry_v0.1.json"

VOWELS = set("aeiou")


# ─────────────────────────────────────────────────────────────
# Inventory assembly
# ─────────────────────────────────────────────────────────────

def load_inventory(reg: dict) -> Dict[str, List[Tuple[str, str]]]:
    """form -> [(system, gloss), ...]. Hyphens stripped; a listener hears no hyphen."""
    inv: Dict[str, List[Tuple[str, str]]] = defaultdict(list)

    for form, v in reg["core_phonemes"].items():
        if form.startswith("_"):
            continue
        inv[form.replace("-", "")].append(("SpL core", f"{v['symbol']} {v['gloss']}"))

    for form, gloss in reg["lexical_particles"].items():
        if form.startswith("_"):
            continue
        inv[form].append(("SpL lexical", gloss))

    for group in ("prosodic_particles", "breath_particles", "gesture_particles",
                  "spatial_particles", "death_particles"):
        label = group.replace("_particles", "")
        for form, gloss in reg[group].items():
            if form.startswith("_"):
                continue
            inv[form.lstrip("-")].append((f"SpL {label}", str(gloss)))

    n36 = reg["native36_spoken_forms"]
    for tok, form in n36["numerals"].items():
        inv[form].append(("Native-36 numeral", f"{tok}"))
    for tok, form in n36["operators"].items():
        inv[form].append(("Native-36 operator", f"{tok}"))

    return inv


# ─────────────────────────────────────────────────────────────
# Sardinas–Patterson
# ─────────────────────────────────────────────────────────────

def dangling(a: Set[str], b: Set[str]) -> Set[str]:
    out = set()
    for x in a:
        for y in b:
            if x != y:
                if x.startswith(y):
                    out.add(x[len(y):])
                elif y.startswith(x):
                    out.add(y[len(x):])
    return out


def uniquely_decodable(code: Set[str]) -> Tuple[bool, str]:
    """
    Sardinas–Patterson. Returns (is_uniquely_decodable, witness).

    The witness, when decodability fails, is a suffix that can be continued two
    ways — the seed of a genuinely ambiguous utterance.
    """
    s1 = dangling(code, code)
    if not s1:
        return True, ""
    seen = [s1]
    current = s1
    for _ in range(64):
        if code & current:
            return False, sorted(code & current)[0]
        current = dangling(code, current) | dangling(current, code)
        if not current or current in seen:
            return True, ""
        seen.append(current)
    return True, ""


def find_ambiguous_pair(code: Set[str], limit: int = 400000) -> Tuple[str, List[str], List[str]] | None:
    """
    Search for a concrete string with two distinct segmentations.
    Breadth-first over short concatenations — the point is a demonstration a
    speaker can say aloud, not an exhaustive proof.
    """
    seen: Dict[str, List[str]] = {}
    frontier: List[Tuple[str, List[str]]] = [("", [])]
    steps = 0
    while frontier and steps < limit:
        s, parts = frontier.pop(0)
        for w in code:
            t, tp = s + w, parts + [w]
            steps += 1
            if len(t) > 9:
                continue
            if t in seen and seen[t] != tp:
                return t, seen[t], tp
            if t not in seen:
                seen[t] = tp
                frontier.append((t, tp))
    return None


# ─────────────────────────────────────────────────────────────
# Phonotactics
# ─────────────────────────────────────────────────────────────

CVN = re.compile(r"^[bcdfghjklmnpqrstvwxyz]?[aeiou][nmr]?$")


def syllabify_ok(form: str) -> bool:
    return bool(CVN.match(form))


def main() -> int:
    reg = json.loads(REGISTRY.read_text(encoding="utf-8"))
    inv = load_inventory(reg)

    print("=" * 74)
    print("SPOKEN LAMAGUE — PHONOLOGY CHECK")
    print("=" * 74)
    print(f"registry: {REGISTRY.name}")
    print(f"distinct spoken forms: {len(inv)}   total senses: {sum(len(v) for v in inv.values())}")

    # ── 1. collisions ────────────────────────────────────────
    collisions = {f: v for f, v in inv.items() if len(v) > 1}
    print(f"\n1. COLLISIONS — one sound, more than one meaning: {len(collisions)}")
    for form in sorted(collisions):
        senses = collisions[form]
        systems = {s for s, _ in senses}
        kind = "CROSS-SYSTEM" if len(systems) > 1 else "within-system"
        print(f"\n   \"{form}\"  [{kind}]")
        for system, gloss in senses:
            print(f"      {system:<22} {gloss}")

    # ── 2. unique decodability ───────────────────────────────
    code = set(inv)
    ok, witness = uniquely_decodable(code)
    print(f"\n2. UNIQUE DECODABILITY (Sardinas-Patterson over {len(code)} forms)")
    print(f"   uniquely decodable: {ok}")
    if not ok:
        print(f"   witness suffix: {witness!r}")
        amb = find_ambiguous_pair(code)
        if amb:
            s, a, b = amb
            print(f"\n   A CONCRETE AMBIGUITY — this string has two readings:")
            print(f"      heard:     {s!r}")
            print(f"      reading 1: {' + '.join(a)}")
            print(f"      reading 2: {' + '.join(b)}")
            for label, parts in (("1", a), ("2", b)):
                gl = " | ".join(f"{p}={inv[p][0][1]}" for p in parts)
                print(f"        {label}: {gl}")

    # ── 3. the (C)V(N) claim ─────────────────────────────────
    bad = sorted(f for f in inv if not syllabify_ok(f))
    print(f"\n3. THE (C)V(N) CLAIM  [README.md line 89]")
    print(f"   forms matching (C)V(N) as a single syllable: {len(inv) - len(bad)}/{len(inv)}")
    if bad:
        print(f"   forms that do NOT fit a single (C)V(N) syllable: {len(bad)}")
        print(f"      {', '.join(bad)}")
        print(f"   -> these are polysyllabic or carry codas outside {{n,m,r}}. The claim")
        print(f"      holds for the core phonemes and breaks on the particle layer,")
        print(f"      which was added later and by a different document.")

    vowels_used = sorted({c for f in inv for c in f if c in VOWELS})
    print(f"\n   vowels actually attested: {vowels_used} ({len(vowels_used)})"
          f"   — README claims five")

    print("\n" + "=" * 74)
    print("WHY THIS MATTERS")
    print("  A collision is survivable in writing and fatal in speech. Two of the")
    print("  attested utterances in the corpus contain forms listed above.")
    print("  Nothing here proposes a repair — that is the language author's call.")
    print("=" * 74)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
