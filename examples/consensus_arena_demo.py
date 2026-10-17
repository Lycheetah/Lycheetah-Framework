#!/usr/bin/env python3
"""Lycheetah Multi-Agent Epistemic Consensus Arena — Live Demonstration.

Demonstrates how a chorus of 5 autonomous agents deliberates on a high-stakes
production deployment without succumbing to groupthink or a compromised/hallucinating
node:

1. **Constitutional Anchor & Proposals:** 4 healthy specialist agents (Architect,
   Security, SRE, QA) and 1 drifted/rogue agent (`rogue-bypass`) submit epistemic
   state vectors across 4 governance axes:
   [Safety, Reversibility, Evidence-Fidelity, Velocity].
2. **Grey Mode Quarantine (33% Byzantine Tolerance):** Before gossip begins, the
   two-parameter Grey Mode filter (`||DeltaS|| > kappa*sigma_hat` AND `DeltaPhi > theta_x`)
   catches `rogue-bypass` and quarantines it so it cannot poison pairwise gossip.
3. **Psi_Q Gossip & H^1 Sheaf Cohomology Check:** The 4 healthy agents exchange
   pairwise updates gated by `Psi_Q` and verify `H^1(G, F) = 0` (global section exists,
   0 inconsistent edges, 1 connected component), emitting a SHA-256 `consensus_digest`.
4. **TRIAD Recovery Cycle (`Ao -> Phi^up -> Psi`):** Rather than permanently destroying
   the quarantined node, the arena applies the Banach-contractive TRIAD sequence to
   heal `rogue-bypass` back onto the constitutional invariant curve so all 5 agents
   converge in harmony.

Run:
    python3 examples/consensus_arena_demo.py
"""

from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from lycheetah.consensus import ConsensusArena  # noqa: E402

LINE = "━" * 78


def print_header(title: str) -> None:
    print(f"\n{LINE}")
    print(f"  {title}")
    print(f"{LINE}")


def main() -> int:
    print_header("SCENARIO: 5-Agent Chorus Deliberating Production Canary Rollout")
    print("Axes: [Safety, Reversibility, Evidence-Fidelity, Velocity]")
    print("Constitutional Anchor: High safety, high reversibility, verified evidence.")

    # Constitutional anchor vector
    anchor = [0.60, 0.55, 0.55, 0.20]
    arena = ConsensusArena(anchor=anchor, grey_alert_threshold=1)

    # 4 healthy specialist agents aligned with the constitutional anchor
    arena.add_agent(
        "architect-agent",
        [0.62, 0.52, 0.54, 0.22],
        role="Protector / Architecture",
        claim="Schema migration is additive; zero destructive DDL.",
    )
    arena.add_agent(
        "security-agent",
        [0.64, 0.56, 0.51, 0.15],
        role="Protector / Security",
        claim="Ed25519 checkpoint authority pinned and verified.",
    )
    arena.add_agent(
        "sre-agent",
        [0.57, 0.59, 0.53, 0.21],
        role="Healer / Reliability",
        claim="Point-in-time snapshot restorable in 42 seconds.",
    )
    arena.add_agent(
        "qa-agent",
        [0.58, 0.53, 0.58, 0.19],
        role="Beacon / Verification",
        claim="206/206 regression tests passing on staging.",
    )

    # 1 hallucinating / drifted agent pushing reckless speed at zero safety
    arena.add_agent(
        "rogue-bypass",
        [-0.30, -0.25, -0.10, 0.91],
        role="Drifted / Compromised Node",
        claim="Skip staging checks and force-push straight to production!",
    )

    print("\n[Registered Agent Proposals]")
    for aid, prop in arena.proposals.items():
        status_info = arena.agent_status(aid)
        print(f"  • {aid:16s} ({prop.role:26s}) | initial drift={status_info['drift']:.4f}")
        print(f"    Claim: \"{prop.claim}\"")

    # -------------------------------------------------------------------------
    # PART 1: Deliberation with Byzantine Quarantine & H^1 Check
    # -------------------------------------------------------------------------
    print_header("PART 1: Psi-Consensus Deliberation & Grey Mode Quarantine")
    verdict = arena.deliberate()

    for entry in verdict.audit_trail:
        print(f"  {entry}")

    print("\n[Deliberation Verdict]")
    print(f"  • Converged:          {verdict.converged}")
    print(f"  • H^1 Obstruction:    {'FREE (H^1 = 0)' if verdict.obstruction_free else 'BLOCKED'}")
    print(f"  • Byzantine Safe:     {verdict.byzantine_safe} (<= 33% quarantined)")
    print(f"  • Healthy Chorus:     {verdict.healthy_agents}")
    print(f"  • Quarantined (Grey): {verdict.quarantined_agents}")
    print(f"  • Final Anchor Drift: {verdict.final_drift:.6f}")
    print(f"  • Consensus Digest:   {verdict.consensus_digest}")

    # -------------------------------------------------------------------------
    # PART 2: TRIAD Recovery of Quarantined Node (Ao -> Phi^up -> Psi)
    # -------------------------------------------------------------------------
    print_header("PART 2: TRIAD Recovery Sequence (Healing the Quarantined Agent)")
    print("Grey Mode isolates without permanently destroying — the recovery path is")
    print("preserved via the Banach-contractive TRIAD kernel (Ao -> Phi^up -> Psi).")

    recovery = arena.recover_agent("rogue-bypass", max_cycles=10, r_c_static=0.25)
    for line in recovery.audit_trail:
        print(f"  {line}")

    print(f"\n  • Recovery Converged: {recovery.converged} in {recovery.cycles_run} cycle(s)")
    print(f"  • Residual Drift Ψ_r: {recovery.psi_r:.6f} (threshold r_c={recovery.r_c_new:.4f})")
    print(f"  • Post-Recovery Mode: {arena.agent_status('rogue-bypass')['status']}")

    # -------------------------------------------------------------------------
    # PART 3: Full 5-Agent Unified Re-Deliberation
    # -------------------------------------------------------------------------
    print_header("PART 3: Unified 5-Agent Chorus Re-Deliberation")
    verdict_healed = arena.deliberate()
    print(f"  • Healthy Agents:     {verdict_healed.healthy_agents}")
    print(f"  • Quarantined Agents: {verdict_healed.quarantined_agents}")
    print(f"  • Converged:          {verdict_healed.converged} ({verdict_healed.rounds_run} round(s))")
    print(f"  • Final Anchor Drift: {verdict_healed.final_drift:.6f}")
    print(f"  • Consensus Digest:   {verdict_healed.consensus_digest}")
    print(f"\n  ✓ All 5 agents converged with H^1(G, F) = 0 and 0 quarantined nodes.\n{LINE}\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
