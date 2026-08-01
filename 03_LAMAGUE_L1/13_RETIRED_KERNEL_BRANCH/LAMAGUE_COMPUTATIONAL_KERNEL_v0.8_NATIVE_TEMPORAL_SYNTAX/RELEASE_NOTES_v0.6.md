# Release Notes — v0.6.0

## Added

- semantic equivalence benchmark engine;
- field-level precision and recall;
- six result classes;
- synthetic corpus of 20 reference cases;
- 200 deterministic candidate packets;
- unknown, authority, affected-party, dissent, value-flow, recovery, and invariant-loss mutations;
- benchmark CLI;
- corpus card;
- red-team track;
- benchmark regression tests.

## Verification

```text
Kernel and benchmark tests passed: 39
Seed label matches: 200 / 200
Benchmark accuracy against constructed labels: 1.000
```

## Evidence boundary

The benchmark corpus is synthetic.

It verifies the measurement machinery before external blind submissions are collected.
