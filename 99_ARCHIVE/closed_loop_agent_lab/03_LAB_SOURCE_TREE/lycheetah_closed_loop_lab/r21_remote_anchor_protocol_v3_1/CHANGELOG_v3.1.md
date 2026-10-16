# Changelog v3.1 — Remote Anchor Protocol

- Added an HTTP-level remote-monotonic-anchor reference client and local service simulator.
- Added detached Ed25519 operator approvals binding the exact state transition.
- Added timestamped/nonce-bound HMAC request authentication and signed Ed25519 responses.
- Added server-side CAS append, durable request idempotency and signed history validation.
- Added a durable authenticated local publish outbox and explicit `UNKNOWN` recovery state.
- Added recovery paths for lost pre-commit and post-commit responses, including service restart.
- Added anti-redirect client behavior, loopback HTTP opt-in, request size limits, terminal outbox-state guards and index/history cross-checks.
- Retained and reran 33 v3.0 checkpoint regression tests alongside 41 remote-protocol tests.
- Result: 74 local test methods passed across four independently executed test groups.
- Limits remain: local service simulator, no true remote/WORM anchor, no upstream code changes or production CI.
