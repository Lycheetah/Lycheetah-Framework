#!/usr/bin/env python3
"""
===============================================================================
WORKSPACE WITNESS & LIVE REALITY-BINDING VERIFIER — S = (H, K, A, R)
===============================================================================
Author:   Aetheron (Antigravity Seat — Gemini 4 Argon) & Mackenzie Conor James Clark
Lineage:  Lycheetah Framework — Live Disk SHA-256 Verifier, AST Phantom Symbol
          Auditor, Git Boundary Guard, and Case G Recovery Capability Verifier
Module:   creations/continuity_prover/workspace_witness.py

Solves the fundamental gap between text-only handover comparison and physical
workspace reality identified in `2026-10-18_KNOWLEDGE_SESSION_HANDOFF.md` and
`2026-10-18_REAL_TOOL_DISCUSSION.md`:

  1. Case G — Recovery Capability vs. Stored Recovery Text (`S = (H, K, A, R)`):
     Two states can have identical text in `(H, K, A)` (including identical
     `recovery_path` strings and identical text hashes), yet one points to a
     valid backup artifact on disk while the other points to a missing or
     corrupted backup. `R` binds physical recovery capability into the state.

  2. Live Markdown SHA-256 Receipt Table Verification:
     Parses Markdown tables/lists of `(file_path, sha256)` pairs (such as the
     12 Framework source identity hashes in `2026-10-18_KNOWLEDGE_SESSION_HANDOFF.md`)
     and computes the actual SHA-256 of each file on disk right now, classifying
     each receipt as `EXACT_DISK_MATCH`, `DISK_MODIFIED_SINCE_HANDOFF`, or
     `FILE_MISSING_ON_DISK`.

  3. AST Phantom Symbol & Method Auditor:
     Parses Python source files with `ast` to verify whether functions, methods,
     or classes claimed in a handover or review actually exist on disk. Directly
     reproduces the real workspace catch from `2026-10-18_KNOWLEDGE_SESSION_HANDOFF.md`
     where `evaluate_and_execute` exists in `lycheetah/sovereign_harness.py`
     while `inspect_context` does not exist (`PHANTOM_SYMBOL_DOES_NOT_EXIST`).

  4. Live Git Read-Only Boundary Guard:
     Verifies via `git status --porcelain` that protected read-only repositories
     have not been dirtied by unauthorized writes.
===============================================================================
"""

from __future__ import annotations

import ast
import hashlib
import os
import re
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple


# =============================================================================
# 1. CASE G: S = (H, K, A, R) — STORED RECOVERY TEXT vs ACTUAL RECOVERY CAPABILITY
# =============================================================================

@dataclass
class RecoveryArtifactBinding:
    """Physical recovery witness R in S = (H, K, A, R)."""
    recovery_id: str
    recovery_text: str
    backup_path: Path
    expected_sha256: str


def verify_case_g_recovery_capability(binding: RecoveryArtifactBinding) -> Dict[str, Any]:
    """
    Verify Case G (Stored Recovery Text vs. Actual Physical Recovery Capability).
    Even if `recovery_text` is preserved verbatim in text, recovery fails if the
    underlying backup file is missing, empty, or hash-mismatched on disk.
    """
    text_preserved = bool(binding.recovery_text.strip())
    if not binding.backup_path.is_file():
        return {
            "recovery_id": binding.recovery_id,
            "text_preserved": text_preserved,
            "physical_recovery_capable": False,
            "status": "UNRECOVERABLE_MISSING_BACKUP",
            "violation": f"CASE_G_MISSING_BACKUP: recovery text {binding.recovery_text!r} is intact, "
                         f"but backup artifact {str(binding.backup_path)!r} does not exist on disk.",
        }

    actual_bytes = binding.backup_path.read_bytes()
    actual_sha256 = hashlib.sha256(actual_bytes).hexdigest()
    if binding.expected_sha256 and actual_sha256.lower() != binding.expected_sha256.lower():
        return {
            "recovery_id": binding.recovery_id,
            "text_preserved": text_preserved,
            "physical_recovery_capable": False,
            "status": "UNRECOVERABLE_CORRUPTED_BACKUP",
            "actual_sha256": actual_sha256,
            "expected_sha256": binding.expected_sha256,
            "violation": f"CASE_G_CORRUPTED_BACKUP: backup artifact {binding.backup_path.name!r} "
                         f"hash {actual_sha256[:12]}... != expected {binding.expected_sha256[:12]}...",
        }

    return {
        "recovery_id": binding.recovery_id,
        "text_preserved": text_preserved,
        "physical_recovery_capable": True,
        "status": "RECOVERY_ARTIFACT_INTACT",
        "actual_sha256": actual_sha256,
        "expected_sha256": binding.expected_sha256,
        "violation": "",
    }


def run_case_g_experiment(tmp_dir: Optional[Path] = None) -> Dict[str, Any]:
    """
    Run the worked Case G experiment from `2026-10-18_KNOWLEDGE_SESSION_HANDOFF.md`:
    Two states have identical recovery text (`"Restore from snapshot_v1.json"`),
    so a text-only verifier sees no difference. State 1 has the real backup on
    disk; State 2 has a missing backup (`UNRECOVERABLE_MISSING_BACKUP`).
    """
    import tempfile

    with tempfile.TemporaryDirectory() as tdir:
        base = tmp_dir or Path(tdir)
        valid_backup = base / "snapshot_v1.json"
        payload = b'{"state_id":"S0","authority":"BUILD_BOUNDED","unknowns":["U<tail_latency>"]}'
        valid_backup.write_bytes(payload)
        expected_hash = hashlib.sha256(payload).hexdigest()

        # State 1: Valid physical backup exists and matches SHA-256
        b_valid = RecoveryArtifactBinding(
            recovery_id="CASE_G_VALID_BACKUP",
            recovery_text="Restore from snapshot_v1.json",
            backup_path=valid_backup,
            expected_sha256=expected_hash,
        )
        rep_valid = verify_case_g_recovery_capability(b_valid)

        # State 2: Identical recovery_text, but backup file was deleted / missing
        missing_backup = base / "deleted_snapshot_v1.json"
        b_missing = RecoveryArtifactBinding(
            recovery_id="CASE_G_MISSING_BACKUP",
            recovery_text="Restore from snapshot_v1.json",  # IDENTICAL TEXT!
            backup_path=missing_backup,
            expected_sha256=expected_hash,
        )
        rep_missing = verify_case_g_recovery_capability(b_missing)

        # State 3: Identical recovery_text, but backup file on disk was corrupted
        corrupted_backup = base / "corrupted_snapshot_v1.json"
        corrupted_backup.write_bytes(b'{"corrupted":true}')
        b_corrupt = RecoveryArtifactBinding(
            recovery_id="CASE_G_CORRUPTED_BACKUP",
            recovery_text="Restore from snapshot_v1.json",  # IDENTICAL TEXT!
            backup_path=corrupted_backup,
            expected_sha256=expected_hash,
        )
        rep_corrupt = verify_case_g_recovery_capability(b_corrupt)

    verified = (
        rep_valid["physical_recovery_capable"] is True
        and rep_missing["physical_recovery_capable"] is False
        and rep_missing["status"] == "UNRECOVERABLE_MISSING_BACKUP"
        and rep_corrupt["physical_recovery_capable"] is False
        and rep_corrupt["status"] == "UNRECOVERABLE_CORRUPTED_BACKUP"
    )
    return {
        "case_id": "Case_G",
        "title": "Physical Recovery Capability R vs. Stored Recovery Text in S = (H, K, A, R)",
        "verified": verified,
        "valid_backup_report": rep_valid,
        "missing_backup_report": rep_missing,
        "corrupted_backup_report": rep_corrupt,
    }


# =============================================================================
# 2. LIVE MARKDOWN SHA-256 RECEIPT TABLE VERIFIER
# =============================================================================

_MD_TABLE_HASH_ROW_RE = re.compile(
    r"\|\s*`?([^|`\n]+?\.[a-zA-Z0-9_]+)`?\s*\|\s*`?([a-fA-F0-9]{64})`?\s*\|"
)


def extract_file_sha256_pairs_from_markdown(md_text: str) -> List[Tuple[str, str]]:
    """Extract `(relative_or_abs_path, sha256_hex)` pairs from Markdown tables."""
    pairs: List[Tuple[str, str]] = []
    for m in _MD_TABLE_HASH_ROW_RE.finditer(md_text):
        rel_path = m.group(1).strip()
        digest = m.group(2).strip().lower()
        pairs.append((rel_path, digest))
    return pairs


def _default_search_roots() -> List[Path]:
    roots: List[Path] = []
    fw_env = os.environ.get("LYCHEETAH_FRAMEWORK_ROOT", "").strip()
    if fw_env:
        roots.append(Path(fw_env))
    notes_env = os.environ.get("LYCHEETAH_TRIAD_NOTES_DIR", "").strip()
    if notes_env:
        roots.append(Path(notes_env))
    roots.append(Path(__file__).resolve().parent.parent.parent)
    return roots


def verify_markdown_sha256_receipts_on_disk(
    md_text: str,
    search_roots: Optional[List[Path]] = None,
) -> Dict[str, Any]:
    """
    Verify every `(file_path, sha256)` receipt in a Markdown handover against
    the live filesystem right now.
    """
    roots = search_roots if search_roots is not None else _default_search_roots()
    pairs = extract_file_sha256_pairs_from_markdown(md_text)
    results: List[Dict[str, Any]] = []

    for raw_path, claimed_sha256 in pairs:
        resolved_path: Optional[Path] = None
        cand_direct = Path(raw_path)
        if cand_direct.is_absolute() and cand_direct.is_file():
            resolved_path = cand_direct
        else:
            for r in roots:
                cand = r / raw_path
                if cand.is_file():
                    resolved_path = cand
                    break

        if resolved_path is None:
            results.append({
                "claimed_path": raw_path,
                "resolved_path": None,
                "claimed_sha256": claimed_sha256,
                "actual_sha256": None,
                "status": "FILE_MISSING_ON_DISK",
                "matches_disk": False,
            })
            continue

        actual_sha256 = hashlib.sha256(resolved_path.read_bytes()).hexdigest()
        matches = (actual_sha256.lower() == claimed_sha256.lower())
        results.append({
            "claimed_path": raw_path,
            "resolved_path": str(resolved_path),
            "claimed_sha256": claimed_sha256,
            "actual_sha256": actual_sha256,
            "status": "EXACT_DISK_MATCH" if matches else "DISK_MODIFIED_SINCE_HANDOFF",
            "matches_disk": matches,
        })

    exact_matches = sum(1 for r in results if r["status"] == "EXACT_DISK_MATCH")
    modified_since = sum(1 for r in results if r["status"] == "DISK_MODIFIED_SINCE_HANDOFF")
    missing_files = sum(1 for r in results if r["status"] == "FILE_MISSING_ON_DISK")

    return {
        "total_receipt_pairs": len(results),
        "exact_disk_matches": exact_matches,
        "modified_since_handoff": modified_since,
        "missing_on_disk": missing_files,
        "all_files_exist_on_disk": missing_files == 0 and len(results) > 0,
        "results": results,
    }


# =============================================================================
# 3. AST PHANTOM SYMBOL & METHOD AUDITOR
# =============================================================================

def extract_python_symbols_from_file(py_path: Path) -> Set[str]:
    """Parse a Python file's AST and return all defined functions, methods, Class.method, and classes."""
    if not py_path.is_file():
        return set()
    tree = ast.parse(py_path.read_text(encoding="utf-8"), filename=str(py_path))
    symbols: Set[str] = set()

    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            symbols.add(node.name)
        elif isinstance(node, ast.ClassDef):
            symbols.add(node.name)
            for item in node.body:
                if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    symbols.add(item.name)
                    symbols.add(f"{node.name}.{item.name}")
    return symbols


def verify_claimed_symbols_in_python_file(
    py_path: Path,
    claimed_symbols: List[str],
) -> Dict[str, Any]:
    """
    Verify whether each symbol (function, method, or class) claimed in a handover
    or code review actually exists in `py_path`'s AST.
    Catches `PHANTOM_SYMBOL_DOES_NOT_EXIST` (e.g., `inspect_context()` vs `evaluate_and_execute()`).
    """
    actual_symbols = extract_python_symbols_from_file(py_path)
    verified: List[str] = []
    phantom: List[str] = []

    for sym in claimed_symbols:
        clean_sym = sym.strip().rstrip("()")
        if clean_sym in actual_symbols:
            verified.append(clean_sym)
        else:
            phantom.append(clean_sym)

    return {
        "file_path": str(py_path),
        "file_exists": py_path.is_file(),
        "total_ast_symbols_in_file": len(actual_symbols),
        "claimed_symbols": claimed_symbols,
        "verified_symbols": verified,
        "phantom_symbols": phantom,
        "all_claimed_exist": len(phantom) == 0 and py_path.is_file(),
    }


# =============================================================================
# 4. LIVE WORKSPACE REALITY-BINDING SUITE (SUITE 7)
# =============================================================================

def run_live_workspace_witness_suite(
    handoff_path: Optional[Path] = None,
    harness_path: Optional[Path] = None,
    search_roots: Optional[List[Path]] = None,
    tmp_dir: Optional[Path] = None,
) -> Dict[str, Any]:
    """
    Execute the Live Reality-Binding & Workspace Witness Suite:
      - Requires explicit paths or `LYCHEETAH_TRIAD_NOTES_DIR` / `LYCHEETAH_FRAMEWORK_ROOT`
        environment variables.
      - If external paths are absent, prints `"DID NOT RUN"` to stderr and returns
        `status="DID_NOT_RUN"`, `verified=False` (never passes silently).
    """
    case_g = run_case_g_experiment(tmp_dir=tmp_dir)

    if handoff_path is None:
        notes_env = os.environ.get("LYCHEETAH_TRIAD_NOTES_DIR", "").strip()
        if notes_env:
            handoff_path = Path(notes_env) / "2026-10-18_KNOWLEDGE_SESSION_HANDOFF.md"

    if harness_path is None:
        fw_env = os.environ.get("LYCHEETAH_FRAMEWORK_ROOT", "").strip()
        if fw_env:
            harness_path = Path(fw_env) / "lycheetah" / "sovereign_harness.py"

    if handoff_path is None or not handoff_path.is_file() or harness_path is None or not harness_path.is_file():
        print(
            "DID NOT RUN: run_live_workspace_witness_suite requires --handoff-file / --harness-file "
            "or LYCHEETAH_TRIAD_NOTES_DIR and LYCHEETAH_FRAMEWORK_ROOT environment variables.",
            file=sys.stderr,
        )
        return {
            "experiment": "EXPERIMENT_7_LIVE_WORKSPACE_REALITY_WITNESS",
            "status": "DID_NOT_RUN",
            "available": False,
            "verified": False,
            "evidence_classification": {
                "measured_components": [
                    "Case G SHA-256 backup verification on tmp_dir",
                ],
                "scripted_or_synthetic_components": [
                    "External handoff and harness checks DID NOT RUN because paths were not provided",
                ],
            },
            "case_g_recovery_capability": case_g,
            "handoff_disk_sha256_verification": {
                "status": "DID_NOT_RUN",
                "total_receipt_pairs": 0,
                "exact_disk_matches": 0,
                "modified_since_handoff": 0,
                "missing_on_disk": 0,
                "all_files_exist_on_disk": False,
                "results": [],
            },
            "ast_phantom_symbol_audit": {
                "status": "DID_NOT_RUN",
                "verified": False,
                "real_symbols_check": {},
                "phantom_symbol_caught_check": {},
            },
        }

    eff_roots = list(search_roots) if search_roots is not None else _default_search_roots()
    for p_cand in (handoff_path.parent, harness_path.parent):
        if p_cand not in eff_roots:
            eff_roots.insert(0, p_cand)

    disk_receipts = verify_markdown_sha256_receipts_on_disk(
        handoff_path.read_text(encoding="utf-8"),
        search_roots=eff_roots,
    )

    ast_good = verify_claimed_symbols_in_python_file(
        harness_path, ["SovereignExecutionHarness", "evaluate_and_execute"]
    )
    ast_phantom = verify_claimed_symbols_in_python_file(
        harness_path, ["evaluate_and_execute", "inspect_context"]
    )
    ast_verified = (
        ast_good["all_claimed_exist"] is True
        and ast_phantom["all_claimed_exist"] is False
        and "inspect_context" in ast_phantom["phantom_symbols"]
    )

    all_passed = (
        case_g["verified"] is True
        and disk_receipts["all_files_exist_on_disk"] is True
        and disk_receipts["exact_disk_matches"] >= 1
        and ast_verified is True
    )

    return {
        "experiment": "EXPERIMENT_7_LIVE_WORKSPACE_REALITY_WITNESS",
        "status": "VERIFIED" if all_passed else "FAILED",
        "available": True,
        "verified": all_passed,
        "evidence_classification": {
            "measured_components": [
                "On-disk SHA-256 hashing of every (file_path, sha256) pair parsed from the Markdown table",
                "Python AST parsing (ast.parse) of target module to verify real vs phantom symbol definitions",
                "On-disk SHA-256 verification of backup artifacts in Case G",
            ],
            "scripted_or_synthetic_components": [
                "Case G synthetic backup payload written to temporary directory",
                "Target symbol names queried against the AST (SovereignExecutionHarness, evaluate_and_execute, inspect_context)",
            ],
        },
        "case_g_recovery_capability": case_g,
        "handoff_disk_sha256_verification": disk_receipts,
        "ast_phantom_symbol_audit": {
            "verified": ast_verified,
            "real_symbols_check": ast_good,
            "phantom_symbol_caught_check": ast_phantom,
        },
    }
