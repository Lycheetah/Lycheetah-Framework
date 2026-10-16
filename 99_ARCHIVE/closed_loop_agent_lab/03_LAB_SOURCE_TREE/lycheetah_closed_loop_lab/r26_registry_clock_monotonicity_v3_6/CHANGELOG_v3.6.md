# Changelog v3.6 — Registry Clock Monotonicity

- Added an HMAC-authenticated persistent clock high-water mark and fixed replay-window binding.
- Move time sampling inside `BEGIN IMMEDIATE` to avoid false rollback errors from request scheduling.
- Reject challenge consumption before `issued_at_ms`; re-use one clock sample for auth and route predicates.
- Prune request-ID records after they are strictly outside the authenticated replay window.
- Guard active request-ID rows against update and premature deletion; check the request-ID table schema.
- Added 11 adversarial tests for clock rollback, expiry resurrection, SQL cache tamper, replay-window widening, safe pruning, config changes, and single-sample transaction semantics.
- Retained v3.5 registry tests, v3.4 freshness demo, primary-only rollback demonstration, and frozen v3.2 negative controls.

Not a production registry. Coordinated backup rollback remains possible, no hosted service was contacted, and upstream code is unchanged.
