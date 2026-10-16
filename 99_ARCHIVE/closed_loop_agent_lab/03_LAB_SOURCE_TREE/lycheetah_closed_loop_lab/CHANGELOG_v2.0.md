# Changelog v2.0 — Evidence Lease and Pre-effect Reconciliation

- Added SQLite-backed evidence lease authority with atomic predicate check + lease issuance.
- Added per-lease evidence-key records, `ACTIVE` -> `IN_FLIGHT` claim, and write blocking that persists beyond token TTL until the effect result is resolved.
- Added HMAC lease tokens bound to operation ID, action SHA-256, trusted requirement digest, evidence snapshot, issue time and expiry.
- Added lease-enforcing idempotent mock provider. The mock verifies lease binding before the effect and atomically writes its business-effect row and idempotency result.
- Added lease-aware broker adapter with response-loss recovery, renewal of a pinned in-flight lease, and safe expiry before an unclaimed provider call.
- Added explicit `DefinitiveDispatchDenial` handling so a known pre-effect condition failure goes to `RECONCILE`, rather than being misclassified as an ambiguous provider outcome.
- Added provider outcome lookup before current evidence/policy revalidation, allowing already committed effects to be reconciled without repeating the action.
- Added 22 focused lease tests, a 30-case deterministic snapshot/lease race test, and a 200-round concurrent SQLite race experiment. Added fault injection for a provider call that crosses the nominal token TTL.
- Preserved v1.9's 27-test suite as a regression baseline, including its explicit reproduction of the unmitigated snapshot TOCTOU case.
- No upstream source files changed; this remains a local reference prototype.
