# Results — R17 Transactional Webhook-to-Reconciliation Queue v2.7

**Checked:** 2026-10-17. Python 3.13. Standard-library-only reference code.

## Results

| Test group | Methods passed | Execution mode |
|---|---:|---|
| R10 evidence lease/durable outbox | 49 / 49 | separate process |
| R11 provider contract | 29 / 29 | separate process |
| R12 refund recovery policy | 39 / 39 | separate process |
| R15 Stripe HTTP adapter | 85 / 85 | separate process |
| R16 inbox + HTTP and R17 queue | 84 / 84 | separate process |
| **Latest watchdog-bounded cumulative run** | **286 / 286** | **one completed invocation** |

Also passed: Python bytecode compilation, loopback HTTP smoke, archive checks in final pack.

## Added R17 cases

- Inbox and reconciliation job commit atomically.
- Queue-write trigger failure rolls back the event insert and makes the HTTP receiver return `503` rather than acking lost work.
- Concurrent duplicate event ingestion creates only one queue job.
- Missing operation correlation goes to manual reconciliation.
- Two concurrent workers cannot both claim one job; fifty separate two-worker claim races yielded one winner per event.
- Claim token digest, not plaintext token, is stored.
- Wrong worker/token, expiry, stale token, account-scope switch and tampered row are rejected or routed to manual state.
- Retry delay, attempt limit, expiry-after-attempt-limit and manual escalation are checked.
- Upgrade backfills authenticated legacy inbox rows; a tampered legacy row aborts migration.
- Webhook-reported `succeeded`, `pending` or `failed` status never becomes a queue-level refund success result.

## Operational smoke

The loopback HTTP smoke returned `200 / INGESTED` for first signed delivery and `200 / DUPLICATE` for redelivery. Its correlated event led to `RETRIEVE_CURRENT_PROVIDER_STATE`. No hosted Stripe requests were made and no real refunds were created.

## Important reproducibility note

Earlier unbounded cumulative-runner attempts intermittently hung within the retained R15 local HTTP simulator, even though R15 passed when run independently. The runner now imposes a timeout for each group and executes the focused R16+R17 runner as a subprocess. The latest watchdog-bounded cumulative invocation completed all five groups successfully (286/286). This remains one local end-to-end test-runner pass; repeat it in CI to establish stability.

## Not established

- No upstream Lycheetah repository code was changed.
- No hosted Stripe account, webhook endpoint or connected account was exercised.
- No production deployment, performance load, multi-host database behavior, authenticated worker identity scheme or whole-database rollback detector was validated.
- Custom signature verification and loopback HTTP receiver are not production substitutes for the Stripe SDK and hardened web server.
