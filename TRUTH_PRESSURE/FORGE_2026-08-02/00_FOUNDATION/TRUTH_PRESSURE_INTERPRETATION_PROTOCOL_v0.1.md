# TRUTH PRESSURE INTERPRETATION PROTOCOL
## Π-IP v0.1 — From Score to Meaning

**Originator:** Mackenzie Conor James Clark  
**Status:** Proposed formal extension  
**Register:** Mathematical identities are DERIVED from the canonical formula. Interpretation rules are PROPOSED and require testing.  
**Date:** 2 August 2026

---

## 1. Purpose

A Truth Pressure score is incomplete unless it explains:

1. what changed;
2. which component caused the change;
3. why that component matters;
4. what action the score supports;
5. what the score does not establish.

The Interpretation Protocol converts `Π` from a headline number into an inspectable research statement.

---

## 2. Canonical Formula

```text
Π = (E · P) / (S + S₀)
```

For two evaluations of the same claim or knowledge block:

```text
Π₁ = (E₁ · P₁) / (S₁ + S₀)
Π₂ = (E₂ · P₂) / (S₂ + S₀)
```

---

## 3. Pressure Attribution Law

```text
Π₂ / Π₁
=
(E₂ / E₁)
· (P₂ / P₁)
· ((S₁ + S₀) / (S₂ + S₀))
```

This exact identity separates total pressure change into three multiplicative causes:

```text
evidence contribution
× explanatory-reach contribution
× strain contribution
= total pressure change
```

### Interpretation

- `E₂/E₁ > 1`: evidence strengthened.
- `P₂/P₁ > 1`: explanatory reach broadened.
- `(S₁+S₀)/(S₂+S₀) > 1`: strain fell, allowing evidence to act more directly.
- A contribution below `1` suppressed total pressure.
- A contribution equal to `1` made no difference.

---

## 4. Additive Attribution Form

```text
Δ ln Π
=
Δ ln E
+
Δ ln P
−
Δ ln(S + S₀)
```

Define:

```text
C_E = Δ ln E
C_P = Δ ln P
C_S = −Δ ln(S + S₀)
```

Then:

```text
Δ ln Π = C_E + C_P + C_S
```

Example:

```text
C_E = +0.22
C_P = +0.08
C_S = −0.15
----------------
net = +0.15
```

Human translation:

> Evidence and explanatory reach increased the challenge, but rising internal strain absorbed a large part of that gain.

---

## 5. Counterfactual Requirements

For a chosen review threshold `T`:

```text
E_required = T(S + S₀) / P
P_required = T(S + S₀) / E
S_max = EP/T − S₀
```

These equations turn the score into a research navigator.

Example:

> The evidence is already sufficient under the current model. The claim remains below the selected review threshold because explanatory reach is too narrow. Collecting more repetitions of the same evidence is unlikely to be the highest-value next step; the model must show what wider pattern it explains.

---

## 6. Saturation Interpretation

The app uses saturation functions of the form:

```text
x = d / (d + k)
```

where `d` is marker density and `k` is a saturation constant.

The elasticity of the bounded score with respect to density is:

```text
∂ ln x / ∂ ln d = 1 − x
```

Meaning:

- when signals are sparse, one additional relevant signal has a large effect;
- when signals are already dense, repetition produces diminishing return;
- `k` determines how quickly the instrument becomes difficult to persuade.

The saturation constants therefore encode the instrument’s standard of sufficiency. They are not cosmetic tuning parameters.

---

## 7. Mandatory Output Structure

Every Truth Pressure evaluation should return seven fields.

### 7.1 Quantity

```text
Π = [value]
scale = [canon | app-text | onion]
```

### 7.2 Input account

```text
E = [value and provenance]
P = [value and provenance]
S = [value and provenance]
S₀ = [value and status]
```

### 7.3 Dominant cause

Identify the largest absolute contribution among `C_E`, `C_P`, and `C_S`.

### 7.4 Human meaning

Explain what the dominant contribution means in the evaluated domain.

### 7.5 Counterfactual

State what would need to change to reach or leave the selected review state.

### 7.6 Decision implication

Use bounded language:

```text
observe
inspect
seek replication
open structured review
retain current foundation
defer
```

Never output automatic replacement solely from `Π`.

### 7.7 Honesty boundary

Every result ends with:

> This score represents revision pressure under the declared operationalization. It does not establish factual truth.

---

## 8. Explanation Grammar

```text
RESULT
What state or change was observed?

CAUSE
Which component moved the score most?

MEANING
Why does that component matter structurally?

NEXT TEST
What evidence, explanation, or strain reduction is now most valuable?

BOUNDARY
What does the score not prove?
```

Example:

> Truth Pressure increased by 41%. Most of the increase came from broader explanatory reach rather than additional evidence. The claim now connects several observations that were previously treated separately. Residual strain remains the main restraint, so resolving the model’s internal contradiction is more valuable than adding another supporting example. This supports structured review, not automatic acceptance.

---

## 9. Forbidden Explanations

The protocol forbids:

- “The claim is true because Π is high.”
- “The AI believes this.”
- “The score proves the theory.”
- “More markers mean more truth.”
- “The threshold is universal.”
- “The app scale and canon scale can be compared directly.”
- “A high-impact claim may bypass weak evidence.”
- “Uncertainty can be hidden behind a single scalar.”
- “A score may be shown without its operational provenance.”

---

## 10. Scale Declaration Rule

Every output must declare its scale before showing a threshold.

For the current app text instrument:

```text
Π_canon = 20 · Π_app
```

For the onion engine, no conversion should be implied merely from output range because its input construction differs.

Mandatory statement when relevant:

> The text-lens app score is a unit-rescaled canon score for identical normalized inputs. The onion score is a separate operationalization and must be interpreted under its own declared rules.

---

## 11. Proposed Evaluation Tests

1. `E` rises while `P` and `S` remain fixed.
2. `P` rises without new evidence.
3. Strain falls after contradiction resolution.
4. Added rhetoric increases marker density but not evidence quality.
5. Paraphrases preserve meaning.
6. Document length doubles without new information.
7. Adversarial marker stuffing.
8. App-to-canon scale conversion.
9. Counterfactual recommendations judged by independent reviewers.
10. Explanations rated for fidelity, usefulness, and overclaim.

---

## 12. Status

### DERIVED

- multiplicative pressure attribution;
- additive logarithmic decomposition;
- threshold counterfactual equations;
- saturation elasticity identity.

### PROPOSED

- seven-field output structure;
- dominant-cause explanation;
- bounded decision vocabulary;
- standard explanation grammar.

### OPEN

- calibration of explanation thresholds;
- independent human evaluation;
- domain-specific interpretation rules;
- zero-valued `E` or `P` in logarithmic attribution;
- uncertainty intervals for all components;
- causal attribution when inputs are statistically dependent.

---

## 13. Core Principle

> **A Truth Pressure instrument should never ask a person to trust a number it cannot explain.**
