# CASCADE glass-transition experiment — fixed protocol v1

Author: Mackenzie Conor James Clark / Lycheetah Framework.
Implementation and experimental design: Caelorynth / Codex, 2026-10-17.
Register: SYNTHETIC. Written before the first sweep.

## Question and source boundary

Test the condition in `TRUTH_PRESSURE/THE_GLASS_TRANSITION_CANON.md`, using the
existing CASCADE engine in a finite, scheduled synthetic memory experiment.
The source expressly fences out claims of a sharp or first-order transition.
Neither a sharp transition nor a critical exponent is an acceptance requirement.
This simulation is not the live LAMAGUE council experiment, a memory git-history
audit, evidence about people, or evidence for substrate independence.

## Operationalisation

- Meaning: finite KnowledgeBlock proposals, each naming a synthetic concept/domain,
  paradigm, and explicit evidence/uncertainty scores.
- Layering and contradiction: the existing CASCADE engine's layer thresholds,
  truth-pressure ordering and same-domain/different-paradigm universal conflicts.
- Arrival process: seeded exponential interarrival times. Chain, star and balanced
  DAGs determine correlated concept selection and populate dependency metadata.
  CASCADE currently does not interpret that metadata; topology is a workload
  intervention, not a claim of dependency-aware reasoning.
- Reorganisation time: independently run isolated, stronger-evidence perturbations
  against a clean store; count engine contradiction comparisons and layer
  assignments. Mean work units divided by a separately chosen processing rate is
  tau_reorg. Virtual service uses that calibrated budget. These are declared
  semantic work units, not CPU seconds. Record actual loaded work separately so
  calibration drift remains visible.
- V = offered arrival rate * calibrated tau_reorg is computed for analysis. The
  simulator never consults V or branches at one to create its outcome.
- Admission: admit proposals before queued adjudication. Report admission and
  completion counts explicitly; draining after arrivals stop is a separate test.
- Primary g: fraction of universal held blocks participating in at least one
  unresolved contradiction. Also report unresolved-pair count, pair fraction,
  backlog, throughput, and contradiction dwell-time. Do not substitute backlog for g.

## Intervention and null

CASCADE adjudicates the highest-pressure available version of the serviced
concept and can qualify several weaker admitted proposals. FIFO presents only its
serviced proposal and already adjudicated state to the same core engine. Compare
the same proposal stream using the same calibration and serialized service budget.
Both arms retain unprocessed proposals as universal held claims. The batching
policy is this harness's explicit intervention, not a new upstream CASCADE API.
A compatible-only stream is a negative control: overload can produce backlog
without semantic contradiction.

Graph, seed, arrival rate, and processing rate are varied independently. Matched
arms share the exact proposal trace. The primary sweep fixes arrival rates from
reference-load values 0.1, 0.25, 0.5, 0.75, 1.0, 1.25, 2.0, 3.0, 5.0 at reference
processing rate 64. It crosses that unchanged arrival grid with processing rates
64 and 128; three topologies; seeds 0–3; 96 proposals and 12 concepts per run.
V is then computed for each row, rather than keeping it constant by changing
arrivals whenever processing changes.

Preflight amendment before the primary sweep: the initial 12-row smoke run used
coupled rescaling of arrivals and processing. The primary grid above corrects the
intervention design. The smoke output is a development check, not evidence in the
primary result. Outcome screens and their thresholds below are unchanged.

## Decision rules fixed before the run

1. Report low-load (V <= 0.5) and high-load (V >= 2) mean g per arm, seed and
   topology. Record a directional load effect only if the high-minus-low
   difference exceeds 0.05. This is a descriptive screen, not a significance test.
2. Report matched CASCADE-minus-FIFO differences. Similar load responses are
   consistent with ordinary queueing; a load effect alone does not distinguish a
   semantic glass law. Differences describe this implementation, not a universal law.
3. A compatible overloaded stream must have g = 0 even when backlog > 0.
   This distinguishes semantic contradiction from queue occupancy and bounds any
   use of total arrival rate as a sufficient predictor.
4. Stop arrivals and allow queued work to drain in a separate control. Record
   whether conflicts disappear. A transient queue backlog is not evidence of
   irreversible freezing or a thermodynamic phase transition.
5. Calibration is estimated before the arrival sweep and never fitted to g.
   Report the loaded-to-calibrated work ratio; do not hide load-dependent tau.
6. Keep every row and seed. No best-seed selection, threshold tuning after the
   result, or promotion of this finite simulation to natural-domain evidence.

## Deliverable and falsifiers

A runnable local command, raw JSON/CSV rows, reproducible aggregate findings and
a readable result note. Focused checks must distinguish: semantic conflict vs
backlog; real CASCADE qualification vs FIFO; independent calibration vs fitted
latency; reproducibility; distinct processing/ingestion interventions; and drain
recovery. Any failed check blocks an experimental claim.

Even a successful synthetic load effect leaves the natural-domain claims and
external review open. Lack of a load effect, a matching queue baseline, compatible
overload without contradiction, and complete drain recovery must remain visible.
