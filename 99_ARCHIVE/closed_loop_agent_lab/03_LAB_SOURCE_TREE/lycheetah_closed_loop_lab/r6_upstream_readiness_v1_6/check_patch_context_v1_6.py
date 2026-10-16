#!/usr/bin/env python3
"""Synthetic unified-diff context check; not a substitute for real checkout preflight."""
from __future__ import annotations
import json
import re
import shutil
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent
PATCHES = [
    ROOT / "strict_assurance_wire_types_v1_3.patch",
    ROOT / "receipt_contract_delta_v1_6.patch",
    ROOT / "policy_type_guard_v1_6.patch",
]


def run(cwd: Path, *args: str):
    return subprocess.run(["git", *args], cwd=cwd, text=True, capture_output=True, check=False)


def sparse_context(patch: Path, target: Path):
    lines = patch.read_text(encoding="utf-8").splitlines()
    files: dict[str, dict[int, str]] = {}
    current = None
    i = 0
    while i < len(lines):
        line = lines[i]
        if line.startswith("diff --git "):
            m = re.match(r"diff --git a/(.+) b/(.+)", line)
            current = m.group(2)
            files.setdefault(current, {})
            i += 1
            continue
        m = re.match(r"@@ -(\d+)(?:,(\d+))? \+(\d+)(?:,(\d+))? @@", line)
        if m and current:
            pos = int(m.group(1)) - 1
            i += 1
            while i < len(lines) and not lines[i].startswith("@@ ") and not lines[i].startswith("diff --git "):
                part = lines[i]
                if part.startswith(" ") or part.startswith("-"):
                    raw = part[1:]
                    if pos in files[current] and files[current][pos] != raw:
                        raise ValueError(f"overlapping synthetic source context: {current}:{pos+1}")
                    files[current][pos] = raw
                    pos += 1
                i += 1
            continue
        i += 1
    target.mkdir(parents=True, exist_ok=True)
    for rel, indexed in files.items():
        p = target / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        maxline = max(indexed) if indexed else 0
        out = ["# omitted upstream context in synthetic fixture"] * (maxline + 1)
        for idx, value in indexed.items():
            out[idx] = value
        p.write_text("\n".join(out) + "\n", encoding="utf-8")
    return sorted(files)


def check(patch: Path) -> dict:
    with tempfile.TemporaryDirectory(prefix="lycheetah-patch-context-v1.6-") as tmp_s:
        tmp = Path(tmp_s)
        targets = sparse_context(patch, tmp)
        init = run(tmp, "init", "-q")
        if init.returncode:
            raise RuntimeError(init.stderr)
        if (a := run(tmp, "add", ".")).returncode:
            raise RuntimeError(a.stderr)
        if (c := run(tmp, "-c", "user.name=PatchFixture", "-c", "user.email=fixture@example.invalid", "commit", "-qm", "synthetic patch context")).returncode:
            raise RuntimeError(c.stderr)
        result = run(tmp, "apply", "--check", str(patch))
        if result.returncode:
            return {"patch": patch.name, "status": "FAIL_SYNTHETIC_CONTEXT", "error": result.stderr.strip(), "targets": targets}
        applied = run(tmp, "apply", str(patch))
        if applied.returncode:
            return {"patch": patch.name, "status": "FAIL_SYNTHETIC_APPLY", "error": applied.stderr.strip(), "targets": targets}
        return {"patch": patch.name, "status": "PASS_SYNTHETIC_CONTEXT_ONLY", "targets": targets}


def main():
    results = [check(p) for p in PATCHES]
    out = {"purpose": "synthetic hunk/context smoke test only", "results": results, "all_pass": all(r["status"] == "PASS_SYNTHETIC_CONTEXT_ONLY" for r in results), "warning": "Does not prove applicability to a full repository checkout or passing package tests."}
    (ROOT / "patch_context_check_v1_6.json").write_text(json.dumps(out, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(out, indent=2))
    return 0 if out["all_pass"] else 1

if __name__ == "__main__":
    raise SystemExit(main())
