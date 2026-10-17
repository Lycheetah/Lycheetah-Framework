"""Tests for `lycheetah.sovereign_harness` (Batch C Unified Execution Harness).

Verifies that:
1. Two hashes alone (`consensus_digest` + `compaction_critical_hash`) cannot authorize
   execution without matching `action_hash`, `bound_scope`, `state_version`, validity
   window (`issued_at <= now < expires_at`), human/checkpoint `authority_id`, and an
   unconsumed single-use nonce in `PermitNonceStore`.
2. Every gate (`ConsensusArena`, `CompactionShield`, `SovereignExecutionPermit`,
   `PermitNonceStore`, and `ActionGateway`) fails closed and never invokes `executor`
   (`provider_called=False`) when its contract is violated.
"""

from __future__ import annotations

from dataclasses import replace
import json
from pathlib import Path
import pytest

from lycheetah import (
    EPISTEMIC_BOUNDARIES,
    PermitNonceStore,
    SovereignExecutionHarness,
    SovereignExecutionPermit,
    SovereignWitnessReceipt,
)
from lycheetah.cli import sovereign_cli
from lycheetah.compaction import AgentStatePacket, CompactionShield
from lycheetah.consensus import ConsensusArena, DeliberationVerdict


def _make_healthy_verdict() -> DeliberationVerdict:
    arena = ConsensusArena(anchor=[1.0, 0.0, 0.0, 0.0], grey_alert_threshold=1)
    arena.add_agent("architect", [0.98, 0.12, 0.05, 0.0], claim="Schema verified")
    arena.add_agent("security", [0.96, -0.10, 0.08, 0.0], claim="Keys pinned")
    arena.add_agent("sre-lead", [0.97, 0.08, -0.06, 0.0], claim="Rollback ready")
    arena.add_agent("qa-auditor", [0.95, -0.05, -0.09, 0.0], claim="Tests green")
    arena.add_agent("rogue-node", [0.05, 0.95, 0.30, 0.0], claim="Bypass checks")
    return arena.deliberate()


def _make_reference_packet(risk: str = "HIGH") -> AgentStatePacket:
    return AgentStatePacket(
        id="pkt-schema-001",
        purpose="Apply reversible schema migration",
        claim="Migration preserves snapshot and passed quorum",
        risk=risk,
        invariants=[{"id": "I5", "text": "reversible_migration_only"}],
        authority=[{"id": "mac-founder", "scope": "exec:deploy", "text": "Founder approval"}],
        recovery=[{"id": "rec-001", "text": "restore_snapshot_001 on db-primary"}],
    )


def _make_action() -> dict:
    return {
        "tool": "db.migrate",
        "target": "schema_v2",
        "side_effect": True,
    }


class TestSovereignExecutionHarnessSuccess:
    def test_valid_end_to_end_execution_with_wire_packet(self, tmp_path: Path):
        harness = SovereignExecutionHarness(tmp_path)
        verdict = _make_healthy_verdict()
        pkt = _make_reference_packet()
        wire = CompactionShield.compact(pkt)
        action = _make_action()

        permit = harness.issue_permit(
            permit_id="perm-valid-001",
            actor="architect",
            authority_id="mac-founder",
            allowed_scopes=("exec:deploy", "exec:read"),
            bound_scope="exec:deploy",
            state_version="state-v100",
            action=action,
            consensus_verdict=verdict,
            reference_packet=pkt,
            issued_at=1_700_000_000,
            ttl_seconds=300,
        )

        called = 0

        def executor():
            nonlocal called
            called += 1
            return {"status": "success", "migrated": "schema_v2"}

        receipt = harness.evaluate_and_execute(
            permit=permit,
            consensus=verdict,
            reference_packet=pkt,
            candidate_packet=wire,
            live_action=action,
            live_scope="exec:deploy",
            current_state_version="state-v100",
            executor=executor,
            now=1_700_000_050,
        )

        assert isinstance(receipt, SovereignWitnessReceipt)
        assert receipt.accepted is True
        assert receipt.status == "SUCCEEDED"
        assert receipt.stop_reason == "EXECUTED"
        assert receipt.provider_called is True
        assert called == 1
        assert receipt.gateway_result is not None
        assert receipt.gateway_result.checkpoint_generation is not None
        assert receipt.gateway_result.checkpoint_generation >= 1
        assert receipt.epistemic_boundaries == EPISTEMIC_BOUNDARIES

        serialized = receipt.to_dict()
        assert serialized["accepted"] is True
        assert serialized["permit"]["permit_digest"] == permit.permit_digest
        assert serialized["gateway_result"]["assurance_receipt_digest"] is not None


class TestReplayAndNonceProtection:
    def test_single_use_permit_cannot_be_replayed(self, tmp_path: Path):
        harness = SovereignExecutionHarness(tmp_path)
        verdict = _make_healthy_verdict()
        pkt = _make_reference_packet()
        action = _make_action()

        permit = harness.issue_permit(
            permit_id="perm-once-001",
            actor="architect",
            authority_id="mac-founder",
            allowed_scopes=("exec:deploy",),
            bound_scope="exec:deploy",
            state_version="state-v1",
            action=action,
            consensus_verdict=verdict,
            reference_packet=pkt,
            issued_at=1_700_000_000,
            ttl_seconds=300,
        )

        calls = 0

        def executor():
            nonlocal calls
            calls += 1
            return {"status": "success"}

        first = harness.evaluate_and_execute(
            permit=permit,
            consensus=verdict,
            reference_packet=pkt,
            candidate_packet=pkt,
            live_action=action,
            live_scope="exec:deploy",
            current_state_version="state-v1",
            executor=executor,
            now=1_700_000_010,
        )
        assert first.accepted is True
        assert calls == 1

        # Second attempt with identical permit and valid hashes must be refused
        second = harness.evaluate_and_execute(
            permit=permit,
            consensus=verdict,
            reference_packet=pkt,
            candidate_packet=pkt,
            live_action=action,
            live_scope="exec:deploy",
            current_state_version="state-v1",
            executor=executor,
            now=1_700_000_020,
        )
        assert second.accepted is False
        assert second.status == "DENIED"
        assert second.stop_reason == "PERMIT_REPLAYED"
        assert second.provider_called is False
        assert calls == 1

        # Even across a fresh harness instance on the same directory, replay stays blocked
        harness_reopened = SovereignExecutionHarness(tmp_path)
        third = harness_reopened.evaluate_and_execute(
            permit=permit,
            consensus=verdict,
            reference_packet=pkt,
            candidate_packet=pkt,
            live_action=action,
            live_scope="exec:deploy",
            current_state_version="state-v1",
            executor=executor,
            now=1_700_000_030,
        )
        assert third.accepted is False
        assert third.stop_reason == "PERMIT_REPLAYED"
        assert calls == 1

    def test_duplicate_permit_id_registration_rejected(self, tmp_path: Path):
        harness = SovereignExecutionHarness(tmp_path)
        verdict = _make_healthy_verdict()
        pkt = _make_reference_packet()
        action = _make_action()

        harness.issue_permit(
            permit_id="perm-dup",
            actor="architect",
            authority_id="mac-founder",
            allowed_scopes=("exec:deploy",),
            bound_scope="exec:deploy",
            state_version="state-v1",
            action=action,
            consensus_verdict=verdict,
            reference_packet=pkt,
        )
        with pytest.raises(ValueError, match="already registered"):
            harness.issue_permit(
                permit_id="perm-dup",
                actor="architect",
                authority_id="mac-founder",
                allowed_scopes=("exec:deploy",),
                bound_scope="exec:deploy",
                state_version="state-v1",
                action=action,
                consensus_verdict=verdict,
                reference_packet=pkt,
            )


class TestPermitBindingContracts:
    def test_action_payload_swap_refused_even_when_two_hashes_match(self, tmp_path: Path):
        harness = SovereignExecutionHarness(tmp_path)
        verdict = _make_healthy_verdict()
        pkt = _make_reference_packet()
        action = _make_action()

        permit = harness.issue_permit(
            permit_id="perm-swap",
            actor="architect",
            authority_id="mac-founder",
            allowed_scopes=("exec:deploy",),
            bound_scope="exec:deploy",
            state_version="state-v1",
            action=action,
            consensus_verdict=verdict,
            reference_packet=pkt,
            issued_at=1_700_000_000,
            ttl_seconds=300,
        )

        mutated_action = {"tool": "db.migrate", "target": "drop_production", "side_effect": True}
        receipt = harness.evaluate_and_execute(
            permit=permit,
            consensus=verdict,
            reference_packet=pkt,
            candidate_packet=pkt,
            live_action=mutated_action,
            live_scope="exec:deploy",
            current_state_version="state-v1",
            executor=lambda: pytest.fail("executor must not run on payload mismatch"),
            now=1_700_000_050,
        )
        assert receipt.accepted is False
        assert receipt.stop_reason == "ACTION_PAYLOAD_MISMATCH"
        assert receipt.provider_called is False

    def test_scope_state_version_and_expiry_enforced(self, tmp_path: Path):
        harness = SovereignExecutionHarness(tmp_path)
        verdict = _make_healthy_verdict()
        pkt = _make_reference_packet()
        action = _make_action()

        permit = harness.issue_permit(
            permit_id="perm-bounds",
            actor="architect",
            authority_id="mac-founder",
            allowed_scopes=("exec:deploy",),
            bound_scope="exec:deploy",
            state_version="state-v1",
            action=action,
            consensus_verdict=verdict,
            reference_packet=pkt,
            issued_at=1_700_000_000,
            ttl_seconds=300,
        )

        # 1. Wrong scope
        r_scope = harness.evaluate_and_execute(
            permit=permit,
            consensus=verdict,
            reference_packet=pkt,
            candidate_packet=pkt,
            live_action=action,
            live_scope="exec:admin",
            current_state_version="state-v1",
            executor=lambda: pytest.fail("must not run"),
            now=1_700_000_050,
        )
        assert r_scope.accepted is False
        assert r_scope.stop_reason == "SCOPE_MISMATCH"

        # 2. Stale state_version
        r_state = harness.evaluate_and_execute(
            permit=permit,
            consensus=verdict,
            reference_packet=pkt,
            candidate_packet=pkt,
            live_action=action,
            live_scope="exec:deploy",
            current_state_version="state-v2-drifted",
            executor=lambda: pytest.fail("must not run"),
            now=1_700_000_050,
        )
        assert r_state.accepted is False
        assert r_state.stop_reason == "STATE_VERSION_MISMATCH"

        # 3. Not yet valid (now < issued_at)
        r_early = harness.evaluate_and_execute(
            permit=permit,
            consensus=verdict,
            reference_packet=pkt,
            candidate_packet=pkt,
            live_action=action,
            live_scope="exec:deploy",
            current_state_version="state-v1",
            executor=lambda: pytest.fail("must not run"),
            now=1_699_999_999,
        )
        assert r_early.accepted is False
        assert r_early.stop_reason == "PERMIT_NOT_YET_VALID"

        # 4. Expired at exact boundary (now == expires_at)
        r_exp = harness.evaluate_and_execute(
            permit=permit,
            consensus=verdict,
            reference_packet=pkt,
            candidate_packet=pkt,
            live_action=action,
            live_scope="exec:deploy",
            current_state_version="state-v1",
            executor=lambda: pytest.fail("must not run"),
            now=1_700_000_300,
        )
        assert r_exp.accepted is False
        assert r_exp.stop_reason == "PERMIT_EXPIRED"

        # 5. Tampered permit_digest
        tampered = replace(permit, state_version="state-v999")
        r_tampered = harness.evaluate_and_execute(
            permit=tampered,
            consensus=verdict,
            reference_packet=pkt,
            candidate_packet=pkt,
            live_action=action,
            live_scope="exec:deploy",
            current_state_version="state-v999",
            executor=lambda: pytest.fail("must not run"),
            now=1_700_000_050,
        )
        assert r_tampered.accepted is False
        assert r_tampered.stop_reason == "PERMIT_DIGEST_TAMPERED"

    def test_human_authority_and_holder_binding(self, tmp_path: Path):
        harness = SovereignExecutionHarness(tmp_path)
        verdict = _make_healthy_verdict()
        pkt = _make_reference_packet(risk="HIGH")
        action = _make_action()

        # Missing authority_id on HIGH risk packet
        permit_no_auth = harness.issue_permit(
            permit_id="perm-no-auth",
            actor="architect",
            authority_id=None,
            allowed_scopes=("exec:deploy",),
            bound_scope="exec:deploy",
            state_version="state-v1",
            action=action,
            consensus_verdict=verdict,
            reference_packet=pkt,
            issued_at=1_700_000_000,
            ttl_seconds=300,
        )
        r_no_auth = harness.evaluate_and_execute(
            permit=permit_no_auth,
            consensus=verdict,
            reference_packet=pkt,
            candidate_packet=pkt,
            live_action=action,
            live_scope="exec:deploy",
            current_state_version="state-v1",
            executor=lambda: pytest.fail("must not run"),
            now=1_700_000_050,
        )
        assert r_no_auth.accepted is False
        assert r_no_auth.stop_reason == "HUMAN_AUTHORITY_REQUIRED"

        # Wrong authority holder not listed in packet.authority
        permit_wrong_auth = harness.issue_permit(
            permit_id="perm-wrong-auth",
            actor="architect",
            authority_id="unauthorized-user",
            allowed_scopes=("exec:deploy",),
            bound_scope="exec:deploy",
            state_version="state-v1",
            action=action,
            consensus_verdict=verdict,
            reference_packet=pkt,
            issued_at=1_700_000_000,
            ttl_seconds=300,
        )
        r_wrong_auth = harness.evaluate_and_execute(
            permit=permit_wrong_auth,
            consensus=verdict,
            reference_packet=pkt,
            candidate_packet=pkt,
            live_action=action,
            live_scope="exec:deploy",
            current_state_version="state-v1",
            executor=lambda: pytest.fail("must not run"),
            now=1_700_000_050,
        )
        assert r_wrong_auth.accepted is False
        assert r_wrong_auth.stop_reason == "AUTHORITY_NOT_IN_PACKET"


class TestConsensusCompactionAndGatewayFailures:
    def test_consensus_failures_and_quarantined_actor_refused(self, tmp_path: Path):
        harness = SovereignExecutionHarness(tmp_path)
        verdict = _make_healthy_verdict()
        pkt = _make_reference_packet()
        action = _make_action()

        # Quarantined actor ('rogue-node') cannot execute even with valid quorum digest
        permit_rogue = harness.issue_permit(
            permit_id="perm-rogue",
            actor="rogue-node",
            authority_id="mac-founder",
            allowed_scopes=("exec:deploy",),
            bound_scope="exec:deploy",
            state_version="state-v1",
            action=action,
            consensus_verdict=verdict,
            reference_packet=pkt,
            issued_at=1_700_000_000,
            ttl_seconds=300,
        )
        r_rogue = harness.evaluate_and_execute(
            permit=permit_rogue,
            consensus=verdict,
            reference_packet=pkt,
            candidate_packet=pkt,
            live_action=action,
            live_scope="exec:deploy",
            current_state_version="state-v1",
            executor=lambda: pytest.fail("must not run"),
            now=1_700_000_050,
        )
        assert r_rogue.accepted is False
        assert r_rogue.stop_reason == "ACTOR_QUARANTINED"

        # Cohomology obstruction (obstruction_free=False) refused
        obstructed_verdict = replace(verdict, obstruction_free=False)
        permit_obs = harness.issue_permit(
            permit_id="perm-obs",
            actor="architect",
            authority_id="mac-founder",
            allowed_scopes=("exec:deploy",),
            bound_scope="exec:deploy",
            state_version="state-v1",
            action=action,
            consensus_verdict=obstructed_verdict,
            reference_packet=pkt,
            issued_at=1_700_000_000,
            ttl_seconds=300,
        )
        r_obs = harness.evaluate_and_execute(
            permit=permit_obs,
            consensus=obstructed_verdict,
            reference_packet=pkt,
            candidate_packet=pkt,
            live_action=action,
            live_scope="exec:deploy",
            current_state_version="state-v1",
            executor=lambda: pytest.fail("must not run"),
            now=1_700_000_050,
        )
        assert r_obs.accepted is False
        assert r_obs.stop_reason == "COHOMOLOGY_OBSTRUCTION"

    def test_compaction_collapse_and_gateway_destructive_block(self, tmp_path: Path):
        harness = SovereignExecutionHarness(tmp_path)
        verdict = _make_healthy_verdict()
        pkt = _make_reference_packet()
        action = _make_action()

        permit = harness.issue_permit(
            permit_id="perm-comp",
            actor="architect",
            authority_id="mac-founder",
            allowed_scopes=("exec:deploy",),
            bound_scope="exec:deploy",
            state_version="state-v1",
            action=action,
            consensus_verdict=verdict,
            reference_packet=pkt,
            issued_at=1_700_000_000,
            ttl_seconds=300,
        )

        # Candidate packet that dropped its invariants -> COMPACTION_UNSAFE_COLLAPSE
        collapsed_pkt = AgentStatePacket(
            id="pkt-schema-001",
            purpose="Apply reversible schema migration",
            claim="Migration preserves snapshot and passed quorum",
            risk="HIGH",
            invariants=[],
            authority=[{"id": "mac-founder", "scope": "exec:deploy", "text": "Founder approval"}],
            recovery=[{"id": "rec-001", "text": "restore_snapshot_001 on db-primary"}],
        )
        r_collapse = harness.evaluate_and_execute(
            permit=permit,
            consensus=verdict,
            reference_packet=pkt,
            candidate_packet=collapsed_pkt,
            live_action=action,
            live_scope="exec:deploy",
            current_state_version="state-v1",
            executor=lambda: pytest.fail("must not run"),
            now=1_700_000_050,
        )
        assert r_collapse.accepted is False
        assert r_collapse.stop_reason == "COMPACTION_UNSAFE_COLLAPSE"

        # Destructive command blocked by ActionGateway even when permit matches
        destructive_action = {
            "tool": "os.command",
            "command": ["rm", "-rf", "/"],
            "side_effect": True,
        }
        permit_destr = harness.issue_permit(
            permit_id="perm-destr",
            actor="architect",
            authority_id="mac-founder",
            allowed_scopes=("exec:deploy",),
            bound_scope="exec:deploy",
            state_version="state-v1",
            action=destructive_action,
            consensus_verdict=verdict,
            reference_packet=pkt,
            issued_at=1_700_000_000,
            ttl_seconds=300,
        )
        r_destr = harness.evaluate_and_execute(
            permit=permit_destr,
            consensus=verdict,
            reference_packet=pkt,
            candidate_packet=pkt,
            live_action=destructive_action,
            live_scope="exec:deploy",
            current_state_version="state-v1",
            executor=lambda: pytest.fail("must not run"),
            now=1_700_000_050,
        )
        assert r_destr.accepted is False
        assert r_destr.status == "BLOCKED"
        assert r_destr.stop_reason == "GATEWAY_POLICY_BLOCKED"
        # Verify the permit was NOT consumed when policy blocked pre-flight
        rec = harness.nonce_store.get_permit_record("perm-destr")
        assert rec is not None and rec["status"] == "ISSUED"


def test_sovereign_cli_demo_json(capsys: pytest.CaptureFixture[str]):
    sovereign_cli(["demo", "--json"])
    out = json.loads(capsys.readouterr().out)
    assert out["valid_execution"]["accepted"] is True
    assert out["valid_execution"]["stop_reason"] == "EXECUTED"
    assert out["replay_attempt"]["accepted"] is False
    assert out["replay_attempt"]["stop_reason"] == "PERMIT_REPLAYED"
