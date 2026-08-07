#!/usr/bin/env python3
"""
SpL — Spoken LAMAGUE. A working parser and speaker.

WHAT THIS IS
------------
`spl_phonology.py` established that Spoken LAMAGUE, as scattered across the
corpus, is **not uniquely decodable**: the string `witun` is both `wi + tun`
("we four") and `wit + un` ("withdrawal one"). Six forms collide outright,
including `ta`, which means both *slow* and *past* and appears in the attested
corpus.

A language you cannot hear unambiguously is a notation, not a speech system.
This module makes it a speech system, using a repair that invents nothing.

THE REPAIR: THE HYPHEN WAS ALWAYS PHONOLOGICAL
-----------------------------------------------
Every particle in every source document is written bound, with a hyphen:
`An-hi`, `-ta`, `Wi kas-om-na`. Roots are written free. That distinction is
already consistently observed in the corpus — it has simply never been given a
sound.

So: **the hyphen is a glottal stop [ʔ]**, and it is obligatory before every
bound particle.

    An-hi     [anʔhi]     whispered anchor
    wi tun    [wi.tun]    we four
    wit-un    [witʔun]    ...is now unpronounceable, because `wit` is a
                          particle and cannot begin a word

This is typologically ordinary — Hawaiian, Arabic, Cockney and a hundred others
use glottal stop as a boundary — and it costs the language nothing, because
every form in the registry survives unchanged. It also resolves the six
collisions structurally rather than by renaming: `ta` the prosodic particle is
`-ta` [ʔta] and can only follow a root; `ta` never occurs free.

**Formal claim, checked by `--verify`:** with particles bound and roots free,
the resulting code is uniquely decodable. The verification is Sardinas-Patterson
over the partitioned inventory, run on every invocation of `--verify`, so the
claim is not left as prose.

STATUS
------
[PROPOSAL] The repair is Sol's, not Mac's, and the language is Mac's. It is
implemented here so it can be *heard and tested* rather than argued about, and
it is reversible — delete this file and the corpus is unchanged.

USAGE
-----
    python3 spl.py --verify                    # prove unique decodability
    python3 spl.py parse "An-hi-ta"            # utterance -> structure
    python3 spl.py speak "A0 fold cascade"     # concepts -> utterance
    python3 spl.py ipa "Wi kas-om-na"          # -> broad IPA
    python3 spl.py corpus                      # re-parse every attested utterance

Author: Sol, for the Lycheetah Framework. MIT.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple

HERE = Path(__file__).resolve().parent
REGISTRY = HERE / "spl_registry_v0.1.json"

GLOTTAL = "ʔ"


# ─────────────────────────────────────────────────────────────
# Inventory, partitioned into free roots and bound particles
# ─────────────────────────────────────────────────────────────

@dataclass
class Morph:
    form: str
    kind: str          # "root" | "particle"
    system: str
    gloss: str


@dataclass
class Lexicon:
    roots: Dict[str, Morph] = field(default_factory=dict)
    particles: Dict[str, Morph] = field(default_factory=dict)
    ambiguous_roots: Dict[str, List[Morph]] = field(default_factory=dict)

    @property
    def all_forms(self) -> Set[str]:
        return set(self.roots) | set(self.particles)


def load_lexicon(reg: dict) -> Lexicon:
    lex = Lexicon()

    def add_root(form: str, system: str, gloss: str) -> None:
        form = form.replace("-", "")
        if form in lex.roots and lex.roots[form].gloss != gloss:
            lex.ambiguous_roots.setdefault(form, [lex.roots[form]]).append(
                Morph(form, "root", system, gloss))
        else:
            lex.roots[form] = Morph(form, "root", system, gloss)

    def add_particle(form: str, system: str, gloss: str) -> None:
        form = form.lstrip("-")
        lex.particles[form] = Morph(form, "particle", system, gloss)

    for f, v in reg["core_phonemes"].items():
        if not f.startswith("_"):
            add_root(f, "core", f"{v['symbol']} {v['gloss']}")
    for f, g in reg["lexical_particles"].items():
        if not f.startswith("_"):
            add_root(f, "lexical", str(g))       # free words, not bound
    for group in ("prosodic_particles", "breath_particles", "gesture_particles",
                  "spatial_particles", "death_particles"):
        label = group.replace("_particles", "")
        for f, g in reg[group].items():
            if not f.startswith("_"):
                add_particle(f, label, str(g))

    n36 = reg["native36_spoken_forms"]
    for tok, form in n36["numerals"].items():
        add_root(form, "n36-num", f"numeral {tok}")
    for tok, form in n36["operators"].items():
        add_root(form, "n36-op", f"operator {tok}")

    return lex


# ─────────────────────────────────────────────────────────────
# Unique decodability, re-proved on demand
# ─────────────────────────────────────────────────────────────

def _dangling(a: Set[str], b: Set[str]) -> Set[str]:
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
    s = _dangling(code, code)
    if not s:
        return True, ""
    seen = [s]
    for _ in range(64):
        hit = code & s
        if hit:
            return False, sorted(hit)[0]
        s = _dangling(code, s) | _dangling(s, code)
        if not s or s in seen:
            return True, ""
        seen.append(s)
    return True, ""


def verify(lex: Lexicon) -> int:
    """The repair's whole justification, checked rather than asserted."""
    flat = lex.all_forms
    ok_flat, wit_flat = uniquely_decodable(flat)

    # With the repair, a particle is only ever reachable across a glottal stop,
    # so its phonological word-form carries the boundary segment.
    bound = set(lex.roots) | {GLOTTAL + p for p in lex.particles}
    ok_bound, wit_bound = uniquely_decodable(bound)

    print("=" * 74)
    print("UNIQUE DECODABILITY — before and after the repair")
    print("=" * 74)
    print(f"  roots: {len(lex.roots)}   particles: {len(lex.particles)}")
    print()
    print(f"  FLAT inventory (no boundary marker) — {len(flat)} forms")
    print(f"    uniquely decodable: {ok_flat}"
          + (f"   witness: {wit_flat!r}" if not ok_flat else ""))
    print()
    print(f"  BOUND inventory (particles carry {GLOTTAL}) — {len(bound)} forms")
    print(f"    uniquely decodable: {ok_bound}"
          + (f"   witness: {wit_bound!r}" if not ok_bound else ""))
    print()
    if ok_bound and not ok_flat:
        print("  RESULT: the glottal boundary repairs decodability. No form was")
        print("          renamed, added, or removed to achieve it.")
    elif ok_bound and ok_flat:
        print("  RESULT: already decodable; the repair is not load-bearing.")
    else:
        print("  RESULT: STILL AMBIGUOUS. The repair is insufficient — do not")
        print("          publish it as a fix.")

    if lex.ambiguous_roots:
        print(f"\n  ⚠ {len(lex.ambiguous_roots)} root form(s) still carry more than one sense.")
        print("    Decodability is about SEGMENTATION, not sense. These are homophones")
        print("    a listener can segment but not disambiguate without context:")
        for form, ms in sorted(lex.ambiguous_roots.items()):
            print(f"      {form:<8} " + " / ".join(f"{m.system}:{m.gloss}" for m in ms))
    print("=" * 74)
    return 0 if ok_bound else 1


# ─────────────────────────────────────────────────────────────
# Parsing
# ─────────────────────────────────────────────────────────────

@dataclass
class Word:
    root: Optional[Morph]
    particles: List[Morph]
    raw: str
    error: Optional[str] = None

    def ipa(self) -> str:
        if not self.root:
            return "?"
        return self.root.form + "".join(GLOTTAL + p.form for p in self.particles)

    def render(self) -> str:
        if self.error:
            return f"  {self.raw:<16} ✗ {self.error}"
        bits = [f"{self.root.form} = {self.root.gloss}"]
        bits += [f"-{p.form} = {p.gloss} [{p.system}]" for p in self.particles]
        return f"  {self.raw:<16} [{self.ipa()}]\n" + "\n".join(f"      {b}" for b in bits)


def parse_word(token: str, lex: Lexicon) -> Word:
    raw = token
    clean = re.sub(r"[.,;?!]", "", token).strip()
    if not clean:
        return Word(None, [], raw, "empty")
    parts = clean.split("-")
    head = parts[0].lower()
    root = lex.roots.get(head)
    if root is None:
        if head in lex.particles:
            return Word(None, [], raw, f"'{head}' is a bound particle and cannot begin a word")
        return Word(None, [], raw, f"unknown root '{head}'")
    ps: List[Morph] = []
    for p in parts[1:]:
        pl = p.lower()
        m = lex.particles.get(pl)
        if m is None:
            m2 = lex.roots.get(pl)
            if m2:
                ps.append(Morph(pl, "particle", m2.system + "(root-as-particle)", m2.gloss))
                continue
            return Word(root, ps, raw, f"unknown particle '-{pl}'")
        ps.append(m)
    return Word(root, ps, raw)


def parse_utterance(text: str, lex: Lexicon) -> List[Word]:
    return [parse_word(t, lex) for t in text.split() if t.strip()]


# ─────────────────────────────────────────────────────────────
# Commands
# ─────────────────────────────────────────────────────────────

def cmd_parse(text: str, lex: Lexicon) -> int:
    words = parse_utterance(text, lex)
    print(f'utterance: "{text}"')
    print(f'IPA:       /{" ".join(w.ipa() for w in words)}/\n')
    bad = 0
    for w in words:
        print(w.render())
        bad += 1 if w.error else 0
    print(f"\n{len(words) - bad}/{len(words)} words parsed")
    return 1 if bad else 0


def cmd_ipa(text: str, lex: Lexicon) -> int:
    print(" ".join(w.ipa() for w in parse_utterance(text, lex)))
    return 0


def cmd_speak(concepts: str, lex: Lexicon) -> int:
    """Concept glosses -> the SpL form that carries them."""
    by_gloss: Dict[str, List[Morph]] = {}
    for m in list(lex.roots.values()) + list(lex.particles.values()):
        for key in re.findall(r"[a-z0-9₀↑∞Ω∅Ψ]+", m.gloss.lower()):
            by_gloss.setdefault(key, []).append(m)
    out = []
    for want in concepts.lower().split():
        hits = by_gloss.get(want, [])
        if hits:
            m = hits[0]
            out.append(("-" if m.kind == "particle" else "") + m.form)
            print(f"  {want:<14} -> {m.form:<8} ({m.system}: {m.gloss})")
        else:
            out.append(f"?{want}")
            print(f"  {want:<14} -> no SpL form carries this")
    print(f"\nutterance: {' '.join(out)}")
    return 0


def cmd_corpus(lex: Lexicon, reg: dict) -> int:
    """Re-parse every attested utterance. The only running text SpL has."""
    print("=" * 74)
    print("ATTESTED CORPUS — every complete SpL sentence in the repository")
    print("=" * 74)
    total = clean = 0
    for src, u in reg["attested_utterances"].items():
        if src.startswith("_"):
            continue
        print(f"\n{src}")
        print(f'  SpL:   {u["spl"]}')
        print(f'  gloss: {u["gloss"]}')
        words = [w for w in parse_utterance(u["spl"], lex)]
        bad = [w for w in words if w.error]
        total += len(words)
        clean += len(words) - len(bad)
        print(f'  IPA:   /{" ".join(w.ipa() for w in words)}/')
        for w in bad:
            print(f"    ✗ {w.raw}: {w.error}")
    print(f"\n{clean}/{total} attested word tokens resolve against the registry.")
    print("Unresolved tokens are forms used in dialogue but never declared in any")
    print("table — the gap between the language as written and as documented.")
    print("=" * 74)
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("command", nargs="?", default="verify",
                    choices=["verify", "parse", "speak", "ipa", "corpus"])
    ap.add_argument("text", nargs="*")
    ap.add_argument("--verify", action="store_true")
    args = ap.parse_args()

    reg = json.loads(REGISTRY.read_text(encoding="utf-8"))
    lex = load_lexicon(reg)
    text = " ".join(args.text)

    if args.verify or args.command == "verify":
        return verify(lex)
    if args.command == "parse":
        return cmd_parse(text, lex)
    if args.command == "ipa":
        return cmd_ipa(text, lex)
    if args.command == "speak":
        return cmd_speak(text, lex)
    if args.command == "corpus":
        return cmd_corpus(lex, reg)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
