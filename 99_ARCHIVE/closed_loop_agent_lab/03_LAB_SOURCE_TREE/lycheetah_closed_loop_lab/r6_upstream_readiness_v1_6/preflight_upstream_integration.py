#!/usr/bin/env python3
"""Read-only source-pinned preflight; never edits the user's checkout.

It checks that the checkout matches the inspected source snapshot, is clean on
a non-default branch, simulates all source patches in a temporary copy, syntax-
compiles patched Python files, meta-validates candidate schemas and verifies
that proposed new test destinations are unused.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

import jsonschema

HERE = Path(__file__).resolve().parent
BASE_COMMIT = "8ae1b367dcf09997e82ce66f9ad5d30ff36e5d65"
EXPECTED_BLOBS = {
    "lycheetah/assurance/models.py": "12895f2a7d3e66f4584040713dad131c154b80f0",
    "lycheetah/assurance/receipt.py": "91f9ec4d7177480d259240a0899b8b54aff6f0e5",
    "lycheetah/assurance/policy.py": "913006991327ac40bf34e96fce591ca100334ca9",
    "lycheetah/assurance/schemas/policy.schema.json": "669f21b9f2c800f15e93116d1b9cbeb1bd84e128",
    "lycheetah/assurance/schemas/receipt.schema.json": "eeb1306040a17ce530f42f74966b185fece9a41e",
}
PATCHES_IN_ORDER = [
    "strict_assurance_wire_types_v1_3.patch",
    "receipt_contract_delta_v1_6.patch",
    "policy_type_guard_v1_6.patch",
]
NEW_TEST_PATHS = [
    "tests/test_assurance_wire_types.py",
    "tests/test_assurance_policy_wire_types.py",
    "tests/test_assurance_candidate_schemas.py",
]


def run(args, cwd: Path) -> str:
    p = subprocess.run(args, cwd=cwd, text=True, capture_output=True)
    if p.returncode:
        raise RuntimeError(f"command failed ({' '.join(map(str,args))}):\n{p.stderr.strip() or p.stdout.strip()}")
    return p.stdout.strip()


def git_blob_sha(data: bytes) -> str:
    return hashlib.sha1(f"blob {len(data)}\0".encode("ascii") + data).hexdigest()


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("repo", type=Path, help="local Lycheetah-Framework checkout")
    args = ap.parse_args()
    repo = args.repo.resolve()
    if not (repo / ".git").exists():
        ap.error(f"not a Git checkout: {repo}")
    branch = run(["git", "branch", "--show-current"], repo)
    head = run(["git", "rev-parse", "HEAD"], repo)
    if branch in {"", "master", "main"}:
        print("FAIL: use a named non-default review branch. No repository files changed.", file=sys.stderr)
        return 2
    if head != BASE_COMMIT:
        print(f"FAIL: checkout HEAD {head} differs from inspected base {BASE_COMMIT}. Re-inspect; no changes made.", file=sys.stderr)
        return 2
    dirty = run(["git", "status", "--porcelain"], repo)
    if dirty:
        print("FAIL: worktree must be clean before preflight. No repository files changed.", file=sys.stderr)
        print(dirty, file=sys.stderr)
        return 2
    for rel, expected in EXPECTED_BLOBS.items():
        p = repo / rel
        if not p.is_file():
            print(f"FAIL: missing {rel}", file=sys.stderr)
            return 2
        actual = git_blob_sha(p.read_bytes())
        if actual != expected:
            print(f"FAIL: source blob mismatch for {rel}: {actual} (expected {expected})", file=sys.stderr)
            print("Re-inspect the patch against the new source; do not force it.", file=sys.stderr)
            return 2
    for rel in NEW_TEST_PATHS:
        if (repo / rel).exists():
            print(f"FAIL: destination already exists: {rel}; inspect it first.", file=sys.stderr)
            return 2
    for name in ("policy.schema.strict-candidate.json", "receipt.schema.strict-candidate.json"):
        schema = json.loads((HERE / name).read_text(encoding="utf-8"))
        jsonschema.Draft202012Validator.check_schema(schema)
    with tempfile.TemporaryDirectory(prefix="lycheetah-preflight-") as tmp_s:
        tmp = Path(tmp_s)
        for rel in EXPECTED_BLOBS:
            dest = tmp / rel
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(repo / rel, dest)
        run(["git", "init", "-q"], tmp)
        run(["git", "add", "."], tmp)
        run(["git", "-c", "user.name=LycheetahPreflight", "-c", "user.email=preflight@example.invalid", "commit", "-qm", "source-pinned patch context"], tmp)
        for patch_name in PATCHES_IN_ORDER:
            patch = HERE / patch_name
            run(["git", "apply", "--check", "-p1", str(patch)], tmp)
            run(["git", "apply", "-p1", str(patch)], tmp)
        for rel in ("lycheetah/assurance/models.py", "lycheetah/assurance/receipt.py", "lycheetah/assurance/policy.py"):
            run([sys.executable, "-m", "py_compile", str(tmp / rel)], tmp)
    print(f"PASS: exact source blobs match inspected base {BASE_COMMIT}.")
    print(f"PASS: clean worktree on non-default branch {branch!r}.")
    print("PASS: source patches apply sequentially in a temporary copy; no checkout files changed.")
    print("PASS: patched Python files syntax-compile in the temporary copy.")
    print("PASS: policy and receipt candidate schemas pass Draft 2020-12 meta-validation.")
    print("LIMIT: this does not run the package test suite or migrate persisted records.")
    print("Next: apply patches in the same order, replace the two schema files, copy the three tests, then run the prescribed pytest suite and migration inventory.")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
