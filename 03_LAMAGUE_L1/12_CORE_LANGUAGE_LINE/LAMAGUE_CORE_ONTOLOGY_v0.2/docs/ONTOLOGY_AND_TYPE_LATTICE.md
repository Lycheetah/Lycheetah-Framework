# Ontology and Type Lattice

## Binding lattice

```text
StateLike
├── Field
│   ├── ModifiedField
│   └── InvariantField
├── Invariant
│   ├── InvariantMarker
│   ├── InvariantField
│   └── NullState
└── Composite
    ├── Fusion
    ├── Path
    ├── Exchange
    ├── Recurrence
    ├── Collapse
    └── Ascent
```

`InvariantField` is multiply inherited.

## Why the lattice exists

The original four classes are historically important but too coarse for a runtime.

Examples:

- `Φ↑` behaves like a field but is structurally a modified form of `Φ`.
- `Ψ_inv` is both field-like and invariant-qualified.
- `∅` belongs to the historical invariant class while requiring separation from
  missing information.
- transformation results are expressions that can participate in later paths.

## Binding distinction

```text
primitive      created directly by the core vocabulary
derived        decomposable into a base and modifier
composite      created by a transformation operator
reference      name resolving to another expression
meta           compression declaration only
```

## Unknown is not null

A future adapter may define an unknown type, but:

```text
UNKNOWN ≠ ∅
ERROR   ≠ ∅
FALSE   ≠ ∅
BOTTOM  ≠ ∅
```

This distinction is part of the v0.2 semantic lock.
