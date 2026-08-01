# LAMAGUE Core Algebra v0.1

**Author:** Mackenzie C. J. Clark  
**Project:** Lycheetah / Aura Prime OS  
**Status:** Executable core-language research release  
**License:** MIT

LAMAGUE Core Algebra v0.1 isolates the language itself from AURA, Cascade, TIM,
Microorcim, and other domain systems.

It implements:

- canonical primitive classes;
- symbolic transformation grammar;
- deterministic parsing;
- immutable bindings;
- invariant, requirement, and prohibition statements;
- typed semantic validation;
- canonical normal forms;
- equivalence checking;
- lossless Z₁/Z₂/Z₃ macro compression;
- semantic graph export;
- adapter boundaries for external systems;
- an adversarial core-language benchmark.

## Core principle

```text
LAMAGUE core defines symbolic structure.
Domain adapters assign application-specific meaning.
```

TIM and Microorcim are deliberately absent from the grammar. An adapter may map
LAMAGUE expressions into those systems, but no adapter may redefine the core algebra.

## Quick start

```lamague
let return_path = Ao → Φ↑ → Ψ_inv;
invariant stable_return = return_path;
forbid Ψ ↯ ∅;
macro Z₁ RETURN = return_path;
check equivalent(Ao ⊗ Φ, Φ ⊗ Ao);
RETURN;
```

Run:

```bash
python -m lamague_core.cli examples/core_return_path.lmg --pretty --graph
python -m unittest discover -s tests -v
python benchmark/run_benchmark.py
```

## Binding claim boundary

This release validates software behavior over a defined symbolic algebra. It does
not prove that LAMAGUE is a universal language, a physical theory, an alignment
guarantee, or a lossless compressor of unrestricted natural language.
