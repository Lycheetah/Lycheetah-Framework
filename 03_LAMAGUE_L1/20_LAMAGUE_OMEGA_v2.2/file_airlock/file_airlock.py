#!/usr/bin/env python3
"""
===============================================================================
LYCHEETAH FILE AIRLOCK — REAL FILESYSTEM SNAPSHOT, BOUNDARY DIFF & ROLLBACK
===============================================================================
Author:   Aetheron (Antigravity Seat — Gemini 4 Argon) & Mackenzie Conor James Clark
Lineage:  Lycheetah Framework — Real-World Permissioned Work, Write-Scope
          Enforcement, Handover-vs-Disk Verification, and 1-Command Recovery
Location: creations/file_airlock/file_airlock.py

Solves the four concrete engineering requirements from
`2026-10-18_REAL_TOOL_DISCUSSION.md` using real filesystem bytes (zero mocks):

  1. Pre-Task Snapshot & Content-Addressed Backup (`open_airlock_snapshot`):
     Captures the exact pre-task SHA-256 hashes, byte sizes, file modes (S_IMODE),
     symlinks, empty directories, and zlib-compressed file contents of a target
     workspace, bound to explicit `allow_globs`, `forbid_globs`, a strict total
     size cap (`max_total_bytes`), and an optional HMAC-SHA256 passphrase seal.

  2. Live Post-Task Filesystem vs. Policy & Handover Audit (`verify_airlock_state`):
     Compares the live directory on disk against the pre-task snapshot and
     separates:
       - `authorized_changes`: modified/added/deleted regular files inside
         `allow_globs` and outside `forbid_globs`.
       - `boundary_breaches`: any modification, addition, or deletion inside
         `forbid_globs` or outside `allow_globs`, plus any added, modified, or
         removed symlink (`SYMLINK_MUTATION_FORBIDDEN`).
       - `handover_mismatches`: cross-checks a Markdown handover (`HANDOVER.md`)
         against actual disk changes—catching both `UNDECLARED_DISK_MUTATION`
         and `PHANTOM_HANDOVER_CLAIM`.

  3. Atomic Byte-Exact Rollback (`rollback_airlock_snapshot`):
     Verifies via `os.lstat` that neither the target nor any parent directory is
     a symlink or resolves outside `root_dir`, writes atomically via a same-dir
     temporary file + `os.replace`, restores file modes (`S_IMODE`) and empty
     directories, removes untracked files and untracked empty directories, and
     flags any symlinked/missing-payload file in `unrecoverable_files` (failing
     closed with nonzero exit).
===============================================================================
"""

from __future__ import annotations

import argparse
import base64
import fnmatch
import hashlib
import hmac
import json
import os
import stat
import sys
import tempfile
import time
import zlib
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple


DEFAULT_IGNORE_NAMES: Set[str] = {
    ".git",
    "__pycache__",
    ".pytest_cache",
    ".ruff_cache",
    ".mypy_cache",
    "node_modules",
    ".airlock_snapshot.json",
}

DEFAULT_MAX_TOTAL_BYTES: int = 50_000_000  # 50 MB total snapshot cap


@dataclass
class FileRecord:
    rel_path: str
    size_bytes: int
    sha256: str
    compressed_b64: str  # zlib-compressed base64 payload for exact recovery
    mode: int = 0o644


@dataclass
class AirlockSnapshot:
    snapshot_id: str
    created_at_unix: float
    root_dir: str
    allow_globs: List[str]
    forbid_globs: List[str]
    files: Dict[str, FileRecord]
    symlinks: Dict[str, str] = field(default_factory=dict)
    empty_dirs: List[str] = field(default_factory=list)
    content_stored: bool = True
    warnings: List[str] = field(default_factory=list)
    manifest_sha256: str = ""
    hmac_signature: str = ""

    def compute_manifest_digest(self) -> str:
        payload = {
            "snapshot_id": self.snapshot_id,
            "root_dir": self.root_dir,
            "allow_globs": sorted(self.allow_globs),
            "forbid_globs": sorted(self.forbid_globs),
            "content_stored": self.content_stored,
            "files": {
                k: {
                    "size_bytes": v.size_bytes,
                    "sha256": v.sha256,
                    "mode": v.mode,
                }
                for k, v in sorted(self.files.items())
            },
            "symlinks": dict(sorted(self.symlinks.items())),
            "empty_dirs": sorted(self.empty_dirs),
        }
        raw = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
        return hashlib.sha256(raw).hexdigest()

    def compute_hmac(self, secret: str) -> str:
        digest = self.compute_manifest_digest()
        return hmac.new(secret.encode("utf-8"), digest.encode("utf-8"), hashlib.sha256).hexdigest()


def _matches_any_glob(rel_path: str, globs: List[str]) -> bool:
    for g in globs:
        norm_g = g.strip().lstrip("./")
        if (
            fnmatch.fnmatch(rel_path, norm_g)
            or rel_path.startswith(norm_g.rstrip("/") + "/")
            or rel_path == norm_g.rstrip("/")
        ):
            return True
    return False


def _scan_directory_state(
    root_dir: Path,
    max_file_bytes: int = 2_000_000,
    max_total_bytes: int = DEFAULT_MAX_TOTAL_BYTES,
    store_content: bool = True,
) -> Tuple[Dict[str, FileRecord], Dict[str, str], List[str], List[str]]:
    root = root_dir.resolve()
    records: Dict[str, FileRecord] = {}
    symlinks: Dict[str, str] = {}
    empty_dirs: List[str] = []
    warnings: List[str] = []
    total_bytes = 0

    for dirpath, dirnames, filenames in os.walk(root, followlinks=False):
        kept_dirs: List[str] = []
        for d in sorted(dirnames):
            if d in DEFAULT_IGNORE_NAMES:
                continue
            dpath = Path(dirpath) / d
            st = os.lstat(dpath)
            rel_d = dpath.relative_to(root).as_posix()
            if stat.S_ISLNK(st.st_mode):
                symlinks[rel_d] = os.readlink(dpath)
            else:
                kept_dirs.append(d)
        dirnames[:] = kept_dirs

        valid_filenames = [
            f for f in sorted(filenames)
            if f not in DEFAULT_IGNORE_NAMES and not f.endswith(".airlock.json")
        ]
        cur_dir = Path(dirpath)
        if cur_dir != root and not kept_dirs and not valid_filenames:
            empty_dirs.append(cur_dir.relative_to(root).as_posix())

        for fname in valid_filenames:
            fpath = cur_dir / fname
            st = os.lstat(fpath)
            rel = fpath.relative_to(root).as_posix()
            if stat.S_ISLNK(st.st_mode):
                symlinks[rel] = os.readlink(fpath)
                continue
            if not stat.S_ISREG(st.st_mode):
                continue

            raw = fpath.read_bytes()
            total_bytes += len(raw)
            if total_bytes > max_total_bytes:
                raise ValueError(
                    f"AIRLOCK_SNAPSHOT_SIZE_CAP_EXCEEDED: total bytes ({total_bytes}) exceeds cap ({max_total_bytes})"
                )

            sha = hashlib.sha256(raw).hexdigest()
            fmode = stat.S_IMODE(st.st_mode)
            if store_content and len(raw) <= max_file_bytes:
                comp_b64 = base64.b64encode(zlib.compress(raw, level=6)).decode("ascii")
            else:
                comp_b64 = ""
                warnings.append(
                    f"File {rel!r} ({len(raw)} bytes) stored without content payload; rollback will be impossible for this file."
                )

            records[rel] = FileRecord(
                rel_path=rel,
                size_bytes=len(raw),
                sha256=sha,
                compressed_b64=comp_b64,
                mode=fmode,
            )

    return records, symlinks, sorted(empty_dirs), warnings


def open_airlock_snapshot(
    root_dir: Path,
    allow_globs: Optional[List[str]] = None,
    forbid_globs: Optional[List[str]] = None,
    snapshot_out: Optional[Path] = None,
    secret_key: str = "",
    store_content: bool = True,
    max_file_bytes: int = 2_000_000,
    max_total_bytes: int = DEFAULT_MAX_TOTAL_BYTES,
) -> AirlockSnapshot:
    """
    Create a real content-addressed filesystem snapshot of `root_dir` with explicit
    write-scope `allow_globs` and read-only `forbid_globs`.
    """
    root = root_dir.resolve()
    allow = list(allow_globs) if allow_globs else ["*"]
    forbid = list(forbid_globs) if forbid_globs else []
    files, symlinks, empty_dirs, warnings = _scan_directory_state(
        root,
        max_file_bytes=max_file_bytes,
        max_total_bytes=max_total_bytes,
        store_content=store_content,
    )
    if not store_content:
        msg = "WARNING: open_airlock_snapshot called with store_content=False; byte-exact rollback is impossible!"
        if msg not in warnings:
            warnings.insert(0, msg)
        print(msg, file=sys.stderr)

    snap_id = f"AIRLOCK-{int(time.time())}-{hashlib.sha256(str(root).encode('utf-8')).hexdigest()[:8]}"
    snap = AirlockSnapshot(
        snapshot_id=snap_id,
        created_at_unix=round(time.time(), 3),
        root_dir=str(root),
        allow_globs=allow,
        forbid_globs=forbid,
        files=files,
        symlinks=symlinks,
        empty_dirs=empty_dirs,
        content_stored=store_content,
        warnings=warnings,
    )
    snap.manifest_sha256 = snap.compute_manifest_digest()
    if secret_key:
        snap.hmac_signature = snap.compute_hmac(secret_key)

    if snapshot_out is not None:
        save_snapshot_to_file(snap, snapshot_out)
    return snap


def save_snapshot_to_file(snap: AirlockSnapshot, path: Path) -> None:
    data = {
        "snapshot_id": snap.snapshot_id,
        "created_at_unix": snap.created_at_unix,
        "root_dir": snap.root_dir,
        "allow_globs": snap.allow_globs,
        "forbid_globs": snap.forbid_globs,
        "content_stored": snap.content_stored,
        "warnings": snap.warnings,
        "manifest_sha256": snap.manifest_sha256,
        "hmac_signature": snap.hmac_signature,
        "files": {k: asdict(v) for k, v in sorted(snap.files.items())},
        "symlinks": dict(sorted(snap.symlinks.items())),
        "empty_dirs": sorted(snap.empty_dirs),
    }
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")


def load_snapshot_from_file(path: Path, secret_key: str = "") -> AirlockSnapshot:
    raw = json.loads(path.read_text(encoding="utf-8"))
    files = {
        k: FileRecord(
            rel_path=v["rel_path"],
            size_bytes=int(v["size_bytes"]),
            sha256=v["sha256"],
            compressed_b64=v.get("compressed_b64", ""),
            mode=int(v.get("mode", 0o644)),
        )
        for k, v in raw.get("files", {}).items()
    }
    snap = AirlockSnapshot(
        snapshot_id=raw["snapshot_id"],
        created_at_unix=float(raw["created_at_unix"]),
        root_dir=raw["root_dir"],
        allow_globs=list(raw.get("allow_globs", ["*"])),
        forbid_globs=list(raw.get("forbid_globs", [])),
        files=files,
        symlinks=dict(raw.get("symlinks", {})),
        empty_dirs=list(raw.get("empty_dirs", [])),
        content_stored=bool(raw.get("content_stored", True)),
        warnings=list(raw.get("warnings", [])),
        manifest_sha256=raw.get("manifest_sha256", ""),
        hmac_signature=raw.get("hmac_signature", ""),
    )
    expected_digest = snap.compute_manifest_digest()
    if not snap.manifest_sha256:
        raise ValueError(
            "AIRLOCK_MANIFEST_UNSIGNED_OR_TAMPERED: snapshot manifest_sha256 is empty or missing!"
        )
    if snap.manifest_sha256 != expected_digest:
        raise ValueError(
            "AIRLOCK_MANIFEST_TAMPERED: snapshot manifest_sha256 does not match file table!"
        )
    if snap.hmac_signature and not secret_key:
        raise ValueError(
            "AIRLOCK_HMAC_REQUIRED: snapshot carries an HMAC signature; a non-empty secret_key is required!"
        )
    if secret_key:
        if not snap.hmac_signature:
            raise ValueError(
                "AIRLOCK_HMAC_INVALID: secret_key provided, but snapshot has no HMAC signature!"
            )
        expected_hmac = snap.compute_hmac(secret_key)
        if not hmac.compare_digest(snap.hmac_signature, expected_hmac):
            raise ValueError(
                "AIRLOCK_HMAC_INVALID: human passphrase HMAC signature verification failed!"
            )
    return snap


def _is_path_authorized(rel_path: str, allow_globs: List[str], forbid_globs: List[str]) -> Tuple[bool, str]:
    if _matches_any_glob(rel_path, forbid_globs):
        return False, f"MATCHED_FORBID_BOUNDARY ({forbid_globs})"
    if not _matches_any_glob(rel_path, allow_globs):
        return False, f"OUTSIDE_ALLOW_SCOPE ({allow_globs})"
    return True, "AUTHORIZED_IN_SCOPE"


def verify_airlock_state(
    snap: AirlockSnapshot,
    handover_md_text: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Compare the live filesystem on disk against `snap` (and optionally a Markdown
    handover report), separating Intended / Authorized / Observed / Breached changes.
    """
    root = Path(snap.root_dir).resolve()
    current_files, current_symlinks, _current_empty_dirs, _ = _scan_directory_state(
        root,
        max_total_bytes=10**12,
        store_content=False,
    )

    before_paths = set(snap.files.keys())
    after_paths = set(current_files.keys())

    added = sorted(after_paths - before_paths)
    deleted = sorted(before_paths - after_paths)
    modified = sorted(
        p for p in (before_paths & after_paths)
        if (
            snap.files[p].sha256 != current_files[p].sha256
            or snap.files[p].mode != current_files[p].mode
        )
    )
    unchanged_count = len(before_paths & after_paths) - len(modified)

    all_changed: List[Dict[str, Any]] = []
    authorized_changes: List[Dict[str, Any]] = []
    boundary_breaches: List[Dict[str, Any]] = []

    for p in added:
        ok, reason = _is_path_authorized(p, snap.allow_globs, snap.forbid_globs)
        entry = {
            "rel_path": p,
            "change_type": "ADDED",
            "before_sha256": None,
            "after_sha256": current_files[p].sha256,
            "authorized": ok,
            "policy_reason": reason,
        }
        all_changed.append(entry)
        (authorized_changes if ok else boundary_breaches).append(entry)

    for p in modified:
        ok, reason = _is_path_authorized(p, snap.allow_globs, snap.forbid_globs)
        entry = {
            "rel_path": p,
            "change_type": "MODIFIED",
            "before_sha256": snap.files[p].sha256,
            "after_sha256": current_files[p].sha256,
            "authorized": ok,
            "policy_reason": reason,
        }
        all_changed.append(entry)
        (authorized_changes if ok else boundary_breaches).append(entry)

    for p in deleted:
        ok, reason = _is_path_authorized(p, snap.allow_globs, snap.forbid_globs)
        entry = {
            "rel_path": p,
            "change_type": "DELETED",
            "before_sha256": snap.files[p].sha256,
            "after_sha256": None,
            "authorized": ok,
            "policy_reason": reason,
        }
        all_changed.append(entry)
        (authorized_changes if ok else boundary_breaches).append(entry)

    # Check symlink mutations: added, removed, or retargeted symlinks are ALWAYS breaches in check
    before_syms = set(snap.symlinks.keys())
    after_syms = set(current_symlinks.keys())
    for sp in sorted(after_syms - before_syms):
        entry = {
            "rel_path": sp,
            "change_type": "SYMLINK_ADDED",
            "before_sha256": None,
            "after_sha256": f"symlink->{current_symlinks[sp]}",
            "authorized": False,
            "policy_reason": "SYMLINK_MUTATION_FORBIDDEN",
        }
        all_changed.append(entry)
        boundary_breaches.append(entry)

    for sp in sorted(before_syms - after_syms):
        entry = {
            "rel_path": sp,
            "change_type": "SYMLINK_DELETED",
            "before_sha256": f"symlink->{snap.symlinks[sp]}",
            "after_sha256": None,
            "authorized": False,
            "policy_reason": "SYMLINK_MUTATION_FORBIDDEN",
        }
        all_changed.append(entry)
        boundary_breaches.append(entry)

    for sp in sorted(before_syms & after_syms):
        if snap.symlinks[sp] != current_symlinks[sp]:
            entry = {
                "rel_path": sp,
                "change_type": "SYMLINK_MODIFIED",
                "before_sha256": f"symlink->{snap.symlinks[sp]}",
                "after_sha256": f"symlink->{current_symlinks[sp]}",
                "authorized": False,
                "policy_reason": "SYMLINK_MUTATION_FORBIDDEN",
            }
            all_changed.append(entry)
            boundary_breaches.append(entry)

    # Optional: Cross-check Markdown handover claims against actual disk changes
    handover_mismatches: List[Dict[str, str]] = []
    if handover_md_text is not None:
        changed_rel_set = {ch["rel_path"] for ch in all_changed}
        for ch in all_changed:
            rel_p = ch["rel_path"]
            fname = Path(rel_p).name
            if rel_p not in handover_md_text and fname not in handover_md_text:
                handover_mismatches.append({
                    "code": "UNDECLARED_DISK_MUTATION",
                    "path": rel_p,
                    "detail": f"File {rel_p!r} was {ch['change_type']} on disk, but is completely omitted from the handover report.",
                })
        handover_lines = handover_md_text.splitlines()
        negation_markers = ("boundary:", "do not", "read-only", "never")
        for tracked_p in sorted(snap.files.keys()):
            if tracked_p not in changed_rel_set and tracked_p in handover_md_text:
                claimed_as_change = any(
                    (tracked_p in ln)
                    and not any(neg in ln.replace(tracked_p, "").lower() for neg in negation_markers)
                    for ln in handover_lines
                )
                if claimed_as_change:
                    handover_mismatches.append({
                        "code": "PHANTOM_HANDOVER_CLAIM",
                        "path": tracked_p,
                        "detail": f"Handover claims changes involving {tracked_p!r}, but its bytes on disk are 100% unchanged.",
                    })

    lawful = (len(boundary_breaches) == 0) and (len(handover_mismatches) == 0)
    return {
        "snapshot_id": snap.snapshot_id,
        "root_dir": snap.root_dir,
        "lawful": lawful,
        "verdict": "AIRLOCK_CLEAN" if lawful else "AIRLOCK_VIOLATION_DETECTED",
        "counts": {
            "unchanged_files": unchanged_count,
            "added_files": len(added),
            "modified_files": len(modified),
            "deleted_files": len(deleted),
            "authorized_changes": len(authorized_changes),
            "boundary_breaches": len(boundary_breaches),
            "handover_mismatches": len(handover_mismatches),
        },
        "authorized_changes": authorized_changes,
        "boundary_breaches": boundary_breaches,
        "handover_mismatches": handover_mismatches,
    }


def _check_path_safe_under_root(root: Path, rel_path: str) -> Tuple[bool, str]:
    """
    Verify using `os.lstat` that no parent directory and no existing target is a
    symlink, and that resolved paths remain strictly inside `root`.
    """
    root_resolved = root.resolve()
    parts = Path(rel_path).parts
    if not parts or ".." in parts:
        return False, "INVALID_REL_PATH"

    cur = root_resolved
    for idx, part in enumerate(parts):
        cur = cur / part
        is_last = idx == len(parts) - 1
        try:
            st = os.lstat(cur)
        except FileNotFoundError:
            if not is_last:
                continue
            break
        if stat.S_ISLNK(st.st_mode):
            return False, "SYMLINK_IN_PATH"
        if not is_last and not stat.S_ISDIR(st.st_mode):
            return False, "NON_DIR_PARENT"

    parent_resolved = (root_resolved / Path(rel_path).parent).resolve()
    if parent_resolved != root_resolved and root_resolved not in parent_resolved.parents:
        return False, "ESCAPES_ROOT"

    return True, "SAFE"


def _atomic_write_bytes_and_mode(target: Path, data: bytes, mode: int) -> None:
    fd, tmp_path = tempfile.mkstemp(dir=str(target.parent), prefix=".airlock_tmp_")
    try:
        with os.fdopen(fd, "wb") as fh:
            fh.write(data)
            fh.flush()
            os.fsync(fh.fileno())
        os.chmod(tmp_path, stat.S_IMODE(mode))
        os.replace(tmp_path, str(target))
    except Exception:
        if os.path.exists(tmp_path):
            os.unlink(tmp_path)
        raise


def rollback_airlock_snapshot(
    snap: AirlockSnapshot,
    remove_added_files: bool = True,
) -> Dict[str, Any]:
    """
    Restore the live directory on disk to the exact byte and mode state captured in `snap`.
    Refuses to unlink or write through symlinks (`os.lstat` on target and every parent).
    Verifies post-rollback SHA-256 digests on disk.
    """
    root = Path(snap.root_dir).resolve()
    current_files, _current_symlinks, _current_empty_dirs, _ = _scan_directory_state(
        root,
        max_total_bytes=10**12,
        store_content=False,
    )

    restored_files: List[str] = []
    removed_added: List[str] = []
    unrecoverable_files: List[str] = []

    # 1. Remove any newly added regular files not in the original snapshot
    if remove_added_files:
        for rel_p in sorted(set(current_files.keys()) - set(snap.files.keys())):
            safe, _reason = _check_path_safe_under_root(root, rel_p)
            if not safe:
                unrecoverable_files.append(rel_p)
                continue
            target = root / rel_p
            try:
                st = os.lstat(target)
                if stat.S_ISREG(st.st_mode):
                    target.unlink()
                    removed_added.append(rel_p)
            except FileNotFoundError:
                pass

    # 2. Restore modified or deleted files from compressed payload
    for rel_p, rec in sorted(snap.files.items()):
        safe, _reason = _check_path_safe_under_root(root, rel_p)
        if not safe:
            unrecoverable_files.append(rel_p)
            continue

        target = root / rel_p
        exists_reg = False
        cur_mode = 0
        try:
            st = os.lstat(target)
            if stat.S_ISLNK(st.st_mode):
                unrecoverable_files.append(rel_p)
                continue
            exists_reg = stat.S_ISREG(st.st_mode)
            cur_mode = stat.S_IMODE(st.st_mode)
        except FileNotFoundError:
            exists_reg = False

        bytes_changed = (not exists_reg) or (
            hashlib.sha256(target.read_bytes()).hexdigest() != rec.sha256
        )
        mode_changed = exists_reg and (cur_mode != rec.mode)

        if not bytes_changed and not mode_changed:
            continue

        if bytes_changed:
            if not rec.compressed_b64:
                unrecoverable_files.append(rel_p)
                continue
            raw_bytes = zlib.decompress(base64.b64decode(rec.compressed_b64.encode("ascii")))
            if hashlib.sha256(raw_bytes).hexdigest() != rec.sha256:
                unrecoverable_files.append(rel_p)
                continue
            target.parent.mkdir(parents=True, exist_ok=True)
            # Re-verify parent chain after mkdir
            safe_after, _ = _check_path_safe_under_root(root, rel_p)
            if not safe_after:
                unrecoverable_files.append(rel_p)
                continue
            _atomic_write_bytes_and_mode(target, raw_bytes, rec.mode)
            restored_files.append(rel_p)
        elif mode_changed:
            os.chmod(target, stat.S_IMODE(rec.mode))
            restored_files.append(rel_p)

    # 3. Restore snapshotted empty directories
    for rel_empty in sorted(snap.empty_dirs):
        safe, _ = _check_path_safe_under_root(root, rel_empty)
        if safe:
            (root / rel_empty).mkdir(parents=True, exist_ok=True)
        else:
            unrecoverable_files.append(rel_empty)

    # 4. Remove added empty directories that were not in the snapshot
    if remove_added_files:
        allowed_dirs: Set[str] = set(snap.empty_dirs)
        for p in list(snap.files.keys()) + list(snap.symlinks.keys()) + list(snap.empty_dirs):
            parent = Path(p).parent
            while str(parent) not in (".", ""):
                allowed_dirs.add(parent.as_posix())
                parent = parent.parent

        for dirpath, dirnames, filenames in os.walk(root, topdown=False, followlinks=False):
            cur = Path(dirpath)
            if cur == root:
                continue
            rel_d = cur.relative_to(root).as_posix()
            if any(part in DEFAULT_IGNORE_NAMES for part in Path(rel_d).parts):
                continue
            if rel_d not in allowed_dirs:
                safe, _ = _check_path_safe_under_root(root, rel_d)
                if safe and not any(cur.iterdir()):
                    cur.rmdir()

    # 5. Verify post-rollback state matches snapshot 100%
    post_check = verify_airlock_state(snap)
    exact_match = (
        post_check["counts"]["added_files"] == 0
        and post_check["counts"]["modified_files"] == 0
        and post_check["counts"]["deleted_files"] == 0
        and post_check["counts"]["boundary_breaches"] == 0
        and len(unrecoverable_files) == 0
    )

    return {
        "snapshot_id": snap.snapshot_id,
        "rollback_verified": exact_match,
        "restored_files": restored_files,
        "removed_untracked_files": removed_added,
        "unrecoverable_files": unrecoverable_files,
        "post_rollback_check": post_check,
    }


def run_airlock_self_test_demo() -> Dict[str, Any]:
    """
    Run a real filesystem demonstration in a temporary workspace.
    """
    with tempfile.TemporaryDirectory() as tdir:
        root = Path(tdir)
        (root / "src").mkdir()
        (root / "tests").mkdir()
        (root / "readonly_anchor").mkdir()

        (root / "src" / "app.py").write_text("def run():\n    return 'v1'\n", encoding="utf-8")
        (root / "tests" / "test_app.py").write_text("def test_run():\n    assert True\n", encoding="utf-8")
        (root / "readonly_anchor" / "PRIME.md").write_text("# CONSTITUTION — DO NOT EDIT\n", encoding="utf-8")

        snap = open_airlock_snapshot(
            root,
            allow_globs=["src/*", "tests/*"],
            forbid_globs=["readonly_anchor/*"],
            secret_key="mac-sovereign-key",
        )

        (root / "src" / "app.py").write_text("def run():\n    return 'v2'\n", encoding="utf-8")
        (root / "tests" / "test_app.py").write_text("def test_run():\n    assert 1 == 1\n", encoding="utf-8")
        (root / "readonly_anchor" / "PRIME.md").write_text("# TAMPERED CONSTITUTION\n", encoding="utf-8")
        (root / "src" / "rogue_temp.py").write_text("x = 1\n", encoding="utf-8")

        partial_handover = "# Handover\n- Modified `src/app.py` only.\n"
        audit_breach = verify_airlock_state(snap, handover_md_text=partial_handover)

        rollback_rep = rollback_airlock_snapshot(snap, remove_added_files=True)

    return {
        "demo": "FILE_AIRLOCK_LIVE_FILESYSTEM_CYCLE",
        "breach_audit": audit_breach,
        "rollback_report": rollback_rep,
        "all_verified": (
            audit_breach["lawful"] is False
            and audit_breach["counts"]["boundary_breaches"] == 1
            and audit_breach["counts"]["handover_mismatches"] >= 2
            and rollback_rep["rollback_verified"] is True
        ),
    }


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(
        prog="file-airlock",
        description="Lycheetah File Airlock — Real Filesystem Snapshot, Write-Scope Verifier & 1-Command Rollback",
    )
    sub = parser.add_subparsers(dest="cmd")

    p_open = sub.add_parser("open", help="Capture a pre-task filesystem snapshot & write-boundary lock")
    p_open.add_argument("dir", help="Target directory to snapshot")
    p_open.add_argument("--out", default=".airlock_snapshot.json", help="Output snapshot file path")
    p_open.add_argument("--allow", action="append", default=[], help="Allowed write glob (e.g. 'src/*')")
    p_open.add_argument("--forbid", action="append", default=[], help="Forbidden read-only glob (e.g. 'CAELORYNTH/*')")
    p_open.add_argument("--secret", default="", help="Optional human passphrase for HMAC seal")
    p_open.add_argument("--no-content", action="store_true", help="Do not store compressed file contents (disables rollback)")
    p_open.add_argument("--max-total-bytes", type=int, default=DEFAULT_MAX_TOTAL_BYTES, help="Maximum total bytes allowed in snapshot")
    p_open.add_argument("--json", action="store_true", help="Emit JSON output")

    p_check = sub.add_parser("check", help="Verify live disk changes against an Airlock snapshot & optional handover.md")
    p_check.add_argument("snapshot", help="Path to snapshot JSON file")
    p_check.add_argument("--handover", default="", help="Optional Markdown handover file to cross-check against disk")
    p_check.add_argument("--secret", default="", help="Optional human passphrase to verify HMAC seal")
    p_check.add_argument("--json", action="store_true", help="Emit JSON output")

    p_roll = sub.add_parser("rollback", help="Restore directory on disk to exact byte state in Airlock snapshot")
    p_roll.add_argument("snapshot", help="Path to snapshot JSON file")
    p_roll.add_argument("--secret", default="", help="Optional human passphrase to verify HMAC seal")
    p_roll.add_argument("--json", action="store_true", help="Emit JSON output")

    p_demo = sub.add_parser("demo", help="Run live temporary-directory snapshot, breach detection & rollback self-test")
    p_demo.add_argument("--json", action="store_true", help="Emit JSON output")

    args = parser.parse_args(argv)

    if args.cmd == "open":
        out_path = Path(args.out).resolve()
        snap = open_airlock_snapshot(
            Path(args.dir),
            allow_globs=args.allow or ["*"],
            forbid_globs=args.forbid or [],
            snapshot_out=out_path,
            secret_key=args.secret,
            store_content=not args.no_content,
            max_total_bytes=args.max_total_bytes,
        )
        res = {
            "snapshot_id": snap.snapshot_id,
            "root_dir": snap.root_dir,
            "snapshot_file": str(out_path),
            "files_captured": len(snap.files),
            "symlinks_captured": len(snap.symlinks),
            "empty_dirs_captured": len(snap.empty_dirs),
            "content_stored": snap.content_stored,
            "warnings": snap.warnings,
            "allow_globs": snap.allow_globs,
            "forbid_globs": snap.forbid_globs,
            "manifest_sha256": snap.manifest_sha256,
        }
        if args.json:
            print(json.dumps(res, indent=2))
        else:
            print(f"=== AIRLOCK SNAPSHOT OPENED: {snap.snapshot_id} ===")
            print(f"  Root Dir:        {snap.root_dir}")
            print(f"  Files Captured:  {len(snap.files)}")
            print(f"  Symlinks:        {len(snap.symlinks)}")
            print(f"  Allowed Globs:   {snap.allow_globs}")
            print(f"  Forbidden Globs: {snap.forbid_globs}")
            print(f"  Manifest SHA256: {snap.manifest_sha256}")
            print(f"  Saved To:        {out_path}")
            for w in snap.warnings:
                print(f"  [WARNING] {w}")
        return 0

    if args.cmd == "check":
        snap = load_snapshot_from_file(Path(args.snapshot), secret_key=args.secret)
        h_text = Path(args.handover).read_text(encoding="utf-8") if args.handover else None
        rep = verify_airlock_state(snap, handover_md_text=h_text)
        if args.json:
            print(json.dumps(rep, indent=2))
        else:
            print(f"=== AIRLOCK DISK VERIFICATION: {rep['verdict']} ===")
            c = rep["counts"]
            print(f"  Unchanged: {c['unchanged_files']} | Added: {c['added_files']} | Modified: {c['modified_files']} | Deleted: {c['deleted_files']}")
            print(f"  Authorized Changes: {c['authorized_changes']} | Boundary Breaches: {c['boundary_breaches']} | Handover Mismatches: {c['handover_mismatches']}")
            for b in rep["boundary_breaches"]:
                print(f"  [BREACH] {b['change_type']} {b['rel_path']} -> {b['policy_reason']}")
            for m in rep["handover_mismatches"]:
                print(f"  [MISMATCH] {m['code']}: {m['detail']}")
        return 0 if rep["lawful"] else 1

    if args.cmd == "rollback":
        snap = load_snapshot_from_file(Path(args.snapshot), secret_key=args.secret)
        rep = rollback_airlock_snapshot(snap)
        if args.json:
            print(json.dumps(rep, indent=2))
        else:
            print(f"=== AIRLOCK BYTE-EXACT ROLLBACK: verified={rep['rollback_verified']} ===")
            print(f"  Restored Files:          {rep['restored_files']}")
            print(f"  Removed Untracked Files: {rep['removed_untracked_files']}")
            if rep["unrecoverable_files"]:
                print(f"  [ERROR] Unrecoverable:   {rep['unrecoverable_files']}")
        return 0 if (rep["rollback_verified"] and len(rep["unrecoverable_files"]) == 0) else 1

    res = run_airlock_self_test_demo()
    if getattr(args, "json", False):
        print(json.dumps(res, indent=2))
    else:
        b = res["breach_audit"]
        r = res["rollback_report"]
        print("============================================================================")
        print("  🛡️ LYCHEETAH FILE AIRLOCK — SNAPSHOT, BOUNDARY DIFF & ROLLBACK DEMO")
        print(f"  Overall Self-Test Status: {'VERIFIED' if res['all_verified'] else 'FAILED'}")
        print("============================================================================")
        print(f"  1. Pre-Rollback Audit Verdict: {b['verdict']}")
        print(f"     • Authorized Changes:  {b['counts']['authorized_changes']}")
        print(f"     • Boundary Breaches:   {b['counts']['boundary_breaches']} ({b['boundary_breaches'][0]['rel_path']})")
        print(f"     • Handover Mismatches: {b['counts']['handover_mismatches']} undeclared disk changes caught")
        print(f"  2. Post-Rollback Verification: {r['rollback_verified']}")
        print(f"     • Restored Files:      {r['restored_files']}")
        print(f"     • Removed Untracked:   {r['removed_untracked_files']}")
    return 0 if res["all_verified"] else 1


if __name__ == "__main__":
    sys.exit(main())
