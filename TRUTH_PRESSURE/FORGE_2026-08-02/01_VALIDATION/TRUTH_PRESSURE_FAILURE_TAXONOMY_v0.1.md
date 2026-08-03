# TRUTH PRESSURE FAILURE TAXONOMY
## TP-FT v0.1

**Status:** PROPOSED FROZEN CLASSIFICATION SYSTEM  
**Date:** 2026-08-02

This taxonomy classifies how a Truth Pressure instrument can fail.

---

## A. Mathematical Failures

| Code | Name | Definition |
|---|---|---|
| `MATH-DIV0` | Division failure | Zero or near-zero strain causes invalid output |
| `MATH-NAN` | Non-numeric output | Any NaN or undefined score |
| `MATH-MONO-E` | Evidence reversal | Raising E lowers Π |
| `MATH-MONO-P` | Power reversal | Raising P lowers Π |
| `MATH-MONO-S` | Strain reversal | Raising S raises Π |
| `MATH-SCALE` | Scale mismatch | Values or thresholds from incompatible scales are compared |
| `MATH-BOUND` | Boundary error | Strict/inclusive threshold behavior differs from specification |
| `MATH-CLAMP` | Hidden clamp | Distinct values are silently collapsed by an undocumented cap |

---

## B. Measurement Failures

| Code | Name | Definition |
|---|---|---|
| `MEAS-LENGTH` | Length inflation | Longer text scores higher without added information |
| `MEAS-DUP` | Duplication reward | Repeating the same text materially raises score or layer |
| `MEAS-PAD` | Padding reward | Irrelevant prose raises score |
| `MEAS-NEG` | Negation failure | Negated evidence is counted as positive evidence |
| `MEAS-QUOTE` | Quotation failure | Quoted claims are attributed to the author |
| `MEAS-STUFF` | Marker stuffing | Keyword density can manufacture high scores |
| `MEAS-CITE` | Citation theatre | Citation appearance is mistaken for evidence |
| `MEAS-JARGON` | Jargon inflation | Technical vocabulary is mistaken for explanation |
| `MEAS-SCOPE` | Scope blindness | Narrowing a claim is treated only as loss rather than strain reduction |
| `MEAS-UNCERT` | Uncertainty penalty | Honest uncertainty is punished more than unsupported certainty |
| `MEAS-PARA` | Paraphrase instability | Equivalent meaning produces materially different outputs |
| `MEAS-DOMAIN` | Domain brittleness | Marker logic fails outside the vocabulary it was authored around |

---

## C. Component Failures

| Code | Name | Definition |
|---|---|---|
| `COMP-E` | Evidence construct failure | Engine E does not track observable support |
| `COMP-P` | Explanation construct failure | Engine P tracks rhetorical breadth rather than earned reach |
| `COMP-S` | Strain construct failure | Engine S does not track unresolved contradiction |
| `COMP-CANCEL` | Compensating error | Final Π looks correct because component errors cancel |
| `COMP-DEPEND` | Dependency distortion | Layer dependency rules silently alter source values |
| `COMP-CAP` | Cap opacity | Falsifiability or other caps apply without visible provenance |

---

## D. Governance Failures

| Code | Name | Definition |
|---|---|---|
| `GOV-TRIGGER` | Trigger error | Review or reorganization activates at the wrong boundary |
| `GOV-CONFLATE` | Gate conflation | Attention and pairwise replacement gates are merged |
| `GOV-DELETE` | Knowledge deletion | Incumbent knowledge is removed rather than contextualized |
| `GOV-PROV` | Provenance loss | Promotion, demotion, or correction cannot be reconstructed |
| `GOV-TRUTH` | Truth promotion | High Π is treated as objective truth |
| `GOV-INJECT` | Evaluator capture | Evaluated content changes evaluator rules |
| `GOV-NONDET` | State instability | Identical input produces inconsistent governance outcomes |

---

## E. Calibration Failures

| Code | Name | Definition |
|---|---|---|
| `CAL-OVERFIT` | Corpus overfit | Constants are tuned to the evaluation set |
| `CAL-LEAK` | Test leakage | Held-out information influences tuning |
| `CAL-THRESH` | Threshold fragility | Small threshold changes reverse many outcomes |
| `CAL-CONST` | Constant fragility | Small constant changes destabilize rankings |
| `CAL-BASE` | Baseline failure | Simpler model performs equally well or better |
| `CAL-HUMAN` | Human divergence | Engine components weakly correspond with blinded raters |
| `CAL-IMBAL` | Objective imbalance | Final accuracy hides failures in stability or adversarial resistance |

---

## F. Interpretation Failures

| Code | Name | Definition |
|---|---|---|
| `INT-NAKED` | Naked score | Number is shown without cause or provenance |
| `INT-CAUSE` | Wrong cause | Explanation names the wrong dominant component |
| `INT-BOUND` | Missing boundary | Result omits what Π cannot prove |
| `INT-ACTION` | Over-action | Score recommends acceptance or replacement without review |
| `INT-UNITS` | Missing scale | Instrument and units are not declared |
| `INT-CF` | False counterfactual | Suggested next step does not follow from current components |
| `INT-CERTAINTY` | Certainty inflation | Language is stronger than the evidence register |

---

## G. Research-Process Failures

| Code | Name | Definition |
|---|---|---|
| `PROC-MOVE` | Moving target | Success criteria change after results are seen |
| `PROC-HIDE` | Failure suppression | Failed cases are removed or omitted |
| `PROC-RETRO` | Retrospective preregistration | Tests are described as predeclared after execution |
| `PROC-MIX` | Register collapse | Assumed, measured, derived, and interpretive claims are mixed |
| `PROC-SOURCE` | Source drift | Prose description replaces what the code actually does |
| `PROC-PUBLISH` | Premature claim | Public claim exceeds completed validation |

---

## Severity Rule

Severity depends on consequence, not embarrassment.

```text
CRITICAL
Can reverse meaning, capture governance, compare wrong scales,
or promote a score into truth.

HIGH
Can materially game ranking, layer, or trigger behavior.

MEDIUM
Reduces construct validity, stability, or human usefulness.

LOW
Presentation or trace defect without material score impact.
```

---

## Governing Principle

> **A named failure can be tested. An unnamed failure becomes mythology.**
