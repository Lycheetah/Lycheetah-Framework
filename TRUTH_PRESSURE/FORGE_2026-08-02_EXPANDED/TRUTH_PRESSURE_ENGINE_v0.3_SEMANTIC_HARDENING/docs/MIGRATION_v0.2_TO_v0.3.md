# Migration v0.2 → v0.3

## Breaking changes

1. Core component values outside `[0,1]` now throw errors.
2. `appScaleFactor` is removed. Use `piNormalized = piCanon × s0`.
3. Onion scale must be declared as `unit` or `percent`.
4. Onion v3 separates load-bearingness and predictive reach.
5. Judge JSON uses `TP-JUDGE-0.3` with a named `layers` array.
6. Review application requires `approved=true` and returns a transaction result.
7. Evidence provenance is a structured record with an explicit status.

v0.2 remains preserved as the prior executable receipt.
