# Lycheetah Checkpoint Witness Quorum v3.2

This research iteration extends the v3.1 remote checkpoint protocol with independent witness votes, quorum certificates, nonce-fresh head queries, full certificate-chain continuity checks, and signed equivocation evidence.

## Quick start

Requirements: Python 3.10+ and `cryptography`.

```bash
python -m pip install -r requirements.txt
python -W error::ResourceWarning -m unittest -v test_checkpoint_witness_quorum.py
```

The test uses ephemeral Ed25519 keys and temporary SQLite files. It does not call a hosted anchor, Stripe, or any production service.

## Core protocol

- A witness first validates the primary anchor's signed record with the pinned anchor public key.
- It binds the checkpoint to `(database_id, sequence, record_sha256, previous_record_sha256, logical_sha256, anchor_server_key_id)`.
- Each witness advances only from the guard's exact current head to the next linked sequence. A conflicting head at an already-locked sequence is rejected.
- A certificate is formed only after a configured quorum of unique, trusted witness keys sign the *same* checkpoint statement.
- Fresh head queries include an unpredictable verifier nonce and signed timestamp. A previously captured report cannot answer a new challenge.
- A new verifier validates the chain from genesis. Before treating its tip as current, it also compares the tip with a nonce-fresh witness quorum.
- If two valid quorum certificates conflict at the same database/sequence, `find_equivocation()` extracts overlapping signed votes as evidence of witness key double-signing.

For a four-witness roster with a one-Byzantine-witness budget, the required quorum is 3 of 4. The general threshold is the smallest `q` for which two quorums intersect in more than `f` members: `q = floor((n + f) / 2) + 1`, provided `n >= 3f + 1`. This matters for rosters larger than the minimum: 5 witnesses with `f=1` require 4 signatures, not 3.

## Use limits

This is a protocol reference, not a production service. `SQLiteCASGuard` is a local reference guard. Restoring both a witness's local ledger and its guard file together can erase its remembered high-water mark. In production, each witness needs a separately administered, non-rollbackable CAS/high-water-mark service or an equivalent trusted monotonic primitive, and the witness signing key must be protected independently.

The module does not automatically deploy witnesses, manage keys, authorize changes to the roster, or replace the operator approval process. Roster/key changes require a separate reviewed governance/migration protocol. A quorum certificate authenticates a checkpoint; it does not establish that the underlying state was wise or safe.

Run `python demo_quorum_v3_2.py` for a self-contained, no-network sequence that issues two signed checkpoints, gathers four witness votes, verifies the continuous chain and checks that the tip matches a nonce-fresh quorum head.

See `API_CONTRACT_v3.2.md`, `THREAT_MODEL_v3.2.md`, `SCENARIO_MATRIX_v3.2.json`, and `RESULTS_v3.2.md`.
