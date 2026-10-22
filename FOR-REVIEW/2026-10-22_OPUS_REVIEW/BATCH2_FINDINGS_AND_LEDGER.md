# Opus review — Batch 2: findings register and coverage ledger

Reviewer seat: Sol (Claude Opus 5.5, xhigh). Date: 2026-10-22.
Branch: `review/full-framework-2026-10-20` at `d7ae0ad` (**not** `master`).
Nothing in this batch is committed or pushed. All edits are working-tree only.

Scope: checklist items **RV02** (sovereign harness binding) and **RV03**
(Psi-Consensus, arena, Grey Mode, MCP network health). Batch 1 also closed F09.
RV01, RV04–RV09, RV13 and RV15–RV37 are **not yet reviewed**. Nothing outside
the ledger below is marked reviewed.

Reproduction: `repro_batch2.py` in this folder prints one JSON object with a
`reproduced` flag per finding. It runs against the working tree and against a
`git archive HEAD` export of the same commit.

## Findings register

| ID | Item | Severity | Status | Where |
|----|------|----------|--------|-------|
| F11 | RV02 | Medium | FIXED in working tree | `lycheetah/assurance/gateway.py` |
| F12 | RV02 | Low | FIXED in working tree | `lycheetah/sovereign_harness.py` (permit issuance) |
| F13 | RV02 | Medium | PARTIAL: witness fixed, permit by design, v3 → Mac | `lycheetah/sovereign_harness.py` |
| F14 | RV03 | High | FIXED in working tree | `12_IMPLEMENTATIONS/core/psi_consensus.py`, `lycheetah/consensus/arena.py` |
| F15 | RV03 | High | FIXED in working tree | `psi_consensus.py` |
| F16 | RV03 | Medium | FIXED in working tree | `psi_consensus.py` |
| F17 | RV03 | High | FIXED in working tree | `psi_consensus.py`, `arena.py` |
| F18 | RV03 | Medium | FIXED in working tree | `arena.py`, `psi_consensus.py` |
| F19 | RV03 | Medium | FIXED in working tree | `psi_consensus.py`, `arena.py` |
| F20 | RV03 | Medium | FIXED in working tree | `arena.py` |
| F21 | RV03 | Medium | FIXED in working tree | `12_IMPLEMENTATIONS/applications/lycheetah_guard_mcp.py` |
| F22 | RV03 | High | FIXED at the Grey Mode boundary; kernel → Mac | `12_IMPLEMENTATIONS/core/grey_mode.py` |
| F23 | RV03 | Medium | OPEN, design decision for Mac | `grey_mode.py` re-entry threshold |
| F24 | RV03 | Medium | OPEN, design decision for Mac | `lycheetah/sovereign_harness.py` consensus gate |
| G2 | RV03 | Low | FIXED in working tree | `grey_mode.py` `recovery_cycle` |
| G3 | RV03 | Low | FIXED in working tree | `grey_mode.py` `run` |
| G6 | RV03 | Low | OPEN, note | `grey_mode.py` docstring vs alert counter |

### F11 — Two permits for one action in one second collided (MEASURED, FIXED)

The gateway derived its default approval id from
`sha256(digest:now:actor)` and the effect id from `sha256(aid:now)`, where `now`
had one-second resolution. Two legitimate proposals of the same action by the
same actor inside one second got the same ids. On HEAD the second run returned
`GATEWAY_BLOCKED`, and its permit was already consumed. Fix: default ids are
`secrets.token_hex(8)`. Explicit ids still pass through unchanged.

### F12 — String scope lists were split into characters (MEASURED, FIXED)

Permit issuance accepted `allowed_scopes="deploy"` and iterated it into nine
single-character scopes. Real scope checks then failed closed, but any
single-character scope was allowed. Issuance now refuses a string, and refuses
a `bound_scope` outside `allowed_scopes`.

### F13 — The permit binds the critical hash only (MEASURED, PARTIAL)

Two packets that differ only in non-critical fields share a critical hash, so
one permit authorises both. That is the documented design. The defect was
that the witness could not tell afterwards which complete packet ran. The
witness now records `reference_full_hash` and `candidate_full_hash`, and
records `None` for an invalid packet instead of raising. The probe's
`reproduced` flag stays true by design. `receipt_blind_to_change` is now false.
**Decision for Mac:** permit v3 (proposal P1 below).

### F14 — The anchor's antipode passed every consensus flag (MEASURED, FIXED)

The alignment gate used `|<ψ, anchor>|`. A unanimous network at the exact
opposite of the anchor scored as perfectly aligned. On HEAD the verdict was
converged, obstruction-free and Byzantine-safe, with drift 0.0. Fed into the
sovereign harness, **the action EXECUTED and the executor was called.** Drift
is now the signed `1 − <ψ, anchor>`, which for unit vectors equals the Lyapunov
function S = ½‖ψ − a‖² (DERIVED). It is 0 on the anchor, 1 when orthogonal and
2 at the antipode. The harness now stops with `CONSENSUS_NOT_CONVERGED`.

### F15 — Agreement far from the anchor converged (MEASURED, FIXED)

Convergence required only that no agent was quarantined. A unanimous network
orthogonal to the anchor converged with drift 1.0. Convergence now also
requires `anchor_aligned`, and the audit trail records the flag.

### F16 — Cancelling states got the anchor as their consensus (MEASURED, FIXED)

When states summed to zero, normalisation fell back to the anchor, so `[a, −a]`
reported consensus `[1, 0, 0]` with drift 0.0. The run now reports no
consensus vector, does not converge, and records drift 1.0.

### F17 — Re-registering an agent cleared its quarantine (MEASURED, FIXED)

`add_agent` with an existing id replaced the agent and reset its Grey Mode
record. A quarantined agent re-registered and came back HEALTHY on the next
run. Both `PsiConsensus.add_agent` and `ConsensusArena.add_agent` now refuse an
id that is already registered.

### F18 — Unknown neighbors were dropped silently (MEASURED, FIXED)

A neighbor list naming an unregistered agent was accepted, and the edge
vanished. On HEAD the run converged. Deliberation now refuses it with
`ValueError`.

### F19 — NaN and unusable parameters disabled quarantine (MEASURED, FIXED)

A NaN threshold made every comparison false, so nobody was quarantined. On
HEAD `quarantined == []`. `mu` outside (0, 1], non-positive round and alert
counts, and non-finite thresholds are now refused when the arena is built.

### F20 — Recovery rewrote an agent without a trace (MEASURED, FIXED)

`recover_agent` replaced the dissenter's state and proposal vector. Later
verdicts showed a clean network and no record of the rewrite. Later verdicts
now carry `RECOVERED: '<id>'` in the audit trail, and the integrity check
still passes.

### F21 — MCP network health could never quarantine (MEASURED, FIXED)

The MCP tool built a two-strike Grey Mode monitor and ran it once, so no agent
could reach quarantine. It printed "Network is healthy." for an antipodal
network, with drift `-0.0000`. It now uses a one-strike monitor for its single
run. An outlier is quarantined, and the antipodal report says not converged.

### F22 — TRIAD recovery readmitted an agent it carried to the antipode (MEASURED, FIXED at the boundary)

With default parameters, a back-hemisphere dissenter `[-0.5, 0.866, 0]` was
"recovered" to `[-1, 0, 0]`, reported `psi_r = 0.0`, and converged after one
cycle. The antipodal agent did the same. Its signed drift is 2.0.

Shared root cause in `12_IMPLEMENTATIONS/core/lamague_reference.py`
(`TRIADKernel`, not edited):

- `anchor_operator` returns `<ψ, a>·a`, a projection onto the line, so a
  back-hemisphere state lands on the antipode;
- `detect_drift` returns `1 − |<ψ, a>|`, so the antipode scores 0.

Fix at the Grey Mode boundary: `compute_psi_r` scores recovery with the signed
drift. That drift now has one definition, `grey_mode.anchor_drift`, which
`psi_consensus` imports, and the arena reaches it through `psi_consensus`. The
back-hemisphere agent now reports `psi_r = 2.0`, is not readmitted, and stays
quarantined. Control: an orthogonal dissenter still recovers to about
`[0.997, 0.035, 0]`.

The kernel was **not** changed. Whether TRIAD states are rays (sign-free) or
vectors (signed) is a framework-wide contract. Census of the unsigned pattern
(`detect_drift(`, `compute_psi_r(`, `1 - abs(`), with hit counts:

| File | Hits |
|------|------|
| `12_IMPLEMENTATIONS/core/seven_phase.py` | 8 |
| `lamague_reference.py` | 7 |
| `tests/test_grey_mode.py` | 5 |
| `14_MYSTERY_SCHOOL/implementations/aura_mystery_school_v2.py` | 4 |
| `tests/test_lamague_reference.py` | 3 |
| `grey_mode.py` | 3 |
| `tests/test_seven_phase.py` | 1 |
| `34_CYBERNETICS/loop_audit.py` | 1 |
| `systems/knowledge_genome.py` | 1 |
| `lycheetah_guard_mcp.py` | 1 |

**Decision for Mac:** proposal P6.

### F23 — The default re-entry threshold sits above every unsigned drift (MEASURED, OPEN)

The threshold is `r_merge = exp(−β·Δt_iso)·(1 + γ·ratio)`. With defaults it
measured 1.66–1.69. The old unsigned `psi_r` is bounded by 1, so the re-entry
test could never fail. With signed drift, only a state past orthogonal can fail
it.

`Δt_iso` is measured from the start of `run()`, which is loop time, not time
since isolation began. That makes it wall-clock dependent. Measured: r_merge is
1.3 at 0 s and 0.478 at 2 s. With β per second, a true isolation clock would
make re-entry impossible after about 10 s.

The F22 fix does not depend on this threshold, because convergence also
requires drift below `r_c` (DERIVED from `run()`). **Proposal P4.**

### F24 — One agent is a quorum (MEASURED, OPEN)

An arena with one agent, `worker`, is converged, obstruction-free (trivially)
and Byzantine-safe. The sovereign harness then EXECUTES on its own say. The
Byzantine-safe flag claims a budget that one agent cannot meet. **Proposal P5.**

### G2, G3, G6 — Grey Mode robustness (MEASURED)

- **G2 (fixed):** `recovery_cycle` restored the kernel's coherence only on the
  success path. The restore is now in `try/finally`, and the copy is taken
  unconditionally.
- **G3 (fixed):** `run(max_cycles=0)` raised `UnboundLocalError` on `r_c_new`.
  It now raises `ValueError` for any non-positive or non-integer count.
- **G6 (open note):** the docstring says alerts must be "consecutive", but a
  breach of a single parameter does not reset `alert_count`. Either the word
  or the counter is wrong. The spec `02_AURA_L3/GREY_MODE.md` was not read.

The module header claims "[ACTIVE] — fully implemented from spec". That is a
self-claim and has not been checked against the spec.

## Notes (not defects, or not yet)

- **N1:** a raw `PsiConsensus` result's `converged` ignores the one-third
  Byzantine budget. The arena verdict applies the budget, and callers who read
  the raw result do not get it.
- **N2 (MEASURED):** the same four agents inserted in reverse order took 3
  rounds each. Their consensus vectors differed by at most 3.77e-4 per
  component, and **the digests were not equal**. A verdict digest depends on
  insertion order. Proposal P7.
- **N3:** `PsiConsensus.run()` is stateful. A second run continues from the
  first run's states and Grey Mode counters.
- **N4:** `byzantine_safe` reports a quarantine count within budget. It is not
  a Byzantine fault-tolerance proof.
- **N5:** the sheaf H⁰/H¹ figures use a constant sheaf, so they measure graph
  topology (connected components and cycles), not state agreement.
- **N6:** `seven_phase.py` (around line 436) and the MCP `format_seven_phase`
  (around line 282) use unsigned alignment. They belong to the P6 decision.
- **N7:** `build_consensus` fixes its seed at 42.
- **Pre-existing lint:** `grey_mode.py` imports `Tuple`, which is unused. The
  HEAD version imports it too. It was left alone.

## Leads for RV04 and RV05 (read in full, not yet probed)

From `lycheetah/assurance/gateway.py`:

- The destructive-command check is a substring denylist (`"rm -rf /"`, the fork
  bomb). `rm -r -f /` and `find / -delete` would pass. Any `rm -rf /abs/path`
  would be blocked as a false positive. UNVERIFIED until probed.
- `CommandExecutor` runs string commands with `shell=True`.
- Dispatch re-evaluates policy on `intended_action`, not `live_action`.
  `claim_dispatch` must be the step that verifies the hash match.
- The effect claim precedes `_event_record`, so an exception while recording
  burns the effect (see P2).
- The harness's `_canonical_json` does not pass `allow_nan=False`.

## Proposals for Mac (none applied)

- **P1 — permit v3.** Bind the full packet hash, or a declared field set, so a
  permit names exactly what it authorises.
- **P2 — claim ordering.** Claim a permit or effect only after everything that
  can fail before execution has succeeded. Otherwise, make the claim
  releasable on a pre-execution failure. This applies to the gateway and the
  harness.
- **P3 — recovery as resubmission.** Recovery writes the agent's new vector
  inside the arena, so the arena authors an agent's position. Emit the
  recovered vector as a candidate that the agent must resubmit.
- **P4 — r_merge redesign.** Count Δt in deliberation rounds from isolation
  entry, not in wall-clock seconds from `run()`. Then cap or rescale r_merge
  against `r_c` so the threshold can bind.
- **P5 — quorum.** Add a harness `min_agents`, and tie it to the claimed budget:
  tolerating f faulty agents needs n ≥ 3f + 1, so 4 agents for f = 1 (DERIVED,
  standard BFT bound). This supersedes the "3" I suggested in chat.
- **P6 — TRIAD sign semantics.** Choose rays or vectors. If rays, consensus and
  Grey Mode must be sign-free end to end. If vectors, `detect_drift` and
  `anchor_operator` become signed, and the census above migrates together.
- **P7 — canonical edge order.** Iterate agents and neighbors in sorted order,
  so a verdict digest does not depend on insertion order.

## Tests added

- `tests/test_sovereign_binding_gaps.py`: 3 tests (F11, F12, F13 witness).
- `tests/test_consensus_anchor_and_registration.py`: 20 tests, counting the
  parametrised cases (F14–F22, G3), with a benign control beside each refusal.

## Verification (MEASURED)

**Planted failures:**

| Run | Result |
|-----|--------|
| RV02 tests vs HEAD harness and gateway | 3 failed |
| RV03 tests vs HEAD `psi_consensus`, `arena` and MCP | 16 failed, 1 passed |
| Same, after restore | 17 passed; `cmp` identical ×3 |
| F22/G3 tests with the two Grey Mode repairs reverted | 2 failed, 2 passed |
| Same, after restore | `cmp` identical |

The one RV03 pass on HEAD was the benign control. Both passes in the Grey Mode
run were controls: the orthogonal recovery, and the F20 test.

**Focused suites:** 11 files (consensus, Grey Mode, Psi, integrity, MCP guard,
harness, binding gaps, sheaf factorial, LAMAGUE reference, seven phase): 166
passed, 1 skipped.

**`repro_batch2.py`:**

| Findings | Working tree | HEAD export |
|----------|--------------|-------------|
| F11, F12, F14–F22 | `reproduced` false | reproduced |
| F13, F23, F24 | true (by design or open) | reproduced |

On HEAD, F14 and F24 both reached `EXECUTED` with the executor called. F22
reported `psi_r = 0.0` for a final state of `[-1, 0, 0]`, and F23 measured
r_merge = 1.6692.

**AST unused-import check:** clean on every edited file except the
pre-existing `Tuple`, which HEAD imports and never uses.

Full suite on the Batch 2 tree, MEASURED 2026-10-22 (`python3 -m pytest -q`, whole collected
suite): **1175 passed, 1 skipped, 1 xfailed, 0 failed** in 365 s, exit 0. Baselines: 3 failed /
1144 passed before Batch 1; 2 failed / 1150 passed after Batch 1. `tests/test_guarded_handoff_bundle.py`
is inside that collection.

## Coverage ledger (Batch 2)

Read in full: `lycheetah/assurance/gateway.py`,
`lycheetah/sovereign_harness.py`, `lycheetah/consensus/arena.py`,
`12_IMPLEMENTATIONS/core/psi_consensus.py` (across two sessions),
`12_IMPLEMENTATIONS/core/grey_mode.py`.

Read in part:

| File | Lines |
|------|-------|
| `12_IMPLEMENTATIONS/core/lamague_reference.py` | 60–234 |
| `12_IMPLEMENTATIONS/applications/lycheetah_guard_mcp.py` | 262–300, 320–400 |
| `tests/test_consensus.py` | 78–150 |
| `tests/test_consensus_integrity.py` | full |
| `tests/test_sovereign_harness.py` | 268–300 |
| `codec.py` | 20–226 |
| `shield.py` | 36–246 |
| `examples/meaning_handover/demo.py` | 160–280 |

Not reviewed: every other folder, including all of Appendices A–F.
The frozen sources and the evidence bundle
`34_ASSURANCE_RUNTIME/evidence/guarded-handoff-risk-2026-10-18/` were not edited.
