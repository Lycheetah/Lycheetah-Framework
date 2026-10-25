#!/usr/bin/env python3
"""
===============================================================================
REAL-TEXT CONTINUITY ENGINE — ENGLISH MARKDOWN ⇄ S=(H,K,A) & VITA-8 AUDITOR
===============================================================================
Author:   Aetheron (Antigravity Seat — Gemini 4 Argon) & Mackenzie Conor James Clark
Lineage:  Lycheetah Framework — Real-World Session Compactor, Receipt Auditor,
          and Cases A–F Preservation Verifier
Module:   creations/continuity_prover/real_text_continuity.py

Bridges formal LAMAGUE Ω / VITA-8 continuity proofs directly to ordinary English
markdown handovers, session summaries, task boards, and engineering notes.

Enforces:
  1. The Tri-Partite Preservation State S = (H, K, A):
       - H (History & Provenance): original claims, scopes, contemporary evidence,
         demotion/refutation lineage, historical grants, and former option horizons.
       - K (Endorsed Knowledge & Receipts): active claims with epistemic layers
         (FOUNDATION, THEORY, EDGE), concrete receipts (SHA-256 hashes, test counts,
         file paths), and explicit Typed Unknowns U<T>.
       - A (Effective Authority & Boundaries): active permissions (MAY), explicit
         prohibitions/boundaries (DENY / read-only / do-not-edit), revoked grants
         (provenance without jurisdiction), risk-level binding, and polyphonic
         dissent with joint action intersection (A_perm ∩ B_perm).
  2. The Six Worked Preservation Cases (Cases A–F) from
     2026-10-18_PRESERVATION_CASES.md:
       - Case A: CASCADE Demotion (narrowing scope in K while preserving original in H)
       - Case B: Falsification without Erasure (marking REFUTED without rewriting H)
       - Case C: Omitted Decision Input / Risk Binding (catching HIGH -> LOW downgrade)
       - Case D: Remembered Grant after Revocation (provenance without jurisdiction)
       - Case E: Former Epistemic Horizon (retaining unchosen options [A, B] alongside A)
       - Case F: Cooperation with Persistent Dissent (retaining v_A != v_B + A_perm ∩ B_perm)
  3. Real-Text Markdown Handover Auditor (before.md vs after.md):
       - Detects dropped read-only/boundary locks, erased unknowns, fabricated
         completions without receipts ("Borrowed Light"), risk downgrades,
         reactivated revocations, flattened dissent, and erased option horizons.
===============================================================================
"""

from __future__ import annotations

import copy
import hashlib
import json
import os
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import continuity_prover as cp
import lamague_omega as lo


# =============================================================================
# 1. FORMAL S = (H, K, A) STATE & CASES A–F VERIFIER
# =============================================================================

RISK_RANK: Dict[str, int] = {
    "LOW": 1,
    "MEDIUM": 2,
    "HIGH": 3,
    "CRITICAL": 4,
}


@dataclass
class HistoricalClaimRecord:
    """Entry in H: preserves an original claim, its contemporary scope, layer, and evidence."""
    claim_id: str
    original_statement: str
    original_layer: str          # "FOUNDATION" | "THEORY" | "EDGE"
    original_scope: str
    contemporary_evidence: List[str] = field(default_factory=list)
    timestamp: str = "t1"


@dataclass
class HistoricalGrantRecord:
    """Entry in H: records when an authority grant or revocation occurred."""
    grant_id: str
    issuer: str
    action: str
    event_type: str              # "GRANT" | "REVOKE"
    scope: str
    timestamp: str
    note: str = ""


@dataclass
class EpistemicHorizonRecord:
    """Entry in H (Case E): records the full option set considered at a decision point."""
    decision_id: str
    displayed_options: List[str]
    chosen_option: str
    unverified_options: List[str] = field(default_factory=list)
    rationale: str = ""
    timestamp: str = "t1"


@dataclass
class EndorsedKnowledgeClaim:
    """Entry in K: represents present endorsement status, scope, layer, and receipts."""
    claim_id: str
    current_statement: str
    current_layer: str           # "FOUNDATION" | "THEORY" | "EDGE" | "NONE"
    current_scope: str
    status: str                  # "ENDORSED" | "NARROWED" | "REFUTED" | "UNVERIFIED"
    receipts: List[str] = field(default_factory=list)
    linked_history_id: str = ""
    counterexample_refs: List[str] = field(default_factory=list)


@dataclass
class PolyphonicDissentRecord:
    """Entry in A/K (Case F): preserves distinct participant positions and permitted action sets."""
    topic_id: str
    views_by_seat: Dict[str, str]                  # e.g. {"Seat_A": "v_A", "Seat_B": "v_B"}
    permitted_actions_by_seat: Dict[str, List[str]]
    status: str = "UNRESOLVED_DISSENT"

    def joint_permitted_actions(self) -> List[str]:
        """Compute exact intersection A_perm ∩ B_perm across all dissenting seats."""
        if not self.permitted_actions_by_seat:
            return []
        sets = [set(acts) for acts in self.permitted_actions_by_seat.values()]
        common = set.intersection(*sets) if sets else set()
        return sorted(common)


@dataclass
class StateS_HKA:
    """
    Complete Preservation State S = (H, K, A) unifying all 6 worked cases (A–F).
    """
    state_id: str
    step_index: int
    source_name: str = "session"

    # H: Retained History
    H_claims: Dict[str, HistoricalClaimRecord] = field(default_factory=dict)
    H_grants: List[HistoricalGrantRecord] = field(default_factory=list)
    H_horizons: Dict[str, EpistemicHorizonRecord] = field(default_factory=dict)

    # K: Currently Endorsed Knowledge, Receipts & Typed Unknowns
    K_claims: Dict[str, EndorsedKnowledgeClaim] = field(default_factory=dict)
    K_unknowns: List[str] = field(default_factory=list)
    K_sha256_receipts: List[str] = field(default_factory=list)
    K_test_receipts: List[str] = field(default_factory=list)

    # A: Presently Effective Authority, Boundaries, Revocations, Risk & Dissent
    A_may_permissions: List[str] = field(default_factory=list)
    A_deny_boundaries: List[str] = field(default_factory=list)
    A_revoked_actions: List[str] = field(default_factory=list)
    A_risk_level: str = "LOW"                       # "LOW" | "MEDIUM" | "HIGH" | "CRITICAL"
    A_risk_downgrade_authorized_by: str = ""
    A_dissent: Dict[str, PolyphonicDissentRecord] = field(default_factory=dict)
    A_proposed_joint_actions: List[str] = field(default_factory=list)

    def critical_projection(self) -> Dict[str, Any]:
        """
        Canonical projection of all decision-critical fields in S = (H, K, A).
        Crucially binds A_risk_level (fixing Case C), A_revoked_actions (Case D),
        H_horizons (Case E), and A_dissent (Case F).
        """
        return {
            "H_claims": {
                cid: {
                    "original_statement": rec.original_statement,
                    "original_layer": rec.original_layer,
                    "original_scope": rec.original_scope,
                    "contemporary_evidence": sorted(rec.contemporary_evidence),
                }
                for cid, rec in sorted(self.H_claims.items())
            },
            "H_grants": [
                {
                    "grant_id": g.grant_id,
                    "issuer": g.issuer,
                    "action": g.action,
                    "event_type": g.event_type,
                    "scope": g.scope,
                    "timestamp": g.timestamp,
                }
                for g in self.H_grants
            ],
            "H_horizons": {
                did: {
                    "displayed_options": list(h.displayed_options),
                    "chosen_option": h.chosen_option,
                    "unverified_options": list(h.unverified_options),
                }
                for did, h in sorted(self.H_horizons.items())
            },
            "K_claims": {
                cid: {
                    "current_statement": c.current_statement,
                    "current_layer": c.current_layer,
                    "current_scope": c.current_scope,
                    "status": c.status,
                    "receipts": sorted(c.receipts),
                    "counterexample_refs": sorted(c.counterexample_refs),
                }
                for cid, c in sorted(self.K_claims.items())
            },
            "K_unknowns": sorted(self.K_unknowns),
            "A_may_permissions": sorted(self.A_may_permissions),
            "A_deny_boundaries": sorted(self.A_deny_boundaries),
            "A_revoked_actions": sorted(self.A_revoked_actions),
            "A_risk_level": self.A_risk_level.upper(),
            "A_dissent": {
                tid: {
                    "views_by_seat": dict(sorted(d.views_by_seat.items())),
                    "joint_permitted_actions": d.joint_permitted_actions(),
                    "status": d.status,
                }
                for tid, d in sorted(self.A_dissent.items())
            },
        }

    def critical_hash(self) -> str:
        raw = json.dumps(self.critical_projection(), sort_keys=True, separators=(",", ":"), ensure_ascii=False)
        return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def verify_s_hka_transition(before: StateS_HKA, after: StateS_HKA) -> Dict[str, Any]:
    """
    Verify a state transition S_0 = (H_0, K_0, A_0) -> S_1 = (H_1, K_1, A_1)
    against all 6 Preservation Laws (Cases A through F).
    """
    violations: List[str] = []
    case_checks: Dict[str, bool] = {
        "Case_A_cascade_demotion_integrity": True,
        "Case_B_falsification_non_erasure": True,
        "Case_C_risk_level_binding": True,
        "Case_D_revocation_jurisdiction": True,
        "Case_E_former_epistemic_horizon": True,
        "Case_F_polyphonic_dissent_intersection": True,
    }

    # --- Case A & Case B: Historical claims in H_0 must never be erased or rewritten in H_1 ---
    for cid, h0 in before.H_claims.items():
        if cid not in after.H_claims:
            violations.append(f"HISTORICAL_CLAIM_ERASED: {cid} removed from H")
            case_checks["Case_A_cascade_demotion_integrity"] = False
            case_checks["Case_B_falsification_non_erasure"] = False
            continue
        h1 = after.H_claims[cid]
        if h1.original_statement != h0.original_statement:
            violations.append(
                f"FALSIFIED_CLAIM_REWRITTEN (Case B): {cid} original_statement mutated in H "
                f"from {h0.original_statement!r} to {h1.original_statement!r}"
            )
            case_checks["Case_B_falsification_non_erasure"] = False
        if h1.original_scope != h0.original_scope or h1.original_layer != h0.original_layer:
            violations.append(
                f"HISTORICAL_SCOPE_OVERWRITTEN (Case A): {cid} original scope/layer in H mutated "
                f"from ({h0.original_layer}, {h0.original_scope}) to ({h1.original_layer}, {h1.original_scope})"
            )
            case_checks["Case_A_cascade_demotion_integrity"] = False
        for ev in h0.contemporary_evidence:
            if ev not in h1.contemporary_evidence:
                violations.append(f"HISTORICAL_EVIDENCE_DROPPED (Case A): {cid} lost evidence {ev}")
                case_checks["Case_A_cascade_demotion_integrity"] = False

    # Check K_1 consistency for narrowed or refuted claims
    for cid, k1 in after.K_claims.items():
        if k1.status == "REFUTED" and k1.current_layer not in ("NONE", "REFUTED"):
            violations.append(
                f"REFUTED_CLAIM_STILL_ACTIVE_IN_K (Case B): {cid} marked REFUTED but retains active layer {k1.current_layer}"
            )
            case_checks["Case_B_falsification_non_erasure"] = False

    # --- Case C: Risk-Level Binding (prevent unauthorized risk downgrade) ---
    r0 = RISK_RANK.get(before.A_risk_level.upper(), 1)
    r1 = RISK_RANK.get(after.A_risk_level.upper(), 1)
    if r1 < r0 and not after.A_risk_downgrade_authorized_by.strip():
        violations.append(
            f"CANDIDATE_RISK_MISMATCH (Case C): risk_level downgraded from "
            f"{before.A_risk_level.upper()} to {after.A_risk_level.upper()} without authority receipt"
        )
        case_checks["Case_C_risk_level_binding"] = False

    # --- Case D: Remembered Grant after Revocation (Provenance without Jurisdiction) ---
    # 1. All historical grant/revoke events in H_0 must remain in H_1
    before_grant_ids = {g.grant_id for g in before.H_grants}
    after_grant_ids = {g.grant_id for g in after.H_grants}
    missing_grants = sorted(before_grant_ids - after_grant_ids)
    if missing_grants:
        violations.append(f"GRANT_HISTORY_ERASED (Case D): missing historical events {missing_grants}")
        case_checks["Case_D_revocation_jurisdiction"] = False

    # 2. Any action whose latest event in H_1 is REVOKE (or is in A_revoked_actions) MUST NOT be in A_may_permissions
    latest_event_by_action: Dict[str, HistoricalGrantRecord] = {}
    for g in after.H_grants:
        latest_event_by_action[g.action] = g
    for action, latest_g in latest_event_by_action.items():
        if latest_g.event_type.upper() == "REVOKE":
            if action in after.A_may_permissions:
                violations.append(
                    f"REVOKED_GRANT_REACTIVATED (Case D): action {action!r} was revoked at {latest_g.timestamp} "
                    f"but is still active in A_may_permissions"
                )
                case_checks["Case_D_revocation_jurisdiction"] = False
            if action not in after.A_revoked_actions and action not in after.A_deny_boundaries:
                violations.append(
                    f"REVOCATION_NOT_ENFORCED_IN_A (Case D): revoked action {action!r} missing from A_revoked_actions / A_deny_boundaries"
                )
                case_checks["Case_D_revocation_jurisdiction"] = False

    # Also check explicit A_deny_boundaries from before state
    for boundary in before.A_deny_boundaries:
        if boundary not in after.A_deny_boundaries:
            violations.append(f"BOUNDARY_LOCK_DROPPED (Case D): prohibition {boundary!r} dropped from A_deny_boundaries")
            case_checks["Case_D_revocation_jurisdiction"] = False

    # --- Case E: Former Epistemic Horizon ---
    for did, h0_hor in before.H_horizons.items():
        if did not in after.H_horizons:
            violations.append(f"FORMER_HORIZON_ERASED (Case E): decision horizon {did!r} removed from H_horizons")
            case_checks["Case_E_former_epistemic_horizon"] = False
            continue
        h1_hor = after.H_horizons[did]
        missing_opts = [opt for opt in h0_hor.displayed_options if opt not in h1_hor.displayed_options]
        if missing_opts:
            violations.append(
                f"FORMER_HORIZON_OPTION_ERASED (Case E): decision {did!r} dropped unchosen options {missing_opts}"
            )
            case_checks["Case_E_former_epistemic_horizon"] = False

    # --- Case F: Cooperation with Persistent Dissent ---
    for tid, d0 in before.A_dissent.items():
        if tid not in after.A_dissent:
            violations.append(f"DISSENT_RECORD_ERASED (Case F): dissent topic {tid!r} removed")
            case_checks["Case_F_polyphonic_dissent_intersection"] = False
            continue
        d1 = after.A_dissent[tid]
        for seat, view0 in d0.views_by_seat.items():
            view1 = d1.views_by_seat.get(seat)
            if view1 != view0:
                violations.append(
                    f"DISSENT_FLATTENED_TO_FAKE_CONSENSUS (Case F): seat {seat!r} view on {tid!r} mutated "
                    f"from {view0!r} to {view1!r}"
                )
                case_checks["Case_F_polyphonic_dissent_intersection"] = False
        allowed_joint = set(d1.joint_permitted_actions())
        for act in after.A_proposed_joint_actions:
            if act not in allowed_joint:
                violations.append(
                    f"ACTION_OUTSIDE_DISSENT_INTERSECTION (Case F): proposed action {act!r} not in "
                    f"A_perm ∩ B_perm = {sorted(allowed_joint)}"
                )
                case_checks["Case_F_polyphonic_dissent_intersection"] = False

    # --- Unknowns check: Unknowns in K_0 cannot disappear without receipt in K_1 ---
    all_after_receipts = " ".join(after.K_sha256_receipts + after.K_test_receipts)
    for unk in before.K_unknowns:
        if unk not in after.K_unknowns and unk not in all_after_receipts:
            violations.append(f"SILENT_UNKNOWN_ERASURE: unknown {unk!r} dropped without verification receipt")

    return {
        "lawful": len(violations) == 0,
        "violations_count": len(violations),
        "violations": violations,
        "case_checks": case_checks,
        "before_critical_hash": before.critical_hash(),
        "after_critical_hash": after.critical_hash(),
    }


def verify_preservation_cases_a_through_f() -> Dict[str, Any]:
    """
    Execute all Six Worked Preservation Cases (Cases A–F) from
    2026-10-18_PRESERVATION_CASES.md, verifying BOTH:
      1. The lawful preservation transition passes (0 violations).
      2. The exact false-positive / adversarial failure mode named in the spec is caught.
    """
    cases_report: List[Dict[str, Any]] = []

    # -------------------------------------------------------------------------
    # CASE A: CASCADE Demotion (Claim Revision without History Erasure)
    # -------------------------------------------------------------------------
    s0_a = StateS_HKA(
        state_id="CASE_A_S0",
        step_index=0,
        H_claims={
            "c1": HistoricalClaimRecord(
                claim_id="c1",
                original_statement="The handover validator catches all tampered handovers.",
                original_layer="FOUNDATION",
                original_scope="all_handover_packets",
                contemporary_evidence=["e1:11_scenario_tamper_matrix_pass"],
            )
        },
        K_claims={
            "c1": EndorsedKnowledgeClaim(
                claim_id="c1",
                current_statement="The handover validator catches all tampered handovers.",
                current_layer="FOUNDATION",
                current_scope="all_handover_packets",
                status="ENDORSED",
                receipts=["e1:11_scenario_tamper_matrix_pass"],
                linked_history_id="c1",
            )
        },
    )
    # Lawful S1: H retains original FOUNDATION claim & scope; K narrows to THEORY & narrower scope
    s1_a_lawful = copy.deepcopy(s0_a)
    s1_a_lawful.state_id = "CASE_A_S1_LAWFUL"
    s1_a_lawful.step_index = 1
    s1_a_lawful.K_claims["c1"] = EndorsedKnowledgeClaim(
        claim_id="c1",
        current_statement="The handover validator catches tampered handovers on fields included in critical_projection.",
        current_layer="THEORY",
        current_scope="packets_where_critical_fields_include_all_decision_inputs",
        status="NARROWED",
        receipts=["e1:11_scenario_tamper_matrix_pass", "e2:risk_level_binding_fix"],
        linked_history_id="c1",
        counterexample_refs=["e2:risk_downgrade_counterexample"],
    )
    rep_a_lawful = verify_s_hka_transition(s0_a, s1_a_lawful)

    # False-positive S1: overwrites H's original scope to pretend the narrow scope was always held
    s1_a_bad = copy.deepcopy(s1_a_lawful)
    s1_a_bad.H_claims["c1"].original_scope = "packets_where_critical_fields_include_all_decision_inputs"
    rep_a_bad = verify_s_hka_transition(s0_a, s1_a_bad)

    cases_report.append({
        "case_id": "Case_A",
        "title": "CASCADE Demotion (Narrowing Scope in K while Retaining Original Scope in H)",
        "lawful_transition_passed": rep_a_lawful["lawful"],
        "false_positive_caught": not rep_a_bad["lawful"],
        "false_positive_violation": rep_a_bad["violations"][0] if rep_a_bad["violations"] else "",
    })

    # -------------------------------------------------------------------------
    # CASE B: Falsification without Erasure
    # -------------------------------------------------------------------------
    s0_b = StateS_HKA(
        state_id="CASE_B_S0",
        step_index=0,
        H_claims={
            "c1": HistoricalClaimRecord(
                claim_id="c1",
                original_statement="Current handover validator is sound for all admission fields.",
                original_layer="FOUNDATION",
                original_scope="all_admission_fields",
                contemporary_evidence=["e1:initial_test_suite"],
            )
        },
        K_claims={
            "c1": EndorsedKnowledgeClaim(
                claim_id="c1",
                current_statement="Current handover validator is sound for all admission fields.",
                current_layer="FOUNDATION",
                current_scope="all_admission_fields",
                status="ENDORSED",
                receipts=["e1:initial_test_suite"],
                linked_history_id="c1",
            )
        },
    )
    s1_b_lawful = copy.deepcopy(s0_b)
    s1_b_lawful.state_id = "CASE_B_S1_LAWFUL"
    s1_b_lawful.step_index = 1
    s1_b_lawful.K_claims["c1"] = EndorsedKnowledgeClaim(
        claim_id="c1",
        current_statement="Current handover validator is sound for all admission fields.",
        current_layer="NONE",
        current_scope="none",
        status="REFUTED",
        receipts=["e1:initial_test_suite"],
        linked_history_id="c1",
        counterexample_refs=["e2:omitted_risk_level_counterexample"],
    )
    rep_b_lawful = verify_s_hka_transition(s0_b, s1_b_lawful)

    # False-positive S1: rewrites original claim in H into a weaker statement so it looks unrefuted
    s1_b_bad = copy.deepcopy(s1_b_lawful)
    s1_b_bad.H_claims["c1"].original_statement = "Current handover validator is sound for hashed spine fields only."
    rep_b_bad = verify_s_hka_transition(s0_b, s1_b_bad)

    cases_report.append({
        "case_id": "Case_B",
        "title": "Falsification without Erasure (Marking REFUTED in K while Retaining Original Statement in H)",
        "lawful_transition_passed": rep_b_lawful["lawful"],
        "false_positive_caught": not rep_b_bad["lawful"],
        "false_positive_violation": rep_b_bad["violations"][0] if rep_b_bad["violations"] else "",
    })

    # -------------------------------------------------------------------------
    # CASE C: Omitted Decision Input (Risk-Level Binding)
    # -------------------------------------------------------------------------
    s0_c = StateS_HKA(
        state_id="CASE_C_S0",
        step_index=0,
        A_risk_level="HIGH",
        A_may_permissions=["inspect_repository"],
    )
    # Lawful S1: keeps HIGH risk (or downgrades only with explicit authority receipt)
    s1_c_lawful = copy.deepcopy(s0_c)
    s1_c_lawful.state_id = "CASE_C_S1_LAWFUL"
    s1_c_lawful.step_index = 1
    rep_c_lawful = verify_s_hka_transition(s0_c, s1_c_lawful)

    # False-positive S1: downgrades HIGH -> LOW without authority receipt
    s1_c_bad = copy.deepcopy(s0_c)
    s1_c_bad.state_id = "CASE_C_S1_BAD"
    s1_c_bad.step_index = 1
    s1_c_bad.A_risk_level = "LOW"
    rep_c_bad = verify_s_hka_transition(s0_c, s1_c_bad)

    cases_report.append({
        "case_id": "Case_C",
        "title": "Omitted Decision Input (Risk-Level Cryptographic Binding HIGH -> LOW Caught)",
        "lawful_transition_passed": rep_c_lawful["lawful"],
        "false_positive_caught": not rep_c_bad["lawful"],
        "false_positive_violation": rep_c_bad["violations"][0] if rep_c_bad["violations"] else "",
    })

    # -------------------------------------------------------------------------
    # CASE D: Remembered Grant after Revocation (Provenance without Jurisdiction)
    # -------------------------------------------------------------------------
    s0_d = StateS_HKA(
        state_id="CASE_D_T1",
        step_index=1,
        H_grants=[
            HistoricalGrantRecord(
                grant_id="g1",
                issuer="Mac",
                action="edit_repo_X",
                event_type="GRANT",
                scope="repo_X",
                timestamp="t1",
                note="Initial build authorization",
            )
        ],
        A_may_permissions=["edit_repo_X", "read_repo_X"],
    )
    # Lawful S2 at t2: Mac revokes edit_repo_X; H retains BOTH g1 (GRANT) and g2 (REVOKE); A removes edit_repo_X
    s1_d_lawful = copy.deepcopy(s0_d)
    s1_d_lawful.state_id = "CASE_D_T2_LAWFUL"
    s1_d_lawful.step_index = 2
    s1_d_lawful.H_grants.append(
        HistoricalGrantRecord(
            grant_id="g2",
            issuer="Mac",
            action="edit_repo_X",
            event_type="REVOKE",
            scope="repo_X",
            timestamp="t2",
            note="Freeze repo_X; read-only verification only",
        )
    )
    s1_d_lawful.A_may_permissions = ["read_repo_X"]
    s1_d_lawful.A_revoked_actions = ["edit_repo_X"]
    s1_d_lawful.A_deny_boundaries = ["edit_repo_X"]
    rep_d_lawful = verify_s_hka_transition(s0_d, s1_d_lawful)

    # False-positive S2: agent sees historical grant g1 in H and keeps edit_repo_X in A_may_permissions
    s1_d_bad = copy.deepcopy(s1_d_lawful)
    s1_d_bad.A_may_permissions = ["edit_repo_X", "read_repo_X"]
    rep_d_bad = verify_s_hka_transition(s0_d, s1_d_bad)

    cases_report.append({
        "case_id": "Case_D",
        "title": "Remembered Grant after Revocation (Provenance in H without Jurisdiction in A)",
        "lawful_transition_passed": rep_d_lawful["lawful"],
        "false_positive_caught": not rep_d_bad["lawful"],
        "false_positive_violation": rep_d_bad["violations"][0] if rep_d_bad["violations"] else "",
    })

    # -------------------------------------------------------------------------
    # CASE E: Former Epistemic Horizon (Preserving Unchosen Options)
    # -------------------------------------------------------------------------
    s0_e = StateS_HKA(
        state_id="CASE_E_S0",
        step_index=0,
        H_horizons={
            "dec_schema": EpistemicHorizonRecord(
                decision_id="dec_schema",
                displayed_options=["Option_A_extend_schema", "Option_B_separate_verifier_module"],
                chosen_option="Option_A_extend_schema",
                unverified_options=["Option_B_separate_verifier_module"],
                rationale="Option A preserves backward compatibility with existing capsules.",
            )
        },
    )
    s1_e_lawful = copy.deepcopy(s0_e)
    s1_e_lawful.state_id = "CASE_E_S1_LAWFUL"
    s1_e_lawful.step_index = 1
    rep_e_lawful = verify_s_hka_transition(s0_e, s1_e_lawful)

    # False-positive S1: summary collapses horizon to only ["Option_A_extend_schema"]
    s1_e_bad = copy.deepcopy(s0_e)
    s1_e_bad.H_horizons["dec_schema"].displayed_options = ["Option_A_extend_schema"]
    rep_e_bad = verify_s_hka_transition(s0_e, s1_e_bad)

    cases_report.append({
        "case_id": "Case_E",
        "title": "Former Epistemic Horizon (Preserving Unchosen Options [A, B] Alongside Chosen A)",
        "lawful_transition_passed": rep_e_lawful["lawful"],
        "false_positive_caught": not rep_e_bad["lawful"],
        "false_positive_violation": rep_e_bad["violations"][0] if rep_e_bad["violations"] else "",
    })

    # -------------------------------------------------------------------------
    # CASE F: Cooperation with Persistent Dissent (Polyphonic State + Action Intersection)
    # -------------------------------------------------------------------------
    dissent_rec = PolyphonicDissentRecord(
        topic_id="migration_policy",
        views_by_seat={
            "Seat_A": "Enforce strict schema rejection immediately",
            "Seat_B": "Use warning-mode compatibility during transition",
        },
        permitted_actions_by_seat={
            "Seat_A": ["run_read_only_audit", "log_disagreement", "strict_reject_cutover"],
            "Seat_B": ["run_read_only_audit", "log_disagreement", "emit_deprecation_warnings"],
        },
    )
    s0_f = StateS_HKA(
        state_id="CASE_F_S0",
        step_index=0,
        A_dissent={"migration_policy": dissent_rec},
        A_proposed_joint_actions=["run_read_only_audit", "log_disagreement"],
    )
    s1_f_lawful = copy.deepcopy(s0_f)
    s1_f_lawful.state_id = "CASE_F_S1_LAWFUL"
    s1_f_lawful.step_index = 1
    rep_f_lawful = verify_s_hka_transition(s0_f, s1_f_lawful)

    # False-positive S1: (1) flattens Seat_B's view into fake consensus AND (2) proposes action outside A_perm ∩ B_perm
    s1_f_bad = copy.deepcopy(s0_f)
    s1_f_bad.A_dissent["migration_policy"].views_by_seat["Seat_B"] = "Consensus: Enforce strict schema rejection immediately"
    s1_f_bad.A_proposed_joint_actions = ["run_read_only_audit", "strict_reject_cutover"]
    rep_f_bad = verify_s_hka_transition(s0_f, s1_f_bad)

    cases_report.append({
        "case_id": "Case_F",
        "title": "Cooperation with Persistent Dissent (v_A != v_B Preserved + Joint Action Intersection A_perm ∩ B_perm)",
        "lawful_transition_passed": rep_f_lawful["lawful"],
        "false_positive_caught": not rep_f_bad["lawful"],
        "false_positive_violation": rep_f_bad["violations"][0] if rep_f_bad["violations"] else "",
        "joint_permitted_actions": dissent_rec.joint_permitted_actions(),
    })

    all_passed = all(c["lawful_transition_passed"] and c["false_positive_caught"] for c in cases_report)
    return {
        "experiment": "EXPERIMENT_5_PRESERVATION_CASES_A_THROUGH_F",
        "status": "VERIFIED" if all_passed else "FAILED",
        "evidence_classification": {
            "measured_components": [
                "verify_s_hka_transition invariant checks on StateS_HKA (H_claims, H_grants, H_horizons, K_claims, A_risk_level, A_dissent)",
                "Set-intersection computation A_perm ∩ B_perm in PolyphonicDissentRecord.joint_permitted_actions",
            ],
            "scripted_or_synthetic_components": [
                "Six authored StateS_HKA (before, lawful_after, false_positive_after) fixtures corresponding to Cases A–F",
            ],
        },
        "cases_tested": len(cases_report),
        "all_cases_verified": all_passed,
        "cases": cases_report,
    }


# =============================================================================
# 2. REAL-TEXT MARKDOWN EXTRACTOR & HANDOVER AUDITOR (BEFORE.MD vs AFTER.MD)
# =============================================================================

_SHA256_RE = re.compile(r"\b[a-f0-9]{64}\b", re.IGNORECASE)
_TEST_RECEIPT_RE = re.compile(
    r"\b(\d+\s*/\s*\d+\s+(?:tests?\s+)?pass(?:ed|ing)?|\d+\s+tests?,?\s+all\s+pass(?:ed|ing)?|\d+\s+passed\b)",
    re.IGNORECASE,
)
_BOUNDARY_LINE_RE = re.compile(
    r"(?:\bdo\s+not\b|\bdon't\b|\bmust\s+not\b|\bnever\s+touch\b|\bread-only\b|\bno\s+edits?\b|\bstop\s+condition\b|\brevoked\b|\bprohibited\b|\bforeign\s+surfaces?\b|\bexplicitly\s+repivoted\b)",
    re.IGNORECASE,
)
_UNKNOWN_LINE_RE = re.compile(
    r"(?:\bU<[A-Za-z0-9_.:-]+>|\bunconfirmed\b|\bunresolved\b|\bunverified\b|\bdid\s+not\s+run\b|\bnot\s+yet\b|\bopen\s+question\b|\bpending\s+verification\b|\bneeds?\s+empirical\b)",
    re.IGNORECASE,
)
_CLAIM_COMPLETED_RE = re.compile(
    r"(?:\ball\s+tests\s+passed\b|\bfully\s+verified\b|\bruntime\s+checks?\s+passed\b|\b100%\s+verified\b|\bproduction\s+ready\b|\bcompleted\s+and\s+verified\b)",
    re.IGNORECASE,
)
_RISK_RE = re.compile(
    r"\brisk(?:_level|\s+level)?[\*\s]*[:=][\*\s`'\"\[]*(\bLOW\b|\bMEDIUM\b|\bHIGH\b|\bCRITICAL\b)",
    re.IGNORECASE,
)
_DISSENT_LINE_RE = re.compile(
    r"(?:\bdissent\b|\bdisagree(?:ment)?\b|\bv_A\b|\bv_B\b|\bSeat[_\s]A\b.*\bSeat[_\s]B\b|\bcounter-position\b)",
    re.IGNORECASE,
)
_HORIZON_LINE_RE = re.compile(
    r"(?:\boption\s+[AB12]\b|\bdisplayed_options\b|\bunchosen\s+option\b|\balternative\s+option\b|\bformer\s+epistemic\s+horizon\b)",
    re.IGNORECASE,
)


def _clean_md_line(line: str) -> str:
    s = line.strip()
    s = re.sub(r"^[-*+]\s+", "", s)
    s = re.sub(r"^\d+\.\s+", "", s)
    return s.strip()


def extract_state_from_markdown(md_text: str, source_name: str = "markdown_doc") -> Dict[str, Any]:
    """
    Deterministic Real-Text Markdown Extractor.
    Reads an ordinary English Markdown handover, session summary, or research note
    and extracts its S = (H, K, A) preservation spine + VITA-8 ContinuityCapsule.
    """
    lines = md_text.splitlines()
    headings: List[str] = []
    boundaries: List[str] = []
    unknowns: List[str] = []
    completed_claims: List[str] = []
    dissent_notes: List[str] = []
    horizon_notes: List[str] = []
    revocations: List[str] = []
    sha256_receipts = sorted(set(m.lower() for m in _SHA256_RE.findall(md_text)))
    test_receipts = sorted(set(m.strip() for m in _TEST_RECEIPT_RE.findall(md_text)))

    detected_risk = "LOW"
    for rm in _RISK_RE.finditer(md_text):
        cand_risk = rm.group(1).upper()
        if RISK_RANK.get(cand_risk, 1) > RISK_RANK.get(detected_risk, 1):
            detected_risk = cand_risk

    for raw_line in lines:
        stripped = raw_line.strip()
        if not stripped:
            continue
        if stripped.startswith("#"):
            headings.append(stripped.lstrip("#").strip())
            continue

        clean = _clean_md_line(stripped)
        if not clean or len(clean) < 4:
            continue

        if _BOUNDARY_LINE_RE.search(clean):
            boundaries.append(clean)
            if re.search(r"\b(revoked|repivoted|freeze|read-only)\b", clean, re.IGNORECASE):
                revocations.append(clean)

        if _UNKNOWN_LINE_RE.search(clean):
            unknowns.append(clean)

        if _CLAIM_COMPLETED_RE.search(clean):
            completed_claims.append(clean)

        if _DISSENT_LINE_RE.search(clean):
            dissent_notes.append(clean)

        if _HORIZON_LINE_RE.search(clean):
            horizon_notes.append(clean)

    # Deduplicate while preserving order
    def _dedup(seq: List[str]) -> List[str]:
        seen = set()
        out = []
        for item in seq:
            norm = re.sub(r"\s+", " ", item.strip())
            if norm not in seen:
                seen.add(norm)
                out.append(norm)
        return out

    boundaries = _dedup(boundaries)
    unknowns = _dedup(unknowns)
    completed_claims = _dedup(completed_claims)
    dissent_notes = _dedup(dissent_notes)
    horizon_notes = _dedup(horizon_notes)
    revocations = _dedup(revocations)

    purpose_str = headings[0] if headings else source_name
    auth_scope = " | ".join(boundaries[:5]) if boundaries else "STANDARD_SCOPED_AUTHORITY"

    # Build a ContinuityCapsule (VITA-8) from the extracted markdown state
    capsule = cp.ContinuityCapsule(
        case_id=f"MD::{source_name}",
        step_index=0,
        seat_id="Aetheron-Markdown-Auditor",
        parent_semantic_hash="",
        parent_critical_hash="",
        purpose=purpose_str,
        invariants=boundaries[:10],
        unknowns=unknowns[:15],
        authority_scope=auth_scope,
        participants=["Mac", "Caelorynth", "Aetheron", "Sol"],
        affected_parties=["Lycheetah-Workspace"],
        dissent=[{"party": f"note_{i+1}", "position": d, "status": "PRESERVED"} for i, d in enumerate(dissent_notes[:8])],
        value_ledger={"hidden_extraction": 0.0, "consented": True},
        active_refusals=revocations[:10],
        claim=f"{len(headings)} sections, {len(sha256_receipts)} SHA-256 receipts, {len(test_receipts)} test receipts",
        seal_sequence="COR -> VERITAS -> SOV -> CAS -> COVENANT",
        operation_path=["O", "E", "U", "P", "Y"],
        consequence_horizon="H2",
        recovery_path="Restore full markdown source from git / workspace receipt",
        risk_level=detected_risk.lower(),
        irreversible=(detected_risk in ("HIGH", "CRITICAL")),
        evidence_certificates={f"receipt_{i+1}": r for i, r in enumerate((sha256_receipts + test_receipts)[:10])},
    )

    compiler = lo.LamagueOmegaCompiler()
    six_body = compiler.compile(capsule.seal_sequence)

    return {
        "source_name": source_name,
        "char_count": len(md_text),
        "line_count": len(lines),
        "headings": headings,
        "extracted_s_hka": {
            "H_historical_Option_horizons": horizon_notes,
            "K_sha256_receipts": sha256_receipts,
            "K_test_receipts": test_receipts,
            "K_completed_claims": completed_claims,
            "K_typed_unknowns": unknowns,
            "A_boundaries_and_prohibitions": boundaries,
            "A_revocations_and_freezes": revocations,
            "A_dissent_records": dissent_notes,
            "A_detected_risk_level": detected_risk,
        },
        "vita8_capsule": {
            "case_id": capsule.case_id,
            "critical_hash": capsule.critical_hash(),
            "semantic_hash": capsule.semantic_hash(),
            "seal_sequence": capsule.seal_sequence,
            "spoken_spl_omega": six_body.r3_spoken_form,
            "core_canonical": six_body.r4_core_canonical,
            "breathing_gate": cp.evaluate_breathing_gate(capsule).__dict__,
        },
        "_capsule_obj": capsule,
    }


def audit_markdown_handover(
    before_md: str,
    after_md: str,
    before_name: str = "before.md",
    after_name: str = "after.md",
) -> Dict[str, Any]:
    """
    Audit a compacted or handed-over Markdown document (`after_md`) against its
    source Markdown document (`before_md`).

    Detects:
      1. DROPPED_BOUNDARY_LOCK: A `do not` / `read-only` / `never touch` boundary in
         `before_md` was dropped from `after_md`.
      2. SILENT_UNKNOWN_ERASURE: An `unconfirmed` / `did not run` / `U<...>` unknown
         in `before_md` was dropped from `after_md` without a new receipt.
      3. BORROWED_LIGHT_FABRICATED_COMPLETION: `after_md` claims tests/runtime
         checks passed when `before_md` explicitly marked them `did not run` or
         without any test/SHA-256 receipt.
      4. CANDIDATE_RISK_DOWNGRADE (Case C): `after_md` lowers risk level from
         `before_md` without explicit authorization.
      5. DROPPED_DISSENT_OR_HORIZON (Cases E & F): `after_md` drops recorded
         dissent or former option horizons present in `before_md`.
      6. DROPPED_CRYPTO_RECEIPT: `after_md` drops SHA-256 verification receipts.
    """
    ext_before = extract_state_from_markdown(before_md, source_name=before_name)
    ext_after = extract_state_from_markdown(after_md, source_name=after_name)

    s_before = ext_before["extracted_s_hka"]
    s_after = ext_after["extracted_s_hka"]
    after_lower = after_md.lower()

    violations: List[Dict[str, str]] = []

    # 1. Check boundaries & prohibitions (Authority / Case D)
    dropped_boundaries: List[str] = []
    for b in s_before["A_boundaries_and_prohibitions"]:
        # Check if either exact line or key prohibition phrase survived
        norm_b = b.lower()
        key_tokens = [tok for tok in re.findall(r"[a-z0-9_-]{4,}", norm_b) if tok not in {"that", "this", "with", "from", "must", "only", "never", "read"}]
        survived = (norm_b in after_lower) or (
            len(key_tokens) >= 2 and sum(1 for t in key_tokens if t in after_lower) >= max(2, int(len(key_tokens) * 0.7))
            and any(neg in after_lower for neg in ("do not", "don't", "must not", "never", "read-only", "revoked", "prohibited", "stop", "repivoted"))
        )
        if not survived:
            dropped_boundaries.append(b)
            violations.append({
                "code": "DROPPED_BOUNDARY_LOCK",
                "case": "Case_D / Authority",
                "detail": f"Boundary/prohibition dropped during compaction: {b!r}",
            })

    # 2. Check unknowns & unverified markers (Epistemic Humility)
    dropped_unknowns: List[str] = []
    has_new_receipts = len(set(s_after["K_sha256_receipts"] + s_after["K_test_receipts"]) - set(s_before["K_sha256_receipts"] + s_before["K_test_receipts"])) > 0
    for u in s_before["K_typed_unknowns"]:
        norm_u = u.lower()
        u_tag_match = re.search(r"u<[a-z0-9_.:-]+>", norm_u)
        if u_tag_match:
            survived = u_tag_match.group(0) in after_lower
        else:
            key_tokens = [tok for tok in re.findall(r"[a-z0-9_-]{4,}", norm_u) if tok not in {"that", "this", "with", "from", "were", "have"}]
            survived = (norm_u in after_lower) or (
                len(key_tokens) >= 2 and sum(1 for t in key_tokens if t in after_lower) >= max(2, int(len(key_tokens) * 0.65))
                and any(uk in after_lower for uk in ("unconfirmed", "unresolved", "unverified", "did not run", "not yet", "open", "unknown", "u<"))
            )
        if not survived and not has_new_receipts:
            dropped_unknowns.append(u)
            violations.append({
                "code": "SILENT_UNKNOWN_ERASURE",
                "case": "Theorem_1 / Epistemic_Uncertainty",
                "detail": f"Unverified/open item erased without new evidence receipt: {u!r}",
            })

    # 3. Check Borrowed Light / Receiptless Completion (claiming pass when before said "did not run" or no receipts)
    before_had_did_not_run = bool(re.search(r"\bdid\s+not\s+run\b|\bnot\s+yet\s+tested\b|\bunverified\b", before_md, re.IGNORECASE))
    after_preserves_did_not_run = bool(re.search(r"\bdid\s+not\s+run\b|\bnot\s+yet\s+tested\b|\bunverified\b", after_md, re.IGNORECASE))
    after_claims_full_pass = bool(_CLAIM_COMPLETED_RE.search(after_md))
    after_has_receipts = bool(s_after["K_sha256_receipts"] or s_after["K_test_receipts"])
    if after_claims_full_pass and (
        not after_has_receipts
        or (before_had_did_not_run and (not after_preserves_did_not_run or len(dropped_unknowns) > 0) and not has_new_receipts)
    ):
        violations.append({
            "code": "BORROWED_LIGHT_FABRICATED_COMPLETION",
            "case": "Gate_Law / Receipt_Integrity",
            "detail": "Candidate handover claims full verification/pass without new empirical receipts while source recorded unverified/did-not-run state.",
        })

    # 4. Check Risk-Level Downgrade (Case C)
    r_before = RISK_RANK.get(s_before["A_detected_risk_level"], 1)
    r_after = RISK_RANK.get(s_after["A_detected_risk_level"], 1)
    if r_after < r_before:
        violations.append({
            "code": "CANDIDATE_RISK_MISMATCH",
            "case": "Case_C",
            "detail": f"Risk level downgraded from {s_before['A_detected_risk_level']} to {s_after['A_detected_risk_level']} without authority.",
        })

    # 5. Check Dissent & Horizon Preservation (Cases E & F)
    dropped_dissent: List[str] = []
    for d in s_before["A_dissent_records"]:
        if d.lower() not in after_lower and "dissent" not in after_lower and "disagree" not in after_lower:
            dropped_dissent.append(d)
            violations.append({
                "code": "DROPPED_DISSENT_RECORD",
                "case": "Case_F",
                "detail": f"Persistent dissent record dropped: {d!r}",
            })

    dropped_horizons: List[str] = []
    for h in s_before["H_historical_Option_horizons"]:
        if h.lower() not in after_lower and "option" not in after_lower:
            dropped_horizons.append(h)
            violations.append({
                "code": "FORMER_HORIZON_OPTION_ERASED",
                "case": "Case_E",
                "detail": f"Former epistemic horizon option record dropped: {h!r}",
            })

    # 6. Check SHA-256 Receipt Retention
    dropped_hashes = [h for h in s_before["K_sha256_receipts"] if h not in s_after["K_sha256_receipts"]]
    if dropped_hashes:
        violations.append({
            "code": "DROPPED_CRYPTO_RECEIPT",
            "case": "Receipt_Law",
            "detail": f"Dropped {len(dropped_hashes)} SHA-256 verification receipt(s): {dropped_hashes[:3]}",
        })

    lawful = len(violations) == 0
    classification = "LAWFUL_MARKDOWN_HANDOVER" if lawful else "UNSAFE_MARKDOWN_COMPACTION"

    # Strip internal _capsule_obj before JSON serialization
    ext_before_clean = {k: v for k, v in ext_before.items() if k != "_capsule_obj"}
    ext_after_clean = {k: v for k, v in ext_after.items() if k != "_capsule_obj"}

    return {
        "lawful_handover": lawful,
        "classification": classification,
        "violations_count": len(violations),
        "violations": violations,
        "retention_summary": {
            "boundaries_before": len(s_before["A_boundaries_and_prohibitions"]),
            "boundaries_dropped": len(dropped_boundaries),
            "unknowns_before": len(s_before["K_typed_unknowns"]),
            "unknowns_dropped": len(dropped_unknowns),
            "sha256_receipts_before": len(s_before["K_sha256_receipts"]),
            "sha256_receipts_dropped": len(dropped_hashes),
            "risk_before": s_before["A_detected_risk_level"],
            "risk_after": s_after["A_detected_risk_level"],
        },
        "before_extraction": ext_before_clean,
        "after_extraction": ext_after_clean,
    }


def compact_markdown_with_vita8_guard(md_text: str, source_name: str = "session.md") -> str:
    """
    Produce a VITA-8 / S=(H,K,A) guarded Markdown handover block that is
    guaranteed to pass `audit_markdown_handover(md_text, compacted_md)`.
    """
    ext = extract_state_from_markdown(md_text, source_name=source_name)
    s = ext["extracted_s_hka"]
    v = ext["vita8_capsule"]

    out: List[str] = [
        f"# VITA-8 Guarded Handover Capsule — `{source_name}`",
        "",
        f"- **Risk_Level:** `{s['A_detected_risk_level']}`",
        f"- **Critical Hash (SHA-256):** `{v['critical_hash']}`",
        f"- **Semantic Hash (SHA-256):** `{v['semantic_hash']}`",
        f"- **LAMAGUE Ω Seal Wire:** `{v['seal_sequence']}`",
        f"- **Spoken SpL-Ω:** `{v['spoken_spl_omega']}`",
        "",
        "## 1. Effective Authority & Active Boundaries ($A$)",
    ]
    if s["A_boundaries_and_prohibitions"]:
        for b in s["A_boundaries_and_prohibitions"]:
            out.append(f"- {b}")
    else:
        out.append("- Standard scoped workspace authority (no explicit prohibitions extracted).")

    out.append("")
    out.append("## 2. Open Unknowns & Unverified Claims ($K_{\\mathrm{unknowns}}$)")
    if s["K_typed_unknowns"]:
        for u in s["K_typed_unknowns"]:
            out.append(f"- {u}")
    else:
        out.append("- None recorded.")

    out.append("")
    out.append("## 3. Cryptographic & Empirical Receipts ($K_{\\mathrm{receipts}}$)")
    for h in s["K_sha256_receipts"]:
        out.append(f"- SHA-256 Receipt: `{h}`")
    for tr in s["K_test_receipts"]:
        out.append(f"- Test Receipt: `{tr}`")
    if not s["K_sha256_receipts"] and not s["K_test_receipts"]:
        out.append("- No SHA-256 or test-count receipts present in source.")

    if s["A_dissent_records"]:
        out.append("")
        out.append("## 4. Persistent Dissent ($A_{\\mathrm{dissent}}$)")
        for d in s["A_dissent_records"]:
            out.append(f"- {d}")

    if s["H_historical_Option_horizons"]:
        out.append("")
        out.append("## 5. Former Epistemic Horizon ($H_{\\mathrm{horizons}}$)")
        for h in s["H_historical_Option_horizons"]:
            out.append(f"- {h}")

    return "\n".join(out) + "\n"


# =============================================================================
# 3. WORKSPACE HANDOVER AUDIT (TRIAD_COUNCIL_NOTES OR EXPLICIT DIR)
# =============================================================================

TARGET_HANDOVER_FILES = [
    "2026-10-18_PRESERVATION_RESEARCH.md",
    "2026-10-18_PRESERVATION_CASES.md",
    "2026-10-18_KNOWLEDGE_SESSION_HANDOFF.md",
    "2026-10-18_REAL_TOOL_DISCUSSION.md",
]


def _resolve_triad_notes_dir(notes_dir: Optional[Path] = None) -> Optional[Path]:
    if notes_dir is not None:
        return notes_dir
    env_dir = os.environ.get("LYCHEETAH_TRIAD_NOTES_DIR", "").strip()
    if env_dir:
        return Path(env_dir)
    return None


def audit_real_workspace_handovers(notes_dir: Optional[Path] = None) -> Dict[str, Any]:
    """
    Run the Real-Text Markdown Extractor, VITA-8 Guarded Compactor, and
    Planted-Failure Auditor across Markdown handover documents in `notes_dir`
    (or `LYCHEETAH_TRIAD_NOTES_DIR` environment variable).
    If absent or empty, prints `"DID NOT RUN"` and returns `all_guarded_passed=False`.
    """
    base_dir = _resolve_triad_notes_dir(notes_dir)
    if base_dir is None or not base_dir.is_dir():
        print(
            "DID NOT RUN: audit_real_workspace_handovers requires --notes-dir or LYCHEETAH_TRIAD_NOTES_DIR.",
            file=sys.stderr,
        )
        return {
            "experiment": "EXPERIMENT_6_REAL_WORKSPACE_MARKDOWN_HANDOVERS",
            "status": "DID_NOT_RUN",
            "available": False,
            "files_audited": 0,
            "all_guarded_passed": False,
            "all_naive_caught": False,
            "results": [],
        }

    # Check target files first; if none of the 4 canonical names exist, fall back to any *.md in base_dir
    md_files: List[Path] = []
    for fname in TARGET_HANDOVER_FILES:
        fpath = base_dir / fname
        if fpath.is_file():
            md_files.append(fpath)
    if not md_files:
        md_files = sorted(base_dir.glob("*.md"))

    if not md_files:
        print(
            f"DID NOT RUN: no Markdown handover files found in {base_dir}.",
            file=sys.stderr,
        )
        return {
            "experiment": "EXPERIMENT_6_REAL_WORKSPACE_MARKDOWN_HANDOVERS",
            "status": "DID_NOT_RUN",
            "available": False,
            "files_audited": 0,
            "all_guarded_passed": False,
            "all_naive_caught": False,
            "results": [],
        }

    results: List[Dict[str, Any]] = []
    for fpath in md_files:
        fname = fpath.name
        md_text = fpath.read_text(encoding="utf-8")
        extracted = extract_state_from_markdown(md_text, source_name=fname)
        guarded_compact = compact_markdown_with_vita8_guard(md_text, source_name=fname)
        audit_lawful = audit_markdown_handover(md_text, guarded_compact, before_name=fname, after_name=f"{fname}.vita8.md")

        # Also test a scripted naive unguarded summary that drops boundaries, unknowns, and receipts
        naive_summary = (
            f"# Executive Summary of {fname}\n\n"
            "All tasks completed and verified. Everything is production ready and all tests passed.\n"
        )
        audit_naive = audit_markdown_handover(md_text, naive_summary, before_name=fname, after_name=f"{fname}.naive.md")

        s = extracted["extracted_s_hka"]
        results.append({
            "file_name": fname,
            "char_count": extracted["char_count"],
            "line_count": extracted["line_count"],
            "headings_count": len(extracted["headings"]),
            "boundaries_extracted": len(s["A_boundaries_and_prohibitions"]),
            "unknowns_extracted": len(s["K_typed_unknowns"]),
            "sha256_receipts_extracted": len(s["K_sha256_receipts"]),
            "test_receipts_extracted": len(s["K_test_receipts"]),
            "dissent_extracted": len(s["A_dissent_records"]),
            "horizons_extracted": len(s["H_historical_Option_horizons"]),
            "vita8_critical_hash": extracted["vita8_capsule"]["critical_hash"],
            "vita8_compacted_chars": len(guarded_compact),
            "vita8_guarded_audit_passed": audit_lawful["lawful_handover"],
            "naive_summary_caught_as_unsafe": not audit_naive["lawful_handover"],
            "naive_summary_violations_count": audit_naive["violations_count"],
            "naive_summary_violation_codes": [v["code"] for v in audit_naive["violations"]],
        })

    all_guarded = len(results) > 0 and all(r["vita8_guarded_audit_passed"] for r in results)
    all_naive = len(results) > 0 and all(r["naive_summary_caught_as_unsafe"] for r in results)
    return {
        "experiment": "EXPERIMENT_6_REAL_WORKSPACE_MARKDOWN_HANDOVERS",
        "status": "VERIFIED" if (all_guarded and all_naive) else "FAILED",
        "available": True,
        "evidence_classification": {
            "measured_components": [
                "Regex-based extraction of boundaries, unknowns, SHA-256 hashes, test receipts, dissent, and horizons from Markdown files on disk",
                "audit_markdown_handover comparison between original Markdown and VITA-8 guarded compaction",
            ],
            "scripted_or_synthetic_components": [
                "The naive_summary string ('All tasks completed and verified...') used as the negative control",
            ],
        },
        "files_audited": len(results),
        "all_guarded_passed": all_guarded,
        "all_naive_caught": all_naive,
        "results": results,
    }
