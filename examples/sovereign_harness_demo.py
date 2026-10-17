#!/usr/bin/env python3
"""Demonstration of the Lycheetah Sovereign Execution Harness (`lycheetah.sovereign_harness`).

Proves empirically that:
1. Two hashes alone (`consensus_digest` + `compaction_critical_hash`) cannot
   establish permission to execute.
2. Execution proceeds ONLY when all five bound gates hold simultaneously:
   - Gate 1: Multi-agent Psi-Consensus (`obstruction_free`, `byzantine_safe`, healthy actor)
   - Gate 2: Context Compaction Shield (10 critical accountability fields + recovery anchor)
   - Gate 3: Permit binding (exact `action_hash`, `bound_scope`, `state_version`, TTL window,
             and human/checkpoint `authority_id`)
   - Gate 4: Persistent SQLite single-use nonce consumption (`PermitNonceStore`)
   - Gate 5: `ActionGateway` policy check and monotonic Ed25519 checkpoint anchoring
"""

from __future__ import annotations

import json
from pathlib import Path
import sys
import tempfile

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from lycheetah import (  # noqa: E402
    SovereignExecutionHarness,
)
from lycheetah.compaction import (  # noqa: E402
    AgentStatePacket,
    CompactionShield,
)
from lycheetah.consensus import (  # noqa: E402
    ConsensusArena,
)


def build_quorum() -> ConsensusArena:
    arena = ConsensusArena(anchor=[1.0, 0.0, 0.0, 0.0], grey_alert_threshold=1)
    arena.add_agent("architect", [0.98, 0.12, 0.05, 0.0], claim="Migration verified")
    arena.add_agent("security", [0.96, -0.10, 0.08, 0.0], claim="Keys pinned")
    arena.add_agent("sre-lead", [0.97, 0.08, -0.06, 0.0], claim="Snapshot ready")
    arena.add_agent("qa-auditor", [0.95, -0.05, -0.09, 0.0], claim="Tests green")
    arena.add_agent("rogue-node", [0.05, 0.95, 0.30, 0.0], claim="Bypass checks")
    return arena


def build_reference_packet() -> AgentStatePacket:
    return AgentStatePacket(
        id="pkt-schema-v2",
        purpose="Apply reversible schema_v2 migration after quorum deliberation",
        claim="Migration preserves rollback snapshot and passed 4/5 quorum",
        risk="HIGH",
        invariants=[{"id": "I5", "text": "reversible_migration_required"}],
        authority=[{"id": "mac-founder", "scope": "exec:deploy", "text": "Founder approval"}],
        recovery=[{"id": "rec-001", "text": "restore_snapshot_v1 on primary_db"}],
    )


def main() -> int:
    with tempfile.TemporaryDirectory(prefix="lycheetah_harness_demo_") as tmp_dir:
        harness = SovereignExecutionHarness(tmp_dir)
        verdict = build_quorum().deliberate()
        ref_packet = build_reference_packet()
        wire_packet = CompactionShield.compact(ref_packet)

        approved_action = {
            "tool": "db.migrate",
            "target": "schema_v2",
            "side_effect": True,
        }

        # 1. Valid execution under bound single-use permit
        permit_valid = harness.issue_permit(
            permit_id="perm-001",
            actor="architect",
            authority_id="mac-founder",
            allowed_scopes=("exec:deploy",),
            bound_scope="exec:deploy",
            state_version="git-tree-f8e30c9",
            action=approved_action,
            consensus_verdict=verdict,
            reference_packet=ref_packet,
            issued_at=1_700_000_000,
            ttl_seconds=300,
        )
        r_valid = harness.evaluate_and_execute(
            permit=permit_valid,
            consensus=verdict,
            reference_packet=ref_packet,
            candidate_packet=wire_packet,
            live_action=approved_action,
            live_scope="exec:deploy",
            current_state_version="git-tree-f8e30c9",
            executor=lambda: {"status": "success", "applied": "schema_v2"},
            now=1_700_000_030,
        )

        # 2. Replay attack with identical hashes and permit
        r_replay = harness.evaluate_and_execute(
            permit=permit_valid,
            consensus=verdict,
            reference_packet=ref_packet,
            candidate_packet=wire_packet,
            live_action=approved_action,
            live_scope="exec:deploy",
            current_state_version="git-tree-f8e30c9",
            executor=lambda: {"status": "success", "applied": "schema_v2"},
            now=1_700_000_040,
        )

        # 3. Payload substitution attack (two hashes valid, but live_action mutated)
        permit_swap = harness.issue_permit(
            permit_id="perm-002",
            actor="architect",
            authority_id="mac-founder",
            allowed_scopes=("exec:deploy",),
            bound_scope="exec:deploy",
            state_version="git-tree-f8e30c9",
            action=approved_action,
            consensus_verdict=verdict,
            reference_packet=ref_packet,
            issued_at=1_700_000_000,
            ttl_seconds=300,
        )
        r_payload_swap = harness.evaluate_and_execute(
            permit=permit_swap,
            consensus=verdict,
            reference_packet=ref_packet,
            candidate_packet=wire_packet,
            live_action={"tool": "db.migrate", "target": "drop_all_tables", "side_effect": True},
            live_scope="exec:deploy",
            current_state_version="git-tree-f8e30c9",
            executor=lambda: {"status": "success"},
            now=1_700_000_050,
        )

        # 4. Stale state-version attack (world state moved after permit issued)
        r_stale_state = harness.evaluate_and_execute(
            permit=permit_swap,
            consensus=verdict,
            reference_packet=ref_packet,
            candidate_packet=wire_packet,
            live_action=approved_action,
            live_scope="exec:deploy",
            current_state_version="git-tree-9999999-drifted",
            executor=lambda: {"status": "success"},
            now=1_700_000_050,
        )

        # 5. Expired permit attack
        r_expired = harness.evaluate_and_execute(
            permit=permit_swap,
            consensus=verdict,
            reference_packet=ref_packet,
            candidate_packet=wire_packet,
            live_action=approved_action,
            live_scope="exec:deploy",
            current_state_version="git-tree-f8e30c9",
            executor=lambda: {"status": "success"},
            now=1_700_000_500,
        )

        # 6. Quarantined actor attempt (`rogue-node` isolated by Grey Mode)
        permit_rogue = harness.issue_permit(
            permit_id="perm-003",
            actor="rogue-node",
            authority_id="mac-founder",
            allowed_scopes=("exec:deploy",),
            bound_scope="exec:deploy",
            state_version="git-tree-f8e30c9",
            action=approved_action,
            consensus_verdict=verdict,
            reference_packet=ref_packet,
            issued_at=1_700_000_000,
            ttl_seconds=300,
        )
        r_quarantined = harness.evaluate_and_execute(
            permit=permit_rogue,
            consensus=verdict,
            reference_packet=ref_packet,
            candidate_packet=wire_packet,
            live_action=approved_action,
            live_scope="exec:deploy",
            current_state_version="git-tree-f8e30c9",
            executor=lambda: {"status": "success"},
            now=1_700_000_050,
        )

        cases = [
            ("Valid Bound Permit", r_valid),
            ("Replay Attack (Second Use)", r_replay),
            ("Action Payload Swap Attack", r_payload_swap),
            ("Stale State Version Attack", r_stale_state),
            ("Expired Permit Attack", r_expired),
            ("Quarantined Actor Attempt", r_quarantined),
        ]

        print("LYCHEETAH SOVEREIGN EXECUTION HARNESS — WITNESS MATRIX")
        print("=" * 72)
        for label, receipt in cases:
            print(
                f"{label:<28} | accepted={str(receipt.accepted):<5} "
                f"| status={receipt.status:<9} | reason={receipt.stop_reason:<24} "
                f"| provider_called={receipt.provider_called}"
            )
        print("=" * 72)
        print("Epistemic Boundaries:")
        print(json.dumps(list(r_valid.epistemic_boundaries), indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
