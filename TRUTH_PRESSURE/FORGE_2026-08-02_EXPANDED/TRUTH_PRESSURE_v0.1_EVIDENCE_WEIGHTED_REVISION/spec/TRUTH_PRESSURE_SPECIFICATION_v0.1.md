# Truth Pressure v0.1 — Evidence-Weighted Revision Pressure

**Author:** Mackenzie C. J. Clark  
**Project:** Lycheetah / LAMAGUE / Cascade  
**Status:** Experimental software specification  
**License:** MIT

## 1. Canonical definition

Truth Pressure does not estimate the probability that a claim is true.

It estimates the evidence-weighted pressure a claim places on an existing knowledge structure to undergo structured review.

The canonical object is a vector:

```text
Π⃗(K) = (Q, I, X, U)
```

- `Q` = evidential support
- `I` = structural impact
- `X` = contradiction strength against the current foundation
- `U` = residual uncertainty

The scalar review priority is:

```text
π_raw = (Q × I × X) / (U₀ + U)
π̂ = π_raw / (1 + π_raw)
```

`U₀ > 0` is a denominator floor. The metric never emits infinity.

## 2. Evidential support

```text
Q = weighted geometric mean(
    evidence quality,
    source independence,
    reproducibility,
    provenance completeness
)
```

A geometric mean prevents one excellent dimension from fully hiding a zero in another.

Default weights:

```text
evidence quality         0.30
source independence      0.25
reproducibility          0.25
provenance completeness  0.20
```

These are synthetic defaults and require empirical calibration.

## 3. Structural impact

```text
I = √(load-bearing centrality × scope of consequence)
```

Impact answers how central the challenged claim is and how much of the knowledge structure depends on it.

Impact does not increase truth confidence. It only increases the consequence of being wrong.

## 4. Contradiction strength

`X ∈ [0,1]` measures how directly the challenger conflicts with the current foundation.

A well-supported compatible claim may be valuable, but it does not create reorganisation pressure.

## 5. Uncertainty

`U ∈ [0,1]` represents residual uncertainty, unresolved measurement error, ambiguity or model uncertainty.

Zero uncertainty remains finite because `U₀ = 0.10` by default.

## 6. Comparison rule

The source lineage proposes:

```text
Π_new > Π_found + ε
```

v0.1 implements this as:

```text
π̂_new - π̂_found ≥ δ
```

A Cascade candidate must pass:

1. evidential support
2. provenance
3. source independence
4. reproducibility
5. source count
6. contradiction strength
7. absolute pressure threshold
8. relative pressure margin

## 7. States

```text
OBSERVE
REVIEW_PRIORITY
CHALLENGE
CASCADE_CANDIDATE
INSUFFICIENT
HELD_FRONTIER
BLOCKED
```

`CASCADE_CANDIDATE` authorizes structured review. It does not automatically replace the foundation.

## 8. Frontier correction

Earlier material used `Π = 999` and `Π = ∞`.

v0.1 removes both from the numeric domain.

```text
HELD_FRONTIER = maturity state
```

A frontier claim is preserved with provenance and limitations. Conviction, identity, importance and enthusiasm do not promote it.

## 9. Cascade boundary

A candidate opens this protocol:

```text
preserve current foundation
open contradiction ledger
run independent replication
map dependent claims
test candidate foundation
compare explanatory and predictive performance
approve, reject, narrow or defer
```

## 10. Binding limitations

- Truth Pressure is not Bayesian posterior probability.
- It is not a consciousness, morality or metaphysical truth detector.
- It cannot make weak evidence strong.
- A high-impact claim with weak evidence remains `HELD_FRONTIER`.
- Thresholds are not universal constants.
- Inputs can be manipulated; provenance and audit are mandatory.
