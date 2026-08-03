# Sovereign Sol Integration Guide
## Truth Pressure App RC v0.5

## Integration posture

Do not replace the historical engine immediately.

Use three stages:

```text
OFF → SHADOW → CANDIDATE PREVIEW → RELEASE
```

The first app state should be `shadow`.

The historical `scoreCASCADE` result remains the visible behavior while v0.5 computes a second result in parallel. Comparison records contain no raw text.

## 1. Copy the runtime

Copy this folder into the app as:

```text
lib/truth-pressure-rc/
```

Required runtime files:

```text
src/app-adapter.ts
src/core.ts
src/index.ts
src/judge-contract.ts
src/onion-judge-contract.ts
src/onion.ts
src/review.ts
src/shadow.ts
src/structured.ts
src/text-adapter.ts
src/types.ts
src/validation.ts
```

The runtime contains no `node:` imports and is safe to bundle in Expo/React Native.

## 2. Keep the legacy engine intact

Do not delete or rewrite:

```text
lib/cascade-score.ts
lib/intelligence/cascade-onion.ts
lib/intelligence/cascade-judge.ts
lib/intelligence/cascade-reorganise.ts
```

They are the historical comparison instrument and correction receipt.

## 3. Add the feature flag

Start with:

```ts
export const TRUTH_PRESSURE_RC_MODE = 'shadow';
```

Do not expose candidate scores as authoritative while shadow evidence is still being collected.

## 4. Wire text shadow mode

Use `integration/sovereign-sol-shadow-example.ts` as the adapter pattern.

The candidate text mode is deliberately `TRIAGE_ONLY`:

- it may identify passages worth structured review;
- it must not propose or apply layer movement;
- it must never be labelled a truth score;
- it must display the boundary that revision pressure is not truth probability.

## 5. Store privacy-safe comparison records

A shadow record may contain:

```text
engine version
mode
E / P / S
normalized revision-pressure index
legacy score
review-state comparison
warnings and attack flags
input length
```

It must not contain raw user text by default.

Recommended local key:

```text
truth-pressure-shadow-v0.5
```

Do not upload records without a separate explicit research-consent flow.

## 6. Upgrade the onion judge contract

The historical judge gives one score each to TENSION and CONTESTED, while its prompt rewards good acknowledgement. That cannot feed a formula that needs unresolved tension magnitude.

Use `TP-ONION-JUDGE-0.5`, which separates:

```text
tensionMagnitude
tensionHandlingQuality
contestedMagnitude
contestedHandlingQuality
speculativeExtent
speculativeLabelQuality
```

The parser rejects incomplete or version-mismatched output.

## 7. Structural review

Only structured or onion assessments can become eligible for a review proposal.

Required sequence:

```text
score
→ threshold signal
→ proposal
→ explicit sovereign approval
→ stale-state check
→ reversible application
```

Text triage cannot reach this sequence directly.

No threshold is configured by default. Until calibration exists, any threshold used in development must be labelled `EXPERIMENTAL` and kept out of public validity claims.

## 8. UI migration

Historical UI label:

```text
Truth Pressure
```

Candidate UI label:

```text
Revision pressure index
```

Mandatory nearby copy:

> This is a review signal under declared inputs. It is not a probability that the claim is true.

Do not use certainty colors such as green = true or red = false.

## 9. Shadow acceptance record

Before candidate preview, collect at least:

```text
100 real local shadow comparisons
0 crashes
0 NaN or infinite values
0 raw-content telemetry records
all disagreement cases inspectable
no automatic reorganisation
```

These are engineering gates, not validation claims.

## 10. Candidate-preview gate

Candidate preview may open when:

- runtime and type checks pass;
- the app renders all states safely;
- raw content is absent from telemetry;
- judge contract failures leave existing scores untouched;
- stale proposals cannot apply;
- text triage cannot restructure knowledge;
- the boundary statement is visible;
- known limitations are linked from the interface.

## 11. Research-release gate

Do not call the instrument calibrated or validated until:

- blinded human E/P/S ratings are collected;
- inter-rater agreement is reported;
- weights are fitted without test leakage;
- an untouched held-out set is opened once;
- simple baselines are compared;
- failures and limitations are published with successes.
