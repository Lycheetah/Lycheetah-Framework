# Lycheetah Action Guard v0.6 — durable execution-boundary research prototype

## What this pass adds

- SQLite-backed authority epochs, approvals, effect intents, and append-only decision events.
- Single-use approvals: a given approval can create only one effect intent, even if the caller invents a new effect ID.
- A durable state machine: `PREPARED -> DISPATCHING -> SUCCEEDED | FAILED | UNKNOWN`; pre-dispatch invalidations go to `CANCELLED`.
- Distinct `approver_id` and executing-agent `actor` identities in each approval.
- A last local authorization check at the `PREPARED -> DISPATCHING` transition, including authority epoch, expiry, exact action hash (including merge method), and a refreshed trusted pull-request snapshot.
- A fail-closed rule for uncertain outcomes: `UNKNOWN` is not automatically dispatchable again, but a dedicated reconciliation method can record a definitive provider-state observation without issuing another effect.
- A concurrency test proving that eight simultaneous requests cannot consume one approval eight times.
- A test-only fake merge provider with conditional head/base SHA validation and idempotency-key behavior. It never calls GitHub.

## Run the tests

```bash
python3 -m unittest discover -s tests -v
python3 run_verification.py
python3 run_synthetic_scenario.py
```

## State model

```text
human approval bound to exact action
                 |
                 v
              PREPARED  <--- persisted intent, no provider call yet
                 |
   authority + expiry + live-state check inside DB transaction
                 |
                 v
             DISPATCHING  --- provider-specific conditional call ---> outcome
                 |                                                   /   |   \
                 +---------------------------------------------- SUCCEEDED FAILED UNKNOWN
```

`UNKNOWN` means the client cannot establish whether the provider applied the side effect (e.g., request timed out after transmission). It must be reconciled against provider state; do not blindly retry. `reconcile_effect` records a definitive result and supplied evidence, but trusts the caller to authenticate that evidence. A provider-supported idempotency key can make retry safe. Otherwise build a provider-specific reconciliation routine.

## Critical limitations

- Research prototype; no live GitHub connection, token, webhook, or real pull request was touched.
- `approver_id` is recorded as data; this prototype does not authenticate the human or cryptographically bind that identity to an approval UI/session. Production needs verified identity and a protected approval event.
- The `FakeMergeProvider` is deliberately stronger than some real APIs: it stores idempotency keys and rejects stale SHA values at the effect boundary. These properties are test fixtures, not claims about GitHub idempotency.
- The SQLite ledger does not make a remote API transaction atomic. Once a persisted effect is in `DISPATCHING`, revocation cannot reliably cancel a request already in flight. Revocation prevents work that remains `PREPARED` from crossing the local dispatch boundary.
- Real GitHub adapter must pass the approved head SHA using the documented conditional merge parameter, then reconcile timeouts using authoritative pull-request/merge state. Do not assume the GitHub merge endpoint supports a client-provided idempotency key.
- SQLite WAL is useful for a single host/process family; production multi-host execution should use a transactional shared datastore, tightly controlled executor identity, and downstream least privilege.
- No formal verification, security audit, third-party review, adversarial red-team test, or production deployment has occurred.

## Next validation step

Build a dry-run-only GitHub adapter in a disposable test repository. Read the current PR and SHAs, prepare an exact-action approval, re-read immediately before dispatch, pass expected head SHA to the merge endpoint, and record the provider response. Fault-inject timeout-after-send, changed head SHA, duplicate delivery, process restart, and revocation before dispatch. Keep real merges disabled until the reconcile path has been independently reviewed.
