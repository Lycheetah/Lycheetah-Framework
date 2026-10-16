# Changelog v3.6 — Registry Clock Monotonicity

- Adds an HMAC-authenticated persistent wall-clock high-water mark to the external spent-challenge registry.
- Serializes clock sampling with the SQLite write transaction to avoid request-ordering false positives.
- Pins the replay-window width into the authenticated state; widening fails closed.
- Bounds the request-ID replay cache by its authenticated freshness window and protects live cache rows from ordinary SQL deletion/update.
- Ensures challenge consumption cannot happen before its issue time and uses one time sample for the operation.
- Adds 11 focused tests; retained suite reaches 82 passing methods in one invocation.
- Retains the explicit coordinated-rollback negative control: a coherent old registry snapshot restores a valid old high-water mark.
- No upstream files or hosted services changed.
