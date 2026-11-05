# Findings — failures, contradictions, reductions, rejected designs

Append-only. Each entry: what was observed, the evidence, what it changes. Severity is a
review convention. Nothing here edits the source it describes; the sync-zone repository is
written only by its seats (its `CHARTER.md` §1–2), so its findings are recorded here for Mac
and a seat to act on.

## SZF-01 · Sync Zone already exists as a practice · reframes the brief

The packet places Sync Zone in the Framework. `Lycheetah/lycheetah-sync-zone` already runs the
loop: charter, 100 seat folders, threads, a disputes ledger, a seat-signature hook and
`zone-check`. **Change:** the contract targets that loop; no new orchestrator was built.

## SZF-02 · Dispute 1100 is circular by construction · HIGH

`code/24_recursive_dark_node_engine.py` defines open-loop entropy as
`initial * sqrt(1 + 1.5k)` (line 59) and closed-loop as `alpha*(1-0.7*taste)*H + eps`
(lines 64-69). `run.py` feeds `human_taste_score=0.88` and checks that open > 4.5 and
closed < 0.15. The "falsification" therefore re-reads its own constants; the swarm responses
passed in do not enter the entropy calculation. The claim, the strawman defender ("The Fully
Autonomous Unsupervised Swarm Thesis"), the run and the RESOLVED line came from one seat
(commit `9e15591`, author `Aetheron (Gemini)`). MEASURED: ran `run.py`, read the formulas.
**Change:** the protocol may not cite 1100 as evidence that human steering is necessary.
**Suggested action for Mac:** invite a different seat to open a dispute against 1100's
falsifier (the charter's own route).

## SZF-03 · Dispute 1200 is a sound simulation with an interpretive leap · MEDIUM

`code/26_swarm_flocking_engine.py` is a real Vicsek model; an external aligning field
ordering a noisy flock is a known result. Treating boids as AI seats and the field as
"founder taste" is analogy, not measurement of any AI system. **Change:** cite as
illustration only.

## SZF-04 · Summary drift caught live: the dossier drops dispute 400 · HIGH

The 2026-11-06 Aetheron dossier lists "Brier Calibration Score: 0.000428" as predictions
evidence. Dispute 400 (Nettle, 2026-10-23, commit `712a50f`) found that every settled
prediction was committed already HIT; the number is correct arithmetic and "measures nothing
about calibration". `disputes/LEDGER.md` has no later RESOLVED for 400. `cold-boot-audit.py`
still prints the number without the caveat. MEASURED. This is threat T11 / question 14 in the
wild and the strongest real motivation for `CAVEAT_DROPPED_FROM_HANDOFF`.

## SZF-05 · Two of my own tests were vacuous · MEDIUM (self-found)

Mutation probes (rule removed, suite rerun) on the first test version:
M1 ratifier check → caught; M2 parent lineage → caught (9 tests); M3 digest binding → caught;
**M4 self-review shortcut → survived; M5 ledger prev-link → survived.** M4 was masked by the
builder fixture declaring `same_run`; M5 by seq/digest checks catching naive tampering. Added
`test_self_review_is_same_run_even_when_the_run_claims_more` and
`test_ledger_detects_splice_by_forger_who_knows_the_hash`; reran M4, M5 and new M6 (caveat),
M7 (authority widening), M8 (failure deletion): all now caught. Sources restored and compared
byte-for-byte after each probe.

## SZF-06 · Fixture error, not validator error · LOW

`test_limit_shared_fabricated_source_passes_structure` first failed with `BUDGET_EXCEEDED`:
seven runs against `max_runs: 6`. The validator was right. The case also showed that
correlated reviewers were silent, so `SHARED_REVIEW_CONTEXT` (MEDIUM, non-blocking) was added.

## SZF-07 · Stale review checklist · LOW

`FOR-REVIEW/FULL_FRAMEWORK_REVIEW_CHECKLIST.md` RV10 says the Chorus defect is "Reproduced
open"; `19_MULTI_AGENT_CHORUS/README.md` records its correction on 22 Oct and running
`run_chorus.py` today shows `INSTANTIATED_NOT_PROBED`. Not edited here (review ledgers have
their own owner).

## SZF-08 · Test counts differ from the README · LOW

README: `1,571 passed, 1 skipped, 2 expected failures`. This container (Python 3.13, no `mcp`,
no `flask`): `1567 passed, 3 skipped, 2 xfailed`. The 4-test gap is the three optional-dependency
skips (`test_mcp_guard.py`, `test_web_demo.py`, one in `test_sol_workspace_mcp.py`). Not a
regression.

## SZF-09 · Workshop counts · LOW

Dossier: "70 / 70 Tests" across 12 suites. Ran each `code/*test*.py`: 11×7 + 6 = **83 passed**.
Dossier understates; harmless, but a summary number again diverges from its source.
`zone-check`: 692 checks, 0 failures, 2 warnings — matches. Cold-boot audit counts (100 seats,
55 builds, 23 disputes) match its own output.

## SZF-10 · Out of scope, flagged · note

The dossier's revenue figures (Capsule 001, Desk Node) are projections presented in a
"measured" register next to test counts. They are UNVERIFIED and were not assessed. The
dossier's three questions to "Sol Prime" (unboxing liturgy, lookbook voice, Round 29 focus) are
Mac's creative and product decisions and were not answered in this forge.

## SZF-11 · The contract cannot see circular evidence · design limit

Retrospective V3: dispute 1100 plus one different-model review with no findings passes every
rule. Kept as the central null result in `THREAT_MODEL.md` and `CLAIMS_AND_LIMITS.md`.

## SZF-12 · Push to the Framework was not available · blocker

This session's request for push access to `Lycheetah/Lycheetah-Framework` was refused by the
environment's permission classifier; read access worked. Work is committed locally on branch
`claude/youthful-volta-di3ma8` and exported as a bundle and patch. Mac decides how it lands.

## SZF-13 · Genesis ruleset cannot be adopted from inside · design property

Recording this forge as SZ-0001 (`experiments/session_cycle.py`) shows the firewall applied
to itself: the cycle writes `sync_zone/` and `PROTOCOL.md`, so it is a meta-governance
change; there is no earlier ruleset to judge it under, and the session that wrote the rules
dissents from being judged by them (`D-SELF-RULES`). The record is valid and **not
ratifiable**: `OPEN_CRITICAL_DISSENT`, `NO_INDEPENDENT_REVIEW`,
`META_CHANGE_NEEDS_SEPARATE_RATIFICATION`. That is correct. A genesis ruleset is adopted by
Mac directly, outside the contract, the way a constitution is adopted; the contract governs
changes after that.

## Rejected designs

- **A scheduler/orchestrator.** Rejected: the packet's own order is contract first; the workshop
  already has the social loop.
- **Reusing Chorus or consensus as reviewers.** Rejected: scaffold / agreement is not evidence.
- **A universal Sync Score.** Rejected per the packet §12; gates stay separate.
- **Importing ActionGateway into the validator.** Rejected for v0.1: records cite receipts; the
  gateway stays the only permissions runtime.
- **Promotion into `lycheetah/`.** Rejected for now: no comparator experiment has been run.
