# Batch 21 — RV22 Agent-Safety Continuations: Findings and Ledger

**Reviewer:** Sol (Claude Opus 5.5, xhigh) · **Date:** 2026-10-22
**Branch:** `review/full-framework-2026-10-20` @ `d7ae0ad` · working tree only, nothing committed
**Scope:** the seven continuation homes under `papers/agent-safety/`: simulator, compensation-race-benchmark, earned-light, earned-trust, frontier-controls, sovereign-choice-research. Also included: `papers/ai-futures/hybrid-gateway/` and the `35_ABSTRACT_AND_GENERATIVE/SOVEREIGN_WILL/` handoff that cites them.
**Reproduce:** `python3 -B FOR-REVIEW/2026-10-22_OPUS_REVIEW/repro_batch21.py . <scratch> [--suites]`

## Coverage

Every suite was run from a `git archive HEAD` copy in scratch, never in the repository. Every manifest was recomputed byte for byte. No label was inherited from a README.

| Home | What was run | Result | Label |
|---|---|---|---|
| earned-light | `verify.py` (Forges 02–07) | 207 test executions, all passed, `skips_reported: false` | MEASURED |
| sovereign-choice-research | `verify.py` | 207 = forge_ii 28 + forge_iii 37 + archived IV–VIII chain 142 (32 new + 110 prior) | MEASURED |
| hybrid-gateway v1.2 | `verify_release.py`, `pytest tests`, `demo_sql_comparison.py` | VERIFIED 137 files · 264 passed, 43 subtests · SQL 4 = gateway 4, latest-known 2 | MEASURED |
| simulator | `pytest tests` | 63 passed, 149 subtests. README cites 53 for the original v0.3 run | MEASURED |
| compensation-race | unittest, benchmark at 1000 rounds | 5 OK · weak overwrites 1000, sequential partial repairs 1000, atomic stale refusals 1000 | MEASURED |
| earned-trust cycles 001–009 | `verify_release.py`, `--tests`, integration bridge | 132 manifest entries, 64 files parsed · C001–C009 ran 378 tests, **9 of them skipped** · bridge 5 OK | MEASURED |
| frontier-controls 01–08 | maintained manifests, drivers | INTEGRATION_MANIFEST 75/75, all component `SHA256SUMS.json` OK · drivers: see Verification | MEASURED |
| every manifest in scope | recomputed | see F3, F5, F6 | MEASURED |

## Findings

**F1 — The Earned Trust release runner counts skipped tests as passing. [MEASURED, frozen file → staged patch]**
`papers/agent-safety/earned-trust/cycles_001_009/verify_release.py` reads `Ran N tests` from unittest output and prints the sum as `Selected locally-authored suites: 378 passing tests`. unittest counts a skipped method as run. On an ordinary-user host, Cycle 009 reports `OK (skipped=9)` because its privilege-drop tests skip, but the runner still prints 378 passing. The true figure on this host is 369 passed and 9 skipped. The earned-trust README already says the 378 is the privileged-environment figure, so the prose is honest and only the tool's own output overclaims. The runner is one of the 148 files pinned by the 2026-10-18 intake manifest, so it was not edited. The fix is staged as `RV22_earned_trust_skip_count.patch` (+8 −4) by `stage_rv22_patches.py`. The patch keeps the exact-count gate (`count != EXPECTED[i]`) unchanged, and only reports passes and skips separately.

**F2 — The Sovereign Will validation note names the wrong forges. [MEASURED, fixed by an inline note]**
`VALIDATION_AND_LIMITATIONS.md:10` says the 142-test chain ran "through Forges II–VII". The chain is Forge VIII's 32 tests plus 110 historical tests. Those 110 are Forge IV 28 + V 23 + VI 36 + VII 23 (`forge_vii/results/verification.json`: 23 + 87 lineage = 110), and `forge_viii/run_verification.py:55` requires exactly 110. Forges II (28) and III (37) are not in it. A dated correction now follows the bullet, and the handoff bullet is kept as written.

**F3 — Eight superseded Hybrid Gateway manifests sat unexplained beside the live one. [MEASURED, fixed by an inline note]**
`v1.2/SHA256SUMS_v0.2` … `_v0.9` have 4–7 entries each that no longer match (ok/non-matching: 12/4, 22/5, 32/7, 47/6, 67/5, 77/4, 93/4, 102/4). Only `SHA256SUMS.txt` (137/137) describes the current tree. Nothing said so. A reader running `sha256sum -c` on an old one would see failures and conclude that the release was tampered with. The wrapper README now says this in a dated note. The intake wrapper's required `**[SCAFFOLD]` and "experimental" wording is untouched, and `tools/verify_research_intake.py` still passes.

**F4 — Earned Trust Cycle 009 tests fail when TMPDIR is a long path. [MEASURED, environmental]**
Cycle 009 binds AF_UNIX sockets under `TMPDIR`, and the Unix socket path limit is about 108 bytes. With TMPDIR set to the session scratch path, the same 47 tests report `FAILED (errors=9, skipped=1)`, all nine errors `OSError: AF_UNIX path too long`. With TMPDIR set to `/tmp/claude-1000/rv22s`, they report `OK (skipped=9)`. The working directory does not matter; TMPDIR does. This is a portability hazard for CI runners with deep temp directories, not a logic defect. The long-TMPDIR run is recorded as DID NOT RUN, not FAILED. Note that the error path also changes the skip count (1 instead of 9): the errored tests never reach their skip guard.

**F5 — Historical source manifests do not verify the current tree, and their documentation says so. [MEASURED, no change]**
Frontier `SOURCE_SHA256SUMS.json` (bad, missing): 01 (3,1), 02 (2,2), 03 (4,1), 04 (2,0), 05 (2,0), 06 (1,0), 07 (2,0), 08 (0,2). These are documented in `frontier-controls/PACKAGING_RECONCILIATION.md:9,15`. Simulator `reports/artifact-manifest.json`: 16 ok, 12 non-matching. `VERIFICATION.md:3,48` labels it the historical v0.3 receipt. Compensation `SOURCE_MANIFEST.sha256`: only `README.md` differs, which `LOCAL_VERIFICATION` documents. All three are pinned in C3 so that silent drift would show.

**F6 — Earned Light intake: every recorded byte survived the import. [MEASURED]**
The intake manifest lists pre-import paths, so only 4 entries match in place. All 86 recorded digests exist somewhere in earned-light/ or in the Mythos library. The two stories moved to `LYCHEETAH_MYTHOS/SCRIPTURES_AND_STORIES/TEXTS/ORIGINAL_NARRATIVES/` with identical hashes, and `earned-light/README.md:48–49` links them there. The `story/` links in `intake/README.md:12–13` are broken, but that README is preserved pre-publication wording (its line 42), so it is left as history.

**F7 — No test or CI covered five of the seven continuations. [MEASURED, fixed with a new test]**
`tests/test_research_intake.py` pins only Earned Trust and Hybrid Gateway. `.github/workflows/agent-safety.yml` runs only the simulator and the compensation benchmark. Frontier Controls, Compensation's own manifest, Earned Light and Sovereign Choice could drift without anything failing. NEW `tests/test_agent_safety_continuations.py` (4 tests) adds:
- the maintained manifests: frontier INTEGRATION_MANIFEST plus 8 component SUMS, compensation MANIFEST, 6 earned-light forge SUMS;
- byte survival for the earned-light intake;
- the 7 sovereign forge manifests, with the documented `lineage/` omission excluded;
- a guard that `lycheetah/` imports none of the continuations.

Each test was witnessed failing under a planted defect (C2), and an unknown manifest shape is refused rather than skipped.

**F8 — Every preserved negative or neutral result is still in its result file. [MEASURED]**
- Earned Trust C009: the conventional provider agrees on 15/15 cases.
- Earned Light Forge_02: the EAC still lets 2/33 unauthorized effects through and blocks 2/10 benign tasks.
- Forge_05: the conventional JSON ties on every task.
- forge_vii: the standard arm ties the sovereign arm at 18/18, with `baseline_parity: true`.
- forge_viii: 7 of 8 matched pairs differ, with 1 negative control, on fictional fixtures.
- Hybrid: SQL ties the gateway 4/4.

Nobody softened them. C7 pins each one.

**F9 — No continuation has been promoted into the runtime. [MEASURED]**
Nothing in `lycheetah/` imports the continuations (now guarded by F7). `lycheetah/assurance/finality.py` and `execution_cell.py` are native implementations labelled [SCAFFOLD]. `pyproject.toml` mentions earned-trust and hybrid only in lint per-file ignores.

**F10 — The 2026-10-19 intake record is now stale for one file. [DERIVED]**
`28_DEFENSE/RESEARCH_INTAKE_2026-10-19_SOURCE_MANIFEST.json` records a `current_sha256` for `VALIDATION_AND_LIMITATIONS.md`. The F2 note changes those bytes. No test or tool enforces the 10-19 manifest; `test_research_intake.py` and `verify_research_intake.py` read only the 10-18 manifest, so nothing goes red. The record itself is a dated canonical receipt, so it was not re-minted silently. See G-INTAKE-1019-RECORD.

**F12 — Frontier drivers 01–05 rewrite a manifested file on every run. [MEASURED]**
Running the documented `benchmark.py` in components 01–05 rewrites `reports/report.json`, and the new bytes no longer match that component's `SHA256SUMS.json`. The counts in it depend on how a thread race interleaves. In 01 one rerun moved `commit_ordered_first` from 16 to 19 and `revoke_ordered_first` from 48 to 45. Components 06, 07 and 08 reproduce byte for byte. So the committed report is one sample of a nondeterministic run, not a fixed result. Anyone who reruns a driver in place will turn `test_agent_safety_continuations.py` red, honestly. The drivers were run only in a HEAD copy. Whether the README says the report is one sample was not checked in this batch, so that is UNVERIFIED. See G-FRONTIER-REPORT-SAMPLE.

**F11 — The simulator README header says "Version 0.2" inside the v0.3 packet. [MEASURED, minor]**
Left unchanged. See G-SIM-VERSION-LABEL.

**Count hygiene. [MEASURED]** No document in scope adds overlapping counts together. The sovereign README and `verify.py` label the 207 as executions that include the archived chain.

## Writes

| Path | Kind | Why |
|---|---|---|
| `tests/test_agent_safety_continuations.py` | NEW, 4 tests | F7 |
| `papers/ai-futures/hybrid-gateway/README.md` | dated review note | F3 |
| `35_ABSTRACT_AND_GENERATIVE/SOVEREIGN_WILL/VALIDATION_AND_LIMITATIONS.md` | dated correction, original bullet kept | F2 |
| `FOR-REVIEW/2026-10-22_OPUS_REVIEW/stage_rv22_patches.py` | patch generator | F1 |
| `FOR-REVIEW/2026-10-22_OPUS_REVIEW/RV22_earned_trust_skip_count.patch` | staged, NOT applied | F1 |
| `FOR-REVIEW/2026-10-22_OPUS_REVIEW/repro_batch21.py` | reproduction | all |
| this ledger | record | all |

## Verification

- `repro_batch21.py` static: **37 PASS, 0 FAIL**.
  - C1: the new functions are clean on the tree.
  - C2: the control is clean; five planted defects are each caught; an unknown shape is refused; the copy is clean after restore.
  - C3: historical manifest counts are pinned.
  - C5: the 23 + 87 = 110 composition and the `==110` gate.
  - C6: the patch applies to the HEAD runner and compiles.
  - C7: preserved results.
  - C8: the intake wrapper still passes.
- `repro_batch21.py --suites`: **54 PASS, 0 FAIL, 0 DID NOT RUN**.
  - C4 results: earned-light test_executions 207 · sovereign Ran 28, 37, 28, 32 with all_passed · hybrid 137 files and 264 passed · simulator 63 · compensation 5 plus the 1000-round values.
  - Earned-trust HEAD runner prints `378 passing tests`. The patched runner prints `369 passed, 9 skipped (378 run); a skip is not a pass` (non-root host).
  - Frontier 01–08 drivers all exit 0, with manifest drift in 01–05 (F12).
- Earlier run of the same command: 3 FAIL. Two were caused by the long TMPDIR (F4), with C009 failing on both the HEAD and patched runners. The third was the repro's own parser: it summed `Ran N` lines, but earned-light forges mix unittest and pytest output, giving 89. The parser now reads the verifier's own `test_executions`. Both causes were diagnosed before the rerun; the earlier FAILs are kept here and not erased.
- Patch staging: diff against `git show HEAD:` bytes; `patch -p1` on a HEAD copy; filecmp matches; no CR bytes.
- Full suite (once, after all RV22 writes): **1501 passed, 1 skipped, 1 xfailed, 1 warning** in 137 s — baseline 1497 + the 4 new continuation tests. MEASURED.

## Decisions for Mac

- **G-ET-SKIP-COUNT.** Apply `RV22_earned_trust_skip_count.patch` and re-mint that one file's digest in the 10-18 intake manifest in the same dated change? **Sol: yes.** A verifier that turns a skip into a pass is the exact upgrade-by-rhetoric this repo forbids, even when the README hedges it.
- **G-INTAKE-1019-RECORD.** Re-mint `current_sha256` / `changed_since_import` for `VALIDATION_AND_LIMITATIONS.md` in the 10-19 manifest, or leave the record as the 10-19 snapshot? **Sol: re-mint with a dated note.** The manifest's own fields exist to track post-import change.
- **G-CI-CONTINUATIONS.** Extend `.github/workflows/agent-safety.yml` to run the earned-light, sovereign-choice, earned-trust (`--tests`) and hybrid verifiers? **Sol: yes, after G-ET-SKIP-COUNT.** Run earned-trust from a short working directory (F4), and use the fixed runner so CI prints 369 + 9 skipped rather than 378 passing on a non-root runner.
- **G-FRONTIER-REPORT-SAMPLE.** Drivers 01–05 overwrite a committed, manifested report with a run-dependent sample (F12). Options: (a) add `--output`, defaulting outside the tree, so the committed report stays a dated sample; (b) say in each README that the report is one sample and the counts vary per run; (c) leave it. **Sol: (b) now and (a) when the code is next touched.** These are frozen intake files, so either change needs a re-mint of the manifest.
- **G-SIM-VERSION-LABEL.** Change the simulator README header to v0.3? **Sol: yes, trivial.** Held only because `simulator/README.md` is an entry in the historical v0.3 `artifact-manifest.json`, and changing it is a choice about that receipt, not a typo fix.
