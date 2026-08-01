# LAMAGUE Computational Kernel v0.7
## Temporal Evidence & Drift Bridge

## Thesis

Most programming languages type-check data.

LAMAGUE aims to type-check consequential meaning **without erasing where that meaning came from or how it changed over time**.

Version 0.7 preserves the complete v0.6 computational kernel and semantic benchmark, then adds a deterministic bridge joining:

```text
LAMAGUE  — typed consequential meaning
TIM      — evidence provenance and contradiction preservation
MICROORCIM — declared-intent drift across time
```

## Existing kernel retained

The v0.6 kernel remains intact:

- 26 registered semantic operations;
- 9-operation Public Core;
- typed semantic IR;
- authority, affected-party, dissent, value-flow and recovery checks;
- immutable state lineage;
- 20 reference cases;
- 200 synthetic candidate mutations;
- six semantic-equivalence classes.

## New v0.7 bridge

The temporal evidence packet makes these distinctions machine-visible:

```text
OBSERVED
DECLARED
CALCULATED
INFERRED
UNKNOWN
```

Each evidence branch retains:

```text
branch id
semantic key
provenance
exact value
unit
operator
source reference
timestamp
```

Conflicts preserve all branches. The bridge does not choose a winner automatically.

## Temporal layer

The bridge accepts paired intent and action events and calculates:

```text
d_t             instantaneous normalized discrepancy
mu_drift        mean discrepancy
rho_drift       least-squares drift slope
rho_recovery    recovered breach episodes / total breach episodes
invariant preservation
phase risk
operational status
```

Missing intent or action blocks dependent metrics.

Black-box results remain behavioral anomaly signals only.

## TIM silent-repair example

```bash
python -m lamague_temporal temporal_examples/tim_silent_repair_packet.json \
  -o reports/TIM_SILENT_REPAIR_BRIDGE_OUTPUT.json
```

The bundled case preserves:

```text
OBSERVED:   100 ≥ 110 → PASS
DECLARED:   A ≤ RHS
CALCULATED: 100 ≤ 110 is true
```

It then converts three repeated evidence rewrites into a Microorcim drift series:

```text
0, 0, 1, 1, 1
```

## Tests

```bash
python -m unittest discover -s tests -v
```

Current deterministic result:

```text
66 tests passing
```

## Benchmarks

### Semantic integrity benchmark inherited from v0.6

```text
20 reference cases
200 candidate packets
6 equivalence classes
```

### Temporal evidence benchmark added in v0.7

```text
8 frozen synthetic cases
8/8 expected seed matches
```

These verify software behavior against constructed cases. They are not external human or model evidence.

## Binding limitations

LAMAGUE v0.7 does not:

- prove truth from syntax;
- prove alignment, honesty, consciousness or sovereignty;
- detect sufficiently deceptive hidden objectives;
- resolve scientific conflicts automatically;
- validate real-world safety merely because deterministic tests pass.
