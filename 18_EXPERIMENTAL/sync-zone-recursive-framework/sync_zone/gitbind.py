"""Bind cycle records to real git state. Reads only: never commits, merges or pushes."""

from __future__ import annotations

import subprocess
from collections.abc import Iterable
from pathlib import Path
from typing import Any

from .canonical import candidate_digest, sha256_hex


class GitBindError(RuntimeError):
    pass


def _git(repo: str | Path, *args: str) -> str:
    proc = subprocess.run(["git", "-C", str(repo), *args], capture_output=True, text=True)
    if proc.returncode != 0:
        raise GitBindError(f"git {' '.join(args)} failed: {proc.stderr.strip()}")
    return proc.stdout


def head(repo: str | Path) -> str:
    return _git(repo, "rev-parse", "HEAD").strip()


def is_ancestor(repo: str | Path, older: str, newer: str) -> bool:
    proc = subprocess.run(["git", "-C", str(repo), "merge-base", "--is-ancestor", older, newer],
                          capture_output=True)
    return proc.returncode == 0


def assert_baseline(repo: str | Path, revision: str) -> None:
    """The recorded baseline must be the current HEAD or one of its ancestors."""
    if not is_ancestor(repo, revision, head(repo)):
        raise GitBindError(f"{revision} is not HEAD or an ancestor of HEAD")


def changed_paths(repo: str | Path, baseline: str) -> list[str]:
    """Tracked changes since ``baseline`` plus untracked files, excluding ignored ones."""
    tracked = _git(repo, "diff", "--name-only", baseline).splitlines()
    untracked = _git(repo, "ls-files", "--others", "--exclude-standard").splitlines()
    return sorted({p for p in tracked + untracked if p})


def artifacts(repo: str | Path, paths: Iterable[str]) -> list[dict[str, Any]]:
    """Working-tree content hashes; a missing file is recorded as a deletion."""
    out = []
    for p in sorted(set(paths)):
        f = Path(repo) / p
        out.append({"path": p, "sha256": sha256_hex(f.read_bytes()) if f.is_file() else None})
    return out


def candidate_from_worktree(repo: str | Path, baseline: str, candidate_id: str,
                            produced_by: str, paths: Iterable[str] | None = None) -> dict[str, Any]:
    assert_baseline(repo, baseline)
    arts = artifacts(repo, paths if paths is not None else changed_paths(repo, baseline))
    return {
        "candidate_id": candidate_id,
        "produced_by": produced_by,
        "baseline_revision": baseline,
        "artifacts": arts,
        "digest": candidate_digest(arts),
        "supersedes": None,
        "meta_governance": False,
        "effects": ["local_files"],
    }
