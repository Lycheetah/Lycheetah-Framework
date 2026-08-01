# SOL Handoff — LAMAGUE Core v0.3

## Release

Complete Operator Algebra and Transformation Contracts.

## Verify

```bash
python -m unittest discover -s tests -v
python benchmark/run_operator_benchmark.py
python -m lamague_core.cli examples/operator_contracts.lmg --pretty
python -m lamague_core.cli --contracts --pretty
python -m lamague_core.cli --composition-matrix --pretty
```

## Immutable decisions

1. No universal identity element is declared.
2. No universal annihilator is declared.
3. Structural inverse and operational reversibility remain distinct.
4. Exchange is structurally self-inverse only.
5. Recurrence termination is domain-dependent.
6. Collapse never simplifies automatically to its target.
7. Ascent does not imply improvement.
8. Structural closure does not prove domain semantic validity.
9. TIM and Microorcim remain external.
10. Operator-law status must remain explicit.

## Suggested tag

```text
lamague-core-v0.3.0
```
