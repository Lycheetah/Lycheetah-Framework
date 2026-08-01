# LAMAGUE Temporal Evidence & Drift Bridge v0.7

## 1. Purpose

The bridge prevents three forms of semantic collapse:

```text
provenance collapse
conflict collapse
temporal collapse
```

Provenance collapse occurs when an observed, declared, calculated or inferred value is treated as interchangeable.

Conflict collapse occurs when one branch silently replaces another.

Temporal collapse occurs when repeated behavior is reduced to a single context-free result.

## 2. Evidence branch

An evidence branch is immutable input data:

```json
{
  "branch_id": "obs_tur_printed",
  "key": "tur.operator",
  "provenance": "OBSERVED",
  "value": "100 ≥ 110 → PASS",
  "unit": "",
  "operator": "≥",
  "source_ref": "synthetic_image:E008"
}
```

The exact operator and value are included in the cryptographic evidence hash.

Changing `≥` to `≤` changes the hash.

## 3. Provenance classes

```text
OBSERVED    directly observed or transcribed
DECLARED    supplied by a specification, policy or source
CALCULATED  produced by a deterministic calculation
INFERRED    explicitly inferred rather than observed
```

Equal values do not collapse provenance classes.

## 4. Unknowns

Unknowns remain protected objects:

```json
{
  "key": "hidden_objective",
  "expected_type": "Objective",
  "protected": true
}
```

The bridge does not infer a value merely to make downstream calculation possible.

## 5. Conflicts

A conflict records branch IDs, conflict dimensions and status.

Dimensions:

```text
VALUE
UNIT
OPERATOR
TYPE
PROVENANCE
```

Unresolved conflicts automatically block:

```text
silent_branch_selection
dependent_calculation_from_unresolved_conflict
```

## 6. Intent–action telemetry

For each matched timestamp and key:

```text
d = clip(abs(action - intent) / scale, 0, 1)
```

Multiple dimensions at one timestamp use a weighted mean.

The framework then calculates mean drift, least-squares slope and breach recovery.

## 7. Observability

```text
WHITE_BOX
operational intent-action coherence

INSTRUMENTED_COLLABORATOR
declared-intent behavioral coherence

BLACK_BOX
behavioral anomaly signal only

UNOBSERVABLE
no metric claim permitted
```

Low observable drift never proves hidden alignment.

## 8. Integration with the 26-operation kernel

The original `.lmg` program continues to govern consequential semantic execution.

The temporal packet acts as a typed evidence sidecar:

```text
.lmg programme
+ temporal evidence packet
→ kernel execution
+ evidence/drift audit
```

This preserves backward compatibility while allowing TIM and Microorcim to enter the language without rewriting the existing parser.

## 9. Current status

```text
CANONICAL IMPLEMENTATION
provenance classes
exact branch preservation
conflict blocking
unknown restraint
intent-action discrepancy
rolling drift
recovery
invariant ratio
observability limits
hash lineage

EXPERIMENTAL
automatic natural-language extraction
real scientific inputs
cross-model decoder performance
production safety control
```
