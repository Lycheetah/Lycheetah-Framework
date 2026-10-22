#!/usr/bin/env python3
"""Stage the RV22 patch against the frozen Earned Trust release runner.

`papers/agent-safety/earned-trust/cycles_001_009/` is pinned byte for byte by
`28_DEFENSE/RESEARCH_INTAKE_2026-10-18_SOURCE_MANIFEST.json` and
`tests/test_research_intake.py`, so nothing is edited in place. Every swap is applied
to the HEAD bytes, must match exactly once, and the patch is checked by applying it to
a fresh HEAD copy.

    python3 -B stage_rv22_patches.py <repo-root> <scratch-dir>

Writes:
    FOR-REVIEW/2026-10-22_OPUS_REVIEW/RV22_earned_trust_skip_count.patch

Applying it changes one intake-pinned file, so the intake manifest entry would need a
dated re-mint in the same change. That is Mac's call (see the ledger).
"""
from __future__ import annotations

import filecmp
import shutil
import subprocess
import sys
from pathlib import Path

RUNNER = "papers/agent-safety/earned-trust/cycles_001_009/verify_release.py"

SWAPS = [
    (" grand=0\n", " grand=0;skips=0\n"),
    ("""  count=int(found.group(1)) if found else 0
  print(f'C{i:03d}: {count} tests '+('PASS' if result.returncode==0 else 'FAIL'),flush=True)
""",
     """  count=int(found.group(1)) if found else 0
  # unittest counts a skipped method as run. On an ordinary-user host Cycle 009's
  # privilege-drop tests skip, so a run total is not a pass total.
  skipped=re.search(r'skipped=(\\d+)',output)
  skip=int(skipped.group(1)) if skipped else 0
  print(f'C{i:03d}: {count} tests ({skip} skipped) '+('PASS' if result.returncode==0 else 'FAIL'),flush=True)
"""),
    ("  grand+=count\n", "  grand+=count;skips+=skip\n"),
    (" print(f'Selected locally-authored suites: {grand} passing tests')\n",
     " print(f'Selected locally-authored suites: {grand-skips} passed, {skips} skipped ({grand} run); a skip is not a pass')\n"),
]

PATCH_NAME = "RV22_earned_trust_skip_count.patch"


def main() -> int:
    root, scratch = Path(sys.argv[1]).resolve(), Path(sys.argv[2]).resolve()
    out = root / "FOR-REVIEW/2026-10-22_OPUS_REVIEW" / PATCH_NAME
    work = scratch / "rv22_stage"
    if work.exists():
        shutil.rmtree(work)
    text = subprocess.run(["git", "-C", str(root), "show", f"HEAD:{RUNNER}"],
                          check=True, capture_output=True).stdout.decode("utf-8")
    assert (root / RUNNER).read_text(encoding="utf-8") == text, f"{RUNNER} differs from HEAD"
    new = text
    for old, rep in SWAPS:
        assert new.count(old) == 1, f"swap matched {new.count(old)}x: {old[:60]!r}"
        new = new.replace(old, rep)
    assert "\r" not in new
    for side, body in (("a", text), ("b", new)):
        dest = work / side / RUNNER
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(body, encoding="utf-8")
    diff = subprocess.run(["diff", "-ruN", "a", "b"], cwd=work, capture_output=True, text=True)
    assert diff.returncode == 1 and diff.stdout, "empty diff"
    out.write_text(diff.stdout, encoding="utf-8")
    check = work / "check"
    shutil.copytree(work / "a", check)
    subprocess.run(["patch", "-p1", "--quiet", "-i", str(out)], cwd=check, check=True)
    assert filecmp.cmp(check / RUNNER, work / "b" / RUNNER, shallow=False), "mismatch after patch"
    added = sum(1 for line in diff.stdout.splitlines() if line.startswith("+") and not line.startswith("+++"))
    removed = sum(1 for line in diff.stdout.splitlines() if line.startswith("-") and not line.startswith("---"))
    print(f"STAGED {PATCH_NAME}: 1 file, +{added} -{removed}, applies to HEAD copy and matches")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
