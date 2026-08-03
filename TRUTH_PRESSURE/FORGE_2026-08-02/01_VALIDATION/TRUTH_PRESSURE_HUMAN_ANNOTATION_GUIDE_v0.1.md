# TRUTH PRESSURE HUMAN ANNOTATION GUIDE
## TP-HAG v0.1

**Purpose:** Obtain blinded human judgments of Evidence (`E`), Explanatory Power (`P`), and Residual Strain (`S`) before comparing them with the engine.

## 1. General rule

Rate the passage as written.

Do not reward:
- confidence;
- length;
- jargon;
- repetition;
- citation appearance without inspectable sources;
- agreement with your own beliefs.

Do not punish:
- explicit uncertainty;
- narrow scope;
- admission of missing evidence.

## 2. Evidence Strength — E

Question:

> How much observable, inspectable, or independently checkable support is actually presented?

Use a 0–4 ordinal scale:

| Score | Meaning |
|---:|---|
| 0 | No evidence; assertion only |
| 1 | Anecdotal, vague, or uncheckable support |
| 2 | Some concrete support, but limited or dependent |
| 3 | Strong, specific, inspectable support |
| 4 | Multiple independent, well-controlled or replicated supports |

Important:
- A prediction is not evidence until tested.
- A citation marker is not evidence unless provenance is available.
- Repetition is not independence.
- “Studies show” without identifying studies remains weak.

## 3. Explanatory Power — P

Question:

> How much does the passage connect evidence into a mechanism, pattern, prediction, or wider account?

| Score | Meaning |
|---:|---|
| 0 | No explanation |
| 1 | Restates the claim |
| 2 | Explains a limited local pattern |
| 3 | Connects several observations or produces a risky prediction |
| 4 | Unifies a broad set of observations while preserving scope and testability |

Important:
- Breadth of assertion is not explanatory power.
- Jargon is not mechanism.
- A claim that “explains everything” but predicts nothing receives a low score.

## 4. Residual Coherence Strain — S

Question:

> How much unresolved contradiction, ambiguity, scope confusion, or structural incompatibility remains?

| Score | Meaning |
|---:|---|
| 0 | No visible unresolved strain |
| 1 | Minor uncertainty or local gap |
| 2 | Material unresolved issue |
| 3 | Major contradiction or unstable interpretation |
| 4 | Internally incoherent, self-defeating, or impossible to adjudicate |

Important:
- Honest uncertainty is not automatically high strain.
- A clearly bounded unknown may deserve less strain than false certainty hiding alternatives.
- Scope clarification can reduce strain without increasing evidence.

## 5. Separate confidence rating

For every E/P/S judgment, also record confidence:

| Score | Meaning |
|---:|---|
| 1 | Low confidence |
| 2 | Moderate confidence |
| 3 | High confidence |

Low-confidence items should be reviewed for construct ambiguity rather than forced into calibration.

## 6. Required annotation fields

```text
case_id
rater_id
E_score
E_confidence
P_score
P_confidence
S_score
S_confidence
brief_reason
ambiguity_flag
```

## 7. Blinding

Raters must not see:
- app scores;
- expected directional labels;
- other raters’ scores;
- calibration constants;
- intended threshold class.

## 8. Adjudication

Disagreements are not averaged away automatically.

Classify each major disagreement as:
- passage ambiguity;
- rubric ambiguity;
- domain knowledge gap;
- rater error;
- engine-relevant construct dispute;
- unresolved.

## 9. Core principle

> The engine should be calibrated against judgments people can explain, not against numbers people were instructed to produce.
