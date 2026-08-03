# Truth Pressure Sovereign Sol Shadow Bridge v0.6

This bundle turns Truth Pressure App RC v0.5 into a drop-in **shadow integration layer** for the Lycheetah mobile app.

It does not claim scientific validation and does not replace the historical CASCADE engine.

## What is complete

- React Native-safe Truth Pressure RC runtime.
- Legacy + candidate parallel execution.
- `off`, `shadow`, and `candidate-preview` modes.
- Privacy-safe comparison records with no raw text fields.
- Bounded local record retention.
- Serialized local writes to prevent lost concurrent records.
- AsyncStorage adapter.
- Explicit-submit React hook.
- Neutral candidate preview card.
- Installer that refuses to overwrite existing paths.
- Executable bridge verification.

## Initial behavior

```text
historical scoreCASCADE
        +
candidate text triage
        ↓
privacy-safe comparison
        ↓
local AsyncStorage only
```

The historical result remains visible in `shadow`.

The candidate is:

```text
PROVISIONAL
TEXT TRIAGE ONLY
NOT A TRUTH PROBABILITY
NOT STRUCTURALLY AUTHORITATIVE
```

## Install files into a repository copy

```bash
node tools/apply-shadow-bridge.mjs /path/to/lycheetah-mobile
```

The installer:

- confirms the target package is `lycheetah-mobile`;
- copies only new bridge paths;
- refuses to overwrite existing files;
- leaves historical CASCADE source untouched;
- does not guess which UI screen should be edited.

## Verify this bundle

```bash
npm run verify
npm run typecheck
```

## What remains for true in-app wiring

The live `scoreCASCADE` screen/service and persistence wrapper were not included in the supplied source. See `docs/CALL_SITE_PATCH_TEMPLATE.md`.

A line-level app patch requires those exact files.

## Engineering acceptance target

Before candidate preview:

```text
100 local shadow comparisons
0 crashes
0 NaN or infinite outputs
0 raw-content records
all disagreements inspectable
no automatic reorganisation
```

These are engineering gates, not scientific validation.
