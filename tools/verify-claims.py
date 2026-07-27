#!/usr/bin/env python3
"""
⊚ DOES EVERY CLAIM-BEARING DOCUMENT SAY HOW MUCH IT KNOWS?

    python3 tools/verify-claims.py            # full report
    python3 tools/verify-claims.py --quiet    # CI-shaped: baseline check only

Built 2026-07-27, after a sweep found the framework's epistemic discipline was real
but *fragmented*: a 56 KB falsification register, an empirical inventory classifying
every load-bearing claim, and a prior-art document — expressed in FOUR different
marking vocabularies, so nothing could audit the whole corpus in one pass. Including
the audit itself, which grepped one vocabulary, found 12 hits, and nearly concluded
the work was unrigorous. It was the instrument that was wrong.

So this gate credits EVERY vocabulary in use. It is not here to make the corpus write
in one dialect; it is here to make sure a document that argues something says how well
it knows it.

WHAT IT IS NOT: a truth detector. It cannot tell whether a claim is right. It checks
only that a claim-bearing document declares its footing somewhere. A marked document
can still be wrong — it just cannot be silently wrong.
"""

import os, re, sys, subprocess
from collections import Counter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
QUIET = "--quiet" in sys.argv

# Documents that ARGUE. Reference material, indexes and session logs are exempt: a map
# makes no claim, and holding it to one would be theatre.
CLAIM_BEARING = (
    "papers/", "docs/", "28_DEFENSE/", "29_GOVERNANCE/",
    "11_MATHEMATICAL_FOUNDATIONS/", "23_NZ_AI_GOVERNANCE/",
    "24_LAMAGUE_CROSS_CULTURAL/", "31_EMPIRICAL/", "32_TIANXIA/",
)
EXEMPT_DIRS = ("99_ARCHIVE/", "_PROPRIETARY/", "000_1404RawSourceTranslate/")
MIN_BYTES = 3000            # below this it is a note, not an argument

# Every marking vocabulary actually in use in this corpus. Adding a fifth is allowed;
# leaving a document unmarked is what this gate exists to catch.
VOCABULARIES = {
    "governance (EMPIRICAL/FORMAL/…)":
        r"\[?\b(EMPIRICAL|FORMAL|OBSERVATIONAL|ASPIRATIONAL|REMOVED|FALSIFIED|SPECULATIVE)\b\]?",
    "sol registers (MEASURED/CONJECTURE/…)":
        r"\b(MEASURED|DERIVED|CONJECTURE|ASSUMED|INTERPRETIVE|UNVERIFIED|SCAFFOLD|RETRACTED)\b",
    "promotion states (FOUNDATION/EDGE)":
        r"\b(FOUNDATION|EDGE)\b",
    "inline proposal marks":
        r"\[(PROPOSAL|PROPOSED|DRAFT|UNVERIFIED|CONJECTURE)\]",
}
COMPILED = {k: re.compile(v) for k, v in VOCABULARIES.items()}

# The count of unmarked claim-bearing documents on the day this gate was written.
# It exists so the gate blocks REGRESSION today instead of staying red forever.
# Lower it whenever the real number drops. Never raise it.
BASELINE = 31   # 2026-07-27: the maths bridge classified [OBSERVATIONAL/ASPIRATIONAL]. Never raise this.


def tracked_markdown():
    """Tracked files AND new untracked ones — but never ignored ones.

    ⚠ `git ls-files` alone sees only TRACKED files, so a brand-new document is
    invisible to it. The first version of this gate had exactly that hole, and the
    regression test written to prove the gate worked passed against a new unmarked
    file — proving nothing. `--others --exclude-standard` adds untracked files while
    still respecting .gitignore, so `_PROPRIETARY/` stays out.
    """
    out = subprocess.run(
        ["git", "-c", "core.quotePath=false", "ls-files", "-z",
         "--cached", "--others", "--exclude-standard", "*.md"],
        cwd=ROOT, capture_output=True, text=True).stdout
    return sorted({f for f in out.split("\0") if f})


def main():
    files = tracked_markdown()
    if not files:
        print("verify-claims: no tracked markdown found — is this a git repo?")
        return 2

    marked, unmarked, exempt_small, per_vocab = [], [], 0, Counter()

    for f in files:
        if f.startswith(EXEMPT_DIRS):
            continue
        if not f.startswith(CLAIM_BEARING):
            continue
        path = os.path.join(ROOT, f)
        try:
            size = os.path.getsize(path)
            text = open(path, encoding="utf-8", errors="ignore").read()
        except OSError:
            continue
        if size < MIN_BYTES:
            exempt_small += 1
            continue
        hits = [name for name, rx in COMPILED.items() if rx.search(text)]
        if hits:
            marked.append(f)
            per_vocab.update(hits)
        else:
            unmarked.append((size, f))

    total = len(marked) + len(unmarked)
    unmarked.sort(reverse=True)

    if not QUIET:
        print(f"\n\033[36m⊚ CLAIM-BEARING DOCUMENTS\033[0m  "
              f"\033[2m{total} argued documents ≥{MIN_BYTES//1000}KB "
              f"({exempt_small} shorter ones exempt)\033[0m\n")
        for name in VOCABULARIES:
            print(f"  \033[2m{per_vocab.get(name, 0):4d}  {name}\033[0m")
        pct = 100 * len(marked) // total if total else 100
        print(f"\n  \033[32m●\033[0m marked   {len(marked):4d}  ({pct}%)")
        print(f"  \033[33m●\033[0m UNMARKED {len(unmarked):4d}\n")
        if unmarked:
            print("  \033[33mdocuments that argue and never say how well they know:\033[0m")
            for size, f in unmarked[:20]:
                print(f"    \033[2m{size//1024:4d} KB\033[0m  {f}")
            if len(unmarked) > 20:
                print(f"    \033[2m… and {len(unmarked)-20} more\033[0m")

    base = BASELINE if BASELINE is not None else len(unmarked)
    if len(unmarked) > base:
        print(f"\n\033[31m✗ REGRESSION\033[0m — {len(unmarked)} unmarked, baseline {base}. "
              f"A new document argues without declaring its footing.\n")
        return 1
    if len(unmarked) < base:
        print(f"\n\033[32m✓ IMPROVED\033[0m — {len(unmarked)} unmarked, baseline was {base}. "
              f"Lower BASELINE in this file to lock it in.\n")
        return 0
    print(f"\n\033[32m✓ HOLDING\033[0m — {len(unmarked)} unmarked, at baseline. "
          f"No new document argues without saying how well it knows.\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
