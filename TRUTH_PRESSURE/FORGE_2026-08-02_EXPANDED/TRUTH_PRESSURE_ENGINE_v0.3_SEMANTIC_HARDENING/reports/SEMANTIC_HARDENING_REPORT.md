# Truth Pressure Engine v0.3 — Semantic Hardening Report

## Status

- Canonical scalar: preserved.
- v0.2: preserved unchanged as the prior executable receipt.
- v0.3: development branch, not held-out validated.
- Verification: 24/24 hardening checks passed.
- Strict TypeScript check: passed under the included local Node shims.

## Defects removed

1. Invalid E/P/S values no longer become zero through silent clamping.
2. Normalized pressure is now `Π_norm = Π × S₀`, so it remains in `[0,1]` for every valid S₀.
3. Limiter ties are reported rather than resolved by arbitrary branch order.
4. Evidence-count bonuses now depend on item quality, independence, replication, and provenance.
5. Unverified source locators no longer earn evidence credit merely by appearing in text.
6. Handling quality no longer increases Truth Pressure or review priority.
7. Negated evidence is scoped to the sentence in which it appears.
8. A contradiction resolution can reduce only a matched contradiction; unrelated strain survives.
9. Apostrophes in contractions are not interpreted as quotation boundaries.
10. Onion input scale is explicit. The 1 versus 1.01 discontinuity is removed.
11. Load-bearingness no longer contributes to explanatory power.
12. Judge output is versioned, named, complete, and confidence-bearing.
13. Review plans require explicit approval and reject stale layer states.

## Development-corpus comparison

The same 24 cases were executed under v0.2 and v0.3.

- v0.2 non-zero Π cases: **14 / 24**
- v0.3 non-zero Π cases: **10 / 24**
- v0.2 mean Π: **0.5059**
- v0.3 mean Π: **0.1349**

These figures are diagnostic only. The corpus influenced both branches and is not independent validation.

## Remaining research debt

- Component weights remain authored rather than calibrated.
- Text triage is still pattern-based and English-oriented.
- External source verification is not implemented.
- Sentence-level logic does not solve coreference or general contradiction detection.
- Judge confidence remains self-reported until calibrated.
- No validated review threshold exists.
- No blinded human component study has yet been executed.
- No untouched held-out corpus has yet been scored.

## Next gate

The next serious milestone is **v0.4 measurement protocol**, not another scoring rewrite:

1. freeze a new untouched corpus;
2. create blinded E/P/S annotation packets;
3. collect at least three independent raters;
4. measure agreement before fitting weights;
5. calibrate on development/validation splits;
6. open the held-out set once;
7. publish passes and failures together.

> v0.3 is harder to fool than v0.2, but it has not yet earned calibration or validity claims.
