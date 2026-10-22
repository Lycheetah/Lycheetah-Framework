"""Sovereign-harness binding gaps found in the Opus review of 2026-10-22 (RV02).

Each test fails on the code before the repair:
- two permits for one action and actor in one second collided in the gateway,
  and the second was refused after its single-use permit was already claimed;
- the witness could not tell which complete packet was evaluated;
- a permit could be issued with a string scope list or an out-of-set bound scope.
"""

from __future__ import annotations

import types

import pytest

import lycheetah.assurance.gateway as gateway_module
from lycheetah.compaction import AgentStatePacket
from lycheetah.consensus import ConsensusArena
from lycheetah.sovereign_harness import SovereignExecutionHarness, SovereignExecutionPermit

ACTION = {"tool": "metrics.read", "target": "fixture", "side_effect": False}


def _verdict():
    arena = ConsensusArena(anchor=[1.0, 0.0])
    arena.add_agent("worker", [1.0, 0.0], neighbors=["peer"])
    arena.add_agent("peer", [1.0, 0.0], neighbors=["worker"])
    return arena.deliberate()


def _packet(**changes):
    packet = AgentStatePacket(
        id="rv-fixture",
        purpose="Read a local fixture",
        claim="No external effect",
        risk="LOW",
        recovery=[{"id": "noop", "text": "No external mutation"}],
        horizon="Only after human review",
        yield_desc="Hold for review",
    )
    for name, value in changes.items():
        setattr(packet, name, value)
    return packet


def _run(harness, permit_id, packet, verdict):
    permit = harness.issue_permit(
        permit_id=permit_id,
        actor="worker",
        authority_id=None,
        allowed_scopes=("exec:read",),
        bound_scope="exec:read",
        state_version="v1",
        action=ACTION,
        consensus_verdict=verdict,
        reference_packet=_packet(),
        issued_at=100,
        ttl_seconds=300,
    )
    return harness.evaluate_and_execute(
        permit=permit,
        consensus=verdict,
        reference_packet=packet,
        candidate_packet=packet,
        live_action=ACTION,
        live_scope="exec:read",
        current_state_version="v1",
        executor=lambda: {"status": "success"},
        now=110,
    )


def test_two_permits_for_one_action_in_one_second_both_execute(tmp_path, monkeypatch):
    # Pin the gateway clock so both proposals land in the same second.
    monkeypatch.setattr(gateway_module, "time", types.SimpleNamespace(time=lambda: 1_700_000_000.0))
    harness = SovereignExecutionHarness(tmp_path)
    verdict = _verdict()

    first = _run(harness, "first", _packet(), verdict)
    second = _run(harness, "second", _packet(), verdict)

    assert first.stop_reason == "EXECUTED"
    assert second.stop_reason == "EXECUTED"
    assert first.gateway_result.effect_id != second.gateway_result.effect_id


def test_witness_records_which_full_packet_ran(tmp_path):
    verdict = _verdict()
    (tmp_path / "a").mkdir()
    (tmp_path / "b").mkdir()
    control = _run(SovereignExecutionHarness(tmp_path / "a"), "p", _packet(), verdict)
    changed = _run(
        SovereignExecutionHarness(tmp_path / "b"),
        "p",
        _packet(yield_desc="Publish now without further review"),
        verdict,
    )

    # The permit binds the critical hash only, a documented boundary. The
    # witness must still record which complete packet each run evaluated.
    assert (
        control.compaction_summary["candidate_critical_hash"]
        == changed.compaction_summary["candidate_critical_hash"]
    )
    assert control.compaction_summary["candidate_full_hash"] == _packet().full_hash
    assert (
        control.compaction_summary["candidate_full_hash"]
        != changed.compaction_summary["candidate_full_hash"]
    )
    assert control.witness_digest != changed.witness_digest


def test_permit_issuance_rejects_unusable_scopes():
    common = dict(
        permit_id="s",
        actor="worker",
        authority_id=None,
        state_version="v1",
        action=ACTION,
        consensus_digest="0" * 64,
        compaction_critical_hash="0" * 64,
        bound_packet_id="p",
        bound_risk="LOW",
        issued_at=1,
    )
    with pytest.raises(ValueError, match="not a string"):
        SovereignExecutionPermit.issue(allowed_scopes="exec:read", bound_scope="exec:read", **common)
    with pytest.raises(ValueError, match="bound_scope"):
        SovereignExecutionPermit.issue(
            allowed_scopes=("exec:read",), bound_scope="exec:deploy", **common
        )
    permit = SovereignExecutionPermit.issue(
        allowed_scopes=("exec:read",), bound_scope="exec:read", **common
    )
    assert permit.allowed_scopes == ("exec:read",)
