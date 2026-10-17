"""Synthetic experiment checks, including deliberately broken CASCADE actuation.

These checks validate the measurement harness; they do not validate the glass law.
"""

from dataclasses import asdict
import json
from pathlib import Path
import sys

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "12_IMPLEMENTATIONS" / "core"))

from cascade_engine import CascadeEngine, KnowledgeBlock
from cascade_glass_transition import (
    Arrival, WorkMeterEngine, arrival_trace, calibrate, clone, initial_store,
    run_sweep, simulate,
)


def test_fast_coherence_matches_original_engine_after_real_cascades():
    measured = initial_store(4, "balanced")
    reference = CascadeEngine()
    for block in measured.blocks.values():
        reference.add_block(clone(block))
    for item in arrival_trace(4, "balanced", 3, 1.0, 16):
        measured.add_block(clone(item.block))
        reference.add_block(clone(item.block))
        assert measured.coherence() == pytest.approx(reference.coherence(), abs=1e-14)


def test_calibration_changes_time_with_processing_rate_without_fitting_work():
    slow = calibrate(4, "chain", 32.0)
    fast = calibrate(4, "chain", 64.0)
    assert slow.work_samples == fast.work_samples
    assert len(slow.work_samples) == 4
    assert all(sample > 0 for sample in slow.work_samples)
    assert slow.tau == pytest.approx(2 * fast.tau)


def test_calibration_rejects_a_disabled_actual_cascade(monkeypatch):
    monkeypatch.setattr(WorkMeterEngine, "_execute_cascade", lambda *args: {"cut": True})
    with pytest.raises(RuntimeError, match="not actually resolved"):
        calibrate(4, "chain", 64.0)


def test_compatible_overload_is_backlog_without_semantic_glass():
    calibration = calibrate(4, "star", 64.0)
    trace = arrival_trace(4, "star", 0, 5 / calibration.tau, 48, compatible=True)
    for model in ("cascade", "fifo"):
        row = simulate(trace, calibration, model)
        assert row["final_backlog"] > 0
        assert row["mean_backlog"] > 0
        assert row["final_g"] == row["mean_g"] == 0
        assert row["contradiction_pairs"] == 0


@pytest.mark.parametrize("model", ["cascade", "fifo"])
def test_conflicting_overload_and_separate_drain_recovery(model):
    calibration = calibrate(4, "chain", 64.0)
    trace = arrival_trace(4, "chain", 0, 5 / calibration.tau, 48)
    row = simulate(trace, calibration, model)
    assert row["final_g"] > 0
    assert row["final_backlog"] > 0
    assert row["censored_pair_dwells"] == row["contradiction_pairs"] > 0
    assert row["drain_duration"] > 0
    assert row["drained_backlog"] == 0
    assert row["drained_g"] == 0


def test_harness_exposes_a_cut_actuator_after_calibration(monkeypatch):
    calibration = calibrate(4, "chain", 64.0)
    trace = arrival_trace(4, "chain", 1, 0.25 / calibration.tau, 24)
    healthy = simulate(trace, calibration, "cascade")
    assert healthy["drained_g"] == 0
    monkeypatch.setattr(WorkMeterEngine, "_execute_cascade", lambda *args: {"cut": True})
    broken = simulate(trace, calibration, "cascade")
    assert broken["drained_g"] > 0
    assert broken["mean_g"] > healthy["mean_g"]


def test_cascade_batching_is_observably_different_from_fifo_pairwise():
    calibration = calibrate(2, "chain", 64.0)
    tau = calibration.tau

    def block(identity, concept, paradigm, pressure):
        return KnowledgeBlock(
            identity, identity, f"concept-{concept}", paradigm,
            evidence_strength=1.0, explanatory_power=2.0, uncertainty=2 / pressure,
        )

    trace = (
        Arrival(0.001 * tau, block("first", 0, "b", 3)),
        Arrival(0.002 * tau, block("second", 0, "a", 4)),
        Arrival(1.2 * tau, block("third", 1, "a", 3)),
    )
    cascade = simulate(trace, calibration, "cascade")
    fifo = simulate(trace, calibration, "fifo")
    assert cascade["mean_g"] < fifo["mean_g"]
    assert cascade["drained_g"] == fifo["drained_g"] == 0


@pytest.mark.parametrize("model", ["cascade", "fifo"])
def test_scaling_ingestion_and_processing_together_preserves_outcome(model):
    slow = calibrate(4, "balanced", 64.0)
    fast = calibrate(4, "balanced", 128.0)
    slow_trace = arrival_trace(4, "balanced", 5, 2 / slow.tau, 32)
    fast_trace = arrival_trace(4, "balanced", 5, 2 / fast.tau, 32)
    left = simulate(slow_trace, slow, model)
    right = simulate(fast_trace, fast, model)
    for key in ("mean_g", "final_g", "mean_backlog", "final_backlog",
                "contradiction_pairs", "service_completions_in_window"):
        assert left[key] == pytest.approx(right[key], abs=1e-12)
    assert left["mean_observed_pair_dwell"] == pytest.approx(
        2 * right["mean_observed_pair_dwell"]
    )


def test_both_arms_preserve_the_supplied_trace():
    calibration = calibrate(4, "star", 64.0)
    trace = arrival_trace(4, "star", 0, 3 / calibration.tau, 24)
    before = [asdict(item.block) for item in trace]
    simulate(trace, calibration, "cascade")
    simulate(trace, calibration, "fifo")
    assert [asdict(item.block) for item in trace] == before


def test_sweep_reproducible_and_matched_by_actual_trace_hash():
    kwargs = dict(seeds=(7,), concepts=4, proposals=16, loads=(0.25, 3.0),
                  processing_rates=(64.0,), topologies=("star",))
    left = run_sweep(**kwargs)
    assert left == run_sweep(**kwargs)
    assert len(left["rows"]) == 8
    assert left["summary"]["matched_pairs"] == 4
    for cascade, fifo in zip(left["rows"][::2], left["rows"][1::2]):
        assert cascade["model"] == "cascade"
        assert fifo["model"] == "fifo"
        assert cascade["trace_sha256"] == fifo["trace_sha256"]
    assert json.loads(json.dumps(left, allow_nan=False))["register"] == "SYNTHETIC"


def test_processing_intervention_reuses_offered_arrivals_in_a_full_factorial():
    result = run_sweep(seeds=(1,), concepts=4, proposals=16, loads=(3.0,),
                       processing_rates=(64.0, 128.0), topologies=("chain",))
    rows = [row for row in result["rows"] if row["model"] == "fifo" and not row["compatible"]]
    slow, fast = rows
    assert slow["trace_sha256"] == fast["trace_sha256"]
    assert slow["offered_arrival_rate"] == fast["offered_arrival_rate"]
    assert slow["nominal_load"] == pytest.approx(2 * fast["nominal_load"])
    assert slow["final_backlog"] > fast["final_backlog"]


@pytest.mark.parametrize("rate", [0.0, -1.0, float("nan"), float("inf"), True])
def test_invalid_processing_rate_does_not_produce_evidence(rate):
    with pytest.raises(ValueError):
        calibrate(4, "chain", rate)


def test_empty_sweep_axis_is_not_a_zero_row_success():
    with pytest.raises(ValueError, match="cannot be empty"):
        run_sweep(seeds=())


def test_duplicate_proposals_are_rejected_instead_of_overwriting_evidence():
    calibration = calibrate(4, "chain", 64.0)
    trace = arrival_trace(4, "chain", 0, 1.0, 2)
    invalid = (trace[0], Arrival(trace[1].at, clone(trace[0].block)))
    with pytest.raises(ValueError, match="IDs must be unique"):
        simulate(invalid, calibration, "cascade")
