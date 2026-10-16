#!/usr/bin/env python3
"""Read-only preflight for the v1.2 parser patch on an upstream checkout.

No files are changed. Requires the inspected source blob, a clean named branch,
and a clean git-apply check before telling the operator how to run the patch.
"""
from __future__ import annotations
import argparse
import hashlib
import subprocess
import sys
from pathlib import Path

EXPECTED_POLICY_BLOB_SHA = "913006991327ac40bf34e96fce591ca100334ca9"
TARGET = Path("lycheetah/assurance/policy.py")
ROOT = Path(__file__).resolve().parent
PATCH = ROOT / "strict_text_rule_parser_v1_2.patch"
TEST = ROOT / "test_assurance_policy_text_rule_types_v1_2.py"
DEST = Path("tests/test_assurance_policy_text_rule_types_v1_2.py")


def git(repo: Path, *args: str) -> str:
    result = subprocess.run(["git", *args], cwd=repo, text=True, capture_output=True)
    if result.returncode:
        raise RuntimeError(result.stderr.strip() or f"git {' '.join(args)} failed")
    return result.stdout.strip()


def git_blob_sha(data: bytes) -> str:
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
        print("FAIL: use a named non-default review branch; no files changed.", file=sys.stderr)
        return 2
    dirty = git(repo, "status", "--porcelain")
    if dirty:
        print("FAIL: checkout must be clean; no files changed.", file=sys.stderr)
        print(dirty, file=sys.stderr)
        return 2
    source = repo / TARGET
    if not source.is_file():
        print(f"FAIL: missing {TARGET}; no files changed.", file=sys.stderr)
        return 2
    actual = git_blob_sha(source.read_bytes())
    if actual != EXPECTED_POLICY_BLOB_SHA:
        print(f"FAIL: source blob mismatch: expected {EXPECTED_POLICY_BLOB_SHA}, found {actual}.", file=sys.stderr)
        print("Re-inspect and reconcile the patch instead of forcing it. No files changed.", file=sys.stderr)
        return 2
    if (repo / DEST).exists():
        print(f"FAIL: destination test already exists: {DEST}; inspect before proceeding.", file=sys.stderr)
        return 2
    check = subprocess.run(["git", "apply", "--check", str(PATCH)], cwd=repo, text=True, capture_output=True)
    if check.returncode:
        print("FAIL: patch does not apply cleanly. No files changed.", file=sys.stderr)
        print(check.stderr.strip(), file=sys.stderr)
        return 2
    print("PASS: source blob matches the inspected upstream revision.")
    print(f"PASS: clean worktree on review branch {branch!r}.")
    print("PASS: git apply --check.")
    print("No files were changed.")
    print(f"Next: git apply {PATCH}")
    print(f"Then: cp {TEST} {DEST}")
    print(f"Then: python -m pytest {DEST} tests/test_assurance_policy.py tests/test_assurance_runtime.py tests/test_assurance_models.py -q")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
