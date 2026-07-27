#!/usr/bin/env python3
"""THE LINKS RESOLVE — a corpus gate.

Every markdown link that points at a local file must point at a file that exists.

Companion to `verify-claims.py`, and it works the same way: it holds a **baseline**
rather than demanding a clean sweep. 99_ARCHIVE is a frozen record of a closed era —
its links are allowed to stay broken, and are counted, not fixed. Everywhere else the
budget is zero.

History: the 2026-07-27 audit cut dead links from 116 to 26, then to 21 (all archive)
on the same day. Nothing stopped them coming back. This does.

⚠ Two defects this tool was born with, both found by deliberate breakage:
  1. `git ls-files` alone misses untracked files — the same blind spot that let
     verify-claims.py pass its own regression test while broken. Uses
     --cached --others --exclude-standard.
  2. A link is a URL, not a path: `%20` and `%E2%80%93` must be decoded before the
     existence check, or a live link reads as dead. Cost one false "dead link" before
     it was caught.

Exit 0 = holding. Exit 1 = a new dead link outside the archive.
"""
import re
import subprocess
import sys
from pathlib import Path
from urllib.parse import unquote

ARCHIVE = "99_ARCHIVE"
BASELINE_OUTSIDE = 0  # the budget outside the archive: zero

C_GREEN, C_RED, C_DIM, C_OFF = "\033[32m", "\033[31m", "\033[2m", "\033[0m"

# [text](target) — tolerates <angle brackets> and a "title" after the target
LINK = re.compile(r"\[[^\]]*\]\(\s*(<)?([^)>\s]+)(?(1)>)[^)]*\)")
EXTERNAL = re.compile(r"^(https?:|mailto:|ftp:|tel:|data:|#)")


def main() -> int:
    root = Path(sys.argv[1] if len(sys.argv) > 1 else ".").resolve()

    listing = subprocess.run(
        ["git", "ls-files", "--cached", "--others", "--exclude-standard", "-z"],
        cwd=root, capture_output=True, text=True, check=True,
    )
    files = [root / p for p in listing.stdout.split("\0") if p.endswith(".md")]

    total = local = 0
    dead: list[tuple[Path, int, str]] = []

    for f in files:
        try:
            text = f.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        for m in LINK.finditer(text):
            target = m.group(2)
            total += 1
            if EXTERNAL.match(target):
                continue
            path = target.split("#", 1)[0].split("?", 1)[0]
            if not path:
                continue  # pure in-page anchor
            local += 1
            if not (f.parent / unquote(path)).resolve().exists():
                dead.append((f.relative_to(root), text[: m.start()].count("\n") + 1, target))

    outside = [d for d in dead if not str(d[0]).startswith(ARCHIVE)]
    archived = len(dead) - len(outside)

    print(f"{C_DIM}scanned {len(files)} files · {total} links · {local} local{C_OFF}")

    for path, line, target in sorted(outside):
        print(f"  {C_RED}✗{C_OFF} {path}:{line} → {target}")

    if len(outside) > BASELINE_OUTSIDE:
        print(
            f"\n{C_RED}✗ BROKEN{C_OFF} — {len(outside)} dead link(s) outside the archive, "
            f"budget {BASELINE_OUTSIDE}. A link that points at nothing is a claim that "
            f"the thing exists."
        )
        return 1

    print(
        f"\n{C_GREEN}✓ THE LINKS RESOLVE{C_OFF} — 0 dead outside the archive · "
        f"{archived} inside {ARCHIVE}, held as a frozen record."
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
