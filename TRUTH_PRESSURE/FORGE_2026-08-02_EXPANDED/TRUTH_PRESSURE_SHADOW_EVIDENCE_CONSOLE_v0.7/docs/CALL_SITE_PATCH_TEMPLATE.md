# Live Call-Site Patch Template

This template is deliberately exact about behavior but neutral about the unknown screen filename.

## Historical pattern

Find the screen or service containing:

```ts
const result = scoreCASCADE(text);
```

Do not remove the historical call during shadow collection.

## Replace the local call with

```ts
import { runAndRecordTruthPressureBridge } from '@/lib/truth-pressure-integration/shadow-service';
import { truthPressureShadowRecorder } from '@/lib/truth-pressure-integration/shadow-store-async';

const bridge = await runAndRecordTruthPressureBridge(
  text,
  truthPressureShadowRecorder,
  'shadow',
);

// Existing UI remains unchanged in shadow mode.
const result = bridge.legacy;

// Developer inspection only.
const candidate = bridge.candidate;
const comparison = bridge.comparison;
```

If the call site is synchronous today, move the bridge call into its existing submit or analysis handler and make that handler asynchronous. Do not run or persist on every keystroke.

## Candidate preview

Only behind a developer or research switch:

```tsx
{bridge.visible === 'CANDIDATE_PREVIEW' && bridge.candidate ? (
  <TruthPressureCandidateCard view={bridge.candidate} />
) : null}
```

## Rules that must survive the patch

1. Historical UI remains visible in `shadow`.
2. Raw input text is not written to the comparison store.
3. Text mode remains `TRIAGE_ONLY`.
4. No structural proposal is produced from text mode.
5. No threshold is invented.
6. No automatic reorganisation occurs.
7. Analysis errors do not erase the legacy result.
8. Persist only after explicit user submission, not while typing.

## Exact source files still needed for a line-level patch

Upload the current versions of whichever files contain:

- the `scoreCASCADE(...)` call used by the live screen;
- the Library Truth Pressure display;
- the CASCADE/Onion screen;
- `components/cascade/OnionProfile.tsx`;
- the app persistence wrapper, when one already exists.

Likely names referenced by the current source and implementation report include:

```text
app/.../cascade.tsx
app/.../library.tsx
components/cascade/OnionProfile.tsx
lib/...storage....ts
```

Once supplied, the generic template can be replaced with a verified line-level patch against the real files.
