# Human Construct Pilot Preregistration — TP-MEASURE-0.4

## Status

Frozen before human ratings are collected.

## Aim

Determine whether independent raters can apply the proposed meanings of:

- `E`: evidence strength;
- `P`: explanatory reach;
- `S`: unresolved structural strain.

This pilot does not test objective truth and does not provide held-out validation of the engine.

## Materials

- 24 development passages;
- three independently shuffled packets;
- no case titles, families, expectations, or engine outputs visible to raters.

## Primary outcomes

For each component separately:

1. interval Krippendorff-style alpha using squared disagreement;
2. mean exact agreement across rater pairs;
3. mean within-one agreement across rater pairs;
4. pairwise Spearman rank correlations;
5. ambiguity-flag rate;
6. mean rater confidence.

## Engine correspondence outcomes

After ratings are locked:

- Spearman correlation between mean human component score and engine component score;
- mean absolute error after mapping human 0–4 scores to 0–1;
- largest component disagreements by case.

Final Π alone will not be treated as success if component correspondence is poor.

## Interpretation gates

These are provisional research gates, not universal standards:

- `alpha < 0.40`: construct or rubric requires redesign;
- `0.40 ≤ alpha < 0.67`: tentative only, substantial ambiguity remains;
- `0.67 ≤ alpha < 0.80`: usable for provisional calibration with disagreement review;
- `alpha ≥ 0.80`: strong agreement for this pilot corpus.

Confidence and ambiguity must be reviewed alongside alpha. A high agreement produced by uniformly low-information ratings is not sufficient.

## No-moving-target rule

The scoring rubric, packet contents, analysis formulas, and gates cannot be changed after the first completed packet is opened. Any change creates v0.5 and preserves v0.4 results.
