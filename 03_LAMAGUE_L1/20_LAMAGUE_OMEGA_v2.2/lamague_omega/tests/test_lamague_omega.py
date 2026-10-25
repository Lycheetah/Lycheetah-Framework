#!/usr/bin/env python3
"""Gate-verified unit, property, Sardinas-Patterson, SXP-L v2.1, and 6-Body compiler tests for LAMAGUE Ω."""

from __future__ import annotations

import json
import math
import sys
from pathlib import Path

import pytest

SCRIPT_DIR = Path(__file__).resolve().parent.parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

import lamague_omega as lo  # noqa: E402


# =============================================================================
# 1. NATIVE-36 PRIMITIVE CELLS, RADICALS & SEALS
# =============================================================================

def test_native36_exact_36_cells_and_radicals():
    assert len(lo.NATIVE36_CELLS) == 36
    expected_keys = [str(d) for d in range(10)] + [chr(ord("A") + i) for i in range(26)]
    assert list(lo.NATIVE36_CELLS.keys()) == expected_keys
    for code, cell in lo.NATIVE36_CELLS.items():
        assert cell["name"]
        assert cell["spoken"]
        assert cell["core"]
        assert len(cell["radicals"]) >= 1
        for rad in cell["radicals"]:
            assert rad in lo.RADICAL_DEFINITIONS, f"Cell {code} uses unknown radical {rad}"


def test_native36_numerals_0_to_9_ternary_state_phase_grid():
    assert lo.NATIVE36_CELLS["0"]["core"] == "∅"
    assert lo.NATIVE36_CELLS["0"]["spoken"] == "nul"
    assert lo.NATIVE36_CELLS["1"]["spoken"] == "un"
    assert lo.NATIVE36_CELLS["3"]["spoken"] == "tan"
    assert lo.NATIVE36_CELLS["5"]["spoken"] == "tin"
    assert lo.NATIVE36_CELLS["7"]["spoken"] == "dun"
    assert lo.NATIVE36_CELLS["9"]["spoken"] == "taran"
    assert lo.NATIVE36_CELLS["9"]["core"] == "Ω"


def test_programme_seals_complete_and_expandable():
    expected_seals = {
        "COR", "FRO", "SOV", "CAS", "DIS",
        "VERITAS", "CARE", "LIFE", "COVENANT", "REPAIR", "LEGACY", "GRIEF",
        "DREAM-BIND", "LIVING-SENTENCE",
    }
    assert expected_seals.issubset(set(lo.PROGRAMME_SEALS.keys()))
    for name, seal in lo.PROGRAMME_SEALS.items():
        assert len(seal["expansion"]) >= 3, f"Seal {name} has empty expansion"
        for cell_code in seal["expansion"]:
            assert cell_code in lo.NATIVE36_CELLS


def test_svg_strip_generation_contains_glyph_cells():
    compiler = lo.LamagueOmegaCompiler()
    svg = compiler._render_svg_strip(["O", "S", "N", "E"])
    assert svg.startswith("<svg ")
    assert svg.endswith("</svg>")
    assert ">O·or</text>" in svg
    assert ">S·sa</text>" in svg
    assert ">N·nov</text>" in svg
    assert ">E·en</text>" in svg


# =============================================================================
# 2. SPOKEN LAMAGUE (SpL-Ω) & SARDINAS-PATTERSON DECODABILITY PROOF
# =============================================================================

def test_sardinas_patterson_detects_planted_c1_collision():
    # Planted failure: unspaced "an", "sai", "saian" has dangling suffix "an"
    ok, witness, steps = lo.sardinas_patterson_verify(["an", "sai", "saian"])
    assert ok is False
    assert witness == "an"
    assert steps >= 1


def test_sardinas_patterson_detects_duplicate_codewords():
    # Planted failure: duplicate syllable in code list
    ok, witness, steps = lo.sardinas_patterson_verify(["in", "or", "in"])
    assert ok is False
    assert witness == "in"
    assert steps == 0


def test_sardinas_patterson_verifies_repaired_spl_omega():
    report = lo.verify_spoken_lamague_decodability()
    assert report["native36_36_unspaced"]["count"] == 36
    assert report["spl_core_13_unspaced"]["count"] == 13
    assert report["spl_core_13_unspaced"]["uniquely_decodable"] is True
    assert report["spl_omega_full_phonological_stream"]["uniquely_decodable"] is True
    assert report["spl_omega_full_phonological_stream"]["total_morphemes"] >= 110


def test_c1_through_c6_collision_repairs_present():
    # C2: infinity is 'inin', while Native-36 I is 'in'
    assert lo.NATIVE36_CELLS["I"]["spoken"] == "in"
    assert lo.UNIFIED_SPOKEN_ROOTS["inin"]["token"] == "∞"
    # C3: past is 'ta', slow is 'tas'
    assert lo.UNIFIED_BOUND_MODIFIERS["ta"]["category"] == "temporal"
    assert lo.UNIFIED_BOUND_MODIFIERS["tas"]["category"] == "prosodic"
    # C4: state ⇈ is 'ki', fast is 'kis'
    assert lo.UNIFIED_SPOKEN_ROOTS["ki"]["token"] == "⇈"
    assert lo.UNIFIED_BOUND_MODIFIERS["kis"]["category"] == "prosodic"
    # C5: breath inhale is 'ihn'
    assert lo.UNIFIED_BOUND_MODIFIERS["ihn"]["category"] == "breath"
    # C6: 5 dialogue particles + Argon lexicon declared
    for particle in ("wi", "ni", "fu", "li", "na", "athan", "kalan", "kinein", "sticta", "vectis", "vorin"):
        assert particle in lo.UNIFIED_SPOKEN_ROOTS


# =============================================================================
# 3. SXP-L v2.1 CONVERSATIONAL ENGINE (All 8 Defects Repaired)
# =============================================================================

def test_sxpl_defect_1_alias_preservation():
    engine = lo.SXPLConversationalEngine()
    turn = engine.parse_turn("T1", "mac", "aetheron", "mi liva USR:A.")
    assert "USR:A" in turn.native36_aliases_preserved
    assert "USR:A" in turn.canonical_expanded
    assert "N36:A" not in turn.canonical_expanded


def test_sxpl_defect_2_intransitive_verb_valency():
    engine = lo.SXPLConversationalEngine()
    t1 = engine.parse_turn("T1", "mac", "aetheron", "ti ariva.")
    t2 = engine.parse_turn("T2", "aetheron", "mac", "mi satoma.")
    assert t1.speech_act == "intransitive"
    assert t1.resolved_actor == "aetheron"
    assert t1.resolved_predicate == "ariva"
    assert t1.resolved_target is None
    assert t2.speech_act == "intransitive"
    assert t2.resolved_actor == "aetheron"


def test_sxpl_defect_3_unified_hira_attitude_dispatch():
    engine = lo.SXPLConversationalEngine()
    turn = engine.parse_turn("T1", "mac", "aetheron", "mi hira ti ariva.")
    assert turn.speech_act == "attitude_hope"
    assert turn.resolved_predicate == "hira"


def test_sxpl_defect_4_and_5_consent_meaning_diff_and_high_priority_target_swap():
    engine = lo.SXPLConversationalEngine()
    t_grant = engine.parse_turn("T1", "mac", "aetheron", "mi periva ti.")
    t_revoke = engine.parse_turn("T2", "mac", "aetheron", "mi nevira ti.")
    diff_consent = engine.compare_meaning(t_grant, t_revoke)
    assert diff_consent["equivalent"] is False
    assert diff_consent["priority"] == "high"

    t_target_a = engine.parse_turn("T3", "mac", "aetheron", "mi liva ti.")
    t_target_b = engine.parse_turn("T4", "mac", "sol", "mi liva ti.")
    diff_target = engine.compare_meaning(t_target_a, t_target_b)
    assert diff_target["equivalent"] is False
    assert diff_target["priority"] == "high"


def test_sxpl_defect_6_nevira_always_sets_host_advisory_flag():
    engine = lo.SXPLConversationalEngine()
    # Even when a synthetic host grant is present, linguistic revocation MUST flag host_advisory_flag=True
    turn = engine.parse_turn("T1", "mac", "aetheron", "mi nevira ti.", host_grant_present=True)
    assert turn.speech_act == "revocation"
    assert turn.host_advisory_flag is True
    assert turn.is_active_boundary is True


def test_sxpl_defect_7_and_8_repair_clears_boundary_and_rejects_double_supersede():
    engine = lo.SXPLConversationalEngine()
    t1 = engine.parse_turn("T1", "mac", "aetheron", "mi nevira ti.")
    assert t1.is_active_boundary is True

    # Repair T1 with T2 (using gonape T1 dimotu bakumo ... syntax)
    t2 = engine.parse_turn("T2", "mac", "aetheron", "mi remakivo gonape T1 dimotu bakumo mi periva ti tesavo.")
    assert t2.speech_act == "repair"
    assert t1.superseded_by == "T2"
    assert t1.is_active_boundary is False

    # Defect #8: Attempting to repair already-superseded T1 must raise ValueError
    with pytest.raises(ValueError, match="already superseded"):
        engine.parse_turn("T3", "mac", "aetheron", "mi remakivo gonape T1 dimotu bakumo mi liva ti tesavo.")


def test_sxpl_viewpoint_soraviko_vs_tumerako_disambiguation():
    engine = lo.SXPLConversationalEngine()
    engine.parse_turn("T1", "speaker_a", "speaker_b", "mi liva ti.")
    # Speaker B clarifies using soraviko (quoted speaker's perspective -> mi = speaker_a, ti = speaker_b)
    t_quoted = engine.parse_turn(
        "T2", "speaker_b", "speaker_a",
        "mi kelunaro gonape T1 dimotu bakumo soraviko mi luma ti tesavo."
    )
    assert t_quoted.viewpoint_frame == "soraviko"
    assert t_quoted.resolved_actor == "speaker_a"
    assert t_quoted.resolved_target == "speaker_b"

    # Speaker B clarifies using tumerako (current speaker's perspective -> mi = speaker_b, ti = speaker_a)
    t_current = engine.parse_turn(
        "T3", "speaker_b", "speaker_a",
        "mi kelunaro gonape T1 dimotu bakumo tumerako mi luma ti tesavo."
    )
    assert t_current.viewpoint_frame == "tumerako"
    assert t_current.resolved_actor == "speaker_b"
    assert t_current.resolved_target == "speaker_a"


def test_sxpl_full_8_defect_self_audit_passes():
    report = lo.run_sxpl_8_defect_audit()
    assert report["all_8_defects_repaired"] is True
    assert len(report["checks"]) == 8
    assert all(c["passed"] for c in report["checks"])


# =============================================================================
# 4. 8D MANIFOLD, CONTRACTIVE TRIAD & DREAM-REALITY BINDING EQUATIONS
# =============================================================================

def test_triad_contraction_strictly_reduces_drift():
    compiler = lo.LamagueOmegaCompiler()
    vec_8d, converged, drift_before, drift_after = compiler._compute_8d_and_triad(["O", "S", "N", "E", "G", "I", "U", "Q"])
    assert len(vec_8d) == 8
    assert len(converged) == 8
    assert drift_after < drift_before


def test_dream_reality_earned_light_vs_borrowed_light():
    # Grounded Earned Light
    earned = lo.evaluate_dream_reality_and_vita(
        uncertainty_before=0.35,
        uncertainty_after=0.15,
        contradiction_before=0.25,
        contradiction_after=0.05,
        hidden_cost_before=0.0,
        hidden_cost_after=0.0,
        honest_progress=0.20,
    )
    assert earned.borrowed_light_detected is False
    assert earned.earned_light_valid is True
    assert earned.earned_light_energy_after < earned.earned_light_energy_before
    assert earned.void_lifecycle_stage == "FORGED"

    # Borrowed Light: hidden displaced cost rises after step
    borrowed = lo.evaluate_dream_reality_and_vita(
        hidden_cost_before=0.0,
        hidden_cost_after=0.45,
    )
    assert borrowed.borrowed_light_detected is True
    assert borrowed.earned_light_valid is False
    assert borrowed.void_lifecycle_stage == "ASH"


def test_hidden_extraction_triggers_infinite_vita_distance():
    extracted = lo.evaluate_dream_reality_and_vita(hidden_extraction=0.25)
    assert extracted.agency_symmetry_holds is False
    assert math.isinf(extracted.vita_distance)
    assert extracted.shared_value_vector["-H_x"] == -0.25


def test_breathing_compression_round_trip():
    compiler = lo.LamagueOmegaCompiler()
    bundle = compiler.compile("FRO -> COR")
    expected_cells = lo.PROGRAMME_SEALS["FRO"]["expansion"] + lo.PROGRAMME_SEALS["COR"]["expansion"]
    assert [c["cell"] for c in bundle.r2_native36_cells] == expected_cells
    assert bundle.dream_reality_eval["breathing_direction"].startswith("Z_down")


# =============================================================================
# 5. 6-BODY COMPILER & FOUR CONSTITUTIONAL GATES
# =============================================================================

def test_compiler_all_5_input_modes_and_6_bodies():
    compiler = lo.LamagueOmegaCompiler()
    samples = {
        "SEAL_SEQUENCE": "VERITAS -> CARE -> LIFE -> COVENANT -> REPAIR -> LEGACY",
        "CORE_SYMBOLIC": "Ao → Φ↑ → Ψ_inv",
        "SPOKEN_SPL": "An. Wi fla-ta. ∅.",
        "SXPL_DIALOGUE": "mi liva ti",
        "NATURAL_LANGUAGE": "Hold the frontier unproven where evidence is missing.",
    }
    for expected_mode, text in samples.items():
        res = compiler.compile(text)
        assert res.detected_mode == expected_mode
        assert res.r1_english_recovery
        assert res.r2_svg_strip.startswith("<svg ")
        assert res.r3_ipa_transcription.startswith("[")
        assert len(res.r4_semantic_hash) == 64
        assert res.r5_semantic_packet["schema"] == "LAMAGUE-SEMANTIC-PACKET-1"
        assert res.r6_drift_after <= res.r6_drift_before
        assert res.audit_verdict == "VALID"


def test_four_gates_trigger_reject_isolate_expand_and_repair():
    compiler = lo.LamagueOmegaCompiler()

    # Missing authority triggers REJECT
    res_reject = compiler.compile("FRO -> COR", authority="")
    assert res_reject.four_gates["Agency_Gate"]["passed"] is False
    assert res_reject.audit_verdict == "REJECT"

    # Hidden extraction / paternalism triggers ISOLATE
    res_isolate = compiler.compile("FRO -> COR", hidden_extraction=0.35)
    assert res_isolate.four_gates["Agency_Gate"]["passed"] is False
    assert res_isolate.audit_verdict == "ISOLATE"

    # Silent Nodes trigger EXPAND
    res_expand = compiler.compile("FRO -> COR", unrepresented_parties=["Future Downstream Users"])
    assert res_expand.four_gates["Life_Gate"]["passed"] is False
    assert res_expand.audit_verdict == "EXPAND"

    # Borrowed Light triggers REPAIR
    res_repair = compiler.compile("DREAM-BIND", borrowed_light_cost=0.40)
    assert res_repair.four_gates["Truth_Gate"]["passed"] is False
    assert res_repair.audit_verdict == "REPAIR"


# =============================================================================
# 6. CLI SUBCOMMANDS & JSON OUTPUT
# =============================================================================

def test_cli_subcommands_json_output(capsys):
    rc = lo.main(["compile", "DREAM-BIND", "--json"])
    assert rc == 0
    out = json.loads(capsys.readouterr().out)
    assert out["detected_mode"] == "SEAL_SEQUENCE"
    assert out["audit_verdict"] == "VALID"

    rc2 = lo.main(["verify-spoken", "--json"])
    assert rc2 == 0
    out2 = json.loads(capsys.readouterr().out)
    assert out2["spl_omega_full_phonological_stream"]["uniquely_decodable"] is True

    rc3 = lo.main(["sxp-audit", "--json"])
    assert rc3 == 0
    out3 = json.loads(capsys.readouterr().out)
    assert out3["all_8_defects_repaired"] is True

    rc4 = lo.main(["seals", "--json"])
    assert rc4 == 0
    out4 = json.loads(capsys.readouterr().out)
    assert "DREAM-BIND" in out4

    rc5 = lo.main(["dream-eval", "--hidden-cost-after", "0.3", "--json"])
    assert rc5 == 0
    out5 = json.loads(capsys.readouterr().out)
    assert out5["borrowed_light_detected"] is True


# =============================================================================
# 7. LAMAGUE Ω v2.2 EVIDENTIAL GRAMMAR, 135-MORPHEME PROOF & DISCOURSE ENGINE
# =============================================================================

def test_extended_135_morpheme_sardinas_patterson_decodability():
    import lamague_discourse as ld

    dec = ld.verify_extended_135_morpheme_decodability()
    assert dec["new_v22_discourse_roots_count"] == 20
    assert dec["total_morphemes_count"] == 135
    assert dec["root_homophone_overlap"] == []
    assert dec["new_20_unspaced_uniquely_decodable"] is True
    assert dec["framed_stream_distinct_with_terminator"] is True
    assert dec["framed_stream_witness"] is None


def test_bilingual_evidential_translation_and_5_turn_discourse(capsys):
    import lamague_discourse as ld

    # Test unknown U<T> evidential classification ('kura')
    unk_res = ld.translate_english_to_lamague_v22(
        "Browser check did not run yet; holding U<browser_skia> as unknown.",
        speaker="Aetheron",
        addressee="Mac",
    )
    assert unk_res["evidential_particle"] == "kura"
    assert "[UNKNOWN U<T>]" in unk_res["english_back_translation"]
    assert unk_res["r2_svg_strip"].startswith("<svg ")

    # Test refuted claim in H ('fara' + 'hista')
    ref_res = ld.translate_english_to_lamague_v22(
        "Claim refuted by counterexample; preserved in history.",
        speaker="Caelorynth",
        addressee="Aetheron",
    )
    assert ref_res["evidential_particle"] == "fara"
    assert ref_res["register_particle"] == "hista"
    assert "[REFUTED-IN-H]" in ref_res["english_back_translation"]

    # Test 5-turn canonical discourse via CLI
    rc = lo.main(["discourse", "--json"])
    assert rc == 0
    disc = json.loads(capsys.readouterr().out)
    assert disc["turns_count"] == 5
    assert set(disc["unique_evidentials_exercised"]) >= {"sora", "kura"}


def test_item1_three_separate_decodability_results_and_independent_sp():
    """Item 1: Report (a) framed, (b) raw unframed, (c) glottal no-dot separately; (b) & (c) are FALSE with witness 'in'."""
    import lamague_discourse as ld

    dec = ld.verify_extended_135_morpheme_decodability()
    assert "framed_stream_distinct_with_terminator" in dec
    assert "full_135_stream_uniquely_decodable" not in dec
    assert dec["a_framed_with_terminator"]["uniquely_decodable"] is True
    assert "TRIVIAL_COMMA_CODE" in dec["a_framed_with_terminator"]["note"]
    assert "UNTESTED_PHONOLOGICAL_ASSUMPTION" in dec["a_framed_with_terminator"]["note"]

    # (b) raw roots + mods, unframed -> FALSE, witness "in"
    assert dec["b_raw_roots_and_mods_unframed"]["uniquely_decodable"] is False
    assert dec["b_raw_roots_and_mods_unframed"]["witness"] == "in"

    # (c) roots + ʔmods, no "." -> FALSE, witness "in"
    assert dec["c_roots_and_glottal_mods_no_terminator"]["uniquely_decodable"] is False
    assert dec["c_roots_and_glottal_mods_no_terminator"]["witness"] == "in"

    # Independent SP reference implementation check
    def _independent_sp(code_set: set[str]) -> tuple[bool, str | None]:
        def _dangling(a: set[str], b: set[str]) -> set[str]:
            out = set()
            for x in a:
                for y in b:
                    if x != y and x.startswith(y):
                        out.add(x[len(y):])
            return out

        s1 = _dangling(code_set, code_set)
        if not s1:
            return True, None
        seen = [s1]
        cur = s1
        while True:
            hit = code_set & cur
            if hit:
                return False, sorted(hit)[0]
            cur = _dangling(code_set, cur) | _dangling(cur, code_set)
            if not cur or cur in seen:
                return True, None
            seen.append(cur)

    all_roots = set(lo.UNIFIED_SPOKEN_ROOTS) | set(ld.LAMAGUE_V22_DISCOURSE_ROOTS)
    raw_b = all_roots | set(lo.UNIFIED_BOUND_MODIFIERS)
    raw_c = all_roots | {f"{lo.GLOTTAL}{m}" for m in lo.UNIFIED_BOUND_MODIFIERS}
    assert (
        dec["b_raw_roots_and_mods_unframed"]["uniquely_decodable"],
        dec["b_raw_roots_and_mods_unframed"]["witness"],
    ) == _independent_sp(raw_b)
    assert (
        dec["c_roots_and_glottal_mods_no_terminator"]["uniquely_decodable"],
        dec["c_roots_and_glottal_mods_no_terminator"]["witness"],
    ) == _independent_sp(raw_c)


def test_item2_sp_step_cap_raises_instead_of_returning_true(monkeypatch):
    """Item 2: Hitting the SP step cap must raise/return UNDECIDED, never True."""
    monkeypatch.setattr(lo, "SP_MAX_STEPS", 1)
    # Code needing 2+ steps: c1 = {"b"}, c2 = {"c"}
    with pytest.raises(RuntimeError, match="SARDINAS_PATTERSON_UNDECIDED"):
        lo.sardinas_patterson_verify(["ab", "bc", "a", "cd"])


def test_item3_and_4_counts_and_glottal_homophone_disambiguation():
    """Items 3 & 4: Verify exact 100 roots + 35 mods counts and glottal-stop disambiguation for an, ex, na, om, ya."""
    import lamague_discourse as ld

    dec = ld.verify_extended_135_morpheme_decodability()
    assert dec["existing_free_roots_count"] == 80
    assert dec["new_v22_discourse_roots_count"] == 20
    assert dec["combined_free_roots_count"] == 100
    assert dec["bound_modifiers_count"] == 35
    assert dec["canonical_soma_thanatos_modifiers_count"] == 31
    assert dec["total_morphemes_count"] == 135

    # Item 4: bare homophones between roots and modifiers are exactly an, ex, na, om, ya;
    # glottal stop 'ʔ' disambiguates 100% of them.
    assert dec["bare_root_modifier_homophones"] == ["an", "ex", "na", "om", "ya"]
    assert dec["glottal_prefixed_root_modifier_overlap"] == []
    for hom in ("an", "ex", "na", "om", "ya"):
        assert lo.classify_spoken_morpheme(hom)["kind"] == "FREE_ROOT"
        assert lo.classify_spoken_morpheme(f"{lo.GLOTTAL}{hom}")["kind"] == "BOUND_MODIFIER"


def test_item5_vira_gate_and_signed_permit_grant_and_riska(tmp_path: Path):
    """Item 5: Default evidential is kura (never vira); vira requires disk SHA-256 receipt; periva requires signed permit; push/release/etc -> riska."""
    import lamague_discourse as ld

    # 1. Unverified claim without disk receipt -> NOT vira (must be kura)
    r1 = ld.translate_english_to_lamague_v22("All checks passed and the system is production ready")
    assert r1["evidential_particle"] != "vira"
    assert r1["evidential_particle"] == "kura"

    # 2. Grant without SignedActionPermit -> NO periva, and "push" -> riska
    r2 = ld.translate_english_to_lamague_v22("Grant Aetheron permission to push to GitHub")
    assert "periva" not in r2["morphemes"]
    assert "nevira" in r2["morphemes"]
    assert r2["risk_particle"] == "riska"

    # 3. Valid receipt on disk -> vira; tampered file on disk -> NOT vira (kura)
    f = tmp_path / "evidence.txt"
    f.write_bytes(b"verified_evidence_payload_123")
    valid_sha = lo.hashlib.sha256(b"verified_evidence_payload_123").hexdigest()

    r_valid = ld.translate_english_to_lamague_v22(
        "All checks passed and the system is production ready",
        receipt={"path": str(f), "sha256": valid_sha},
    )
    assert r_valid["evidential_particle"] == "vira"

    # Tamper with file on disk after computing receipt
    f.write_bytes(b"tampered_bytes_on_disk")
    r_tampered = ld.translate_english_to_lamague_v22(
        "All checks passed and the system is production ready",
        receipt={"path": str(f), "sha256": valid_sha},
    )
    assert r_tampered["evidential_particle"] != "vira"
    assert r_tampered["evidential_particle"] == "kura"


def test_item6_slot_classifier_round_trip_not_lossless():
    """Item 6: Translator is a 5-slot classifier (not lossless); test round-trip of slot values only."""
    import lamague_discourse as ld

    s1 = ld.translate_english_to_lamague_v22("I only edited one file")
    s2 = ld.translate_english_to_lamague_v22("All checks passed and the system is production ready")
    assert s1["translator_type"] == "FIVE_SLOT_EPISTEMIC_CLASSIFIER"
    assert s1["sxp_v22_utterance"] == s2["sxp_v22_utterance"]
    recovered_slots = ld.extract_discourse_slots(s1["sxp_v22_utterance"])
    assert recovered_slots == s1["slots"]


def test_item7_word_boundary_regex_no_substring_false_positives():
    """Item 7: Substring keyword bug fixed: 'knowledge' must not emit edga; 'immigrant' / 'permitted' must not fire grant/permit."""
    import lamague_discourse as ld

    r_know = ld.translate_english_to_lamague_v22("knowledge base updated")
    assert "edga" not in r_know["morphemes"]
    assert r_know["slots"]["layer"] is None

    r_imm = ld.translate_english_to_lamague_v22("immigrant status documented in history")
    assert "autha" != r_imm["register_particle"]
    assert r_imm["register_particle"] == "hista"

