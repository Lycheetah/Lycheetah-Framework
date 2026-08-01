# LAMAGUE Core v0.3 — Complete Operator Algebra and Transformation Contracts

**Author:** Mackenzie C. J. Clark  
**Project:** Lycheetah / Aura Prime OS  
**Status:** Executable core-language research release  
**License:** MIT

## 1. Purpose

v0.3 answers:

> What does each core transformation guarantee, refute, leave undeclared, or defer to a domain adapter?

The release preserves the v0.2 ontology and defines a contract for every operator:

```text
⊗  fusion
→  projection
⇌  exchange
⟲  recurrence
↯  collapse
↗  ascent
```

## 2. Four-valued claim discipline

Every proposed law receives one of five statuses:

```text
PROVEN
REFUTED
UNDECLARED
DOMAIN_DEPENDENT
NOT_APPLICABLE
```

This avoids converting absence of evidence into a false universal law.

### PROVEN

Implemented by canonical normalization or the type system.

### REFUTED

A deterministic structural counterexample exists.

### UNDECLARED

The core does not currently assert the law.

### DOMAIN_DEPENDENT

The answer requires meanings or execution rules outside the core.

### NOT_APPLICABLE

The property does not apply to the operator.

## 3. Core contract table

| Operator | Commutative | Associative | Idempotent | Structural inverse | Operational reversibility |
|---|---|---|---|---|---|
| `⊗` | proven | proven | refuted | undeclared | domain-dependent |
| `→` | refuted | proven | refuted | undeclared | domain-dependent |
| `⇌` | proven | refuted | refuted | self | domain-dependent |
| `⟲` | refuted | refuted | refuted | undeclared | domain-dependent |
| `↯` | refuted | refuted | refuted | undeclared | domain-dependent |
| `↗` | refuted | refuted | refuted | undeclared | domain-dependent |

No operator currently has a declared universal identity or annihilator.

## 4. Fusion

```text
A ⊗ B ≡ B ⊗ A
(A ⊗ B) ⊗ C ≡ A ⊗ (B ⊗ C)
A ⊗ A ≢ A
```

Fusion is normalized as a sorted n-ary structure while retaining duplicates.

It does not imply:

- agreement;
- compatibility;
- lossless real-world merger;
- a neutral identity element.

## 5. Projection

```text
(A → B) → C ≡ A → (B → C)
A → B ≢ B → A
A → A ≢ A
```

Projection is normalized as an ordered path.

It does not imply:

- causation;
- mutation;
- reversibility;
- guaranteed reachability.

## 6. Exchange

```text
A ⇌ B ≡ B ⇌ A
(A ⇌ B) ⇌ C ≢ A ⇌ (B ⇌ C)
```

Exchange has a structural self-inverse because reversing its two direct operands produces
the same canonical relation.

This does not prove that a domain exchange can be undone.

## 7. Recurrence

```text
A ⟲ B ≢ B ⟲ A
(A ⟲ B) ⟲ C ≢ A ⟲ (B ⟲ C)
```

The core records recurrence but does not execute it.

Termination, convergence, fixed points, loop bounds, and progress are domain-dependent.

## 8. Collapse

```text
A ↯ B ≢ B ↯ A
(A ↯ B) ↯ C ≢ A ↯ (B ↯ C)
```

`↯` remains collapse only. It is not a decision junction.

The expression:

```text
A ↯ ∅
```

is preserved exactly. It does not normalize to `∅`.

## 9. Ascent

```text
A ↗ B ≢ B ↗ A
(A ↗ B) ↗ C ≢ A ↗ (B ↗ C)
```

The glyph name does not give the core permission to infer:

- improvement;
- morality;
- numerical increase;
- hierarchy;
- monotonic progress.

## 10. Structural closure

All six operators accept `StateLike × StateLike`.

All six return a subtype of `StateLike`.

Therefore every pair of core operators is structurally composable.

This is a grammar and type fact, not a domain-validity claim.

## 11. Native contract inspection

```lamague
describe operator ⊗;
describe operator ⟲;

check law(⊗, commutative);
check law(→, commutative);
check law(⇌, inverse);
check law(⟲, terminating);

check composition(⊗, →);
check composition(↯, ⟲);
```

## 12. Rewrite trace

Normalization outputs the exact rules applied:

```text
FUSION_ASSOCIATIVE_FLATTEN
FUSION_COMMUTATIVE_SORT
PROJECTION_ASSOCIATIVE_FLATTEN
EXCHANGE_SYMMETRIC_ORDER
REFERENCE_EXPANSION
DERIVED_ATOM_DECOMPOSITION
```

Directed operators are not silently reordered or flattened.

## 13. Binding exclusions

v0.3 does not prove:

- real-world reversibility;
- termination;
- convergence;
- physical causality;
- ethical improvement;
- agent alignment;
- universal identities;
- universal annihilators.

Those claims require later formal definitions or domain adapters.
