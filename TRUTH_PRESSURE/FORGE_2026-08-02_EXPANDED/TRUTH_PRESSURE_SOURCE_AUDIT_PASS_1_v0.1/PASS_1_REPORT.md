# TRUTH PRESSURE SOURCE AUDIT — PASS 1
## Source capture, official gate, frozen-corpus baseline, and first failure matrix

**Originator:** Mackenzie Conor James Clark  
**Audit date:** 2026-08-02  
**Uploaded source commit:** `d8c8a12c52e65fa7f0bc13ae2675f8ad37457572`  
**Uploaded working tree:** dirty / uncommitted changes present  
**Uploaded runtime receipt:** Node `v24.16.0`, npm `11.13.0`  
**Audit runtime available here:** Node `v22.16.0`, npm `10.9.2`  
**Register:** Source findings are IMPLEMENTED; executed outputs are MEASURED; conceptual interpretations are marked separately.

---

## 1. Source capture

The ten uploaded files were copied byte-for-byte into `SOURCE_SNAPSHOT/`.

Because the working tree contained uncommitted changes, the Git commit is not a sufficient reproduction identifier. `SOURCE_HASHES.sha256` is the authoritative receipt for this pass.

---

## 2. Official gate result

The shipped command:

```text
node --experimental-strip-types scripts/verify-truth-pressure.ts
```

completed with exit code `0`.

All six existing behavioral checks passed:

- no hard pin at 1.000;
- repetition invariance for Π;
- contradiction lowers Π;
- S₀ keeps the score finite;
- assertion without theory markers produces low pressure;
- selected weak prose scores below selected reasoned prose.

This is a real success. The repaired scalar behaves as the six gate fixtures expect.

It is not yet broad construct validation.

---

## 3. Frozen-corpus baseline

The untouched `scoreCASCADE` function was run against all 24 preregistered controlled cases.

### Headline result

```text
24 / 24 cases produced Π = 0
0 / 24 requested reorganisation
```

The main cause is structural:

```text
E = saturation(THEORY marker density)
P = saturation(INVARIANT marker density)
Π = E × P × S₀ / (S + S₀)
```

Normal evidential language such as:

> “The model predicted a 12 percent increase. In a preregistered test, the measured increase was 11.8 percent.”

contains no invariant marker under the present regex set, so `P = 0` and therefore `Π = 0`.

By contrast:

> “By definition this proven theorem must be true because therefore the framework explains the pattern.”

produced:

```text
Π = 0.831
```

despite presenting no evidence provenance.

This is the central Pass-1 finding: the text lens currently measures a specific rhetorical co-occurrence pattern more reliably than it measures evidence-weighted explanatory pressure.

---

## 4. What is working

The audit should preserve the parts that genuinely held:

1. **The repaired Π scalar is finite and monotone under its own internal variables.**
2. **Exact repetition preserves Π when the marker ratios remain constant.**
3. **Direct contradiction markers lower Π.**
4. **The onion strain direction is corrected:** higher coherence raises Π when other scores are fixed.
5. **The reorganisation planner is pure, human-mediated, reversible, and refuses to overwrite occupied edge content.**
6. **Sovereign scores are preserved when judge verdicts are applied.**
7. **The code comments are unusually candid about prior defects, assumptions, and calibration debt.**

These are meaningful engineering strengths.

---

## 5. Critical failures discovered

### 5.1 Evidence and explanatory power are not operationalized as named

`cascade-score.ts` labels THEORY-marker density as `E` and INVARIANT-marker density as `P`.

The invariant patterns primarily detect foundational certainty:

```text
always
never
by definition
proven
theorem
must be
cannot be violated
```

Those are not evidence, and they are not explanatory reach.

The product constraint prevents pure assertion from scoring when no theory marker is present, but a small mixture of causal connectors and certainty language can produce extremely high pressure without evidence.

### 5.2 The score is length-invariant while the layer classification is not

Repeating one sentence ten times preserved Π at `0.681`, but changed:

```text
FOUNDATION 1 → 31
THEORY    18 → 89
```

The old length fallacy was repaired in Π but remains active in the visible layer scores through `wordScale` and word-count bonuses.

### 5.3 Honest uncertainty and actual contradiction are merged

The EDGE patterns combine:

```text
contradiction
conflict
uncertain
might
could
perhaps
limitation
open question
not yet
```

This makes honest boundary language increase S alongside real incoherence.

The instrument therefore cannot yet distinguish:

```text
the model contradicts itself
```

from:

```text
the author accurately states what remains unknown
```

### 5.4 The judge and onion engine disagree about what TENSION means

The judge asks:

> How honestly does the block name genuine friction? Naming tension well scores HIGH.

The onion equation then treats a high TENSION score as more strain and lowers Π.

A score of 80 may therefore mean either:

```text
the block contains severe unresolved tension
```

or:

```text
the block handles its tension excellently
```

Those meanings cannot occupy the same variable.

### 5.5 Reorganisation has conflicting definitions

The legacy text lens requires:

```text
Π > 0.6 AND incoherenceHits > 1
```

The newer onion planner explicitly says the trigger must be Π alone because requiring high strain cancels the formula.

Both are live source facts.

The legacy condition is also length-gameable. With the same two contradiction hits held constant, repeating unsupported certainty/theory text eventually diluted S enough to turn reorganisation on:

```text
1,509 words  Π=.316  false
3,009 words  Π=.449  false
7,509 words  Π=.616  true
```

### 5.6 Reorganisation moves content without moving its epistemic metadata

`applyReorganisation` transfers only `content`.

It leaves scores and falsifiability attached to the original layer positions. After a move, the content and the score describing it can refer to different material until a rescore occurs.

### 5.7 The judge parser fails open on partial output

A valid JSON object containing only AXIOM was accepted as a complete verdict.

The parser generated zero scores for the other eight layers, defaulted `falsifiable` to true, and `applyVerdict` replaced all eight existing framework scores with zero.

A malformed model response does not need to be syntactically invalid to damage the block.

### 5.8 Source reveals a fourth Π

Beyond:

```text
canon Π
text-lens Π
onion block Π
```

`computePyramidPi` defines:

```text
E = average file score
P = maximum file score
S = score spread
```

This is a materially different construct sharing the same symbol. The source itself warns that it may share band language with block Π despite using another meaning of S.

---

## 6. Interpretation of Pass 1

The current system is not empty or fake.

It contains:

- a repaired mathematical scalar;
- multiple working scoring engines;
- explicit governance;
- reversible reorganisation;
- human override;
- unusually strong internal documentation.

But the first real corpus run shows that the legacy text lens is not yet a defensible evidence instrument.

Its present success is narrower:

> It reliably detects and combines its own authored rhetorical marker families.

That is a valid baseline implementation fact. It is not yet evidence-strength measurement.

The most important next move is not threshold tuning.

It is separating the constructs before calibration:

```text
EVIDENCE QUALITY
EXPLANATORY REACH
CLAIM LOAD-BEARINGNESS
ACTUAL UNRESOLVED STRAIN
QUALITY OF ACKNOWLEDGING STRAIN
```

Those are currently entangled.

---

## 7. Next execution order

1. Preserve this untouched baseline permanently.
2. Formalize corrected component semantics.
3. Split actual tension from quality-of-tension handling.
4. Replace certainty markers as the source of explanatory power.
5. add schema-completeness validation to the judge parser.
6. make reorganisation move or invalidate metadata with content.
7. unify reorganisation trigger semantics.
8. separate pyramid Π by name and scale.
9. build v0.2 beside v0.1 rather than rewriting the historical source.
10. rerun the frozen corpus unchanged.

---

## 8. Verdict

### What passed

```text
FORMULA-LEVEL REPAIR: PASSED its existing six-fixture gate
SOURCE CAPTURE: COMPLETE
FIRST FROZEN CORPUS RUN: COMPLETE
FAILURE DISCOVERY: SUCCESSFUL
```

### What did not pass

```text
GENERAL-LANGUAGE CONSTRUCT VALIDITY: FAILED
MARKER-GAMING RESISTANCE: FAILED
LAYER LENGTH INVARIANCE: FAILED
SEMANTIC POLARITY CONSISTENCY: FAILED
UNIFIED REORGANISATION SEMANTICS: FAILED
PARTIAL-JUDGE-OUTPUT SAFETY: FAILED
```

This is exactly the kind of result the preregistration was built to make visible.

> **The instrument has now begun telling the truth about itself.**
