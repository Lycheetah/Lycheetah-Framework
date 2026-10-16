# Changelog — v1.3

## Assurance wire-schema audit

- Expanded the review from policy text rules to `ControlReference`, `Finding`, and `AssuranceReceipt` deserialization in the current inspected repository revision.
- Added a source-equivalent fixture showing eight malformed-type variants that normalize to an existing valid representation under the mirrored coercion expressions.
- Added proposed regression tests and a proposed upstream patch for strict wire-type checks.
- Added a blob-identity preflight utility that requires a clean, named review branch and runs `git apply --check` before any change.
- Preserved a failed sparse synthetic-context check and documented why it is not valid patch-application evidence.
- No change made to the public GitHub repository. Full upstream tests were not run.

- Added a receipt-shaped digest normalization probe covering five nested/top-level wire-type mutations; all five reproduce in the source-equivalent fixture and are rejected by its strict candidate.
- Narrowed the proposed patch to deserialization boundaries, preserving direct dataclass-constructor behavior while compatibility remains unverified.
- Synthetic patch-context reconstruction now passes; full-checkout `git apply --check` remains unrun.
