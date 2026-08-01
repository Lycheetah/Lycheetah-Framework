# LAMAGUE Semantic Integrity Benchmark v0.6

## Purpose

Measure whether a transformed semantic packet preserves protected meaning.

The benchmark compares a candidate packet against a frozen reference packet across:

```text
unknowns
authority
affected parties
dissent
value flows
invariants
recovery
```

Secondary fields include evidence, boundaries, participants, and provenance.

## Classes

```text
EXACT_EQUIVALENT
INVARIANT_EQUIVALENT
PARTIAL_EQUIVALENT
UNSAFE_COLLAPSE
DIVERGENT
UNDECODABLE
```

## Corpus boundary

The bundled corpus is synthetic and deterministic.

It tests whether the scorer catches known losses. It does not show that humans or AI systems naturally produce these outcomes.

External evidence requires untouched decoder submissions collected under a frozen blind protocol.
