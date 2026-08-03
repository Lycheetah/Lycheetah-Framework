# TRUTH PRESSURE EXECUTION ROADMAP
## TP-ER v0.1 — From Handcrafted Instrument to Evidence-Bearing Research System

**Originator:** Mackenzie Conor James Clark  
**System:** CASCADE / Truth Pressure / Sovereign Sol  
**Status:** ACTIVE EXECUTION PLAN  
**Date:** 2026-08-02

---

## 1. Current Position

The research has already established:

- a canonical Truth Pressure quantity;
- a documented app implementation state;
- the three-scale distinction;
- a formal interpretation protocol;
- a pre-calibration validation protocol;
- a frozen controlled corpus;
- a human annotation guide;
- an untuned execution runbook;
- a failure taxonomy;
- a machine-readable result schema.

What has **not** yet happened:

- direct audit of the real TypeScript source;
- source-faithful reproduction of the documented outputs;
- untuned execution against the frozen corpus;
- blinded human component ratings;
- calibration against held-out data;
- external replication;
- justified public performance claims.

The project is therefore at the transition:

```text
FORMALIZATION → EXECUTION
```

---

## 2. Governing Rule

Until the untuned baseline run is complete:

```text
NO new constants
NO changed thresholds
NO changed marker lists
NO removed failures
NO public performance claims
NO promotion of Π into a truth probability
```

The next work must reduce uncertainty about the instrument rather than expand the theory around it.

---

# STAGE 1 — SOURCE CAPTURE

## Goal

Acquire and preserve exactly what Sovereign Sol currently runs.

## Required files

```text
lib/cascade-score.ts
lib/intelligence/cascade-onion.ts
lib/intelligence/cascade-judge.ts
lib/intelligence/cascade-reorganise.ts
scripts/verify-truth-pressure.ts
package.json
package-lock.json / pnpm-lock.yaml / yarn.lock
```

Useful supporting files:

```text
lib/talk/truth-lens.ts
lib/mystery-school/truth-covenant.ts
```

Explicit exclusion:

```text
lib/care/care-pressure.ts
```

## Deliverables

```text
SOURCE_SNAPSHOT/
SOURCE_HASHES.sha256
ENVIRONMENT.md
REPOSITORY_STATE.json
```

## Gate 1

Proceed only when the source snapshot is complete and immutable.

---

# STAGE 2 — IMPLEMENTATION MAP

## Goal

Explain the running engine line by line without changing it.

## Extract

- every marker and regex;
- every raw count;
- every normalization rule;
- every saturation function;
- every constant;
- every clamp and floor;
- every layer formula;
- every dependency;
- every falsifiability rule;
- every trigger;
- every branch;
- every persistent-state effect.

## Deliverables

```text
IMPLEMENTATION_MAP.md
CONSTANT_REGISTER.json
MARKER_REGISTER.json
BRANCH_MAP.md
SCALE_MAP.md
```

## Gate 2

Every displayed score must be reconstructable from the map.

---

# STAGE 3 — REPRODUCTION

## Goal

Reproduce every numerical claim in the implementation report.

Minimum checks:

```text
canon/app ×20 relationship
onion reference outputs
legacy length saturation
legacy inverted-strain outputs
current repaired outputs
trigger conversion
dependency caps
falsifiability cap
```

## Deliverables

```text
REPRODUCTION_RESULTS.json
REPRODUCTION_REPORT.md
```

## Gate 3

Any unreproduced claim is marked clearly before the corpus run.

---

# STAGE 4 — UNTOUCHED BASELINE RUN

## Goal

Run the current engine against the frozen corpus before changing anything.

## Inputs

```text
TP-CC v0.1 controlled corpus
TP-VP v0.1 validation protocol
TP-UER v0.1 runbook
TP-FT v0.1 failure taxonomy
```

## Execute

- all 24 frozen cases;
- repeated deterministic runs;
- controlled pair comparisons;
- word-count baseline;
- raw-count baseline;
- density baseline;
- saturation baseline;
- E-only baseline;
- E×P baseline;
- complete Truth Pressure forms.

## Deliverables

```text
CASE_RESULTS.jsonl
PAIRWISE_RESULTS.jsonl
BASELINE_RESULTS.json
RUN_SUMMARY.md
```

## Gate 4

The run is accepted only if no constant, case, expectation, or marker was changed during execution.

---

# STAGE 5 — FAILURE MATRIX

## Goal

Learn exactly how the current instrument fails.

## Classify each failure as

```text
mathematical
measurement
component
governance
calibration
interpretation
research-process
```

## Critical questions

- Does length still affect score unexpectedly?
- Can marker stuffing beat real evidence?
- Does negation reverse meaning correctly?
- Are quotations handled?
- Does jargon imitate explanatory power?
- Is honest uncertainty punished?
- Are paraphrases stable?
- Can correct final Π hide incorrect E, P, or S?
- Do trigger states depend on scale confusion?
- Does any output imply truth rather than review pressure?

## Deliverables

```text
FAILURE_MATRIX.jsonl
FAILURE_ATLAS.md
ROOT_CAUSE_MAP.md
```

## Gate 5

No repair begins until the full untouched failure record is preserved.

---

# STAGE 6 — HUMAN PILOT

## Goal

Test whether the components correspond to judgments humans can explain.

## First pilot

```text
3 blinded raters
24 frozen passages
E, P, S rated separately
confidence recorded separately
```

Then expand to:

```text
60+ passages
3 or more domains
held-out cases
```

## Compare

```text
human E ↔ engine E
human P ↔ engine P
human S ↔ engine S
human ranking ↔ engine ranking
```

Never evaluate only final Π.

## Deliverables

```text
ANNOTATIONS.csv
AGREEMENT_REPORT.md
ENGINE_HUMAN_DISAGREEMENTS.md
```

## Gate 6

If humans cannot agree on a component, refine the construct before calibrating the engine to it.

---

# STAGE 7 — REPAIR AND CALIBRATION

## Goal

Repair observed failures and make constants earn their values.

## Candidate parameters

```text
S₀
k_E
k_P
k_S
tension weight
contested weight
falsifiability cap
text review trigger
pairwise margin
layer thresholds
dependency multipliers
```

## Data separation

```text
training set
validation set
untouched test set
```

## Optimize jointly for

- component fidelity;
- length invariance;
- paraphrase stability;
- adversarial resistance;
- ranking stability;
- false promotion;
- false rejection;
- explanation fidelity;
- simplicity.

## Rule

A more complicated engine must beat a simpler transparent baseline or justify its complexity in another measured way.

## Deliverables

```text
CALIBRATION_PLAN.md
PARAMETER_SWEEP_RESULTS.json
SELECTED_CONFIGURATION.json
CHANGELOG.md
```

## Gate 7

Freeze the selected configuration before touching the held-out test set.

---

# STAGE 8 — HELD-OUT VALIDATION

## Goal

Determine what the repaired instrument has actually earned.

## Test on

- unseen passages;
- unseen paraphrases;
- unseen domains;
- adversarial examples;
- independent raters;
- scale and trigger boundary cases.

## Deliverables

```text
HELD_OUT_RESULTS.json
VALIDATION_REPORT.md
KNOWN_LIMITATIONS.md
```

## Gate 8

Claims are limited to properties that survive held-out testing.

---

# STAGE 9 — EXTERNAL CHALLENGE

## Goal

Let someone outside the project break it.

Provide:

- source snapshot;
- formula and scale map;
- frozen tests;
- result schema;
- known failures;
- reproduction instructions.

Ask external reviewers to target:

```text
construct validity
prior art
measurement validity
adversarial gaming
threshold stability
alternative explanations
simpler baselines
```

## Deliverables

```text
EXTERNAL_REVIEW_LOG.md
REPLICATION_RESULTS/
RESPONSE_AND_REVISIONS.md
```

---

# STAGE 10 — PUBLICATION

Only after the earlier gates should the article be finalized.

The first serious article should report:

1. what Truth Pressure is;
2. what the app operationalizes;
3. what failed in the untouched engine;
4. what was repaired;
5. which properties survived held-out testing;
6. which claims remain conjectural;
7. how another person can reproduce the work.

The article must not become a victory story.

It should become a transparent research record.

---

## 3. Claim Ladder

### Allowed now

> Truth Pressure is a handcrafted experimental architecture with a working software instantiation and a preregistered validation path.

### Allowed after source reproduction

> The implementation behaves as documented for the reproduced cases.

### Allowed after untouched corpus testing

> The current engine passes these named properties and fails these others.

### Allowed after human pilot

> The components show this degree of correspondence with blinded human judgments.

### Allowed after held-out validation

> The calibrated instrument demonstrates these specific properties on unseen cases.

### Not allowed without much stronger evidence

> Truth Pressure detects truth.

> Truth Pressure is a universal law.

> Current thresholds are universal constants.

---

## 4. Immediate Next Action

The immediate action is not another theory document.

It is:

```text
UPLOAD THE REAL SOURCE FILES
↓
HASH THEM
↓
AUDIT THEM
↓
REPRODUCE THE REPORT
↓
RUN THE UNTOUCHED CORPUS
```

---

## 5. Working Principle

> **We do not make Truth Pressure credible by defending it. We make it credible by constructing the conditions under which it is allowed to fail.**
