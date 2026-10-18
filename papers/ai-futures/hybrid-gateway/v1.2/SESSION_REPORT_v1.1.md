# Lycheetah Hybrid Gateway — Cycle 11 Report

**Date:** 18 October 2026 (NZ)  
**Stage:** Local research prototype; continued directly from v1.0, no branch pushed or deployed.

## Research question

Can the existing reviewer desk record **both** positive and negative decisions durably, without allowing a failed audit-write to create a partially admitted knowledge batch?

## Implemented

- `hybrid_gateway/review_journal.py`: signed, hashed local journal records, operator-key witness, append-only SQL schema and restart audit, explicit external-head comparison.
- `hybrid_gateway/durable.py`: optional persistent `journal_v1` admission policy; atomic four-part approval (event + used nonce + decision journal in one transaction); signed rejection with no knowledge event; duplicate-reviewed-batch rejection; migration refusal for unjournalled legacy histories.
- `hybrid_gateway/review_desk.py`: journal-mode support for authentic local browser actions; journal policy checked again on submission; browser failure responses do not claim success.
- `tests/test_review_journal.py`: independent new tests covering rejection durability, approval/event attachment, tampered MACs, independent head anchoring, duplicate/replay, cross-ledger rejection, race between reviewers, failure rollback, legacy upgrade refusal and real loopback HTTP routes.
- `demo_review_journal.py`: scripted, fictional, separate-database v1.0 vs v1.1 demonstration.

## Tests and comparator

Previous cycle: 224 tests. Cycle 11: **254 total** (224 existing and 30 additional unique tests) using Python unittest. Run from a freshly extracted archive again before external handoff.

| Scenario | Legacy signed-v1 desk | v1.1 journal_v1 desk |
|---|---|---|
| Local rejection returns REJECTED | yes | yes |
| Signed rejection retrievable after DB reopen | no | yes |
| Approval recorded as an event | yes | yes |
| Approval and review journal all-or-nothing | no review journal | yes, under tested local transaction |
| A previous rejection prevents same-batch approval after restart | no durable rejection | yes |

These are internal scripted tests with constructed documents and keys; *not* independent AI accuracy, human performance or external effectiveness results.

## Engineering observations

The earlier 1,200 generated SQL differential comparisons remain the strongest check of the temporal **query contract**, but demonstrate a tie with conventional temporal SQL. None of the Cycle 11 work changes that result. Model inference and the canonical CASCADE executable were not run. We did not evaluate a real human review study or independent documents.

## Next frontier

1. Split permit signing into a genuine key-holder process with privilege separation and an authentication boundary; separately model what constitutes real reviewer authorization.
2. Build a controlled key rotation and revocation path with preserved historic verification capability.
3. Add an external journal anchor with retention policy (including rejected decisions) and privacy review.
4. Freeze independently annotated temporal/extraction corpus *before* running model experiments. Report precision, recall, abstention, wrong-field errors, review time and missed facts against both fair SQL+RAG and hybrid systems.
5. Run the canonical SHA-pinned CASCADE source with explicit evidence weights and verify it cannot mutate the authoritative ledger.

## Status

Runnable local functionality, executable adversarial tests, and transparent limits. No claim of production readiness, independent performance advantage, penetration-test certification, deployed human-authenticated approval, or improvement in neural reasoning.
