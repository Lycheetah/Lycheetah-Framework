"""Snapshot causality and work accounting, including deliberately false receipts."""

from dataclasses import asdict, replace
from pathlib import Path
import sys

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "12_IMPLEMENTATIONS" / "core"))

import cascade_glass_dynamic as dynamic
from cascade_engine import KnowledgeBlock
from cascade_glass_transition import Arrival, arrival_trace, calibrate, clone, initial_store


def proposal(identity="first", paradigm="b", pressure=3.0):
    return KnowledgeBlock(identity, identity, "concept-0", paradigm,
                          evidence_strength=1.0, explanatory_power=2.0,
                          uncertainty=2.0/pressure)


def admit(engine, block):
    engine.blocks[block.id] = clone(block)
    engine._assign_layer(engine.blocks[block.id])


def test_planning_does_not_apply_the_actuator_early_or_alias_live_state():
    engine = initial_store(4, "chain")
    admit(engine, proposal())
    before = {key:asdict(block) for key, block in engine.blocks.items()}
    plan = dynamic.plan_service(engine, "first", {"first"}, "cascade", 0.0, 64.0)
    assert {key:asdict(block) for key, block in engine.blocks.items()} == before
    assert plan.updates
    assert plan.finish > plan.start
    assert plan.observed_ids == set(before)
    assert plan.work_units > 0
    dynamic.commit_service(engine, plan)
    assert engine.blocks["anchor-0"].regime == "qualified"


def test_future_arrival_cannot_influence_or_be_deleted_by_older_commit():
    engine = initial_store(4, "chain")
    admit(engine, proposal())
    plan = dynamic.plan_service(engine, "first", {"first"}, "cascade", 0.0, 64.0)
    future = proposal("future", "a", 5.0)
    admit(engine, future)
    before = asdict(engine.blocks["future"])
    assert "future" not in plan.observed_ids
    dynamic.commit_service(engine, plan)
    assert asdict(engine.blocks["future"]) == before
    assert engine.blocks["anchor-0"].regime == "qualified"
    assert engine.blocks["first"].regime == "universal"
    assert engine.blocks["future"].regime == "universal"
    # If the first service had seen the future a/5 proposal, it would instead
    # have qualified the earlier b/3 proposal. The actual snapshot does not.


def test_commit_rejects_updates_outside_observed_snapshot():
    engine = initial_store(4, "chain")
    admit(engine, proposal())
    plan = dynamic.plan_service(engine, "first", {"first"}, "cascade", 0.0, 64.0)
    admit(engine, proposal("future"))
    forged = replace(plan, updates=plan.updates + (proposal("future"),))
    with pytest.raises(RuntimeError, match="unobserved"):
        dynamic.commit_service(engine, forged)


@pytest.mark.parametrize("model", ["cascade", "fifo"])
@pytest.mark.parametrize("load", [0.25, 1.0, 3.0])
def test_measured_work_fits_elapsed_capacity_and_accounts_for_in_flight_job(model, load):
    calibration = calibrate(4, "chain", 64.0)
    trace = arrival_trace(4, "chain", 0, load/calibration.tau, 32)
    row = dynamic.simulate_dynamic(trace, calibration, model)
    assert row["work_units_in_window"] <= row["available_work_in_window"] + 1e-8
    assert row["work_units_in_window"] == pytest.approx(
        row["completed_work_units_in_window"] + row["in_flight_work_units_at_horizon"]
    )
    assert row["work_units_total"] == pytest.approx(row["busy_duration_total"] * 64.0)
    assert abs(row["window_budget_error"]) < 1e-7
    assert abs(row["total_budget_error"]) < 1e-6
    assert row["drained_g"] == row["drained_backlog"] == 0


def test_harness_rejects_a_false_work_receipt(monkeypatch):
    calibration = calibrate(4, "chain", 64.0)
    trace = arrival_trace(4, "chain", 0, 0.25/calibration.tau, 24)
    original = dynamic.plan_service

    def lie_about_work(*args, **kwargs):
        plan = original(*args, **kwargs)
        return replace(plan, work_units=plan.work_units + 1)

    monkeypatch.setattr(dynamic, "plan_service", lie_about_work)
    with pytest.raises(RuntimeError, match="conservation|account"):
        dynamic.simulate_dynamic(trace, calibration, "fifo")


def test_cut_commit_is_visible_as_undrained_semantic_conflict(monkeypatch):
    calibration = calibrate(4, "chain", 64.0)
    trace = arrival_trace(4, "chain", 2, 0.25/calibration.tau, 24)
    healthy = dynamic.simulate_dynamic(trace, calibration, "cascade")
    assert healthy["drained_g"] == 0
    monkeypatch.setattr(dynamic, "commit_service", lambda *args: None)
    broken = dynamic.simulate_dynamic(trace, calibration, "cascade")
    assert broken["drained_g"] > 0


@pytest.mark.parametrize("model", ["cascade", "fifo"])
def test_compatible_overload_remains_semantically_clear(model):
    calibration = calibrate(4, "star", 64.0)
    trace = arrival_trace(4, "star", 3, 5/calibration.tau, 32, compatible=True)
    row = dynamic.simulate_dynamic(trace, calibration, model)
    assert row["final_backlog"] > 0
    assert row["mean_g"] == row["final_g"] == row["drained_g"] == 0


def test_processing_rate_intervention_reuses_inputs_and_preserves_reproducibility():
    options = dict(seeds=(0,), concepts=4, proposals=16, loads=(3.0,),
                   processing_rates=(64.0, 128.0), topologies=("chain",))
    report = dynamic.run_dynamic_sweep(**options)
    assert report == dynamic.run_dynamic_sweep(**options)
    fifo = [r for r in report["rows"] if r["model"] == "fifo" and not r["compatible"]]
    slow, fast = fifo
    assert slow["trace_sha256"] == fast["trace_sha256"]
    assert slow["offered_arrival_rate"] == fast["offered_arrival_rate"]
    assert slow["final_backlog"] > fast["final_backlog"]


def test_dynamic_simulation_preserves_caller_owned_blocks():
    calibration = calibrate(4, "balanced", 64.0)
    trace = arrival_trace(4, "balanced", 1, 3/calibration.tau, 24)
    before = [asdict(item.block) for item in trace]
    for model in ("cascade", "fifo"):
        dynamic.simulate_dynamic(trace, calibration, model)
    assert [asdict(item.block) for item in trace] == before


def test_anchor_identity_collision_cannot_destroy_the_initial_store():
    calibration = calibrate(4, "chain", 64.0)
    trace = (Arrival(0.1, proposal("anchor-0")), Arrival(0.2, proposal("next")))
    with pytest.raises(ValueError, match="overwrite initial anchors"):
        dynamic.simulate_dynamic(trace, calibration, "fifo")
