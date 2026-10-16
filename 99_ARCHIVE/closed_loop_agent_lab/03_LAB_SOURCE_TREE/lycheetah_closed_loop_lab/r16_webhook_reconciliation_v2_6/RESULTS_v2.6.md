# Results — v2.6 signed webhook inbox

**Date:** 2026-10-17  
**Python:** 3.13  
**Dependencies:** standard library only

## Verification

| Check | Result |
|---|---:|
| R16 focused inbox + loopback HTTP tests | 54 / 54 passed |
| Retained R10–R12 + R15 + R16 combined test methods | 256 / 256 passed |
| Bytecode compilation | PASS |
| Loopback HTTP smoke | PASS |
| Hosted Stripe API calls | 0 |
| Real refunds | 0 |
| Upstream repository changes | 0 |

Smoke: first signed event returns `200 / INGESTED`; retry with same event ID and body returns `200 / DUPLICATE`; the correlated event produces `RETRIEVE_CURRENT_PROVIDER_STATE`, never direct `SUCCEEDED`; sensitive sample fields and raw body are not persisted.

## Focused adversarial coverage

- Raw-body byte mutation invalidates signature.
- Old/future timestamps outside configured tolerance are rejected.
- Missing/malformed signature, duplicate `t`, absent `v1`, invalid UTF-8, invalid JSON, duplicate JSON keys, `NaN`, non-object root and oversized body are rejected before ledger write.
- Platform vs connected-account mismatch rejects; reopening a connected-account database under a different expected account cannot route the older event as a valid reconciliation signal.
- Non-test-mode event/refund payloads, unknown event types, malformed refund fields and contradictory `refund.failed` event/status combinations fail closed.
- Duplicate valid delivery produces one stored row and a duplicate acknowledgement; concurrent duplicate submissions produce one `INGESTED` and one `DUPLICATE`.
- Same event ID with different signed payload digest is rejected.
- Local SQLite row tampering is detected on reads.
- Raw payload, arbitrary metadata, descriptive fields, receipt URLs and other unneeded provider fields are not retained.
- HTTP receiver rejects wrong path/method, missing or duplicate Content-Length headers, transfer encoding, and oversized bodies; it does not echo raw payload or signature.

## Limits

The signature verifier is a constrained standard-library reference implementation; production should use Stripe's official SDK and raw-body path. The cumulative runner executes historical suites in isolated subprocesses to avoid version/module-name collisions. The receiver is loopback-only and not a production web server. The fixtures model a narrow subset of Stripe snapshot refund events and do not establish hosted API behavior. Event summaries are authenticated but not encrypted. Retention/deletion controls are still required. A webhook never substitutes for an authenticated retrieval of the current refund state. No complete upstream Lycheetah test suite or CI run was performed.
