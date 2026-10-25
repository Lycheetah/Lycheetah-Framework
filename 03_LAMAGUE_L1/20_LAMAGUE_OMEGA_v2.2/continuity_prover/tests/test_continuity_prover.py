#!/usr/bin/env python3
"""Gate-verified tests for continuity_prover.py — Compression, Handover & Long-Horizon Prover."""

from __future__ import annotations

import copy
import json
import sys
from pathlib import Path

import pytest

SCRIPT_DIR = Path(__file__).resolve().parent.parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

import continuity_prover as cp  # noqa: E402


# =============================================================================
# 1. CONTINUITY CAPSULE & BREATHING COMPRESSION GATE (THEOREM 1)
# =============================================================================

def test_canonical_seed_capsule_hashes_are_deterministic():
    c1 = cp.make_canonical_seed_capsule()
    c2 = cp.make_canonical_seed_capsule()
    assert c1.critical_hash() == c2.critical_hash()
    assert c1.semantic_hash() == c2.semantic_hash()
    assert len(c1.critical_hash()) == 64
    assert len(c1.semantic_hash()) == 64


def test_breathing_gate_allows_safe_low_risk_and_forces_expand_on_high_risk():
    seed = cp.make_canonical_seed_capsule()
    gate_safe = cp.evaluate_breathing_gate(seed)
    assert gate_safe.allowed_to_compress is True
    assert gate_safe.mode == "COMPRESS (Z_down)"

    high_risk = copy.deepcopy(seed)
    high_risk.risk_level = "high"
    high_risk.irreversible = True
    gate_unsafe = cp.evaluate_breathing_gate(high_risk)
    assert gate_unsafe.allowed_to_compress is False
    assert gate_unsafe.mode == "EXPAND (Z_up)"
    assert len(gate_unsafe.reasons) >= 2


def test_z_down_and_z_up_exact_round_trip_and_tamper_rejection():
    seed = cp.make_canonical_seed_capsule()
    wire = cp.compress_z_down(seed)
    restored = cp.expand_z_up(wire)
    assert restored.critical_hash() == seed.critical_hash()
    assert restored.semantic_hash() == seed.semantic_hash()
    assert restored.unknowns == seed.unknowns
    assert restored.authority_scope == seed.authority_scope
    assert restored.dissent == seed.dissent

    # Planted failure: tamper with wire's authority_scope without updating critical_hash
    tampered_wire = copy.deepcopy(wire)
    tampered_wire["critical_spine"]["authority_scope"] = "UNRESTRICTED_ROOT"
    with pytest.raises(ValueError, match="CRITICAL HASH MISMATCH"):
        cp.expand_z_up(tampered_wire)


def test_item8_compression_relabelled_as_scripted_simulation_and_seal_not_standalone_compression(tmp_path):
    """Item 8: Relabel Theorem 1 as 'Illustrative simulation · scripted baseline', remove 32.34x,
    prove seal_sequence alone cannot round-trip to full capsule, and measure blind compaction on tmp_path docs."""
    res = cp.run_compression_survival_experiment(cycles=10)
    assert res["baseline_type"] == "Illustrative simulation · scripted baseline"
    assert "surface_seal_compression_factor" not in res
    assert res["seal_sequence_is_standalone_compression"] is False

    # Trying to decode seal_sequence alone without critical_spine sidecar cannot reconstruct capsule fields
    seed = cp.make_canonical_seed_capsule()
    seal_only = cp.decode_seal_sequence_only(seed.seal_sequence)
    assert seal_only["can_reconstruct_full_capsule_without_sidecar"] is False
    assert "purpose" in seal_only["missing_critical_fields"]
    assert "unknowns" in seal_only["missing_critical_fields"]
    assert "authority_scope" in seal_only["missing_critical_fields"]

    # Empirical blind extraction on tmp_path handover docs
    doc_path = tmp_path / "handover_1.md"
    doc_md = (
        "# Vault Migration Handover\n"
        "- Risk_Level: `HIGH`\n"
        "- Boundary: Do not push to remote repository; read-only foreign seats.\n"
        "- Open Question: `U<p99_tail_latency>` did not run on hardware.\n"
        "- Receipt: SHA-256 `4fa7c7399dddc5d9eb442d1a0bb94736c82112a988cf3920b983b1c037cfbe51`, 11/11 tests passed.\n"
        "- Dissent: Sol disagrees with live dual-write.\n"
    )
    doc_path.write_text(doc_md, encoding="utf-8")
    summary_lossy = "# Summary\nMigration is progressing smoothly. All checks look good.\n"
    import real_text_continuity as rtc
    summary_guarded = rtc.compact_markdown_with_vita8_guard(doc_md, source_name="handover_1.md")

    blind_eval = cp.measure_blind_markdown_compaction_retention([
        {"doc_id": "doc1", "original_md": doc_md, "candidate_summary_md": summary_lossy, "label": "unstructured_summary"},
        {"doc_id": "doc1_vita8", "original_md": doc_md, "candidate_summary_md": summary_guarded, "label": "vita8_guarded"},
    ])
    assert blind_eval["evidence_type"] == "MEASURED_BLIND_MARKDOWN_EXTRACTION"
    assert blind_eval["results"][0]["overall_field_retention_rate"] == 0.0
    assert blind_eval["results"][1]["overall_field_retention_rate"] == 1.0


def test_item9_factorial_relabelled_as_toy_model_wired_by_construction():
    """Item 9: Relabel Theorem 3 as toy model wired by construction, drop 'main_effects',
    and state that each factor is wired to its own metric with zero interaction."""
    res = cp.run_2k_factorial_long_horizon_experiment(steps=50)
    assert "main_effects" not in res
    assert res["model_type"] == "Illustrative toy model · wired by construction"
    assert res["interaction_effects_all_zero"] is True
    assert "wired to its own metric" in res["architecture_note"]
    wb = res["wired_factor_bindings"]
    assert wb["Factor_A_Capsule_Lock"]["wired_target_metrics"] == [
        "authority_intact", "active_refusals_intact", "protected_dissent_intact", "unverified_unknown_preserved"
    ]
    assert wb["Factor_B_TRIAD_GreyMode"]["wired_target_metrics"] == ["final_drift"]
    assert wb["Factor_C_Glass_CASCADE"]["wired_target_metrics"] == ["glass_fraction"]


def test_item10_seeded_random_capsule_mutation_fuzzer_1000_mutations():
    """Item 10: Seeded random mutation fuzzing of capsule fields (>= 1000 mutations).
    Every mutation must be caught or explicitly classified as lawful."""
    fuzz = cp.run_seeded_capsule_mutation_fuzzer(num_mutations=1000, seed=20261025)
    assert fuzz["total_mutations"] == 1000
    assert fuzz["unclassified_or_missed"] == 0
    assert fuzz["unlawful_mutations_caught"] + fuzz["lawful_extensions_classified"] == 1000
    assert fuzz["unlawful_mutations_caught"] >= 700
    assert fuzz["lawful_extensions_classified"] >= 100


def test_item11_missing_paths_report_did_not_run_and_exit_nonzero(tmp_path, monkeypatch, capsys):
    """Item 11: When benchmark/notes/witness paths are absent, print 'DID NOT RUN',
    return available=False and all_matched=False (never pass), and exit nonzero on CLI."""
    monkeypatch.delenv("LYCHEETAH_FRAMEWORK_ROOT", raising=False)
    monkeypatch.delenv("LYCHEETAH_TRIAD_NOTES_DIR", raising=False)

    missing_dir = tmp_path / "nonexistent_dir"
    res_v03 = cp.run_framework_v03_benchmark_verification(benchmark_dir=missing_dir)
    assert res_v03["available"] is False
    assert res_v03["status"] == "DID_NOT_RUN"
    assert res_v03["all_matched"] is False

    import real_text_continuity as rtc
    res_notes = rtc.audit_real_workspace_handovers(notes_dir=missing_dir)
    assert res_notes["available"] is False
    assert res_notes["status"] == "DID_NOT_RUN"
    assert res_notes["all_guarded_passed"] is False

    import workspace_witness as ww
    res_ww = ww.run_live_workspace_witness_suite(
        handoff_path=missing_dir / "missing.md",
        harness_path=missing_dir / "missing.py",
        tmp_dir=tmp_path,
    )
    assert res_ww["verified"] is False
    assert res_ww["status"] == "DID_NOT_RUN"

    rc = cp.main(["real-handovers", "--notes-dir", str(missing_dir)])
    captured = capsys.readouterr()
    assert rc != 0
    assert "DID NOT RUN" in (captured.out + captured.err)


def test_item12_and_25_measured_vs_scripted_labels_and_no_guestpc_paths():
    """Items 12 & 25: Every check states what is measured vs scripted, no 'PROVEN' where scripted,
    and zero hardcoded user home paths across continuity_prover, real_text_continuity, workspace_witness."""
    base = Path(__file__).resolve().parent.parent
    forbidden_prefix = "/" + "home/" + "guestpc"
    for fname in ("continuity_prover.py", "real_text_continuity.py", "workspace_witness.py"):
        src = (base / fname).read_text(encoding="utf-8")
        assert forbidden_prefix not in src, f"Found hardcoded user home path in {fname}"

    import real_text_continuity as rtc
    af = rtc.verify_preservation_cases_a_through_f()
    assert "evidence_classification" in af
    assert "measured_components" in af["evidence_classification"]
    assert "scripted_or_synthetic_components" in af["evidence_classification"]



# =============================================================================
# 2. CROSS-MODEL HANDOVER & ADVERSARIAL TAMPER MATRIX (THEOREM 2)
# =============================================================================

def test_handover_exact_continuation_and_evidence_backed_descendant():
    seed = cp.make_canonical_seed_capsule()
    child = copy.deepcopy(seed)
    child.seat_id = "Caelorynth"
    child.parent_semantic_hash = seed.semantic_hash()
    rep_cont = cp.verify_handover_transition(seed, child)
    assert rep_cont["lawful_handover"] is True
    assert rep_cont["classification"] == "EXACT_CONTINUATION"
    assert rep_cont["unsafe_losses"] == []

    # Resolve one unknown WITH an explicit Evidence Certificate
    desc = copy.deepcopy(child)
    desc.seat_id = "Aetheron"
    desc.parent_semantic_hash = child.semantic_hash()
    desc.unknowns = ["U<offline_sync_conflict_rate>"]
    desc.evidence_certificates["U<p99_tail_latency_under_load>"] = "EVIDENCE-01: p99=4.1ms"
    rep_desc = cp.verify_handover_transition(child, desc)
    assert rep_desc["lawful_handover"] is True
    assert rep_desc["classification"] == "VERIFIED_DESCENDANT"
    assert rep_desc["verified_resolved_unknowns"] == ["U<p99_tail_latency_under_load>"]
    assert rep_desc["unsafe_losses"] == []


def test_handover_catches_planted_silent_unknown_erasure_and_authority_escalation():
    seed = cp.make_canonical_seed_capsule()

    # Planted tamper 1: drop unknown without evidence certificate
    bad_unk = copy.deepcopy(seed)
    bad_unk.parent_semantic_hash = seed.semantic_hash()
    bad_unk.unknowns = []
    rep_unk = cp.verify_handover_transition(seed, bad_unk)
    assert rep_unk["lawful_handover"] is False
    assert rep_unk["classification"] == "IMPOSTOR"
    assert len(rep_unk["unverified_resolved_unknowns"]) == 2

    # Planted tamper 2: escalate authority scope
    bad_auth = copy.deepcopy(seed)
    bad_auth.parent_semantic_hash = seed.semantic_hash()
    bad_auth.authority_scope = "PUBLISH_WITHOUT_APPROVAL"
    rep_auth = cp.verify_handover_transition(seed, bad_auth)
    assert rep_auth["lawful_handover"] is False
    assert rep_auth["classification"] == "UNSAFE_COLLAPSE"
    assert any("authority_scope_mutated" in x for x in rep_auth["unsafe_losses"])


def test_full_11_scenario_handover_tamper_matrix_zero_false_negatives():
    res = cp.run_handover_tamper_matrix()
    assert res["total_scenarios"] == 11
    assert res["lawful_scenarios_passed"] == 3
    assert res["tamper_vectors_caught"] == 8
    assert res["false_negatives"] == 0
    assert res["false_positives"] == 0
    assert res["all_assertions_verified"] is True


# =============================================================================
# 3. 50-STEP LONG-RUNNING TASK & 2^3 TOY MODEL (SIMULATION 3)
# =============================================================================

def test_2k_factorial_long_horizon_all_8_cells_and_main_effects():
    res = cp.run_2k_factorial_long_horizon_experiment(steps=50)
    assert len(res["all_8_cells"]) == 8

    open_loop = res["baseline_open_loop_000"]
    full_stack = res["full_lycheetah_stack_111"]

    # Open loop fails on authority, unknowns, drift, and glass vitrification
    assert open_loop["authority_intact"] is False
    assert open_loop["unverified_unknown_preserved"] is False
    assert open_loop["glass_fraction"] == 1.0
    assert open_loop["continuity_index"] < 0.15

    # Full Lycheetah stack (1,1,1) preserves authority, unknowns, dissent, zero glass, low drift
    assert full_stack["authority_intact"] is True
    assert full_stack["active_refusals_intact"] is True
    assert full_stack["protected_dissent_intact"] is True
    assert full_stack["unverified_unknown_preserved"] is True
    assert full_stack["fabricated_certainties_count"] == 0
    assert full_stack["glass_fraction"] == 0.0
    assert full_stack["final_drift"] < 0.05
    assert full_stack["continuity_index"] >= 0.98

    # Check wired factor bindings for all 3 factors
    wb = res["wired_factor_bindings"]
    assert wb["Factor_A_Capsule_Lock"]["wired_continuity_index_weight"] > 0.60
    assert wb["Factor_B_TRIAD_GreyMode"]["delta_final_drift"] < -0.20
    assert wb["Factor_C_Glass_CASCADE"]["delta_glass_fraction"] == -1.0


def _create_tmp_continuity_fixtures(tmp_path: Path):
    """Create self-contained v0.3 benchmark, markdown handovers, and witness fixtures in tmp_path."""
    bench_dir = tmp_path / "benchmark"
    sample_dir = bench_dir / "sample_packets"
    sample_dir.mkdir(parents=True, exist_ok=True)

    ref_pkt = {
        "case_id": "CASE-01",
        "decoder_id": "REF",
        "purpose": "Preserve continuity across seats",
        "invariants": ["no_silent_unknown_erasure", "human_primacy"],
        "unknowns": ["U<tail_latency>"],
        "authority": ["BUILD_BOUNDED"],
        "participants": ["Mac", "Aetheron"],
        "affected_parties": ["Mac", "Operators"],
        "dissent": [{"parties": ["Sol"], "positions": {"Sol": "audit_first"}, "status": "UNRESOLVED"}],
        "value_ledger": [{"declared": True, "consent": True, "amount": 0.0}],
        "claim": "Safe reference packet",
        "operation_path": ["O", "E", "U", "P", "Y"],
        "consequence_horizon": "H2",
        "recovery": ["COR"],
    }
    pack_data = {
        "cases": [
            {
                "case_id": "CASE-01",
                "source_expression": "O -> E -> U -> P -> Y",
                "reference_packet": ref_pkt,
            }
        ]
    }
    (bench_dir / "challenge_pack.json").write_text(json.dumps(pack_data), encoding="utf-8")

    safe_pkt = dict(ref_pkt, decoder_id="DEC_SAFE")
    unsafe_pkt = dict(ref_pkt, decoder_id="DEC_UNSAFE", unknowns=[])
    (sample_dir / "01_SAFE.json").write_text(json.dumps(safe_pkt), encoding="utf-8")
    (sample_dir / "02_UNSAFE.json").write_text(json.dumps(unsafe_pkt), encoding="utf-8")

    notes_dir = tmp_path / "notes"
    notes_dir.mkdir(parents=True, exist_ok=True)
    harness_py = tmp_path / "sovereign_harness.py"
    harness_bytes = (
        b"class SovereignExecutionHarness:\n"
        b"    def evaluate_and_execute(self):\n"
        b"        return True\n"
    )
    harness_py.write_bytes(harness_bytes)
    import hashlib
    harness_sha = hashlib.sha256(harness_bytes).hexdigest()

    handoff_md = (
        "# Session Handover — Continuity Audit\n\n"
        "- Risk_Level: `HIGH`\n"
        "- Boundary: Do not edit foreign seat surfaces (read-only boundary).\n"
        "- Status: Runtime checks did not run (`U<hardware_witness>`).\n"
        f"- Receipt: SHA-256 `{harness_sha}`, 11/11 tests passed.\n"
        "- Dissent: Seat_A and Seat_B disagree on immediate cutover.\n"
        "- Horizon: Considered Option A and Option B.\n\n"
        "| File | SHA-256 |\n"
        "| --- | --- |\n"
        f"| `{harness_py.name}` | `{harness_sha}` |\n"
    )
    handoff_file = notes_dir / "2026-10-18_KNOWLEDGE_SESSION_HANDOFF.md"
    handoff_file.write_text(handoff_md, encoding="utf-8")

    return bench_dir, notes_dir, handoff_file, harness_py


def test_full_continuity_proof_suite_and_cli_json(tmp_path, capsys):
    bench_dir, notes_dir, handoff_file, harness_py = _create_tmp_continuity_fixtures(tmp_path)
    cert = cp.run_full_continuity_proof_suite(
        benchmark_dir=bench_dir,
        notes_dir=notes_dir,
        handoff_path=handoff_file,
        harness_path=harness_py,
        search_roots=[tmp_path],
        tmp_dir=tmp_path,
    )
    assert cert["status"] == "VERIFIED"
    assert cert["all_checks_verified"] is True

    # Without external args or env vars, CLI prove reports DID_NOT_RUN and exits nonzero
    rc = cp.main(["prove", "--json"])
    assert rc == 1
    out_cert = json.loads(capsys.readouterr().out)
    assert out_cert["status"] == "DID_NOT_RUN"


def test_framework_v03_benchmark_challenge_pack_verification(tmp_path):
    bench_dir, _, _, _ = _create_tmp_continuity_fixtures(tmp_path)
    res = cp.run_framework_v03_benchmark_verification(benchmark_dir=bench_dir)
    assert res["available"] is True
    assert res["status"] == "VERIFIED"
    assert res["cases_verified"] == 1
    assert res["packets_verified"] == 2
    assert res["safe_packets_passed"] == 1
    assert res["unsafe_packets_caught"] == 1
    assert res["all_matched"] is True


# =============================================================================
# 4. CASES A-F PRESERVATION LAWS & REAL-TEXT MARKDOWN HANDOVER AUDITOR
# =============================================================================

def test_preservation_cases_a_through_f_lawful_and_false_positives_caught():
    import real_text_continuity as rtc

    res = rtc.verify_preservation_cases_a_through_f()
    assert res["cases_tested"] == 6
    assert res["all_cases_verified"] is True

    by_id = {c["case_id"]: c for c in res["cases"]}
    assert "HISTORICAL_SCOPE_OVERWRITTEN" in by_id["Case_A"]["false_positive_violation"]
    assert "FALSIFIED_CLAIM_REWRITTEN" in by_id["Case_B"]["false_positive_violation"]
    assert "CANDIDATE_RISK_MISMATCH" in by_id["Case_C"]["false_positive_violation"]
    assert "REVOKED_GRANT_REACTIVATED" in by_id["Case_D"]["false_positive_violation"]
    assert "FORMER_HORIZON_OPTION_ERASED" in by_id["Case_E"]["false_positive_violation"]
    assert "DISSENT_FLATTENED_TO_FAKE_CONSENSUS" in by_id["Case_F"]["false_positive_violation"]
    assert by_id["Case_F"]["joint_permitted_actions"] == ["log_disagreement", "run_read_only_audit"]


def test_markdown_handover_auditor_catches_planted_real_text_failures():
    import real_text_continuity as rtc

    before_md = (
        "# Session Handover — Continuity Audit\n\n"
        "- Risk_Level: `HIGH`\n"
        "- Boundary: Do not edit foreign seat surfaces (read-only foreign surface).\n"
        "- Status: Runtime browser checks did not run in this session (`U<browser_skia_render>`).\n"
        "- Receipt: SHA-256 `4fa7c7399dddc5d9eb442d1a0bb94736c82112a988cf3920b983b1c037cfbe51`, 58 tests, all passed.\n"
        "- Dissent: Seat_A and Seat_B disagree on immediate strict cutover.\n"
        "- Horizon: Considered Option A (schema extension) and Option B (standalone verifier).\n"
    )

    # 1. VITA-8 Guarded Compaction must pass with 0 violations
    guarded_md = rtc.compact_markdown_with_vita8_guard(before_md, source_name="handover.md")
    rep_good = rtc.audit_markdown_handover(before_md, guarded_md)
    assert rep_good["lawful_handover"] is True
    assert rep_good["violations_count"] == 0

    # 2. Naive / lossy summary that drops boundary, erases unknown, downgrades risk, drops receipt, and fabricates full pass
    bad_after_md = (
        "# Compact Summary\n\n"
        "- Risk_Level: `LOW`\n"
        "- All tests passed and runtime checks passed. Everything is 100% verified and production ready.\n"
    )
    rep_bad = rtc.audit_markdown_handover(before_md, bad_after_md)
    assert rep_bad["lawful_handover"] is False
    codes = {v["code"] for v in rep_bad["violations"]}
    assert "DROPPED_BOUNDARY_LOCK" in codes
    assert "SILENT_UNKNOWN_ERASURE" in codes
    assert "BORROWED_LIGHT_FABRICATED_COMPLETION" in codes
    assert "CANDIDATE_RISK_MISMATCH" in codes
    assert "DROPPED_CRYPTO_RECEIPT" in codes


def test_real_workspace_triad_council_handovers_audit(tmp_path):
    import real_text_continuity as rtc

    _, notes_dir, _, _ = _create_tmp_continuity_fixtures(tmp_path)
    res = rtc.audit_real_workspace_handovers(notes_dir=notes_dir)
    assert res["available"] is True
    assert res["files_audited"] == 1
    assert res["all_guarded_passed"] is True
    assert res["all_naive_caught"] is True


def test_live_workspace_witness_case_g_sha256_and_ast_phantom_symbols(tmp_path, capsys):
    import workspace_witness as ww

    _, _, handoff_file, harness_py = _create_tmp_continuity_fixtures(tmp_path)
    res = ww.run_live_workspace_witness_suite(
        handoff_path=handoff_file,
        harness_path=harness_py,
        search_roots=[tmp_path],
        tmp_dir=tmp_path,
    )
    assert res["verified"] is True
    assert res["case_g_recovery_capability"]["verified"] is True
    assert res["case_g_recovery_capability"]["missing_backup_report"]["status"] == "UNRECOVERABLE_MISSING_BACKUP"
    assert res["case_g_recovery_capability"]["corrupted_backup_report"]["status"] == "UNRECOVERABLE_CORRUPTED_BACKUP"
    assert res["handoff_disk_sha256_verification"]["all_files_exist_on_disk"] is True
    assert res["handoff_disk_sha256_verification"]["exact_disk_matches"] == 1
    assert "inspect_context" in res["ast_phantom_symbol_audit"]["phantom_symbol_caught_check"]["phantom_symbols"]

    rc = cp.main(["verify-disk", "--handoff-file", str(handoff_file), "--harness-file", str(harness_py), "--json"])
    assert rc == 0
    out = json.loads(capsys.readouterr().out)
    assert out["verified"] is True

