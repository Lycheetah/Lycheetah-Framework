# SOL Handoff — LAMAGUE Core Algebra v0.1

## Verify

```bash
python -m unittest discover -s tests -v
python benchmark/run_benchmark.py
python -m lamague_core.cli examples/core_return_path.lmg --pretty --graph
```

## Do not silently change

1. TIM and Microorcim remain adapters, not grammar primitives.
2. `↯` means collapse in the core.
3. `∮` is reserved and rejected.
4. Fusion is associative and commutative but not idempotent.
5. Projection is an ordered associative path.
6. Exchange is symmetric but not associative.
7. Macro compression is AST aliasing, not unrestricted language compression.
8. Successful parsing does not prove truth or alignment.
9. Raw alias spellings must remain visible in warnings.
10. Adapter-specific assumptions must be declared.

## Suggested tag

```text
lamague-core-v0.1.0
```
