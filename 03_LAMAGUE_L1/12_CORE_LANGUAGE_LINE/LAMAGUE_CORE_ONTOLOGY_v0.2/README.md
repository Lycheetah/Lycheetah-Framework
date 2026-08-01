# LAMAGUE Core v0.2 — Primitive Ontology and Type Lock

**Author:** Mackenzie C. J. Clark  
**Project:** Lycheetah / Aura Prime OS  
**Status:** Executable core-language research release  
**License:** MIT

v0.2 evolves LAMAGUE Core Algebra v0.1 without introducing any domain adapter.

It adds:

- a binding ontology registry;
- an explicit subtype lattice;
- optional type annotations;
- type and subtype checks;
- ontology inspection;
- derived-symbol decomposition;
- operator input/output signatures;
- a hard distinction between intentional null and missing information;
- typed semantic graphs;
- 30 deterministic ontology benchmark cases.

## Deep locks

```text
Φ↑    = modify(Φ, ↑)
Ψ_inv = qualify(Ψ, inv)
∅     = intentional null, never missing evidence
```

## Example

```lamague
let anchor: Field = Ao;
let lifted: Field = Φ↑;
let target: Invariant = Ψ_inv;

invariant return_path: Path = Ao → Φ↑ → Ψ_inv;

check type(Φ↑, Field);
check type(Ψ_inv, Invariant);
check subtype(Path, StateLike);

describe Φ↑;
describe Ψ_inv;
```

## Run

```bash
python -m unittest discover -s tests -v
python benchmark/run_benchmark.py
python -m lamague_core.cli examples/ontology_lock.lmg --pretty --graph
python -m lamague_core.cli --ontology --pretty
```

## Claim boundary

This release validates deterministic software behavior over a declared type system.

It does not establish that the ontology is complete, universal, physically real,
aligned, conscious, or suitable for a domain without an explicit adapter.
