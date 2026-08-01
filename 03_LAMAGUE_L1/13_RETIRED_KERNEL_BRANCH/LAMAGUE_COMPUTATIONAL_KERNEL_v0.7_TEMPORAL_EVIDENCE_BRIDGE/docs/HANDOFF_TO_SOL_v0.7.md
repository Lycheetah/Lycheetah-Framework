# Handoff to SOL / Claude Code

## Release

`LAMAGUE Computational Kernel v0.7 — Temporal Evidence & Drift Bridge`

## Verify

```bash
python -m unittest discover -s tests -v
python -m lamague_kernel run examples/tim_microorcim_bridge.lmg
python -m lamague_temporal temporal_examples/tim_silent_repair_packet.json \
  -o reports/TIM_SILENT_REPAIR_BRIDGE_OUTPUT.json
```

## Frozen decisions

1. Preserve v0.6 behavior and benchmark compatibility.
2. Observed, declared, calculated and inferred branches remain distinct.
3. Exact values, units and operators enter the evidence hash.
4. Unresolved conflicts cannot silently select a branch.
5. Missing intent or action blocks drift metrics.
6. No breach means recovery is `NOT_APPLICABLE`, not perfect.
7. Black-box results are anomaly signals only.
8. Low drift is not evidence of hidden alignment or sovereignty.
9. Deterministic tests are software verification, not external validation.

## Suggested commit

```text
feat(lamague): add temporal evidence and drift bridge v0.7
```

## Suggested tag

```text
lamague-kernel-v0.7.0
```
