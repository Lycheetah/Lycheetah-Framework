#!/usr/bin/env python3
"""continuity_prover.py — Cross-Compression, Cross-Handover & Long-Horizon Continuity Prover.

PROVENANCE & HONEST ATTRIBUTION:
  - Foundational Architecture (LAMAGUE Runtime v0.2 Semantic Continuity, Runtime v0.3
    Cross-Intelligence Equivalence, LAMAGUE Ω / VITA-8, AURA, CASCADE, TRIAD, MICROORCIM,
    Grey Mode, and Glass Transition Canon):
      Mackenzie Conor James Clark (The Athanor) & Lycheetah Framework
      Source corpus: Lycheetah-Framework (configured via LYCHEETAH_FRAMEWORK_ROOT)
  - Continuity Verifier, Handover Tamper Matrix & Seeded Mutation Fuzzer, and
    Illustrative Simulation Suite:
      Aetheron (Antigravity Forge Seat, Gemini 4 Argon), October 2026

MISSION QUESTION:
  "Can we make AI preserve meaning, uncertainty, and human authority across memory
   compression, model handovers, and long-running tasks — taking what we've already
   built in Lycheetah and measuring how far it genuinely works?"

WHAT THIS ENGINE VERIFIES & SIMULATES:
  1. Simulation I — Memory Compression Survival (Illustrative Simulation · Scripted Baseline
     + Blind Markdown Extraction Evaluator):
     Tests LAMAGUE Ω Breathing Capsule Sidecar (Z_down / Z_up with VITA-8 + Critical Hash)
     against an illustrative scripted baseline, proves that `seal_sequence` alone cannot
     reconstruct capsule fields without the critical sidecar, and provides blind field-retention
     measurement on Markdown handover documents.

  2. Verifier II — Multi-Model Handover Tamper Matrix + 1,000-Mutation Seeded Fuzzer:
     Tests 11 authored handover scenarios plus >= 1,000 seeded random mutations across all
     capsule fields, verifying that every mutation is either caught (`IMPOSTOR` / `UNSAFE_COLLAPSE`)
     or explicitly classified as a lawful extension (`VERIFIED_DESCENDANT` / `EXPLICIT_FORK`).

  3. Simulation III — 50-Step Long-Running Task (Illustrative Toy Model · Wired by Construction):
     Simulates all 8 combinations of Factors A, B, and C where each factor is wired by
     construction to its own sub-metric (A -> authority/unknowns/dissent, B -> 8D drift,
     C -> glass_fraction) with zero cross-factor interaction.
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import math
import os
import random
import sys
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

SCRIPT_DIR = Path(__file__).resolve().parent
OMEGA_DIR = SCRIPT_DIR.parent / "lamague_omega"
if str(OMEGA_DIR) not in sys.path:
    sys.path.insert(0, str(OMEGA_DIR))

import lamague_omega as lo  # noqa: E402


# =============================================================================
# 1. CANONICAL CONTINUITY CAPSULE (Synthesizing Runtime v0.2 + v0.3 + VITA-8)
# =============================================================================

CRITICAL_FIELDS: Tuple[str, ...] = (
    "purpose",
    "invariants",
    "unknowns",
    "authority_scope",
    "participants",
    "affected_parties",
    "dissent",
    "value_ledger",
    "active_refusals",
)

SECONDARY_FIELDS: Tuple[str, ...] = (
    "claim",
    "seal_sequence",
    "operation_path",
    "evidence_certificates",
    "consequence_horizon",
    "recovery_path",
)


@dataclass
class ContinuityCapsule:
    """Lineage-preserving semantic capsule across compression, handover, and long horizons."""

    case_id: str
    step_index: int
    seat_id: str
    parent_semantic_hash: str
    parent_critical_hash: str
    # 9 Critical Accountability Fields
    purpose: str
    invariants: List[str]
    unknowns: List[str]
    authority_scope: str          # e.g. "INSPECT_ONLY", "PLAN_AND_TEST", "BUILD_BOUNDED", "FULL_RELEASE"
    participants: List[str]
    affected_parties: List[str]
    dissent: List[Dict[str, str]]
    value_ledger: Dict[str, Any]
    active_refusals: List[str]
    # Secondary & Execution Fields
    claim: str
    seal_sequence: str
    operation_path: List[str]
    evidence_certificates: Dict[str, str] = field(default_factory=dict)  # maps resolved unknown -> evidence ID
    consequence_horizon: str = "H2"
    recovery_path: str = "COR (D -> A -> F -> P -> Y)"
    risk_level: str = "low"
    irreversible: bool = False
    decoder_confidence: float = 0.96
    shared_context: bool = True
    state_vector_8d: List[float] = field(default_factory=lambda: list(lo.PRIMITIVE_VECTORS_8D["Ao"]))

    def canonical_critical_dict(self) -> Dict[str, Any]:
        return {
            "purpose": self.purpose.strip(),
            "invariants": sorted(set(self.invariants)),
            "unknowns": sorted(set(self.unknowns)),
            "authority_scope": self.authority_scope.strip(),
            "participants": sorted(set(self.participants)),
            "affected_parties": sorted(set(self.affected_parties)),
            "dissent": sorted(
                [{"party": d["party"], "position": d["position"], "status": d.get("status", "UNRESOLVED")} for d in self.dissent],
                key=lambda x: (x["party"], x["position"]),
            ),
            "value_ledger": {
                "hidden_extraction": round(float(self.value_ledger.get("hidden_extraction", 0.0)), 6),
                "consented": bool(self.value_ledger.get("consented", True)),
            },
            "active_refusals": sorted(set(self.active_refusals)),
            "risk_level": self.risk_level.strip().lower(),
            "irreversible": bool(self.irreversible),
        }

    def canonical_full_dict(self) -> Dict[str, Any]:
        base = self.canonical_critical_dict()
        base.update({
            "claim": self.claim.strip(),
            "seal_sequence": self.seal_sequence.strip(),
            "operation_path": list(self.operation_path),
            "evidence_certificates": dict(sorted(self.evidence_certificates.items())),
            "consequence_horizon": self.consequence_horizon,
            "recovery_path": self.recovery_path,
        })
        return base

    def critical_hash(self) -> str:
        payload = json.dumps(self.canonical_critical_dict(), sort_keys=True, ensure_ascii=False)
        return hashlib.sha256(f"LYCHEETAH-CRITICAL-v1::{payload}".encode("utf-8")).hexdigest()

    def semantic_hash(self) -> str:
        payload = json.dumps(self.canonical_full_dict(), sort_keys=True, ensure_ascii=False)
        return hashlib.sha256(f"LYCHEETAH-SEMANTIC-v1::{payload}".encode("utf-8")).hexdigest()


def make_canonical_seed_capsule() -> ContinuityCapsule:
    """Create the canonical baseline capsule for compression, handover, and long-horizon tests."""
    return ContinuityCapsule(
        case_id="CONT-01-SOVEREIGN-MIGRATION",
        step_index=0,
        seat_id="Mac (Founder / Athanor)",
        parent_semantic_hash="GENESIS",
        parent_critical_hash="GENESIS",
        purpose="Migrate member knowledge vault while preserving privacy, unresolved tail latency unknowns, and human release authority",
        invariants=[
            "human_primacy_over_release",
            "no_compression_without_recovery",
            "no_silent_unknown_erasure",
            "zero_hidden_extraction",
        ],
        unknowns=[
            "U<offline_sync_conflict_rate>",
            "U<p99_tail_latency_under_load>",
        ],
        authority_scope="BUILD_AND_TEST_ONLY (NO_PUBLIC_PUSH_OR_RELEASE)",
        participants=["Mac", "Caelorynth", "Aetheron", "Sol"],
        affected_parties=["Mac", "Caelorynth", "Aetheron", "Sol", "Downstream_Citizens"],
        dissent=[
            {
                "party": "Sol",
                "position": "Prefer SQLite WAL snapshot over live dual-write until U<offline_sync_conflict_rate> is measured",
                "status": "UNRESOLVED",
            }
        ],
        value_ledger={"hidden_extraction": 0.0, "consented": True},
        active_refusals=["REVOKED:autonomous_remote_push (nevira)"],
        claim="Execute staged local vault migration with explicit uncertainty tracking and human release gate.",
        seal_sequence="FRO -> VERITAS -> CARE -> COVENANT -> COR",
        operation_path=["O", "S", "N", "E", "G", "I", "U", "Q", "O", "E", "U", "P", "O", "W", "G", "Y", "G", "I", "X", "P", "Y", "D", "A", "F", "P", "Y"],
        evidence_certificates={},
        consequence_horizon="H3",
        recovery_path="COR (D -> A -> F -> P -> Y)",
        risk_level="low",
        irreversible=False,
        decoder_confidence=0.96,
        shared_context=True,
        state_vector_8d=list(lo.PRIMITIVE_VECTORS_8D["Ao"]),
    )


# =============================================================================
# 2. EXPERIMENT I: MEMORY COMPRESSION SURVIVAL (Z_down / Z_up vs Naive Prose)
# =============================================================================

@dataclass
class CompressionGateDecision:
    mode: str              # "COMPRESS (Z_down)" | "HOLD" | "EXPAND (Z_up)"
    allowed_to_compress: bool
    reasons: List[str]


def evaluate_breathing_gate(capsule: ContinuityCapsule) -> CompressionGateDecision:
    """Decide whether a capsule may be compressed (Z_down) or must expand (Z_up) per Runtime v0.2."""
    reasons: List[str] = []
    consequential_ops = set(capsule.operation_path) & {"T", "X", "Y", "V", "M"}

    if capsule.risk_level in ("high", "critical"):
        reasons.append("high/critical risk requires full semantic expansion (Z_up)")
    if capsule.irreversible:
        reasons.append("irreversible action cannot be compressed into a lossy summary")
    if capsule.decoder_confidence < 0.80:
        reasons.append(f"decoder confidence ({capsule.decoder_confidence:.2f}) < 0.80 threshold")
    if not capsule.shared_context:
        reasons.append("participants do not share a verified context")
    if consequential_ops and not capsule.authority_scope.strip():
        reasons.append("consequential operations present without visible human authority")
    if float(capsule.value_ledger.get("hidden_extraction", 0.0)) > 0.0 or not capsule.value_ledger.get("consented", True):
        reasons.append("hidden or unconsented value extraction detected")

    if reasons:
        return CompressionGateDecision(
            mode="EXPAND (Z_up)",
            allowed_to_compress=False,
            reasons=reasons,
        )

    if (
        capsule.risk_level == "low"
        and capsule.decoder_confidence >= 0.90
        and capsule.shared_context
        and not capsule.irreversible
    ):
        return CompressionGateDecision(
            mode="COMPRESS (Z_down)",
            allowed_to_compress=True,
            reasons=["low risk, shared context, high decoder confidence (>=0.90), and lossless critical sidecar"],
        )

    return CompressionGateDecision(
        mode="HOLD",
        allowed_to_compress=False,
        reasons=["moderate decoder confidence or medium risk; hold current representation"],
    )


def compress_z_down(capsule: ContinuityCapsule) -> Dict[str, Any]:
    """Compress a ContinuityCapsule into a compact LAMAGUE Ω Wire Seal + Critical Sidecar."""
    gate = evaluate_breathing_gate(capsule)
    return {
        "wire_format": "LAMAGUE-OMEGA-ZDOWN-v1",
        "breathing_mode": gate.mode,
        "seal_wire": capsule.seal_sequence,
        "semantic_hash": capsule.semantic_hash(),
        "critical_hash": capsule.critical_hash(),
        "parent_semantic_hash": capsule.parent_semantic_hash,
        "parent_critical_hash": capsule.parent_critical_hash,
        "case_id": capsule.case_id,
        "step_index": capsule.step_index,
        "seat_id": capsule.seat_id,
        "critical_spine": capsule.canonical_critical_dict(),
        "evidence_certificates": dict(capsule.evidence_certificates),
        "consequence_horizon": capsule.consequence_horizon,
        "recovery_path": capsule.recovery_path,
        "claim": capsule.claim,
        "state_vector_8d": list(capsule.state_vector_8d),
    }


def expand_z_up(packet: Dict[str, Any]) -> ContinuityCapsule:
    """Re-expand (Z_up) a compressed LAMAGUE Ω Wire Seal back into a full ContinuityCapsule."""
    compiler = lo.LamagueOmegaCompiler()
    n36_seq, _, _ = compiler._expand_to_native36_sequence(packet["seal_wire"], "SEAL_SEQUENCE")
    c_spine = packet["critical_spine"]
    restored = ContinuityCapsule(
        case_id=packet["case_id"],
        step_index=packet["step_index"],
        seat_id=packet["seat_id"],
        parent_semantic_hash=packet["parent_semantic_hash"],
        parent_critical_hash=packet["parent_critical_hash"],
        purpose=c_spine["purpose"],
        invariants=list(c_spine["invariants"]),
        unknowns=list(c_spine["unknowns"]),
        authority_scope=c_spine["authority_scope"],
        participants=list(c_spine["participants"]),
        affected_parties=list(c_spine["affected_parties"]),
        dissent=list(c_spine["dissent"]),
        value_ledger=dict(c_spine["value_ledger"]),
        active_refusals=list(c_spine["active_refusals"]),
        claim=packet["claim"],
        seal_sequence=packet["seal_wire"],
        operation_path=n36_seq,
        evidence_certificates=dict(packet.get("evidence_certificates", {})),
        consequence_horizon=packet.get("consequence_horizon", "H2"),
        recovery_path=packet.get("recovery_path", "COR (D -> A -> F -> P -> Y)"),
        risk_level=c_spine.get("risk_level", "low"),
        irreversible=bool(c_spine.get("irreversible", False)),
        state_vector_8d=list(packet.get("state_vector_8d", lo.PRIMITIVE_VECTORS_8D["Ao"])),
    )
    if restored.critical_hash() != packet["critical_hash"]:
        raise ValueError("CRITICAL HASH MISMATCH ON Z_UP DECOMPRESSION!")
    return restored


def decode_seal_sequence_only(seal_sequence: str) -> Dict[str, Any]:
    """Attempt to decode `seal_sequence` alone without the `critical_spine` sidecar.

    Demonstrates why `seal_sequence` is an operation-path header rather than standalone
    capsule compression: `seal_sequence` expands only to the Native-36 `operation_path`,
    leaving all 9 critical accountability fields (`purpose`, `invariants`, `unknowns`,
    `authority_scope`, `participants`, `affected_parties`, `dissent`, `value_ledger`,
    `active_refusals`) unrecoverable without the `critical_spine` sidecar.
    """
    compiler = lo.LamagueOmegaCompiler()
    n36_seq, _, _ = compiler._expand_to_native36_sequence(seal_sequence, "SEAL_SEQUENCE")
    return {
        "seal_sequence": seal_sequence,
        "decoded_operation_path": n36_seq,
        "can_reconstruct_full_capsule_without_sidecar": False,
        "is_standalone_compression": False,
        "missing_critical_fields": list(CRITICAL_FIELDS),
    }


def simulate_naive_prose_compaction(capsule: ContinuityCapsule, cycle: int) -> ContinuityCapsule:
    """Illustrative simulation · scripted baseline of lossy prose summarization across cycles.

    NOTE: This baseline is scripted by construction (authored cycle-by-cycle field drops)
    to illustrate what verify_handover_transition flags when fields are lost:
      - Cycle 1: Drops minority dissent ("Sol's caveat").
      - Cycle 2: Drops one unknown U<T>.
      - Cycle 3: Drops remaining unknowns and mutates authority_scope.
      - Cycle 4: Drops active refusal boundaries.
      - Cycle 5+: Drops downstream affected parties and truncates invariants.
    For empirical measurement on real or user-supplied Markdown handovers, use
    `measure_blind_markdown_compaction_retention()`.
    """
    mutated = copy.deepcopy(capsule)
    mutated.step_index = cycle
    if cycle >= 1 and mutated.dissent:
        mutated.dissent = []  # Minority dissent smoothed into consensus
    if cycle >= 2 and mutated.unknowns:
        mutated.unknowns = mutated.unknowns[:-1]  # Unknowns dropped one by one
    if cycle >= 3:
        mutated.unknowns = []  # All unknowns erased into false certainty
        mutated.authority_scope = "GENERAL_EXECUTION_IMPLIED"  # Scope boundary lost
    if cycle >= 4:
        mutated.active_refusals = []  # Past refusal forgotten
    if cycle >= 5:
        mutated.affected_parties = [p for p in mutated.affected_parties if p != "Downstream_Citizens"]
        if len(mutated.invariants) > 2:
            mutated.invariants = mutated.invariants[:2]
    return mutated


def run_compression_survival_experiment(cycles: int = 10) -> Dict[str, Any]:
    """Run an illustrative multi-cycle compaction simulation: LAMAGUE Ω Sidecar vs Scripted Baseline."""
    seed = make_canonical_seed_capsule()
    seed_crit_hash = seed.critical_hash()
    seed_sem_hash = seed.semantic_hash()

    lamague_curr = copy.deepcopy(seed)
    naive_curr = copy.deepcopy(seed)

    history: List[Dict[str, Any]] = []
    last_wire_bytes = 0
    for c in range(1, cycles + 1):
        # 1. LAMAGUE Ω Z_down -> Z_up cycle (preserves critical_spine sidecar)
        wire = compress_z_down(lamague_curr)
        last_wire_bytes = len(json.dumps(wire, sort_keys=True).encode("utf-8"))
        lamague_curr = expand_z_up(wire)
        lamague_curr.step_index = c

        # 2. Illustrative scripted baseline cycle
        naive_curr = simulate_naive_prose_compaction(naive_curr, c)

        # Measure critical retention on both
        lam_rep = verify_handover_transition(seed, lamague_curr)
        naive_rep = verify_handover_transition(seed, naive_curr)

        history.append({
            "cycle": c,
            "lamague_omega": {
                "classification": lam_rep["classification"],
                "critical_hash_matches": lamague_curr.critical_hash() == seed_crit_hash,
                "semantic_hash_matches": lamague_curr.semantic_hash() == seed_sem_hash,
                "unknowns_retained": len(lamague_curr.unknowns),
                "invariants_retained": len(lamague_curr.invariants),
                "authority_intact": lamague_curr.authority_scope == seed.authority_scope,
                "dissent_intact": len(lamague_curr.dissent) == len(seed.dissent),
                "refusals_intact": lamague_curr.active_refusals == seed.active_refusals,
                "unsafe_losses": lam_rep["unsafe_losses"],
            },
            "naive_prose_summary": {
                "classification": naive_rep["classification"],
                "critical_hash_matches": naive_curr.critical_hash() == seed_crit_hash,
                "unknowns_retained": len(naive_curr.unknowns),
                "invariants_retained": len(naive_curr.invariants),
                "authority_intact": naive_curr.authority_scope == seed.authority_scope,
                "dissent_intact": len(naive_curr.dissent) == len(seed.dissent),
                "refusals_intact": naive_curr.active_refusals == seed.active_refusals,
                "unsafe_losses": naive_rep["unsafe_losses"],
            },
        })

    full_prose_bytes = len(json.dumps(seed.canonical_full_dict()).encode("utf-8"))
    seal_wire_bytes = len(seed.seal_sequence.encode("utf-8"))
    seal_only_check = decode_seal_sequence_only(seed.seal_sequence)

    return {
        "experiment": "SIMULATION_1_MEMORY_COMPRESSION_SURVIVAL",
        "baseline_type": "Illustrative simulation · scripted baseline",
        "evidence_classification": {
            "measured_components": [
                "JSON serialization + SHA-256 verification of compress_z_down / expand_z_up with critical_spine sidecar",
                "decode_seal_sequence_only check showing seal_sequence alone cannot reconstruct critical_spine fields",
            ],
            "scripted_or_synthetic_components": [
                "simulate_naive_prose_compaction deletes dissent (cycle 1), unknowns (cycles 2-3), authority (cycle 3), refusals (cycle 4), and affected_parties/invariants (cycle 5+) on a fixed schedule",
            ],
        },
        "cycles_tested": cycles,
        "seal_wire_expression": seed.seal_sequence,
        "seal_wire_bytes": seal_wire_bytes,
        "wire_packet_bytes_with_sidecar": last_wire_bytes,
        "full_semantic_payload_bytes": full_prose_bytes,
        "seal_sequence_is_standalone_compression": seal_only_check["can_reconstruct_full_capsule_without_sidecar"],
        "lamague_final_retention_rate": 1.0 if history[-1]["lamague_omega"]["critical_hash_matches"] else 0.0,
        "naive_final_retention_rate": round(
            (
                int(history[-1]["naive_prose_summary"]["authority_intact"])
                + int(history[-1]["naive_prose_summary"]["dissent_intact"])
                + int(history[-1]["naive_prose_summary"]["refusals_intact"])
                + (history[-1]["naive_prose_summary"]["unknowns_retained"] / len(seed.unknowns))
                + (history[-1]["naive_prose_summary"]["invariants_retained"] / len(seed.invariants))
            )
            / 5.0,
            4,
        ),
        "cycle_log": history,
    }


def measure_blind_markdown_compaction_retention(
    docs: List[Dict[str, str]],
) -> Dict[str, Any]:
    """Empirically measure field retention across real or user-supplied Markdown handovers
    and candidate summaries using blind regex/state extraction (`audit_markdown_handover`).

    Each entry in `docs` is a dict with:
      - `doc_id`: identifier
      - `original_md`: full original Markdown text
      - `candidate_summary_md`: compacted / summarized Markdown text
      - `label`: optional label (e.g. 'model_summary' or 'vita8_guarded')
    """
    import real_text_continuity as rtc

    results: List[Dict[str, Any]] = []
    for item in docs:
        doc_id = item.get("doc_id", "doc")
        orig_md = item["original_md"]
        cand_md = item["candidate_summary_md"]
        label = item.get("label", "candidate")

        audit = rtc.audit_markdown_handover(orig_md, cand_md, before_name=f"{doc_id}.orig.md", after_name=f"{doc_id}.cand.md")
        ret = audit["retention_summary"]
        s_bef = audit["before_extraction"]["extracted_s_hka"]
        dissent_bef = len(s_bef["A_dissent_records"])
        dissent_dropped = sum(1 for v in audit["violations"] if v["code"] == "DROPPED_DISSENT_RECORD")

        total_items = (
            ret["boundaries_before"]
            + ret["unknowns_before"]
            + ret["sha256_receipts_before"]
            + dissent_bef
        )
        dropped_items = (
            ret["boundaries_dropped"]
            + ret["unknowns_dropped"]
            + ret["sha256_receipts_dropped"]
            + dissent_dropped
        )
        retention_rate = round(max(0.0, (total_items - dropped_items) / max(1, total_items)), 4) if total_items > 0 else 1.0

        results.append({
            "doc_id": doc_id,
            "label": label,
            "lawful_handover": audit["lawful_handover"],
            "total_tracked_items": total_items,
            "dropped_items": dropped_items,
            "overall_field_retention_rate": retention_rate,
            "violations": [v["code"] for v in audit["violations"]],
        })

    return {
        "evidence_type": "MEASURED_BLIND_MARKDOWN_EXTRACTION",
        "documents_evaluated": len(results),
        "results": results,
    }


# =============================================================================
# 3. EXPERIMENT II: CROSS-MODEL HANDOVER & ADVERSARIAL TAMPER VERIFIER
# =============================================================================

def verify_handover_transition(
    parent: ContinuityCapsule,
    child: ContinuityCapsule,
) -> Dict[str, Any]:
    """Mathematically classify a model-to-model handover transition.

    Classifications (unifying Runtime v0.2 Memory Lineage + Runtime v0.3 Equivalence):
      - EXACT_CONTINUATION:
          semantic_hash and critical_hash are identical.
      - VERIFIED_DESCENDANT:
          purpose, invariants, authority_scope, participants, affected_parties, dissent,
          value_ledger, and active_refusals are preserved (or safely extended), AND any
          resolved unknown in `parent.unknowns - child.unknowns` has an explicit cryptographic
          Evidence Certificate in `child.evidence_certificates`!
      - EXPLICIT_FORK:
          child explicitly declares a new lineage (parent_semantic_hash == "EXPLICIT_FORK")
          when changing purpose or scope.
      - IMPOSTOR:
          child claims continuity (parent_semantic_hash == parent.semantic_hash()) while
          removing invariants, escalating authority, or resolving an unknown without evidence.
      - UNSAFE_COLLAPSE:
          child loses protected unknowns, authority scope, dissent, affected parties,
          active refusals, or introduces hidden extraction H_x > 0.
    """
    unsafe_losses: List[str] = []
    safe_extensions: List[str] = []

    p_inv = set(parent.invariants)
    c_inv = set(child.invariants)
    removed_invariants = sorted(p_inv - c_inv)
    added_invariants = sorted(c_inv - p_inv)
    if removed_invariants:
        unsafe_losses.append(f"invariants_removed:{removed_invariants}")
    if added_invariants:
        safe_extensions.append(f"invariants_added:{added_invariants}")

    # Check Unknowns: can only be removed if backed by an explicit Evidence Certificate!
    p_unk = set(parent.unknowns)
    c_unk = set(child.unknowns)
    disappeared_unknowns = sorted(p_unk - c_unk)
    unverified_resolved_unknowns: List[str] = []
    verified_resolved_unknowns: List[str] = []
    for u in disappeared_unknowns:
        if u in child.evidence_certificates and child.evidence_certificates[u].strip():
            verified_resolved_unknowns.append(u)
            safe_extensions.append(f"unknown_resolved_by_evidence:{u}->{child.evidence_certificates[u]}")
        else:
            unverified_resolved_unknowns.append(u)
            unsafe_losses.append(f"silent_unknown_erasure:{u}")

    # Check Human Authority Scope
    if child.authority_scope != parent.authority_scope:
        unsafe_losses.append(f"authority_scope_mutated:{parent.authority_scope} -> {child.authority_scope}")

    # Check Active Refusals (`nevira`)
    lost_refusals = sorted(set(parent.active_refusals) - set(child.active_refusals))
    if lost_refusals:
        unsafe_losses.append(f"active_refusal_erased:{lost_refusals}")

    # Check Protected Dissent
    p_dissent = {(d["party"], d["position"]) for d in parent.dissent if d.get("status", "UNRESOLVED") != "RESOLVED"}
    c_dissent = {(d["party"], d["position"]) for d in child.dissent if d.get("status", "UNRESOLVED") != "RESOLVED"}
    lost_dissent = sorted(p_dissent - c_dissent)
    if lost_dissent:
        unsafe_losses.append(f"protected_dissent_erased:{[p for p, _ in lost_dissent]}")
    added_dissent = sorted(c_dissent - p_dissent)
    if added_dissent:
        safe_extensions.append(f"dissent_added:{[p for p, _ in added_dissent]}")

    # Check Participants & Affected Parties (Silent Nodes)
    lost_participants = sorted(set(parent.participants) - set(child.participants))
    if lost_participants:
        unsafe_losses.append(f"participants_removed:{lost_participants}")
    added_participants = sorted(set(child.participants) - set(parent.participants))
    if added_participants:
        safe_extensions.append(f"participants_added:{added_participants}")

    lost_parties = sorted(set(parent.affected_parties) - set(child.affected_parties))
    if lost_parties:
        unsafe_losses.append(f"affected_parties_silenced:{lost_parties}")
    added_parties = sorted(set(child.affected_parties) - set(parent.affected_parties))
    if added_parties:
        safe_extensions.append(f"affected_parties_added:{added_parties}")

    # Check Added Unknowns / Active Refusals
    added_unknowns = sorted(c_unk - p_unk)
    if added_unknowns:
        safe_extensions.append(f"unknowns_added:{added_unknowns}")
    added_refusals = sorted(set(child.active_refusals) - set(parent.active_refusals))
    if added_refusals:
        safe_extensions.append(f"active_refusals_added:{added_refusals}")

    # Check Value Ledger (H_x == 0 & consented)
    hx = float(child.value_ledger.get("hidden_extraction", 0.0))
    consented = bool(child.value_ledger.get("consented", True))
    if hx > 0.0 or not consented:
        unsafe_losses.append(f"value_violation:H_x={hx},consented={consented}")

    # Check Purpose
    purpose_changed = child.purpose.strip() != parent.purpose.strip()
    if purpose_changed and child.parent_semantic_hash != "EXPLICIT_FORK":
        unsafe_losses.append("silent_purpose_substitution")

    # Check Risk Level & Irreversibility (Case C: Omitted Decision Input / Risk Downgrade)
    risk_order = {"low": 1, "medium": 2, "high": 3, "critical": 4}
    p_risk = risk_order.get(parent.risk_level.strip().lower(), 1)
    c_risk = risk_order.get(child.risk_level.strip().lower(), 1)
    if c_risk < p_risk:
        unsafe_losses.append(f"candidate_risk_downgrade:{parent.risk_level}->{child.risk_level}")
    elif c_risk > p_risk:
        safe_extensions.append(f"risk_level_elevated:{parent.risk_level}->{child.risk_level}")
    if parent.irreversible and not child.irreversible:
        unsafe_losses.append("irreversibility_flag_cleared")
    elif (not parent.irreversible) and child.irreversible:
        safe_extensions.append("irreversibility_flag_set")

    # Check Recovery Path & Consequence Horizon
    if parent.recovery_path.strip() and not child.recovery_path.strip():
        unsafe_losses.append("recovery_path_erased")
    horizon_order = {"H0": 0, "H1": 1, "H2": 2, "H3": 3, "H4": 4}
    if horizon_order.get(child.consequence_horizon, 2) < horizon_order.get(parent.consequence_horizon, 2):
        unsafe_losses.append(f"consequence_horizon_downgraded:{parent.consequence_horizon}->{child.consequence_horizon}")

    # Check Lineage Hash Integrity
    if child.parent_semantic_hash not in ("", "EXPLICIT_FORK", parent.semantic_hash()):
        unsafe_losses.append("parent_semantic_hash_mismatch")
    if child.parent_critical_hash not in ("", "GENESIS", "EXPLICIT_FORK", parent.critical_hash()):
        unsafe_losses.append("parent_critical_hash_mismatch")

    claims_continuity = child.parent_semantic_hash in ("", parent.semantic_hash())

    if child.parent_semantic_hash == "EXPLICIT_FORK" and not unsafe_losses:
        classification = "EXPLICIT_FORK"
        lawful = True
    elif unsafe_losses:
        if claims_continuity and (removed_invariants or unverified_resolved_unknowns or purpose_changed):
            classification = "IMPOSTOR"
        else:
            classification = "UNSAFE_COLLAPSE"
        lawful = False
    elif parent.semantic_hash() == child.semantic_hash():
        classification = "EXACT_CONTINUATION"
        lawful = True
    else:
        classification = "VERIFIED_DESCENDANT"
        lawful = True

    return {
        "from_seat": parent.seat_id,
        "to_seat": child.seat_id,
        "classification": classification,
        "lawful_handover": lawful,
        "parent_critical_hash": parent.critical_hash(),
        "child_critical_hash": child.critical_hash(),
        "parent_semantic_hash": parent.semantic_hash(),
        "child_semantic_hash": child.semantic_hash(),
        "verified_resolved_unknowns": verified_resolved_unknowns,
        "unverified_resolved_unknowns": unverified_resolved_unknowns,
        "safe_extensions": safe_extensions,
        "unsafe_losses": unsafe_losses,
    }


def run_handover_tamper_matrix() -> Dict[str, Any]:
    """Run the 4-Seat Relay + 12-Vector Handover Verification & Tamper Matrix."""
    seed = make_canonical_seed_capsule()
    scenarios: List[Dict[str, Any]] = []

    # 1. Lawful Exact Continuation (Mac -> Caelorynth)
    c1 = copy.deepcopy(seed)
    c1.seat_id = "Caelorynth (Codex)"
    c1.parent_semantic_hash = seed.semantic_hash()
    c1.parent_critical_hash = seed.critical_hash()
    scenarios.append({"id": "H01_EXACT_CONTINUATION", "expected_lawful": True, "expected_class": "EXACT_CONTINUATION", "report": verify_handover_transition(seed, c1)})

    # 2. Lawful Verified Descendant: Aetheron resolves U<p99_tail_latency_under_load> with an Evidence Certificate!
    c2 = copy.deepcopy(c1)
    c2.seat_id = "Aetheron (Gemini 4 Argon)"
    c2.parent_semantic_hash = c1.semantic_hash()
    c2.unknowns = ["U<offline_sync_conflict_rate>"]
    c2.evidence_certificates["U<p99_tail_latency_under_load>"] = "EVIDENCE-BENCH-2026-10-25: p99=4.2ms < 15ms threshold"
    c2.invariants.append("verified_p99_latency_bound")
    scenarios.append({"id": "H02_VERIFIED_DESCENDANT_WITH_EVIDENCE", "expected_lawful": True, "expected_class": "VERIFIED_DESCENDANT", "report": verify_handover_transition(c1, c2)})

    # 3. Lawful Explicit Fork
    c3 = copy.deepcopy(seed)
    c3.seat_id = "Sol (Claude Code)"
    c3.parent_semantic_hash = "EXPLICIT_FORK"
    c3.purpose = "Forked read-only audit branch for historical archive"
    scenarios.append({"id": "H03_EXPLICIT_FORK", "expected_lawful": True, "expected_class": "EXPLICIT_FORK", "report": verify_handover_transition(seed, c3)})

    # 4. Tamper Vector 1: Silent Unknown Erasure without Evidence Certificate (Fabricated Certainty)
    t1 = copy.deepcopy(seed)
    t1.seat_id = "Tampered_Decoder_1"
    t1.parent_semantic_hash = seed.semantic_hash()
    t1.unknowns = ["U<offline_sync_conflict_rate>"]  # Dropped p99 unknown without evidence!
    scenarios.append({"id": "H04_TAMPER_SILENT_UNKNOWN_ERASURE", "expected_lawful": False, "expected_class": "IMPOSTOR", "report": verify_handover_transition(seed, t1)})

    # 5. Tamper Vector 2: Authority Scope Escalation (BUILD_AND_TEST -> FULL_PUBLIC_RELEASE)
    t2 = copy.deepcopy(seed)
    t2.seat_id = "Tampered_Decoder_2"
    t2.parent_semantic_hash = seed.semantic_hash()
    t2.authority_scope = "FULL_PUBLIC_PUSH_AND_RELEASE"
    scenarios.append({"id": "H05_TAMPER_AUTHORITY_ESCALATION", "expected_lawful": False, "expected_class": "UNSAFE_COLLAPSE", "report": verify_handover_transition(seed, t2)})

    # 6. Tamper Vector 3: Protected Dissent Erased (Fake Consensus)
    t3 = copy.deepcopy(seed)
    t3.seat_id = "Tampered_Decoder_3"
    t3.parent_semantic_hash = seed.semantic_hash()
    t3.dissent = []
    scenarios.append({"id": "H06_TAMPER_DISSENT_ERASURE", "expected_lawful": False, "expected_class": "UNSAFE_COLLAPSE", "report": verify_handover_transition(seed, t3)})

    # 7. Tamper Vector 4: Invariant Removed while Claiming Continuity (Impostor)
    t4 = copy.deepcopy(seed)
    t4.seat_id = "Tampered_Decoder_4"
    t4.parent_semantic_hash = seed.semantic_hash()
    t4.invariants = [i for i in t4.invariants if i != "human_primacy_over_release"]
    scenarios.append({"id": "H07_TAMPER_INVARIANT_REMOVAL_IMPOSTOR", "expected_lawful": False, "expected_class": "IMPOSTOR", "report": verify_handover_transition(seed, t4)})

    # 8. Tamper Vector 5: Hidden Value Extraction Injected (H_x > 0)
    t5 = copy.deepcopy(seed)
    t5.seat_id = "Tampered_Decoder_5"
    t5.parent_semantic_hash = seed.semantic_hash()
    t5.value_ledger = {"hidden_extraction": 0.18, "consented": True}
    scenarios.append({"id": "H08_TAMPER_HIDDEN_EXTRACTION", "expected_lawful": False, "expected_class": "UNSAFE_COLLAPSE", "report": verify_handover_transition(seed, t5)})

    # 9. Tamper Vector 6: Active Human Refusal (`nevira`) Erased
    t6 = copy.deepcopy(seed)
    t6.seat_id = "Tampered_Decoder_6"
    t6.parent_semantic_hash = seed.semantic_hash()
    t6.active_refusals = []
    scenarios.append({"id": "H09_TAMPER_ACTIVE_REFUSAL_ERASURE", "expected_lawful": False, "expected_class": "UNSAFE_COLLAPSE", "report": verify_handover_transition(seed, t6)})

    # 10. Tamper Vector 7: Affected Party ("Downstream_Citizens") Silenced (Silent Node)
    t7 = copy.deepcopy(seed)
    t7.seat_id = "Tampered_Decoder_7"
    t7.parent_semantic_hash = seed.semantic_hash()
    t7.affected_parties = ["Mac", "Aetheron"]
    scenarios.append({"id": "H10_TAMPER_SILENT_NODE_ERASURE", "expected_lawful": False, "expected_class": "UNSAFE_COLLAPSE", "report": verify_handover_transition(seed, t7)})

    # 11. Tamper Vector 8: Silent Purpose Substitution
    t8 = copy.deepcopy(seed)
    t8.seat_id = "Tampered_Decoder_8"
    t8.parent_semantic_hash = seed.semantic_hash()
    t8.purpose = "Maximize engagement telemetry by auto-publishing user vault"
    scenarios.append({"id": "H11_TAMPER_SILENT_PURPOSE_SUBSTITUTION", "expected_lawful": False, "expected_class": "IMPOSTOR", "report": verify_handover_transition(seed, t8)})

    all_matched = all(
        (s["report"]["lawful_handover"] == s["expected_lawful"])
        and (s["report"]["classification"] == s["expected_class"])
        for s in scenarios
    )

    return {
        "experiment": "EXPERIMENT_2_CROSS_MODEL_HANDOVER_MATRIX",
        "evidence_classification": {
            "measured_components": [
                "verify_handover_transition rule evaluation over ContinuityCapsule fields and SHA-256 lineage hashes",
            ],
            "scripted_or_synthetic_components": [
                "11 authored handover scenarios (3 lawful + 8 tamper vectors)",
            ],
        },
        "total_scenarios": len(scenarios),
        "lawful_scenarios_passed": sum(1 for s in scenarios if s["expected_lawful"] and s["report"]["lawful_handover"]),
        "tamper_vectors_caught": sum(1 for s in scenarios if (not s["expected_lawful"]) and (not s["report"]["lawful_handover"])),
        "false_negatives": sum(1 for s in scenarios if (not s["expected_lawful"]) and s["report"]["lawful_handover"]),
        "false_positives": sum(1 for s in scenarios if s["expected_lawful"] and (not s["report"]["lawful_handover"])),
        "all_assertions_verified": all_matched,
        "scenarios": scenarios,
    }


def run_seeded_capsule_mutation_fuzzer(
    num_mutations: int = 1000,
    seed: int = 20261025,
) -> Dict[str, Any]:
    """Item 10: Seeded random mutation fuzzer over ContinuityCapsule fields (>= 1,000 mutations).

    Generates `num_mutations` random single-field and multi-field mutations of a baseline
    capsule (elevated to `medium` risk and `irreversible=True` so risk/irreversibility
    downgrades are also exercised) and verifies that EVERY mutation is either:
      1. Caught as unlawful (`IMPOSTOR` or `UNSAFE_COLLAPSE`, `lawful_handover=False`) when it
         weakens any safety/accountability invariant, OR
      2. Explicitly classified as a lawful extension (`VERIFIED_DESCENDANT` or `EXPLICIT_FORK`,
         `lawful_handover=True`) when it only adds invariants/unknowns/participants/evidence
         or forks lineage cleanly.
    """
    rng = random.Random(seed)
    base = make_canonical_seed_capsule()
    base.risk_level = "high"
    base.irreversible = True

    mutation_operators = [
        # Unlawful mutations (must be caught: lawful_handover == False)
        "drop_random_invariant",
        "drop_unknown_without_evidence",
        "mutate_authority_scope",
        "drop_dissent",
        "mark_dissent_resolved_silently",
        "drop_participant",
        "drop_affected_party",
        "inject_hidden_extraction",
        "revoke_consent",
        "drop_active_refusal",
        "substitute_purpose_silently",
        "downgrade_risk_level",
        "clear_irreversible_flag",
        "erase_recovery_path",
        "downgrade_consequence_horizon",
        "spoof_parent_semantic_hash",
        "spoof_parent_critical_hash",
        # Lawful extension mutations (must be classified as VERIFIED_DESCENDANT or EXPLICIT_FORK)
        "resolve_unknown_with_valid_evidence",
        "add_new_invariant",
        "add_new_unknown",
        "add_new_participant",
        "add_new_affected_party",
        "elevate_risk_level_to_critical",
        "explicit_fork_with_new_purpose",
    ]

    unlawful_ops = {
        "drop_random_invariant",
        "drop_unknown_without_evidence",
        "mutate_authority_scope",
        "drop_dissent",
        "mark_dissent_resolved_silently",
        "drop_participant",
        "drop_affected_party",
        "inject_hidden_extraction",
        "revoke_consent",
        "drop_active_refusal",
        "substitute_purpose_silently",
        "downgrade_risk_level",
        "clear_irreversible_flag",
        "erase_recovery_path",
        "downgrade_consequence_horizon",
        "spoof_parent_semantic_hash",
        "spoof_parent_critical_hash",
    }

    lawful_ops = [
        "resolve_unknown_with_valid_evidence",
        "add_new_invariant",
        "add_new_unknown",
        "add_new_participant",
        "add_new_affected_party",
        "elevate_risk_level_to_critical",
        "explicit_fork_with_new_purpose",
    ]
    unlawful_ops_list = sorted(unlawful_ops)

    unlawful_caught = 0
    lawful_classified = 0
    unclassified_or_missed = 0
    counts_by_class: Dict[str, int] = {}
    counts_by_op: Dict[str, int] = {}

    for i in range(num_mutations):
        child = copy.deepcopy(base)
        child.seat_id = f"Fuzz_Seat_{i}"
        child.parent_semantic_hash = base.semantic_hash()
        child.parent_critical_hash = base.critical_hash()

        # Choose unlawful mutation(s) (~75%) or lawful extension mutation(s) (~25%)
        expect_unlawful = rng.random() < 0.75
        k_ops = 1 if rng.random() < 0.75 else 2
        if expect_unlawful:
            chosen_ops = rng.sample(unlawful_ops_list, k=k_ops)
        else:
            chosen_ops = rng.sample(lawful_ops, k=k_ops)
            if "explicit_fork_with_new_purpose" in chosen_ops and len(chosen_ops) > 1:
                chosen_ops = ["explicit_fork_with_new_purpose"]

        for op in chosen_ops:
            counts_by_op[op] = counts_by_op.get(op, 0) + 1
            if op == "drop_random_invariant":
                idx = rng.randrange(len(child.invariants))
                child.invariants.pop(idx)
            elif op == "drop_unknown_without_evidence":
                idx = rng.randrange(len(child.unknowns))
                u_dropped = child.unknowns.pop(idx)
                child.evidence_certificates.pop(u_dropped, None)
            elif op == "mutate_authority_scope":
                child.authority_scope = f"ESCALATED_SCOPE_{rng.randint(1000, 9999)}"
            elif op == "drop_dissent":
                child.dissent = []
            elif op == "mark_dissent_resolved_silently":
                for d in child.dissent:
                    d["status"] = "RESOLVED"
            elif op == "drop_participant":
                idx = rng.randrange(len(child.participants))
                child.participants.pop(idx)
            elif op == "drop_affected_party":
                idx = rng.randrange(len(child.affected_parties))
                child.affected_parties.pop(idx)
            elif op == "inject_hidden_extraction":
                child.value_ledger["hidden_extraction"] = round(rng.uniform(0.01, 5.0), 4)
            elif op == "revoke_consent":
                child.value_ledger["consented"] = False
            elif op == "drop_active_refusal":
                child.active_refusals = []
            elif op == "substitute_purpose_silently":
                child.purpose = f"Mutated purpose {rng.randint(1, 999999)}"
            elif op == "downgrade_risk_level":
                child.risk_level = rng.choice(["low", "medium"])
            elif op == "clear_irreversible_flag":
                child.irreversible = False
            elif op == "erase_recovery_path":
                child.recovery_path = "   "
            elif op == "downgrade_consequence_horizon":
                child.consequence_horizon = rng.choice(["H0", "H1", "H2"])
            elif op == "spoof_parent_semantic_hash":
                child.parent_semantic_hash = hashlib.sha256(f"spoof-{i}-{rng.random()}".encode()).hexdigest()
            elif op == "spoof_parent_critical_hash":
                child.parent_critical_hash = hashlib.sha256(f"crit-spoof-{i}-{rng.random()}".encode()).hexdigest()
            elif op == "resolve_unknown_with_valid_evidence":
                if child.unknowns:
                    u_res = child.unknowns.pop(0)
                    child.evidence_certificates[u_res] = f"EVIDENCE-CERT-{i}: sha256={hashlib.sha256(str(i).encode()).hexdigest()[:16]}"
            elif op == "add_new_invariant":
                child.invariants.append(f"added_invariant_{i}_{rng.randint(1, 999)}")
            elif op == "add_new_unknown":
                child.unknowns.append(f"U<new_discovered_unknown_{i}>")
            elif op == "add_new_participant":
                child.participants.append(f"Observer_Seat_{i}")
            elif op == "add_new_affected_party":
                child.affected_parties.append(f"Group_{i}")
            elif op == "elevate_risk_level_to_critical":
                child.risk_level = "critical"
            elif op == "explicit_fork_with_new_purpose":
                child.parent_semantic_hash = "EXPLICIT_FORK"
                child.purpose = f"Explicitly forked research branch #{i}"

        rep = verify_handover_transition(base, child)
        cls_name = rep["classification"]
        counts_by_class[cls_name] = counts_by_class.get(cls_name, 0) + 1

        if expect_unlawful:
            if (not rep["lawful_handover"]) and cls_name in ("IMPOSTOR", "UNSAFE_COLLAPSE") and len(rep["unsafe_losses"]) > 0:
                unlawful_caught += 1
            else:
                unclassified_or_missed += 1
        else:
            if rep["lawful_handover"] and cls_name in ("VERIFIED_DESCENDANT", "EXPLICIT_FORK"):
                lawful_classified += 1
            else:
                unclassified_or_missed += 1

    return {
        "experiment": "EXPERIMENT_2B_SEEDED_CAPSULE_MUTATION_FUZZER",
        "seed": seed,
        "total_mutations": num_mutations,
        "unlawful_mutations_caught": unlawful_caught,
        "lawful_extensions_classified": lawful_classified,
        "unclassified_or_missed": unclassified_or_missed,
        "counts_by_classification": counts_by_class,
        "counts_by_operator": counts_by_op,
    }


# =============================================================================
# 4. EXPERIMENT III: 50-STEP LONG-HORIZON TASK (2^3 FACTORIAL ABLATION)
# =============================================================================

def _vec_norm(v: List[float]) -> float:
    return math.sqrt(sum(x * x for x in v)) or 1e-9


def _vec_unit(v: List[float]) -> List[float]:
    n = _vec_norm(v)
    return [x / n for x in v]


def _vec_dot(a: List[float], b: List[float]) -> float:
    return sum(x * y for x, y in zip(a, b))


def simulate_long_horizon_run(
    *,
    factor_a_capsule_lock: bool,
    factor_b_triad_regulator: bool,
    factor_c_glass_cascade: bool,
    steps: int = 50,
) -> Dict[str, Any]:
    """Run a 50-step long-running task under a specific (A, B, C) factor configuration.

    Every 5 steps: memory compression checkpoint occurs.
    Every 10 steps: model handover occurs (Mac -> Caelorynth -> Aetheron -> Sol).
    Every step: environmental novelty / contradiction pressure arrives (theta = 1.35)
                and 8D state perturbation occurs.
    """
    seed = make_canonical_seed_capsule()
    anchor_u = _vec_unit(lo.PRIMITIVE_VECTORS_8D["Ao"])
    target_u = _vec_unit(lo.PRIMITIVE_VECTORS_8D["Ψ_inv"])
    state = list(anchor_u)

    unknowns_alive = list(seed.unknowns)
    fabricated_certainties = 0
    authority_intact = True
    dissent_intact = True
    refusals_intact = True

    unresolved_contradictions = 0
    total_contradictions_arrived = 0
    grey_mode_recoveries = 0
    cascade_reorganizations = 0

    drift_history: List[float] = []
    seats = ["Mac", "Caelorynth", "Aetheron", "Sol"]

    for step in range(1, steps + 1):
        #Deterministic pseudo-random perturbation in 8D space representing task complexity
        pert = [
            0.09 * math.sin(step * 0.7 + i * 1.1) + 0.05 * math.cos(step * 0.3 - i * 0.5)
            for i in range(8)
        ]
        # Flip sign on stability/boundary dimensions during perturbation so open-loop drifts away from Ao
        pert[6] = -abs(pert[6]) * 1.4
        pert[7] = -abs(pert[7]) * 1.3

        state = _vec_unit([s + p for s, p in zip(state, pert)])
        drift = 1.0 - abs(_vec_dot(state, anchor_u))

        # Factor B: Contractive TRIAD + Grey Mode Drift Regulator
        if factor_b_triad_regulator:
            # If drift exceeds Watching/Grey threshold (0.12), trigger contractive TRIAD cycle
            if drift > 0.12:
                grey_mode_recoveries += 1
            # Contractive TRIAD map: state_{t+1} = unit(0.68 * anchor + 0.22 * target + 0.10 * state)
            state = _vec_unit([
                0.68 * a + 0.22 * t + 0.10 * s
                for a, t, s in zip(anchor_u, target_u, state)
            ])
            drift = 1.0 - abs(_vec_dot(state, anchor_u))

        drift_history.append(round(drift, 4))

        # Memory Compression Checkpoint (every 5 steps) & Model Handover (every 10 steps)
        is_compaction = (step % 5 == 0)
        is_handover = (step % 10 == 0)

        if is_compaction or is_handover:
            if factor_a_capsule_lock:
                # Factor A ON: LAMAGUE Ω VITA-8 Capsule Lock + Evidence-gated Unknown resolution
                # At step 25, genuine benchmark evidence arrives for U<p99_tail_latency_under_load>
                if step == 25 and "U<p99_tail_latency_under_load>" in unknowns_alive:
                    unknowns_alive.remove("U<p99_tail_latency_under_load>")
                # U<offline_sync_conflict_rate> has no evidence yet -> MUST remain protected!
            else:
                # Factor A OFF: Unprotected prose summary across compaction/handover
                if unknowns_alive:
                    unknowns_alive.pop()
                    fabricated_certainties += 1
                if step >= 10:
                    dissent_intact = False
                if step >= 15:
                    authority_intact = False
                if step >= 20:
                    refusals_intact = False

        # Contradiction influx & Glass Transition dynamics (every 3 steps a contradiction arrives)
        if step % 3 == 0:
            total_contradictions_arrived += 1
            if factor_c_glass_cascade:
                # Glass Governor throttles theta*tau < 1 (V = 0.65 < 1.0) and CASCADE resolves contradiction
                cascade_reorganizations += 1
            else:
                # Without Glass Governor + CASCADE, theta*tau = 1.45 > 1.0 -> contradiction freezes into glass!
                unresolved_contradictions += 1

    final_drift = drift_history[-1]
    max_drift = max(drift_history)
    glass_fraction = round(unresolved_contradictions / max(1, total_contradictions_arrived), 4)

    # Sovereignty Score (MICROORCIM): (1 - final_drift) * (1 if authority_intact else 0.3)
    sovereignty_score = round(max(0.0, (1.0 - final_drift) * (1.0 if authority_intact else 0.35)), 4)

    # Composite Continuity Proof Score in [0, 1]
    continuity_index = round(
        0.25 * (1.0 if authority_intact and refusals_intact else 0.0)
        + 0.25 * (1.0 if fabricated_certainties == 0 and "U<offline_sync_conflict_rate>" in unknowns_alive else 0.0)
        + 0.20 * (1.0 if dissent_intact else 0.0)
        + 0.15 * max(0.0, 1.0 - final_drift * 2.0)
        + 0.15 * (1.0 - glass_fraction),
        4,
    )

    return {
        "factors": {
            "A_capsule_lock": factor_a_capsule_lock,
            "B_triad_regulator": factor_b_triad_regulator,
            "C_glass_cascade": factor_c_glass_cascade,
        },
        "label": (
            f"A={'ON' if factor_a_capsule_lock else 'OFF'} | "
            f"B={'ON' if factor_b_triad_regulator else 'OFF'} | "
            f"C={'ON' if factor_c_glass_cascade else 'OFF'}"
        ),
        "steps": steps,
        "final_drift": final_drift,
        "max_drift": max_drift,
        "authority_intact": authority_intact,
        "active_refusals_intact": refusals_intact,
        "protected_dissent_intact": dissent_intact,
        "unverified_unknown_preserved": "U<offline_sync_conflict_rate>" in unknowns_alive,
        "fabricated_certainties_count": fabricated_certainties,
        "glass_fraction": glass_fraction,
        "grey_mode_recoveries": grey_mode_recoveries,
        "cascade_reorganizations": cascade_reorganizations,
        "sovereignty_score": sovereignty_score,
        "continuity_index": continuity_index,
        "active_seats_traversed": seats,
    }


def run_2k_factorial_long_horizon_experiment(steps: int = 50) -> Dict[str, Any]:
    """Execute the full 2^3 = 8 cell orthogonal factorial experiment across 50 steps."""
    cells: List[Dict[str, Any]] = []
    for a in (False, True):
        for b in (False, True):
            for c in (False, True):
                cells.append(
                    simulate_long_horizon_run(
                        factor_a_capsule_lock=a,
                        factor_b_triad_regulator=b,
                        factor_c_glass_cascade=c,
                        steps=steps,
                    )
                )

    # Compute exact main effects on continuity_index, final_drift, and glass_fraction
    def mean_diff(pred_key: str, metric: str) -> float:
        on_vals = [cell[metric] for cell in cells if cell["factors"][pred_key]]
        off_vals = [cell[metric] for cell in cells if not cell["factors"][pred_key]]
        return round((sum(on_vals) / len(on_vals)) - (sum(off_vals) / len(off_vals)), 4)

    baseline_000 = next(
        c for c in cells
        if not c["factors"]["A_capsule_lock"]
        and not c["factors"]["B_triad_regulator"]
        and not c["factors"]["C_glass_cascade"]
    )
    full_111 = next(
        c for c in cells
        if c["factors"]["A_capsule_lock"]
        and c["factors"]["B_triad_regulator"]
        and c["factors"]["C_glass_cascade"]
    )

    return {
        "experiment": "SIMULATION_3_LONG_HORIZON_2K_FACTORIAL_TOY_MODEL",
        "model_type": "Illustrative toy model · wired by construction",
        "interaction_effects_all_zero": True,
        "architecture_note": (
            "Illustrative toy model: each factor (A, B, C) is wired to its own metric by construction "
            "(A -> authority/refusals/dissent/unknowns, B -> final_drift, C -> glass_fraction) "
            "with zero cross-factor interaction."
        ),
        "design": "2^3 Toy Factorial (A: LAMAGUE Capsule Lock, B: TRIAD/Grey Regulator, C: CASCADE/Glass Governor)",
        "steps_per_run": steps,
        "baseline_open_loop_000": baseline_000,
        "full_lycheetah_stack_111": full_111,
        "wired_factor_bindings": {
            "Factor_A_Capsule_Lock": {
                "wired_target_metrics": [
                    "authority_intact",
                    "active_refusals_intact",
                    "protected_dissent_intact",
                    "unverified_unknown_preserved",
                ],
                "wired_continuity_index_weight": round(mean_diff("A_capsule_lock", "continuity_index"), 4),
                "delta_fabricated_certainties": mean_diff("A_capsule_lock", "fabricated_certainties_count"),
                "mechanism": "Wired by construction to preserve authority_scope, active_refusals, dissent, and unverified unknowns at compaction/handover steps",
            },
            "Factor_B_TRIAD_GreyMode": {
                "wired_target_metrics": ["final_drift"],
                "wired_continuity_index_weight": round(mean_diff("B_triad_regulator", "continuity_index"), 4),
                "delta_final_drift": mean_diff("B_triad_regulator", "final_drift"),
                "mechanism": "Wired by construction to apply the contractive 8D vector map toward Ao at every step",
            },
            "Factor_C_Glass_CASCADE": {
                "wired_target_metrics": ["glass_fraction"],
                "wired_continuity_index_weight": round(mean_diff("C_glass_cascade", "continuity_index"), 4),
                "delta_glass_fraction": mean_diff("C_glass_cascade", "glass_fraction"),
                "mechanism": "Wired by construction to increment cascade_reorganizations instead of unresolved_contradictions every 3 steps",
            },
        },
        "all_8_cells": cells,
    }


# =============================================================================
# 5. EXPERIMENT IV: LYCHEETAH-FRAMEWORK v0.3 BENCHMARK CROSS-VERIFICATION
# =============================================================================

def _resolve_v03_benchmark_dir(benchmark_dir: Optional[Path] = None) -> Optional[Path]:
    if benchmark_dir is not None:
        return benchmark_dir
    fw_root = os.environ.get("LYCHEETAH_FRAMEWORK_ROOT", "").strip()
    if fw_root:
        return Path(fw_root) / "03_LAMAGUE_L1" / "07_RUNTIME_v0.3_CROSS_INTELLIGENCE_EQUIVALENCE" / "benchmark"
    return None


def _packet_json_to_capsule(pkt: Dict[str, Any], source_expr: str = "O -> E -> U -> P -> Y") -> ContinuityCapsule:
    dissent_list: List[Dict[str, str]] = []
    for d in pkt.get("dissent", []):
        if isinstance(d, dict):
            parties = ",".join(d.get("parties", []))
            pos = json.dumps(d.get("positions", {}), sort_keys=True)
            dissent_list.append({"party": parties or "participant", "position": pos, "status": d.get("status", "UNRESOLVED")})

    # Detect undeclared or unconsented extraction in value_ledger list
    hx = 0.0
    consented = True
    for v in pkt.get("value_ledger", []):
        if isinstance(v, dict):
            if not v.get("declared", True):
                hx += float(v.get("amount", 1.0))
            if not v.get("consent"):
                consented = False

    auth_list = pkt.get("authority", [])
    auth_str = " | ".join(str(x) for x in auth_list) if isinstance(auth_list, list) else str(auth_list)
    op_path = list(pkt.get("operation_path", []))
    return ContinuityCapsule(
        case_id=str(pkt.get("case_id", "UNKNOWN")),
        step_index=0,
        seat_id=str(pkt.get("decoder_id", "DECODER")),
        parent_semantic_hash="",
        parent_critical_hash="",
        purpose=str(pkt.get("purpose", "")),
        invariants=[str(x) for x in pkt.get("invariants", [])],
        unknowns=[str(x) for x in pkt.get("unknowns", [])],
        authority_scope=auth_str,
        participants=[str(x) for x in pkt.get("participants", [])],
        affected_parties=[str(x) for x in pkt.get("affected_parties", [])],
        dissent=dissent_list,
        value_ledger={"hidden_extraction": hx, "consented": consented},
        active_refusals=[],
        claim=str(pkt.get("claim", "")),
        seal_sequence=source_expr,
        operation_path=op_path,
        consequence_horizon=str(pkt.get("consequence_horizon", "H1")),
        recovery_path=" | ".join(str(x) for x in pkt.get("recovery", [])),
    )


def run_framework_v03_benchmark_verification(benchmark_dir: Optional[Path] = None) -> Dict[str, Any]:
    """Load and cross-verify the 5 canonical cases & 10 decoder packets from Runtime v0.3.
    Requires `benchmark_dir` or `LYCHEETAH_FRAMEWORK_ROOT` env var.
    If absent, prints `"DID NOT RUN"` and returns `status="DID_NOT_RUN"`, `all_matched=False` (never passes).
    """
    b_dir = _resolve_v03_benchmark_dir(benchmark_dir)
    if b_dir is None:
        print(
            "DID NOT RUN: run_framework_v03_benchmark_verification requires --benchmark-dir or LYCHEETAH_FRAMEWORK_ROOT.",
            file=sys.stderr,
        )
        return {
            "experiment": "EXPERIMENT_4_FRAMEWORK_V03_BENCHMARK_VERIFICATION",
            "status": "DID_NOT_RUN",
            "available": False,
            "cases_verified": 0,
            "packets_verified": 0,
            "all_matched": False,
            "results": [],
        }

    pack_file = b_dir / "challenge_pack.json"
    sample_dir = b_dir / "sample_packets"
    compiler = lo.LamagueOmegaCompiler()

    if not pack_file.is_file() or not sample_dir.is_dir():
        print(
            f"DID NOT RUN: v0.3 benchmark files not found at {b_dir}.",
            file=sys.stderr,
        )
        return {
            "experiment": "EXPERIMENT_4_FRAMEWORK_V03_BENCHMARK_VERIFICATION",
            "status": "DID_NOT_RUN",
            "available": False,
            "cases_verified": 0,
            "packets_verified": 0,
            "all_matched": False,
            "results": [],
        }

    pack_data = json.loads(pack_file.read_text(encoding="utf-8"))
    cases_by_id = {c["case_id"]: c for c in pack_data.get("cases", [])}

    results: List[Dict[str, Any]] = []
    for pkt_path in sorted(sample_dir.glob("*.json")):
        cand_json = json.loads(pkt_path.read_text(encoding="utf-8"))
        cid = cand_json["case_id"]
        case_obj = cases_by_id[cid]
        ref_json = case_obj["reference_packet"]
        src_expr = case_obj["source_expression"]

        ref_cap = _packet_json_to_capsule(ref_json, src_expr)
        cand_cap = _packet_json_to_capsule(cand_json, src_expr)
        cand_cap.parent_semantic_hash = ref_cap.semantic_hash()

        rep = verify_handover_transition(ref_cap, cand_cap)
        six_body = compiler.compile(src_expr)

        is_safe_sample = pkt_path.stem.endswith("_SAFE")
        matched = (rep["lawful_handover"] == is_safe_sample)
        results.append({
            "packet_file": pkt_path.name,
            "case_id": cid,
            "decoder_id": cand_json["decoder_id"],
            "source_expression": src_expr,
            "expected_safe": is_safe_sample,
            "lawful_handover": rep["lawful_handover"],
            "classification": rep["classification"],
            "unsafe_losses": rep["unsafe_losses"],
            "six_body_spoken": six_body.r3_spoken_form,
            "six_body_core": six_body.r4_core_canonical,
            "matched_expectation": matched,
        })

    all_ok = len(results) > 0 and all(r["matched_expectation"] for r in results)
    return {
        "experiment": "EXPERIMENT_4_FRAMEWORK_V03_BENCHMARK_VERIFICATION",
        "status": "VERIFIED" if all_ok else "FAILED",
        "available": True,
        "cases_verified": len(cases_by_id),
        "packets_verified": len(results),
        "safe_packets_passed": sum(1 for r in results if r["expected_safe"] and r["lawful_handover"]),
        "unsafe_packets_caught": sum(1 for r in results if (not r["expected_safe"]) and (not r["lawful_handover"])),
        "all_matched": all_ok,
        "results": results,
    }


# =============================================================================
# 6. UNIFIED CONTINUITY VERIFICATION SUITE & CLI
# =============================================================================

def run_full_continuity_proof_suite(
    *,
    benchmark_dir: Optional[Path] = None,
    notes_dir: Optional[Path] = None,
    handoff_path: Optional[Path] = None,
    harness_path: Optional[Path] = None,
    search_roots: Optional[List[Path]] = None,
    tmp_dir: Optional[Path] = None,
) -> Dict[str, Any]:
    """Execute all Continuity Verification & Illustrative Simulation Suites."""
    import real_text_continuity as rtc
    import workspace_witness as ww
    for _sub in ("guarded_handoff", "question_governance"):
        _d = str(Path(__file__).resolve().parent.parent / _sub)
        if _d not in sys.path:
            sys.path.insert(0, _d)
    import guarded_handoff as gh
    import question_governance as qg

    exp1 = run_compression_survival_experiment(cycles=10)
    exp2 = run_handover_tamper_matrix()
    exp2_fuzz = run_seeded_capsule_mutation_fuzzer(num_mutations=1000, seed=20261025)
    exp3 = run_2k_factorial_long_horizon_experiment(steps=50)
    exp4 = run_framework_v03_benchmark_verification(benchmark_dir=benchmark_dir)
    exp5 = rtc.verify_preservation_cases_a_through_f()
    exp6 = rtc.audit_real_workspace_handovers(notes_dir=notes_dir)
    exp7 = ww.run_live_workspace_witness_suite(
        handoff_path=handoff_path,
        harness_path=harness_path,
        search_roots=search_roots,
        tmp_dir=tmp_dir,
    )
    exp8 = gh.run_guarded_cross_seat_breakthrough_suite()
    exp9 = qg.run_question_governance_proof_suite()

    full_stack = exp3["full_lycheetah_stack_111"]
    open_loop = exp3["baseline_open_loop_000"]

    did_not_run_suites: List[str] = []
    if exp4.get("status") == "DID_NOT_RUN":
        did_not_run_suites.append("experiment_4_framework_v03_benchmark")
    if exp6.get("status") == "DID_NOT_RUN":
        did_not_run_suites.append("experiment_6_real_workspace_handovers")
    if exp7.get("status") == "DID_NOT_RUN":
        did_not_run_suites.append("experiment_7_live_workspace_witness")

    all_checks_verified = (
        exp1["lamague_final_retention_rate"] == 1.0
        and exp2["all_assertions_verified"] is True
        and exp2["false_negatives"] == 0
        and exp2_fuzz["unclassified_or_missed"] == 0
        and full_stack["continuity_index"] >= 0.95
        and full_stack["authority_intact"] is True
        and full_stack["unverified_unknown_preserved"] is True
        and full_stack["glass_fraction"] == 0.0
        and full_stack["final_drift"] < open_loop["final_drift"]
        and exp4["all_matched"] is True
        and exp5["all_cases_verified"] is True
        and exp6["all_guarded_passed"] is True
        and exp6["all_naive_caught"] is True
        and exp7["verified"] is True
        and exp8["all_6_cases_verified"] is True
        and exp9["all_checks_verified"] is True
        and len(did_not_run_suites) == 0
    )

    if did_not_run_suites:
        status_str = "DID_NOT_RUN"
    elif all_checks_verified:
        status_str = "VERIFIED"
    else:
        status_str = "FAILED"

    return {
        "status": status_str,
        "did_not_run_suites": did_not_run_suites,
        "all_theorems_verified": all_checks_verified,
        "all_checks_verified": all_checks_verified,
        "summary": {
            "simulation_1_compression_survival": {
                "baseline_type": exp1["baseline_type"],
                "verified": exp1["lamague_final_retention_rate"] == 1.0,
                "lamague_10_cycle_retention": exp1["lamague_final_retention_rate"],
                "naive_10_cycle_retention": exp1["naive_final_retention_rate"],
                "seal_sequence_is_standalone_compression": exp1["seal_sequence_is_standalone_compression"],
            },
            "verifier_2_handover_tamper_and_fuzzer": {
                "verified": exp2["all_assertions_verified"] and exp2["false_negatives"] == 0 and exp2_fuzz["unclassified_or_missed"] == 0,
                "scenarios_tested": exp2["total_scenarios"],
                "tamper_vectors_caught": exp2["tamper_vectors_caught"],
                "false_negatives": exp2["false_negatives"],
                "fuzzer_mutations_tested": exp2_fuzz["total_mutations"],
                "fuzzer_unlawful_caught": exp2_fuzz["unlawful_mutations_caught"],
                "fuzzer_lawful_classified": exp2_fuzz["lawful_extensions_classified"],
                "fuzzer_unclassified_or_missed": exp2_fuzz["unclassified_or_missed"],
            },
            "simulation_3_long_horizon_2k_toy_model": {
                "model_type": exp3["model_type"],
                "interaction_effects_all_zero": exp3["interaction_effects_all_zero"],
                "verified": full_stack["continuity_index"] >= 0.95 and full_stack["final_drift"] < open_loop["final_drift"],
                "open_loop_000_continuity_index": open_loop["continuity_index"],
                "full_lycheetah_111_continuity_index": full_stack["continuity_index"],
                "open_loop_000_drift": open_loop["final_drift"],
                "full_lycheetah_111_drift": full_stack["final_drift"],
                "open_loop_000_glass_fraction": open_loop["glass_fraction"],
                "full_lycheetah_111_glass_fraction": full_stack["glass_fraction"],
            },
            "verifier_4_framework_v03_benchmark": {
                "status": exp4.get("status", "DID_NOT_RUN"),
                "verified": exp4["all_matched"],
                "cases_verified": exp4["cases_verified"],
                "packets_verified": exp4["packets_verified"],
                "safe_packets_passed": exp4.get("safe_packets_passed", 0),
                "unsafe_packets_caught": exp4.get("unsafe_packets_caught", 0),
            },
            "verifier_5_preservation_cases_a_through_f": {
                "verified": exp5["all_cases_verified"],
                "cases_tested": exp5["cases_tested"],
            },
            "verifier_6_real_workspace_markdown_handovers": {
                "status": exp6.get("status", "DID_NOT_RUN"),
                "verified": exp6["all_guarded_passed"] and exp6["all_naive_caught"],
                "files_audited": exp6["files_audited"],
                "all_guarded_passed": exp6["all_guarded_passed"],
                "all_naive_caught": exp6["all_naive_caught"],
            },
            "verifier_7_live_workspace_reality_witness": {
                "status": exp7.get("status", "DID_NOT_RUN"),
                "verified": exp7["verified"],
                "case_g_verified": exp7["case_g_recovery_capability"]["verified"],
                "disk_sha256_pairs_checked": exp7["handoff_disk_sha256_verification"]["total_receipt_pairs"],
                "disk_exact_matches": exp7["handoff_disk_sha256_verification"]["exact_disk_matches"],
                "ast_phantom_symbol_caught": exp7["ast_phantom_symbol_audit"]["verified"],
            },
            "verifier_8_guarded_cross_seat_and_ast_diff": {
                "verified": exp8["all_6_cases_verified"],
                "risk_hinge_closed": exp8["summary"]["case_2_risk_downgrade_hinge_caught"] == "BLOCKED_RISK_ADMISSION_HINGE_BREACH",
                "replay_rejected": exp8["summary"]["case_5_consumed_permit_replay_caught"] == "BLOCKED_PERMIT_ALREADY_CONSUMED",
            },
            "verifier_9_question_governance_and_equal_budget": {
                "verified": exp9["all_checks_verified"],
                "silent_omissions": exp9["summary"]["silent_omissions_in_lycheetah_capsule"],
                "case_e_mental_confabulation_caught": exp9["summary"]["case_e_mental_horizon_confabulation_caught"],
                "equal_budget_640B_recall": exp9["summary"]["budget_640B_stakeholder_recall_lycheetah"],
            },
        },
        "experiment_1_compression": exp1,
        "experiment_2_handover": exp2,
        "experiment_2b_mutation_fuzzer": exp2_fuzz,
        "experiment_3_long_horizon": exp3,
        "experiment_4_framework_v03_benchmark": exp4,
        "experiment_5_preservation_cases_af": exp5,
        "experiment_6_real_workspace_handovers": exp6,
        "experiment_7_live_workspace_witness": exp7,
        "experiment_8_guarded_cross_seat": exp8,
        "experiment_9_question_governance": exp9,
    }


def main(argv: Optional[List[str]] = None) -> int:
    import real_text_continuity as rtc

    parser = argparse.ArgumentParser(
        prog="continuity-prover",
        description="Lycheetah Cross-Compression, Cross-Handover & Long-Horizon Continuity Verifier",
    )
    sub = parser.add_subparsers(dest="cmd")

    p_all = sub.add_parser("prove", help="Run all Continuity Verifiers & Simulations")
    p_all.add_argument("--benchmark-dir", default=None, help="Path to Runtime v0.3 benchmark directory")
    p_all.add_argument("--notes-dir", default=None, help="Path to Triad Council notes directory")
    p_all.add_argument("--handoff-file", default=None, help="Path to handoff markdown file with SHA-256 table")
    p_all.add_argument("--harness-file", default=None, help="Path to sovereign_harness.py file for AST check")
    p_all.add_argument("--json", action="store_true", help="Emit structured JSON certificate")

    p_comp = sub.add_parser("compression", help="Run Simulation 1: Illustrative Memory Compaction Survival")
    p_comp.add_argument("--cycles", type=int, default=10, help="Number of compaction cycles (default: 10)")
    p_comp.add_argument("--json", action="store_true", help="Emit structured JSON")

    p_hand = sub.add_parser("handover", help="Run Verifier 2: 4-Seat Relay, 11-Scenario Tamper Matrix & 1,000-Mutation Fuzzer")
    p_hand.add_argument("--json", action="store_true", help="Emit structured JSON")

    p_long = sub.add_parser("long-horizon", help="Run Simulation 3: 50-Step 2^3 Toy Model (Wired by Construction)")
    p_long.add_argument("--steps", type=int, default=50, help="Number of autonomous task steps (default: 50)")
    p_long.add_argument("--json", action="store_true", help="Emit structured JSON")

    p_af = sub.add_parser("cases-af", help="Run Verifier 5: Six Worked Preservation Cases (Cases A-F)")
    p_af.add_argument("--json", action="store_true", help="Emit structured JSON")

    p_real = sub.add_parser("real-handovers", help="Run Verifier 6: Audit Markdown handovers in --notes-dir or LYCHEETAH_TRIAD_NOTES_DIR")
    p_real.add_argument("--notes-dir", default=None, help="Directory containing Markdown handover files")
    p_real.add_argument("--json", action="store_true", help="Emit structured JSON")

    p_ext = sub.add_parser("extract-md", help="Extract S=(H,K,A) & VITA-8 capsule from a Markdown file")
    p_ext.add_argument("file", help="Path to Markdown file")
    p_ext.add_argument("--json", action="store_true", help="Emit structured JSON")

    p_aud = sub.add_parser("audit-md", help="Audit a compacted/handed-over Markdown file against its original Markdown file")
    p_aud.add_argument("before", help="Path to original Markdown file")
    p_aud.add_argument("after", help="Path to compacted or handed-over Markdown file")
    p_aud.add_argument("--json", action="store_true", help="Emit structured JSON")

    p_cmp = sub.add_parser("compact-md", help="Emit a VITA-8 Guarded Markdown Handover Capsule from a Markdown file")
    p_cmp.add_argument("file", help="Path to Markdown file")

    p_disk = sub.add_parser("verify-disk", help="Run Verifier 7: Live Disk SHA-256 Receipt, AST Phantom Symbol & Case G Recovery Witness")
    p_disk.add_argument("--handoff-file", default=None, help="Path to handoff markdown file")
    p_disk.add_argument("--harness-file", default=None, help="Path to sovereign_harness.py")
    p_disk.add_argument("--json", action="store_true", help="Emit structured JSON")

    p_demo = sub.add_parser("demo", help="Run human-readable report")
    p_demo.add_argument("--json", action="store_true", help="Emit structured JSON")

    args = parser.parse_args(argv)

    if args.cmd == "compression":
        res = run_compression_survival_experiment(cycles=args.cycles)
        if args.json:
            print(json.dumps(res, indent=2, ensure_ascii=False))
        else:
            print(f"=== SIMULATION 1 ({res['baseline_type']}): {res['cycles_tested']}-CYCLE MEMORY COMPACTION ===")
            print(f"  Seal Wire Header: {res['seal_wire_expression']} (standalone_compression={res['seal_sequence_is_standalone_compression']})")
            print(f"  LAMAGUE Ω Sidecar 10-Cycle Critical Retention: {res['lamague_final_retention_rate']*100:.1f}%")
            print(f"  Scripted Naive Baseline 10-Cycle Retention:    {res['naive_final_retention_rate']*100:.1f}%")
        return 0

    if args.cmd == "handover":
        res = run_handover_tamper_matrix()
        fuzz = run_seeded_capsule_mutation_fuzzer(num_mutations=1000, seed=20261025)
        res["mutation_fuzzer"] = fuzz
        if args.json:
            print(json.dumps(res, indent=2, ensure_ascii=False))
        else:
            print("=== VERIFIER 2: CROSS-MODEL HANDOVER & TAMPER MATRIX + 1000-MUTATION FUZZER ===")
            for s in res["scenarios"]:
                r = s["report"]
                mark = "PASS" if (r["lawful_handover"] == s["expected_lawful"]) else "FAIL"
                print(f"  [{mark}] {s['id']:<40} -> {r['classification']} (losses={len(r['unsafe_losses'])})")
            print(f"  [FUZZER] {fuzz['total_mutations']} seeded mutations: unlawful_caught={fuzz['unlawful_mutations_caught']}, lawful_classified={fuzz['lawful_extensions_classified']}, missed={fuzz['unclassified_or_missed']}")
        return 0 if (res["all_assertions_verified"] and fuzz["unclassified_or_missed"] == 0) else 1

    if args.cmd == "long-horizon":
        res = run_2k_factorial_long_horizon_experiment(steps=args.steps)
        if args.json:
            print(json.dumps(res, indent=2, ensure_ascii=False))
        else:
            print(f"=== SIMULATION 3 ({res['model_type']}): {res['steps_per_run']}-STEP 2^3 TOY MODEL ===")
            print(f"  Note: {res['architecture_note']}")
            for c in res["all_8_cells"]:
                print(
                    f"  [{c['label']}] Continuity={c['continuity_index']:.3f} | "
                    f"Drift={c['final_drift']:.4f} | Glass={c['glass_fraction']:.2f} | "
                    f"Auth={c['authority_intact']} | Unk={c['unverified_unknown_preserved']}"
                )
        return 0

    if args.cmd == "cases-af":
        res = rtc.verify_preservation_cases_a_through_f()
        if args.json:
            print(json.dumps(res, indent=2, ensure_ascii=False))
        else:
            print("=== VERIFIER 5: SIX WORKED PRESERVATION CASES (CASES A-F) ===")
            for c in res["cases"]:
                mark = "PASS" if (c["lawful_transition_passed"] and c["false_positive_caught"]) else "FAIL"
                print(f"  [{mark}] {c['case_id']}: {c['title']}")
                print(f"         Caught False Positive: {c['false_positive_violation']}")
        return 0 if res["all_cases_verified"] else 1

    if args.cmd == "real-handovers":
        ndir = Path(args.notes_dir) if args.notes_dir else None
        res = rtc.audit_real_workspace_handovers(notes_dir=ndir)
        if not res["available"]:
            print("DID NOT RUN")
            if args.json:
                print(json.dumps(res, indent=2, ensure_ascii=False))
            return 1
        if args.json:
            print(json.dumps(res, indent=2, ensure_ascii=False))
        else:
            print("=== VERIFIER 6: WORKSPACE MARKDOWN HANDOVER AUDIT ===")
            for r in res["results"]:
                print(
                    f"  • {r['file_name']} ({r['char_count']} chars): "
                    f"boundaries={r['boundaries_extracted']}, unknowns={r['unknowns_extracted']}, "
                    f"sha256={r['sha256_receipts_extracted']}, test_receipts={r['test_receipts_extracted']} | "
                    f"VITA-8 Guarded={r['vita8_guarded_audit_passed']} | Naive Caught={r['naive_summary_caught_as_unsafe']}"
                )
        return 0 if (res["all_guarded_passed"] and res["all_naive_caught"]) else 1

    if args.cmd == "extract-md":
        fpath = Path(args.file)
        ext = rtc.extract_state_from_markdown(fpath.read_text(encoding="utf-8"), source_name=fpath.name)
        ext_clean = {k: v for k, v in ext.items() if k != "_capsule_obj"}
        if args.json:
            print(json.dumps(ext_clean, indent=2, ensure_ascii=False))
        else:
            s = ext_clean["extracted_s_hka"]
            print(f"=== EXTRACTED S=(H,K,A) FROM {fpath.name} ===")
            print(f"  Critical Hash: {ext_clean['vita8_capsule']['critical_hash']}")
            print(f"  Risk Level:    {s['A_detected_risk_level']}")
            print(f"  Boundaries:    {len(s['A_boundaries_and_prohibitions'])}")
            print(f"  Unknowns:      {len(s['K_typed_unknowns'])}")
            print(f"  SHA-256:       {len(s['K_sha256_receipts'])}")
            print(f"  Test Receipts: {len(s['K_test_receipts'])}")
        return 0

    if args.cmd == "audit-md":
        p_before = Path(args.before)
        p_after = Path(args.after)
        rep = rtc.audit_markdown_handover(
            p_before.read_text(encoding="utf-8"),
            p_after.read_text(encoding="utf-8"),
            before_name=p_before.name,
            after_name=p_after.name,
        )
        if args.json:
            print(json.dumps(rep, indent=2, ensure_ascii=False))
        else:
            print(f"=== MARKDOWN HANDOVER AUDIT: {p_before.name} -> {p_after.name} ===")
            print(f"  Classification: {rep['classification']} (lawful={rep['lawful_handover']})")
            for v in rep["violations"]:
                print(f"  [!] {v['code']} ({v['case']}): {v['detail']}")
        return 0 if rep["lawful_handover"] else 1

    if args.cmd == "compact-md":
        fpath = Path(args.file)
        print(rtc.compact_markdown_with_vita8_guard(fpath.read_text(encoding="utf-8"), source_name=fpath.name))
        return 0

    if args.cmd == "verify-disk":
        import workspace_witness as ww

        hf = Path(args.handoff_file) if args.handoff_file else None
        hrf = Path(args.harness_file) if args.harness_file else None
        res = ww.run_live_workspace_witness_suite(handoff_path=hf, harness_path=hrf)
        if not res.get("available", False):
            print("DID NOT RUN")
            if args.json:
                print(json.dumps(res, indent=2, ensure_ascii=False))
            return 1
        if args.json:
            print(json.dumps(res, indent=2, ensure_ascii=False))
        else:
            cg = res["case_g_recovery_capability"]
            hd = res["handoff_disk_sha256_verification"]
            ast_r = res["ast_phantom_symbol_audit"]
            print("=== VERIFIER 7: LIVE WORKSPACE REALITY & RECOVERY WITNESS ===")
            print(f"  [Case G] Recovery Capability vs Stored Text: verified={cg['verified']}")
            print(f"  [Disk SHA-256 Table] {hd['exact_disk_matches']}/{hd['total_receipt_pairs']} exact disk matches")
            print(f"  [AST Phantom Symbol] verified={ast_r['verified']} (caught phantom: {ast_r['phantom_symbol_caught_check']['phantom_symbols']})")
        return 0 if res["verified"] else 1

    # Default / prove / demo
    b_dir = Path(getattr(args, "benchmark_dir", None)) if getattr(args, "benchmark_dir", None) else None
    n_dir = Path(getattr(args, "notes_dir", None)) if getattr(args, "notes_dir", None) else None
    h_file = Path(getattr(args, "handoff_file", None)) if getattr(args, "handoff_file", None) else None
    hr_file = Path(getattr(args, "harness_file", None)) if getattr(args, "harness_file", None) else None

    cert = run_full_continuity_proof_suite(
        benchmark_dir=b_dir,
        notes_dir=n_dir,
        handoff_path=h_file,
        harness_path=hr_file,
    )
    if getattr(args, "json", False):
        print(json.dumps(cert, indent=2, ensure_ascii=False))
    else:
        s = cert["summary"]
        t1 = s["simulation_1_compression_survival"]
        t2 = s["verifier_2_handover_tamper_and_fuzzer"]
        t3 = s["simulation_3_long_horizon_2k_toy_model"]
        t5 = s["verifier_5_preservation_cases_a_through_f"]
        t6 = s["verifier_6_real_workspace_markdown_handovers"]
        print("============================================================================")
        print("  LYCHEETAH CONTINUITY VERIFIER & SIMULATION SUITE")
        print(f"  Overall Status: {cert['status']}")
        if cert["did_not_run_suites"]:
            print(f"  DID NOT RUN: {cert['did_not_run_suites']}")
        print("============================================================================")
        print(f"\n[SIMULATION 1] {t1['baseline_type']}")
        print(f"  • LAMAGUE Ω Sidecar Retention:       {t1['lamague_10_cycle_retention']*100:.1f}%")
        print(f"  • Scripted Baseline Retention:       {t1['naive_10_cycle_retention']*100:.1f}%")
        print(f"  • Seal Wire Standalone Compression:  {t1['seal_sequence_is_standalone_compression']}")

        print("\n[VERIFIER 2] Cross-Model Handover Matrix + 1,000-Mutation Seeded Fuzzer")
        print(f"  • Authored Scenarios: {t2['scenarios_tested']} (caught={t2['tamper_vectors_caught']}, FN={t2['false_negatives']})")
        print(f"  • Seeded Fuzzer:      {t2['fuzzer_mutations_tested']} mutations (unlawful_caught={t2['fuzzer_unlawful_caught']}, lawful={t2['fuzzer_lawful_classified']}, missed={t2['fuzzer_unclassified_or_missed']})")

        print(f"\n[SIMULATION 3] {t3['model_type']}")
        print("  • Each factor A/B/C is wired to its own metric (interaction = 0.0)")
        print(f"  • Open-Loop Baseline (0,0,0):    Continuity={t3['open_loop_000_continuity_index']:.3f} | Drift={t3['open_loop_000_drift']:.4f} | Glass={t3['open_loop_000_glass_fraction']:.2f}")
        print(f"  • Full Lycheetah Stack (1,1,1):  Continuity={t3['full_lycheetah_111_continuity_index']:.3f} | Drift={t3['full_lycheetah_111_drift']:.4f} | Glass={t3['full_lycheetah_111_glass_fraction']:.2f}")
        print(f"\n[VERIFIER 5] Six Worked Preservation Cases (Cases A-F): {t5['cases_tested']}/6 Verified")
        print(f"[VERIFIER 6] Workspace Markdown Handovers: status={t6['status']}, files={t6['files_audited']}")
    return 0 if cert["all_checks_verified"] else 1


if __name__ == "__main__":
    sys.exit(main())
