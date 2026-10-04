# Practical tools: make one real decision easier

**Status: PROPOSED product and game briefs; no prototype implied.**

The first useful outcome should fit on one screen and leave an inspectable artifact. A metaphor can welcome someone; explicit inputs and visible limitations carry the actual work.

[Catalogue home](README.md) · [Build contract](07_BUILD_CONTRACT_AND_SEQUENCE.md)

## LYC-B001 · Witness Desk

**Form:** tool · **Build status:** PROPOSED

Inspect a proposed action, its authority, its evidence and its unresolved conditions before deciding what to do.

- **Source to inspect:** [34_ASSURANCE_RUNTIME/README.md](../../34_ASSURANCE_RUNTIME/README.md). This is a lineage pointer, not a statement that the proposed product already exists.
- **Inputs:** A synthetic action, explicit approval flag, policy identity and named evidence records.
- **Interaction:** Choose an action → inspect the rule that applies → change one fact → see ALLOW, REVIEW or BLOCK with the reason. A separate human control decides whether a real host may act.
- **Artifact:** A local JSON decision record with policy version, evidence references and limitations.
- **First build:** One offline browser page and eight transparent fixtures; a ported demonstration evaluator must identify itself separately from the Python runtime.
- **Acceptance:** Every fixture explains the deciding rule; changing required evidence updates the result; export and reload preserve the inputs. REVIEW cannot trigger execution.
- **Limits:** The existing runtime is SCAFFOLD. A digest is not issuer authentication, and a correct permission decision does not establish harmlessness.

## LYC-B002 · Evidence Board

**Form:** tool · **Build status:** PROPOSED

Keep a claim, its supporting sources and competing explanations on the same visible board.

- **Source to inspect:** [01_CASCADE_L4/](../../01_CASCADE_L4/). This is a lineage pointer, not a statement that the proposed product already exists.
- **Inputs:** User-entered claims, dated sources, explicit uncertainty and conflicting observations.
- **Interaction:** Add a claim → attach a source → record a counterexample → compare interpretations → revise with a reason. Source age and status are visible without silently changing belief.
- **Artifact:** A versioned claim ledger and a readable account of what changed.
- **First build:** Five sample claims with manually entered sources, one conflict and an undoable revision.
- **Acceptance:** A reader can identify which source supports each statement; no revision deletes the previous claim or its rationale; unsupported claims remain labelled.
- **Limits:** CASCADE scores and reorganisations are research mechanisms, not truth oracles. Source quality requires human judgement and task-specific evaluation.

## LYC-B003 · Feedback Playground

**Form:** tool · **Build status:** PROPOSED

See why a controller oscillates, reacts late or has no actuator at all.

- **Source to inspect:** [34_CYBERNETICS/README.md](../../34_CYBERNETICS/README.md). This is a lineage pointer, not a statement that the proposed product already exists.
- **Inputs:** A toy plant, target, disturbance, sensor delay, controller gain and actuator limits.
- **Interaction:** Set a target → disturb the system → change gain or delay → watch state, error and control effort on one plot → compare with a disconnected loop.
- **Artifact:** A reproducible parameter preset and time-series export.
- **First build:** A temperature-like toy process with proportional control and a deliberately open-loop mode.
- **Acceptance:** Disconnected actuation cannot change the plant; delay and saturation are shown explicitly; replaying a fixed preset gives the same trajectory.
- **Limits:** The code audit identifies structural loop closure. It does not establish stability, correct sensing or efficacy in a real control system.

## LYC-B004 · Resonance Playground

**Form:** tool · **Build status:** PROPOSED

Explore synchronisation by moving frequencies and coupling, with a visible mathematical state.

- **Source to inspect:** [12_IMPLEMENTATIONS/core/harmonia_calculator.py](../../12_IMPLEMENTATIONS/core/harmonia_calculator.py). This is a lineage pointer, not a statement that the proposed product already exists.
- **Inputs:** Oscillator count, frequencies, initial phases, coupling strength and optional audio.
- **Interaction:** Start separated oscillators → increase coupling → perturb one oscillator → inspect phase relationships and the order parameter. Sound begins only after a tap.
- **Artifact:** A parameter preset, phase trace and optional user-requested recording.
- **First build:** Eight oscillators, a two-dimensional phase view and an on-demand sonification.
- **Acceptance:** Fixed seeds reproduce trajectories; displayed quantities come from the simulation; reduced motion and mute work; no audio starts automatically.
- **Limits:** Synchronisation in a toy oscillator model is not evidence of brain entrainment, healing or a universal harmony law.

## LYC-B005 · Goal and Change Journal

**Form:** tool · **Build status:** PROPOSED

Compare a chosen intention with observable actions without scoring the person.

- **Source to inspect:** [12_IMPLEMENTATIONS/core/microorcim_tracker.py](../../12_IMPLEMENTATIONS/core/microorcim_tracker.py). This is a lineage pointer, not a statement that the proposed product already exists.
- **Inputs:** A user-defined goal, explicit observations and a private review interval.
- **Interaction:** Write an intention → record a concrete action → inspect the discrepancy → choose a next step or revise the goal. The user can reject an interpretation.
- **Artifact:** A locally stored review that distinguishes events, interpretation and choice.
- **First build:** One goal, a short event timeline and an editable review; no hidden activity monitoring.
- **Acceptance:** Unknown events remain unknown; changing a goal preserves its earlier version; deletion and export work; the interface never turns missing activity into moral failure.
- **Limits:** MICROORCIM is a research lens. A chosen discrepancy metric is not a validated measure of agency, sovereignty, mental health or character.

## LYC-B006 · Transformation Workshop

**Form:** tool · **Build status:** PROPOSED

Compare transformation sequences and see why the order of operations matters.

- **Source to inspect:** [09_CHRYSOPOEIA_L4/](../../09_CHRYSOPOEIA_L4/). This is a lineage pointer, not a statement that the proposed product already exists.
- **Inputs:** A toy state vector or an ordinary document, explicit operations and a protected baseline.
- **Interaction:** Choose a sequence → preview each intermediate state → swap two operations → compare the result → keep, revise or undo.
- **Artifact:** A before/after diff with the operation order and user-supplied rationale.
- **First build:** A numerical demonstration plus one reversible document editing exercise; keep their claims separate.
- **Acceptance:** Swapping noncommuting operators visibly changes the toy output; document operations never silently rewrite the original; exported history explains each step.
- **Limits:** Formal operator properties under explicit assumptions do not imply personal transformation or validate historical alchemy.

## LYC-B007 · Pattern Explorer

**Form:** tool · **Build status:** PROPOSED

Compare recurring structures while keeping independent sources and rival explanations visible.

- **Source to inspect:** [07_ANAMNESIS_L0/](../../07_ANAMNESIS_L0/). This is a lineage pointer, not a statement that the proposed product already exists.
- **Inputs:** Source passages, named traditions, a proposed structural resemblance and diffusion alternatives.
- **Interaction:** Place two examples side by side → describe the resemblance → add differences → ask whether copying, shared constraints or coincidence explains it.
- **Artifact:** A comparison worksheet with attribution, counterexamples and an uncertainty statement.
- **First build:** Three openly usable examples and one deliberately misleading resemblance.
- **Acceptance:** The misleading example can be rejected; resemblance and ancestry are separate fields; each cultural source remains named and revisable.
- **Limits:** Similar motifs do not prove transcultural independence, shared metaphysical truth or permission to repurpose cultural knowledge.

## LYC-B008 · Resource Budget Bench

**Form:** tool · **Build status:** PROPOSED

Make an explicit time, memory or action allowance visible before allocating it.

- **Source to inspect:** [06_EARNED_LIGHT_L0/](../../06_EARNED_LIGHT_L0/). This is a lineage pointer, not a statement that the proposed product already exists.
- **Inputs:** A chosen resource unit, capacity, named tasks and measured or clearly estimated costs.
- **Interaction:** Allocate → run a simulated workload → inspect remaining capacity → change the schedule → compare results. Estimates are never silently relabelled as measurements.
- **Artifact:** An allocation table and a record of actual versus estimated expenditure.
- **First build:** A deterministic time/action scheduling toy, with one infeasible workload and a transparent refusal.
- **Acceptance:** The ledger cannot exceed its declared capacity; units remain consistent; the infeasible case explains which constraint blocks it.
- **Limits:** This is ordinary resource budgeting inspired by the lens. It does not operationalise consciousness thermodynamics or measure a person’s inner energy.
