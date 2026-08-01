# LAMAGUE Runtime v0.1

**First executable milestone for the LAMAGUE Frontier Canon.**

This is a bounded research prototype. It does not claim that LAMAGUE is proven superior to natural language, JSON, formal logic, or policy languages. It demonstrates that the post-1C architecture can be represented as executable software with explicit ontology, typed syntax, deterministic seal expansion, constitutional auditing, abstract interpretation, explanation, and trace preservation.

## What this prototype implements

- sixteen-root Ontological Kernel
- VITA-8 context fields
- operation-sequence DSL
- typed unknowns such as `U<consent>`
- deterministic seal expansion under registry version `0.1`
- typed AST nodes
- Truth, Agency, and Life Gate auditing
- outcomes: `VALID`, `EXPAND`, `REPAIR`, `ISOLATE`, `REJECT`
- abstract-state interpreter with no real-world side effects
- plain-language recovery
- JSON trace records
- canonical first-milestone natural-language compiler

## Quick start

```bash
python -m lamague_runtime.cli demo
python -m lamague_runtime.cli parse "FRO -> COR"
python -m lamague_runtime.cli compile \
  "Human and AI collaborators examine an unproven claim, preserve uncertainty, record contributions, and publish only what the evidence supports."
python -m unittest discover -s tests -v
```

## Canonical first milestone

Input:

```text
Human and AI collaborators examine an unproven claim,
preserve uncertainty,
record contributions,
and publish only what the evidence supports.
```

Expected operation path:

```text
Q -> O -> E -> U -> I -> G -> T -> P -> F -> Y
```

The natural-language compiler in v0.1 is deliberately narrow. It recognizes this research pattern and does not pretend to be a general semantic parser.

## DSL examples

```text
FRO -> COR
U<consent> -> G -> Y
VERITAS -> CARE -> LIFE
X{from=human,to=ai,value=knowledge,consent=explicit}
```

## Constitutional rule

No consequential expression is executed unless all applicable gates pass. Failed or incomplete expressions return explicit audit outcomes rather than confident synthetic completion.

## Status boundary

- **Implemented:** parser, AST, seal expansion, auditor, abstract interpreter, explainer, traces, tests.
- **Specified but not proven:** VITA-8 utility, agency symmetry, semantic efficiency, cross-model consistency.
- **Not implemented:** native glyph parsing, real-world action connectors, automated consent verification, semantic hashes, human recognition studies.
