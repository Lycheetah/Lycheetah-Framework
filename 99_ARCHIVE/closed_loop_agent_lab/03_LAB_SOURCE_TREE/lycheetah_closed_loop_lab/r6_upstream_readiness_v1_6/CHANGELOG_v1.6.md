# Changelog v1.6

- Consolidated receipt and policy contract hardening into an upstream-readiness handoff.
- Added a source-pinned preflight that simulates patch application in a temporary copy and syntax-compiles modified source without mutating the checkout.
- Added a read-only persisted policy/receipt compatibility inventory, based on bundled old-schema snapshots and candidate schemas.
- Added regression tests for explicit null `cap_reason` normalization, unknown control properties and policy text-rule type coercion.
- Added proposed PR description and an ordered promotion checklist.
- Corrected the compatibility audit sequence: inventory persistent records against the untouched base **before** applying schema/parser changes.
- No upstream branch/PR or package CI run was possible; see `INTEGRATION_STATUS.md`.
