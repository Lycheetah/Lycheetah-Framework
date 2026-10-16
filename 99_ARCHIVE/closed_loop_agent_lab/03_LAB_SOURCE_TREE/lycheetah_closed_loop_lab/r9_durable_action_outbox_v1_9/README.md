# Lycheetah Closed-Loop Agent Lab v1.9 — Durable Action Outbox

## Research question

What happens when an authorization is successfully consumed, but the process crashes before its corresponding external action has been recorded—or when the external action succeeds but its response is lost?

## What this pack contains

- `durable_action_broker.py` — standalone reference design for authenticated admission, atomic local consume+outbox, recovery and dispatch.
- `test_durable_action_broker.py` — 27 local tests including crash simulation, provider response loss, persisted-intent tampering, concurrent dispatch, a non-idempotent provider refusal, and an explicitly open evidence-provider TOCTOU race.
- `FAULT_MATRIX_v1.9.md` — expected outcomes at each fault boundary.
- `DESIGN_AND_THREAT_MODEL_v1.9.md` — architecture, guarantees, assumptions and non-guarantees.
- `UPSTREAM_INTEGRATION_PLAN_v1.9.md` — staged plan to integrate into the real Lycheetah Assurance Runtime.
- `RESULTS_v1.9.json` and `test_results_v1.9.log` — captured local test outcomes.
- `SOURCE_PIN.json` — inspected source revision and relevant upstream paths.

## Quick start

```bash
cd r9_durable_action_outbox_v1_9
python -m unittest -v test_durable_action_broker.py
```

Only the Python standard library is required.

## Design in one sentence

Consume an authenticated witness and insert a durable pending action in one local SQLite transaction; dispatch from the outbox using a stable operation ID; require the remote provider to durably bind that ID to the request digest and effect in its own transaction, or do not auto-retry and route ambiguity to reconciliation.

## Current maturity

**Research reference prototype — not production-certified and not integrated into the upstream package.** The runtime adapter is synthetic, the provider is a second SQLite database simulating a cooperating remote API, and crashes are injected at explicit cut-points. No live payment, deployment or third-party operation is executed.
