# Results — Lycheetah Stripe Recovery State Audit v2.4

**Run date:** 2026-10-17  
**Python runtime:** 3.13  
**Dependency surface:** Python standard library only

## Executed locally

- Focused R14 suite: **76/76 test methods passed** in 7.104 seconds.
- Retained R10–R12 suites plus R14: **193/193 test methods passed** in 16.401 seconds.
- Python compilation of adapter, simulator, tests and complete-runner: passed.
- Local loopback smoke: passed. The simulated provider committed a refund, dropped the response, and the adapter recovered using the same persisted key. Final summary: one simulated effect, two POST requests, `SUCCEEDED`.

## Newly added audit cases

- A persisted `READY`, `UNKNOWN`, or `CONFLICT` operation cannot bypass the local retry cutoff by using the direct dispatch path.
- The durable `IN_FLIGHT` state is committed before the initial refund POST.
- Recovery of `IN_FLIGHT` reuses the same persisted idempotency key and pinned body.
- `WAITING` refunds are re-queried and move to the current verified provider state rather than remaining stale forever.
- Target Charge/PaymentIntent preflight is checked before the first refund POST.
- Provider response storage is minimized to allow-listed recovery fields. `client_secret`, arbitrary provider metadata and free-text error messages/URLs are not persisted.
- Local tampering of stored state, response and request fingerprint is tested; HMAC is explicitly treated as integrity protection, not encryption.

## External actions and limits

No hosted Stripe API calls were made. No real Stripe keys were supplied. No refund was created. The local simulator used a mock test-shaped key on `127.0.0.1` only. No upstream Lycheetah source file changed, and the complete upstream package CI was not run.

These test counts are test-method counts. Retained harnesses and the local simulator are not independent proofs, and the simulator does not fully model Stripe. Hosted Stripe test-mode conformance and production controls remain separate promotion gates.
