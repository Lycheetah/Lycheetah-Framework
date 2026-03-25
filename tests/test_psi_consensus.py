"""
Tests for psi_consensus.py -- Psi-Consensus Multi-Agent Coherence Protocol

Claim coverage:
  [ACTIVE]  Network with aligned agents converges in gossip
  [ACTIVE]  PsiQOperator accepts merge when both conditions met
  [ACTIVE]  PsiQOperator rejects when states too divergent (eps_neighbor)
  [ACTIVE]  PsiQOperator rejects when candidate not invariant-aligned (theta_inv)
  [ACTIVE]  GossipProtocol converges on already-aligned agents
  [ACTIVE]  GossipProtocol does not converge when Psi_Q rejects all pairs
  [ACTIVE]  GossipProtocol with no edges returns trivially converged
  [ACTIVE]  ObstructionDetector: connected + consistent => obstruction_free
  [ACTIVE]  ObstructionDetector: disconnected graph => H^1 != 0
  [ACTIVE]  ObstructionDetector: inconsistent edge => H^1 != 0
  [ACTIVE]  AdaptiveThresholds: eps_c scales with sqrt(n)
  [ACTIVE]  AdaptiveThresholds: theta_inv relaxes with high drift
  [ACTIVE]  PsiConsensus: drifted agent quarantined before gossip
  [ACTIVE]  PsiConsensus: full run on healthy network converges
  [ACTIVE]  PsiConsensus: consensus_vector near anchor on healthy network
  [ACTIVE]  PsiConsensus: audit trail populated on complete run
  [ACTIVE]  PsiConsensus: 33% Byzantine -- consensus proceeds with one grey agent
  [ACTIVE]  PsiConsensus: no agents registered returns error result
"""

import pytest
import numpy as np
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '12_IMPLEMENTATIONS', 'core'))

from psi_consensus import (
    PsiConsensus, PsiQOperator, GossipProtocol, GossipRound,
    ObstructionDetector, AdaptiveThresholds, ConsensusResult,
    ObstructionReport, build_consensus,
)


# ─── Fixtures ─────────────────────────────────────────────────────────────────

DIM = 8

@pytest.fixture
def anchor():
    rng = np.random.default_rng(0)
    v = rng.standard_normal(DIM)
    return v / np.linalg.norm(v)

@pytest.fixture
def coherence(anchor):
    rng = np.random.default_rng(1)
    v = rng.standard_normal(DIM)
    return v / np.linalg.norm(v)

@pytest.fixture
def near_anchor(anchor):
    """State very close to anchor -- high alignment."""
    rng = np.random.default_rng(2)
    noise = rng.standard_normal(DIM) * 0.05
    v = anchor + noise
    return v / np.linalg.norm(v)

@pytest.fixture
def drifted(anchor):
    """State nearly orthogonal to anchor -- low alignment."""
    rng = np.random.default_rng(99)
    perp = rng.standard_normal(DIM)
    perp -= perp.dot(anchor) * anchor
    return perp / np.linalg.norm(perp)

@pytest.fixture
def net(anchor, coherence):
    return PsiConsensus(anchor=anchor, coherence=coherence)


# ─── PsiQOperator ─────────────────────────────────────────────────────────────

class TestPsiQOperator:

    @pytest.mark.active
    def test_accepts_close_aligned_states(self, anchor):
        """Two near-anchor states should be accepted."""
        rng = np.random.default_rng(10)
        s1 = anchor + rng.standard_normal(DIM) * 0.05
        s1 /= np.linalg.norm(s1)
        s2 = anchor + rng.standard_normal(DIM) * 0.05
        s2 /= np.linalg.norm(s2)

        op = PsiQOperator(anchor=anchor, theta_inv=0.3, eps_neighbor=1.0)
        result = op.apply(s1, s2)
        assert result is not None
        assert abs(np.linalg.norm(result) - 1.0) < 1e-5

    @pytest.mark.active
    def test_rejects_divergent_states(self, anchor, drifted):
        """States far apart (delta > eps_neighbor) must be rejected."""
        op = PsiQOperator(anchor=anchor, theta_inv=0.1, eps_neighbor=0.1)
        # anchor and drifted are ~90 degrees apart -> delta >> 0.1
        result = op.apply(anchor, drifted)
        assert result is None

    @pytest.mark.active
    def test_rejects_non_invariant_candidate(self, anchor):
        """Merge rejected when candidate is not aligned with anchor."""
        rng = np.random.default_rng(20)
        # Build two states that average to something orthogonal to anchor
        perp1 = rng.standard_normal(DIM)
        perp1 -= perp1.dot(anchor) * anchor
        perp1 /= np.linalg.norm(perp1)
        perp2 = rng.standard_normal(DIM)
        perp2 -= perp2.dot(anchor) * anchor
        perp2 /= np.linalg.norm(perp2)

        # Close to each other (delta small) but averaged result orthogonal to anchor
        close_perp2 = perp1 + 0.01 * (perp2 - perp1)
        close_perp2 /= np.linalg.norm(close_perp2)

        op = PsiQOperator(anchor=anchor, theta_inv=0.9, eps_neighbor=1.0)
        result = op.apply(perp1, close_perp2)
        assert result is None

    @pytest.mark.active
    def test_can_merge_consistent_with_apply(self, anchor):
        """can_merge() returns True iff apply() returns non-None."""
        rng = np.random.default_rng(30)
        s1 = anchor + rng.standard_normal(DIM) * 0.05
        s1 /= np.linalg.norm(s1)
        s2 = anchor + rng.standard_normal(DIM) * 0.05
        s2 /= np.linalg.norm(s2)

        op = PsiQOperator(anchor=anchor, theta_inv=0.3, eps_neighbor=1.0)
        assert op.can_merge(s1, s2) == (op.apply(s1, s2) is not None)


# ─── GossipProtocol ──────────────────────────────────────────────────────────

class TestGossipProtocol:

    @pytest.mark.active
    def test_converges_on_near_identical_states(self, anchor):
        """Two nearly identical near-anchor states converge immediately."""
        s0 = anchor.copy()
        s1 = anchor + np.array([0.001] + [0.0] * (DIM - 1))
        s1 /= np.linalg.norm(s1)

        op = PsiQOperator(anchor=anchor, theta_inv=0.3, eps_neighbor=1.0)
        gossip = GossipProtocol(psi_q=op, eps_c=0.01, mu=0.5, max_rounds=50)
        final, rounds = gossip.run({"a": s0, "b": s1}, [("a", "b")])

        assert rounds[-1].converged is True

    @pytest.mark.active
    def test_does_not_converge_when_all_merges_rejected(self, anchor, drifted):
        """When Psi_Q rejects all pairs, gossip makes no progress."""
        # Tight eps_neighbor to force rejection of anchor vs drifted
        op = PsiQOperator(anchor=anchor, theta_inv=0.1, eps_neighbor=0.01)
        gossip = GossipProtocol(psi_q=op, eps_c=0.001, mu=0.5, max_rounds=10)
        _, rounds = gossip.run({"a": anchor, "b": drifted}, [("a", "b")])

        # No exchanges should have happened (all rejected)
        total_exchanges = sum(r.exchanges for r in rounds)
        assert total_exchanges == 0

    @pytest.mark.active
    def test_no_edges_trivially_converged(self, anchor):
        """Network with no edges returns immediately converged."""
        s0 = anchor.copy()
        s1 = anchor.copy()
        op = PsiQOperator(anchor=anchor)
        gossip = GossipProtocol(psi_q=op, eps_c=0.01, max_rounds=50)
        _, rounds = gossip.run({"a": s0, "b": s1}, [])
        assert rounds[0].converged is True

    @pytest.mark.active
    def test_final_states_are_unit_norm(self, anchor):
        """All final states must be unit-norm after gossip."""
        rng = np.random.default_rng(40)
        states = {}
        for i in range(4):
            v = anchor + rng.standard_normal(DIM) * 0.05
            states[f"a{i}"] = v / np.linalg.norm(v)
        edges = [("a0", "a1"), ("a1", "a2"), ("a2", "a3")]
        op = PsiQOperator(anchor=anchor, theta_inv=0.3, eps_neighbor=1.0)
        gossip = GossipProtocol(psi_q=op, eps_c=0.01, max_rounds=50)
        final, _ = gossip.run(states, edges)
        for s in final.values():
            assert abs(np.linalg.norm(s) - 1.0) < 1e-4


# ─── ObstructionDetector ─────────────────────────────────────────────────────

class TestObstructionDetector:

    @pytest.mark.active
    def test_connected_consistent_is_obstruction_free(self, anchor):
        """Connected graph with consistent edges: H^1 = 0."""
        s0 = anchor.copy()
        s1 = anchor + np.array([0.01] + [0.0] * (DIM - 1))
        s1 /= np.linalg.norm(s1)

        det = ObstructionDetector(eps_local=0.5)
        report = det.detect({"a": s0, "b": s1}, [("a", "b")])
        assert report.obstruction_free is True
        assert report.connected is True
        assert report.partition_count == 1
        assert len(report.inconsistent_edges) == 0

    @pytest.mark.active
    def test_disconnected_graph_has_obstruction(self, anchor):
        """Two isolated nodes (no edges): partition_count = 2, H^1 != 0."""
        s0 = anchor.copy()
        s1 = anchor.copy()
        det = ObstructionDetector(eps_local=0.5)
        report = det.detect({"a": s0, "b": s1}, [])  # no edges
        assert report.connected is False
        assert report.partition_count == 2
        assert report.obstruction_free is False

    @pytest.mark.active
    def test_inconsistent_edge_has_obstruction(self, anchor, drifted):
        """Edge with large state difference: H^1 != 0."""
        det = ObstructionDetector(eps_local=0.1)
        report = det.detect(
            {"a": anchor, "b": drifted},
            [("a", "b")],
        )
        # Connected but edge is inconsistent
        assert report.connected is True
        assert len(report.inconsistent_edges) == 1
        assert report.obstruction_free is False

    @pytest.mark.active
    def test_single_agent_always_obstruction_free(self, anchor):
        """Single agent: trivially consistent, trivially connected."""
        det = ObstructionDetector(eps_local=0.1)
        report = det.detect({"a": anchor}, [])
        assert report.obstruction_free is True
        assert report.partition_count == 1


# ─── AdaptiveThresholds ──────────────────────────────────────────────────────

class TestAdaptiveThresholds:

    @pytest.mark.active
    def test_eps_c_scales_with_sqrt_n(self):
        """eps_c(n) = eps_c_base * sqrt(n)."""
        t = AdaptiveThresholds(eps_c_base=0.01)
        assert t.eps_c(1) == pytest.approx(0.01, rel=1e-5)
        assert t.eps_c(4) == pytest.approx(0.02, rel=1e-5)
        assert t.eps_c(9) == pytest.approx(0.03, rel=1e-5)

    @pytest.mark.active
    def test_theta_inv_relaxes_with_high_drift(self):
        """theta_inv decreases (relaxes) when avg_drift is high."""
        t = AdaptiveThresholds(theta_inv_base=0.5)
        low = t.theta_inv(0.0)
        high = t.theta_inv(0.9)
        assert high < low

    @pytest.mark.active
    def test_theta_inv_never_below_minimum(self):
        """theta_inv has a floor of 0.1."""
        t = AdaptiveThresholds(theta_inv_base=0.1)
        assert t.theta_inv(1.0) >= 0.1

    @pytest.mark.active
    def test_eps_neighbor_widens_with_drift(self):
        """eps_neighbor increases (widens) when network drift is high."""
        t = AdaptiveThresholds(eps_neighbor_base=0.5)
        low = t.eps_neighbor(0.0)
        high = t.eps_neighbor(1.0)
        assert high > low


# ─── PsiConsensus Integration ─────────────────────────────────────────────────

class TestPsiConsensus:

    @pytest.mark.active
    def test_empty_network_returns_error(self, anchor, coherence):
        """Zero agents registered -> error ConsensusResult."""
        net = PsiConsensus(anchor=anchor, coherence=coherence)
        result = net.run()
        assert result.converged is False
        assert any("ERROR" in line for line in result.audit_trail)

    @pytest.mark.active
    def test_healthy_network_converges(self, anchor, coherence):
        """Three near-anchor agents connected in a line converge."""
        rng = np.random.default_rng(50)
        net = PsiConsensus(anchor=anchor, coherence=coherence)
        for i in range(3):
            v = anchor + rng.standard_normal(DIM) * 0.05
            v /= np.linalg.norm(v)
            neighbors = []
            if i > 0:
                neighbors.append(f"a{i-1}")
            net.add_agent(f"a{i}", v, neighbors=neighbors)

        result = net.run()
        assert result.converged is True

    @pytest.mark.active
    def test_consensus_vector_near_anchor(self, anchor, coherence):
        """Consensus vector of near-anchor agents should be close to anchor."""
        rng = np.random.default_rng(51)
        net = PsiConsensus(anchor=anchor, coherence=coherence)
        for i in range(4):
            v = anchor + rng.standard_normal(DIM) * 0.02
            v /= np.linalg.norm(v)
            net.add_agent(f"a{i}", v, neighbors=[f"a{(i+1) % 4}"])

        result = net.run()
        assert result.consensus_vector is not None
        alignment = abs(float(np.dot(result.consensus_vector, anchor)))
        assert alignment > 0.9

    @pytest.mark.active
    def test_drifted_agent_quarantined(self, anchor, coherence, drifted):
        """A strongly drifted agent should end up in grey_agents list."""
        net = PsiConsensus(
            anchor=anchor, coherence=coherence,
            grey_kappa=0.5, grey_sigma_hat=0.01, grey_theta_x=0.01,
            grey_alert_threshold=1,
        )
        v = anchor + np.array([0.01] + [0.0] * (DIM - 1))
        v /= np.linalg.norm(v)
        net.add_agent("healthy", v, neighbors=["drifted"])
        net.add_agent("drifted", drifted, neighbors=["healthy"])

        result = net.run()
        assert "drifted" in result.grey_agents

    @pytest.mark.active
    def test_audit_trail_populated(self, anchor, coherence):
        """Audit trail must contain phase markers on a complete run."""
        rng = np.random.default_rng(60)
        net = PsiConsensus(anchor=anchor, coherence=coherence)
        for i in range(2):
            v = anchor + rng.standard_normal(DIM) * 0.02
            v /= np.linalg.norm(v)
            net.add_agent(f"a{i}", v, neighbors=[f"a{1-i}"])

        result = net.run()
        trail = "\n".join(result.audit_trail)
        assert "Psi-Consensus starting" in trail
        assert "Gossip:" in trail
        assert "Consensus drift" in trail

    @pytest.mark.active
    def test_byzantine_tolerance_one_grey_of_three(self, anchor, coherence, drifted):
        """1 of 3 agents grey (33%) -- consensus proceeds on remaining 2."""
        net = PsiConsensus(
            anchor=anchor, coherence=coherence,
            grey_kappa=0.5, grey_sigma_hat=0.01, grey_theta_x=0.01,
            grey_alert_threshold=1,
        )
        rng = np.random.default_rng(70)
        for i in range(2):
            v = anchor + rng.standard_normal(DIM) * 0.02
            v /= np.linalg.norm(v)
            net.add_agent(f"healthy{i}", v, neighbors=[f"healthy{1-i}"])
        net.add_agent("grey_agent", drifted, neighbors=["healthy0"])

        result = net.run()
        # Consensus should still have a valid vector (2 healthy agents)
        assert result.consensus_vector is not None
        assert len(result.grey_agents) >= 1

    @pytest.mark.active
    def test_build_consensus_convenience(self):
        """build_consensus() returns a usable PsiConsensus instance."""
        net = build_consensus(dim=8)
        assert isinstance(net, PsiConsensus)
        # Add a single agent and run -- should not crash
        rng = np.random.default_rng(80)
        v = rng.standard_normal(8)
        v /= np.linalg.norm(v)
        net.add_agent("a0", v)
        result = net.run()
        assert result.consensus_vector is not None
