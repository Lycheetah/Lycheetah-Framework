# TRUTH PRESSURE
## Public Research Statement v1.0

**Author and originator:** Mackenzie Conor James Clark  
**Location:** Dunedin, Aotearoa New Zealand  
**First formulation:** March 2026  
**Research lineage:** CASCADE → Truth Pressure Canon → Sovereign Sol implementation  
**Status:** Experimental research architecture with a working software instantiation  
**Date:** 2 August 2026

---

## 1. The One-Sentence Flag

**Truth Pressure is not a truth detector. It is an experimental instrument for making the reasons behind belief revision visible, contestable, and measurable inside a structured knowledge system.**

That is the public claim. Nothing wider is required.

---

## 2. The Problem

Knowledge systems need more than a confidence score.

A useful system must distinguish between a claim supported by strong evidence, a claim that explains a wide part of a domain, a claim repeated many times without new support, a coherent model challenged by a decisive result, and a chaotic model in which new evidence has no stable target.

Truth Pressure was developed to represent the pressure a claim places on an existing knowledge structure to reconsider its current organization.

The intended output is not:

> “This claim is true.”

The intended output is:

> “Given the evidence, explanatory reach, and unresolved strain represented by this instrument, this claim currently exerts this degree of pressure for structured review.”

---

## 3. Canonical Quantity

```text
Π = (E · P) / (S + S₀)
```

where:

- `E` is evidence strength;
- `P` is explanatory power or structural reach;
- `S` is residual coherence strain;
- `S₀ > 0` is a regularization floor preventing divergence as `S → 0`.

### Human meaning

- Evidence without explanatory reach may establish a local fact without reorganizing a domain.
- Explanatory reach without evidence is speculation.
- High unresolved strain disperses the effect of a new finding across too many unstable possibilities.
- A coherent structure gives contrary evidence a stable target and can therefore be revised more precisely.

Truth Pressure is a **revision-pressure scalar**, not a posterior probability and not a substitute for factual verification.

---

## 4. What the Sovereign Sol App Implements

### 4.1 Text-level instrument: `cascade-score`

The text lens operationalizes `E`, `P`, and `S` using marker densities per 100 words and bounded saturation functions:

```text
density = marker_hits / word_count × 100
sat(d, k) = d / (d + k)
```

The current app-side form is:

```text
Π_app = (E · P · S₀) / (S + S₀)
```

with `S₀ = 0.05`.

This is exactly a rescaling of the canon quantity:

```text
Π_app = Π_canon / 20
Π_canon = 20 · Π_app
```

The rescaling preserves ordering. It changes units, not epistemic meaning.

### 4.2 Knowledge-block instrument: `cascade-onion`

The nine-layer engine scores:

```text
AXIOM · FOUNDATION · STRUCTURE · COHERENCE · RESONANCE
TENSION · CONTESTED · SPECULATIVE · FRONTIER
```

It derives:

```text
E = (FOUNDATION + STRUCTURE) / 2
P = AXIOM
net_coherence = COHERENCE − 0.3·TENSION − 0.2·CONTESTED
S = 100 − net_coherence
Π_onion = (E · P) / (S + 5)
```

It also applies authored governance rules, including a falsifiability cap and dependency constraints between layers.

These rules are implemented facts about the program. They are not automatically promoted into universal theory.

---

## 5. The Three-Scale Rule

| Instrument | Input scale | Formula | Approximate output scale |
|---|---:|---|---:|
| Canon | `[0,1]` | `(E·P)/(S+0.05)` | `0–20` |
| App text lens | `[0,1]` | `(E·P·0.05)/(S+0.05)` | `0–1` |
| App onion engine | `[0,100]` | `(E·P)/(S+5)` | `0–2000` |

No threshold comparison is valid until the scale and operationalization are declared.

```text
0.6 app-scale = 12 canon-scale
```

The app trigger is an authored implementation threshold, not evidence that the canon threshold has been scientifically calibrated.

---

## 6. What the Implementation Has Already Taught

### Finding 1 — Length inflation

The first text implementation used raw counts for evidence and explanatory markers. Because two counts were multiplied, the score grew approximately quadratically with document length.

The system accidentally encoded:

```text
more words = more truth pressure
```

A hard clamp then pinned many texts at `1.000`, hiding the defect. The repair replaced raw counts with marker densities and bounded saturation.

### Finding 2 — Inverted strain

The first onion implementation placed coherence directly in the denominator. Greater coherence therefore lowered Truth Pressure.

```text
coherence 20 → Π 280
coherence 90 → Π 62
```

The repair retained the composite as `net_coherence` and defined strain as its absence:

```text
S = 100 − net_coherence
```

These failures are part of the research record. They demonstrate why implementation is not merely deployment: it is an experiment performed against the theory.

---

## 7. Claim Register

| Claim | Register | Current basis |
|---|---|---|
| The Sovereign Sol app computes the formulas and rules documented in its implementation report | **IMPLEMENTED / MEASURED** | Read from running code |
| The app text score is exactly the canon score divided by 20 for identical normalized inputs | **DERIVED + MEASURED** | Algebra and direct test cases |
| Raw count multiplication caused length inflation and score saturation | **MEASURED** | Observed in the implementation |
| The onion strain direction was inverted and repaired | **MEASURED** | Observed in the implementation |
| `Π = (E·P)/(S+S₀)` is the canonical research quantity | **CANONICAL DEFINITION** | Ratified theory statement |
| The fixed layer thresholds `1.2` and `1.5` are universal | **NOT ESTABLISHED** | Sensitivity and calibration remain owed |
| The app trigger `Π_app > 0.6` is scientifically validated | **NOT ESTABLISHED** | Authored implementation choice |
| Regex marker density measures factual evidence | **NOT ESTABLISHED** | Transparent proxy only |
| The nine layers are naturally derived from first principles | **NOT ESTABLISHED** | Authored and implemented |
| Truth Pressure generalizes across human, social, biological, or physical systems | **INTERPRETIVE / CONJECTURE** | Domain-specific measurement remains owed |
| Truth Pressure measures truth itself | **REJECTED CLAIM** | Outside the construct’s scope |

---

## 8. Strongest Defensible Contribution

A computable importance or surprise score is not new by itself.

The defensible contribution is narrower:

> **A structured knowledge architecture in which a computed revision-pressure quantity contributes to earned layer membership and can trigger an explicit, ordered adjudication process when new knowledge should replace or demote an incumbent foundation.**

The emphasis is on **adjudication**, not mere protection.

The system is designed to preserve prior knowledge as contextualized material rather than simply deleting it when a challenger wins.

This claim still requires stronger comparative testing before performance superiority is asserted.

---

## 9. What Is Not Claimed

This work does not currently claim that:

- the app determines whether a statement is factually true;
- the current text markers are a validated evidence instrument;
- the present constants are optimal;
- the layer cutoffs are universal;
- the app trigger corresponds to a validated critical threshold;
- cross-domain analogies constitute proof of a universal law;
- the historical `√n` spectral model describes the implemented CASCADE engine;
- a high score authorizes automatic belief replacement;
- AI-assisted formalization is equivalent to independent peer review.

---

## 10. Research Method

```text
FORGE
State the idea widely enough to expose its full structure.

REGISTER
Mark each claim as implemented, measured, derived, assumed,
interpretive, or conjectural.

ATTACK
Search for counterexamples, scale errors, inverted variables,
hidden clamps, circular measurements, and prior art.

RETREAT OR REPAIR
Narrow claims that fail. Repair only what the evidence permits.

RETEST
Promote nothing until the revised form survives a new test.
```

The governing principle is:

> A narrow claim that survives is stronger than a grand claim that retreats only after criticism.

---

## 11. Current Calibration Debt

```text
S₀                         0.05
E saturation k             4
P saturation k             3
S saturation k             3
tension weight             0.3
contested weight           0.2
falsifiability cap         70
app reorganization trigger 0.6
```

These constants are not hidden. Their calibration is part of the research program.

Immediate questions:

1. Are the marker categories construct-valid?
2. Do independent raters agree on intended `E`, `P`, and `S` values?
3. Does the score remain stable under paraphrase and document-length changes?
4. Which constants minimize false promotion and false rejection?
5. Are the layer cutoffs robust under sensitivity analysis?
6. Does the system outperform simpler transparent baselines?
7. Does it remain reliable under adversarial rhetoric and marker stuffing?
8. Can it explain its own score in language a non-specialist can contest?

---

## 12. Public Description

### 35-word form

Truth Pressure is an experimental knowledge-revision instrument. It estimates how strongly evidence should make a structured system reconsider a belief, while showing what evidence, explanatory reach, and unresolved strain produced the result.

### 100-word form

Truth Pressure is an experimental epistemic architecture developed by Mackenzie Clark as part of CASCADE and implemented in the Sovereign Sol application. It does not claim to detect truth. It estimates evidence-weighted pressure for structured belief revision using evidence strength, explanatory reach, and residual coherence strain. The application makes those abstract quantities operational through transparent text and knowledge-block proxies, while preserving a record of its own defects, repairs, assumptions, and uncalibrated constants. The research goal is to build an inspectable system that shows not only a score, but why the score changed, what decision it supports, and what evidence could overturn it.

---

## 13. Closing Position

This project should be judged neither as established science nor as empty metaphor.

It is a handcrafted research architecture with a defined quantity, working software, visible assumptions, documented failures, adversarial self-review, explicit calibration debt, and falsifiable next steps.

> **We are not asking anyone to trust the number. We are building a system that must show how the number was earned.**
