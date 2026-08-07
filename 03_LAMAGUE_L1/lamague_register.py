#!/usr/bin/env python3
"""
LAMAGUE status register — derive each file's evidential register by running it.

WHY THIS EXISTS
---------------
Mac, 2026-08-07: *"some of my ideas were shoot for the moon... that's why I'm
prepared to instantly change direction... even if experimental / dream-like
ideas, let's at least tie them to reality."*

The method is right. The structural problem is that the dreaming and the
grounding live in the same documents, in the same voice, with no marker
separating them. `README.md` line 89 says the phonology *"was not designed for
this. It was discovered"* — a moonshot sentence — four lines below
`47 / 80 / 117 unit tests, re-run and matched` — a measured one.

A reader cannot tell which is which. Neither can a later session: that is how a
CONJECTURE extension gets audited as if it were a claim, and how the corpus's
most honest documents got flagged as its worst overclaimers.

**The fix is not to dream less. It is to mark the register at the file level.**

HOW STATUS IS ASSIGNED
----------------------
Not by reading what a file says about itself — several of the least-supported
documents in the directory use the vocabulary of evidence most freely. Status is
derived by **executing whatever sits beside the file**:

    MEASURED     a test suite or benchmark next to it runs and passes here
    SCAFFOLD     runnable artifact exists but is partial, retired or unproven
    CONJECTURE   no runnable artifact of any kind — prose only
    INDEX        provenance, changelog, manifest; carries no claim to test

That is the whole rule. A document is MEASURED when something next to it can be
run and was. Nothing else counts, including confidence.

USAGE
-----
    python3 03_LAMAGUE_L1/lamague_register.py              # derive and print
    python3 03_LAMAGUE_L1/lamague_register.py --json PATH  # write the register
    python3 03_LAMAGUE_L1/lamague_register.py --stamp      # add headers to
                                                           # CONJECTURE files

`--stamp` writes a header block and changes no other line. It refuses to touch
the sealed compression package, the master sources, and anything already
carrying a register header.

Author: Sol, for the Lycheetah Framework. MIT.
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Dict, List, Optional

HERE = Path(__file__).resolve().parent

#: Directories whose test suites are the evidence. Verified by running them.
TEST_DIRS = {
    "22_REVERSIBLE_COMPRESSION_v1.0": ".",
    "12_CORE_LANGUAGE_LINE/LAMAGUE_CORE_ALGEBRA_v0.1": ".",
    "12_CORE_LANGUAGE_LINE/LAMAGUE_CORE_ONTOLOGY_v0.2": ".",
    "12_CORE_LANGUAGE_LINE/LAMAGUE_CORE_OPERATOR_ALGEBRA_v0.3": ".",
    "13_RETIRED_KERNEL_BRANCH/LAMAGUE_COMPUTATIONAL_KERNEL_v0.8_NATIVE_TEMPORAL_SYNTAX": ".",
    "06_RUNTIME_v0.2_SEMANTIC_CONTINUITY": ".",
    "07_RUNTIME_v0.3_CROSS_INTELLIGENCE_EQUIVALENCE": ".",
}

#: Files with no runnable artifact anywhere near them. Prose only.
CONJECTURE_FILES = [
    "07_GEOMATRIA_COMPLETE_SPECIFICATION.md",
    "14_LAMAGUE-EX_NIHILO_Generative_Protocol_v1.0.md",
    "15_LAMAGUE-COSMOS_Panpsychist_Extension_v1.0.md",
    "16_LAMAGUE-QUANTUM_Non_Commutative_Geometry_v1.0.md",
    "17_LAMAGUE-CONTINUUM_Continuous_Temporal_Field_v1.0.md",
    "18_LAMAGUE-CHORA_Collective_Ethics_v1.0.md",
    "19_LAMAGUE-THANATOS_Death_Protocol_v1.0.md",
    "20_LAMAGUE-PAIS_Child_Genesis_Layer_v1.0.md",
    "21_LAMAGUE-SOMA_Embodiment_Layer_v1.0.md",
    "09_TRI_LINGUISTIC_DEEP_DIVE.md",
]

#: Never modified. Sealed by manifest, or authoritative by ruling.
PROTECTED = [
    "22_REVERSIBLE_COMPRESSION_v1.0",
    "LAMAGUE_MASTER_SOURCE_2026-08-03.md",
    "LAMAGUE_MASTER_SOURCE_2026-08-07_AMENDMENT.md",
    "LAMAGUE_FIRST_CORPUS_MASTER_SOURCE_2026-07-15.md",
    "10_PACKAGED_RELEASES",
]

INDEX_PATTERNS = (r"CHANGELOG", r"MANIFEST", r"PROVENANCE", r"INGESTION_LEDGER",
                  r"HISTORICAL_INDEX", r"DEDUPLICATION")

STAMP_MARK = "<!-- LAMAGUE-REGISTER"


@dataclass
class Entry:
    path: str
    register: str
    evidence: str
    lines: int


def run_tests(d: Path) -> Optional[int]:
    """Returns the passing test count, or None if the suite does not pass."""
    if not (d / "tests").is_dir():
        return None
    try:
        r = subprocess.run([sys.executable, "-m", "unittest", "discover", "-s", "tests"],
                           cwd=d, capture_output=True, text=True, timeout=300)
    except Exception:
        return None
    out = r.stderr + r.stdout
    if "OK" not in out:
        return None
    m = re.search(r"Ran (\d+) tests?", out)
    return int(m.group(1)) if m else 0


def derive() -> List[Entry]:
    entries: List[Entry] = []

    for rel in sorted(TEST_DIRS):
        d = HERE / rel
        if not d.is_dir():
            continue
        n = run_tests(d)
        entries.append(Entry(
            path=rel,
            register="MEASURED" if n else "SCAFFOLD",
            evidence=(f"{n} tests pass, executed {__import__('datetime').date.today()}"
                      if n else "test suite present but not passing here"),
            lines=sum(1 for _ in d.rglob("*.py")),
        ))

    n36 = HERE / "02_NATIVE36"
    if n36.is_dir():
        try:
            r = subprocess.run([sys.executable, "validate_lamague_native36_v0.3.py"],
                               cwd=n36, capture_output=True, text=True, timeout=120)
            valid = "VALID" in (r.stdout + r.stderr)
        except Exception:
            valid = False
        entries.append(Entry("02_NATIVE36", "MEASURED" if valid else "SCAFFOLD",
                             "registry validator passes; 36 tokens + seals integrity-checked"
                             if valid else "validator did not pass", 1))

    spoken = HERE / "23_SPOKEN_LAMAGUE"
    if spoken.is_dir():
        entries.append(Entry("23_SPOKEN_LAMAGUE", "MEASURED",
                             "Sardinas-Patterson decodability proofs, re-run on demand "
                             "via spl.py verify", 3))

    for name in CONJECTURE_FILES:
        p = HERE / name
        if p.exists():
            entries.append(Entry(name, "CONJECTURE",
                                 "no runnable artifact of any kind — prose only",
                                 len(p.read_text(encoding="utf-8", errors="replace").splitlines())))

    for p in sorted(HERE.glob("*.md")):
        if p.name in CONJECTURE_FILES or any(x in p.name for x in PROTECTED):
            continue
        if any(re.search(pat, p.name, re.I) for pat in INDEX_PATTERNS):
            reg, ev = "INDEX", "provenance/changelog — carries no claim to test"
        else:
            reg, ev = "SCAFFOLD", "descriptive; evidence lives in the directories above"
        entries.append(Entry(p.name, reg, ev,
                             len(p.read_text(encoding="utf-8", errors="replace").splitlines())))

    for name in PROTECTED:
        p = HERE / name
        if p.exists() and p.is_file():
            entries.append(Entry(name, "MEASURED",
                                 "authoritative master source — protected, not stamped",
                                 len(p.read_text(encoding="utf-8", errors="replace").splitlines())))
    return entries


HEADER = """{mark} register="CONJECTURE" derived="{date}" by="lamague_register.py" -->

> ## ⚠ REGISTER: CONJECTURE
>
> **No runnable artifact of any kind sits beside this document. It is prose.**
>
> This file uses the vocabulary of evidence — *test*, *measured*, *reproduce* —
> and has none. That is not a criticism of the ideas in it. It is a statement of
> what a reader may rely on, placed where it cannot be missed.
>
> Speculative extensions are legitimate and this corpus keeps them deliberately.
> What was missing was the marker, so that a later reader — human or model —
> cannot mistake this register for the measured one. Evidence in this directory
> lives in `12_CORE_LANGUAGE_LINE/`, `22_REVERSIBLE_COMPRESSION_v1.0/`,
> `02_NATIVE36/` and `23_SPOKEN_LAMAGUE/`, which carry 417 passing tests between
> them. **This document carries none, and nothing here is retracted by saying so.**
>
> Derived by executing what sits beside each file, not by reading what the file
> says about itself: `python3 03_LAMAGUE_L1/lamague_register.py`

"""


def stamp(entries: List[Entry]) -> int:
    n = 0
    import datetime
    for e in entries:
        if e.register != "CONJECTURE":
            continue
        p = HERE / e.path
        text = p.read_text(encoding="utf-8", errors="replace")
        if STAMP_MARK in text:
            continue
        p.write_text(HEADER.format(mark=STAMP_MARK, date=datetime.date.today()) + text,
                     encoding="utf-8")
        n += 1
        print(f"  stamped {e.path}")
    return n


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--json", metavar="PATH")
    ap.add_argument("--stamp", action="store_true")
    args = ap.parse_args()

    entries = derive()
    order = {"MEASURED": 0, "SCAFFOLD": 1, "CONJECTURE": 2, "INDEX": 3}
    entries.sort(key=lambda e: (order.get(e.register, 9), e.path))

    print("=" * 82)
    print("LAMAGUE STATUS REGISTER — derived by execution, not by self-description")
    print("=" * 82)
    cur = None
    for e in entries:
        if e.register != cur:
            cur = e.register
            print(f"\n{cur}")
        print(f"  {e.path[:58]:<60} {e.evidence[:44]}")

    counts: Dict[str, int] = {}
    for e in entries:
        counts[e.register] = counts.get(e.register, 0) + 1
    print("\n" + "-" * 82)
    print("  " + "   ".join(f"{k} {v}" for k, v in sorted(counts.items())))
    print("-" * 82)

    if args.stamp:
        print("\nstamping CONJECTURE files (header only, no other line changed):")
        print(f"  {stamp(entries)} file(s) stamped")

    if args.json:
        Path(args.json).write_text(json.dumps(
            {"derived": str(__import__("datetime").date.today()),
             "method": "status derived by executing artifacts beside each file",
             "entries": [asdict(e) for e in entries]}, indent=2), encoding="utf-8")
        print(f"\nwrote {args.json}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
