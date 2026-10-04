# Local integration verification — 4 October 2026

**Status: MEASURED local synthetic engineering observations; SCAFFOLD candidates, not deployed.**

The logs under [local-verification/](local-verification/) distinguish source-reported results from reruns on this host. None are independent external replications. The first three drivers ran from an isolated copy after packaging adapters were added and before callback-binding lint clarification; later drivers used the subsequent source tree. Original report bytes are retained alongside their source manifests.

| Component | Local witness | Limit |
|---|---|---|
| 01 commit-time authority | 8/8 scripted cases, 341/341 bounded traces, 64 races with zero observed violations | SQLite model; conventional generation fencing expected to tie |
| 02 shared resources | Supplied driver completed; shared-resource thread/process probes met its declared expectations | Historical supporting research; the public v0.4 live-authority repair remains canonical |
| 03 atomic authority/resource finality | Supplied driver completed; 259/259 bounded traces, 64 races with zero observed violations | One local serialization boundary; intentionally weak dual-write counterexamples retained |
| 04 dependency evidence | 10/10 scripted cases; 8 race trials, zero observed violations | Full driver exceeded 75 seconds; its exhaustive trace claim was not reproduced here |
| 05 hazard coverage | 11/11 scripted cases; 8 race trials, zero observed violations | Full exhaustive boolean model was not rerun; supplied broader results remain historical |
| 06 policy evolution | 10/10 scripted cases, 64/64 semantic classifier cases | Same-programme self-authored fixtures |
| 07 mutation museum | Initial 19/30 mutants killed; augmented 30/30; all 30 have a synthetic counterexample | This score covers the declared mutant set, not arbitrary faults; incoming report had a stale source digest |
| 08 threat boundary | Replacement reproducer matched its declared 12 packets, 46 removals and 64 finite classifications | Original driver and extended report absent; coverage labels do not test hostile execution |

## Native runtime candidates

The integration adds four regressions to the twelve supplied finality tests: empty evidence after recomputed witness digest, a provider returning the wrong key, non-string record fields and re-evaluation with the real Assurance Runtime. The five execution-cell tests use temporary workspaces. The first local attempt exposed an assumption that socket creation would succeed; the fixture now catches refusal at creation as well as connection. This preserves the blocked-network expectation instead of weakening it.

The complete non-conjecture suite passed 695 tests before final package-quality edits. Final rerun counts, lint, type, source and wheel checks are recorded in the Framework [publication receipt](../../PUBLICATION_2026-10-04.md). The native package retains SCAFFOLD status. This host also restricts network access, so a blocked connection in a cell is not independently attributable to namespace isolation alone.

The finality digest is not authenticated admission. The caller must protect witness/evidence sources and enforce REVIEW. The execution cell has no seccomp/cgroup guarantee and does not hide arbitrary readable host files. No provider call, real deployment, independent security review or safety superiority was performed.
