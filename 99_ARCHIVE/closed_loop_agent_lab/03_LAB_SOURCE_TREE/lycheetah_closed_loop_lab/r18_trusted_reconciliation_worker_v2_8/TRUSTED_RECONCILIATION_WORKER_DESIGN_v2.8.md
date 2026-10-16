# Lycheetah Trusted Reconciliation Worker v2.8

## Purpose

Bridge the authenticated Stripe webhook inbox and the operation ledger without treating webhook snapshot status as proof that a refund is currently terminal. The worker performs **read-only provider retrieval**. It does not create, retry, cancel, or otherwise issue financial actions.

## Normal flow

1. A webhook is signature-verified against the exact incoming body, then its minimal event and a reconciliation job are committed atomically to SQLite.
2. A worker claims a job using a lease and claim token. Queue rows are HMAC-authenticated.
3. The worker resolves the pre-registered operation from the separate operation ledger, verifies its HMAC, then binds event account, target, amount, currency, operation ID, and refund ID.
4. The provider client is pinned to one account scope and test mode. A live-mode client or account-scope mismatch is rejected before any provider retrieval.
5. The worker retrieves the current Refund, validates identity, target, amount, currency, `livemode`, allowed state, and `metadata.lycheetah_operation_id`; it minimizes the observation before writing it to the operation ledger.
6. A terminal provider state is authenticated in the ledger first. Only then may the inbox queue API mark the matching event job `DONE`.
7. `pending` is retried; not-found/transient reads are retried without interpreting absence as non-execution; unsupported states and mismatches become manual review.

## Critical invariants

- `DONE` is not a worker assertion. The inbox implementation enforces it transactionally by checking an authenticated terminal ledger observation for the same operation, account, refund, amount, currency, target, and exact event ID.
- Existing legacy `DONE` jobs without that proof are downgraded to `MANUAL` during initialization. A corrupted authentication record fails closed rather than being quietly repaired.
- Inbox queue and operation ledger must use the same resolved SQLite database file so the `DONE` check and transition share one transaction.
- The operation ledger stores only validated, minimized provider fields and an observation digest, not the raw provider response.
- Webhook payload status is a routing hint, not the terminal truth. The worker reads current provider state.
- Worker is read-only against provider APIs. There is no refund-create POST in this worker.

## State mapping

| Current provider state | Operation ledger result | Queue result |
|---|---|---|
| `succeeded` | `PROVIDER_SUCCEEDED` | `DONE`, after ledger authentication |
| `failed` | `PROVIDER_FAILED` | `DONE`, after ledger authentication |
| `canceled` | `PROVIDER_CANCELED` | `DONE`, after ledger authentication |
| `pending` | `WAITING_PROVIDER` | retry/requeue |
| `requires_action` | `MANUAL` | manual review |
| provider not-found / transient GET failure | unchanged evidence | retry/requeue |
| wrong object/target/account/mode/currency/amount/metadata | `MANUAL` | manual review |
| unknown adapter exception | sanitized `MANUAL` reason | manual review |

## Trust model and residual risks

The trusted computing base includes the process, its config, the external HMAC keys, SQLite file and filesystem ACLs, the real Stripe SDK/API transport, account mapping, and whoever provisions operation intent. HMAC authenticates rows against parties without the key; it does **not** encrypt fields, prevent whole-database rollback/deletion, or protect the key if the process or host is compromised. Backups, access control, key rotation, monitoring, retention, restore testing and independent review remain deployment requirements.

The local fake provider demonstrates interface behaviour only. No Stripe API call was made. Hosted contract conformance, actual event/account mapping, provider pagination/retrieval details, and full upstream repository integration remain unproven. The worker records status after a GET, but does not create an atomic transaction between Stripe state and local SQLite. Future changes in Stripe state are possible after a read; the record is an authenticated observation at a point in time, not a remote lock or provider-side commit lease.

## Running locally

From this directory:

```bash
python -W error::ResourceWarning run_worker_tests_v2_8.py
python -W error::ResourceWarning run_worker_smoke.py
```

Run the historical test groups separately from the lab root as documented in `RESULTS_v2.8.md`. No secrets are required. Smoke uses a local loopback HTTP fake only.
