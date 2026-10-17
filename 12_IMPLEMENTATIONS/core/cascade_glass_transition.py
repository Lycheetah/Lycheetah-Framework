"""Finite CASCADE/queue experiment; synthetic evidence, not a universal glass law.

Author: Mackenzie Conor James Clark / Lycheetah Framework.
Design and implementation: Caelorynth / Codex, 2026-10-17.

Run from the repository root::

    python3 12_IMPLEMENTATIONS/core/cascade_glass_transition.py --output /tmp/glass.json

The fixed protocol lives in TRUTH_PRESSURE/EXPERIMENTS/GLASS_TRANSITION/PROTOCOL.md.
Service time is independently calibrated semantic work, not measured CPU seconds.
Neither simulator arm reads the dimensionless load or branches at its value of one.
"""

from __future__ import annotations

import argparse
from collections import Counter, defaultdict, deque
from dataclasses import dataclass, replace
import csv
import hashlib
import itertools
import json
import math
from pathlib import Path
import random
import statistics

from cascade_engine import CascadeEngine, KnowledgeBlock


TOPOLOGIES = ("chain", "star", "balanced")
LOADS = (0.1, 0.25, 0.5, 0.75, 1.0, 1.25, 2.0, 3.0, 5.0)
PROCESSING_RATES = (64.0, 128.0)
MODELS = ("cascade", "fifo")


def _positive(value: float, name: str) -> float:
    if isinstance(value, bool) or not math.isfinite(value) or value <= 0:
        raise ValueError(f"{name} must be finite and positive")
    return float(value)


def _count(value: int, name: str, minimum: int = 1) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < minimum:
        raise ValueError(f"{name} must be an integer >= {minimum}")
    return value


def clone(block: KnowledgeBlock) -> KnowledgeBlock:
    return replace(block, dependencies=set(block.dependencies))


class WorkMeterEngine(CascadeEngine):
    """Real CASCADE operations, with counters and an equivalent O(n) coherence.

    The counter charges contradiction comparisons and layer assignments only.
    It is an explicit synthetic work metric, not a CPU or instruction counter.
    """

    def __init__(self) -> None:
        self.work = 0
        super().__init__()

    def contradicts(self, left: KnowledgeBlock, right: KnowledgeBlock) -> bool:
        self.work += 1
        return super().contradicts(left, right)

    def _assign_layer(self, block: KnowledgeBlock) -> None:
        self.work += 1
        super()._assign_layer(block)

    def coherence(self) -> float:
        size = len(self.blocks)
        if size < 2:
            return 1.0
        groups: dict[str, Counter] = defaultdict(Counter)
        for block in self.blocks.values():
            if block.regime == "universal":
                groups[block.domain][block.paradigm] += 1
        pairs = sum(
            (sum(counts.values()) ** 2 - sum(n * n for n in counts.values())) // 2
            for counts in groups.values()
        )
        return 1.0 - pairs / (size * (size - 1) / 2)


def parents(size: int, topology: str) -> tuple[tuple[int, ...], ...]:
    _count(size, "concepts", 2)
    if topology not in TOPOLOGIES:
        raise ValueError(f"unknown topology: {topology}")
    return tuple(
        () if index == 0 else (
            (index - 1,) if topology == "chain" else
            (0,) if topology == "star" else ((index - 1) // 2,)
        )
        for index in range(size)
    )


def initial_store(size: int, topology: str) -> WorkMeterEngine:
    graph = parents(size, topology)
    engine = WorkMeterEngine()
    for index in range(size):
        engine.add_block(KnowledgeBlock(
            id=f"anchor-{index}", content=f"initial concept {index}",
            domain=f"concept-{index}", paradigm="a",
            evidence_strength=1.0, explanatory_power=2.0, uncertainty=1.0,
            dependencies={f"anchor-{parent}" for parent in graph[index]},
        ))
    engine.work = 0
    return engine


@dataclass(frozen=True)
class Calibration:
    topology: str
    concepts: int
    processing_rate: float
    work_samples: tuple[int, ...]

    def __post_init__(self) -> None:
        parents(self.concepts, self.topology)
        _positive(self.processing_rate, "processing_rate")
        if not self.work_samples:
            raise ValueError("calibration needs actual work samples")
        for sample in self.work_samples:
            _count(sample, "work sample")

    @property
    def mean_work(self) -> float:
        return statistics.mean(self.work_samples)

    @property
    def tau(self) -> float:
        return self.mean_work / self.processing_rate


def calibrate(size: int, topology: str, processing_rate: float) -> Calibration:
    """Measure isolated repairs before generating the arrival-rate intervention."""
    _positive(processing_rate, "processing_rate")
    samples = []
    for concept in range(size):
        engine = initial_store(size, topology)
        proposal = KnowledgeBlock(
            id=f"probe-{concept}", content="independent calibration perturbation",
            domain=f"concept-{concept}", paradigm="b",
            evidence_strength=1.0, explanatory_power=2.0, uncertainty=0.5,
        )
        # Admission is outside the measured reorganisation operation.
        engine.blocks[proposal.id] = proposal
        engine._assign_layer(proposal)
        engine.work = 0
        event = engine.add_block(proposal)
        measured_work = engine.work
        if event is None or engine.active_contradictions():
            raise RuntimeError("calibration perturbation was not actually resolved")
        samples.append(measured_work)
    return Calibration(topology, size, processing_rate, tuple(samples))


@dataclass(frozen=True)
class Arrival:
    at: float
    block: KnowledgeBlock


def arrival_trace(
    size: int, topology: str, seed: int, arrival_rate: float,
    proposals: int, compatible: bool = False,
) -> tuple[Arrival, ...]:
    _positive(arrival_rate, "arrival_rate")
    _count(proposals, "proposals", 2)
    graph = parents(size, topology)
    neighbours = [list(items) for items in graph]
    for child, items in enumerate(graph):
        for parent in items:
            neighbours[parent].append(child)
    rng = random.Random(seed)
    generations: Counter = Counter()
    concept = rng.randrange(size)
    clock = 0.0
    trace = []
    for index in range(proposals):
        clock += rng.expovariate(arrival_rate)
        concept = (rng.choice(neighbours[concept]) if rng.random() < 0.65
                   else rng.randrange(size))
        generations[concept] += 1
        generation = generations[concept]
        # Explicit pressure ordering supplies adjudicable evidence, not an oracle
        # about the truth of any natural-language proposition.
        pressure = 2.0 + generation
        block = KnowledgeBlock(
            id=f"proposal-{index}", content=f"version {generation} of concept {concept}",
            domain=f"concept-{concept}",
            paradigm="a" if compatible or generation % 2 == 0 else "b",
            evidence_strength=1.0, explanatory_power=2.0,
            uncertainty=2.0 / pressure,
            dependencies={f"anchor-{parent}" for parent in graph[concept]},
        )
        trace.append(Arrival(clock, block))
    return tuple(trace)


def conflict_pairs(engine: CascadeEngine) -> set[tuple[str, str]]:
    groups: dict[str, list[KnowledgeBlock]] = defaultdict(list)
    for block in engine.blocks.values():
        if block.regime == "universal":
            groups[block.domain].append(block)
    return {
        tuple(sorted((left.id, right.id)))
        for group in groups.values()
        for left, right in itertools.combinations(group, 2)
        if left.paradigm != right.paradigm
    }


def glass_fraction(engine: CascadeEngine) -> float:
    participants = {item for pair in conflict_pairs(engine) for item in pair}
    universal = sum(b.regime == "universal" for b in engine.blocks.values())
    return len(participants) / universal if universal else 0.0


def _adjudicate(engine: WorkMeterEngine, job: str, pending: set[str], model: str) -> int:
    """CASCADE sees all admitted proposals; FIFO sees committed state plus its job."""
    hidden = {}
    if model == "fifo":
        for key in pending - {job}:
            hidden[key] = engine.blocks.pop(key)
    try:
        domain = engine.blocks[job].domain
        candidates = [b for b in engine.blocks.values()
                      if b.domain == domain and b.regime == "universal"]
        winner = max(candidates, key=lambda block: (block.truth_pressure, block.id))
        engine.work = 0
        engine.add_block(winner)
        return engine.work
    finally:
        engine.blocks.update(hidden)


def simulate(trace: tuple[Arrival, ...], calibration: Calibration, model: str) -> dict:
    """Discrete events and actual contradictions produce g; load is not an input."""
    if model not in MODELS or len(trace) < 2:
        raise ValueError("expected cascade/fifo and at least two arrivals")
    if any(not math.isfinite(item.at) or item.at <= 0 for item in trace):
        raise ValueError("arrival times must be finite and positive")
    if any(right.at <= left.at for left, right in zip(trace, trace[1:])):
        raise ValueError("arrival times must be strictly increasing")
    if len({item.block.id for item in trace}) != len(trace):
        raise ValueError("proposal IDs must be unique")
    engine = initial_store(calibration.concepts, calibration.topology)
    horizon = trace[-1].at
    warmup = 0.2 * horizon
    queue: deque[str] = deque()
    pending: set[str] = set()
    current: str | None = None
    completion = math.inf
    index = 0
    clock = 0.0
    g_area = 0.0
    backlog_area = 0.0
    work_samples: list[int] = []
    service_count = 0
    service_before_horizon = 0
    open_pairs: dict[tuple[str, str], float] = {}
    closed_dwells: list[float] = []

    def observe_pairs(at: float) -> None:
        now = conflict_pairs(engine)
        for pair in open_pairs.keys() - now:
            closed_dwells.append(at - open_pairs.pop(pair))
        for pair in now - open_pairs.keys():
            open_pairs[pair] = at

    def start(at: float) -> None:
        nonlocal current, completion
        while queue and queue[0] not in pending:
            queue.popleft()
        if queue:
            current = queue.popleft()
            completion = at + calibration.tau
        else:
            current, completion = None, math.inf

    def complete(at: float) -> None:
        nonlocal current, service_count, service_before_horizon
        if current is None:
            raise RuntimeError("completion without a service job")
        work_samples.append(_adjudicate(engine, current, pending, model))
        service_count += 1
        service_before_horizon += int(at <= horizon)
        pending.discard(current)
        # CASCADE can qualify queued proposals during the actual batch operation.
        if model == "cascade":
            pending.difference_update(
                key for key in tuple(pending) if engine.blocks[key].regime == "qualified"
            )
        current = None
        observe_pairs(at)
        start(at)

    while index < len(trace) or completion <= horizon:
        arrival_at = trace[index].at if index < len(trace) else math.inf
        at = min(arrival_at, completion)
        if at > horizon:
            break
        duration = max(0.0, min(at, horizon) - max(clock, warmup))
        g_area += glass_fraction(engine) * duration
        backlog_area += len(pending) * duration
        clock = at
        if completion <= arrival_at:
            complete(at)
        else:
            block = clone(trace[index].block)
            engine.blocks[block.id] = block
            engine._assign_layer(block)
            queue.append(block.id)
            pending.add(block.id)
            index += 1
            observe_pairs(at)
            if current is None:
                start(at)

    final_g = glass_fraction(engine)
    final_pairs = len(conflict_pairs(engine))
    final_backlog = len(pending)
    held_pairs = len(engine.blocks) * (len(engine.blocks) - 1) / 2
    observed_ages = closed_dwells + [horizon - start_at for start_at in open_pairs.values()]
    censored_at_horizon = len(open_pairs)
    primary_duration = horizon - warmup
    # Recovery is measured separately; it never contaminates the load-window g.
    while current is not None:
        clock = completion
        complete(clock)
    mean_work = statistics.mean(work_samples) if work_samples else 0.0
    return {
        "model": model, "topology": calibration.topology,
        "processing_rate": calibration.processing_rate,
        "tau_reorg": calibration.tau, "calibration_mean_work": calibration.mean_work,
        "calibration_samples": len(calibration.work_samples),
        "arrivals": len(trace), "horizon": horizon,
        "admitted_rate_realized": len(trace) / horizon,
        "mean_g": g_area / primary_duration, "final_g": final_g,
        "contradiction_pairs": final_pairs,
        "contradiction_pair_fraction": final_pairs / held_pairs if held_pairs else 0.0,
        "mean_backlog": backlog_area / primary_duration, "final_backlog": final_backlog,
        "service_completions_in_window": service_before_horizon,
        "service_throughput": service_before_horizon / horizon,
        "mean_observed_pair_dwell": statistics.mean(observed_ages) if observed_ages else 0.0,
        "censored_pair_dwells": censored_at_horizon,
        "loaded_mean_work": mean_work,
        "loaded_to_calibrated_work": mean_work / calibration.mean_work,
        "drain_duration": max(0.0, clock - horizon),
        "drained_g": glass_fraction(engine), "drained_backlog": len(pending),
        "service_completions_total": service_count,
    }


def summarize(rows: list[dict]) -> dict:
    effects = {}
    for model in MODELS:
        selected = [r for r in rows if r["model"] == model and not r["compatible"]]
        low = [r["mean_g"] for r in selected if r["nominal_load"] <= 0.5]
        high = [r["mean_g"] for r in selected if r["nominal_load"] >= 2]
        if low and high:
            delta = statistics.mean(high) - statistics.mean(low)
            effects[model] = {
                "low_load_mean_g": statistics.mean(low),
                "high_load_mean_g": statistics.mean(high),
                "high_minus_low": delta, "directional_screen_above_0_05": delta > 0.05,
            }
    grouped: dict[tuple, dict] = defaultdict(dict)
    for row in rows:
        key = (row["topology"], row["seed"], row["processing_rate"],
               row["nominal_load"], row["compatible"])
        grouped[key][row["model"]] = row
    differences = [pair["cascade"]["mean_g"] - pair["fifo"]["mean_g"]
                   for pair in grouped.values() if set(pair) == set(MODELS)]
    controls = [row for row in rows if row["compatible"] and row["nominal_load"] >= 2]
    return {
        "rows": len(rows), "load_effects": effects,
        "matched_pairs": len(differences),
        "mean_cascade_minus_fifo_g": statistics.mean(differences) if differences else None,
        "compatible_overload_max_g": max((r["final_g"] for r in controls), default=None),
        "compatible_overload_max_backlog": max((r["final_backlog"] for r in controls), default=None),
        "max_drained_g": max((r["drained_g"] for r in rows), default=None),
        "interpretation": (
            "Synthetic load response and a matched queue comparison only. A directional "
            "effect cannot establish a distinct glass law, a sharp phase transition, "
            "irreversible freezing, or substrate independence. Fixed service budgets "
            "must be read alongside loaded work, which can exceed calibration."
        ),
    }


def run_sweep(
    *, seeds: tuple[int, ...] = (0, 1, 2, 3), concepts: int = 12,
    proposals: int = 96, loads: tuple[float, ...] = LOADS,
    processing_rates: tuple[float, ...] = PROCESSING_RATES,
    topologies: tuple[str, ...] = TOPOLOGIES,
) -> dict:
    if not seeds or not loads or not processing_rates or not topologies:
        raise ValueError("sweep axes cannot be empty")
    for load in loads:
        _positive(load, "load")
    rows = []
    calibrations = []
    for topology, processing_rate in itertools.product(topologies, processing_rates):
        calibration = calibrate(concepts, topology, processing_rate)
        calibrations.append({
            "topology": topology, "concepts": concepts,
            "processing_rate": processing_rate, "work_samples": calibration.work_samples,
            "tau_reorg": calibration.tau,
        })
        # Fix the offered-rate grid using one reference capacity, then cross it
        # with every processing rate. Ingestion and processing are interventions
        # in their own right, rather than always being rescaled together.
        reference_tau = calibration.mean_work / PROCESSING_RATES[0]
        for seed, reference_load, compatible in itertools.product(seeds, loads, (False, True)):
            rate = reference_load / reference_tau
            trace = arrival_trace(concepts, topology, seed, rate, proposals, compatible)
            trace_bytes = json.dumps([
                (item.at, item.block.id, item.block.domain, item.block.paradigm,
                 item.block.truth_pressure) for item in trace
            ], separators=(",", ":")).encode()
            trace_hash = hashlib.sha256(trace_bytes).hexdigest()
            for model in MODELS:
                row = simulate(trace, calibration, model)
                row.update(seed=seed, nominal_load=rate * calibration.tau,
                           reference_load=reference_load, offered_arrival_rate=rate,
                           compatible=compatible, trace_sha256=trace_hash)
                rows.append(row)
    return {
        "schema": "lycheetah.cascade-glass-experiment.v1", "register": "SYNTHETIC",
        "author": "Mackenzie Conor James Clark / Lycheetah Framework",
        "protocol": "TRUTH_PRESSURE/EXPERIMENTS/GLASS_TRANSITION/PROTOCOL.md",
        "config": {"seeds": seeds, "concepts": concepts, "proposals": proposals,
                   "reference_loads": loads, "reference_processing_rate": PROCESSING_RATES[0],
                   "processing_rates": processing_rates, "topologies": topologies},
        "calibrations": calibrations, "summary": summarize(rows), "rows": rows,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--csv", type=Path)
    parser.add_argument("--quick", action="store_true", help="small focused smoke experiment")
    args = parser.parse_args(argv)
    result = (run_sweep(seeds=(0,), proposals=32, loads=(0.25, 1.0, 3.0),
                        processing_rates=(64.0,), topologies=("chain",))
              if args.quick else run_sweep())
    root = Path(__file__).resolve().parents[2]
    result["source_sha256"] = {
        path.relative_to(root).as_posix(): hashlib.sha256(path.read_bytes()).hexdigest()
        for path in (
            Path(__file__).resolve(), Path(__file__).with_name("cascade_engine.py").resolve(),
            root / result["protocol"],
        )
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    payload = json.dumps(result, indent=2, allow_nan=False) + "\n"
    args.output.write_text(payload, encoding="utf-8")
    if args.csv:
        args.csv.parent.mkdir(parents=True, exist_ok=True)
        with args.csv.open("w", encoding="utf-8", newline="") as stream:
            writer = csv.DictWriter(stream, fieldnames=list(result["rows"][0]))
            writer.writeheader()
            writer.writerows(result["rows"])
    print(json.dumps(result["summary"], indent=2, allow_nan=False))
    print(f"Saved {len(result['rows'])} rows to {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
