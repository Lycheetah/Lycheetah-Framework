# Changelog v3.3 — Quorum Verifier Hardening

- Closed a currentness-verification API gap by accepting and validating signed fresh-head reports inside `verify_current_chain()` instead of trusting a caller-constructible summary object.
- Rejected duplicate Ed25519 public-key bytes across distinct witness IDs so one key cannot count multiple times toward the quorum threshold.
- Added strict certificate scalar/container validation to prevent Boolean values from passing as integer sequence/fault-budget values.
- Added strict shape/type/digest validation for values returned by the pluggable monotonic guard, including the witness `attest()` path.
- Versioned witness vote/report domains to v3.3 to prevent cross-version message reuse.
- Reproduced five accepted baseline cases against frozen v3.2 source; added six focused tests. Current suite 37 passed; four retained v3.1 groups 74 passed, in five process invocations total.
- No hosted APIs or upstream source changes. Production guard, key custody, roster governance, and true operator independence remain unimplemented.
