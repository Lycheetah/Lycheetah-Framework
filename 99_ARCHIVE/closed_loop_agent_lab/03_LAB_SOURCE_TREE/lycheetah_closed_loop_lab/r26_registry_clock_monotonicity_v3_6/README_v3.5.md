# Lycheetah v3.5 — External Spent-Nonce Registry

v3.5 addresses the v3.4 negative result: a locally valid HMAC-authenticated SQLite snapshot can be restored to re-enable a spent challenge. This iteration adds a separate HTTP registry that atomically spends a nonce and signs its responses. The primary-ledger snapshot-restore test is now rejected while the registry remains current.

## Run

```bash
cd r25_external_spent_nonce_v3_5
./run_v3_5_tests.sh
```

## Read first

- `API_CONTRACT_v3.5.md`
- `THREAT_MODEL_v3.5.md`
- `RESULTS_v3.5.md`
- `SCENARIO_MATRIX_v3.5.json`

## Very important boundary

The registry's SQLite file runs on the same local test host. Coordinated restore of both database snapshots allows replay in the deliberate negative control. The design only demonstrates rollback resistance against restoration of the primary verifier database while the independently administered registry remains monotonic. The included service is not safe to deploy as a production service without a separate operational trust domain, TLS, protected storage/key management, failover and anti-rollback recovery design.

No upstream Lycheetah files were edited. No hosted registry, Stripe or other provider was called.
