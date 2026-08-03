# Truth Pressure Engine v0.2

A source-auditable tool for computing **revision pressure**, not truth probability.

This package is built beside the historical Sovereign Sol implementation. It does not overwrite the original engine or erase its failure record.

## What changed

- Preserves the canonical scalar: `Π = E·P/(S+S₀)`.
- Separates evidence, explanatory reach, load-bearingness, unresolved strain, and quality of handling strain.
- Treats certainty language as load-bearingness, never as evidence.
- Provides a structured assessment mode with explicit provenance.
- Provides a **provisional** text adapter that exposes every signal and warning.
- Separates tension magnitude from tension-handling quality in the onion adapter.
- Rejects incomplete nine-layer judge output instead of defaulting missing layers to zero.
- Uses a strict `Π > threshold` review boundary.
- Moves content and epistemic metadata together in reversible review proposals.
- Leaves review thresholds unconfigured unless the caller supplies one.

## Run verification

```bash
npm run verify
```

## Analyze text

```bash
node --experimental-strip-types src/cli.ts analyze-text path/to/text.txt
```

The result is marked `PROVISIONAL_TEXT_ADAPTER`. It is an inspectable heuristic, not a measurement of truth.

## Score a structured assessment

```bash
node --experimental-strip-types src/cli.ts score examples/assessment.json
```

Structured mode is the primary research path because evidence provenance and component judgments are explicit.

## Run the frozen corpus

```bash
node --experimental-strip-types src/cli.ts corpus data/frozen-corpus-v0.1.jsonl results.jsonl
```

The frozen corpus is now a development set for v0.2. It must not be presented as held-out validation.

## Core boundary

> This score represents revision pressure under the declared operationalization. It does not establish factual truth.
