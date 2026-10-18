# Lycheetah Hybrid Gateway — Cycle 12 research continuation

## Change
Introduced `hybrid_gateway/external_witness.py`, a separately retained, HMAC-authenticated journal checkpoint. This is intended to detect rollback or truncation of the local review-decision journal when the checkpoint and witness key are retained outside the SQLite database.

## Tests
The inherited v1.1 suite passed 254 tests before modifications. Five new focused tests pass, covering empty journal checkpoints, incorrect witness key, incorrect ledger identity, forged count, and short witness key refusal. A complete combined suite was not confirmed during packaging; do not report 259 tests as verified.

## Boundaries
The external checkpoint must actually be retained outside the ledger's administrative trust boundary. An attacker controlling both the database and external witness key can forge history. The current tests do not establish full rollback detection on populated journals or production security.

## Next
Add populated-journal integration tests, enforce independent witness storage and identity, connect a genuine reviewer identity provider, then conduct real human-review and neural extraction trials.
