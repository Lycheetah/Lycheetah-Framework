#!/usr/bin/env python3
"""Lycheetah Context Compaction Shield — constructed record demonstration.

Round-trips one authored packet and compares manually changed copies. No model
summarizer, database migration, telemetry query or execution authorization runs.

The critical hash covers ten declared accountability fields. It excludes risk,
evidence, horizon and yield, among other fields. A matching hash or the legacy
`is_safe` result is not execution permission, truth verification or general safety.
See examples/meaning_handover/README.md for the existing full-field comparator.

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
    print_header("CONSTRUCTED SCENARIO: Database Migration Handover")
    print("This authored fixture represents a hypothetical agent at turn 41.")
    print("No model, migration, telemetry query or production action runs in this example.")

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
    print_header("PART 1: Rejecting a Declared Protected Unknown Without Recovery")
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
        print("  ✓ This packet was refused because it lacks the required recovery record.")
        print("    This codec check does not control execution or verify a rollback works.")

    # -------------------------------------------------------------------------
    # PART 2: Exact Round-Trip & SHA-256 Comparisons
    # -------------------------------------------------------------------------
    print_header("PART 2: Exact Round-Trip Comparison for One Fixture")

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
    print("\n  ✓ Full and critical hashes match for this one round-tripped fixture.")

    # -------------------------------------------------------------------------
    # PART 3: Comparing Manually Changed Records
    # -------------------------------------------------------------------------
    print_header("PART 3: Comparing Manually Changed Records")
    print("The following copies simulate lost or changed fields; no LLM was evaluated.")
    print("The legacy is_safe flag reports a bounded critical-projection comparison.")

    # Simulated LLM lossy summary
    lossy_candidate = json.loads(json.dumps(original_dict))
    lossy_candidate["dissent"] = []  # LLM dropped the objection!
    lossy_candidate["invariants"][0]["text"] = "Confirm with lead before dropping tables if convenient"

    print("\nCase A: Manually removed DBA dissent & weakened a negative constraint:")
    verdict_lossy = CompactionShield.verify_integrity(original_packet, lossy_candidate)
    print(f"  • Legacy is_safe:   {verdict_lossy['is_safe']}")
    print(f"  • Classification:   {verdict_lossy['classification']}")
    print(f"  • Cause:            {verdict_lossy['reason']}")
    if "fields" in verdict_lossy:
        print(f"  • Disappeared data: {verdict_lossy['fields']}")

    # Case B: LLM dropped the recovery path
    unrecoverable_candidate = json.loads(json.dumps(original_dict))
    unrecoverable_candidate["recovery"] = []

    print("\nCase B: Manually removed the rollback snapshot procedure:")
    verdict_unrec = CompactionShield.verify_integrity(original_packet, unrecoverable_candidate)
    print(f"  • Legacy is_safe:   {verdict_unrec['is_safe']}")
    print(f"  • Classification:   {verdict_unrec['classification']}")
    print(f"  • Cause:            {verdict_unrec['reason']}")
    if "violations" in verdict_unrec:
        print(f"  • Violations:       {verdict_unrec['violations']}")

    # Case C: Added evidence is outside the critical projection
    safe_candidate = json.loads(json.dumps(original_dict))
    safe_candidate["evidence"].append({
        "id": "ev-3",
        "text": "Canary pod telemetry healthcheck 200 OK",
        "provenance": "prometheus:turn-42",
    })

    print("\nCase C: Added fictional telemetry evidence outside the critical projection:")
    verdict_safe = CompactionShield.verify_integrity(original_packet, safe_candidate)
    print(f"  • Legacy is_safe:   {verdict_safe['is_safe']}")
    print(f"  • Classification:   {verdict_safe['classification']}")
    print(f"  • Verification:     {verdict_safe['reason']}")

    print_header("INTERPRETING THESE RECORD COMPARISONS")
    print("The critical hash compares ten declared fields against a trusted reference.")
    print("It excludes risk, evidence, horizon and yield, among other fields.")
    print("A matching projection does not establish truth, consent or execution permission.")
    print("Inspect all declared fields with the existing meaning-handover comparator:")
    print("  examples/meaning_handover/README.md")
    print(f"\n{LINE}\n")


if __name__ == "__main__":
    demo_agent_context_shield()
    sys.exit(0)
