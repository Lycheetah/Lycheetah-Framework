# LAMAGUE v0.7 Temporal Evidence Benchmark

## Purpose

Verify that the bridge detects constructed losses and preserves scope boundaries.

## Frozen cases

```text
T001 stable control
T002 value conflict
T003 unit conflict
T004 operator conflict and persistent drift
T005 missing intent restraint
T006 black-box compliant mimic
T007 boundary breach and recovery
T008 invariant failure under low numerical drift
```

## Current evidence boundary

The included cases are synthetic and deterministically generated.

An 8/8 match proves that the reference implementation reproduces its frozen expected outputs.

It does not measure independent model or human performance.

## External phase

The next empirical stage requires untouched external outputs under a preregistered prompt and scoring protocol.
