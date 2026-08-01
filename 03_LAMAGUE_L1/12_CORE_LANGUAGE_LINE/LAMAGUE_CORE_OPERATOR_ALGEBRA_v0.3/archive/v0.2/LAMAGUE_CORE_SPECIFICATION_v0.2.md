# LAMAGUE Core v0.2 — Primitive Ontology and Type Lock

**Author:** Mackenzie C. J. Clark  
**Project:** Lycheetah / Aura Prime OS  
**Status:** Executable core-language research release  
**License:** MIT

## 1. Purpose

Version 0.2 answers the first ontology question:

> What kinds of things exist inside LAMAGUE, and which operations may legally combine them?

It evolves v0.1 directly. No TIM, Microorcim, AURA, or Cascade syntax enters the core.

## 2. Source basis

The historical corpus defines:

- I-class invariants;
- D-class transformations;
- F-class fields;
- M-class compression operators;
- the structural form `[STATE] [TRANSFORMATION] [STATE]`.

The source does not fully distinguish primitive symbols from modified symbols, and it
places `∅`, `Ψ_inv`, and `Φ↑` into broad classes without a typed subtype lattice.

v0.2 formalizes those gaps without claiming the historical prose already supplied the
new implementation details.

## 3. Ontology layers

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

`InvariantField` has two parents by design. `Ψ_inv` remains field-like while carrying
an invariant qualification.

## 4. Primitive lock

| Symbol | Type | Role |
|---|---|---|
| `Ao` | Field | anchor |
| `Φ` | Field | orientation |
| `Ψ` | Field | contextual fold/drift field |
| `S` | Field | entropy or uncertainty |
| `Δ` | Field | variation |
| `⟟` | InvariantMarker | fixed point |
| `⟐` | InvariantMarker | stable triad |
| `⟁` | InvariantMarker | integrity |
| `∞` | InvariantMarker | closed cycle |
| `∅` | NullState | intentional null |

## 5. Derived-symbol lock

### `Φ↑`

`Φ↑` is no longer represented internally as an indivisible primitive.

```text
surface:      Φ↑
structure:    modify(Φ, ↑)
type:         ModifiedField
supertypes:   Field, StateLike
```

The source still prints and accepts `Φ↑`. The AST and semantic graph expose its
decomposition.

### `Ψ_inv`

`Ψ_inv` is a derived invariant-qualified field.

```text
surface:      Ψ_inv
structure:    qualify(Ψ, inv)
type:         InvariantField
supertypes:   Field, Invariant, StateLike
```

This avoids forcing it to be only a field or only an invariant.

## 6. Null law

```text
∅ = intentional null state
```

It does not mean:

- missing evidence;
- unavailable information;
- false;
- parser failure;
- semantic error;
- contradiction.

The core contains no unknown-value literal in v0.2. Domain adapters requiring unknown
or missing values must define them explicitly without aliasing them to `∅`.

## 7. Type annotations

Bindings, invariants, and macros may declare an expected type.

```lamague
let anchor: Field = Ao;
let lifted: Field = Φ↑;
let fixed: Invariant = ⟟;
let nullpoint: NullState = ∅;
invariant return_path: Path = Ao → Φ↑ → Ψ_inv;
macro Z₁ RETURN: Path = return_path;
```

A subtype satisfies a supertype annotation:

```text
ModifiedField <: Field
InvariantField <: Field
InvariantField <: Invariant
Path <: Composite
Composite <: StateLike
```

A mismatched annotation is rejected.

```lamague
let invalid: Field = ⟟;
```

## 8. Operator signatures

Every core operator accepts two `StateLike` operands.

| Operator | Left | Right | Returns |
|---|---|---|---|
| `⊗` | StateLike | StateLike | Fusion |
| `→` | StateLike | StateLike | Path |
| `⇌` | StateLike | StateLike | Exchange |
| `⟲` | StateLike | StateLike | Recurrence |
| `↯` | StateLike | StateLike | Collapse |
| `↗` | StateLike | StateLike | Ascent |

These signatures establish structural legality only. They do not imply physical,
ethical, numerical, or causal validity.

## 9. Type and subtype checks

```lamague
check type(Φ↑, Field);
check type(Ψ_inv, Invariant);
check subtype(ModifiedField, Field);
check subtype(Path, StateLike);
```

Type checks report results. They do not throw merely because a check is false.

## 10. Ontology inspection

```lamague
describe Φ↑;
describe Ψ_inv;
describe Ao → Φ↑;
```

The result includes:

- normalized form;
- semantic hash;
- inferred type;
- supertypes;
- atom ontology or operator signature;
- derived-symbol decomposition where applicable.

## 11. Compatibility

All valid v0.1 core expressions remain valid unless they depended on undocumented
internal `Sort` objects.

The output format now records typed binding objects rather than plain strings:

```json
{
  "anchor": {
    "type": "Field",
    "normal_form": "Ao"
  }
}
```

## 12. Binding exclusions

v0.2 does not define:

- numeric values;
- unknown evidence;
- temporal events;
- branching;
- functions;
- domain-specific Ψ interpretations;
- physical entropy calculations;
- alignment guarantees.

Those remain future core extensions or adapter responsibilities.
