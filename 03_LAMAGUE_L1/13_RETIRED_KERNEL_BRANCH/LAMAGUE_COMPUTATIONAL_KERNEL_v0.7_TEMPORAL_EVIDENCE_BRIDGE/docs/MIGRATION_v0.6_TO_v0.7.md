# Migration from v0.6 to v0.7

No existing v0.6 source programme must change.

Version 0.7 is additive.

## Old flow

```text
LAMAGUE source
→ parser
→ semantic IR
→ type/effect checks
→ immutable runtime
```

## New flow

```text
LAMAGUE source
→ existing v0.6 kernel

Temporal evidence JSON
→ v0.7 evidence/drift bridge

Both reports
→ joined audit surface
```

## Why a sidecar first

The current source parser is deliberately bounded and line-oriented.

Directly forcing scientific provenance and temporal telemetry into that grammar would increase parser ambiguity before the semantics were independently stabilized.

The sidecar allows the new type system to be tested first.

A later release may compile temporal declarations directly from `.lmg` once the packet schema and benchmark survive adversarial testing.
