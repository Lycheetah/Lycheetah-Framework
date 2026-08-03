# Migration from the Sovereign Sol Truth Pressure implementation

## Historical engine retained

Do not delete or rewrite:

- `cascade-score.ts`
- `cascade-onion.ts`
- `cascade-judge.ts`
- `cascade-reorganise.ts`

They are the evidence-bearing historical implementation.

## Recommended integration

1. Add this package beside the old modules.
2. Route new structured assessments through `scoreStructuredAssessment`.
3. Use `analyzeText` only as a provisional pre-screen.
4. Replace permissive judge parsing with `parseStrictJudgeVerdict`.
5. Introduce separate fields for `tensionMagnitude` and `tensionHandlingQuality`.
6. Keep the old pyramid score visible under a distinct name rather than calling every instrument Π.
7. Require an explicit configured threshold before any review proposal can fire.
8. Store original layers before applying a reversible review plan.

## Semantic corrections

| Historical field | v0.2 meaning |
|---|---|
| Invariant-marker density used as P | Load-bearingness only |
| Theory-marker density used as E | Not accepted as evidence by itself |
| TENSION score | Split into magnitude and handling quality |
| CONTESTED score | Split into magnitude and handling quality |
| Partial judge JSON | Rejected |
| Reorganisation move | Content and metadata move together |
| Threshold at equality | Does not fire; strict greater-than |

## Register

The v0.2 component aggregators and text heuristics are **ASSUMED / PROVISIONAL** until calibrated against blinded human ratings and held-out cases.
