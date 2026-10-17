# Dependency-policy extension: recorded results and limits

Author: Mackenzie Conor James Clark / Lycheetah Framework.
Implementation: Aetheron / Antigravity. Review: Caelorynth / Codex, 17 October 2026.
Register: **SYNTHETIC**.

The [original 768-row JSON](topological_recorded.json) is preserved unchanged.
Its source revision, raw hash and reviewed source identities are recorded in
[the manifest](topological_manifest.json) and [reproduction note](REPRODUCING_RECORDED_RUNS.md).
It is a finite simulator result, not a mathematical proof or empirical glass law.

## What the model adds

The engine traverses dependency edges and charges declared semantic work. On the
recorded 12-concept engine, a star hub costs 47 operations versus 25 for a leaf;
mean calibration work differs across chain, star, balanced and multi-parent DAGs.
These counts belong to the recorded engine revision. The new diagnostic work
changes the current calibration.

The model also explicitly suspends local adjudication when a child's governing
parents carry different paradigm labels, and includes child/parent disagreement
in its conflict metric. In selected contradictory multi-parent runs at nominal
load >= 1, mean conflict after drain is 0.7464 and maximum is 0.9167 despite zero
backlog. Selected tree runs drain to zero; compatible controls have zero conflict.
Correcting a parent can resolve the fixture's disagreement.

**Persistent conflict follows from the declared policy and metric.** It is not an
independent derivation of a glass state from topology. No sheaf, boundary matrix,
cohomology group or Betti number is computed. The three-node two-parent fixture
already triggers the policy although its undirected graph is a tree. Historical
JSON keys containing `theorem`, `b1_eq_0` or `b1_gt_0` do not establish those claims.

## Three sequential service policies

At nominal load >= 3 on contradictory streams:

| Policy | CASCADE minus FIFO mean g | CASCADE mean drain duration |
|---|---:|---:|
| Fixed service, completion-time inputs | -0.3159 | 12.58 |
| Fixed service, start-time inputs and domain isolation | -0.0801 | 19.18 |
| Measured work, start-time inputs and domain isolation | -0.0360 | 65.97 |

Durations use **virtual work/rate time**, not measured wall-clock seconds. Traces
are matched within each condition. Moving to the middle policy changes both input
timing and cross-domain queue visibility. The three policies are not a full
factorial design and do not identify those effects separately. Topology also
changes calibration and hence the offered rates at the same nominal load.

The source retains historical output keys for compatibility and now emits an
explicit claim-status and limitations field. Cross-seat review corrected its
initial theorem framing. No production governor, natural-language truth guarantee,
or general topology-to-cohomology result is established by these runs.
