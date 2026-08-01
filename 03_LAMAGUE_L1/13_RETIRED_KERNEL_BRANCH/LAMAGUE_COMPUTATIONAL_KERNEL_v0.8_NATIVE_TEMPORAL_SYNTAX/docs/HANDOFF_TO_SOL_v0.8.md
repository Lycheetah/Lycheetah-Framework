# SOL Handoff — LAMAGUE Computational Kernel v0.8

## Verify

```bash
python -m unittest discover -s tests -v
python -m lamague_native examples/tim_native_conflict.lmg --pretty
python -m lamague_native examples/microorcim_native_recovery.lmg --pretty
python native_benchmark/run_benchmark.py
```

## Suggested commit

```text
feat(lamague): add native temporal syntax and provenance compiler v0.8
```

## Suggested tag

```text
lamague-kernel-v0.8.0
```

## Do not silently change

1. Codex v1.x and kernel v0.x are separate version lines.
2. Provenance classes remain distinct.
3. Unknowns are never inferred.
4. Conflicts preserve every branch.
5. `preserve` references must exist.
6. Every temporal intent requires an explicit drift dimension.
7. BLACK_BOX output remains a behavioral anomaly signal only.
8. Mythic notation cannot override executable semantics.
