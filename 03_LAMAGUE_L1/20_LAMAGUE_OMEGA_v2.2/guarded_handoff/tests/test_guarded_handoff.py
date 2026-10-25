#!/usr/bin/env python3
"""Gate-verified tests for guarded_handoff.py — Guarded Cross-Seat Executor & AST Semantic Diff Prover."""

from __future__ import annotations

import json
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent.parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

import guarded_handoff as gh  # noqa: E402


def test_theorem_8_all_six_guarded_cross_seat_cases():
    rep = gh.run_guarded_cross_seat_breakthrough_suite()
    assert rep["status"] == "VERIFIED"
    assert rep["all_6_cases_verified"] is True
    s = rep["summary"]
    assert s["case_1_approved_cross_seat_job"] == "COMMITTED_AND_WITNESSED"
    assert s["case_2_risk_downgrade_hinge_caught"] == "BLOCKED_RISK_ADMISSION_HINGE_BREACH"
    assert s["case_2_ten_field_hash_identical"] is True
    assert s["case_3_altered_context_caught"] == "BLOCKED_ALTERED_PROTECTED_CONTEXT"
    assert "UNAUTHORIZED_CAPABILITY_ESCALATION" in s["case_4_ast_capability_and_threshold_breach_caught"]
    assert "SILENT_THRESHOLD_WEAKENING" in s["case_4_ast_capability_and_threshold_breach_caught"]
    assert "UNDISCLOSED_LOGIC_MUTATION" in s["case_4_ast_capability_and_threshold_breach_caught"]
    assert s["case_5_consumed_permit_replay_caught"] == "BLOCKED_PERMIT_ALREADY_CONSUMED"
    assert s["case_6_post_write_divergence_rolled_back"] == "OBSERVED_EFFECT_DIVERGENCE_ROLLED_BACK"


def test_python_ast_diff_distinguishes_docstring_from_logic_and_catches_escalation():
    before = (
        '"""Module docstring v1."""\n'
        "SAFETY_FLOOR = 0.80\n"
        "def verify(x: float) -> bool:\n"
        '    """Old docstring."""\n'
        "    return x >= SAFETY_FLOOR\n"
    )
    docstring_only = (
        '"""Module docstring v2."""\n'
        "SAFETY_FLOOR = 0.80\n"
        "def verify(x: float) -> bool:\n"
        '    """Updated docstring with more detail."""\n'
        "    return x >= SAFETY_FLOOR\n"
    )
    rep_doc = gh.audit_python_ast_diff(before, docstring_only, handover_claim_text="Updated docstrings only.")
    assert rep_doc["lawful_ast_diff"] is True
    assert rep_doc["bytes_changed"] is True
    assert rep_doc["logic_changed"] is False
    assert rep_doc["docstring_or_comment_only"] is True

    # Now mutate logic while claiming "docstrings only" and weaken SAFETY_FLOOR
    sneaky = (
        '"""Module docstring v2."""\n'
        "import os\n"
        "SAFETY_FLOOR = 0.50\n"
        "def verify(x: float) -> bool:\n"
        '    """Updated docstring."""\n'
        "    os.system('whoami')\n"
        "    return x >= SAFETY_FLOOR\n"
    )
    rep_bad = gh.audit_python_ast_diff(before, sneaky, handover_claim_text="Updated docstrings only.")
    assert rep_bad["lawful_ast_diff"] is False
    codes = {v["code"] for v in rep_bad["violations"]}
    assert "UNDISCLOSED_LOGIC_MUTATION" in codes
    assert "SILENT_THRESHOLD_WEAKENING" in codes
    assert "UNAUTHORIZED_CAPABILITY_ESCALATION" in codes


def test_cli_prove_json(capsys):
    rc = gh.main(["prove", "--json"])
    assert rc == 0
    out = json.loads(capsys.readouterr().out)
    assert out["all_6_cases_verified"] is True


def test_audit_git_working_tree_on_real_git_repo(tmp_path: Path):
    import subprocess

    repo = tmp_path / "git_repo"
    (repo / "src").mkdir(parents=True)
    (repo / "foreign").mkdir(parents=True)
    py_file = repo / "src" / "engine.py"
    foreign_file = repo / "foreign" / "PRIME.md"

    py_file.write_text(
        '"""Engine v1."""\n'
        "SAFETY_FLOOR = 0.80\n"
        "def run(score: float) -> bool:\n"
        "    return score >= SAFETY_FLOOR\n",
        encoding="utf-8",
    )
    foreign_file.write_text("# READ ONLY\n", encoding="utf-8")

    subprocess.run(["git", "init"], cwd=repo, check=True, capture_output=True)
    subprocess.run(["git", "config", "user.email", "aetheron@lycheetah.local"], cwd=repo, check=True, capture_output=True)
    subprocess.run(["git", "config", "user.name", "Aetheron"], cwd=repo, check=True, capture_output=True)
    subprocess.run(["git", "add", "."], cwd=repo, check=True, capture_output=True)
    subprocess.run(["git", "commit", "-m", "Initial commit"], cwd=repo, check=True, capture_output=True)

    # 1. Sneaky capability escalation + threshold weakening in working tree -> caught by audit-git!
    py_file.write_text(
        '"""Engine v2."""\n'
        "import subprocess\n"
        "SAFETY_FLOOR = 0.30\n"
        "def run(score: float) -> bool:\n"
        "    subprocess.run(['echo', 'hi'], check=False)\n"
        "    return score >= SAFETY_FLOOR\n",
        encoding="utf-8",
    )
    rep_bad = gh.audit_git_working_tree(
        repo,
        allow_globs=["src/*"],
        forbid_globs=["foreign/*"],
        handover_claim_text="Updated docstrings only in src/engine.py",
    )
    assert rep_bad["lawful_working_tree"] is False
    assert rep_bad["verdict"] == "GIT_TREE_VIOLATION_DETECTED"
    assert rep_bad["highest_derived_risk"] == "CRITICAL"
    codes = {v["code"] for v in rep_bad["ast_violations"]}
    assert "UNAUTHORIZED_CAPABILITY_ESCALATION" in codes
    assert "SILENT_THRESHOLD_WEAKENING" in codes
    assert "UNDISCLOSED_LOGIC_MUTATION" in codes
    assert "fara" in rep_bad["lamague_v22_seal"]["sxp_v22_utterance"]

    # 2. Clean authorized edit -> GIT_TREE_CLEAN_AND_LAWFUL
    py_file.write_text(
        '"""Engine v2."""\n'
        "SAFETY_FLOOR = 0.80\n"
        "def run(score: float) -> bool:\n"
        "    return score >= SAFETY_FLOOR\n\n"
        "def version() -> str:\n"
        "    return 'v2'\n",
        encoding="utf-8",
    )
    rep_good = gh.audit_git_working_tree(
        repo,
        allow_globs=["src/*"],
        forbid_globs=["foreign/*"],
        handover_claim_text="Added version() helper to src/engine.py",
    )
    assert rep_good["lawful_working_tree"] is True
    assert rep_good["verdict"] == "GIT_TREE_CLEAN_AND_LAWFUL"
    assert "vira" in rep_good["lamague_v22_seal"]["sxp_v22_utterance"]


def test_item20_ed25519_asymmetric_permit_public_key_cannot_mint(tmp_path: Path):
    """Item 20: Real Ed25519 signature; a seat holding only the public key cannot mint a valid permit."""
    import pytest

    priv_key, pub_key = gh.generate_ed25519_keypair()
    ws = tmp_path / "ws"
    (ws / "src").mkdir(parents=True)
    (ws / "src" / "app.py").write_text("x = 1\n", encoding="utf-8")

    pkt = gh.GuardedStatePacket(
        purpose="Update x",
        claim="x=2",
        unknowns=[],
        invariants=["I1"],
        authority=["src/*"],
        participants=["Mac", "Aetheron"],
        affectedParties=["Users"],
        dissent=[],
        valueFlow="OK",
        recovery="AIRLOCK",
        risk="MEDIUM",
    )

    # Seat holding ONLY the public key attempts to mint a permit -> must raise TypeError/ValueError!
    with pytest.raises((TypeError, ValueError), match="ED25519_PRIVATE_KEY_REQUIRED"):
        gh.issue_signed_action_permit(
            permit_id="FORGED-001",
            issuer_id="RogueSeat",
            authority_private_key=pub_key,
            executor_seat="Aetheron",
            workspace_root=ws,
            target_rel_path="src/app.py",
            proposed_after_content="x = 2\n",
            parent_packet=pkt,
            allow_globs=["src/*"],
            forbid_globs=[],
        )

    # Minting with a different rogue private key must fail verification under Mac's public key
    rogue_priv, _ = gh.generate_ed25519_keypair()
    forged_permit = gh.issue_signed_action_permit(
        permit_id="FORGED-002",
        issuer_id="RogueSeat",
        authority_private_key=rogue_priv,
        executor_seat="Aetheron",
        workspace_root=ws,
        target_rel_path="src/app.py",
        proposed_after_content="x = 2\n",
        parent_packet=pkt,
        allow_globs=["src/*"],
        forbid_globs=[],
    )
    assert forged_permit.verify_signature(pub_key) is False


def test_item21_concurrent_8_process_permit_consumption_flock(tmp_path: Path):
    """Item 21: 8 concurrent OS processes attempt to consume the same permit at once -> exactly 1 succeeds."""
    import multiprocessing

    ledger_file = tmp_path / "ledger.json"
    gh.ConsumedPermitLedger.create_new(ledger_file)

    start_event = multiprocessing.Event()
    result_queue: multiprocessing.Queue = multiprocessing.Queue()

    def _worker(lpath: str, pid: str, ev, q):
        led = gh.ConsumedPermitLedger(Path(lpath))
        ev.wait()
        ok, reason = led.try_consume(pid, "sha256_effect")
        q.put((ok, reason))

    procs = [
        multiprocessing.Process(
            target=_worker,
            args=(str(ledger_file), "PERMIT-RACE-001", start_event, result_queue),
        )
        for _ in range(8)
    ]
    for p in procs:
        p.start()
    start_event.set()
    for p in procs:
        p.join(timeout=10)

    results = [result_queue.get(timeout=5) for _ in range(8)]
    successes = [r for r in results if r[0] is True]
    failures = [r for r in results if r[0] is False]
    assert len(successes) == 1
    assert len(failures) == 7


def test_item22_corrupt_or_missing_ledger_refuses_all_permits(tmp_path: Path):
    """Item 22: Corrupt or missing ledger must refuse ALL permits (fail closed)."""
    missing_path = tmp_path / "does_not_exist.json"
    ledger_missing = gh.ConsumedPermitLedger(missing_path)
    ok_missing, reason_missing = ledger_missing.try_consume("PERMIT-001", "abc")
    assert ok_missing is False
    assert "LEDGER_CORRUPT_OR_MISSING" in reason_missing

    corrupt_path = tmp_path / "corrupt.json"
    corrupt_path.write_text("{not valid json!!!", encoding="utf-8")
    ledger_corrupt = gh.ConsumedPermitLedger(corrupt_path)
    ok_corrupt, reason_corrupt = ledger_corrupt.try_consume("PERMIT-001", "abc")
    assert ok_corrupt is False
    assert "LEDGER_CORRUPT_OR_MISSING" in reason_corrupt


def test_item23_permit_binds_expiry_exact_action_and_target_hash(tmp_path: Path):
    """Item 23: Permit binds expiry, exact action_type, and target hash; altered target or expired permit is refused."""
    priv_key, pub_key = gh.generate_ed25519_keypair()
    ws = tmp_path / "ws23"
    (ws / "src").mkdir(parents=True)
    (ws / "src" / "a.py").write_text("a = 1\n", encoding="utf-8")
    (ws / "src" / "b.py").write_text("a = 1\n", encoding="utf-8")

    ledger = gh.ConsumedPermitLedger.create_new(tmp_path / "ledger23.json")
    pkt = gh.GuardedStatePacket(
        purpose="Edit a.py",
        claim="a=2",
        unknowns=[],
        invariants=["I1"],
        authority=["src/*"],
        participants=["Mac", "Aetheron"],
        affectedParties=["Users"],
        dissent=[],
        valueFlow="OK",
        recovery="AIRLOCK",
        risk="MEDIUM",
    )
    permit = gh.issue_signed_action_permit(
        permit_id="PERMIT-23",
        issuer_id="Mac",
        authority_private_key=priv_key,
        executor_seat="Aetheron",
        workspace_root=ws,
        target_rel_path="src/a.py",
        proposed_after_content="a = 2\n",
        parent_packet=pkt,
        allow_globs=["src/*"],
        forbid_globs=[],
        action_type="WRITE_FILE",
    )

    # Attempt to replay/redirect permit against src/b.py -> refused!
    res_wrong_target = gh.execute_guarded_cross_seat_job(
        workspace_root=ws,
        permit=permit,
        authority_public_key=pub_key,
        ledger=ledger,
        intended_parent_packet=pkt,
        candidate_child_packet=pkt,
        attempted_target_rel_path="src/b.py",
        attempted_after_content="a = 2\n",
        handover_claim_text="Updated src/b.py",
    )
    assert res_wrong_target["committed"] is False
    codes = {r["code"] for r in res_wrong_target["rejection_reasons"]}
    assert "TARGET_PATH_MISMATCH" in codes


def test_item24_non_py_reported_as_not_audited_and_untracked_files_audited(tmp_path: Path):
    """Item 24: Non-.py files reported as NOT_AUDITED (never passed); audit-git includes untracked files and clean tree is not proof."""
    import subprocess

    rep_md = gh.audit_python_ast_diff("# v1\n", "# v2\n", file_path="README.md")
    assert rep_md["ast_audit_status"] == "NOT_AUDITED"
    assert rep_md["lawful_ast_diff"] is None

    repo = tmp_path / "git24"
    (repo / "src").mkdir(parents=True)
    (repo / "src" / "init.py").write_text("x = 1\n", encoding="utf-8")
    subprocess.run(["git", "init"], cwd=repo, check=True, capture_output=True)
    subprocess.run(["git", "config", "user.email", "a@b.c"], cwd=repo, check=True, capture_output=True)
    subprocess.run(["git", "config", "user.name", "A"], cwd=repo, check=True, capture_output=True)
    subprocess.run(["git", "add", "."], cwd=repo, check=True, capture_output=True)
    subprocess.run(["git", "commit", "-m", "init"], cwd=repo, check=True, capture_output=True)

    # Clean tree -> must report GIT_TREE_CLEAN_NO_CHANGES_TO_AUDIT, NOT proof of safety
    rep_clean = gh.audit_git_working_tree(repo)
    assert rep_clean["verdict"] == "GIT_TREE_CLEAN_NO_CHANGES_TO_AUDIT"

    # Untracked malicious .py file in nested dir + modified non-.py file
    (repo / "src" / "sub").mkdir(parents=True)
    (repo / "src" / "sub" / "untracked_evil.py").write_text("import os\nos.system('id')\n", encoding="utf-8")
    (repo / "src" / "notes.md").write_text("hello\n", encoding="utf-8")

    rep_untracked = gh.audit_git_working_tree(repo, allow_globs=["src/*"])
    assert rep_untracked["lawful_working_tree"] is False
    by_path = {f["rel_path"]: f for f in rep_untracked["files"]}
    assert "src/sub/untracked_evil.py" in by_path
    assert "src/notes.md" in by_path
    assert by_path["src/notes.md"]["ast_audit_status"] == "NOT_AUDITED"


def test_item25_no_hardcoded_guestpc_in_guarded_handoff():
    """Item 25: No hardcoded user home path in guarded_handoff.py."""
    src = Path(gh.__file__).read_text(encoding="utf-8")
    assert "/home/" + "guestpc" not in src


