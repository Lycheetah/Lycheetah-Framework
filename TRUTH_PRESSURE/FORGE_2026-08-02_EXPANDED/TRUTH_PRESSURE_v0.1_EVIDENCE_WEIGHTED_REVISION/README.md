# Truth Pressure v0.1 — Evidence-Weighted Revision Pressure

**Author:** Mackenzie C. J. Clark  
**Project:** Lycheetah / LAMAGUE / Cascade  
**Status:** Experimental deterministic software  
**License:** MIT

Truth Pressure measures how much justified revision pressure a claim places on an existing knowledge foundation.

It does **not** measure how true a claim is.

## Canonical vector

```text
Π⃗(K) = (support, impact, conflict, uncertainty)
```

## Scalar review priority

```text
π_raw = support × impact × conflict / (uncertainty_floor + uncertainty)
π̂ = π_raw / (1 + π_raw)
```

## Critical corrections

```text
999        → HELD_FRONTIER status
infinity   → impossible
importance ≠ evidence
conviction ≠ evidence
candidate  ≠ automatic Cascade
```

## Run

```bash
python -m unittest discover -s tests -v
python benchmark/run_benchmark.py
python -m truth_pressure examples/strong_challenger.json --pretty
```
