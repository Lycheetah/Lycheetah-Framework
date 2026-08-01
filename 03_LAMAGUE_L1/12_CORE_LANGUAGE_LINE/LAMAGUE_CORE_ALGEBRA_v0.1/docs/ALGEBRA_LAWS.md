# LAMAGUE Core Algebra Laws

## Canonical laws

### Fusion

```text
x ⊗ y = y ⊗ x
(x ⊗ y) ⊗ z = x ⊗ (y ⊗ z)
```

Fusion is a commutative semigroup over composable expressions.

No identity element is declared in v0.1. Although the raw mathematics gives `⟟` unit
properties in a numerical encoding, that does not establish `⟟` as the identity for
symbolic fusion.

### Projection

```text
(x → y) → z = x → (y → z)
```

Projection is represented as an ordered path. It is not commutative.

### Exchange

```text
x ⇌ y = y ⇌ x
```

Exchange is symmetric but not declared associative.

### Collapse, Ascent, Recursion

```text
x ↯ y ≠ y ↯ x
x ↗ y ≠ y ↗ x
x ⟲ y ≠ y ⟲ x
```

These are directed structural relations. No inverse, convergence, or termination is
implied by syntax alone.

## Laws deliberately not adopted

- `x ⊗ ∅ = ∅`
- `x ⊗ ⟟ = x`
- collapse reversibility
- recursion termination
- automatic entropy reduction
- automatic coherence increase

Those may be valid inside specific adapters but are not justified as universal core
laws.
