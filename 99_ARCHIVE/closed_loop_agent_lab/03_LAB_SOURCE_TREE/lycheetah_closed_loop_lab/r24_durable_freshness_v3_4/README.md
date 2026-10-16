# Lycheetah Durable Freshness Challenge v3.4

A source-pinned reference implementation for durable, one-use verification of the v3.3 checkpoint-witness protocol.

## What it adds

- Persisted nonce challenges bound to one database identity.
- A policy fingerprint covering protocol version, anchor public keys, witness roster/key bytes, Byzantine fault budget, report clock-skew window, and TTL.
- HMAC authentication of every challenge-ledger row, including state and consumption timestamp.
- Strict challenge-row and SQLite schema checks; an incompatible old ledger fails explicitly rather than being silently reinterpreted.
- Signed chain/current-head verification delegated to the retained v3.3 verifier, with atomic one-use consumption after all checks succeed.
- Concurrency, restart, expiry, key/roster/policy-change and tampering regression tests.
- A deliberate backup-rollback negative control showing that local HMAC plus SQLite is not a non-rollbackable trust root.

## Quick start

Requirements: Python 3.10+ and `cryptography` (see `requirements.txt`). From this directory:

```bash
python -m py_compile *.py baseline_v3_2/*.py
python -m unittest -v test_checkpoint_witness_quorum test_durable_freshness_verifier
python demo_durable_freshness_v3_4.py
python reproduce_v3_2_findings.py
```

All demos and tests are local-only. They do not call a hosted checkpoint anchor, Stripe, or another external service.

## Honest verification summary

- 56 test methods pass in the combined v3.3 quorum + v3.4 freshness suite.
- This includes one **intentional negative-control test** that demonstrates a known limitation: restoring a pre-consumption database snapshot allows the old challenge to be accepted again. The test passes because it expects and records that residual weakness.
- Five v3.2 baseline acceptance cases were re-run and reproduced against the frozen baseline. The copied baseline reproduction script's malformed module docstring was corrected in this pack before execution.
- The no-network demo passes and shows one successful current-chain verification followed by rejection of the same challenge as already consumed.
- These are local reference tests, not upstream CI or a production security certification.

## Non-goals / limits

This verifier does not provide rollback resistance against an attacker or operator who can restore the entire SQLite ledger and retain the HMAC key. A production deployment needs the consumed-nonce/high-water state in an independently administered monotonic store, protected key custody, authenticated roster updates, and operator/failure-domain independence. The witness quorum authenticates a checkpoint claim under its stated assumptions; it does not prove the underlying data are true, safe, or policy-compliant, and it is not a standards-conformant RFC 9162 Certificate Transparency implementation.

See `API_CONTRACT_v3.4.md`, `THREAT_MODEL_v3.4.md`, and `RESULTS_v3.4.md`.
