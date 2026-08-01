# LAMAGUE Core v0.3 — Complete Operator Algebra and Transformation Contracts

**Author:** Mackenzie C. J. Clark  
**Project:** Lycheetah / Aura Prime OS  
**Status:** Executable core-language research release  
**License:** MIT

v0.3 gives every core transformation a binding machine-readable contract.

```text
⊗  fusion
→  projection
⇌  exchange
⟲  recurrence
↯  collapse
↗  ascent
```

## Claim discipline

Every law is classified as:

```text
PROVEN
REFUTED
UNDECLARED
DOMAIN_DEPENDENT
NOT_APPLICABLE
```

This release deliberately declares no universal identity or annihilator.

## Example

```lamague
describe operator ⊗;
describe operator ⟲;

check law(⊗, commutative);
check law(→, associative);
check law(⇌, inverse);
check law(⟲, terminating);
check law(↯, identity);

check composition(⊗, →);
check composition(↯, ⟲);

check equivalent(
    (Ao ⊗ Φ) ⊗ Ψ,
    Ψ ⊗ (Φ ⊗ Ao)
);

describe Ψ ↯ ∅;
```

## Run

```bash
python -m unittest discover -s tests -v
python benchmark/run_operator_benchmark.py
python -m lamague_core.cli examples/operator_contracts.lmg --pretty
python -m lamague_core.cli --contracts --pretty
```

## Boundary

Operator contracts describe symbolic structure.

They do not prove domain causality, reversibility, termination, improvement, alignment,
physical validity, or real-world semantic compatibility.
