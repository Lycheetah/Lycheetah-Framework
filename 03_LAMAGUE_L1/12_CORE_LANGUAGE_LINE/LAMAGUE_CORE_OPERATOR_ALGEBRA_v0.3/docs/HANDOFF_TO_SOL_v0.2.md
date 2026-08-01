# SOL Handoff — LAMAGUE Core v0.2

## Release

Primitive Ontology and Type Lock.

## Verification

```bash
python -m unittest discover -s tests -v
python benchmark/run_benchmark.py
python -m lamague_core.cli examples/ontology_lock.lmg --pretty --graph
python -m lamague_core.cli --ontology --pretty
```

## Immutable decisions

1. `∅` is intentional null, not missing data.
2. `Φ↑` is internally `modify(Φ, ↑)`.
3. `Ψ_inv` is internally `qualify(Ψ, inv)`.
4. `InvariantField` is both Field and Invariant.
5. All six core operators accept StateLike operands.
6. Type validity does not prove domain validity.
7. Adapters may add types but may not alias unknown to `∅`.
8. TIM and Microorcim syntax remain outside the core.

## Suggested tag

```text
lamague-core-v0.2.0
```
