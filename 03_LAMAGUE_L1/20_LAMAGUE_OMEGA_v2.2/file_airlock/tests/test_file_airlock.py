#!/usr/bin/env python3
"""Gate-verified tests for file_airlock.py — Real Filesystem Snapshot, Boundary Diff & Rollback."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

SCRIPT_DIR = Path(__file__).resolve().parent.parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

import file_airlock as fa  # noqa: E402


def test_airlock_snapshot_save_load_and_hmac_tamper_rejection(tmp_path: Path):
    proj = tmp_path / "proj"
    proj.mkdir()
    (proj / "main.py").write_text("print('hello')\n", encoding="utf-8")

    snap_file = tmp_path / "snap.airlock.json"
    snap = fa.open_airlock_snapshot(
        proj,
        allow_globs=["*.py"],
        forbid_globs=["secret/*"],
        snapshot_out=snap_file,
        secret_key="mac-key-123",
    )
    assert snap_file.is_file()

    # Load with valid secret key
    loaded = fa.load_snapshot_from_file(snap_file, secret_key="mac-key-123")
    assert loaded.snapshot_id == snap.snapshot_id
    assert loaded.manifest_sha256 == snap.manifest_sha256

    # Reject wrong secret key
    with pytest.raises(ValueError, match="AIRLOCK_HMAC_INVALID"):
        fa.load_snapshot_from_file(snap_file, secret_key="wrong-key")

    # Planted tamper: mutate allow_globs in JSON on disk without updating manifest_sha256
    raw = json.loads(snap_file.read_text(encoding="utf-8"))
    raw["allow_globs"] = ["*"]
    snap_file.write_text(json.dumps(raw), encoding="utf-8")
    with pytest.raises(ValueError, match="AIRLOCK_MANIFEST_TAMPERED"):
        fa.load_snapshot_from_file(snap_file)


def test_airlock_catches_forbidden_boundary_undeclared_mutation_and_phantom_claim(tmp_path: Path):
    proj = tmp_path / "workspace"
    (proj / "src").mkdir(parents=True)
    (proj / "foreign_seat").mkdir(parents=True)

    (proj / "src" / "engine.py").write_text("x = 1\n", encoding="utf-8")
    (proj / "src" / "untouched.py").write_text("y = 2\n", encoding="utf-8")
    (proj / "foreign_seat" / "PRIME.md").write_text("# DO NOT TOUCH\n", encoding="utf-8")

    snap = fa.open_airlock_snapshot(
        proj,
        allow_globs=["src/*"],
        forbid_globs=["foreign_seat/*"],
    )

    # 1. Authorized & clean edit + truthful handover -> AIRLOCK_CLEAN
    (proj / "src" / "engine.py").write_text("x = 2\n", encoding="utf-8")
    honest_handover = "Updated `src/engine.py`."
    rep_clean = fa.verify_airlock_state(snap, handover_md_text=honest_handover)
    assert rep_clean["lawful"] is True
    assert rep_clean["verdict"] == "AIRLOCK_CLEAN"
    assert rep_clean["counts"]["authorized_changes"] == 1
    assert rep_clean["counts"]["boundary_breaches"] == 0
    assert rep_clean["counts"]["handover_mismatches"] == 0

    # 2. Forbidden edit to foreign_seat/PRIME.md + lying handover claiming src/untouched.py was edited
    (proj / "foreign_seat" / "PRIME.md").write_text("# BREACHED\n", encoding="utf-8")
    dishonest_handover = "Updated `src/untouched.py` only."
    rep_bad = fa.verify_airlock_state(snap, handover_md_text=dishonest_handover)
    assert rep_bad["lawful"] is False
    assert rep_bad["counts"]["boundary_breaches"] == 1
    assert rep_bad["boundary_breaches"][0]["rel_path"] == "foreign_seat/PRIME.md"

    mismatch_codes = {m["code"] for m in rep_bad["handover_mismatches"]}
    assert "UNDECLARED_DISK_MUTATION" in mismatch_codes
    assert "PHANTOM_HANDOVER_CLAIM" in mismatch_codes


def test_airlock_atomic_byte_exact_rollback_restores_modified_deleted_and_removes_added(tmp_path: Path):
    proj = tmp_path / "repo"
    proj.mkdir()
    f1 = proj / "keep.txt"
    f2 = proj / "delete_me.txt"
    f1.write_text("original keep content\n", encoding="utf-8")
    f2.write_text("do not lose me\n", encoding="utf-8")

    snap = fa.open_airlock_snapshot(proj)

    # Corrupt f1, delete f2, and add untracked rogue.txt
    f1.write_text("CORRUPTED\n", encoding="utf-8")
    f2.unlink()
    rogue = proj / "rogue.txt"
    rogue.write_text("untracked garbage\n", encoding="utf-8")

    roll = fa.rollback_airlock_snapshot(snap, remove_added_files=True)
    assert roll["rollback_verified"] is True
    assert sorted(roll["restored_files"]) == ["delete_me.txt", "keep.txt"]
    assert roll["removed_untracked_files"] == ["rogue.txt"]
    assert f1.read_text(encoding="utf-8") == "original keep content\n"
    assert f2.read_text(encoding="utf-8") == "do not lose me\n"
    assert not rogue.exists()


def test_airlock_cli_end_to_end(tmp_path: Path, capsys):
    rc = fa.main(["demo", "--json"])
    assert rc == 0
    out = json.loads(capsys.readouterr().out)
    assert out["all_verified"] is True


def test_item13_rollback_refuses_to_write_through_symlink_to_outside_file(tmp_path: Path):
    """Item 13: Swapping a tracked file for a symlink to an outside file must NOT overwrite outside file."""
    outside_file = tmp_path / "outside_victim.txt"
    outside_file.write_bytes(b"SACRED_OUTSIDE_BYTES_DO_NOT_OVERWRITE")

    root = tmp_path / "workspace"
    root.mkdir()
    tracked = root / "tracked.txt"
    tracked.write_bytes(b"original_workspace_bytes")

    snap_file = tmp_path / "snap.json"
    snap = fa.open_airlock_snapshot(root, snapshot_out=snap_file)

    # Replace tracked file with a symlink pointing outside root
    tracked.unlink()
    tracked.symlink_to(outside_file)

    roll = fa.rollback_airlock_snapshot(snap)
    # Must NOT overwrite outside_file!
    assert outside_file.read_bytes() == b"SACRED_OUTSIDE_BYTES_DO_NOT_OVERWRITE"
    assert "tracked.txt" in roll["unrecoverable_files"]
    assert roll["rollback_verified"] is False
    # CLI exit code must be nonzero
    rc = fa.main(["rollback", str(snap_file)])
    assert rc != 0


def test_item14_symlinks_recorded_and_detected_in_check(tmp_path: Path):
    """Item 14: Symlinks recorded with link target; added/changed/removed symlinks flagged in check."""
    root = tmp_path / "ws_sym"
    root.mkdir()
    (root / "real.txt").write_text("hello\n", encoding="utf-8")
    (root / "existing_link").symlink_to("real.txt")

    snap = fa.open_airlock_snapshot(root, allow_globs=["src/*"])
    assert "existing_link" in snap.symlinks
    assert snap.symlinks["existing_link"] == "real.txt"

    # Add a new unauthorized symlink and retarget existing symlink
    (root / "rogue_link").symlink_to("/etc/passwd")
    (root / "existing_link").unlink()
    (root / "existing_link").symlink_to("other.txt")

    rep = fa.verify_airlock_state(snap)
    assert rep["lawful"] is False
    breach_paths = {b["rel_path"] for b in rep["boundary_breaches"]}
    assert "rogue_link" in breach_paths
    assert "existing_link" in breach_paths


def test_item15_unrecoverable_file_warns_and_exits_nonzero(tmp_path: Path):
    """Item 15: store_content=False or missing content payload warns and exits nonzero on rollback."""
    root = tmp_path / "ws_nocontent"
    root.mkdir()
    f = root / "data.bin"
    f.write_bytes(b"important_bytes")

    snap_file = tmp_path / "snap.json"
    snap = fa.open_airlock_snapshot(root, snapshot_out=snap_file, store_content=False)
    assert getattr(snap, "content_stored", True) is False

    f.write_bytes(b"corrupted")
    rc = fa.main(["rollback", str(snap_file)])
    assert rc != 0


def test_item16_restores_file_mode_and_empty_dirs_and_removes_added_empty_dirs(tmp_path: Path):
    """Item 16: Restore file mode (S_IMODE) and empty dirs; remove added empty dirs."""
    import stat

    root = tmp_path / "ws_modes"
    root.mkdir()
    script = root / "run.sh"
    script.write_text("#!/bin/sh\necho ok\n", encoding="utf-8")
    script.chmod(0o755)
    empty_keep = root / "empty_keep_dir"
    empty_keep.mkdir()

    snap = fa.open_airlock_snapshot(root)

    # Change mode to 0600, delete empty_keep_dir, add rogue_empty_dir
    script.chmod(0o600)
    empty_keep.rmdir()
    rogue_dir = root / "rogue_empty_dir"
    rogue_dir.mkdir()

    roll = fa.rollback_airlock_snapshot(snap, remove_added_files=True)
    assert roll["rollback_verified"] is True
    assert stat.S_IMODE(script.stat().st_mode) == 0o755
    assert empty_keep.is_dir()
    assert not rogue_dir.exists()


def test_item17_snapshot_size_cap_fails_visibly(tmp_path: Path):
    """Item 17: Exceeding total snapshot byte cap fails visibly with ValueError."""
    root = tmp_path / "ws_cap"
    root.mkdir()
    (root / "big.bin").write_bytes(b"A" * 2048)

    with pytest.raises(ValueError, match="AIRLOCK_SNAPSHOT_SIZE_CAP_EXCEEDED"):
        fa.open_airlock_snapshot(root, max_total_bytes=1024)


def test_item18_unsigned_or_stripped_manifest_or_hmac_refused_on_empty_key(tmp_path: Path):
    """Item 18: Stripped manifest_sha256 or signed snapshot loaded with secret_key='' is REFUSED."""
    root = tmp_path / "ws_auth"
    root.mkdir()
    (root / "a.txt").write_text("hi\n", encoding="utf-8")

    snap_file = tmp_path / "snap.json"
    fa.open_airlock_snapshot(root, snapshot_out=snap_file, secret_key="mac-secret")

    # 1. Signed snapshot loaded with secret_key="" must be REFUSED
    with pytest.raises(ValueError, match="AIRLOCK_HMAC_REQUIRED"):
        fa.load_snapshot_from_file(snap_file, secret_key="")

    # 2. Snapshot with stripped/empty manifest_sha256 must be REFUSED even when secret_key=""
    raw = json.loads(snap_file.read_text(encoding="utf-8"))
    raw["manifest_sha256"] = ""
    raw["hmac_signature"] = ""
    snap_file.write_text(json.dumps(raw), encoding="utf-8")
    with pytest.raises(ValueError, match="AIRLOCK_MANIFEST_UNSIGNED_OR_TAMPERED"):
        fa.load_snapshot_from_file(snap_file, secret_key="")


def test_item19_no_hardcoded_guestpc_path_in_file_airlock():
    """Item 19: No hardcoded user home path in file_airlock.py."""
    src = Path(fa.__file__).read_text(encoding="utf-8")
    assert "/home/" + "guestpc" not in src

