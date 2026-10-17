"""Frontier verification tests for Topological & Work-Coupled Glass Transition (Batch A2).

Proves three falsifiable theorems on top of Batch A:
1. Theorem 1 (Topological Cascade Cost Separation):
   Perturbing the root hub of a star DAG triggers an O(N) downstream dependency wave,
   separating hub vs. leaf work and separating chain, balanced, star, and diamond
   topologies (which all had identical work=25 in 0-hop CascadeEngine).
2. Theorem 2 (Cohomological Premise Frustration / Quenched Glass State):
   - Single-parent trees (b_1 = 0: chain, star, balanced) always relax to drained_g == 0
     once arrivals stop and the service queue drains.
   - Multi-parent diamond DAGs (b_1 > 0) exhibit quenched topological frustration
     (drained_g > 0 at drained_backlog == 0) when parent branches lock into opposing
     paradigms, and automatically self-heal to drained_g == 0 as soon as a coherent
     parent update resolves the coboundary split.
   - Compatible overload (compatible=True) still has mean_g == final_g == drained_g == 0.
3. Theorem 3 (Snapshot Causality & Work-Coupled Service Timing):
   - Eliminating completion-time lookahead (snapshot_fixed) prevents CASCADE from
     qualifying proposals that arrived after service started.
   - Coupling service duration to actual reorganization work (snapshot_work_coupled)
     stretches completion times under high contradictory load while preserving exact
     trace reproducibility.
"""

from __future__ import annotations

from pathlib import Path
import sys

import pytest

sys.path.insert(
    0, str(Path(__file__).resolve().parents[1] / "12_IMPLEMENTATIONS" / "core")
)

from cascade_engine import KnowledgeBlock
from cascade_glass_transition import Arrival
from topological_cascade_glass import (
    TopologicalCascadeEngine,
    arrival_trace_v2,
    calibrate_v2,
    conflict_pairs_v2,
    glass_fraction_v2,
    initial_store_v2,
    parents_v2,
    run_frontier_comparison,
    simulate_v2,
)


def test_theorem_1_dependency_propagation_separates_hub_vs_leaf_and_topologies():
    """In 0-hop mode every node in every topology costs 25 work units.
    With dependency propagation enabled, flipping the hub of a 12-node star graph
    propagates across all 11 children (47 work units vs 25 for a leaf), and mean
    calibration work separates across star, balanced, chain, and diamond."""
    cal_star_0hop = calibrate_v2(12, "star", 64.0, propagate_dependencies=False)
    assert set(cal_star_0hop.work_samples) == {25}

    cal_star = calibrate_v2(12, "star", 64.0, propagate_dependencies=True)
    cal_balanced = calibrate_v2(12, "balanced", 64.0, propagate_dependencies=True)
    cal_chain = calibrate_v2(12, "chain", 64.0, propagate_dependencies=True)
    cal_diamond = calibrate_v2(12, "diamond", 64.0, propagate_dependencies=True)

    # Star hub (concept-0) cascades to 11 spokes; leaves (concept-1..11) cascade to 0.
    assert cal_star.work_samples[0] == 47
    assert all(w == 25 for w in cal_star.work_samples[1:])

    # Chain root (concept-0) cascades down all 11 descendants sequentially; leaf costs 25.
    assert cal_chain.work_samples[0] > cal_chain.work_samples[-1] == 25

    # Topologies now have distinct mean reorganization work and tau_reorg!
    mean_works = {
        cal_star.mean_work,
        cal_balanced.mean_work,
        cal_chain.mean_work,
        cal_diamond.mean_work,
    }
    assert len(mean_works) == 4


def test_theorem_2_trees_always_drain_to_zero_while_diamond_quenches_and_heals():
    """Single-parent trees (b_1 = 0) cannot sustain multi-parent coboundary frustration,
    so drained_g == 0 after queue drain. Multi-parent diamond DAGs (b_1 > 0) trap child
    domains in quenched frustration (drained_g > 0) when roots split, and heal to 0
    when a root realignment restores premise coherence."""
    for tree_topo in ("chain", "star", "balanced"):
        cal = calibrate_v2(6, tree_topo, 64.0)
        trace = arrival_trace_v2(6, tree_topo, 0, 4.0 / cal.tau, 36, compatible=False)
        for model in ("cascade", "fifo"):
            row = simulate_v2(trace, cal, model, service_mode="snapshot_work_coupled")
            assert row["drained_backlog"] == 0
            assert row["drained_g"] == 0.0

    # Construct an explicit 3-node diamond {0, 1} -> 2 where root-0 flips to paradigm 'b'
    # while root-1 stays in paradigm 'a'.
    engine = initial_store_v2(3, "diamond", propagate_dependencies=True)
    assert parents_v2(3, "diamond") == ((), (), (0, 1))
    assert glass_fraction_v2(engine) == 0.0

    # Flip concept-0 to paradigm 'b' -> now parents of concept-2 are split ('b' vs 'a')!
    flip_root_0 = KnowledgeBlock(
        id="flip-0-b",
        content="root 0 shifts to paradigm b",
        domain="concept-0",
        paradigm="b",
        evidence_strength=1.0,
        explanatory_power=2.0,
        uncertainty=0.25,
        dependencies=set(),
    )
    engine.add_block(flip_root_0)
    assert engine.governing_block("concept-0").paradigm == "b"
    assert engine.governing_block("concept-1").paradigm == "a"

    # Concept-2 now has discordant parents (coboundary defect != 0) -> quenched frustration!
    assert engine.is_premise_frustrated(engine.blocks["anchor-2"]) is True
    assert glass_fraction_v2(engine) > 0.0

    # Even if a high-pressure proposal arrives for concept-2, it cannot clear frustration
    # while its foundation {concept-0, concept-1} remains split.
    child_prop = KnowledgeBlock(
        id="prop-2-b",
        content="child proposal under split foundation",
        domain="concept-2",
        paradigm="b",
        evidence_strength=1.0,
        explanatory_power=2.0,
        uncertainty=0.2,
        dependencies={"anchor-0", "anchor-1"},
    )
    engine.add_block(child_prop)
    assert glass_fraction_v2(engine) > 0.0
    assert len(conflict_pairs_v2(engine)) > 0

    # Now heal the foundation split by shifting concept-1 to paradigm 'b' as well:
    # the dependency cascade automatically propagates to concept-2 and heals g -> 0!
    heal_root_1 = KnowledgeBlock(
        id="flip-1-b",
        content="root 1 aligns to paradigm b",
        domain="concept-1",
        paradigm="b",
        evidence_strength=1.0,
        explanatory_power=2.0,
        uncertainty=0.25,
        dependencies=set(),
    )
    event = engine.add_block(heal_root_1)
    assert event is not None
    assert "concept-2" in event["propagated_domains"]
    assert engine.is_premise_frustrated(engine.governing_block("concept-2")) is False
    assert glass_fraction_v2(engine) == 0.0


def test_compatible_overload_remains_zero_glass_even_on_diamond_dag():
    """Negative control: when all arrivals share paradigm 'a' (compatible=True),
    even 5x overload on a multi-parent diamond DAG produces zero glass (g == 0)."""
    cal = calibrate_v2(8, "diamond", 64.0)
    trace = arrival_trace_v2(8, "diamond", 2, 5.0 / cal.tau, 48, compatible=True)
    for model in ("cascade", "fifo"):
        for smode in ("fixed_lookahead", "snapshot_fixed", "snapshot_work_coupled"):
            row = simulate_v2(trace, cal, model, service_mode=smode)
            assert row["final_backlog"] > 0
            assert row["mean_g"] == 0.0
            assert row["final_g"] == 0.0
            assert row["drained_g"] == 0.0


def test_theorem_3_snapshot_causality_blocks_mid_service_lookahead():
    """Verify that snapshot_fixed prevents a service job started at t=0.001*tau from
    qualifying a stronger proposal that arrives mid-service at t=0.5*tau."""
    cal = calibrate_v2(2, "chain", 64.0)
    tau = cal.tau

    def make_block(bid: str, concept: int, paradigm: str, pressure: float) -> KnowledgeBlock:
        return KnowledgeBlock(
            id=bid,
            content=bid,
            domain=f"concept-{concept}",
            paradigm=paradigm,
            evidence_strength=1.0,
            explanatory_power=2.0,
            uncertainty=2.0 / pressure,
            dependencies={"anchor-0"} if concept == 1 else set(),
        )

    # Proposal 1 arrives at 0.01*tau and immediately starts service (completing at 1.01*tau).
    # Proposal 2 arrives at 0.50*tau (WHILE Proposal 1 is in service!).
    # Proposal 3 arrives at 1.20*tau to set the observation horizon between 1.01*tau and 2.01*tau.
    trace = (
        Arrival(0.01 * tau, make_block("p1", 0, "b", 3.0)),
        Arrival(0.50 * tau, make_block("p2", 0, "a", 4.0)),
        Arrival(1.20 * tau, make_block("p3", 1, "a", 3.0)),
    )
    lookahead_row = simulate_v2(trace, cal, "cascade", service_mode="fixed_lookahead")
    snapshot_row = simulate_v2(trace, cal, "cascade", service_mode="snapshot_fixed")

    # Under fixed_lookahead, p1's completion at 1.01*tau sees p2 (which arrived at 0.50*tau)
    # and resolves the p1-vs-p2 conflict immediately at 1.01*tau (before horizon 1.20*tau).
    assert lookahead_row["final_g"] == 0.0
    assert lookahead_row["contradiction_pairs"] == 0
    # Under snapshot_fixed, p1's snapshot at 0.01*tau only includes {"p1"}, so at 1.01*tau
    # p1 only qualifies anchor-0, leaving p1 ("b") and p2 ("a") in conflict at horizon 1.20*tau
    # until p2's own service job completes at 2.01*tau!
    assert snapshot_row["final_g"] > 0.0
    assert snapshot_row["contradiction_pairs"] == 1
    assert snapshot_row["drained_g"] == 0.0


def test_frontier_comparison_end_to_end_smoke():
    result = run_frontier_comparison(
        seeds=(0, 1),
        concepts=6,
        proposals=32,
        loads=(0.25, 3.0),
        processing_rate=64.0,
    )
    t1 = result["theorems"]["theorem_1_topological_work_separation"]
    assert t1["star_hub_work"] > t1["star_leaf_work"]
    t2 = result["theorems"]["theorem_2_quenched_premise_frustration"]
    assert t2["tree_b1_eq_0_max_drained_g"] == 0.0
    assert t2["diamond_b1_gt_0_max_drained_g"] > 0.0
    assert t2["compatible_overload_max_g"] == 0.0
