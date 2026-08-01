# Adapter Interface v0.2

An adapter receives explicit core types.

It may:

- add domain-specific types;
- map core atoms to domain objects;
- map core operators to domain functions;
- validate constraints;
- define missing, unknown, evidence, time, units, or policy objects.

It may not:

- change the core subtype lattice silently;
- reinterpret `∅` as missing or unknown;
- erase the decomposition of `Φ↑` or `Ψ_inv`;
- change an operator result type;
- import domain validation into core test claims;
- add TIM or Microorcim keywords to the core parser.

An adapter extension must document whether each new type is:

```text
StateLike
Field-like
Invariant-like
Composite-like
or outside the structural algebra
```
