# Truth Pressure App RC v0.5

A React-Native-safe release candidate for integrating Truth Pressure into Sovereign Sol in **shadow mode**.

Truth Pressure is treated here as a revision-pressure instrument under declared inputs—not as truth probability.

## What this release candidate contains

- canonical scalar with strict validation;
- provenance-aware structured assessment;
- provisional text triage;
- onion adapter with explicit scale and separated magnitude/handling fields;
- strict versioned AI judge contracts;
- React-Native-safe reversible review transactions;
- app-facing view-model contract;
- privacy-safe shadow comparison records;
- integration guide and feature-flag example;
- UI copy contract;
- release gates;
- post-ready article and launch copy.

## App posture

```text
historical engine remains intact
        ↓
RC runs beside it in shadow mode
        ↓
disagreements are inspected
        ↓
candidate preview opens only after engineering gates
        ↓
research claims wait for human and held-out validation
```

## Verify

```bash
npm run verify
npm run typecheck
```

Current internal result:

```text
14 / 14 app-readiness checks passed
strict TypeScript check passed
runtime source contains no Node built-ins
```

These are engineering checks, not scientific validation.

## Integration

Read:

```text
integration/SOVEREIGN_SOL_INTEGRATION_GUIDE.md
integration/sovereign-sol-shadow-example.ts
integration/FEATURE_FLAG.ts
```

Recommended first flag:

```ts
export const TRUTH_PRESSURE_RC_MODE = 'shadow';
```

## App API

```ts
import { buildAppViewModel } from './lib/truth-pressure-rc';

const view = buildAppViewModel({
  kind: 'text',
  text,
});
```

Text mode always returns `TRIAGE_ONLY` and cannot become structurally eligible.

Structured mode:

```ts
const view = buildAppViewModel({
  kind: 'structured',
  assessment,
});
```

Onion mode:

```ts
const view = buildAppViewModel({
  kind: 'onion',
  assessment,
});
```

## Mandatory UI boundary

> This is a review signal under declared inputs. It is not a probability that the claim is true.

## Current status

**Ready for:** Sovereign Sol shadow integration and candidate developer preview after the listed engineering gates.

**Not ready for:** calibrated research claims, universal thresholds, automatic belief replacement, or objective-truth language.
