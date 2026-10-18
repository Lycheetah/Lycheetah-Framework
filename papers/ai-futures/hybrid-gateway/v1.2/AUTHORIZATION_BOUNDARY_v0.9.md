# Authorization Boundary v0.9 — threat model and verifiable contract

## The violation repaired

In v0.8, `SQLiteLedger.commit_batch(..., reviewer_approved=True)` treated a caller boolean as authorization. That is an application-level trust assumption, not a verifiable signal. An AI controller or buggy caller able to invoke this API could accidentally or deliberately claim a review occurred.

## New mode

`SQLiteLedger(path, require_signed_approval=True)` persists the strict setting. A permit created by an operator-controlled signing service contains:

- `purpose`: domain-separation string `lycheetah.hybrid-gateway.batch-admit.v1`
- `key_id`: externally maintained identifier, not evidence of a human person
- `ledger_id`: random identity persisted with the database, separate from event head
- `nonce`: 24 random bytes hex-encoded; consumed once, transactionally
- `issued_at`, `expires_at`: real-time approval window up to 600 seconds
- `recorded_at`: the exact requested logical history timestamp; not necessarily signing time
- `source_digest`, `plan_fingerprint`, `registry_fingerprint`, `ledger_head_at_stage`
- `batch_digest`: hash of the full coverage receipt and staged candidate evidence
- `signature`: HMAC-SHA256 under a caller-provided 32+-byte shared secret

The verifier checks the entire unsigned payload with constant-time `hmac.compare_digest`, validates TTL and current time, then uses `BEGIN IMMEDIATE` to check the nonce, source authority, stage fingerprints, and current event head. Event and public approval envelope are committed together; a failed write rolls back both. `audit_persisted_approvals()` rechecks archived MAC and attachment to the chain after restart.

## Security assumptions and exclusions

1. A separate trusted component has custody of the HMAC secret, and the model does not receive it or the ability to request arbitrary signatures. A signer controlled by the model defeats the design.
2. The signer must independently authenticate and display the entire review decision to the person. This repo does **not** implement that authentication or UI.
3. SQLite files are in a trusted local filesystem. Direct writes to the DB or programmatic runtime mutation are outside this module's protection. A copied database carries its original `ledger_id` and approvals.
4. HMAC proves only shared-secret possession. It cannot distinguish two people or services with access to the same secret. The audit includes an operator key ID, not human identity provenance.
5. No trusted wall-clock attestation is preserved in events. Historical MAC audit verifies the signature and local event attachment, **not** proof that the permit was unexpired at the actual original commit time.
6. Storing SHA-256 digests without external anchoring does not prove that a privileged attacker did not replace the whole database. Anchor head digests out of band.
7. Legacy non-strict databases still allow `reviewer_approved=True` to support older tests and educational demos. The strict setting is persisted when enabled and a reopened strict ledger refuses the boolean bypass. Do not use a legacy database for sensitive operations.
8. No external tool/action execution is performed by this gateway. Signed approval permits only a local knowledge-batch commit; it is not a general agent effect permit.
9. The full source quote is included in the signed *batch digest*, but the archive stores the public permit and event, not a complete signed reviewer-screen snapshot. A complete consent-receipt system needs independent presentation and retention controls.

## Test evidence

36 new tests specifically cover unsigned bypass, restart persistence, forged and wrong keys, revocation/rotation, expired and future permits, bounded TTL, tampered purpose/nonce/digest, commit-time mismatch, atomic write rollback, same-nonce replay, distinct-database replay, archived MAC corruption, event-link corruption, ledger-ID corruption, and post-restart audits.

**Status:** internally reproducible reference mechanism; not certified identity/security infrastructure.
