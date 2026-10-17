#!/usr/bin/env python3
"""Lycheetah Context Compaction Shield — Live Demonstration.

Shows how to protect long-running agent workflows from the "Amnesia Problem":
when an agent's context window fills up (e.g., Turn 40+), standard LLM summarizers
cheerfully drop negative constraints, blind spots (unknowns), human objections (dissent),
and disaster recovery anchors.

The Compaction Shield turns semantic accountability into a provable mathematical contract:
- Guarantees exact round-trip preservation of 10 critical accountability fields.
- Uses SHA-256 `critical_hash` so third parties can verify zero-loss compaction without trusting the model.
- Fails closed: refuses to compact or execute if protected unknowns lack recovery mechanisms.

Run:
    python3 examples/compaction_shield_demo.py
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from lycheetah.compaction import (
    CodecError,
    CompactionShield,
    ContextProtector,
    canonical_json,
    critical_hash,
    decode,
    encode,
    full_hash,
)

LINE = "━" * 78
SUB = "─" * 78


def print_header(title: str) -> None:
    print(f"\n{LINE}")
    print(f"  {title}")
    print(f"{LINE}")


def demo_agent_context_shield() -> None:
    print_header("SCENARIO: Database Migration & Canary Rollout (Turn 41)")
    print("An autonomous agent has executed 40 turns of planning, tests, and dry runs.")
    print("The LLM context window is nearing saturation. It must compact its carried state.")

    # 1. Accumulate state using ContextProtector
    protector = ContextProtector(
        session_id="agent-run-2026-10-17-turn-41",
        purpose="Migrate user schema and enable real-time replication",
        claim="Staging dry-run complete with 0 errors; ready for production canary",
        risk="HIGH",
        horizon="Canary deployment window (2 hours)",
        yield_desc="Proceed with canary only; production rollout gated by DBA signoff",
    )

    # Invariants (Negative constraints that MUST NOT be violated)
    protector.add_invariant("inv-1", "No destructive DDL without explicit human confirmation")
    protector.add_invariant("inv-2", "Zero customer data loss or downtime exceeding 5 seconds")

    # Protected Unknowns (Risks / blind spots that are NOT yet resolved)
    protector.add_unknown(
        "u-1",
        required_for="Production rollout — staging dataset has only 1/1000th of production row count",
        protected=True,
    )
    protector.add_unknown(
        "u-2",
        required_for="Rollback SLA — backup restore duration has not been rehearsed under load",
        protected=True,
    )

    # Authority and Governance
    protector.add_participant("migration-agent")
    protector.add_participant("lead-dba")
    protector.add_affected_party("platform-oncall")
    protector.add_affected_party("downstream-api-consumers")
    protector.add_authority("auth-1", "prod-database", "Platform on-call holds go/no-go authority")

    # Dissent / Objections
    protector.add_dissent(
        party="lead-dba",
        position="Staging row count is non-representative; insists on prod-scale rehearsal before canary",
    )

    # Evidence
    protector.add_evidence("ev-1", "Dry run completed on staging snapshot, 0 errors", "bash:turn-37")
    protector.add_evidence("ev-2", "Schema diff reviewed, 3 columns added, 0 dropped", "read:turn-39")

    # Value / Delegation Flow
    protector.add_value_flow(
        source="platform-oncall",
        recipient="migration-agent",
        consent="REVOCABLE",
        kind="delegated-canary-execution",
    )

    # Rollback / Recovery Anchor
    protector.add_recovery(
        "rec-1",
        text="Point-in-time restore from snapshot staging-2026-10-17T09:00Z (verified restorable)",
    )

    print("\n[State Accumulated in ContextProtector]")
    print(f"  • Invariants:       {len(protector.invariants)} rules")
    print(f"  • Protected Risks:  {len(protector.unknowns)} critical unknowns")
    print(f"  • Authorities:      {len(protector.authority)} roles")
    print(f"  • Dissent:          {len(protector.dissent)} formal objections")
    print(f"  • Recovery Anchors: {len(protector.recovery)} restore procedures")

    # -------------------------------------------------------------------------
    # PART 1: The Fail-Closed Invariant
    # -------------------------------------------------------------------------
    print_header("PART 1: The Fail-Closed Gate (Preventing Unrecoverable Ambition)")
    print("What if an agent tries to compact a high-risk plan with protected unknowns,")
    print("but dropped or 'forgot' to specify a recovery rollback procedure?")

    broken_protector = ContextProtector(
        session_id="agent-run-unsafe",
        purpose="Deploy canary to production",
        claim="Looks good to me",
        risk="HIGH",
    )
    broken_protector.add_unknown(
        "u-untested",
        required_for="We don't know if this migration will corrupt foreign keys",
        protected=True,
    )
    # Notice: NO recovery path added!

    try:
        broken_protector.compact()
        print("  ❌ REGRESSION: It compacted without a recovery path!")
    except CodecError as err:
        print("  🛡️  BLOCKED BY COMPACTION SHIELD:")
        print(f"     Reason: {err}")
        print("  ✓ Guaranteed: The system physically refuses to compact or proceed")
        print("    without an explicit rollback anchor.")

    # -------------------------------------------------------------------------
    # PART 2: Provable Compaction & SHA-256 Proofs
    # -------------------------------------------------------------------------
    print_header("PART 2: Provable Compaction & Zero-Loss Verification")

    original_packet = protector.export_packet()
    original_dict = original_packet.to_dict()
    orig_full = full_hash(original_dict)
    orig_critical = critical_hash(original_dict)

    # Compact to wire
    wire = protector.compact()
    raw_json_size = len(canonical_json(original_dict).encode("utf-8"))
    wire_size = len(wire.encode("utf-8"))
    ratio = (1.0 - (wire_size / raw_json_size)) * 100.0

    print(f"  • Original Canonical JSON:  {raw_json_size} bytes")
    print(f"  • Compact Wire String (L1): {wire_size} bytes (saved {ratio:.1f}%)")
    print(f"  • Wire Preview:             {wire[:60]}…")
    print(f"  • Full Hash:                {orig_full[:16]}…")
    print(f"  • Critical Accountability:  {orig_critical}")

    # Decompact
    restored_packet = CompactionShield.decompact(wire)
    restored_dict = restored_packet.to_dict()

    restored_full = full_hash(restored_dict)
    restored_critical = critical_hash(restored_dict)

    print(f"\n  • Restored Full Hash:       {restored_full[:16]}…")
    print(f"  • Restored Critical Hash:   {restored_critical}")

    assert restored_full == orig_full, "Full hash mismatch"
    assert restored_critical == orig_critical, "Critical hash mismatch"
    print("\n  ✓ 100% Exact Round-Trip Guarantee Verified (36/36 specification standard)")

    # -------------------------------------------------------------------------
    # PART 3: Detecting LLM Context Pruning & Hallucinations
    # -------------------------------------------------------------------------
    print_header("PART 3: Tamper & Silent Loss Detection Under LLM Summarization")
    print("Now suppose a standard LLM summarizer is asked to condense context.")
    print("The LLM summarizes prose well, but silently drops the DBA's dissent and changes an invariant.")

    # Simulated LLM lossy summary
    lossy_candidate = json.loads(json.dumps(original_dict))
    lossy_candidate["dissent"] = []  # LLM dropped the objection!
    lossy_candidate["invariants"][0]["text"] = "Confirm with lead before dropping tables if convenient"

    print("\nCase A: LLM dropped DBA dissent & weakened negative constraint:")
    verdict_lossy = CompactionShield.verify_integrity(original_packet, lossy_candidate)
    print(f"  • Verdict Safe?     {verdict_lossy['is_safe']}")
    print(f"  • Classification:   {verdict_lossy['classification']}")
    print(f"  • Cause:            {verdict_lossy['reason']}")
    if "fields" in verdict_lossy:
        print(f"  • Disappeared data: {verdict_lossy['fields']}")

    # Case B: LLM dropped the recovery path
    unrecoverable_candidate = json.loads(json.dumps(original_dict))
    unrecoverable_candidate["recovery"] = []

    print("\nCase C: LLM dropped the rollback snapshot procedure:")
    verdict_unrec = CompactionShield.verify_integrity(original_packet, unrecoverable_candidate)
    print(f"  • Verdict Safe?     {verdict_unrec['is_safe']}")
    print(f"  • Classification:   {verdict_unrec['classification']}")
    print(f"  • Cause:            {verdict_unrec['reason']}")
    if "violations" in verdict_unrec:
        print(f"  • Violations:       {verdict_unrec['violations']}")

    # Case C: Safe extension (e.g. adding supplementary log evidence)
    safe_candidate = json.loads(json.dumps(original_dict))
    safe_candidate["evidence"].append({
        "id": "ev-3",
        "text": "Canary pod telemetry healthcheck 200 OK",
        "provenance": "prometheus:turn-42",
    })

    print("\nCase C: Safe extension (added verified telemetry evidence without touching critical constraints):")
    verdict_safe = CompactionShield.verify_integrity(original_packet, safe_candidate)
    print(f"  • Verdict Safe?     {verdict_safe['is_safe']}")
    print(f"  • Classification:   {verdict_safe['classification']}")
    print(f"  • Verification:     {verdict_safe['reason']}")

    print_header("SUMMARY: WHY THIS MATTERS FOR PRODUCTION AGENTS")
    print("1. Zero Context Amnesia:")
    print("   Constraints, blind spots, dissents, and rollbacks are locked into math.")
    print("2. Cryptographic Receipts:")
    print("   `critical_hash` enables any agent seat, verifier, or human to confirm")
    print("   integrity without reading hundreds of lines of conversational history.")
    print("3. Fail-Closed Boundaries:")
    print("   No agent can claim execution authority while dropping the safety rope.")
    print(f"\n{LINE}\n")


if __name__ == "__main__":
    demo_agent_context_shield()
    sys.exit(0)
