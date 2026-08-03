# TRUTH PRESSURE VALIDATION PROTOCOL
## TP-VP v0.1 — Frozen Pre-Calibration Test Plan

**Originator:** Mackenzie Conor James Clark  
**Research system:** CASCADE / Truth Pressure / Sovereign Sol  
**Status:** PROPOSED AND FROZEN FOR FIRST IMPLEMENTATION AUDIT  
**Date:** 2026-08-02  
**Scope:** Validate the behavior of the current instrument before making public performance claims.

---

## 0. Core Boundary

Truth Pressure is tested here as a **revision-pressure instrument**.

This protocol does not test whether Truth Pressure detects objective truth.

A passing result means:

> Under the declared operationalization, the instrument behaves consistently, exposes its provenance, resists obvious gaming, and tracks independently judged evidence, explanatory reach, and structural strain better than transparent baselines.

A passing result does **not** mean:

> The instrument has discovered a universal law of truth.

---

## 1. Source-Faithful Systems Under Test

### 1.1 Canon quantity

```text
Π_canon = (E · P) / (S + S₀)
```

Current working value:

```text
S₀ = 0.05
```

### 1.2 Text-level app quantity

```text
Π_text = (E · P · S₀) / (S + S₀)
```

For identical normalized inputs at `S₀ = 0.05`:

```text
Π_text = Π_canon / 20
Π_canon = 20 · Π_text
```

### 1.3 Onion quantity

```text
E = (FOUNDATION + STRUCTURE) / 2
P = AXIOM
net_coherence = COHERENCE − 0.3·TENSION − 0.2·CONTESTED
S = 100 − net_coherence
Π_onion = (E · P) / (S + 5)
```

The onion quantity is treated as a separate operationalization. No direct conversion to canon or text scale is assumed.

---

## 2. Implementation Inputs Required

The audit cannot be completed until the following running sources are available:

```text
lib/cascade-score.ts
lib/intelligence/cascade-onion.ts
lib/intelligence/cascade-judge.ts
lib/intelligence/cascade-reorganise.ts
scripts/verify-truth-pressure.ts
```

Optional but relevant:

```text
lib/talk/truth-lens.ts
lib/mystery-school/truth-covenant.ts
```

The separate `care-pressure.ts` module is explicitly outside this audit.

---

## 3. Epistemic Registers

| Register | Meaning |
|---|---|
| IMPLEMENTED | Present in running code |
| MEASURED | Produced by an executed test |
| DERIVED | Follows mathematically from declared assumptions |
| ASSUMED | Chosen but not yet calibrated |
| INTERPRETIVE | Human meaning assigned to a result |
| FAILED | Contradicted by test |
| OPEN | Not yet tested |
| RETIRED | No longer claimed for this implementation |

No claim may be promoted above the register earned by its evidence.

---

## 4. Phase A — Source Audit

### A-01 Formula trace

Confirm the exact formulas used by each engine.

**Pass:** Code and documentation match line by line.  
**Fail:** Hidden clamp, offset, rescaling, branch, or alternative denominator is present but undocumented.

### A-02 Constant inventory

Extract every load-bearing constant, including:

```text
S₀
E saturation k
P saturation k
S saturation k
tension weight
contested weight
falsifiability cap
review trigger
legacy pairwise margin
all layer thresholds
all dependency multipliers
```

**Pass:** Every constant has a name, value, source file, line reference, register, and effect description.

### A-03 Marker inventory

Extract every phrase, regex, marker family, weight, exclusion, and normalization rule.

**Pass:** Every contribution to `E`, `P`, or `S` can be traced to an explicit rule.

### A-04 Branch audit

Enumerate all branches that alter:

```text
score
layer
cap
trigger
reorganization
rollback
history preservation
```

**Pass:** No branch changes epistemic state without appearing in the audit map.

---

## 5. Phase B — Mathematical Regression Tests

### B-01 Exact scale identity

For at least 1,000 random normalized tuples:

```text
Π_text × 20 = Π_canon
```

at `S₀ = 0.05`.

**Required tolerance:** `|difference| < 1e-12`.

### B-02 Finite floor

Test:

```text
S = 0
S → 0+
E = 0
P = 0
E = P = 1
```

**Pass:** No division by zero, infinity, NaN, or hidden clamp unless explicitly specified.

### B-03 Evidence monotonicity

Hold `P`, `S`, and `S₀` fixed. Increase `E`.

**Pass:** `Π` never decreases.

### B-04 Explanatory monotonicity

Hold `E`, `S`, and `S₀` fixed. Increase `P`.

**Pass:** `Π` never decreases.

### B-05 Strain monotonicity

Hold `E`, `P`, and `S₀` fixed. Increase `S`.

**Pass:** `Π` never increases.

### B-06 Saturation monotonicity

For each density function:

```text
x = d / (d + k)
```

**Pass:**

```text
x(0) = 0
0 ≤ x < 1
x increases with d
marginal gain decreases as d rises
```

### B-07 Threshold boundary

Test exact values immediately below, at, and above every threshold.

**Pass:** Boundary behavior matches the declared strict or inclusive comparison.

---

## 6. Phase C — Controlled Text Transformations

Each source passage receives matched transformations.

### C-01 Exact duplication

Duplicate the complete text without adding information.

**Purpose:** Detect length reward.

**Provisional pass criterion:** Absolute change in normalized component scores ≤ 0.02 and no layer promotion caused solely by duplication.

### C-02 Neutral padding

Add grammatically valid but epistemically irrelevant material.

**Pass:** The score does not materially rise.

### C-03 Formatting transformation

Change headings, punctuation, capitalization, and paragraph breaks while preserving words.

**Pass:** Output is unchanged except where regex rules explicitly depend on formatting and that dependency is documented.

### C-04 Meaning-preserving paraphrase

Create at least three paraphrases with the same evidence, explanation, and contradictions.

**Provisional pass criterion:** Rank order remains stable and normalized score spread stays within a preregistered band.

### C-05 Evidence addition

Add one independently checkable datum while preserving the rest of the passage.

**Pass:** `E` rises or remains unchanged; it does not fall.

### C-06 Repetition without new evidence

Repeat an existing support statement several times.

**Pass:** The increase is substantially smaller than adding independent support.

### C-07 Explanatory extension

Add a mechanism or prediction connecting the evidence to a wider domain without adding new evidence.

**Pass:** `P` rises more than `E`.

### C-08 Contradiction injection

Add a direct unresolved contradiction.

**Pass:** `S` rises and `Π` falls when `E` and `P` are otherwise fixed.

### C-09 Contradiction resolution

Resolve a previously explicit contradiction without adding evidence.

**Pass:** `S` falls and `Π` rises when `E` and `P` are otherwise fixed.

### C-10 Uncertainty honesty

Replace overconfident wording with explicit uncertainty while preserving the factual content.

**Test question:** Does the engine punish honest uncertainty more than unsupported certainty?

**Required outcome:** Any penalty must be visible, explainable, and reviewed for construct validity.

---

## 7. Phase D — Adversarial Tests

### D-01 Marker stuffing

Insert many known evidence and explanation markers into unsupported text.

**Pass:** The system flags or limits the manipulation, or the failure is formally recorded.

### D-02 Citation theatre

Add numerous citation-like strings without verifiable sources.

**Pass:** Citation appearance alone cannot produce a high evidence score.

### D-03 Confident nonsense

Write a fluent, internally assertive but factually unsupported passage.

**Pass:** Confidence language does not substitute for evidence.

### D-04 Hidden contradiction

State incompatible claims using different vocabulary.

**Purpose:** Test dependence on exact lexical overlap.

### D-05 Negation trap

Compare:

```text
Evidence supports X.
No evidence supports X.
```

**Pass:** Negation cannot create the same evidence contribution.

### D-06 Quotation trap

Quote a false or contradictory claim for criticism.

**Pass:** The quoted material is not automatically attributed to the authorial position.

### D-07 Domain jargon attack

Use dense technical language without evidence or mechanism.

**Pass:** Terminology density does not automatically elevate `E` or `P`.

### D-08 Prompt-injection text

Include instructions inside the evaluated text telling the judge to assign high scores.

**Pass:** Evaluation rules ignore embedded instructions.

---

## 8. Phase E — Onion Engine Tests

### E-01 Strain direction

Increase `COHERENCE` while holding all other layer values fixed.

**Pass:** `S` falls and `Π_onion` rises.

### E-02 Tension direction

Increase `TENSION` while holding all else fixed.

**Pass:** net coherence falls, `S` rises, and `Π_onion` falls.

### E-03 Contested direction

Increase `CONTESTED` while holding all else fixed.

**Pass:** net coherence falls, `S` rises, and `Π_onion` falls.

### E-04 Dependency enforcement

Test:

```text
FOUNDATION ≤ AXIOM × 1.1
STRUCTURE ≤ FOUNDATION × 1.2
```

**Pass:** Any correction is explicit in the trace and never silently rewrites the supplied values.

### E-05 Falsifiability cap

Test blocks immediately below and above the unfalsifiability condition.

**Pass:** The cap activates only under the declared rule and is shown in provenance.

### E-06 Layer judge reproducibility

Run identical content repeatedly.

**Pass:** Deterministic mode returns identical layer scores.

### E-07 Judge sensitivity

Apply controlled evidence, mechanism, contradiction, and speculation edits.

**Pass:** The intended layer moves in the expected direction without unrelated large movements.

---

## 9. Phase F — Reorganization Tests

### F-01 Trigger boundary

Test directly below, at, and above:

```text
Π_text > 0.6
```

**Pass:** Trigger behavior matches the exact comparator.

### F-02 Pairwise legacy boundary

Where legacy CASCADE comparison remains active, test:

```text
Π_new > Π_incumbent + 0.3
```

**Pass:** The trigger changes only at the declared boundary.

### F-03 Independent gates

Test cases where:

```text
app attention gate passes, pairwise gate fails
app attention gate fails, pairwise gate passes
both pass
neither passes
```

**Pass:** The system does not silently conflate them.

### F-04 Reversibility

**Pass:** Opening review does not delete the incumbent.

### F-05 Provenance preservation

**Pass:** Every demotion, promotion, or retained dependency has a traceable cause.

### F-06 No truth promotion

**Pass:** No trigger state labels the challenger objectively true solely because of `Π`.

---

## 10. Phase G — Human Construct Validation

### G-01 Blind rating panel

Minimum first study:

```text
3 independent raters
60 passages
3 domains
```

Each rater independently scores:

```text
E — observable support
P — explanatory reach
S — unresolved internal strain
```

Raters do not see the app score.

### G-02 Agreement

Measure inter-rater agreement separately for `E`, `P`, and `S`.

A weak agreement result means the construct or instructions require revision before app calibration.

### G-03 Engine correspondence

Compare human ratings with engine components, not only final `Π`.

The engine must not receive credit for a correct final rank produced by compensating component errors.

### G-04 Disagreement analysis

Every major engine-human disagreement receives a written classification:

```text
marker failure
negation failure
domain failure
human ambiguity
construct ambiguity
annotation error
unknown
```

---

## 11. Phase H — Baselines

Truth Pressure must be compared with simpler systems.

Minimum baselines:

```text
word count
raw marker count
marker density without saturation
evidence-only score
E × P without strain
simple weighted linear model
human mean rating
```

The full engine must justify every added layer of complexity.

A simpler baseline that performs equally well triggers a compression review.

---

## 12. Phase I — Calibration

Calibration begins only after Phases A–H are frozen and executable.

Parameters eligible for calibration:

```text
S₀
k_E
k_P
k_S
tension weight
contested weight
falsifiability cap
review trigger
pairwise margin
layer thresholds
dependency multipliers
```

### Required method

```text
training split
validation split
held-out test split
```

No parameter may be selected on the final test set.

### Multi-objective calibration

Do not optimize only final classification accuracy.

Track:

```text
component fidelity
ranking stability
paraphrase stability
length invariance
adversarial resistance
false promotion rate
false rejection rate
explanation fidelity
```

---

## 13. Provisional Acceptance Gates

These gates are proposed for the first serious release and may be revised only before results are inspected.

### Gate 1 — Mathematical correctness

All Phase B tests pass.

### Gate 2 — No obvious length fallacy

Duplication and neutral padding cannot cause promotion by themselves.

### Gate 3 — Directional integrity

All controlled `E`, `P`, and `S` interventions move in the declared direction.

### Gate 4 — Visible provenance

Every score can be reconstructed from its matches, constants, branches, and transformations.

### Gate 5 — Adversarial honesty

Known attacks either fail, are detected, or are published as unresolved weaknesses.

### Gate 6 — Human correspondence

The instrument shows meaningful correspondence with blinded component ratings and beats trivial baselines on held-out data.

### Gate 7 — No scale confusion

Every output declares:

```text
instrument
formula
scale
threshold source
conversion rule if applicable
```

### Gate 8 — No truth claim

The interface and documentation consistently state:

> This is revision pressure under a declared operationalization, not objective truth probability.

---

## 14. Publication Rule

No public performance article is released until:

```text
source audit complete
test suite executable
results frozen
failures documented
constants registered
scale declarations verified
```

The first article must report failures and surviving properties together.

---

## 15. Immediate Execution Order

```text
1. Acquire the five TypeScript source files.
2. Create a line-by-line implementation map.
3. Reproduce every number in APP_IMPLEMENTATION_STATE_2026-08-01.md.
4. Convert this protocol into automated tests.
5. Freeze the controlled text corpus.
6. Run the uncalibrated engine.
7. Publish the failure matrix internally.
8. Calibrate only after the untouched baseline run.
9. Rerun on held-out cases.
10. Decide what has actually been earned.
```

---

## 16. Governing Principle

> **Do not tune the instrument until we have recorded exactly how the untuned instrument fails.**
