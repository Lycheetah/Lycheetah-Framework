# Lycheetah Compensation Race Benchmark v0.1

**Evidence footing: [SCAFFOLD] research, proposal or source review. Supplied and local synthetic results retain their stated limits; no independent validation or production claim.**

**Status:** public engineering experiment. Not a safety proof, patent claim, or production deployment.

This small benchmark demonstrates a temporal failure mode in automated compensation/rollback systems:

> A repair decision can be justified when it is computed and still be unsafe when it is executed.

If a controller checks resource versions, releases control, and later writes restoration values, another legitimate writer can modify a target in the gap. A second common pattern—checking and repairing targets one at a time—can leave a partial rollback when a later target is stale.

The benchmark compares three deliberately simple strategies:

1. **Precheck then write** — all targets match at an earlier snapshot, then restoration is written later without revalidation.
2. **Sequential per-item compare-and-set** — each target is checked and repaired independently.
3. **Atomic commit-fenced repair** — all target versions and content hashes are checked in the same write transaction that applies all restoration values; any mismatch produces zero repair writes.

The third strategy is conventional transaction/concurrency-control engineering. Lycheetah does **not** claim commit-time validation, optimistic concurrency, compare-and-set, or atomic transactions as novel.

## Core invariant

For exact repair set `R`, automatic compensation commits only if, at the resource-owner commit point:

```
for every r in R:
    current_version(r) == expected_version(r)
    current_hash(r)    == expected_hash(r)
```

Only after **all** comparisons pass may restoration be applied, and application is all-or-none over `R`.

If one comparison fails:

```
repair_writes = 0
```

This benchmark intentionally does **not** publish Lycheetah's private causal-attribution or repair-legality mechanisms. It isolates one generally useful concurrency lesson.

## Reproduce

Requires Python 3.11+ and only the standard library.

```bash
python -m unittest discover -s tests -v
python -m compensation_race.benchmark --rounds 1000 --output reports/STRESS_RESULTS.json
```

## Frozen v0.1 result

Across 1,000 deterministic rounds per case:

- precheck-then-write overwrote a legitimate post-permit update: **1,000/1,000**;
- sequential per-item repair left a partial rollback: **1,000/1,000**;
- atomic commit-fenced repair refused the stale repair with zero writes: **1,000/1,000**;
- atomic commit-fenced partial repairs: **0/1,000**;
- clean atomic repairs succeeded: **1,000/1,000**.

These are purpose-built deterministic fixtures, not estimates of real-world failure rates.

## Why this exists

Agent systems increasingly perform real mutations rather than return text. Recovery logic therefore needs the same temporal discipline as ordinary transactional software. An offline verifier can issue a **conditional repair permit**, but the resource owner must revalidate its exact conditions at the commit linearization point.

See `SOURCES.md` for conventional references.

[Local rerun and manifest boundary](LOCAL_VERIFICATION.md) distinguish incoming reports from the current public experiment.
