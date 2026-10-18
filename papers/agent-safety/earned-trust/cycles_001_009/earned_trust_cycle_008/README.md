# EARNED TRUST — Cycle 008: Crash-Safe Authority

**Date:** 18 October 2026 (Pacific/Auckland)  
**Status:** `LOCAL_SYNTHETIC_ENGINEERING_TESTED / REAL_FRAMEWORK_NOT_EXECUTED / NOT_DEPLOYED`  
**No live provider calls, production payments, GitHub writes or remote actions.**

This cycle investigates the failure window between a *local dispatch authorization* and a *remote effect/acknowledgement*. It preserves the upstream Cycle 007 `dispatch_fence.py` byte-for-byte as `upstream_dispatch_fence.py`, and builds a durable outbox on the **same authority SQLite database**. The simulated provider uses a **separate SQLite database**, a single-use effect ID and an HMAC-authenticated response. All cryptographic keys are synthetic fixtures in `lab_fixture.py`.

## Reproduce

Python 3.10+ standard library, local machine. From this folder:

```bash
python3 -W error::ResourceWarning -m unittest -q test_crashsafe_authority
python3 run_scenarios.py
python3 run_historical_recheck.py /path/to/earned_trust_cycles_001_007_complete.zip
sha256sum -c SHA256SUMS.txt
```

The last command checks all files except itself. The native Lycheetah Framework integration is **not** satisfied by these tests; the provided C007 bridge is in the historical ZIP and still requires a genuine Lycheetah-Framework checkout.

## Distinct phases

1. **Prepare** a proposed effect under the existing C007 approval, evidence and source-ancestry rules.
2. **Enqueue** a unique outbox row while the effect is still `PREPARED`.
3. **Reserve send** within `BEGIN IMMEDIATE`: recheck action, witness seal, authority epoch, expiry, source challenges, evidence subject/revision and audit state; in the same transaction, change `PREPARED/PENDING -> DISPATCHING/SENDING` and write one audit event.
4. **Call simulated provider** outside the transaction. It can commit before a process crash or before its response is received. A later challenge cannot retroactively cancel the effect.
5. **Recover** a stranded `SENDING` row to `UNKNOWN`; no implicit resend. An independently signed *fixture* response may reconcile it to `ACKED`/`FAILED`.

This does **not** implement a general exactly-once delivery protocol. Instead it chooses conservative liveness: a lost send can become permanently `UNKNOWN` until an authoritative status query and a human-safe reconciliation procedure. The fixture provider has idempotency, but a real provider's retention window, eventual consistency and authorization model must be assessed independently.

## Measurements, not deployment claims

| Experiment | Observed |
|---|---|
| Unit tests on Cycle 008 | 46/46 pass, with ResourceWarnings treated as errors |
| Fixed authored scenario matrix | 22/22 observed outcomes match expectations |
| Process exits after reservation and provider commit | Exit codes 90 and 91; no automatic duplicate dispatch on recovery |
| Process exit after challenge commit | Exit code 93; challenge remains binding in authority DB |
| Process exit before challenge transaction commit | Exit code 94; transaction rolls back; **no accepted challenge** |
| Thread contention | 1 reservation from 16 attempts for one effect |
| Process contention | 1 reservation from 8 attempts for one effect |
| 6 cross-process challenge-vs-reservation races | Where both events committed, reservation precedes the challenge |
| Native Lycheetah Framework import | NOT EXECUTED — `No module named 'lycheetah'` |

**Counterexamples that remain:** false trusted evidence authorizes a bad effect; direct provider bypass creates an effect without an outbox reservation; a challenge committed to a second registry does not reach the dispatch database; post-reservation revocation cannot cancel a sent request; key compromise and privileged ledger+hash rewriting are outside the current controls.

## Provenance and references

- Based on `earned_trust_cycle_007/dispatch_fence.py`, SHA-256 `07481070fb7f03defc0fa8643608a2183b0551a5f7e0fb2b727079952612392d`.
- C007 was researched against `Lycheetah/Lycheetah-Framework` master commit `d4a65ff64efa0a512c5c07ca64f6ec76242dd775`. This Cycle does **not** import or execute that package.
- SQLite WAL/`synchronous=FULL`: <https://www.sqlite.org/pragma.html> and <https://www.sqlite.org/wal.html>.
- Transactional outbox: <https://microservices.io/patterns/data/transactional-outbox.html>.
- Idempotent consumer: <https://microservices.io/patterns/communication-style/idempotent-consumer.html>.
- Provider idempotency example: <https://docs.stripe.com/api/idempotent_requests>.

See `RESEARCH_REPORT.md` for exact limitations, `INTEGRATION_HANDOFF.md` for honest next steps, and `CLAIMS.json` for falsifiers. No novelty or advantage over equally equipped conventional transaction systems has been established.
