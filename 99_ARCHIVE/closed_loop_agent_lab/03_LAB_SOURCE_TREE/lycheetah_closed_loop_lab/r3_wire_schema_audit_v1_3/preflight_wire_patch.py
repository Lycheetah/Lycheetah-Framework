#!/usr/bin/env python3
"""Read-only upstream preflight for strict assurance wire-type patch v1.3."""
from __future__ import annotations
import argparse
import hashlib
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
PATCH = ROOT / "strict_assurance_wire_types_v1_3.patch"
EXPECTED = {
    Path("lycheetah/assurance/models.py"): "12895f2a7d3e66f4584040713dad131c154b80f0",
    Path("lycheetah/assurance/receipt.py"): "91f9ec4d7177480d259240a0899b8b54aff6f0e5",
}
TEST = ROOT / "test_assurance_wire_types.py"
TEST_DEST = Path("tests/test_assurance_wire_types.py")


def git(repo: Path, *args: str) -> str:
    p = subprocess.run(["git", *args], cwd=repo, text=True, capture_output=True)
    if p.returncode:
        raise RuntimeError(p.stderr.strip() or f"git {' '.join(args)} failed")
    return p.stdout.strip()


def blob_sha(data: bytes) -> str:
    return hashlib.sha1(f"blob {len(data)}\0".encode("ascii") + data).hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("repo", type=Path, help="path to a local Lycheetah-Framework checkout")
    args = parser.parse_args()
    repo = args.repo.resolve()
    if not (repo / ".git").exists():
        parser.error(f"not a Git checkout: {repo}")
    branch = git(repo, "branch", "--show-current")
    if not branch or branch in {"main", "master"}:
        print("FAIL: use a named non-default branch; no files changed.", file=sys.stderr)
        return 2
    dirty = git(repo, "status", "--porcelain")
    if dirty:
        print("FAIL: worktree must be clean; no files changed.", file=sys.stderr)
        print(dirty, file=sys.stderr)
        return 2
    for relative, expected in EXPECTED.items():
        target = repo / relative
        if not target.is_file():
            print(f"FAIL: missing {relative}; no files changed.", file=sys.stderr)
            return 2
        actual = blob_sha(target.read_bytes())
        if actual != expected:
            print(f"FAIL: source blob mismatch at {relative}: {actual}; expected {expected}.", file=sys.stderr)
            print("Re-inspect and reconcile; do not force the patch. No files changed.", file=sys.stderr)
            return 2
    if (repo / TEST_DEST).exists():
        print(f"FAIL: {TEST_DEST} already exists; inspect it first.", file=sys.stderr)
        return 2
    check = subprocess.run(["git", "apply", "--check", str(PATCH)], cwd=repo, text=True, capture_output=True)
    if check.returncode:
        print("FAIL: patch does not apply cleanly; no files changed.", file=sys.stderr)
        print(check.stderr.strip(), file=sys.stderr)
        return 2
    print("PASS: both source blobs match the inspected revision.")
    print(f"PASS: clean worktree on review branch {branch!r}.")
    print("PASS: git apply --check.")
    print("No files were changed.")
    print(f"Next: git apply {PATCH}")
    print(f"Then: cp {TEST} {TEST_DEST}")
    print(f"Then: python -m pytest {TEST_DEST} tests/test_assurance_models.py tests/test_assurance_receipt.py tests/test_assurance_runtime.py -q")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
