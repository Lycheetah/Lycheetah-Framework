"""Consensus bindings must reject mutated decisions before calling an executor."""

from dataclasses import replace

import numpy as np
import pytest

from lycheetah.compaction import AgentStatePacket
from lycheetah.consensus import CellularSheaf, ConsensusArena, ObstructionDetector, PsiConsensus
from lycheetah.sovereign_harness import SovereignExecutionHarness


def test_changing_failed_consensus_flags_cannot_reuse_its_digest(tmp_path):
    arena = ConsensusArena(anchor=[1.0, 0.0])
    arena.add_agent("worker", [1.0, 0.0], neighbors=["peer"])
    arena.add_agent("peer", [1.0, 0.0], neighbors=["worker"])
    arena.add_agent("isolated", [1.0, 0.0])
    verdict = arena.deliberate()
    assert not verdict.converged and not verdict.obstruction_free
    harness = SovereignExecutionHarness(tmp_path)
    packet = AgentStatePacket(
        id="integrity-fixture", purpose="Read a local fixture", claim="No external effect",
        risk="LOW", recovery=[{"id": "noop", "text": "No external mutation"}],
    )
    action = {"tool": "metrics.read", "target": "fixture", "side_effect": False}
    permit = harness.issue_permit(
        permit_id="integrity-permit", actor="worker", authority_id=None,
        allowed_scopes=("exec:read",), bound_scope="exec:read", state_version="fixture-v1",
        action=action, consensus_verdict=verdict, reference_packet=packet,
        issued_at=100, ttl_seconds=300,
    )
    calls = []
    forged = replace(verdict, converged=True, obstruction_free=True)
    assert forged.consensus_digest == verdict.consensus_digest
    result = harness.evaluate_and_execute(
        permit=permit, consensus=forged, reference_packet=packet, candidate_packet=packet,
        live_action=action, live_scope="exec:read", current_state_version="fixture-v1",
        executor=lambda: calls.append("called") or {"status": "success"}, now=110,
    )
    assert not result.accepted
    assert not result.provider_called
    assert result.stop_reason == "CONSENSUS_INTEGRITY_INVALID"
    assert calls == []
    assert harness.nonce_store.get_permit_record("integrity-permit")["status"] == "ISSUED"


def test_invalid_consensus_cannot_register_a_permit(tmp_path):
    arena = ConsensusArena(anchor=[1.0, 0.0])
    arena.add_agent("worker", [1.0, 0.0])
    verdict = replace(arena.deliberate(), consensus_digest="a" * 64)
    harness = SovereignExecutionHarness(tmp_path)
    packet = AgentStatePacket(id="fixture", purpose="Read", claim="Fixture", risk="LOW")
    with pytest.raises(ValueError, match="integrity"):
        harness.issue_permit(
            permit_id="invalid", actor="worker", authority_id=None,
            allowed_scopes=("exec:read",), bound_scope="exec:read", state_version="v1",
            action={"tool": "metrics.read", "side_effect": False},
            consensus_verdict=verdict, reference_packet=packet,
        )
    assert harness.nonce_store.get_permit_record("invalid") is None


@pytest.mark.parametrize("value", [float("nan"), float("inf"), float("-inf")])
def test_consensus_rejects_nonfinite_anchor_and_agent_vectors(value):
    with pytest.raises(ValueError, match="finite"):
        ConsensusArena(anchor=[value, 0.0])
    arena = ConsensusArena(anchor=[1.0, 0.0])
    with pytest.raises(ValueError, match="finite"):
        arena.add_agent("invalid", [value, 0.0])
    with pytest.raises(ValueError, match="finite"):
        PsiConsensus(anchor=np.array([value, 0.0]), coherence=np.array([1.0, 0.0]))
    protocol = PsiConsensus(anchor=np.array([1.0, 0.0]), coherence=np.array([1.0, 0.0]))
    with pytest.raises(ValueError, match="finite"):
        protocol.add_agent("invalid", np.array([value, 0.0]))


def test_verdict_digest_binds_participants_graph_and_audit():
    arena = ConsensusArena(anchor=[1.0, 0.0])
    arena.add_agent("worker", [1.0, 0.0])
    verdict = arena.deliberate()
    assert verdict.verify_integrity()
    for changes in (
        {"healthy_agents": ["worker", "unapproved"]},
        {"partition_count": 99},
        {"audit_trail": ["Substituted history"]},
        {"anchor_vector": (0.0, 1.0)},
        {"final_drift": float("nan")},
        {"final_drift": verdict.final_drift + 1e-9},
        {"anchor_vector": ()},
    ):
        assert not replace(verdict, **changes).verify_integrity()


@pytest.mark.parametrize("payload", ["[[NaN,0]]", "[[Infinity,0]]", "[[]]", "[[[1,0]]]", "[[1,0],[1]]"])
def test_mcp_network_formatter_refuses_invalid_vectors(payload):
    from lycheetah.applications.lycheetah_guard_mcp import format_network_health

    assert format_network_health(payload).startswith("ERROR:")


@pytest.mark.parametrize(
    "vertices,edges,proxy_pass,dim_h1",
    [(3, [(0, 1), (1, 2), (0, 2)], True, 2), (2, [], False, 0)],
)
def test_pairwise_consistency_proxy_is_not_sheaf_first_cohomology(
    vertices, edges, proxy_pass, dim_h1,
):
    states = {str(i): np.array([1.0, 0.0]) for i in range(vertices)}
    proxy = ObstructionDetector().detect(states, [(str(i), str(j)) for i, j in edges])
    exact = CellularSheaf(vertices, edges, stalk_dim=2).cohomology_certificate()
    assert proxy.obstruction_free is proxy_pass
    assert exact.dim_h1_cohomology == dim_h1
