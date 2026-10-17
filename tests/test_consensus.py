"""Tests for lycheetah.consensus (Psi-Consensus, Grey Mode, ConsensusArena, and CLI)."""

from __future__ import annotations

import json

import numpy as np
import pytest

from lycheetah.consensus import (
    AdaptiveThresholds,
    ConsensusArena,
    GossipProtocol,
    GreyModeStatus,
    ObstructionDetector,
    PsiConsensus,
    PsiQOperator,
    build_consensus,
)


# ============================================================================
# 1. Core Operators & Topological Obstruction Detection
# ============================================================================


def test_psi_q_operator_accepts_aligned_neighbors():
    anchor = np.array([1.0, 0.0, 0.0, 0.0])
    psi_q = PsiQOperator(anchor=anchor, theta_inv=0.7, eps_neighbor=0.5)

    s1 = np.array([0.98, 0.20, 0.0, 0.0])
    s1 = s1 / np.linalg.norm(s1)
    s2 = np.array([0.96, -0.15, 0.10, 0.0])
    s2 = s2 / np.linalg.norm(s2)

    merged = psi_q.apply(s1, s2)
    assert merged is not None
    assert abs(float(np.linalg.norm(merged)) - 1.0) < 1e-6
    assert abs(float(np.dot(merged, anchor))) >= 0.7


def test_psi_q_operator_rejects_distant_or_off_anchor_states():
    anchor = np.array([1.0, 0.0, 0.0, 0.0])
    psi_q = PsiQOperator(anchor=anchor, theta_inv=0.8, eps_neighbor=0.3)

    # Distant neighbors
    s1 = np.array([1.0, 0.0, 0.0, 0.0])
    s2 = np.array([0.0, 1.0, 0.0, 0.0])
    assert psi_q.apply(s1, s2) is None
    assert psi_q.can_merge(s1, s2) is False


def test_obstruction_detector_connected_vs_partitioned():
    detector = ObstructionDetector(eps_local=0.4)
    s1 = np.array([1.0, 0.0])
    s2 = np.array([0.98, 0.19])
    s2 = s2 / np.linalg.norm(s2)
    s3 = np.array([0.96, 0.28])
    s3 = s3 / np.linalg.norm(s3)

    states = {"a1": s1, "a2": s2, "a3": s3}

    # Connected graph with small local deltas -> H^1 = 0
    rep_ok = detector.detect(states, [("a1", "a2"), ("a2", "a3")])
    assert rep_ok.obstruction_free is True
    assert rep_ok.connected is True
    assert rep_ok.partition_count == 1
    assert rep_ok.inconsistent_edges == []

    # Disconnected graph (a3 isolated) -> H^1 != 0
    rep_disc = detector.detect(states, [("a1", "a2")])
    assert rep_disc.obstruction_free is False
    assert rep_disc.connected is False
    assert rep_disc.partition_count == 2


# ============================================================================
# 2. Byzantine Quarantine & 33% Fault Tolerance
# ============================================================================


def test_five_agent_byzantine_quarantine_and_convergence():
    anchor = [1.0, 0.0, 0.0, 0.0]
    arena = ConsensusArena(anchor=anchor, grey_alert_threshold=1)

    arena.add_agent("architect", [0.99, 0.10, 0.02, 0.0], role="architect")
    arena.add_agent("security", [0.97, -0.12, 0.05, 0.0], role="security")
    arena.add_agent("sre", [0.98, 0.06, -0.08, 0.0], role="sre")
    arena.add_agent("qa", [0.96, -0.08, -0.06, 0.0], role="qa")
    # 1 rogue/hallucinating agent orthogonal to the constitutional anchor (20% <= 33%)
    arena.add_agent("rogue", [0.02, 0.98, 0.19, 0.0], role="rogue")

    verdict = arena.deliberate()
    assert verdict.converged is True
    assert verdict.obstruction_free is True
    assert verdict.byzantine_safe is True
    assert verdict.quarantined_agents == ["rogue"]
    assert set(verdict.healthy_agents) == {"architect", "security", "sre", "qa"}
    assert verdict.final_drift < 0.02
    assert len(verdict.consensus_digest) == 64


def test_byzantine_threshold_exceeded_flagged():
    anchor = [1.0, 0.0, 0.0, 0.0]
    arena = ConsensusArena(anchor=anchor, grey_alert_threshold=1)

    # 2 healthy, 2 rogue (50% > 33% Byzantine tolerance)
    arena.add_agent("h1", [0.99, 0.05, 0.0, 0.0])
    arena.add_agent("h2", [0.98, -0.05, 0.0, 0.0])
    arena.add_agent("rogue1", [0.0, 1.0, 0.0, 0.0])
    arena.add_agent("rogue2", [0.0, 0.0, 1.0, 0.0])

    verdict = arena.deliberate()
    assert set(verdict.quarantined_agents) == {"rogue1", "rogue2"}
    assert verdict.byzantine_safe is False


# ============================================================================
# 3. TRIAD Grey Mode Recovery Cycle
# ============================================================================


def test_quarantined_agent_triad_recovery_and_reintegration():
    anchor = [1.0, 0.0, 0.0, 0.0]
    arena = ConsensusArena(anchor=anchor, grey_alert_threshold=1)

    arena.add_agent("a1", [0.99, 0.08, 0.0, 0.0])
    arena.add_agent("a2", [0.98, -0.06, 0.05, 0.0])
    arena.add_agent("a3", [0.97, 0.04, -0.07, 0.0])
    arena.add_agent("drifted", [0.10, 0.95, 0.25, 0.0])

    verdict1 = arena.deliberate()
    assert "drifted" in verdict1.quarantined_agents
    assert arena.agent_status("drifted")["status"] == GreyModeStatus.GREY.value

    # Run TRIAD recovery on the quarantined agent
    rec = arena.recover_agent("drifted", max_cycles=10, r_c_static=0.25)
    assert rec.converged is True
    assert rec.psi_r < 0.25
    assert arena.agent_status("drifted")["status"] == GreyModeStatus.HEALTHY.value

    # Re-run deliberation: all 4 agents now participate and converge with 0 quarantined
    verdict2 = arena.deliberate()
    assert verdict2.converged is True
    assert verdict2.quarantined_agents == []
    assert len(verdict2.healthy_agents) == 4


# ============================================================================
# 4. Validation, Convenience Builders & CLI
# ============================================================================


def test_validation_errors():
    with pytest.raises(ValueError, match="zero norm"):
        ConsensusArena(anchor=[0.0, 0.0, 0.0])

    arena = ConsensusArena(anchor=[1.0, 0.0, 0.0])
    with pytest.raises(ValueError, match="dimension"):
        arena.add_agent("bad", [1.0, 0.0])

    with pytest.raises(KeyError, match="Unknown agent_id"):
        arena.agent_status("nonexistent")


def test_build_consensus_helper():
    net = build_consensus(dim=6)
    assert isinstance(net, PsiConsensus)
    assert net.anchor.shape == (6,)
    assert isinstance(net.thresholds, AdaptiveThresholds)
    psi_q = PsiQOperator(anchor=net.anchor)
    gossip = GossipProtocol(psi_q=psi_q)
    assert gossip.max_rounds == 100


def test_consensus_cli_workflow(tmp_path):
    from lycheetah.cli import consensus_cli

    spec = {
        "anchor": [1.0, 0.0, 0.0, 0.0],
        "options": {"grey_alert_threshold": 1},
        "agents": [
            {"id": "a1", "vector": [0.99, 0.10, 0.0, 0.0], "role": "protector"},
            {"id": "a2", "vector": [0.98, -0.08, 0.05, 0.0], "role": "healer"},
            {"id": "a3", "vector": [0.97, 0.05, -0.09, 0.0], "role": "beacon"},
            {"id": "a4", "vector": [0.96, -0.04, 0.06, 0.0], "role": "auditor"},
            {"id": "rogue", "vector": [0.05, 0.98, 0.15, 0.0], "role": "rogue"},
        ],
    }
    spec_file = tmp_path / "spec.json"
    spec_file.write_text(json.dumps(spec), encoding="utf-8")
    verdict_file = tmp_path / "verdict.json"
    recovery_file = tmp_path / "recovery.json"

    # 1. run
    consensus_cli(["run", str(spec_file), "-o", str(verdict_file)])
    assert verdict_file.exists()
    verdict_data = json.loads(verdict_file.read_text(encoding="utf-8"))
    assert verdict_data["converged"] is True
    assert verdict_data["byzantine_safe"] is True
    assert verdict_data["quarantined_agents"] == ["rogue"]

    # 2. recover
    consensus_cli(["recover", str(spec_file), "--agent", "rogue", "-o", str(recovery_file)])
    assert recovery_file.exists()
    rec_data = json.loads(recovery_file.read_text(encoding="utf-8"))
    assert rec_data["converged"] is True
    assert rec_data["quarantined_before"] is True
