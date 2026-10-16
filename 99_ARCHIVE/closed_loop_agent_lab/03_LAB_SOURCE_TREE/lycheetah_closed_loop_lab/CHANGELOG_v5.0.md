# Changelog v5.0 — Bounded-Cardinality Overflow Buckets

## Purpose

The v4.9 hierarchical attempt-rate quota implementation bounds ordinary tracked buckets, but under cardinality pressure new sources could fail to obtain individual peer/aggregate rows. v5.0 adds a fixed-size, keyed overflow-shard path so untracked sources share bounded fallback counters rather than obtaining unlimited per-source state or being denied solely because the exact-bucket table is full.

## Local verification

- Direct unittest rerun: **50 tests passed**.
- Log: `r40_bounded_cardinality_overflow_v5_0/test_output_v5.0_reverified.log`.

## Boundaries

- Local reference implementation, not production certification.
- Hash-shard collisions deliberately aggregate sources and can cause conservative false-sharing.
- The overflow key must be high entropy and consistent across cooperating processes.
- Run the full current v5.1 suite before promoting the v5.0 source by itself.
