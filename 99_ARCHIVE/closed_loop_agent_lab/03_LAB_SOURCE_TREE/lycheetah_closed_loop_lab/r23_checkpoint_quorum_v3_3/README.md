# Lycheetah Closed-Loop Agent Lab — Current Index v3.3

**Current focus:** quorum verifier hardening: reject caller-created freshness summaries, duplicate witness-key aliases, Boolean/int wire-type confusion, and malformed responses from the pluggable monotonic guard.

## Latest artifact: Checkpoint Witness Quorum v3.3

- `r23_checkpoint_quorum_v3_3/checkpoint_witness_quorum.py` updates `verify_current_chain()` to verify raw nonce-bound reports internally; rejects duplicate Ed25519 public keys across witness IDs; strictly validates certificate scalar types; and validates monotonic-guard response shape/types at every read.
- `r23_checkpoint_quorum_v3_3/reproduce_v3_2_findings.py` replays five previously accepted conditions against a frozen copy of v3.2. Results are in `baseline_v3_2_reproduction.json`.
- `r23_checkpoint_quorum_v3_3/test_checkpoint_witness_quorum.py`: 37 tests, including six additions over v3.2.
- The v3.3 focused suite passed, its no-network demo passed, and the four retained v3.1 test groups passed separately. Total 111 passing test methods across five process invocations—not one monolithic run and not upstream CI.

## Download-ready artifacts

- `lycheetah_checkpoint_witness_quorum_v3.3.zip` — standalone v3.3 source, frozen v3.2 baseline, test harness, and docs.
- `lycheetah_closed_loop_agent_lab_v3.3.zip` — complete versioned research history through v3.3.

## Historical path

The series moved from receipt/policy contract audits into witness provenance, durable action outboxes, evidence leases, provider idempotency, Stripe refund recovery, webhook reconciliation, key rotation, remote checkpoint anchoring, and now independent witness quorums. The earlier versions remain in their own folders for traceability.

## Boundaries

- No hosted Stripe/anchor calls, no refunds, and no upstream source changes in this iteration.
- Upstream default branch was last observed at commit `8ae1b367dcf09997e82ce66f9ad5d30ff36e5d65`; no branch, PR or upstream CI was created.
- `SQLiteCASGuard` is reference-only. A real deployment needs separately administered monotonic state, protected independent keys, authenticated roster governance, and actual independent operators/failure domains.
- The protocol authenticates checkpoint history under stated assumptions; it does not prove that underlying data are true, wise, or safe.

See `CHANGELOG_v3.3.md`, `PACK_MANIFEST_v3.3.md`, and `r23_checkpoint_quorum_v3_3/THREAT_MODEL_v3.3.md`.
