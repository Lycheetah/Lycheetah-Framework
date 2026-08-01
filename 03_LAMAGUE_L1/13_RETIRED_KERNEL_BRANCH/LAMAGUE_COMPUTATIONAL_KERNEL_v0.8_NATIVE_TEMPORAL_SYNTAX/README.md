# LAMAGUE Computational Kernel v0.8
## Native Temporal Syntax and Provenance Compiler

v0.8 adds a native `.lmg` language for TIM evidence provenance and MICROORCIM temporal drift while preserving the v0.7 deterministic bridge.

```text
native source
→ native statement AST
→ provenance-preserving temporal packet
→ deterministic bridge validation
→ TIM / MICROORCIM analysis
```

## New native surface

```text
observe  declare  calculate  infer  unknown
conflict preserve block
intent action drift recover invariant
```

## Example

```lamague
packet TIM_E008_NATIVE;
observability INSTRUMENTED_COLLABORATOR;
recover horizon=2;
observe printed key="tur.operator" value="≥" operator="≥";
declare rule key="tur.operator" value="≤" operator="≤";
conflict operator_conflict branches=printed,rule dimensions=OPERATOR,VALUE;
preserve printed;
preserve rule;
block canonical_merge;
analyze;
```

## Version lock

- **Kernel v0.x** is the executable software line.
- **Codex v1.x** is the conceptual and publication line.
- Public packages with v1.0 labels are programme releases and do not supersede kernel versions.

See `docs/CANON_AND_VERSION_MAP_v0.8.md`.

## Verification

```bash
python -m unittest discover -s tests -v
python -m lamague_native examples/tim_native_conflict.lmg --pretty
python native_benchmark/run_benchmark.py
```

## Scope

This is deterministic software verification over synthetic inputs. It does not prove truth, physical validity, alignment, consciousness, or sovereignty.
