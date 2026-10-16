# Lycheetah Closed-Loop Agent Lab v3.2 — Witness Quorum and Freshness

**Current iteration:** independent checkpoint witnesses to detect anchor equivocation and avoid mistaking old but valid checkpoint certificates for current state.

## Quick start

```bash
cd r22_checkpoint_quorum_v3_2
python -m pip install -r requirements.txt
./run_v3_2_tests.sh
python demo_quorum_v3_2.py
```

## What v3.2 adds

- Independent Ed25519 signatures over the exact primary-signed checkpoint head.
- Per-database, one-vote-per-sequence locks using a separate monotonic guard.
- Quorum policy with `n >= 3f + 1` and `q = floor((n + f) / 2) + 1`. For four witnesses and one Byzantine witness, three distinct signatures are required.
- Exact certificate verification, contiguous checkpoint-chain checks, nonce-fresh current-head reports, and an explicit comparison between the chain tip and the fresh quorum head.
- Extractable signed double-vote evidence when two valid certificates conflict at the same database sequence.

## Verification

- 31 focused witness-quorum test methods passed.
- The retained v3.1 suites also passed in separate isolated runs: 33 external-checkpoint tests, and 14, 14 and 13 remote-anchor HTTP tests. Total: 105 test methods across five separate test-process invocations.
- The result does not claim one monolithic run or full upstream CI. Logs are under `r22_checkpoint_quorum_v3_2/verification_logs_v3.2/`.

## Boundary

`SQLiteCASGuard` is a test/reference adapter. It does not prevent coordinated rollback of its own database and the witness ledger if they share a compromised backup/trust domain. Production use requires independently operated witness services, protected signing keys, remote non-rollbackable CAS/high-water storage, explicit roster governance, and a deployment/incident runbook. A quorum certificate proves a quorum attested to a checkpoint; it does not prove the state itself is correct or safe.

The code was built against the observed public upstream commit `8ae1b367dcf09997e82ce66f9ad5d30ff36e5d65`; no upstream files, branches, pull requests or CI were changed. No hosted anchor or Stripe calls were made and no real refunds were created.

For source and threat boundaries, see `r22_checkpoint_quorum_v3_2/SOURCES_v3.2.md` and `THREAT_MODEL_v3.2.md`.
