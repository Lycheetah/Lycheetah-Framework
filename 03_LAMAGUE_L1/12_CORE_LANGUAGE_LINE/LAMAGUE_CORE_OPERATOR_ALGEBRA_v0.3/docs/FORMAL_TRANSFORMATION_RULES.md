# Formal Transformation Rules

Let `Γ ⊢ x : T` mean expression `x` has type `T`.

For every core operator `op`:

```text
Γ ⊢ A : StateLike    Γ ⊢ B : StateLike
----------------------------------------
Γ ⊢ A op B : Result(op)
```

Where:

```text
Result(⊗) = Fusion
Result(→) = Path
Result(⇌) = Exchange
Result(⟲) = Recurrence
Result(↯) = Collapse
Result(↗) = Ascent
```

## Fusion normalization

```text
normalize((A ⊗ B) ⊗ C)
=
sort(normalize(A), normalize(B), normalize(C))
```

Duplicates are retained.

## Projection normalization

```text
normalize((A → B) → C)
=
path(normalize(A), normalize(B), normalize(C))
```

Order and duplicates are retained.

## Exchange normalization

```text
normalize(A ⇌ B)
=
exchange(min(A,B), max(A,B))
```

Nested exchanges do not flatten.

## Directed operators

For `op ∈ {⟲, ↯, ↗}`:

```text
normalize(A op B)
=
binary(op, normalize(A), normalize(B))
```

No reordering or reassociation is permitted.

## Null boundary

No rule exists for:

```text
A op ∅ = ∅
A ⊗ ∅ = A
```

Any future identity or annihilation law requires a separate canon proposal.
