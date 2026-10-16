# Lycheetah Closed-Loop Agent Lab v2.1 — Provider Contract Conformance

This iteration tests the boundary left unresolved by the evidence-lease work: what must an external side-effect provider guarantee for retries and authorization predicates to remain trustworthy?

## Run

```bash
python -m unittest -v test_provider_contract.py
python model_check.py > model_check_results.json
```

Requires Python 3.11+ (for typing and SQLite behavior), no third-party packages.

## Contents

- `provider_contract.py` — an atomic condition+effect+idempotency reference, a split-check negative control, and a non-idempotent negative control.
- `test_provider_contract.py` — contract, restart/recovery, race, and negative-control tests.
- `model_check.py` — enumerates the three-event `CHECK`, `UPDATE_FALSE`, `EFFECT` schedule with the check-before-effect ordering constraint.
- `PROVIDER_CONTRACT.md` — proposed minimum provider adapter semantics and external conformance protocol.
- `RESULTS_v2.1.md`, `model_check_results.json`, `test_output_v2.1.log` — run artifacts.
- `PRODUCTION_CONFORMANCE_TEMPLATE.md` — checklist for testing an actual provider rather than a mock.

## Evidence boundary

All execution here is a local in-process/SQLite simulation. No real payment, cloud, deployment, or external provider was called; no live credentials were used. The atomic provider has condition state and effects in the same database, which is deliberately stronger than many external API arrangements. It demonstrates the contract that must be matched, not that arbitrary providers satisfy it.

## Recovery policy helper

`recovery_policy.py` converts an explicitly documented per-action provider profile plus the observed lookup state into `ACCEPT_STORED_RESULT`, `RETRY_SAME_KEY`, or `RECONCILE`. Unknown retention, unknown lookup, a provider without payload-bound durable deduplication, or a condition-sensitive operation lacking commit-time condition enforcement routes to reconciliation. It is deliberately conservative; it does not discover provider guarantees automatically.
