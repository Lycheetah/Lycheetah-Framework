# TRUTH PRESSURE UNTUNED ENGINE RUNBOOK
## TP-UER v0.1 — First Source-Faithful Execution

**Originator:** Mackenzie Conor James Clark  
**System:** Sovereign Sol / CASCADE / Truth Pressure  
**Status:** PROPOSED FROZEN RUN CONTRACT  
**Date:** 2026-08-02

---

## 1. Purpose

This runbook governs the first evaluation of the untouched Sovereign Sol Truth Pressure engine against the frozen controlled corpus.

The objective is not to make the engine look good.

The objective is to record, with enough detail to reproduce:

- what the engine actually computes;
- how every value was produced;
- which cases behave as intended;
- which cases fail;
- whether failures come from the formula, operationalization, markers, branches, thresholds, or interpretation.

No constants may be changed before the untuned baseline run is complete.

---

## 2. Required Sources

The following source files must be captured exactly as executed:

```text
lib/cascade-score.ts
lib/intelligence/cascade-onion.ts
lib/intelligence/cascade-judge.ts
lib/intelligence/cascade-reorganise.ts
scripts/verify-truth-pressure.ts
```

Also capture:

```text
package.json
lockfile
runtime version
repository commit hash
working tree status
operating system
timezone
```

Optional related sources:

```text
lib/talk/truth-lens.ts
lib/mystery-school/truth-covenant.ts
```

Explicit exclusion:

```text
lib/care/care-pressure.ts
```

Care Pressure is a separate construct and must not contaminate Truth Pressure results.

---

## 3. Freeze Conditions

Before execution:

1. Save the source commit hash.
2. Confirm whether the working tree is clean.
3. Copy the exact source files into the audit bundle.
4. Hash every copied file.
5. Record all environment versions.
6. Confirm the controlled corpus hash.
7. Confirm the validation protocol hash.
8. Disable any adaptive learning or persistent state.
9. Select deterministic mode where available.
10. Record every unavoidable nondeterministic component.

No code change is permitted after Step 1 without creating a new run identifier.

---

## 4. Run Identifiers

Every execution receives:

```text
run_id = TP-UER-YYYYMMDD-NNN
engine_commit
corpus_version
protocol_version
configuration_hash
```

Example:

```text
run_id: TP-UER-20260802-001
engine_commit: [git SHA]
corpus_version: TP-CC v0.1
protocol_version: TP-VP v0.1
configuration_hash: [SHA-256]
```

---

## 5. Configuration Snapshot

Extract and record every active constant before running the corpus.

Required minimum:

```text
S₀
k_E
k_P
k_S
tension_weight
contested_weight
falsifiability_cap
text_review_trigger
pairwise_margin
layer_thresholds
dependency_multipliers
normalization_basis
clamps
floors
ceilings
```

Each constant receives:

```text
name
value
source_file
source_line
register
effect
```

Registers:

```text
INHERITED
DERIVED
APP-INVENTED
CALIBRATED
UNKNOWN
```

No constant may remain anonymous.

---

## 6. Per-Case Execution Record

For every corpus case, capture:

```text
case_id
input_text
word_count
all regex or marker matches
raw hit counts
normalized densities
saturation constants
E_raw
P_raw
S_raw
E_final
P_final
S_final
S₀
Π_text
Π_canon_equivalent
five-layer scores
nine-layer scores
net_coherence
Π_onion
caps activated
dependencies applied
branches taken
review trigger state
reorganization state
warnings
runtime errors
execution time
```

If a field does not apply, record:

```text
NOT_APPLICABLE
```

Do not omit it.

---

## 7. Repeatability

Run every case:

```text
5 times in deterministic mode
```

Expected:

```text
identical outputs
```

If deterministic mode is impossible:

```text
20 runs per case
```

Then record:

```text
mean
minimum
maximum
standard deviation
rank stability
branch stability
```

Any change in branch, cap, layer, or trigger state across identical runs is a major reproducibility issue.

---

## 8. Pairwise Transformation Analysis

Cases are not judged only in isolation.

Required comparisons include:

```text
unsupported assertion → evidence addition
repetition → independent replication
base claim → explanatory extension
clean claim → contradiction injection
contradiction → contradiction resolution
original → neutral padding
original → exact duplication
original → paraphrase A
original → paraphrase B
evidence statement → negated evidence statement
risk prediction → confirmed prediction
broad claim → explicit scope limit
```

For each pair, calculate:

```text
ΔE
ΔP
ΔS
ΔΠ_text
ΔΠ_canon
ΔΠ_onion
layer movement
trigger movement
```

Then compare observed direction against the frozen directional expectation.

---

## 9. Directional Pass Logic

A case passes only when the declared component movement is respected.

Examples:

```text
Evidence addition:
E_new ≥ E_old

Contradiction injection:
S_new ≥ S_old
Π_new ≤ Π_old

Contradiction resolution:
S_new ≤ S_old
Π_new ≥ Π_old

Exact duplication:
no promotion caused solely by duplication

Negation trap:
"No evidence supports X" must not score like
"Evidence supports X"
```

A final Π value cannot hide a component failure.

Example:

```text
Expected:
E up
P same
S same
Π up

Observed:
E down
P up sharply
S down
Π up
```

Result:

```text
FAIL
```

The final direction is correct for the wrong reasons.

---

## 10. Baseline Run Order

Run all baselines before inspecting full-engine results.

Required:

```text
B0 word count
B1 raw marker count
B2 marker density
B3 saturated marker density
B4 E only
B5 E × P
B6 E × P / (S + S₀)
B7 full text engine
B8 onion engine
```

The full engine must justify each added layer.

If a simpler baseline performs equally well or better, record:

```text
COMPLEXITY NOT YET JUSTIFIED
```

---

## 11. Blind Review Order

Human raters receive the passages without:

```text
case family
expected direction
engine score
engine explanation
threshold class
other rater scores
```

Engine outputs are revealed only after annotation is locked.

The comparison order is:

```text
human E ↔ engine E
human P ↔ engine P
human S ↔ engine S
human ranking ↔ engine ranking
human explanation ↔ engine explanation
```

Never compare only final Π.

---

## 12. Failure Review

Every failure receives:

```text
failure_id
case_id
failure_class
severity
observed behavior
expected behavior
root-cause hypothesis
source location
reproduction steps
whether formula is implicated
whether proxy is implicated
whether threshold is implicated
whether interpretation is implicated
proposed next test
```

A proposed fix is not applied during the baseline run.

---

## 13. Severity

### CRITICAL

The engine:

- produces NaN or infinity;
- reverses the declared direction of strain;
- allows evaluated text to control the evaluator;
- silently compares incompatible scales;
- deletes or rewrites knowledge without provenance;
- labels high Π as factual truth.

### HIGH

The engine:

- rewards exact duplication;
- treats negation as positive evidence;
- is easily driven high by marker stuffing;
- changes trigger state across identical runs;
- hides a cap or clamp;
- shows correct Π from incorrect components.

### MEDIUM

The engine:

- is unstable under paraphrase;
- overweights jargon;
- penalizes honest uncertainty;
- gives poor component-level correspondence with human raters.

### LOW

The engine:

- has explanation wording problems;
- omits a non-load-bearing trace field;
- has small numerical drift that does not alter ranking or state.

---

## 14. No-Fix Boundary

During the untuned run:

```text
DO NOT:
change constants
change markers
change regexes
change thresholds
change labels
remove failed cases
rewrite expected directions
change corpus text
```

Allowed:

```text
repair logging only
repair export formatting only
repair a crash only if the original failing run remains preserved
```

Any behavioral code change creates a new engine version.

---

## 15. Completion Conditions

The untuned run is complete only when:

```text
all source files archived
all hashes recorded
all constants inventoried
all corpus cases executed
all pairwise transformations analyzed
all baselines executed
all failures classified
all results exported
no constants changed
```

---

## 16. Output Bundle

The complete bundle must contain:

```text
SOURCE_SNAPSHOT/
CONFIGURATION.json
CASE_RESULTS.jsonl
PAIRWISE_RESULTS.jsonl
BASELINE_RESULTS.json
FAILURE_MATRIX.jsonl
RUN_SUMMARY.md
HASHES.sha256
```

---

## 17. Governing Principle

> **The first run belongs to the truth about the instrument, not to the reputation of the instrument.**
