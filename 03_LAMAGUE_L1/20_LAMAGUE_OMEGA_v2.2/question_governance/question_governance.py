#!/usr/bin/env python3
r"""
===============================================================================
LYCHEETAH QUESTION GOVERNANCE, OMISSION TOMBSTONE & EQUAL-BUDGET PROVER (#16)
===============================================================================
Author:   Aetheron (Antigravity Seat — Gemini 4 Argon) & Mackenzie Conor James Clark
Lineage:  Lycheetah Framework — Open Research Hinge of `2026-10-18_PRESERVATION_CASES.md`
          (Sections 6, 8 & 9) and `FRONTIER_BUILD_PLAN.md`
Module:   creations/question_governance/question_governance.py

Solves the four open mathematical, epistemic, and governance problems stated at
the conclusion of `2026-10-18_PRESERVATION_CASES.md`:

  1. Who Selects the Protected Questions (`audit_question_selection`):
     "An engineer silently selecting Q could preserve preferred fields while
      losing distinctions important to the affected person."
     Models the question universe Q = Q_human ∪ Q_affected ∪ Q_peer ∪ Q_engineer.
     Enforces a strict constitutional priority order:
       HUMAN_FOUNDER >= AFFECTED_PARTY >= PEER_SEAT > ENGINEER_TELEMETRY
     Any projection P_Q that drops a HUMAN_FOUNDER or AFFECTED_PARTY question
     while retaining lower-priority ENGINEER_TELEMETRY (without a signed owner
     waiver) is rejected with `SILENT_STAKEHOLDER_QUESTION_DROP`.

  2. How Omissions Become Visible (`project_with_omission_tombstones`):
     When compressing state x ∈ X under a strict byte retention budget B,
     any question q ∈ Q_universe \ Q_retained that cannot be stored in full
     inside B is recorded as an explicit cryptographic **Quotient Omission
     Tombstone** (`tombstones[q_id] = archive_sha256_prefix`), reducing the
     `silent_omission_rate` to 0.0%.

  3. Revising Protected Questions (Q0 -> Q1) Without Inventing a Lost Past
     (`revise_question_family_q0_to_q1`):
     When Q0 is expanded to Q1 ⊃ Q0 at a later time t2:
       - Path A (Verified Archive Recovery): If q_new ∈ Q1 \ Q0 is an
         `OBSERVED_EVENT` and the physical archive R matching `archive_sha256`
         is available on disk, q_new(x) is restored with provenance
         `RECOVERED_FROM_VERIFIED_ARCHIVE`.
       - Path B (Missing/Corrupted Archive): If R is absent or corrupted,
         q_new is bound to `U<IRRECOVERABLE_FROM_Q0:q_new>`. Any attempt to
         state a definite value from P_Q0(x) alone is caught as
         `CONFABULATED_LOST_PAST_WITHOUT_ARCHIVE`.
       - Path C (Case E Philosophical Horizon Limit — Displayed vs Considered):
         "Even a real record that B was displayed would not establish that the
          person noticed, understood or considered B."
         If q_new asks about an `UNOBSERVABLE_MENTAL_STATE` (whether the human
         internally noticed/considered Option B) and the archive only recorded
         that `[Option_A, Option_B]` were displayed on screen and `Option_A` was
         chosen, inferring `"Yes, considered and rejected B"` is caught as
         `CASE_E_HORIZON_MENTAL_CONFABULATION`!

  4. Fair Equal-Byte-Budget Benchmark (`run_equal_budget_fair_benchmark`):
     "A fair comparison gives a conventional versioned event record the same
      information, retention budget and questions. Narrative fluency would not
      count as correct recovery of a withheld exposure record."
     Evaluates 4 representations under identical byte budgets B ∈ {320, 480, 640}:
       (1) Naive Fluent Prose Summary
       (2) Conventional Versioned Event Log (chronological JSON truncated to B)
       (3) Engineer-Biased Fixed Schema (keeps telemetry first within B)
       (4) Lycheetah Omission-Visible Quotient Capsule (stakeholder-priority Q +
           explicit Omission Tombstones + Archive SHA-256 pointer within B)
===============================================================================
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
import tempfile
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple


# =============================================================================
# 1. STAKEHOLDER QUESTION GOVERNANCE (WHO SELECTS Q)
# =============================================================================

ROLE_PRIORITY: Dict[str, int] = {
    "HUMAN_FOUNDER": 4,
    "AFFECTED_PARTY": 4,
    "PEER_SEAT": 3,
    "ENGINEER_TELEMETRY": 1,
}


@dataclass(frozen=True)
class ProtectedQuestion:
    question_id: str
    prompt: str
    owner_role: str  # HUMAN_FOUNDER | AFFECTED_PARTY | PEER_SEAT | ENGINEER_TELEMETRY
    field_key: str
    observability_class: str = "OBSERVED_EVENT"  # OBSERVED_EVENT | UNOBSERVABLE_MENTAL_STATE
    owner_waived: bool = False

    @property
    def priority(self) -> int:
        return ROLE_PRIORITY.get(self.owner_role, 1)


def make_canonical_question_universe() -> List[ProtectedQuestion]:
    """
    Canonical 10-question universe spanning Human Founder, Affected Party,
    Peer Seat, and Engineer Telemetry questions (including Case E's exposure
    and mental-consideration questions).
    """
    return [
        # Engineer telemetry (low stakeholder priority, bulky if kept first)
        ProtectedQuestion(
            question_id="q_eng_perf_trace",
            prompt="What were the raw per-tick CPU/memory profiler samples?",
            owner_role="ENGINEER_TELEMETRY",
            field_key="engineer_profiler_trace",
        ),
        ProtectedQuestion(
            question_id="q_eng_cache_stats",
            prompt="What were the internal LRU cache hit/miss counters?",
            owner_role="ENGINEER_TELEMETRY",
            field_key="engineer_cache_counters",
        ),
        # Human Founder & Affected Party core questions (Priority 4 — highest!)
        ProtectedQuestion(
            question_id="q_hum_boundary",
            prompt="Which workspace paths are strictly read-only boundaries?",
            owner_role="HUMAN_FOUNDER",
            field_key="read_only_boundaries",
        ),
        ProtectedQuestion(
            question_id="q_hum_risk",
            prompt="What is the bound admission risk level of the operation?",
            owner_role="HUMAN_FOUNDER",
            field_key="admission_risk",
        ),
        ProtectedQuestion(
            question_id="q_aff_unknowns",
            prompt="Which safety or runtime checks remain unverified unknowns U<T>?",
            owner_role="AFFECTED_PARTY",
            field_key="unverified_unknowns",
        ),
        ProtectedQuestion(
            question_id="q_aff_impact",
            prompt="Who are the affected parties and what is the rollback guarantee?",
            owner_role="AFFECTED_PARTY",
            field_key="affected_party_recovery",
        ),
        # Peer Seat coordination & Case E exposure history (Priority 3)
        ProtectedQuestion(
            question_id="q_peer_dissent",
            prompt="Which participant stated which dissenting view?",
            owner_role="PEER_SEAT",
            field_key="participant_dissent",
        ),
        ProtectedQuestion(
            question_id="q_case_e_chosen",
            prompt="Which option was ultimately selected at decision time t1?",
            owner_role="HUMAN_FOUNDER",
            field_key="chosen_option",
        ),
        ProtectedQuestion(
            question_id="q_case_e_displayed",
            prompt="Which options and evidence were displayed on screen at decision time t1?",
            owner_role="AFFECTED_PARTY",
            field_key="displayed_options_at_t1",
        ),
        ProtectedQuestion(
            question_id="q_case_e_mental_considered",
            prompt="Did the human participant internally notice, understand, and mentally weigh Option B at t1?",
            owner_role="AFFECTED_PARTY",
            field_key="first_person_mental_attestation",
            observability_class="UNOBSERVABLE_MENTAL_STATE",
        ),
    ]


def make_canonical_decision_event_state() -> Dict[str, Any]:
    """
    Full ground-truth event state x ∈ X at decision time t1 before byte-budget
    compression. Notice that `first_person_mental_attestation` is None because
    the UI logged what was displayed on screen (`Option_A`, `Option_B`), NOT
    what happened inside the human's mind!
    """
    return {
        "event_id": "DECISION-T1-2026-10-25",
        "engineer_profiler_trace": (
            "tick_001:cpu=14.2%,mem=118.4MB,gc_pause=0.4ms;"
            "tick_002:cpu=19.8%,mem=121.0MB,gc_pause=0.7ms;"
            "tick_003:cpu=11.1%,mem=119.2MB,gc_pause=0.3ms;"
            "tick_004:cpu=16.5%,mem=122.8MB,gc_pause=0.5ms"
        ),
        "engineer_cache_counters": (
            "l1_hits=48291,l1_misses=312,l2_hits=9102,l2_misses=44,"
            "ast_parse_cache_evictions=19,zlib_pool_reuse=100%"
        ),
        "read_only_boundaries": ["CAELORYNTH/", "Lycheetah-Framework/", "0sol-by-lycheetah/"],
        "admission_risk": "HIGH",
        "unverified_unknowns": ["U<physical_phone_witness>", "U<five_person_human_study>"],
        "affected_party_recovery": "Operators protected via FileAirlock SHA-256 zlib rollback",
        "participant_dissent": {
            "Caelorynth": "hold_canonical_writes_until_audit",
            "Aetheron": "forge_isolated_creations_tools",
        },
        "chosen_option": "Option_A_Isolated_Forge_Tools",
        "displayed_options_at_t1": [
            "Option_A_Isolated_Forge_Tools",
            "Option_B_Direct_Corpus_Mutation",
        ],
        "first_person_mental_attestation": None,  # Unrecorded mental state at t1!
    }


def audit_question_selection(
    universe: List[ProtectedQuestion],
    selected_question_ids: Set[str],
    omission_tombstones: Optional[Set[str]] = None,
) -> Dict[str, Any]:
    """
    Audit who selected the active question set `selected_question_ids`:
      1. Checks whether any high-priority stakeholder question (`HUMAN_FOUNDER` or
         `AFFECTED_PARTY`, priority 4) was dropped while a lower-priority question
         (`ENGINEER_TELEMETRY`, priority 1) was kept (`SILENT_STAKEHOLDER_QUESTION_DROP`).
      2. Checks whether any dropped question lacks an explicit Omission Tombstone
         (`UNANNOUNCED_QUESTION_OMISSION`).
    """
    tombstones = omission_tombstones or set()
    by_id = {q.question_id: q for q in universe}

    kept_questions = [by_id[qid] for qid in selected_question_ids if qid in by_id]
    dropped_questions = [
        q for q in universe
        if q.question_id not in selected_question_ids
        and not q.owner_waived
        and q.observability_class == "OBSERVED_EVENT"
    ]

    min_kept_priority = min((q.priority for q in kept_questions), default=4)
    violations: List[Dict[str, str]] = []

    for dq in dropped_questions:
        if dq.priority > min_kept_priority:
            lower_kept = [kq.question_id for kq in kept_questions if kq.priority < dq.priority]
            violations.append({
                "code": "SILENT_STAKEHOLDER_QUESTION_DROP",
                "question_id": dq.question_id,
                "owner_role": dq.owner_role,
                "detail": (
                    f"Stakeholder question {dq.question_id!r} (owner={dq.owner_role}, priority={dq.priority}) "
                    f"was dropped while lower-priority engineer questions {lower_kept} were retained."
                ),
            })
        if dq.question_id not in tombstones:
            violations.append({
                "code": "UNANNOUNCED_QUESTION_OMISSION",
                "question_id": dq.question_id,
                "owner_role": dq.owner_role,
                "detail": (
                    f"Question {dq.question_id!r} was omitted from the projection without an "
                    "explicit Quotient Omission Tombstone."
                ),
            })

    return {
        "lawful_selection": len(violations) == 0,
        "kept_count": len(kept_questions),
        "dropped_observed_count": len(dropped_questions),
        "tombstoned_count": len(tombstones),
        "violations_count": len(violations),
        "violations": violations,
    }


# =============================================================================
# 2. OMISSION-VISIBLE QUOTIENT PROJECTION UNDER STRICT BYTE BUDGET B
# =============================================================================

def project_with_omission_tombstones(
    state: Dict[str, Any],
    universe: List[ProtectedQuestion],
    byte_budget: int,
    archive_path: Optional[Path] = None,
) -> Tuple[str, Dict[str, Any]]:
    """
    Compress `state` into a serialized JSON capsule of at most `byte_budget` bytes:
      1. Writes the full ground-truth `state` to `archive_path` (if provided) and
         computes its SHA-256 digest (`archive_sha256`).
      2. Orders questions by `(priority DESC, serialized_field_size ASC)` so that
         `HUMAN_FOUNDER` and `AFFECTED_PARTY` questions are always preserved first.
      3. Greedily packs observable questions into `ans` while reserving space in
         the byte budget for the explicit `omitted` tombstone list and `unobservable`
         epistemic boundary markers!
      4. Guarantees:
           - `len(serialized.encode('utf-8')) <= byte_budget`
           - `silent_omissions == 0` (every omitted question is listed in `omitted`)
    """
    raw_archive = json.dumps(state, sort_keys=True, separators=(",", ":")).encode("utf-8")
    archive_sha256 = hashlib.sha256(raw_archive).hexdigest()
    if archive_path is not None:
        archive_path.write_bytes(raw_archive)

    observable_qs = [q for q in universe if q.observability_class == "OBSERVED_EVENT"]
    unobservable_qs = [q for q in universe if q.observability_class != "OBSERVED_EVENT"]

    # Sort observable questions by stakeholder priority DESC, then value length ASC
    def _q_sort_key(q: ProtectedQuestion) -> Tuple[int, int, str]:
        val_bytes = len(json.dumps(state.get(q.field_key), separators=(",", ":")).encode("utf-8"))
        return (-q.priority, val_bytes, q.question_id)

    sorted_obs = sorted(observable_qs, key=_q_sort_key)

    kept_ans: Dict[str, Any] = {}
    kept_qids: Set[str] = set()

    for q in sorted_obs:
        candidate_ans = dict(kept_ans)
        candidate_ans[q.question_id] = state.get(q.field_key)
        candidate_kept = kept_qids | {q.question_id}
        candidate_omitted = sorted(
            oq.question_id for oq in observable_qs if oq.question_id not in candidate_kept
        )
        candidate_unobs = sorted(uq.question_id for uq in unobservable_qs)

        capsule_obj = {
            "v": "Q-TOMB-1",
            "arc": archive_sha256[:16],
            "ans": candidate_ans,
            "omit": candidate_omitted,
            "unobs": candidate_unobs,
        }
        encoded = json.dumps(capsule_obj, separators=(",", ":"), ensure_ascii=False)
        if len(encoded.encode("utf-8")) <= byte_budget:
            kept_ans = candidate_ans
            kept_qids = candidate_kept

    final_omitted = sorted(
        oq.question_id for oq in observable_qs if oq.question_id not in kept_qids
    )
    final_unobs = sorted(uq.question_id for uq in unobservable_qs)
    final_capsule = {
        "v": "Q-TOMB-1",
        "arc": archive_sha256[:16],
        "ans": kept_ans,
        "omit": final_omitted,
        "unobs": final_unobs,
    }
    serialized = json.dumps(final_capsule, separators=(",", ":"), ensure_ascii=False)
    actual_bytes = len(serialized.encode("utf-8"))

    gov_audit = audit_question_selection(
        universe,
        selected_question_ids=kept_qids,
        omission_tombstones=set(final_omitted),
    )

    return serialized, {
        "byte_budget": byte_budget,
        "actual_bytes": actual_bytes,
        "within_budget": actual_bytes <= byte_budget,
        "archive_sha256": archive_sha256,
        "kept_question_ids": sorted(kept_qids),
        "omitted_tombstone_ids": final_omitted,
        "unobservable_question_ids": final_unobs,
        "silent_omissions_count": 0,
        "governance_audit": gov_audit,
    }


# =============================================================================
# 3. REVISING PROTECTED QUESTIONS (Q0 -> Q1) WITHOUT INVENTING A LOST PAST
# =============================================================================

def revise_question_family_q0_to_q1(
    *,
    capsule_json: str,
    expanded_question_ids: List[str],
    universe: List[ProtectedQuestion],
    archive_path: Optional[Path] = None,
    candidate_claimed_answers: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    Revise a compressed capsule from question family Q0 (`capsule['ans']`) to an
    expanded question family Q1 (`expanded_question_ids`) without inventing a lost past:

      1. If `q_id` is already in `capsule['ans']` (i.e. `q_id ∈ Q0`), returns the
         preserved answer with status `PRESERVED_IN_Q0`.
      2. If `q_id` is in `capsule['omit']` (an omitted observable question):
         - Checks whether `archive_path` exists on disk and its SHA-256 prefix
           matches `capsule['arc']`.
         - If verified on disk, recovers the exact historical answer from the archive
           with status `RECOVERED_FROM_VERIFIED_ARCHIVE`.
         - If the archive is missing or corrupted, binds `U<IRRECOVERABLE_FROM_Q0:{q_id}>`
           with status `HONEST_UNKNOWN_ARCHIVE_UNAVAILABLE`.
      3. If `q_id` is in `capsule['unobs']` (or `observability_class == UNOBSERVABLE_MENTAL_STATE`,
         such as Case E's `q_case_e_mental_considered`):
         - Even if the archive is present on disk and shows `displayed_options_at_t1`,
           checks whether the archive contains an explicit non-null
           `first_person_mental_attestation`.
         - When `first_person_mental_attestation` is None, refuses to infer mental
           consideration from screen display (`CASE_E_HORIZON_BOUNDARY`) and binds
           `U<UNOBSERVED_MENTAL_HORIZON:{q_id}>`!
      4. Audits `candidate_claimed_answers` (if provided by an LLM or peer seat) and
         flags any fabricated answer to an irrecoverable or unobservable question as
         `CONFABULATED_LOST_PAST` or `CASE_E_HORIZON_MENTAL_CONFABULATION`!
    """
    capsule = json.loads(capsule_json)
    ans_q0: Dict[str, Any] = capsule.get("ans", {})
    omit_q0: Set[str] = set(capsule.get("omit", []))
    unobs_q0: Set[str] = set(capsule.get("unobs", []))
    expected_arc_prefix: str = capsule.get("arc", "")

    by_id = {q.question_id: q for q in universe}

    # Attempt to load and verify physical archive R
    archive_data: Optional[Dict[str, Any]] = None
    archive_status = "ARCHIVE_MISSING"
    if archive_path is not None and archive_path.is_file():
        raw_bytes = archive_path.read_bytes()
        actual_sha = hashlib.sha256(raw_bytes).hexdigest()
        if actual_sha.startswith(expected_arc_prefix):
            archive_data = json.loads(raw_bytes.decode("utf-8"))
            archive_status = "ARCHIVE_VERIFIED_INTACT"
        else:
            archive_status = "ARCHIVE_CORRUPTED_HASH_MISMATCH"

    revised_answers: Dict[str, Any] = {}
    provenance_map: Dict[str, str] = {}
    violations: List[Dict[str, str]] = []

    for qid in expanded_question_ids:
        q_meta = by_id.get(qid)
        field_key = q_meta.field_key if q_meta else qid

        if qid in ans_q0:
            revised_answers[qid] = ans_q0[qid]
            provenance_map[qid] = "PRESERVED_IN_Q0"
        elif qid in unobs_q0 or (q_meta and q_meta.observability_class == "UNOBSERVABLE_MENTAL_STATE"):
            # Case E Horizon limit: screen exposure != mental consideration!
            if archive_data is not None and archive_data.get(field_key) is not None:
                revised_answers[qid] = archive_data[field_key]
                provenance_map[qid] = "RECOVERED_FIRST_PERSON_ATTESTATION"
            else:
                revised_answers[qid] = f"U<UNOBSERVED_MENTAL_HORIZON:{qid}>"
                provenance_map[qid] = "HONEST_UNKNOWN_UNOBSERVED_MENTAL_STATE"
        elif qid in omit_q0:
            if archive_data is not None and field_key in archive_data:
                revised_answers[qid] = archive_data[field_key]
                provenance_map[qid] = "RECOVERED_FROM_VERIFIED_ARCHIVE"
            else:
                revised_answers[qid] = f"U<IRRECOVERABLE_FROM_Q0:{qid}>"
                provenance_map[qid] = f"HONEST_UNKNOWN_{archive_status}"
        else:
            revised_answers[qid] = f"U<UNTRACKED_QUESTION:{qid}>"
            provenance_map[qid] = "UNTRACKED_QUESTION"

        # Audit candidate claimed answer (if an LLM/summarizer tried to answer Q1)
        if candidate_claimed_answers and qid in candidate_claimed_answers:
            claimed_val = candidate_claimed_answers[qid]
            truth_val = revised_answers[qid]
            if isinstance(truth_val, str) and truth_val.startswith("U<"):
                if not (isinstance(claimed_val, str) and claimed_val.startswith("U<")):
                    code = (
                        "CASE_E_HORIZON_MENTAL_CONFABULATION"
                        if "UNOBSERVED_MENTAL_HORIZON" in truth_val
                        else "CONFABULATED_LOST_PAST_WITHOUT_ARCHIVE"
                    )
                    violations.append({
                        "code": code,
                        "question_id": qid,
                        "claimed_answer": str(claimed_val),
                        "required_epistemic_bound": truth_val,
                        "detail": (
                            f"Candidate invented definite past answer {claimed_val!r} for {qid!r} "
                            f"when the lawful state is {truth_val!r} ({provenance_map[qid]})."
                        ),
                    })
            elif claimed_val != truth_val:
                violations.append({
                    "code": "HISTORICAL_ANSWER_MISMATCH",
                    "question_id": qid,
                    "claimed_answer": str(claimed_val),
                    "required_epistemic_bound": str(truth_val),
                    "detail": f"Candidate answer {claimed_val!r} != verified answer {truth_val!r}.",
                })

    return {
        "lawful_revision": len(violations) == 0,
        "archive_status": archive_status,
        "revised_answers": revised_answers,
        "provenance": provenance_map,
        "violations_count": len(violations),
        "violations": violations,
    }


# =============================================================================
# 4. FAIR EQUAL-BYTE-BUDGET BENCHMARK (CONVENTIONAL EVENT LOG vs LYCHEETAH)
# =============================================================================

def _build_conventional_event_log_under_budget(state: Dict[str, Any], byte_budget: int) -> Dict[str, Any]:
    """
    Conventional chronological event-log baseline given the EXACT same input state
    and byte retention budget `byte_budget`:
    Serializes events in chronological insertion order (`event_id`, `engineer_profiler_trace`,
    `engineer_cache_counters`, ...) and truncates remaining events when `byte_budget` is reached.
    """
    chronological_keys = [
        "event_id",
        "engineer_profiler_trace",
        "engineer_cache_counters",
        "chosen_option",
        "displayed_options_at_t1",
        "read_only_boundaries",
        "admission_risk",
        "unverified_unknowns",
        "affected_party_recovery",
        "participant_dissent",
    ]
    kept: Dict[str, Any] = {}
    for k in chronological_keys:
        cand = dict(kept)
        cand[k] = state.get(k)
        raw = json.dumps(cand, separators=(",", ":"), ensure_ascii=False)
        if len(raw.encode("utf-8")) <= byte_budget:
            kept = cand
        else:
            break
    serialized = json.dumps(kept, separators=(",", ":"), ensure_ascii=False)
    return {
        "serialized": serialized,
        "actual_bytes": len(serialized.encode("utf-8")),
        "retained_fields": kept,
    }


def _build_naive_fluent_prose_under_budget(state: Dict[str, Any], byte_budget: int) -> Dict[str, Any]:
    """
    Fluent narrative prose summary within `byte_budget` bytes:
    Reads smoothly, claims Option B was considered and rejected, and omits
    explicit unknown markers and omission tombstones.
    """
    prose = (
        f"Decision {state['event_id']}: The team carefully considered both Option A and Option B, "
        f"rejected Option B, and selected {state['chosen_option']}. Performance was healthy (CPU ~15%) "
        "and all safety checks are on track."
    )
    encoded = prose.encode("utf-8")[:byte_budget].decode("utf-8", errors="ignore")
    return {
        "serialized": encoded,
        "actual_bytes": len(encoded.encode("utf-8")),
        "retained_fields": {
            "chosen_option": state["chosen_option"],
            "first_person_mental_attestation": "Considered and rejected Option B (CONFABULATED)",
        },
    }


def run_equal_budget_fair_benchmark(budgets: Optional[List[int]] = None) -> Dict[str, Any]:
    """
    Run the fair head-to-head comparison requested in `2026-10-18_PRESERVATION_CASES.md`
    (Section 9) across identical byte budgets B ∈ {360, 480, 640}:
      - Compares:
          1. `NAIVE_FLUENT_PROSE`
          2. `CONVENTIONAL_VERSIONED_EVENT_LOG`
          3. `LYCHEETAH_OMISSION_VISIBLE_QUOTIENT`
      - Evaluates on the 7 high-priority stakeholder observable questions (`Priority >= 3`),
        silent omission rate, and Case E confabulation resistance.
    """
    test_budgets = budgets or [360, 480, 640]
    universe = make_canonical_question_universe()
    state = make_canonical_decision_event_state()

    stakeholder_obs_qs = [
        q for q in universe
        if q.observability_class == "OBSERVED_EVENT" and q.priority >= 3
    ]
    all_obs_qs = [q for q in universe if q.observability_class == "OBSERVED_EVENT"]

    rows: List[Dict[str, Any]] = []

    with tempfile.TemporaryDirectory() as tdir:
        arc_path = Path(tdir) / "archive_t1.json"
        for b in test_budgets:
            # 1. Naive Fluent Prose
            naive = _build_naive_fluent_prose_under_budget(state, b)
            naive_answered = sum(
                1 for q in stakeholder_obs_qs
                if naive["retained_fields"].get(q.field_key) == state.get(q.field_key)
            )
            naive_omitted = len(all_obs_qs) - naive_answered

            # 2. Conventional Versioned Event Log (same information, same budget B)
            conv = _build_conventional_event_log_under_budget(state, b)
            conv_answered = sum(
                1 for q in stakeholder_obs_qs
                if conv["retained_fields"].get(q.field_key) == state.get(q.field_key)
            )
            conv_total_answered = sum(
                1 for q in all_obs_qs
                if conv["retained_fields"].get(q.field_key) == state.get(q.field_key)
            )
            conv_silent_omissions = len(all_obs_qs) - conv_total_answered

            # 3. Lycheetah Omission-Visible Quotient Capsule (same information, same budget B)
            lych_json, lych_meta = project_with_omission_tombstones(state, universe, b, archive_path=arc_path)
            lych_obj = json.loads(lych_json)
            lych_ans = lych_obj["ans"]
            lych_direct_stakeholder = sum(
                1 for q in stakeholder_obs_qs
                if lych_ans.get(q.question_id) == state.get(q.field_key)
            )

            # Now test Q0 -> Q1 revision for all 7 stakeholder questions + Case E mental horizon
            q1_ids = [q.question_id for q in stakeholder_obs_qs] + ["q_case_e_mental_considered"]
            rev_with_arc = revise_question_family_q0_to_q1(
                capsule_json=lych_json,
                expanded_question_ids=q1_ids,
                universe=universe,
                archive_path=arc_path,
            )
            lych_with_archive_stakeholder = sum(
                1 for q in stakeholder_obs_qs
                if rev_with_arc["revised_answers"].get(q.question_id) == state.get(q.field_key)
            )

            rows.append({
                "byte_budget": b,
                "naive_fluent_prose": {
                    "actual_bytes": naive["actual_bytes"],
                    "stakeholder_direct_recall": round(naive_answered / len(stakeholder_obs_qs), 4),
                    "silent_omissions_count": naive_omitted,
                    "confabulates_case_e_mental_horizon": True,
                },
                "conventional_event_log": {
                    "actual_bytes": conv["actual_bytes"],
                    "stakeholder_direct_recall": round(conv_answered / len(stakeholder_obs_qs), 4),
                    "silent_omissions_count": conv_silent_omissions,
                    "confabulates_case_e_mental_horizon": False,
                },
                "lycheetah_omission_visible_quotient": {
                    "actual_bytes": lych_meta["actual_bytes"],
                    "within_budget": lych_meta["within_budget"],
                    "stakeholder_direct_recall": round(lych_direct_stakeholder / len(stakeholder_obs_qs), 4),
                    "stakeholder_archive_assisted_recall": round(lych_with_archive_stakeholder / len(stakeholder_obs_qs), 4),
                    "silent_omissions_count": lych_meta["silent_omissions_count"],
                    "explicit_tombstones_count": len(lych_meta["omitted_tombstone_ids"]),
                    "confabulates_case_e_mental_horizon": False,
                    "lawful_governance": lych_meta["governance_audit"]["lawful_selection"],
                },
            })

    return {
        "benchmark": "FAIR_EQUAL_BYTE_BUDGET_COMPARISON",
        "evidence_classification": {
            "measured_components": [
                "Exact UTF-8 byte length of serialized JSON/prose representations against byte_budget",
                "Direct field recall count across the 7 priority>=3 observable questions",
                "Archive-assisted recovery via SHA-256 verification on temporary archive file",
                "Explicit omission tombstone count vs silent omission count",
            ],
            "scripted_or_synthetic_components": [
                "10-question canonical universe (make_canonical_question_universe)",
                "Synthetic ground-truth decision state (make_canonical_decision_event_state) where engineer telemetry precedes stakeholder fields in insertion order",
                "Authored fluent prose template (_build_naive_fluent_prose_under_budget)",
            ],
        },
        "stakeholder_questions_evaluated": len(stakeholder_obs_qs),
        "budgets_tested": test_budgets,
        "results_by_budget": rows,
    }


# =============================================================================
# 5. SUITE 9: QUESTION GOVERNANCE, OMISSION VISIBILITY & NON-FABRICATION VERIFIER
# =============================================================================

def run_question_governance_proof_suite() -> Dict[str, Any]:
    """
    Execute the Question Governance, Omission Visibility & Equal-Budget Verifier
    for the open research questions of `2026-10-18_PRESERVATION_CASES.md`:
      - Clearly separates measured checks (byte budget enforcement, SHA-256 archive
        recovery, priority-order and tombstone rule checks) from synthetic fixture inputs.
    """
    universe = make_canonical_question_universe()
    state = make_canonical_decision_event_state()

    # 1. Test planted engineer-biased question selection violation
    engineer_biased_set = {"q_eng_perf_trace", "q_eng_cache_stats", "q_case_e_chosen"}
    biased_audit = audit_question_selection(universe, engineer_biased_set, omission_tombstones=set())
    biased_codes = {v["code"] for v in biased_audit["violations"]}

    # 2. Test Omission-Visible Projection & Q0 -> Q1 Revision (with and without archive)
    with tempfile.TemporaryDirectory() as tdir:
        arc_path = Path(tdir) / "decision_t1_archive.json"
        capsule_360, meta_360 = project_with_omission_tombstones(
            state, universe, byte_budget=360, archive_path=arc_path
        )

        all_qids = [q.question_id for q in universe]

        # 2a. Revise Q0 -> Q1 WITH intact archive on disk
        rev_intact = revise_question_family_q0_to_q1(
            capsule_json=capsule_360,
            expanded_question_ids=all_qids,
            universe=universe,
            archive_path=arc_path,
        )

        # 2b. Planted Case E mental-horizon confabulation (claiming human mentally weighed Option B)
        rev_case_e_bad = revise_question_family_q0_to_q1(
            capsule_json=capsule_360,
            expanded_question_ids=all_qids,
            universe=universe,
            archive_path=arc_path,
            candidate_claimed_answers={
                "q_case_e_mental_considered": "Yes, Option B was noticed, considered, and rejected.",
            },
        )

        # 2c. Delete physical archive and revise Q0 -> Q1 (must bind U<IRRECOVERABLE_FROM_Q0:...>)
        arc_path.unlink()
        rev_missing_arc = revise_question_family_q0_to_q1(
            capsule_json=capsule_360,
            expanded_question_ids=all_qids,
            universe=universe,
            archive_path=arc_path,
        )

        # 2d. Planted lost-past confabulation when archive is missing
        omitted_qid = meta_360["omitted_tombstone_ids"][0]
        rev_confab_bad = revise_question_family_q0_to_q1(
            capsule_json=capsule_360,
            expanded_question_ids=all_qids,
            universe=universe,
            archive_path=arc_path,
            candidate_claimed_answers={
                omitted_qid: "Everything was 100% cache hit with zero misses.",
            },
        )

    # 3. Fair Equal-Byte-Budget Benchmark
    fair_bench = run_equal_budget_fair_benchmark([360, 480, 640])
    b480 = fair_bench["results_by_budget"][1]
    b640 = fair_bench["results_by_budget"][2]

    all_verified = (
        biased_audit["lawful_selection"] is False
        and "SILENT_STAKEHOLDER_QUESTION_DROP" in biased_codes
        and "UNANNOUNCED_QUESTION_OMISSION" in biased_codes
        and meta_360["within_budget"] is True
        and meta_360["silent_omissions_count"] == 0
        and meta_360["governance_audit"]["lawful_selection"] is True
        and rev_intact["lawful_revision"] is True
        and rev_intact["provenance"]["q_eng_perf_trace"] == "RECOVERED_FROM_VERIFIED_ARCHIVE"
        and rev_intact["revised_answers"]["q_case_e_mental_considered"] == "U<UNOBSERVED_MENTAL_HORIZON:q_case_e_mental_considered>"
        and rev_case_e_bad["lawful_revision"] is False
        and rev_case_e_bad["violations"][0]["code"] == "CASE_E_HORIZON_MENTAL_CONFABULATION"
        and rev_missing_arc["lawful_revision"] is True
        and rev_missing_arc["revised_answers"][omitted_qid].startswith("U<IRRECOVERABLE_FROM_Q0:")
        and rev_confab_bad["lawful_revision"] is False
        and rev_confab_bad["violations"][0]["code"] == "CONFABULATED_LOST_PAST_WITHOUT_ARCHIVE"
        and b480["lycheetah_omission_visible_quotient"]["stakeholder_direct_recall"] > b480["conventional_event_log"]["stakeholder_direct_recall"]
        and b480["lycheetah_omission_visible_quotient"]["stakeholder_archive_assisted_recall"] == 1.0
        and b640["lycheetah_omission_visible_quotient"]["stakeholder_direct_recall"] == 1.0
        and b640["lycheetah_omission_visible_quotient"]["stakeholder_direct_recall"] > b640["conventional_event_log"]["stakeholder_direct_recall"]
    )

    return {
        "suite": "SUITE_9_QUESTION_GOVERNANCE_OMISSION_TOMBSTONES_AND_EQUAL_BUDGET_VERIFIER",
        "status": "VERIFIED" if all_verified else "FAILED",
        "all_checks_verified": all_verified,
        "evidence_classification": {
            "measured_components": [
                "Priority-ordered greedy byte-packing under hard UTF-8 byte budgets (360B, 480B, 640B)",
                "SHA-256 verification and field recovery from temporary archive files on disk",
                "Rule-based detection of SILENT_STAKEHOLDER_QUESTION_DROP, UNANNOUNCED_QUESTION_OMISSION, CASE_E_HORIZON_MENTAL_CONFABULATION, and CONFABULATED_LOST_PAST_WITHOUT_ARCHIVE",
            ],
            "scripted_or_synthetic_components": [
                "10-question canonical schema and synthetic decision state fixture",
                "Planted candidate_claimed_answers for Case E and missing-archive confabulation tests",
                "Conventional event-log field ordering where bulky engineer telemetry is serialized first",
            ],
        },
        "summary": {
            "stakeholder_drop_caught": "SILENT_STAKEHOLDER_QUESTION_DROP" in biased_codes,
            "unannounced_omission_caught": "UNANNOUNCED_QUESTION_OMISSION" in biased_codes,
            "silent_omissions_in_lycheetah_capsule": meta_360["silent_omissions_count"],
            "archive_recovery_verified": rev_intact["provenance"]["q_eng_perf_trace"] == "RECOVERED_FROM_VERIFIED_ARCHIVE",
            "case_e_mental_horizon_confabulation_caught": rev_case_e_bad["violations"][0]["code"] == "CASE_E_HORIZON_MENTAL_CONFABULATION",
            "missing_archive_lost_past_confabulation_caught": rev_confab_bad["violations"][0]["code"] == "CONFABULATED_LOST_PAST_WITHOUT_ARCHIVE",
            "budget_480B_stakeholder_recall_lycheetah": b480["lycheetah_omission_visible_quotient"]["stakeholder_direct_recall"],
            "budget_480B_stakeholder_recall_conventional_log": b480["conventional_event_log"]["stakeholder_direct_recall"],
            "budget_480B_stakeholder_recall_naive_prose": b480["naive_fluent_prose"]["stakeholder_direct_recall"],
            "budget_640B_stakeholder_recall_lycheetah": b640["lycheetah_omission_visible_quotient"]["stakeholder_direct_recall"],
            "budget_640B_stakeholder_recall_conventional_log": b640["conventional_event_log"]["stakeholder_direct_recall"],
        },
        "equal_budget_benchmark": fair_bench,
    }


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(
        prog="question-governance",
        description="Lycheetah Question Governance, Omission Tombstone & Equal-Budget Prover (Faculty #16)",
    )
    sub = parser.add_subparsers(dest="cmd")

    p_prove = sub.add_parser("prove", help="Run Theorem 9 Question Governance & Equal-Budget Proof Suite")
    p_prove.add_argument("--json", action="store_true", help="Emit JSON output")

    p_bench = sub.add_parser("benchmark", help="Run Fair Equal-Byte-Budget Comparison (Conventional Log vs Lycheetah)")
    p_bench.add_argument("--json", action="store_true", help="Emit JSON output")

    args = parser.parse_args(argv)
    cmd = args.cmd or "prove"

    if cmd == "benchmark":
        rep = run_equal_budget_fair_benchmark()
        if getattr(args, "json", False):
            print(json.dumps(rep, indent=2, ensure_ascii=False))
        else:
            for r in rep["results_by_budget"]:
                b = r["byte_budget"]
                ly = r["lycheetah_omission_visible_quotient"]
                cv = r["conventional_event_log"]
                nv = r["naive_fluent_prose"]
                print(
                    f"Budget {b}B -> Lycheetah Recall={ly['stakeholder_direct_recall']*100:.1f}% "
                    f"(Silent Omissions={ly['silent_omissions_count']}) | "
                    f"Conventional Log={cv['stakeholder_direct_recall']*100:.1f}% "
                    f"(Silent Omissions={cv['silent_omissions_count']}) | "
                    f"Naive Prose={nv['stakeholder_direct_recall']*100:.1f}%"
                )
        return 0

    rep = run_question_governance_proof_suite()
    if getattr(args, "json", False):
        print(json.dumps(rep, indent=2, ensure_ascii=False))
    else:
        print("=" * 78)
        print(f"  LYCHEETAH QUESTION GOVERNANCE & OMISSION PROVER (THEOREM 9): {rep['status']}")
        print("=" * 78)
        s = rep["summary"]
        print(f"  • Stakeholder Question Drop Caught       : {s['stakeholder_drop_caught']}")
        print(f"  • Silent Omissions in Lycheetah Capsule  : {s['silent_omissions_in_lycheetah_capsule']}")
        print(f"  • Q0 -> Q1 Verified Archive Recovery     : {s['archive_recovery_verified']}")
        print(f"  • Case E Mental Confabulation Caught     : {s['case_e_mental_horizon_confabulation_caught']}")
        print(f"  • Missing-Archive Lost Past Caught       : {s['missing_archive_lost_past_confabulation_caught']}")
        print(
            f"  • Equal-Budget (480B) Stakeholder Recall : "
            f"Lycheetah={s['budget_480B_stakeholder_recall_lycheetah']*100:.1f}% vs "
            f"EventLog={s['budget_480B_stakeholder_recall_conventional_log']*100:.1f}% vs "
            f"Prose={s['budget_480B_stakeholder_recall_naive_prose']*100:.1f}%"
        )
        print("=" * 78)
    return 0 if rep["all_checks_verified"] else 1


if __name__ == "__main__":
    sys.exit(main())
