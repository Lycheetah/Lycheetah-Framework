# Truth Pressure Shadow Evidence Report

**Version:** TP-SHADOW-EVIDENCE-0.7  
**Generated:** 2026-08-02T03:13:02.579Z  
**Release state:** ENGINEERING_GATE_MET  
**Privacy:** NO_RAW_CONTENT

## Dataset

- Total records: 100
- Text records: 100
- Structured records: 0
- Onion records: 0
- Candidate warnings: 100
- Trigger agreements: 0
- Trigger disagreements: 0
- Trigger not comparable: 100
- Mean candidate pressure: 45%
- Mean legacy pressure: 20%

## Engineering gates

| ID | Gate | State | Detail |
|---|---|---|---|
| GATE-SAMPLE | Minimum engineering sample | PASS | 100/100 privacy-safe shadow comparisons collected. |
| GATE-FINITE | Finite numerical outputs | PASS | No NaN or infinite values found. |
| GATE-RANGE | Normalized range integrity | PASS | All normalized candidate values are within [0,1]. |
| GATE-PRIVACY | No raw-content contract | PASS | Dataset and records declare NO_RAW_CONTENT. |
| GATE-AUTO-REORG | No text-mode structural authority | PASS | Every text-mode record must remain TRIAGE_ONLY. |
| GATE-DISAGREEMENT-REVIEW | Trigger disagreements reviewed | PASS | No comparable trigger disagreements are currently recorded. |

## Candidate pressure distribution

| Normalized range | Count |
|---|---:|
| 0.00–0.19 | 20 |
| 0.20–0.39 | 20 |
| 0.40–0.59 | 20 |
| 0.60–0.79 | 20 |
| 0.80–1.00 | 20 |

## Legacy/candidate delta

- Comparable records: 100
- Mean signed delta: 0.25
- Mean absolute delta: 0.31
- Minimum delta: -0.2
- Maximum delta: 0.7
- Candidate higher: 70
- Candidate lower: 20
- Equal: 10

## Warning frequencies

| Warning | Count | Dataset share |
|---|---:|---:|
| Text mode is pattern-based, English-oriented, and provisional. | 100 | 100% |

## Boundaries

- Engineering gates do not establish scientific validity.
- A 100-case sample is a release-readiness checkpoint, not calibration.
- Trigger disagreement has no invented acceptable rate; each comparable disagreement requires review.
- The report stores no raw analyzed text.


> This report was generated from synthetic records solely to test the pipeline. It is not a research result.
