# API Contract v3.3 — Checkpoint Witness Quorum

## Version change

`VERSION` and the witness signature domain changed to `v3.3`. v3.2 votes and freshness reports are intentionally not interchangeable with v3.3 messages. A deployment must explicitly pin the version and plan an authenticated migration; do not silently co-mingle versions.

## New invariants

1. Every witness ID maps to a distinct Ed25519 public-key byte string. Duplicate public-key aliases are rejected before quorum calculation or fresh-head verification.
2. `verify_current_chain()` accepts the raw signed fresh-head reports, database ID, and challenge nonce. It internally verifies signatures, nonce equality, report timestamps, roster membership, uniqueness, quorum agreement, and the chain tip. A caller-created `FreshHeadQuorum` summary is not accepted as a proof.
3. Certificate wire fields have explicit scalar types. In particular, `sequence`, `max_byzantine`, and `threshold` must be integers and never Booleans. `True == 1` in Python must not substitute for JSON type validation.
4. Hashes, key IDs, parent links, roster and nested record containers are validated before they are treated as trusted fields.
5. Reads from a pluggable `MonotonicGuard` are shape/type/digest checked inside witness code; the adapter contract is treated as an input boundary.

## Currentness verification

```python
nonce = new_freshness_challenge()
reports = [w.report_head(database_id, nonce) for w in witnesses]
heads = verify_current_chain(
    certificates,
    reports,
    anchor_keys,
    witness_keys,
    database_id=database_id,
    challenge_nonce=nonce,
    max_byzantine=1,
)
```

Do not replace `reports` with a manually constructed `FreshHeadQuorum`, even if its fields appear correct. The verifier must see the signed evidence itself. Generate a new unpredictable nonce for each check and enforce challenge use/lifecycle in the consuming application.

## Quorum math

For `n` distinct, pinned witness keys and fault budget `f`, require `n >= 3f + 1` and `q = floor((n + f) / 2) + 1`. This gives quorum intersection greater than `f` identities. Distinct keys do not prove independent operators or hosting/control domains; that is a deployment/roster governance requirement.

## Deployment limitation

`SQLiteCASGuard` remains a local test adapter. This module does not provide remote witness hosting, key custody, authenticated roster governance, a production anti-rollback primitive, nonce lifecycle persistence, or a real quorum service. See `THREAT_MODEL_v3.3.md`.
