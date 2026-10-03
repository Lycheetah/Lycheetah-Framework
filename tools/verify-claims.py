#!/usr/bin/env python3
"""
⊚ DOES EVERY CLAIM-BEARING DOCUMENT SAY HOW MUCH IT KNOWS?

    python3 tools/verify-claims.py            # full report
    python3 tools/verify-claims.py --quiet    # CI-shaped: baseline check only
    python3 tools/verify-claims.py --register # do the claim counts agree everywhere?

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

import json, os, re, sys, subprocess
from collections import Counter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
QUIET = "--quiet" in sys.argv

# Documents that ARGUE. Reference material, indexes and session logs are exempt: a map
# makes no claim, and holding it to one would be theatre.
CLAIM_BEARING = (
    "papers/", "docs/", "28_DEFENSE/", "29_GOVERNANCE/",
    "11_MATHEMATICAL_FOUNDATIONS/", "23_NZ_AI_GOVERNANCE/",
    "24_LAMAGUE_CROSS_CULTURAL/", "31_EMPIRICAL/", "32_TIANXIA/", "34_CYBERNETICS/",
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
    # ⚠ Added 2026-07-27 after the gate flagged MASTER_EQUATION_CALIBRATION.md — the
    # single most rigorous document found in the corpus. It retracts its own earlier
    # mislabelling, states "the k1-k4 coupling constants are still uncalibrated" and
    # "STATUS: NOT YET COLLECTED", and distinguishes what its data shows from what it
    # does not. It failed only because it invented its own honest marker. A gate that
    # penalises the most careful document in the corpus is measuring conformity, not
    # honesty — so the gate changed, not the document.
    "self-correction / status marks":
        r"(\[MISLABELED|\[CORRECTED|\[RETRACTED|NOT YET COLLECTED|"
        r"does NOT show|still uncalibrated|\bSTATUS:\s*NOT\b)",
}
COMPILED = {k: re.compile(v) for k, v in VOCABULARIES.items()}

# The count of unmarked claim-bearing documents on the day this gate was written.
# It exists so the gate blocks REGRESSION today instead of staying red forever.
# Lower it whenever the real number drops. Never raise it.
BASELINE = 30   # 2026-07-27: gate taught to credit self-correction marks. Never raise this.


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


# ── THE REGISTER AND ITS MIRRORS ─────────────────────────────────────────────────────
# Added 2026-10-03, after an outside reader running an AI-assisted review found three
# different claim totals within a few clicks: the README said 60, CLAIMS.json's own
# `total_claims` field said 136, and its `claims` array held 67 records. The gate above
# asks whether a document declares its footing; it could not see this, because every
# one of those documents was marked. A count can be honestly labelled and still wrong.
#
# One truth: the `claims` array. Every surface that repeats a count is a mirror, and
# every mirror is pinned here by the phrase that carries the number. A pinned phrase
# that disappears is itself a failure: the text moved, so the pin must move with it.
# "%STATUS" pins a rounded percentage of the total.
CLAIMS_PATH = "28_DEFENSE/CLAIMS.json"
META_PATH = "ai-meta.json"
STATUSES = ("ACTIVE", "SCAFFOLD", "CONJECTURE", "RETRACTED")
EITHER = r"(?:load-bearing claims|claim records)"
MIRRORS = {
    "README.md": [
        (r"contains (\d+) structured claim records", ("total",)),
        (r"The register holds (\d+) claim records", ("total",)),
        (r"\| \*\*ACTIVE\*\* \| (\d+) \|", ("ACTIVE",)),
        (r"\| \*\*SCAFFOLD\*\* \| (\d+) \|", ("SCAFFOLD",)),
        (r"\| \*\*CONJECTURE\*\* \| (\d+) \|", ("CONJECTURE",)),
        (r"\| \*\*RETRACTED\*\* \| (\d+) \|", ("RETRACTED",)),
    ],
    "llms.txt": [
        (r"Total: (\d+) " + EITHER + r" \((\d+) ACTIVE, (\d+) SCAFFOLD, (\d+) CONJECTURE, "
         r"(\d+) RETRACTED", ("total",) + STATUSES),
        (r"All (\d+) " + EITHER, ("total",)),
    ],
    "FIVE_MINUTE_BRIEF.md": [
        (r"register of all (\d+) status-tagged claim records", ("total",)),
    ],
}


def check_register(root=ROOT):
    """Return (truth, errors): the counts the register holds, and every disagreement."""
    def read(rel):
        with open(os.path.join(root, rel), encoding="utf-8") as fh:
            return fh.read()

    register = json.loads(read(CLAIMS_PATH))
    claims = register["claims"]
    truth = Counter(c["status_normalized"] for c in claims)
    errors = [f"{CLAIMS_PATH}: {c['claim_id']} has status_normalized "
              f"{c['status_normalized']!r}, outside {STATUSES}"
              for c in claims if c["status_normalized"] not in STATUSES]
    truth["total"] = len(claims)
    for s in STATUSES:
        truth["%" + s] = round(100 * truth[s] / len(claims))

    if register.get("total_claims") != len(claims):
        errors.append(f"{CLAIMS_PATH}: total_claims = {register.get('total_claims')}, "
                      f"but the file holds {len(claims)} records")

    pinned = 0
    for rel, pins in MIRRORS.items():
        text = read(rel)
        for pattern, keys in pins:
            matches = list(re.finditer(pattern, text))
            if not matches:
                errors.append(f"{rel}: pinned phrase not found /{pattern}/ — "
                              f"the text moved; move the pin with it")
            for m in matches:
                pinned += 1
                line = text.count("\n", 0, m.start()) + 1
                for key, value in zip(keys, m.groups()):
                    if int(value) != truth[key]:
                        errors.append(f"{rel}:{line}: says {value} for {key}, "
                                      f"the register holds {truth[key]}")

    meta = json.loads(read(META_PATH))
    summary = meta.get("claim_summary", {})
    for key in ("total",) + STATUSES:
        pinned += 1
        if summary.get(key) != truth[key]:
            errors.append(f"{META_PATH}: claim_summary.{key} = {summary.get(key)}, "
                          f"the register holds {truth[key]}")
    by_framework = Counter(c["framework"] for c in claims)
    for fw in meta.get("frameworks", []):
        pinned += 1
        key = fw["name"].replace(" ", "_")
        if fw.get("claim_count") != by_framework[key]:
            errors.append(f"{META_PATH}: {fw['name']} claim_count = {fw.get('claim_count')}, "
                          f"the register holds {by_framework[key]}")
    truth["pinned"] = pinned
    return truth, errors


def register_main():
    truth, errors = check_register()
    print(f"\n\033[36m⊚ THE REGISTER AND ITS MIRRORS\033[0m  \033[2m{CLAIMS_PATH} holds "
          f"{truth['total']} records: " + " · ".join(f"{truth[s]} {s}" for s in STATUSES)
          + "\033[0m\n")
    if errors:
        for e in errors:
            print(f"  \033[31m✗\033[0m {e}")
        print(f"\n\033[31m✗ DRIFT\033[0m — {len(errors)} disagreement(s) across "
              f"{truth['pinned']} pinned counts. Fix the mirror, never the register, "
              f"unless the register is what is wrong.\n")
        return 1
    print(f"\033[32m✓ AGREED\033[0m — {truth['pinned']} pinned counts across "
          f"{', '.join(MIRRORS)} and {META_PATH} match the register.\n")
    return 0


if __name__ == "__main__":
    sys.exit(register_main() if "--register" in sys.argv else main())
