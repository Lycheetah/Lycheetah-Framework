# Migration v0.7 → v0.8

v0.7 accepted typed temporal JSON packets.

v0.8 adds native `.lmg` statements that compile into the same packet schema. The bridge equations and classifications are unchanged.

```text
native .lmg source
→ parsed statement AST
→ deterministic temporal packet
→ v0.7 bridge validation
→ TIM / MICROORCIM analysis
```

## New statements

```text
packet
observability
boundary
recover
observe
declare
calculate
infer
unknown
conflict
drift
intent
action
invariant
preserve
block
analyze
```

## Compatibility

- Existing v0.5–v0.7 kernel source remains supported by `lamague_kernel`.
- Existing temporal JSON remains supported by `lamague_temporal`.
- Native temporal source is handled by `lamague_native`.
- No old file is silently reinterpreted as native temporal syntax.
