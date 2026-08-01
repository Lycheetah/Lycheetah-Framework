# LAMAGUE Core Algebra v0.1 — Binding Specification

## 1. Purpose

LAMAGUE Core is a typed symbolic algebra for representing fields, invariants,
transformations, compressed aliases, and structural constraints.

The core is independent of every application domain.

```text
LAMAGUE Core
├── AURA adapter
├── Cascade adapter
├── TIM adapter
├── Microorcim adapter
└── future adapters
```

## 2. Source-preserving decisions

The source corpus consistently identifies four central classes:

- I-class: invariants;
- D-class: dynamics;
- F-class: fields;
- M-class: meta-compression levels.

The archive also contains contradictions:

- `↯` means collapse in the core grammar but junction in an experimental algorithm notation;
- operators appear both as dynamic atoms and composition operators;
- `∮` is used both as recursion in early prose and integration in raw mathematics;
- `Ψ` is described as drift field, fold operation, awareness field, and context-specific state;
- extreme compression ratios are asserted without adequate measurement.

v0.1 resolves these without deleting history.

## 3. Canonical primitives

### 3.1 Invariants

| Symbol | Canonical core meaning |
|---|---|
| `⟟` | fixed-point marker |
| `∅` | null state |
| `⟐` | stable triad marker |
| `⟁` | integrity marker |
| `∞` | closed-cycle marker |
| `Ψ_inv` | named invariant trajectory |

### 3.2 Fields

| Symbol | Canonical core meaning |
|---|---|
| `Ao` | anchor field |
| `Φ` | orientation field |
| `Φ↑` | upward-oriented field |
| `Ψ` | generic fold/drift field |
| `S` | entropy/uncertainty field |
| `Δ` | variation field |

`Ψ` remains intentionally broad at the core level. Adapters must state their
pragmatic interpretation explicitly.

### 3.3 Transformations

| Operator | Name | Core law |
|---|---|---|
| `→` | projection/path | associative sequence |
| `⊗` | fusion | associative and commutative; not idempotent |
| `⇌` | exchange | commutative; not associative |
| `⟲` | recursion relation | directed; no automatic termination claim |
| `↯` | collapse | directed and non-invertible by default |
| `↗` | ascent | directed and non-invertible by default |

`↯` is collapse only in the core. Junction syntax belongs to a future algorithm
extension with a distinct token.

## 4. Canonical aliases

| Legacy form | Canonical form | Behavior |
|---|---|---|
| `A₀` | `Ao` | warning; raw lexeme retained |
| `∆` | `Δ` | warning; raw lexeme retained |
| `♾` | `∞` | warning; raw lexeme retained |
| `->` | `→` | warning; raw lexeme retained |
| `<->` | `⇌` | warning; raw lexeme retained |

`∮` is not an alias for recursion. It is reserved for the mathematical extension
because the corpus also defines it as an integral.

## 5. Statements

```lamague
let name = expression;
invariant name = expression;
require expression;
forbid expression;
macro Z₁ NAME = expression;
check equivalent(expression, expression);
expression;
```

Bindings, invariants, and macros are immutable.

## 6. Expression grammar

All binary operators are left-associative at parse time.

Precedence, highest to lowest:

```text
⊗
↯  ↗  ⟲
→  ⇌
```

Parentheses override precedence.

## 7. Semantic sorts

```text
Invariant
Field
Fusion
Path
Exchange
Recurrence
Collapse
Ascent
Reference
```

Meta symbols `Z₁`, `Z₂`, and `Z₃` are legal only in macro declarations.

## 8. Algebraic normal form

### Fusion

```text
A ⊗ B ≡ B ⊗ A
(A ⊗ B) ⊗ C ≡ A ⊗ (B ⊗ C)
A ⊗ A ≢ A
```

Fusion normal form is a sorted multiset. Duplicate operands remain.

### Projection

```text
(A → B) → C ≡ A → (B → C)
```

Projection normal form is an ordered path.

### Exchange

```text
A ⇌ B ≡ B ⇌ A
(A ⇌ B) ⇌ C is not normalized as A ⇌ (B ⇌ C)
```

### Directed operators

```text
A ↯ B ≢ B ↯ A
A ↗ B ≢ B ↗ A
A ⟲ B ≢ B ⟲ A
```

No inverse is inferred.

## 9. Constraint semantics

- `invariant`: names an expression that must be preserved by an adapter or later pass;
- `require`: stores a positive structural obligation;
- `forbid`: stores a prohibited normalized expression;
- these statements do not execute domain actions.

## 10. Compression semantics

A macro is a lossless named alias for a normalized expression.

```lamague
macro Z₁ RETURN = Ao → Φ↑ → Ψ_inv;
```

The law is:

```text
expand(compress_level, name) = normalize(original_expression)
```

The level is metadata:

- `Z₁`: local expression;
- `Z₂`: pathway/module;
- `Z₃`: architecture-level form.

No universal compression ratio is claimed. The runtime reports only measured token
and character counts for the provided expression and macro name.

## 11. Semantic graph

Every normalized expression can be exported as a deterministic directed graph:

- atoms become leaf nodes;
- operators become internal nodes;
- child order is retained except where commutativity is part of the core law;
- node IDs derive from SHA-256 of canonical subexpressions.

## 12. Adapter contract

An adapter may:

- map atoms to domain objects;
- map operators to domain functions;
- evaluate constraints;
- attach units, timestamps, evidence, or policies.

An adapter may not:

- change core operator laws silently;
- reinterpret `↯` as junction;
- treat a successful parse as truth;
- erase invariants, requirements, or prohibitions;
- claim domain validation from core tests.

## 13. Non-canonical and experimental material

Excluded from the authoritative core:

- junction branching;
- Pop, Sift, Flip, Pulse, Weaving, Seal, and I-Beam;
- physical claims about consciousness or quantum fields;
- unrestricted natural-language reversibility;
- claimed convergence theorems without stated assumptions and proofs;
- unmeasured compression ratios;
- domain-specific alignment thresholds.

These remain research extensions rather than deleted concepts.
