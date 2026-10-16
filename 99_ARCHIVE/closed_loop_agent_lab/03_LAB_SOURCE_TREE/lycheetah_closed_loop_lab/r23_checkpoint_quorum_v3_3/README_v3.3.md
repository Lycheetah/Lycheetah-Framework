# Lycheetah Checkpoint Witness Quorum v3.3

This iteration hardens four verifier-contract classes found and locally reproduced in v3.2: forgeable freshness-summary input, duplicate witness public-key aliases, and bool-as-int certificate fields.

## Quick start

Requires Python 3.10+ and `cryptography`.

```bash
python -m pip install -r requirements.txt
./run_v3_3_tests.sh
python reproduce_v3_2_findings.py
```

The baseline reproduction intentionally reports five `ACCEPTED_BY_V3_2` findings. The v3.3 tests reject those input classes. The tests use ephemeral Ed25519 keys and temporary SQLite files. They make no external network calls.

## Important changes

- `verify_current_chain()` accepts the actual fresh-head reports and validates them internally; it no longer trusts a caller-supplied `FreshHeadQuorum` dataclass.
- Registry validation rejects the same Ed25519 public key being assigned to multiple witness IDs.
- Certificate wire types use strict checks; Boolean values cannot masquerade as integer sequence/fault-budget fields.
- New v3.3 message/signature domains prevent unintended cross-version vote/report reuse.

## Limitations

The SQLite monotonic guard remains reference-only. Independent public keys do not prove independent human/operator failure domains, and this iteration does not deploy remote witnesses, protect private keys, or implement durable challenge nonce consumption. See `THREAT_MODEL_v3.3.md`.
