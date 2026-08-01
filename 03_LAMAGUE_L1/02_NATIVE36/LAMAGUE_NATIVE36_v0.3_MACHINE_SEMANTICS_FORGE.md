# LAMAGUE Native-36 v0.3 — Machine Semantics Forge

## What changed

v0.2 established a visual alphabet and five compound seals.

v0.3 adds the machine anatomy that the visual prototype was asking for:

- canonical and primitive status
- spoken forms
- type signatures
- accepted and returned types
- minimum and maximum arity
- preconditions
- preserved invariants
- explicit failure modes
- recovery behaviour
- inverse or paired operations
- radical provenance
- visual logic
- executable examples
- ASCII transport grammar

This is not a repudiation of v0.2.

It is the next layer produced by examining it seriously.

## Canonical lifecycle

```text
FORGED VISUAL BODY
→ MACHINE ANATOMY
→ PARSER
→ TYPE CHECKER
→ EXECUTION
→ ROUND TRIP
→ BENCHMARK
```

## Status boundary

Root-supported tokens:

```text
A B C D F I K M T Z
```

Historical/forged tokens:

```text
J V
```

Current forge proposals:

```text
E G H L N O P Q R S U W X Y
```

`P` and `R` remain macro candidates until primitivehood testing determines whether their repeated expansions are more expensive than retaining them as dedicated operations.

## Machine law

```text
A glyph is not executable merely because its meaning is described in prose.
It becomes executable when the registry can reject invalid arguments,
declare what must be preserved, and specify what happens when execution cannot proceed.
```

## Next forge

1. Build the lexer and parser from the EBNF.
2. Convert expressions into a typed AST.
3. Implement the seal expander.
4. Implement a static type checker.
5. Implement an interpreter over abstract state records.
6. Run the deep visual and semantic tests against the stronger v0.3 body.
