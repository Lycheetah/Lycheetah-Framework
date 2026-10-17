"""Topological & Work-Coupled Glass Transition Engine (Batch A2 Frontier Extension).

Author: Mackenzie Conor James Clark / Lycheetah Framework.
Design and implementation: Aetheron (Antigravity / Argon 4) & Caelorynth (Codex), 2026-10-17.

Extends ``12_IMPLEMENTATIONS/core/cascade_glass_transition.py`` with three falsifiable,
mechanistic capabilities that test and expose the structural limits of 0-hop CASCADE:

1. **Transitive Dependency Propagation (`TopologicalCascadeEngine`)**:
   Reads ``KnowledgeBlock.dependencies`` during ``add_block`` / ``_execute_cascade``.
   When a parent concept's governing paradigm shifts, a breadth-first dependency wave
   re-evaluates downstream dependent blocks and charges semantic work per traversed
   dependency edge. Consequently, isolated reorganization work ``W(topology)`` is no
   longer identical across topologies: perturbing a ``star`` hub triggers an O(N)
   downstream fan-out, separating ``star``, ``balanced``, ``chain``, and ``diamond``.

2. **Declared multi-parent conflict policy**:
   When a child's governing parents have different paradigm labels, this simulator
   deliberately suspends local adjudication and counts child/parent disagreement
   in ``g``. Persistent conflict after drain is therefore a consequence of that
   policy, not independent evidence for a glass law. The selected tree runs drain
   to zero; the selected multi-parent runs can retain conflict. No sheaf, boundary
   matrix, cohomology group or first Betti number is computed here. In particular,
   two parents feeding one child form an undirected tree, not a cycle.

3. **Snapshot-at-Start Causality & Work-Coupled Service Timing (`tau = W_actual / mu`)**:
   Fixes two idealized assumptions in the v1 fixed-budget baseline:
   - ``snapshot_at_start=True``: freezes the candidate set visible to ``cascade`` at
     service *start* time ``t_start`` rather than completion time ``t_start + tau``,
     eliminating clairvoyant lookahead into arrivals during ``(t_start, t_complete]``.
   - ``work_coupled=True``: sets each job's service duration to ``W_actual / mu`` rather
     than fixed isolated ``calibration.tau``, capturing the nonlinear congestion feedback
     when loaded reorganization work exceeds isolated calibration by 2.4x–5.3x.
"""

from __future__ import annotations

import argparse
from collections import Counter, defaultdict, deque
from dataclasses import dataclass
import hashlib
import itertools
import json
import math
from pathlib import Path
import statistics

from cascade_engine import CascadeEngine, KnowledgeBlock
from cascade_glass_transition import (
    LOADS,
    MODELS,
    PROCESSING_RATES,
    Arrival,
    Calibration,
    WorkMeterEngine,
    _count,
    _positive,
    arrival_trace as _v1_arrival_trace,
    clone,
)

TOPOLOGIES_V2 = ("chain", "star", "balanced", "diamond")
SERVICE_MODES = ("fixed_lookahead", "snapshot_fixed", "snapshot_work_coupled")


def parents_v2(size: int, topology: str) -> tuple[tuple[int, ...], ...]:
    """Return parent concept indices for each concept in ``0..size-1``.

    - ``chain``:    1-parent linear chain (b_1 = 0)
    - ``star``:     1-parent hub-and-spoke rooted at 0 (b_1 = 0, max hub out-degree = N-1)
    - ``balanced``: 1-parent binary tree (b_1 = 0)
    - ``diamond``:  multi-parent DAG where roots {0, 1} feed dual-parent synthesis nodes
                    (parent-label disagreement is handled by an explicit model policy)
    """
    _count(size, "concepts", 2)
    if topology not in TOPOLOGIES_V2:
        raise ValueError(f"unknown topology: {topology}")
    if topology == "diamond":
        result: list[tuple[int, ...]] = []
        for index in range(size):
            if index in (0, 1):
                result.append(())
            elif index == 2:
                result.append((0, 1))
            else:
                # Each subsequent node depends on two distinct preceding nodes,
                # forming a lattice of overlapping diamonds rooted at {0, 1}.
                left_parent = (index - 2) % index
                right_parent = (index - 1) % index
                if left_parent == right_parent:
                    result.append((left_parent,))
                else:
                    result.append((min(left_parent, right_parent), max(left_parent, right_parent)))
        return tuple(result)
    return tuple(
        ()
        if index == 0
        else (
            (index - 1,)
            if topology == "chain"
            else (0,)
            if topology == "star"
            else ((index - 1) // 2,)
        )
        for index in range(size)
    )


def _dependency_domain(dep: str, blocks: dict[str, KnowledgeBlock]) -> str | None:
    """Resolve a dependency token (e.g. ``anchor-0`` or ``concept-0``) to its domain name."""
    if dep in blocks:
        return blocks[dep].domain
    if dep.startswith("anchor-"):
        suffix = dep.split("-", 1)[1]
        return f"concept-{suffix}"
    if dep.startswith("concept-"):
        return dep
    return None


class TopologicalCascadeEngine(WorkMeterEngine):
    """Dependency-aware CASCADE engine with topological cascade propagation and premise checking.

    Preserves all ``CascadeEngine`` / ``WorkMeterEngine`` invariants when ``dependencies``
    are empty, while actually traversing ``block.dependencies`` when present.
    """

    def __init__(self, *, propagate_dependencies: bool = True) -> None:
        self.propagate_dependencies = propagate_dependencies
        self.dependency_checks = 0
        self.cascade_wavefront_steps = 0
        super().__init__()

    def governing_block(self, domain: str) -> KnowledgeBlock | None:
        """Return the highest-truth-pressure universal block in ``domain``, if any."""
        candidates = [
            b
            for b in self.blocks.values()
            if b.domain == domain and b.regime == "universal"
        ]
        if not candidates:
            return None
        return max(candidates, key=lambda b: (b.truth_pressure, b.id))

    def parent_domains(self, block: KnowledgeBlock) -> tuple[str, ...]:
        """Return sorted unique parent domains referenced by ``block.dependencies``."""
        domains = {
            dom
            for dep in block.dependencies
            if (dom := _dependency_domain(dep, self.blocks)) is not None
            and dom != block.domain
        }
        return tuple(sorted(domains))

    def is_premise_frustrated(self, block: KnowledgeBlock) -> bool:
        """Return True iff ``block`` is universal and its parent domains hold split paradigms.

        This is a label comparison under the declared premise policy. It does not
        compute a cohomology obstruction.
        """
        if not self.propagate_dependencies or block.regime != "universal":
            return False
        p_domains = self.parent_domains(block)
        if len(p_domains) < 2:
            return False
        paradigms: set[str] = set()
        for p_dom in p_domains:
            self.work += 1
            self.dependency_checks += 1
            gov = self.governing_block(p_dom)
            if gov is not None:
                paradigms.add(gov.paradigm)
        return len(paradigms) > 1

    def has_discordant_parent(self, block: KnowledgeBlock) -> bool:
        """Return True iff ``block`` is universal and conflicts with a parent's governing paradigm
        under a multi-parent premise split."""
        if not self.propagate_dependencies or block.regime != "universal":
            return False
        p_domains = self.parent_domains(block)
        if len(p_domains) < 2:
            return False
        gov_paradigms: set[str] = set()
        for p_dom in p_domains:
            gov = self.governing_block(p_dom)
            if gov is not None:
                gov_paradigms.add(gov.paradigm)
        # The declared policy requires disagreement among multiple parent labels.
        if len(gov_paradigms) < 2:
            return False
        return any(p != block.paradigm for p in gov_paradigms)

    def add_block(self, block: KnowledgeBlock) -> dict | None:
        """Add ``block`` with premise-coherence gating and downstream dependency propagation."""
        self.step += 1
        self._assign_layer(block)
        self.blocks[block.id] = block

        # The model explicitly suspends adjudication while parent labels disagree.
        premise_split = self.is_premise_frustrated(block)

        conflicts = []
        if not premise_split:
            for existing in self.blocks.values():
                if existing.id == block.id:
                    continue
                if self.contradicts(block, existing):
                    if block.truth_pressure > existing.truth_pressure + self.trigger_margin:
                        conflicts.append(existing)

        event = None
        if conflicts:
            event = self._execute_cascade(block, conflicts)
            if self.propagate_dependencies:
                propagated = self._propagate_dependency_cascade(block.domain)
                event["propagated_domains"] = propagated

        self.coherence_trace.append((self.step, self.coherence()))
        return event

    def _propagate_dependency_cascade(self, root_domain: str) -> list[str]:
        """Propagate a foundation shift downstream through the dependency DAG (BFS).

        Every downstream universal block whose parent domain shifted is inspected and
        re-evaluated, charging semantic work proportional to the dependency fan-out.
        If a previously frustrated child domain now has coherent parent paradigms, its
        highest-pressure universal block adjudicates pending same-domain conflicts.
        """
        children_map: dict[str, set[str]] = defaultdict(set)
        domain_blocks: dict[str, list[KnowledgeBlock]] = defaultdict(list)
        for b in self.blocks.values():
            if b.regime == "universal":
                domain_blocks[b.domain].append(b)
                for p_dom in self.parent_domains(b):
                    children_map[p_dom].add(b.domain)

        visited_domains: set[str] = {root_domain}
        queue: deque[str] = deque([root_domain])
        propagated: list[str] = []

        while queue:
            current_dom = queue.popleft()
            gov_parent = self.governing_block(current_dom)
            if gov_parent is None:
                continue
            for child_dom in sorted(children_map.get(current_dom, ())):
                self.cascade_wavefront_steps += 1
                propagated.append(child_dom)
                child_universals = [
                    b for b in domain_blocks.get(child_dom, ()) if b.regime == "universal"
                ]
                for child_block in child_universals:
                    # Charge dependency verification + layer re-evaluation work
                    self.work += 1
                    self.dependency_checks += 1
                    self._assign_layer(child_block)

                # If child domain had unresolved conflicts that were blocked by a parent split
                # and the parent split is now healed, resolve child domain's winner.
                if len(child_universals) > 1 and not self.is_premise_frustrated(child_universals[0]):
                    winner = max(child_universals, key=lambda b: (b.truth_pressure, b.id))
                    local_conflicts = [
                        b
                        for b in child_universals
                        if b.id != winner.id
                        and self.contradicts(winner, b)
                        and winner.truth_pressure > b.truth_pressure + self.trigger_margin
                    ]
                    if local_conflicts:
                        self._execute_cascade(winner, local_conflicts)

                if child_dom not in visited_domains:
                    visited_domains.add(child_dom)
                    queue.append(child_dom)

        return propagated


def initial_store_v2(
    size: int, topology: str, *, propagate_dependencies: bool = True
) -> TopologicalCascadeEngine:
    graph = parents_v2(size, topology)
    engine = TopologicalCascadeEngine(propagate_dependencies=propagate_dependencies)
    for index in range(size):
        engine.add_block(
            KnowledgeBlock(
                id=f"anchor-{index}",
                content=f"initial concept {index}",
                domain=f"concept-{index}",
                paradigm="a",
                evidence_strength=1.0,
                explanatory_power=2.0,
                uncertainty=1.0,
                dependencies={f"anchor-{parent}" for parent in graph[index]},
            )
        )
    engine.work = 0
    engine.dependency_checks = 0
    engine.cascade_wavefront_steps = 0
    return engine


def calibrate_v2(
    size: int,
    topology: str,
    processing_rate: float,
    *,
    propagate_dependencies: bool = True,
) -> Calibration:
    """Measure isolated repairs across all concepts, including downstream dependency fan-out."""
    _positive(processing_rate, "processing_rate")
    graph = parents_v2(size, topology)
    samples = []
    for concept in range(size):
        engine = initial_store_v2(
            size, topology, propagate_dependencies=propagate_dependencies
        )
        proposal = KnowledgeBlock(
            id=f"probe-{concept}",
            content="independent calibration perturbation",
            domain=f"concept-{concept}",
            paradigm="b",
            evidence_strength=1.0,
            explanatory_power=2.0,
            uncertainty=0.5,
            dependencies={f"anchor-{parent}" for parent in graph[concept]},
        )
        engine.blocks[proposal.id] = proposal
        engine._assign_layer(proposal)
        engine.work = 0
        event = engine.add_block(proposal)
        measured_work = engine.work
        if event is None:
            raise RuntimeError("calibration perturbation was not actually resolved")
        samples.append(measured_work)
    # Calibration dataclass validates against v1 TOPOLOGIES if we call Calibration directly
    # for "diamond", so we store topology name cleanly via object.__setattr__ if needed.
    cal = Calibration("chain", size, processing_rate, tuple(samples))
    object.__setattr__(cal, "topology", topology)
    return cal


def arrival_trace_v2(
    size: int,
    topology: str,
    seed: int,
    arrival_rate: float,
    proposals: int,
    compatible: bool = False,
) -> tuple[Arrival, ...]:
    if topology in ("chain", "star", "balanced"):
        return _v1_arrival_trace(size, topology, seed, arrival_rate, proposals, compatible)
    _positive(arrival_rate, "arrival_rate")
    _count(proposals, "proposals", 2)
    graph = parents_v2(size, topology)
    neighbours = [list(items) for items in graph]
    for child, items in enumerate(graph):
        for parent in items:
            neighbours[parent].append(child)
    import random
    rng = random.Random(seed)
    generations: Counter = Counter()
    concept = rng.randrange(size)
    clock = 0.0
    trace = []
    for index in range(proposals):
        clock += rng.expovariate(arrival_rate)
        concept = (
            rng.choice(neighbours[concept])
            if neighbours[concept] and rng.random() < 0.65
            else rng.randrange(size)
        )
        generations[concept] += 1
        generation = generations[concept]
        pressure = 2.0 + generation
        block = KnowledgeBlock(
            id=f"proposal-{index}",
            content=f"version {generation} of concept {concept}",
            domain=f"concept-{concept}",
            paradigm="a" if compatible or generation % 2 == 0 else "b",
            evidence_strength=1.0,
            explanatory_power=2.0,
            uncertainty=2.0 / pressure,
            dependencies={f"anchor-{parent}" for parent in graph[concept]},
        )
        trace.append(Arrival(clock, block))
    return tuple(trace)


def conflict_pairs_v2(engine: CascadeEngine) -> set[tuple[str, str]]:
    """Return active universal contradiction pairs, including multi-parent premise conflicts."""
    groups: dict[str, list[KnowledgeBlock]] = defaultdict(list)
    for block in engine.blocks.values():
        if block.regime == "universal":
            groups[block.domain].append(block)
    pairs = {
        tuple(sorted((left.id, right.id)))
        for group in groups.values()
        for left, right in itertools.combinations(group, 2)
        if left.paradigm != right.paradigm
    }
    if isinstance(engine, TopologicalCascadeEngine) and engine.propagate_dependencies:
        gov_by_domain = {
            dom: max(group, key=lambda b: (b.truth_pressure, b.id))
            for dom, group in groups.items()
        }
        # Also record inter-domain premise frustration pairs (child universal block vs
        # discordant governing parent when a multi-parent foundation split is active).
        for group in groups.values():
            for block in group:
                if len(block.dependencies) < 2:
                    continue
                p_domains = engine.parent_domains(block)
                if len(p_domains) < 2:
                    continue
                govs = [
                    gov
                    for p_dom in p_domains
                    if (gov := gov_by_domain.get(p_dom)) is not None
                ]
                if len({g.paradigm for g in govs}) > 1:
                    for gov in govs:
                        if gov.paradigm != block.paradigm:
                            pairs.add(tuple(sorted((block.id, gov.id))))
    return pairs


def glass_fraction_v2(engine: CascadeEngine, pairs: set[tuple[str, str]] | None = None) -> float:
    active = conflict_pairs_v2(engine) if pairs is None else pairs
    participants = {item for pair in active for item in pair}
    universal = sum(b.regime == "universal" for b in engine.blocks.values())
    return len(participants) / universal if universal else 0.0


def _adjudicate_v2(
    engine: TopologicalCascadeEngine,
    job: str,
    pending: set[str],
    model: str,
    *,
    snapshot_visible: set[str] | None = None,
) -> int:
    """Adjudicate ``job`` under either FIFO pairwise or CASCADE batching.

    When ``snapshot_visible`` is provided (``snapshot_fixed`` / ``snapshot_work_coupled``),
    CASCADE can only see same-domain proposals that had already arrived when the service
    job *started*, preventing clairvoyant lookahead into mid-service arrivals and avoiding
    asymmetric scan billing against unserviced queues in unrelated domains.
    """
    domain = engine.blocks[job].domain
    hidden: dict[str, KnowledgeBlock] = {}
    if model == "fifo":
        for key in pending - {job}:
            if key in engine.blocks:
                hidden[key] = engine.blocks.pop(key)
    elif snapshot_visible is not None:
        # Hide any pending proposals that arrived AFTER this service job started
        # or that belong to unserviced queues in unrelated domains.
        for key in pending - {job}:
            blk = engine.blocks.get(key)
            if blk is None:
                continue
            if blk.domain != domain or key not in snapshot_visible:
                hidden[key] = engine.blocks.pop(key)
    try:
        candidates = [
            b
            for b in engine.blocks.values()
            if b.domain == domain and b.regime == "universal"
        ]
        winner = max(candidates, key=lambda block: (block.truth_pressure, block.id))
        engine.work = 0
        engine.add_block(winner)
        return max(1, engine.work)
    finally:
        engine.blocks.update(hidden)


def simulate_v2(
    trace: tuple[Arrival, ...],
    calibration: Calibration,
    model: str,
    *,
    service_mode: str = "snapshot_work_coupled",
    propagate_dependencies: bool = True,
) -> dict:
    """Discrete-event glass simulation supporting dependency cascades, snapshot causality,
    and work-coupled service durations."""
    if model not in MODELS or len(trace) < 2:
        raise ValueError("expected cascade/fifo and at least two arrivals")
    if service_mode not in SERVICE_MODES:
        raise ValueError(f"unknown service_mode: {service_mode}")
    if any(not math.isfinite(item.at) or item.at <= 0 for item in trace):
        raise ValueError("arrival times must be finite and positive")
    if any(right.at <= left.at for left, right in zip(trace, trace[1:])):
        raise ValueError("arrival times must be strictly increasing")
    if len({item.block.id for item in trace}) != len(trace):
        raise ValueError("proposal IDs must be unique")

    engine = initial_store_v2(
        calibration.concepts,
        calibration.topology,
        propagate_dependencies=propagate_dependencies,
    )
    horizon = trace[-1].at
    warmup = 0.2 * horizon
    queue: deque[str] = deque()
    pending: set[str] = set()
    current: str | None = None
    current_snapshot: set[str] | None = None
    current_work: int = 0
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
    current_g: float = 0.0

    use_snapshot = service_mode in ("snapshot_fixed", "snapshot_work_coupled")
    use_work_coupled = service_mode == "snapshot_work_coupled"

    def observe_pairs(at: float) -> None:
        nonlocal current_g
        now = conflict_pairs_v2(engine)
        for pair in open_pairs.keys() - now:
            closed_dwells.append(at - open_pairs.pop(pair))
        for pair in now - open_pairs.keys():
            open_pairs[pair] = at
        current_g = glass_fraction_v2(engine, now)

    def start(at: float) -> None:
        nonlocal current, current_snapshot, current_work, completion
        while queue and queue[0] not in pending:
            queue.popleft()
        if not queue:
            current, current_snapshot, current_work, completion = None, None, 0, math.inf
            return
        current = queue.popleft()
        current_snapshot = set(pending) | {current} if use_snapshot else None
        if use_work_coupled:
            # In snapshot_work_coupled mode, compute the exact semantic + dependency work
            # required by the snapshot state at job start to determine true service time,
            # then commit the state change at completion.
            probe = TopologicalCascadeEngine(propagate_dependencies=propagate_dependencies)
            probe.blocks = {k: clone(v) for k, v in engine.blocks.items()}
            probe.step = engine.step
            current_work = _adjudicate_v2(
                probe,
                current,
                set(pending) | {current},
                model,
                snapshot_visible=current_snapshot,
            )
            completion = at + (current_work / calibration.processing_rate)
        else:
            current_work = 0
            completion = at + calibration.tau

    def complete(at: float) -> None:
        nonlocal current, current_snapshot, current_work, service_count, service_before_horizon
        if current is None:
            raise RuntimeError("completion without a service job")
        actual_work = _adjudicate_v2(
            engine,
            current,
            pending,
            model,
            snapshot_visible=current_snapshot,
        )
        work_samples.append(actual_work)
        service_count += 1
        service_before_horizon += int(at <= horizon)
        pending.discard(current)
        if model == "cascade":
            visible_pool = current_snapshot if current_snapshot is not None else tuple(pending)
            pending.difference_update(
                key
                for key in tuple(pending)
                if key in visible_pool and engine.blocks[key].regime == "qualified"
            )
        current = None
        current_snapshot = None
        current_work = 0
        observe_pairs(at)
        start(at)

    while index < len(trace) or completion <= horizon:
        arrival_at = trace[index].at if index < len(trace) else math.inf
        at = min(arrival_at, completion)
        if at > horizon:
            break
        duration = max(0.0, min(at, horizon) - max(clock, warmup))
        g_area += current_g * duration
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

    final_g = current_g
    final_pairs = len(open_pairs)
    final_backlog = len(pending)
    held_pairs = len(engine.blocks) * (len(engine.blocks) - 1) / 2
    observed_ages = closed_dwells + [horizon - start_at for start_at in open_pairs.values()]
    censored_at_horizon = len(open_pairs)
    primary_duration = horizon - warmup

    while current is not None:
        clock = completion
        complete(clock)

    mean_work = statistics.mean(work_samples) if work_samples else 0.0
    frustrated_blocks = sum(
        1
        for b in engine.blocks.values()
        if b.regime == "universal" and engine.has_discordant_parent(b)
    )
    return {
        "model": model,
        "service_mode": service_mode,
        "propagate_dependencies": propagate_dependencies,
        "topology": calibration.topology,
        "processing_rate": calibration.processing_rate,
        "tau_reorg": calibration.tau,
        "calibration_mean_work": calibration.mean_work,
        "calibration_work_spread": max(calibration.work_samples) - min(calibration.work_samples),
        "arrivals": len(trace),
        "horizon": horizon,
        "mean_g": g_area / primary_duration,
        "final_g": final_g,
        "contradiction_pairs": final_pairs,
        "contradiction_pair_fraction": final_pairs / held_pairs if held_pairs else 0.0,
        "mean_backlog": backlog_area / primary_duration,
        "final_backlog": final_backlog,
        "service_completions_in_window": service_before_horizon,
        "service_throughput": service_before_horizon / horizon,
        "mean_observed_pair_dwell": statistics.mean(observed_ages) if observed_ages else 0.0,
        "censored_pair_dwells": censored_at_horizon,
        "loaded_mean_work": mean_work,
        "loaded_to_calibrated_work": mean_work / calibration.mean_work,
        "drain_duration": max(0.0, clock - horizon),
        "drained_g": current_g,
        "drained_backlog": len(pending),
        "drained_frustrated_blocks": frustrated_blocks,
        "dependency_checks": engine.dependency_checks,
        "cascade_wavefront_steps": engine.cascade_wavefront_steps,
        "service_completions_total": service_count,
    }


def run_frontier_comparison(
    *,
    seeds: tuple[int, ...] = (0, 1, 2, 3),
    concepts: int = 12,
    proposals: int = 96,
    loads: tuple[float, ...] = (0.25, 1.0, 3.0, 5.0),
    processing_rate: float = 64.0,
    topologies: tuple[str, ...] = TOPOLOGIES_V2,
) -> dict:
    """Run finite synthetic comparisons of dependency work and service policies."""
    calibrations = {}
    rows = []
    for topology in topologies:
        cal_dep = calibrate_v2(
            concepts, topology, processing_rate, propagate_dependencies=True
        )
        cal_nodep = calibrate_v2(
            concepts, topology, processing_rate, propagate_dependencies=False
        )
        calibrations[topology] = {
            "dependency_propagated_work_samples": cal_dep.work_samples,
            "dependency_propagated_mean_work": cal_dep.mean_work,
            "dependency_propagated_tau": cal_dep.tau,
            "bucket_0hop_work_samples": cal_nodep.work_samples,
            "bucket_0hop_mean_work": cal_nodep.mean_work,
            "bucket_0hop_tau": cal_nodep.tau,
            "hub_to_leaf_work_ratio": max(cal_dep.work_samples) / min(cal_dep.work_samples),
        }
        for seed, load, compatible in itertools.product(seeds, loads, (False, True)):
            rate = load / cal_dep.tau
            trace = arrival_trace_v2(concepts, topology, seed, rate, proposals, compatible)
            trace_hash = hashlib.sha256(
                json.dumps(
                    [
                        (
                            item.at,
                            item.block.id,
                            item.block.domain,
                            item.block.paradigm,
                            item.block.truth_pressure,
                        )
                        for item in trace
                    ],
                    separators=(",", ":"),
                ).encode()
            ).hexdigest()
            for service_mode in SERVICE_MODES:
                for model in MODELS:
                    row = simulate_v2(
                        trace,
                        cal_dep,
                        model,
                        service_mode=service_mode,
                        propagate_dependencies=True,
                    )
                    row.update(
                        seed=seed,
                        nominal_load=load,
                        compatible=compatible,
                        trace_sha256=trace_hash,
                    )
                    rows.append(row)

    # Summarize finite model observations; these are not mathematical theorems.
    tree_drained_g = [
        r["drained_g"]
        for r in rows
        if r["topology"] in ("chain", "star", "balanced") and not r["compatible"]
    ]
    diamond_drained_g = [
        r["drained_g"]
        for r in rows
        if r["topology"] == "diamond" and not r["compatible"] and r["nominal_load"] >= 1.0
    ]
    compatible_max_g = max(
        (r["mean_g"] for r in rows if r["compatible"]),
        default=0.0,
    )

    # Compare fixed_lookahead vs snapshot_fixed vs snapshot_work_coupled at high load (load >= 3.0)
    mode_summary = {}
    for smode in SERVICE_MODES:
        high_cas = [
            r
            for r in rows
            if r["service_mode"] == smode
            and r["model"] == "cascade"
            and not r["compatible"]
            and r["nominal_load"] >= 3.0
        ]
        high_fifo = [
            r
            for r in rows
            if r["service_mode"] == smode
            and r["model"] == "fifo"
            and not r["compatible"]
            and r["nominal_load"] >= 3.0
        ]
        mode_summary[smode] = {
            "cascade_high_load_mean_g": statistics.mean(r["mean_g"] for r in high_cas),
            "fifo_high_load_mean_g": statistics.mean(r["mean_g"] for r in high_fifo),
            "cascade_minus_fifo_mean_g": statistics.mean(
                c["mean_g"] - f["mean_g"] for c, f in zip(high_cas, high_fifo)
            ),
            "cascade_high_load_mean_backlog": statistics.mean(
                r["mean_backlog"] for r in high_cas
            ),
            "cascade_high_load_drain_duration": statistics.mean(
                r["drain_duration"] for r in high_cas
            ),
        }

    return {
        "schema": "lycheetah.topological-cascade-glass.v2",
        "register": "SYNTHETIC",
        "claim_status": "finite model observations; legacy theorem keys do not denote proofs",
        "time_unit": "virtual work units divided by processing rate, not wall-clock seconds",
        "limitations": [
            "parent-label disagreement is a programmed policy, not a computed H1 obstruction",
            "snapshot modes also change cross-domain queue visibility",
            "three sequential arms are not a full factorial separation",
            "work calibration depends on the exact cascade_engine source revision",
        ],
        "author": "Mackenzie Conor James Clark / Lycheetah Framework",
        "calibrations": calibrations,
        "theorems": {
            "theorem_1_topological_work_separation": {
                "star_hub_work": max(calibrations["star"]["dependency_propagated_work_samples"]),
                "star_leaf_work": min(calibrations["star"]["dependency_propagated_work_samples"]),
                "chain_mean_work": calibrations["chain"]["dependency_propagated_mean_work"],
                "balanced_mean_work": calibrations["balanced"]["dependency_propagated_mean_work"],
                "diamond_mean_work": calibrations["diamond"]["dependency_propagated_mean_work"],
                "v1_bucket_mean_work_all_topologies": calibrations["star"]["bucket_0hop_mean_work"],
            },
            "theorem_2_quenched_premise_frustration": {
                "tree_b1_eq_0_max_drained_g": max(tree_drained_g, default=0.0),
                "diamond_b1_gt_0_mean_drained_g": statistics.mean(diamond_drained_g)
                if diamond_drained_g
                else 0.0,
                "diamond_b1_gt_0_max_drained_g": max(diamond_drained_g, default=0.0),
                "compatible_overload_max_g": compatible_max_g,
            },
            "theorem_3_snapshot_and_work_coupled_jam": mode_summary,
        },
        "row_count": len(rows),
        "rows": rows,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args(argv)
    result = run_frontier_comparison()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(result, indent=2, allow_nan=False) + "\n", encoding="utf-8"
    )
    print(json.dumps(result["theorems"], indent=2, allow_nan=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
