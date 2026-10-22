"""Psi-Consensus anchor, registration and receipt gaps found in the Opus review
of 2026-10-22 (RV03).

Each test fails on the code before the repair:
- the alignment gate took |<state, anchor>|, so the anchor's antipode scored
  as perfect alignment and a unanimous opposing network passed every flag;
- an agreeing network far from the anchor converged when no one was quarantined;
- cancelling states got the anchor itself as their consensus vector;
- re-registering an agent id reset its quarantine, and unknown neighbors and
  NaN thresholds were accepted silently;
- TRIAD recovery rewrote a dissenter's vector without a trace in later verdicts;
- the MCP network-health tool used a two-strike monitor on one fresh run, so it
  could never quarantine, and printed "Network is healthy" for the antipode;
- Grey Mode scored recovery with the unsigned TRIAD drift, so it readmitted a
  back-hemisphere agent that TRIAD had carried onto the antipode, and
  max_cycles=0 crashed with UnboundLocalError.
"""

from __future__ import annotations

import math

import numpy as np
import pytest

from lycheetah.applications.lycheetah_guard_mcp import format_network_health
from lycheetah.consensus import ConsensusArena
from core.psi_consensus import PsiConsensus  # on sys.path via lycheetah's bootstrap

ANCHOR = np.array([1.0, 0.0, 0.0])
ORTHOGONAL = np.array([0.0, 1.0, 0.0])


def _mesh(states, **options):
    net = PsiConsensus(anchor=ANCHOR, coherence=ANCHOR, **options)
    for agent_id, state in states.items():
        net.add_agent(agent_id, state, neighbors=[other for other in states if other != agent_id])
    return net


def test_unanimous_antipode_of_the_anchor_is_not_a_passing_verdict():
    arena = ConsensusArena(anchor=[1.0, 0.0])
    arena.add_agent("w", [-1.0, 0.0], neighbors=["v"])
    arena.add_agent("v", [-1.0, 0.0], neighbors=["w"])
    verdict = arena.deliberate()
    assert not (verdict.converged and verdict.obstruction_free and verdict.byzantine_safe)

    raw = _mesh({"a": -ANCHOR, "b": -ANCHOR, "c": -ANCHOR}).run()
    assert raw.converged is False
    assert math.isclose(raw.final_drift, 2.0)


def test_network_agreeing_off_the_anchor_does_not_converge():
    raw = _mesh({"a": ORTHOGONAL, "b": ORTHOGONAL, "c": ORTHOGONAL}).run()
    assert raw.grey_agents == []
    assert raw.obstruction_report.obstruction_free is True
    assert raw.converged is False
    assert any("anchor_aligned=False" in line for line in raw.audit_trail)

    control = _mesh({"a": ANCHOR, "b": ANCHOR, "c": ANCHOR}).run()
    assert control.converged is True
    assert control.final_drift == 0.0


def test_cancelling_states_report_no_consensus_direction():
    raw = _mesh({"p": ANCHOR, "q": -ANCHOR}).run()
    assert raw.converged is False
    assert raw.consensus_vector is None
    assert math.isclose(raw.final_drift, 1.0)


def test_an_agent_id_registers_once():
    net = PsiConsensus(anchor=ANCHOR, coherence=ANCHOR)
    net.add_agent("a", ANCHOR)
    with pytest.raises(ValueError, match="already registered"):
        net.add_agent("a", ORTHOGONAL)

    arena = ConsensusArena(anchor=[1.0, 0.0])
    arena.add_agent("a", [1.0, 0.0])
    with pytest.raises(ValueError, match="already registered"):
        arena.add_agent("a", [0.0, 1.0])
    assert arena.proposals["a"].vector == [1.0, 0.0]


def test_unknown_neighbor_is_refused():
    arena = ConsensusArena(anchor=[1.0, 0.0])
    arena.add_agent("a", [1.0, 0.0], neighbors=["ghost"])
    arena.add_agent("b", [1.0, 0.0], neighbors=["a"])
    with pytest.raises(ValueError, match="unregistered"):
        arena.deliberate()


@pytest.mark.parametrize(
    "options",
    [
        {"mu": 0.0},
        {"mu": 1.5},
        {"mu": float("nan")},
        {"max_rounds": 0},
        {"grey_alert_threshold": 0},
        {"grey_kappa": float("nan")},
        {"grey_theta_x": float("inf")},
        {"eps_c_base": float("nan")},
    ],
)
def test_consensus_parameters_must_be_usable(options):
    with pytest.raises(ValueError):
        ConsensusArena.from_spec({"anchor": [1.0, 0.0], "options": options})


def test_consensus_parameters_benign_control():
    arena = ConsensusArena.from_spec(
        {"anchor": [1.0, 0.0], "options": {"mu": 1.0, "max_rounds": 1, "grey_alert_threshold": 3}}
    )
    assert arena.protocol.mu == 1.0


def test_recovery_is_recorded_in_later_verdicts():
    arena = ConsensusArena(anchor=[1.0, 0.0, 0.0, 0.0], grey_alert_threshold=1)
    arena.add_agent("a1", [0.99, 0.08, 0.0, 0.0])
    arena.add_agent("a2", [0.98, -0.06, 0.05, 0.0])
    arena.add_agent("a3", [0.97, 0.04, -0.07, 0.0])
    arena.add_agent("drifted", [0.10, 0.95, 0.25, 0.0])

    before = arena.deliberate()
    assert "drifted" in before.quarantined_agents
    assert not any("RECOVERED" in line for line in before.audit_trail)

    assert arena.recover_agent("drifted", max_cycles=10, r_c_static=0.25).converged is True
    after = arena.deliberate()
    assert after.quarantined_agents == []
    assert any("RECOVERED: 'drifted'" in line for line in after.audit_trail)
    assert after.verify_integrity()


def test_mcp_network_health_quarantines_in_its_single_run():
    report = format_network_health("[[1,1,1],[1,1,1],[1,1,0.9],[1,-1,0]]")
    assert "Grey (quarantined): 1" in report
    assert "Converged on these checks" in report


def test_mcp_network_health_does_not_call_the_antipode_healthy():
    report = format_network_health("[[-1,-1,-1],[-1,-1,-1],[-1,-1,-1]]")
    assert "Converged         : False" in report
    assert "healthy" not in report.lower().replace("network health", "")


def _quarantined_arena(dissenter):
    arena = ConsensusArena(anchor=ANCHOR.tolist(), grey_alert_threshold=1)
    for agent_id, vector in (("a", [1.0, 0.02, 0.0]), ("b", [1.0, -0.02, 0.0]),
                             ("c", [1.0, 0.0, 0.02]), ("x", dissenter)):
        arena.add_agent(agent_id, vector)
    assert "x" in arena.deliberate().quarantined_agents
    return arena


def test_recovery_does_not_readmit_an_agent_it_carried_to_the_antipode():
    arena = _quarantined_arena([-0.5, 0.866, 0.0])
    result = arena.recover_agent("x")
    assert result.converged is False
    assert result.psi_r == pytest.approx(2.0, abs=1e-3)
    assert not any("RECOVERED" in line for line in arena.deliberate().audit_trail)


def test_recovery_still_readmits_an_agent_it_brought_to_the_anchor():
    result = _quarantined_arena(ORTHOGONAL.tolist()).recover_agent("x")
    assert result.converged is True
    assert float(np.dot(result.final_state, ANCHOR)) > 0.99


def test_recovery_needs_at_least_one_cycle():
    with pytest.raises(ValueError, match="max_cycles"):
        _quarantined_arena(ORTHOGONAL.tolist()).recover_agent("x", max_cycles=0)
