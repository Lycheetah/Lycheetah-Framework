# Rewrite Trace Specification

A rewrite trace explains why a surface expression reached its canonical form.

Trace rules are deterministic and ordered by evaluation.

## Current rules

```text
DERIVED_ATOM_DECOMPOSITION
REFERENCE_EXPANSION
FUSION_ASSOCIATIVE_FLATTEN
FUSION_COMMUTATIVE_SORT
PROJECTION_ASSOCIATIVE_FLATTEN
EXCHANGE_SYMMETRIC_ORDER
```

The absence of a trace rule is meaningful.

There are deliberately no core rules for:

```text
collapse inversion
ascent inversion
recurrence unrolling
null annihilation
identity removal
duplicate removal
domain causality
```
