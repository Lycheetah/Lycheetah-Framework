# Results — v2.1 Provider Contract Conformance

## Verified in this session

- Combined command: `PYTHONPATH=<r10>:<r11> python -m unittest -v test_r9_baseline_regression test_evidence_lease_integration test_provider_contract test_recovery_policy`
- Outcome: **78 tests passed** in 3.103 seconds.
- v2.0 preserved regression suites: 49 tests passed.
- v2.1 conformance and recovery-policy suites: 29 tests passed.
- Bounded model checker enumerated 3 valid event schedules: split check-then-act has 1 violating schedule; atomic condition/effect model has 0 in this bounded enumeration.
- Diagnostics emitted: atomic reference meets the modeled requirements; split-check control executes against a stale snapshot; non-idempotent control duplicates its effect after response loss + retry.

## Model result

Given `CHECK` must precede `EFFECT`, the split-check model has one violating schedule: `CHECK → UPDATE_FALSE → EFFECT`. The atomic model has zero violating schedules in the same three-schedule bounded enumeration. This is exhaustive for this small abstract model only; it is not a general proof about distributed systems.

## Provider-control results

The atomic reference provider stores condition state, effect, and idempotency result in the same SQLite database transaction. It passed matching-condition, failed-condition, payload-binding, response-loss recovery, rollback-before-commit, duplicate-dispatch and concurrent condition-update tests.

The check-then-act negative control uses a deliberate interleaving to update evidence after the precheck and before its effect. It applies one effect based on a stale snapshot despite using an idempotency key. This demonstrates that idempotency alone does not eliminate authorization TOCTOU.

The non-idempotent negative control applies the simulated effect twice after a lost response and retry. Its failure is expected and documents why a broker must not classify a provider as safely retryable based on interface shape or a feature flag alone.

## Recovery decision helper

The new helper permits `RETRY_SAME_KEY` only when a definitive not-found is observed and the per-action profile says durable idempotency, payload-mismatch conflicts, a known unexpired retention window, and—when the action depends on changing evidence—commit-time predicate enforcement. Unknown lookup, unknown retention, or unknown conditional guarantees map to `RECONCILE`. A verified committed result may be accepted beyond the idempotency TTL only if the lookup is declared authoritative and the result is bound to the exact operation/payload by the adapter.

## Desk research

Official vendor documentation for Stripe, Amazon EC2, and Amazon ECS `RunTask` was reviewed and summarized in `DOCUMENTATION_FINDINGS.md`. No live provider API was called. The documentation-derived notes are constraints for future adapter-specific tests, not a claim that any of those providers passed this harness.

## Limitations

- No actual Stripe, AWS, GitHub, payment, cloud, or deployment API was called.
- The atomic reference stores condition state and effects in one database. This is stronger than ordinary cross-service composition and must not be conflated with an external API contract.
- The concurrency harness tests local SQLite serialization only. It does not cover multi-host split brain, data corruption, malicious providers, or provider-side partial effects.
- Full Lycheetah upstream suite has not been run and no upstream source files were modified.
