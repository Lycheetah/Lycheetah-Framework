#!/usr/bin/env python3
"""Safely preflight the strict policy-parser patch against an upstream checkout.

This script does not mutate the checkout. It only verifies that the caller is on
an explicit non-default branch, the worktree is clean, the target file matches
the inspected upstream blob, and git apply --check succeeds.
"""
from __future__ import annotations

import argparse
import hashlib
import subprocess
import sys
from pathlib import Path

EXPECTED_POLICY_BLOB_SHA = "913006991327ac40bf34e96fce591ca100334ca9"
TARGET = Path("lycheetah/assurance/policy.py")
PATCH = Path(__file__).resolve().parents[1] / "r2_policy_parser_audit/proposed_patches/strict_text_rule_parser.patch"
TEST = Path(__file__).resolve().parents[1] / "r2_policy_parser_audit/proposed_patches/test_assurance_policy_text_rule_types.py"
TEST_DEST = Path("tests/test_assurance_policy_text_rule_types.py")


def git(repo: Path, *args: str) -> str:
    result = subprocess.run(
        ["git", *args], cwd=repo, text=True, capture_output=True, check=False
    )
    if result.returncode:
        raise RuntimeError(result.stderr.strip() or f"git {' '.join(args)} failed")
    return result.stdout.strip()


def git_blob_sha(data: bytes) -> str:
    header = f"blob {len(data)}\0".encode("ascii")
    return hashlib.sha1(header + data).hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("repo", type=Path, help="path to a local Lycheetah-Framework checkout")
    args = parser.parse_args()
    repo = args.repo.resolve()

    if not (repo / ".git").exists():
        parser.error(f"not a Git checkout: {repo}")
    branch = git(repo, "branch", "--show-current")
    if not branch or branch in {"master", "main"}:
        print("FAIL: use a named non-default review branch; no files were changed.", file=sys.stderr)
        return 2
    dirty = git(repo, "status", "--porcelain")
    if dirty:
        print("FAIL: worktree must be clean before patching; no files were changed.", file=sys.stderr)
        print(dirty, file=sys.stderr)
        return 2

    source = repo / TARGET
    if not source.is_file():
        print(f"FAIL: missing target file {TARGET}; no files were changed.", file=sys.stderr)
        return 2
    actual = git_blob_sha(source.read_bytes())
    if actual != EXPECTED_POLICY_BLOB_SHA:
        print(
            "FAIL: policy.py does not match the inspected source blob. "
            f"Expected {EXPECTED_POLICY_BLOB_SHA}, found {actual}. No files were changed.",
            file=sys.stderr,
        )
        return 2
    if (repo / TEST_DEST).exists():
        print(f"FAIL: {TEST_DEST} already exists; inspect it before proceeding.", file=sys.stderr)
        return 2

    check = subprocess.run(
        ["git", "apply", "--check", str(PATCH)], cwd=repo, text=True, capture_output=True
    )
    if check.returncode:
        print("FAIL: patch does not apply cleanly; no files were changed.", file=sys.stderr)
        print(check.stderr.strip(), file=sys.stderr)
        return 2

    print("PASS: upstream source blob matches the inspected revision.")
    print(f"PASS: checkout is on branch {branch!r} with a clean worktree.")
    print("PASS: git apply --check accepts the proposed patch.")
    print("No files were changed by this preflight.")
    print("Next, from the checkout root, run:")
    print(f"  git apply {PATCH}")
    print(f"  cp {TEST} {TEST_DEST}")
    print("  python -m pytest tests/test_assurance_policy_text_rule_types.py tests/test_assurance_policy.py tests/test_assurance_runtime.py tests/test_assurance_models.py -q")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
