# Held-Out Benchmark Protocol

## Question

Can a bounded LAMAGUE semantic codec reduce transmission size while preserving
declared consequential meaning exactly and detecting constructed unsafe collapse?

## Frozen corpus

```text
36 synthetic structured packets
18 application domains
2 packets per domain
```

The first 24 packets form the dictionary-training split.

The final 12 packets are held out from dictionary construction.

## Baseline

Canonical minified JSON measured in UTF-8 bytes.

## Conditions

1. `L1`: compact schema without shared dictionary.
2. `L1D warm`: shared dictionary already present.
3. `L1D cold`: compressed packets plus one-time codebook transmission cost.

## Fidelity tests

- exact canonical packet equality;
- full SHA-256 equality;
- critical SHA-256 equality.

## Mutation tests

Each packet receives nine constructed mutations:

```text
drop unknowns
remove unknown protection
drop authority
drop affected parties
drop dissent
drop value flow
drop recovery
change an invariant
remove Guard from the operation path
```

Expected classifications are frozen before execution.

## Claim boundary

A perfect result verifies deterministic software behavior on this constructed
corpus. It is not evidence of unrestricted prose comprehension, human semantic
agreement, cross-model equivalence, or external adversarial robustness.
