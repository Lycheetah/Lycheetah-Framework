"""Finite model checks for dependency propagation and service timing.

These fixtures exercise the declared parent-label policy. They establish neither
a general glass law nor a cohomology theorem. Work counts depend on the core
engine revision; the isolated zero-hop calibration supplies the independent base.
"""

from __future__ import annotations

from pathlib import Path
import sys

import pytest

sys.path.insert(
    0, str(Path(__file__).resolve().parents[1] / "12_IMPLEMENTATIONS" / "core")
)

from cascade_engine import KnowledgeBlock
from cascade_glass_transition import Arrival, calibrate
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


def test_dependency_propagation_separates_hub_vs_leaf_and_topologies():
    """The star hub adds two metered operations per child to the zero-hop base."""
    baseline = calibrate(12, "star", 64.0).mean_work
    cal_star_0hop = calibrate_v2(12, "star", 64.0, propagate_dependencies=False)
    assert set(cal_star_0hop.work_samples) == {baseline}

    cal_star = calibrate_v2(12, "star", 64.0, propagate_dependencies=True)
    cal_balanced = calibrate_v2(12, "balanced", 64.0, propagate_dependencies=True)
    cal_chain = calibrate_v2(12, "chain", 64.0, propagate_dependencies=True)
    cal_diamond = calibrate_v2(12, "diamond", 64.0, propagate_dependencies=True)

    # Star hub (concept-0) cascades to 11 spokes; leaves (concept-1..11) cascade to 0.
    assert cal_star.work_samples[0] == baseline + 2 * 11
    assert all(w == baseline for w in cal_star.work_samples[1:])

    # A chain root traverses descendants; a leaf pays the zero-hop base.
    assert cal_chain.work_samples[0] > cal_chain.work_samples[-1] == baseline

    # Topologies now have distinct mean reorganization work and tau_reorg!
    mean_works = {
        cal_star.mean_work,
        cal_balanced.mean_work,
        cal_chain.mean_work,
        cal_diamond.mean_work,
    }
    assert len(mean_works) == 4


def test_selected_trees_drain_and_multi_parent_policy_retains_then_resolves_conflict():
    """Exercise the explicit parent-disagreement policy on selected fixtures."""
    for tree_topo in ("chain", "star", "balanced"):
        cal = calibrate_v2(6, tree_topo, 64.0)
        trace = arrival_trace_v2(6, tree_topo, 0, 4.0 / cal.tau, 36, compatible=False)
        for model in ("cascade", "fifo"):
            row = simulate_v2(trace, cal, model, service_mode="snapshot_work_coupled")
            assert row["drained_backlog"] == 0
            assert row["drained_g"] == 0.0

    # A three-node two-parent DAG is an undirected tree. It still triggers the
    # programmed policy when parent labels disagree; no graph cycle is required.
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

    # The child now has discordant parent labels under the declared policy.
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


def test_snapshot_causality_blocks_mid_service_lookahead():
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
