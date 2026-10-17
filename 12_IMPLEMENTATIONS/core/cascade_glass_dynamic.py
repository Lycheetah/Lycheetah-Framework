"""Load-aware CASCADE experiment with frozen service snapshots and measured work.

Author: Mackenzie Conor James Clark / Lycheetah Framework.
Implementation: Caelorynth / Codex, 2026-10-17. Register: SYNTHETIC.
The fixed-service v1 module/data remain intact as the explicit comparison control.
"""

from __future__ import annotations

import argparse
from collections import deque
from dataclasses import dataclass
import csv
import hashlib
import itertools
import json
import math
from pathlib import Path
import statistics

from cascade_engine import KnowledgeBlock
from cascade_glass_transition import (
    Arrival, Calibration, LOADS, MODELS, PROCESSING_RATES, TOPOLOGIES,
    WorkMeterEngine, _adjudicate, arrival_trace, calibrate, clone,
    conflict_pairs, glass_fraction, initial_store, summarize,
)


@dataclass(frozen=True)
class ServicePlan:
    """A completed computation whose observable effects commit at its finish time."""

    job: str
    start: float
    finish: float
    work_units: int
    observed_ids: frozenset[str]
    updates: tuple[KnowledgeBlock, ...]


def plan_service(
    live: WorkMeterEngine, job: str, pending: set[str], model: str,
    at: float, processing_rate: float,
) -> ServicePlan:
    if model not in MODELS or job not in pending or job not in live.blocks:
        raise ValueError("service needs a pending job and a known policy")
    if (isinstance(processing_rate, bool) or not math.isfinite(processing_rate)
            or processing_rate <= 0 or not math.isfinite(at) or at < 0):
        raise ValueError("invalid service clock or processing rate")
    snapshot = WorkMeterEngine()
    for name in ("foundation_threshold", "theory_threshold", "trigger_margin", "compression_gamma"):
        setattr(snapshot, name, getattr(live, name))
    snapshot.blocks = {key: clone(block) for key, block in live.blocks.items()}
    work = _adjudicate(snapshot, job, set(pending), model)
    if work <= 0:
        raise RuntimeError("a service cannot receive unmeasured or free work")
    updates = tuple(
        clone(block) for key, block in snapshot.blocks.items()
        if block != live.blocks[key]
    )
    return ServicePlan(job, at, at + work / processing_rate, work,
                       frozenset(live.blocks), updates)


def commit_service(live: WorkMeterEngine, plan: ServicePlan) -> None:
    """Apply only measured snapshot changes; preserve arrivals outside the snapshot."""
    for block in plan.updates:
        if block.id not in plan.observed_ids or block.id not in live.blocks:
            raise RuntimeError("service attempted to update an unobserved/missing block")
    for block in plan.updates:
        live.blocks[block.id] = clone(block)


def simulate_dynamic(trace: tuple[Arrival, ...], calibration: Calibration, model: str) -> dict:
    if model not in MODELS or len(trace) < 2:
        raise ValueError("expected cascade/fifo and at least two arrivals")
    if any(not math.isfinite(item.at) or item.at <= 0 for item in trace):
        raise ValueError("arrival times must be finite and positive")
    if any(right.at <= left.at for left, right in zip(trace, trace[1:])):
        raise ValueError("arrival times must increase")
    if len({item.block.id for item in trace}) != len(trace):
        raise ValueError("proposal IDs must be unique")
    engine = initial_store(calibration.concepts, calibration.topology)
    if any(item.block.id in engine.blocks for item in trace):
        raise ValueError("proposal IDs cannot overwrite initial anchors")
    horizon = trace[-1].at
    warmup = 0.2 * horizon
    queue: deque[str] = deque()
    pending: set[str] = set()
    current: ServicePlan | None = None
    index = 0
    clock = 0.0
    g_area = 0.0
    backlog_area = 0.0
    busy_total = 0.0
    idle_total = 0.0
    charged_window = 0.0
    completed_work_window = 0
    completed_in_window = 0
    work_samples: list[int] = []
    samples: list[dict] = []
    open_pairs: dict[tuple[str, str], float] = {}
    closed_dwells: list[float] = []

    def observe(at: float) -> None:
        now = conflict_pairs(engine)
        for pair in open_pairs.keys() - now:
            closed_dwells.append(at - open_pairs.pop(pair))
        for pair in now - open_pairs.keys():
            open_pairs[pair] = at

    def advance(at: float) -> None:
        nonlocal clock, g_area, backlog_area, busy_total, idle_total, charged_window
        elapsed = at - clock
        if elapsed < -1e-12:
            raise RuntimeError("event clock moved backwards")
        if current is not None:
            busy_total += elapsed
            charged_window += max(0.0, min(at, horizon) - min(clock, horizon)) * calibration.processing_rate
        else:
            idle_total += elapsed
        window = max(0.0, min(at, horizon) - max(clock, warmup))
        g_area += glass_fraction(engine) * window
        backlog_area += len(pending) * window
        clock = at

    def start(at: float) -> None:
        nonlocal current
        while queue and queue[0] not in pending:
            queue.popleft()
        current = (plan_service(engine, queue.popleft(), pending, model, at,
                                calibration.processing_rate) if queue else None)

    def complete(at: float) -> None:
        nonlocal current, completed_work_window, completed_in_window
        if current is None or at != current.finish:
            raise RuntimeError("completion does not match a measured service plan")
        plan = current
        commit_service(engine, plan)
        work_samples.append(plan.work_units)
        if at <= horizon:
            completed_work_window += plan.work_units
            completed_in_window += 1
        if len(samples) < 3:
            samples.append({"job":plan.job, "start":plan.start, "finish":plan.finish,
                            "work_units":plan.work_units, "snapshot_blocks":len(plan.observed_ids),
                            "changed_blocks":len(plan.updates)})
        pending.discard(plan.job)
        if model == "cascade":
            pending.difference_update(key for key in tuple(pending)
                                      if engine.blocks[key].regime == "qualified")
        current = None
        observe(at)
        start(at)

    while index < len(trace) or (current is not None and current.finish <= horizon):
        arrival_at = trace[index].at if index < len(trace) else math.inf
        completion_at = current.finish if current is not None else math.inf
        at = min(arrival_at, completion_at)
        if at > horizon:
            break
        advance(at)
        if completion_at <= arrival_at:
            complete(at)
        else:
            block = clone(trace[index].block)
            engine.blocks[block.id] = block
            engine._assign_layer(block)
            pending.add(block.id)
            queue.append(block.id)
            index += 1
            observe(at)
            if current is None:
                start(at)

    final_g = glass_fraction(engine)
    final_pairs = len(conflict_pairs(engine))
    censored = len(open_pairs)
    final_backlog = len(pending)
    held_pairs = len(engine.blocks) * (len(engine.blocks) - 1) / 2
    observed_dwells = closed_dwells + [horizon - value for value in open_pairs.values()]
    in_flight_work = ((horizon - current.start) * calibration.processing_rate
                      if current is not None else 0.0)
    budget_error = charged_window - completed_work_window - in_flight_work
    capacity = calibration.processing_rate * horizon
    if abs(budget_error) > 1e-7 or charged_window > capacity + 1e-7:
        raise RuntimeError("work-budget conservation failed")
    while current is not None:
        at = current.finish
        advance(at)
        complete(at)
    total_work = sum(work_samples)
    total_error = total_work - busy_total * calibration.processing_rate
    if abs(total_error) > 1e-6 or abs(clock - busy_total - idle_total) > 1e-7:
        raise RuntimeError("busy/idle timeline does not account for measured work")
    duration = horizon - warmup
    mean_work = statistics.mean(work_samples) if work_samples else 0.0
    return {
        "model":model, "topology":calibration.topology, "timing":"measured_snapshot",
        "processing_rate":calibration.processing_rate, "tau_reorg":calibration.tau,
        "calibration_mean_work":calibration.mean_work,
        "calibration_samples":len(calibration.work_samples), "arrivals":len(trace),
        "horizon":horizon, "admitted_rate_realized":len(trace)/horizon,
        "mean_g":g_area/duration, "final_g":final_g,
        "contradiction_pairs":final_pairs,
        "contradiction_pair_fraction":final_pairs/held_pairs if held_pairs else 0.0,
        "mean_backlog":backlog_area/duration, "final_backlog":final_backlog,
        "service_completions_in_window":completed_in_window,
        "service_throughput":completed_in_window/horizon,
        "mean_observed_pair_dwell":statistics.mean(observed_dwells) if observed_dwells else 0.0,
        "censored_pair_dwells":censored, "loaded_mean_work":mean_work,
        "loaded_to_calibrated_work":mean_work/calibration.mean_work,
        "drain_duration":max(0.0, clock-horizon), "drained_g":glass_fraction(engine),
        "drained_backlog":len(pending), "service_completions_total":len(work_samples),
        "work_units_in_window":charged_window, "available_work_in_window":capacity,
        "completed_work_units_in_window":completed_work_window,
        "in_flight_work_units_at_horizon":in_flight_work,
        "work_units_total":total_work, "busy_duration_total":busy_total,
        "idle_duration_total":idle_total, "window_budget_error":budget_error,
        "total_budget_error":total_error, "sample_services":samples,
    }


def run_dynamic_sweep(
    *, seeds: tuple[int, ...] = (0, 1, 2, 3), concepts: int = 12,
    proposals: int = 96, loads: tuple[float, ...] = LOADS,
    processing_rates: tuple[float, ...] = PROCESSING_RATES,
    topologies: tuple[str, ...] = TOPOLOGIES,
) -> dict:
    if not seeds or not loads or not processing_rates or not topologies:
        raise ValueError("sweep axes cannot be empty")
    if any(isinstance(v, bool) or not math.isfinite(v) or v <= 0 for v in loads):
        raise ValueError("loads must be finite and positive")
    rows = []
    calibrations = []
    for topology, processing_rate in itertools.product(topologies, processing_rates):
        calibration = calibrate(concepts, topology, processing_rate)
        calibrations.append({"topology":topology, "processing_rate":processing_rate,
                             "work_samples":calibration.work_samples, "tau_reorg":calibration.tau})
        reference_tau = calibration.mean_work / PROCESSING_RATES[0]
        for seed, reference_load, compatible in itertools.product(seeds, loads, (False, True)):
            rate = reference_load / reference_tau
            trace = arrival_trace(concepts, topology, seed, rate, proposals, compatible)
            payload = json.dumps([(item.at, item.block.id, item.block.domain,
                                   item.block.paradigm, item.block.truth_pressure)
                                  for item in trace], separators=(",", ":")).encode()
            trace_hash = hashlib.sha256(payload).hexdigest()
            for model in MODELS:
                row = simulate_dynamic(trace, calibration, model)
                row.update(seed=seed, reference_load=reference_load,
                           nominal_load=rate*calibration.tau, offered_arrival_rate=rate,
                           compatible=compatible, trace_sha256=trace_hash)
                rows.append(row)
    summary = summarize(rows)
    summary["interpretation"] = (
        "Finite synthetic measured-work snapshot/commit model. No future arrivals "
        "can change a service already in flight; both policies pay their actual "
        "metered semantic work. This is not CPU timing, natural-domain evidence, "
        "an inferred phase transition, or a validated production governor."
    )
    summary["max_absolute_window_budget_error"] = max(abs(r["window_budget_error"]) for r in rows)
    summary["max_absolute_total_budget_error"] = max(abs(r["total_budget_error"]) for r in rows)
    return {
        "schema":"lycheetah.cascade-glass-dynamic.v2", "register":"SYNTHETIC",
        "author":"Mackenzie Conor James Clark / Lycheetah Framework",
        "protocol":"TRUTH_PRESSURE/EXPERIMENTS/GLASS_TRANSITION/LOAD_AWARE_PROTOCOL.md",
        "config":{"seeds":seeds, "concepts":concepts, "proposals":proposals,
                  "reference_loads":loads, "reference_processing_rate":PROCESSING_RATES[0],
                  "processing_rates":processing_rates, "topologies":topologies},
        "calibrations":calibrations, "summary":summary, "rows":rows,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--csv", type=Path)
    parser.add_argument("--quick", action="store_true")
    args = parser.parse_args(argv)
    result = (run_dynamic_sweep(seeds=(0,), proposals=32, loads=(0.25, 1.0, 3.0),
                               processing_rates=(64.0,), topologies=("chain",))
              if args.quick else run_dynamic_sweep())
    root = Path(__file__).resolve().parents[2]
    result["source_sha256"] = {
        path.relative_to(root).as_posix():hashlib.sha256(path.read_bytes()).hexdigest()
        for path in (Path(__file__).resolve(), Path(__file__).with_name("cascade_glass_transition.py").resolve(),
                     Path(__file__).with_name("cascade_engine.py").resolve(), root/result["protocol"])
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, allow_nan=False)+"\n", encoding="utf-8")
    if args.csv:
        args.csv.parent.mkdir(parents=True, exist_ok=True)
        with args.csv.open("w", encoding="utf-8", newline="") as stream:
            writer = csv.DictWriter(stream, fieldnames=list(result["rows"][0]))
            writer.writeheader()
            for row in result["rows"]:
                serialized = dict(row)
                serialized["sample_services"] = json.dumps(row["sample_services"], separators=(",", ":"))
                writer.writerow(serialized)
    print(json.dumps(result["summary"], indent=2, allow_nan=False))
    print(f"Saved {len(result['rows'])} measured-work rows to {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
