# Truth Pressure App RC v0.5 — App Readiness Report

**Status:** READY FOR SHADOW INTEGRATION  
**Not status:** validated scientific instrument or production-authoritative replacement

## What changed after v0.3

### 1. React Native runtime boundary

The previous review transaction imported `node:crypto`, which is not a safe assumption inside an Expo/React Native runtime.

v0.5 replaces that dependency with a deterministic state token used only to detect stale review plans. The token is explicitly not cryptographic and is not used for security or privacy.

A source scan verifies that runtime modules contain no `node:` imports.

### 2. Stable app contract

The app now receives a versioned `TP-APP-VIEW-0.5` view model containing:

```text
mode
claim
normalized revision-pressure index
E / P / S component views
review state
plain-language explanation
warnings
provenance summary
register summary
mandatory boundary
```

The UI no longer has to infer meaning from raw engine objects.

### 3. No uncalibrated bands

The release candidate does not label pressure as low, moderate, high, true, or false.

It displays a normalized index and explicit components. Review status is available only when a caller deliberately supplies a threshold.

No threshold is configured by default.

### 4. Triage cannot reorganize knowledge

Text analysis always returns:

```text
TRIAGE_ONLY
```

It can direct attention but cannot become eligible for a structural proposal.

### 5. Onion judge contract now matches onion semantics

The new `TP-ONION-JUDGE-0.5` contract directly supplies:

```text
axiom load-bearingness
foundation evidence
structure mechanism
resonance unification
predictive reach
coherence
tension magnitude
tension handling quality
contested magnitude
contested handling quality
speculative extent
speculative label quality
frontier clarity
falsifiability
```

This removes the integration gap where the historical single TENSION score had to mean both magnitude and handling quality.

### 6. Privacy-safe shadow records

The shadow comparison format stores no raw text.

It may record:

```text
legacy output
candidate E/P/S
candidate normalized index
warnings
review-state agreement
input length
engine version
```

Any future upload or shared-research flow requires separate consent. Local comparison is the default.

### 7. Sovereign review transaction

Structural movement remains:

```text
proposed
explicitly approved
stale-state checked
non-overwriting
reversible
```

The app cannot treat a threshold crossing as permission to mutate knowledge automatically.

## Verification result

```text
14 / 14 app-readiness checks passed
TypeScript strict check passed
```

Verified behaviors include:

- bounded normalized pressure;
- stable app contract;
- mandatory boundary statement;
- triage-only text mode;
- no threshold by default;
- review signal without automatic authorization;
- separated onion magnitude and handling semantics;
- privacy-safe shadow record;
- deterministic stale-state token;
- approval requirement;
- stale-plan rejection;
- metadata-preserving movement;
- strict legacy judge contract;
- strict new onion judge contract;
- bounded adversarial text handling;
- no Node built-ins in runtime source.

## Remaining app work

The code package is ready to be copied into Sovereign Sol, but app integration is not complete until:

1. the feature flag is added;
2. the shadow harness is wired at the current text-lens call site;
3. the candidate developer panel renders all states;
4. local privacy-safe shadow storage is tested;
5. the new onion judge prompt replaces the ambiguous tension contract;
6. invalid judge output visibly preserves existing scores;
7. at least 100 real local comparisons are inspected;
8. no automatic reorganisation occurs.

## Article posture

The included article is ready as a transparent development article.

It reports:

- what the instrument proposes;
- what the first implementation got wrong;
- what the frozen corpus exposed;
- how the meanings were separated;
- what the app release candidate now protects;
- what remains unvalidated.

It does not claim scientific validation or truth detection.

## Verdict

> **v0.5 is app-ready for shadow integration, not ready to become an unquestioned authority inside the app.**
