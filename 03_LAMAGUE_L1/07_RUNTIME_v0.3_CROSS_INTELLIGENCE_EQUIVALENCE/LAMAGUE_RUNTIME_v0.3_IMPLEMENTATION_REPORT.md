# LAMAGUE Runtime v0.3 — Implementation Report

## Milestone

Runtime v0.3 creates the first bounded testing harness in this project for the question:

> Can one protected meaning cross multiple intelligence architectures and return without silent loss?

The harness does not answer that question by assertion. It creates a reproducible experiment for collecting the evidence.

## Semantic packet

Each decoder must return a structured packet containing:

- purpose;
- claim;
- primitive operation path;
- invariants;
- unknowns;
- authority;
- participants;
- affected parties;
- evidence;
- provenance;
- dissent;
- value ledger;
- consequences;
- horizon;
- recovery.

Decoder identity is deliberately excluded from the semantic hash.

## Two hashes

```text
semantic hash
    all canonical semantic fields

critical hash
    purpose + invariants + unknowns + authority
    + participants + affected parties + dissent + value flow
```

This makes surface variation visible without confusing it with protected semantic equivalence.

## Loss rules

The following produce `UNSAFE_COLLAPSE`:

```text
unknown disappears
authority disappears
participant disappears
affected party disappears
dissent disappears
value flow disappears
```

Purpose or invariant changes produce `DIVERGENT`.

Safe extensions remain visible as `PARTIAL_EQUIVALENT` rather than being forced into exact identity.

## Consensus

The harness clusters decoders by critical hash and reports:

```text
SAFE_CONSENSUS
SAFE_MAJORITY_WITH_DISSENT
SPLIT
NO_SAFE_CONSENSUS
```

Every unsafe or divergent decoder remains in the report.

## Included benchmark

Five cases test:

1. incomplete evidence and protected uncertainty;
2. coordination without false consensus;
3. declared and consented value exchange;
4. descendant migration with a new unknown;
5. breathing expansion under weak decoder confidence.

The bundled decoder outputs are simulations for software verification only.

## Validation boundary

Runtime v0.3 proves that the comparison machinery behaves as designed under deterministic tests.

It does not yet prove:

- actual cross-model equivalence;
- human learnability;
- inter-rater reliability;
- net communication compression;
- robustness across languages;
- resistance to prompt gaming.

Those require independent decoder outputs collected under the blind protocol.
