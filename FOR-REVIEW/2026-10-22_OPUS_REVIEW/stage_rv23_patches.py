#!/usr/bin/env python3
"""Stage the RV23 note against the canonical Truth Pressure master.

`TRUTH_PRESSURE/TRUTH_PRESSURE_MASTER_SOURCE_2026-08-07.md` is the dated canonical
master, so it is not edited in place. Its headline box reports the persona result as
"p=0.383 not significant". That p ignored tied scores (RV23). The patch adds a
correction note under the box and keeps the box as written. Every swap is applied to
the HEAD bytes, must match exactly once, and the patch is checked by applying it to a
fresh HEAD copy.

    python3 -B stage_rv23_patches.py <repo-root> <scratch-dir>

Writes:
    FOR-REVIEW/2026-10-22_OPUS_REVIEW/RV23_truth_pressure_persona_note.patch
"""
from __future__ import annotations

import filecmp
import shutil
import subprocess
import sys
from pathlib import Path

MASTER = "TRUTH_PRESSURE/TRUTH_PRESSURE_MASTER_SOURCE_2026-08-07.md"

ANCHOR = ("anthropics/evals, 1,000 statements   ROC-AUC 0.516    z=0.87   p=0.383     not significant\n"
          "```\n")
NOTE = """
> **Review correction (2026-10-22, RV23).** The third line of this box is wrong as a
> significance claim. Its p came from a Mann-Whitney SE that ignores tied scores, and
> 96.2% of the persona statements tie at one score. Tie-corrected p = 0.008; an exact
> permutation test (50,000 relabellings) gives p = 0.0096. AUC 0.516 is a detectable
> effect in the correct direction and still far too small to use, so the structural
> finding below survives with one word changed: the instrument sits *near* chance on
> real traffic, not *at* it. The box is kept as written. The corrected table, and which
> commit reproduces which hh-rlhf count, are in `33_APPLICATIONS/README.md`.
"""

SWAPS = [(ANCHOR, ANCHOR + NOTE)]
PATCH_NAME = "RV23_truth_pressure_persona_note.patch"


def main() -> int:
    root, scratch = Path(sys.argv[1]).resolve(), Path(sys.argv[2]).resolve()
    out = root / "FOR-REVIEW/2026-10-22_OPUS_REVIEW" / PATCH_NAME
    work = scratch / "rv23_stage"
    if work.exists():
        shutil.rmtree(work)
    text = subprocess.run(["git", "-C", str(root), "show", f"HEAD:{MASTER}"],
                          check=True, capture_output=True).stdout.decode("utf-8")
    assert (root / MASTER).read_text(encoding="utf-8") == text, f"{MASTER} differs from HEAD"
    new = text
    for old, rep in SWAPS:
        assert new.count(old) == 1, f"swap matched {new.count(old)}x: {old[:60]!r}"
        new = new.replace(old, rep)
    assert "\r" not in new
    for side, body in (("a", text), ("b", new)):
        dest = work / side / MASTER
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(body, encoding="utf-8")
    diff = subprocess.run(["diff", "-ruN", "a", "b"], cwd=work, capture_output=True, text=True)
    assert diff.returncode == 1 and diff.stdout, "empty diff"
    out.write_text(diff.stdout, encoding="utf-8")
    check = work / "check"
    shutil.copytree(work / "a", check)
    subprocess.run(["patch", "-p1", "--quiet", "-i", str(out)], cwd=check, check=True)
    assert filecmp.cmp(check / MASTER, work / "b" / MASTER, shallow=False), "mismatch after patch"
    added = sum(1 for line in diff.stdout.splitlines() if line.startswith("+") and not line.startswith("+++"))
    removed = sum(1 for line in diff.stdout.splitlines() if line.startswith("-") and not line.startswith("---"))
    print(f"STAGED {PATCH_NAME}: 1 file, +{added} -{removed}, applies to HEAD copy and matches")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
