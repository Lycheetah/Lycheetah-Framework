# Authority Boundary Lab v0.7 — Separate-Process Crash Recovery

**Status:** research-only test harness. It is not a production authorization service or real provider integration.

## What changed from v0.6

- Host commands and fake-provider commands run in distinct OS processes, allowing process exit and restart to be exercised rather than represented by in-memory exceptions alone.
- The fake provider stores effects in a durable SQLite ledger keyed by `operation_id` and binds the idempotency record to the exact action digest. Reusing an operation ID with a different digest is rejected.
- The authority database stores the active policy revision. Editing a policy file does not silently change the live policy; an explicit `set-policy` operation commits a revision.
- The approval claim uses a durable SQLite transaction. The fake provider then holds an authority-store revision fence while it validates the active policy, exact claimed approval, and revocation state and commits its own separate provider record.
- Recovery checks provider state first. It can reconcile a committed effect after a lost response, and only retries an absent effect from `CLAIMED` or `UNKNOWN` with the same operation ID when the authoritative policy still matches and the approval has not been revoked.
- Recovery refuses to dispatch an `APPROVED` operation that was never claimed, and refuses to replay a `COMPLETED` operation whose provider record is missing.
- Crash injection covers host loss after claim, provider loss before commit, provider loss after commit, host loss after receiving the provider response, and recovery loss after a provider response.
- Race tests check the ordering of provider commit versus a policy update and versus revocation.

## Run

From this directory:

```bash
python -m unittest discover -s . -p 'test_*.py' -v
```

From the lab root, run all retained suites:

```bash
python run_all_tests.py
```

The test pack uses Python's standard library. The child test processes use `python -S` to avoid importing unrelated environment startup hooks.

## State model

`APPROVED -> CLAIMED -> COMPLETED`

A provider/host uncertainty moves an operation to `UNKNOWN`. Recovery may reconcile an existing provider result; a same-operation retry is allowed only when the fake provider's durable idempotency contract and current policy/revocation checks allow it. Ambiguity, a missing record after `COMPLETED`, a foreign effect without a durable claim, policy drift, and revocation are routed to `NEEDS_REVIEW` or `CONFLICT` instead of silently retried.

## Deliberate trust limitations

- `reviewer_id` and `approval_ref` are fixture inputs. No real human identity provider or approval UI exists.
- The tests model process separation/restart, **not OS privilege separation**. The key file is test material and processes execute under the same user during tests.
- The provider is a synthetic SQLite service. It shares the authority database only to emulate a provider-side fencing contract and linearizable policy/revocation check. A real remote provider needs a supported idempotency key plus an API-native conditional/fencing mechanism or a stronger workflow. A local SQLite lock cannot protect a remote service.
- SQLite commits are durable local transactions. They do not create a distributed transaction with a real provider.
- Provider lookups are strongly consistent in this fixture. Eventual-consistency or unavailable real provider lookups must route to reconciliation, not be interpreted as proof that no effect occurred.
- This is not connected to `Lycheetah Guard MCP`, not committed to the repository, and not an independent security review.
