# Truth Pressure Engine v0.3 — Semantic Hardening

An executable research instrument for **revision pressure**, not truth probability.

v0.3 does not claim perfection. It removes silent ambiguities discovered while attacking v0.2 and makes remaining assumptions more visible.

## Main changes

- Invalid component values now fail loudly instead of being silently clamped.
- Normalized pressure is defined as `Π_norm = Π_canon × S₀`, so its range is always `[0,1]` for every valid `S₀`.
- Limiter ties are reported rather than hidden by branch order.
- Structured evidence bonuses depend on measured independence, replication, quality, and provenance—not merely the number of item IDs.
- Provenance has explicit `UNVERIFIED`, `INSPECTABLE`, and `VERIFIED` registers.
- Handling quality no longer inflates Truth Pressure or review priority.
- Text mode is renamed **provisional triage** and no source locator earns evidence credit without external verification.
- Negated evidence is scoped per sentence rather than wiping unrelated support.
- Scope resolution reduces only matched contradiction strain; unrelated contradictions remain.
- Apostrophes in contractions are no longer treated as quotation delimiters.
- Onion input scale is explicit (`unit` or `percent`), eliminating automatic scale guessing.
- Axiom load-bearingness is separate from explanatory reach.
- Judge output uses a versioned, named nine-layer contract with per-layer confidence.
- Review plans carry a source fingerprint, require explicit sovereign approval, and fail safely when stale.

## Verify

```bash
npm run verify
```

## Commands

```bash
node --experimental-strip-types src/cli.ts analyze-text text.txt
node --experimental-strip-types src/cli.ts score examples/assessment.json
node --experimental-strip-types src/cli.ts onion examples/onion.json
node --experimental-strip-types src/cli.ts corpus data/frozen-corpus-v0.1.jsonl results.jsonl
```

## Boundary

> This score represents revision pressure under a declared operationalization. It does not establish factual truth.
