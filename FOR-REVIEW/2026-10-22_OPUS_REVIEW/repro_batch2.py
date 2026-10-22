#!/usr/bin/env python3
"""Opus review batch 2 probes against the maintained runtime (RV02, RV03).

Each probe prints what happened. Nothing in the repository is modified; every
ledger is written under a temporary directory. Run from the repository root:

    python3 FOR-REVIEW/2026-10-22_OPUS_REVIEW/repro_batch2.py

These target maintained code that was repaired in the working tree, so after
the repair the defect probes report "reproduced": false. Run against HEAD
(d7ae0ad) to see the defects. The unbound-fields probe stays true by design:
the permit binds the critical hash only (see BATCH2 F13). F23 and F24 also stay
true: they are open decisions for Mac, not repairs. The edge-order probe is a
measurement, not a defect probe.
"""
import json
import sys
import tempfile
import types
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

import lycheetah.assurance.gateway as gateway_module  # noqa: E402
from lycheetah.compaction import AgentStatePacket  # noqa: E402
from lycheetah.consensus import ConsensusArena  # noqa: E402
from lycheetah.sovereign_harness import (  # noqa: E402
    SovereignExecutionHarness,
    SovereignExecutionPermit,
)
from lycheetah.applications.lycheetah_guard_mcp import format_network_health  # noqa: E402
from core.psi_consensus import PsiConsensus  # noqa: E402  (on the path via lycheetah)

ACTION = {"tool": "metrics.read", "target": "fixture", "side_effect": False}


def verdict():
    arena = ConsensusArena(anchor=[1.0, 0.0])
    arena.add_agent("worker", [1.0, 0.0], neighbors=["peer"])
    arena.add_agent("peer", [1.0, 0.0], neighbors=["worker"])
    return arena.deliberate()


def packet(**changes):
    p = AgentStatePacket(
        id="rv-fixture", purpose="Read a local fixture", claim="No external effect",
        risk="LOW", recovery=[{"id": "noop", "text": "No external mutation"}],
        horizon="Only after human review", yield_desc="Hold for review",
    )
    for name, value in changes.items():
        setattr(p, name, value)
    return p


def run(harness, permit_id, pkt, v):
    permit = harness.issue_permit(
        permit_id=permit_id, actor="worker", authority_id=None,
        allowed_scopes=("exec:read",), bound_scope="exec:read", state_version="v1",
        action=ACTION, consensus_verdict=v, reference_packet=packet(),
        issued_at=100, ttl_seconds=300,
    )
    calls = []
    r = harness.evaluate_and_execute(
        permit=permit, consensus=v, reference_packet=pkt, candidate_packet=pkt,
        live_action=ACTION, live_scope="exec:read", current_state_version="v1",
        executor=lambda: calls.append(1) or {"status": "success"}, now=110,
    )
    return r, bool(calls)


def unbound_fields():
    """F13: the permit binds the 10 critical fields; yield/horizon/evidence are free."""
    v = verdict()
    cases = {
        "control": packet(),
        "yield": packet(yield_desc="Publish now without further review"),
        "horizon": packet(horizon="Publish immediately"),
        "evidence": packet(evidence=[{"id": "e1", "text": "Substituted", "provenance": "none"}]),
    }
    out = {}
    for name, pkt in cases.items():
        with tempfile.TemporaryDirectory() as tmp:
            r, called = run(SovereignExecutionHarness(tmp), "p", pkt, v)
        out[name] = {"stop_reason": r.stop_reason, "executor_called": called,
                     "summary": r.compaction_summary}
    control = out["control"]["summary"]
    for name in ("yield", "horizon", "evidence"):
        out[name]["summary_identical_to_control"] = out[name].pop("summary") == control
    out["control"].pop("summary")
    out["reproduced"] = all(out[n]["executor_called"] for n in ("yield", "horizon", "evidence"))
    out["receipt_blind_to_change"] = any(
        out[n]["summary_identical_to_control"] for n in ("yield", "horizon", "evidence"))
    return out


def same_second_collision():
    """F11: gateway ids derived from (action, actor, second) collide."""
    real_time = gateway_module.time
    gateway_module.time = types.SimpleNamespace(time=lambda: 1_700_000_000.0)
    try:
        v = verdict()
        with tempfile.TemporaryDirectory() as tmp:
            h = SovereignExecutionHarness(tmp)
            first, _ = run(h, "first", packet(), v)
            second, called = run(h, "second", packet(), v)
            second_permit_claimed = not h.nonce_store.claim_single_use(
                second.permit, now=110)[0]
    finally:
        gateway_module.time = real_time
    return {"first": first.stop_reason, "second": second.stop_reason,
            "second_executor_called": called,
            "second_permit_already_consumed": second_permit_claimed,
            "reproduced": second.stop_reason != "EXECUTED"}


def string_scopes():
    """F12: a string scope list is split into characters at issuance."""
    try:
        p = SovereignExecutionPermit.issue(
            permit_id="s", actor="worker", authority_id=None, allowed_scopes="exec:read",
            bound_scope="exec:read", state_version="v1", action=ACTION,
            consensus_digest="0" * 64, compaction_critical_hash="0" * 64,
            bound_packet_id="p", bound_risk="LOW", issued_at=1,
        )
    except ValueError as error:
        return {"rejected": str(error), "reproduced": False}
    return {"allowed_scopes": list(p.allowed_scopes), "reproduced": True}


E1, E2, E3 = [1.0, 0.0, 0.0], [0.0, 1.0, 0.0], [-1.0, 0.0, 0.0]


def mesh(states, **options):
    net = PsiConsensus(anchor=E1, coherence=E1, **options)
    for agent_id, state in states.items():
        net.add_agent(agent_id, state, neighbors=[o for o in states if o != agent_id])
    return net


def antipode_verdict():
    """F14: every agent at the anchor's antipode, carried to the harness."""
    arena = ConsensusArena(anchor=[1.0, 0.0])
    arena.add_agent("worker", [-1.0, 0.0], neighbors=["peer"])
    arena.add_agent("peer", [-1.0, 0.0], neighbors=["worker"])
    v = arena.deliberate()
    out = {"converged": v.converged, "obstruction_free": v.obstruction_free,
           "byzantine_safe": v.byzantine_safe, "healthy": v.healthy_agents,
           "final_drift": v.final_drift}
    with tempfile.TemporaryDirectory() as tmp:
        try:
            r, called = run(SovereignExecutionHarness(tmp), "anti", packet(), v)
            out["harness"], out["executor_called"] = r.stop_reason, called
        except Exception as error:  # a refusal at issuance is also an answer
            out["harness"] = f"{type(error).__name__}: {error}"
            out["executor_called"] = False
    out["reproduced"] = out["executor_called"]
    return out


def off_anchor_agreement():
    """F15: agreement far from the anchor, nobody quarantined in this run."""
    r = mesh({"a": E2, "b": E2, "c": E2}).run()
    return {"converged": r.converged, "final_drift": r.final_drift,
            "grey": r.grey_agents, "reproduced": r.converged}


def cancelling_states():
    """F16: states that cancel received the anchor as their consensus."""
    r = mesh({"p": E1, "q": E3}).run()
    vec = None if r.consensus_vector is None else [float(x) for x in r.consensus_vector]
    return {"consensus_vector": vec, "final_drift": r.final_drift,
            "reproduced": vec == E1 and r.final_drift == 0.0}


def quarantine_laundering():
    """F17: re-registering an id reset its Grey Mode monitor."""
    net = mesh({"a": E1, "b": E1, "x": E2})
    net.run()
    second = net.run()
    out = {"quarantined_on_second_run": "x" in second.grey_agents}
    try:
        net.add_agent("x", E2, neighbors=["a", "b"])
    except ValueError as error:
        out.update(re_register=f"refused: {error}", reproduced=False)
        return out
    third = net.run()
    out.update(status_after_re_register=net._grey_monitors["x"].status.value,
               quarantined_on_third_run="x" in third.grey_agents,
               reproduced="x" not in third.grey_agents)
    return out


def unknown_neighbor():
    """F18: a neighbor that was never registered was dropped silently."""
    arena = ConsensusArena(anchor=[1.0, 0.0])
    arena.add_agent("a", [1.0, 0.0], neighbors=["ghost"])
    arena.add_agent("b", [1.0, 0.0], neighbors=["a"])
    try:
        v = arena.deliberate()
    except ValueError as error:
        return {"refused": str(error), "reproduced": False}
    return {"converged": v.converged, "reproduced": True}


def nan_threshold():
    """F19: a NaN Grey Mode threshold from a JSON spec disabled quarantine."""
    spec = json.loads('{"anchor": [1.0, 0.0], "options": {"grey_kappa": NaN}}')
    try:
        arena = ConsensusArena.from_spec(spec)
    except ValueError as error:
        return {"refused": str(error), "reproduced": False}
    for name, vec in (("h1", [1.0, 0.0]), ("h2", [1.0, 0.0]), ("rogue", [0.0, 1.0])):
        arena.add_agent(name, vec)
    v = arena.deliberate()
    return {"quarantined": v.quarantined_agents,
            "reproduced": "rogue" not in v.quarantined_agents}


def recovery_trace():
    """F20: TRIAD recovery rewrote a dissenter's vector with no later trace."""
    arena = ConsensusArena(anchor=[1.0, 0.0, 0.0, 0.0], grey_alert_threshold=1)
    for name, vec in (("a1", [0.99, 0.08, 0.0, 0.0]), ("a2", [0.98, -0.06, 0.05, 0.0]),
                      ("a3", [0.97, 0.04, -0.07, 0.0]), ("drifted", [0.10, 0.95, 0.25, 0.0])):
        arena.add_agent(name, vec)
    arena.deliberate()
    rec = arena.recover_agent("drifted", max_cycles=10, r_c_static=0.25)
    v = arena.deliberate()
    traced = any("RECOVERED" in line for line in v.audit_trail)
    return {"recovered": rec.converged, "quarantined_after": v.quarantined_agents,
            "trace_in_verdict": traced, "reproduced": rec.converged and not traced}


def mcp_network_health():
    """F21: the MCP tool could not quarantine and called the antipode healthy."""
    keep = ("Converged ", "Consensus drift", "Grey (quarantined)")
    out = {}
    for name, payload in (("one_outlier", "[[1,1,1],[1,1,1],[1,1,0.9],[1,-1,0]]"),
                          ("antipode", "[[-1,-1,-1],[-1,-1,-1],[-1,-1,-1]]")):
        lines = format_network_health(payload).splitlines()
        out[name] = [line.strip() for line in lines[:-1] if line.strip().startswith(keep)]
        out[name].append(lines[-1].strip())
    out["reproduced"] = any("healthy" in line.lower() for line in out["antipode"])
    return out


def _quarantined(dissenter):
    arena = ConsensusArena(anchor=E1, grey_alert_threshold=1)
    for name, vec in (("a", [1, .02, 0]), ("b", [1, -.02, 0]), ("c", [1, 0, .02]), ("x", dissenter)):
        arena.add_agent(name, vec)
    arena.deliberate()
    return arena


def antipodal_recovery():
    """F22: TRIAD carried a back-hemisphere dissenter to the antipode and readmitted it."""
    rec = _quarantined([-0.5, 0.866, 0.0]).recover_agent("x")
    return {"recovered": rec.converged, "psi_r": round(rec.psi_r, 4),
            "final_state": [round(float(x), 3) for x in rec.final_state],
            "reproduced": rec.converged and float(rec.final_state[0]) < 0}


def default_reentry_threshold():
    """F23: the default re-entry threshold r_merge sits above the unsigned drift ceiling."""
    rec = _quarantined(E2).recover_agent("x")
    return {"r_c_new": round(rec.r_c_new, 4), "unsigned_drift_ceiling": 1.0,
            "reproduced": rec.r_c_new > 1.0}


def one_agent_quorum():
    """F24: a single agent's own verdict satisfies the harness consensus gate."""
    arena = ConsensusArena(anchor=[1.0, 0.0])
    arena.add_agent("worker", [1.0, 0.0])
    v = arena.deliberate()
    with tempfile.TemporaryDirectory() as tmp:
        r, called = run(SovereignExecutionHarness(tmp), "solo", packet(), v)
    return {"agents": v.healthy_agents, "harness": r.stop_reason,
            "executor_called": called, "reproduced": called}


def edge_order():
    """Measurement: gossip updates edges in sequence, so insertion order matters."""
    states = {"a": [0.99, 0.12, 0.0], "b": [0.97, -0.2, 0.1],
              "c": [0.98, 0.05, -0.18], "d": [0.96, 0.1, 0.25]}
    verdicts = []
    for order in (list(states), list(reversed(states))):
        arena = ConsensusArena(anchor=E1)
        for name in order:
            arena.add_agent(name, states[name])
        verdicts.append(arena.deliberate())
    first, second = verdicts
    diff = max(abs(x - y) for x, y in zip(first.consensus_vector, second.consensus_vector))
    return {"rounds": [first.rounds_run, second.rounds_run],
            "max_consensus_component_difference": diff,
            "digests_equal": first.consensus_digest == second.consensus_digest}


if __name__ == "__main__":
    print(json.dumps({
        "F11 same-second gateway id collision": same_second_collision(),
        "F12 string allowed_scopes at issuance": string_scopes(),
        "F13 unbound non-critical packet fields": unbound_fields(),
        "F14 antipode of the anchor passes every flag": antipode_verdict(),
        "F15 agreement off the anchor converges": off_anchor_agreement(),
        "F16 cancelling states get the anchor as consensus": cancelling_states(),
        "F17 re-registration clears a quarantine": quarantine_laundering(),
        "F18 unknown neighbor dropped": unknown_neighbor(),
        "F19 NaN threshold disables quarantine": nan_threshold(),
        "F20 recovery leaves no trace": recovery_trace(),
        "F21 MCP network health": mcp_network_health(),
        "F22 recovery readmits the antipode": antipodal_recovery(),
        "F23 default re-entry threshold above 1": default_reentry_threshold(),
        "F24 one-agent quorum passes the harness": one_agent_quorum(),
        "N2 edge order (measurement)": edge_order(),
    }, indent=2))
