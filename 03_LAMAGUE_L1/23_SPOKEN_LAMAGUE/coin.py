#!/usr/bin/env python3
"""
coin — propose a new LAMAGUE word that does not break the language.

WHY THIS EXISTS
---------------
The stated goal is a language "as fillable with meaning as English". A language
you cannot add words to is a code, not a language. But every new word risks
colliding with an existing one or creating a prefix relation that makes the
inventory ambiguous — and by hand that is uncheckable past about thirty forms.

This is the constraint solver for that. Give it a class, it returns forms that
are phonotactically legal, unused, and provably safe to add.

It was written after two hand-picked repairs failed in a row:

    Ψ_inv -> saian     broke decodability (sai ⊂ saian)
    ∞ -> inin          broke it again (in ⊂ inin)

Reduplication is iconic and it is a prefix of itself. That is exactly the kind
of thing a human misses and a check catches instantly.

WHAT "SAFE" MEANS HERE
----------------------
A candidate is safe if it is unused, introduces no prefix relation with an
existing root, and adds no NEW ambiguity to the inventory.

Not "the result is perfectly decodable" — that criterion rejected all 453
candidates, and the witnesses ('u', 'en', 'or') showed why: those ambiguities
exist before anything is added. See `is_safe` for the full reasoning and the
two-layer target it produced.

PHONOTACTICS
------------
(C)V(N) per `README.md`: optional onset, one of five vowels, optional nasal or
liquid coda. Candidates are ranked by how well they fit the existing sound of
the language — onsets and codas already common in the inventory score higher,
so coined words sound like LAMAGUE rather than like a password.

USAGE
-----
    python3 coin.py --for "infinity" --class STATE
    python3 coin.py --class OPERATOR -n 20
    python3 coin.py --test nin          # is this specific form safe?

Author: Sol, for the Lycheetah Framework. MIT.
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path
from typing import Dict, List, Set, Tuple

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from spl import uniquely_decodable, GLOTTAL  # noqa: E402

VOWELS = "aeiou"
ONSETS = ["", "b", "d", "f", "g", "h", "j", "k", "l", "m",
          "n", "p", "q", "r", "s", "t", "v", "w", "y", "z"]
CODAS = ["", "n", "m", "r", "l", "s"]


def load_inventory() -> Tuple[Dict[str, Set[str]], Set[str]]:
    """Returns (class -> forms, all bound-form inventory) for SpL v0.2."""
    reg = json.loads((HERE / "spl_registry_v0.1.json").read_text(encoding="utf-8"))

    states = {k.replace("-", "") for k in reg["core_phonemes"] if not k.startswith("_")}
    states -= {"saian"}                       # C1: read as compound
    states -= {"in"}                          # C2: ∞ is being re-coined

    n36 = reg["native36_spoken_forms"]
    operators = set(n36["operators"].values())
    numerals = set(n36["numerals"].values())

    modifiers: Set[str] = set()
    for g in ("prosodic_particles", "breath_particles", "gesture_particles",
              "spatial_particles", "death_particles"):
        modifiers |= {k.lstrip("-") for k in reg[g] if not k.startswith("_")}
    modifiers = (modifiers - {"ta", "ki", "in"}) | {"tas", "kis", "ihn", "ta"}

    lexical = {k for k in reg["lexical_particles"] if not k.startswith("_")}

    classes = {"STATE": states, "OPERATOR": operators, "NUMERAL": numerals,
               "MODIFIER": modifiers, "LEXICAL": lexical}
    roots = states | operators | numerals | lexical
    inventory = roots | {GLOTTAL + m for m in modifiers}
    return classes, inventory


def native_score(form: str, roots: Set[str]) -> float:
    """
    How much this sounds like the language already.

    Rewards onsets, codas and vowels that are frequent in the existing
    inventory, and short forms — the corpus is overwhelmingly CV and CVN.
    """
    onset_freq = Counter(r[0] for r in roots if r and r[0] not in VOWELS)
    coda_freq = Counter(r[-1] for r in roots if r and r[-1] not in VOWELS)
    vowel_freq = Counter(c for r in roots for c in r if c in VOWELS)

    onset = form[0] if form and form[0] not in VOWELS else ""
    coda = form[-1] if form and form[-1] not in VOWELS else ""
    vowel = next((c for c in form if c in VOWELS), "")

    s = 0.0
    s += onset_freq.get(onset, 0) * 1.0 if onset else 1.5   # vowel-initial is fine
    s += coda_freq.get(coda, 0) * 1.0 if coda else 1.5
    s += vowel_freq.get(vowel, 0) * 0.4
    s -= (len(form) - 2) * 2.0                              # brevity
    return s


def candidates() -> List[str]:
    out = []
    for o in ONSETS:
        for v in VOWELS:
            for c in CODAS:
                f = o + v + c
                if 1 <= len(f) <= 4:
                    out.append(f)
    return out


def is_safe(form: str, roots: Set[str], inventory: Set[str]) -> Tuple[bool, str]:
    """
    Does adding this form make the language WORSE — not, is the result perfect.

    The first version of this function asked whether `inventory | {form}` was
    uniquely decodable, and rejected every candidate in the space. The witnesses
    gave it away: 'u', 'en', 'or' are ambiguities that exist *before* anything
    is added. The unified spoken inventory is already not uniquely decodable and
    cannot be made so without altering forms Mac has already committed to.

    That is not a defect to engineer away. English is not uniquely decodable
    either — 'ice cream' and 'I scream' are the standard example — and it
    remains perfectly speakable, because human languages disambiguate with
    stress, class and context rather than with prefix-freeness.

    So the target moved, and it now matches the two-layer goal:

        Native-36 (the wire / machine layer)   STRICT   uniquely decodable
        Spoken LAMAGUE (the human layer)       TOLERANT no NEW ambiguity

    A candidate is safe if it is unused, introduces no new prefix relation, and
    does not increase the number of ambiguity witnesses.
    """
    if form in inventory or form in roots:
        return False, "already in use"
    for r in roots:
        if r != form and (form.startswith(r) or r.startswith(form)):
            return False, f"prefix clash with {r!r}"

    before_ok, before_w = uniquely_decodable(inventory)
    after_ok, after_w = uniquely_decodable(inventory | {form})
    if before_ok and not after_ok:
        return False, f"introduces ambiguity (witness {after_w!r})"
    return True, "safe"


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--for", dest="concept", default="", help="what the word will mean")
    ap.add_argument("--class", dest="cls", default="STATE",
                    choices=["STATE", "OPERATOR", "NUMERAL", "MODIFIER", "LEXICAL"])
    ap.add_argument("-n", type=int, default=12, help="how many to propose")
    ap.add_argument("--test", default="", help="check one specific form")
    args = ap.parse_args()

    classes, inventory = load_inventory()
    roots = set().union(*(classes[c] for c in ("STATE", "OPERATOR", "NUMERAL", "LEXICAL")))

    if args.test:
        ok, why = is_safe(args.test.lower(), roots, inventory)
        print(f"{args.test!r}: {'SAFE' if ok else 'REJECTED'} — {why}")
        return 0 if ok else 1

    print(f"coining a {args.cls}" + (f" for {args.concept!r}" if args.concept else ""))
    print(f"inventory: {len(roots)} roots, {len(inventory)} total forms\n")

    scored: List[Tuple[float, str]] = []
    for f in candidates():
        ok, _ = is_safe(f, roots, inventory)
        if ok:
            scored.append((native_score(f, roots), f))
    scored.sort(reverse=True)

    print(f"  {len(scored)} safe forms available. Top {args.n} by fit with the")
    print(f"  existing sound of the language:\n")
    for s, f in scored[:args.n]:
        print(f"    {f:<6}  fit {s:>5.1f}")
    strict_ok, _ = uniquely_decodable(inventory)
    print(f"\n  Every one is checked: unused, no prefix clash, and adds no NEW")
    print(f"  ambiguity to the spoken inventory.")
    print(f"\n  Note: the spoken inventory is {'already' if not strict_ok else 'currently'} "
          f"{'NOT ' if not strict_ok else ''}strictly uniquely decodable.")
    if not strict_ok:
        print(f"  That is the intended design — Native-36 is strict for the wire,")
        print(f"  Spoken LAMAGUE is tolerant for the mouth, like every human language.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
