# Lycheetah EARNED TRUST — Master Handoff, Cycles 001–007

**Date:** 18 October 2026 (Pacific/Auckland)  
**Status:** `SYNTHETIC_LOCAL_ENGINEERING_TESTED / NOT DEPLOYED / REAL-FRAMEWORK_INTEGRATION_NOT_EXECUTED`  
**Canonical GitHub reference inspected:** `Lycheetah/Lycheetah-Framework` `d4a65ff64efa0a512c5c07ca64f6ec76242dd775`.

## Lineage and results

| Cycle | Mechanism | Primary boundary learned |
|---|---|---|
| 001 | Admission/finality versus artificial atomic provider | Admission is not external effect atomicity |
| 002 | Local single-use SQLite effect accounting | Local SQL isolation cannot prove a remote transaction |
| 003 | HMAC approvals, execution receipts and ledger | Authenticated records can still be false |
| 004 | Two independently keyed outcome observers | Separate signatures can represent one information source |
| 005 | Witness ancestry and controlling-source graph | Declared independent paths can share one root |
| 006 | Signed challenges and governed provenance registry | Cached confirmation can outlive a challenge; registry is not dispatch authority |
| **007** | **Transactionally ordered local challenge/authority/evidence/dispatch fence** | **A separate Cycle 006 registry and Cycle 007 ledger can be internally correct yet jointly unsafe when the relay is missed** |

Earlier Cycles 001–006 are included verbatim from the previous complete archive. Their test totals and original documentation are historical records; they were not all reverified in this handoff. **Cycle 007 is newly executed: 47/47 local tests passing, 20 authored scenarios (8 local dispatch claims and 12 pauses), including one false-evidence negative control.** Separate real Framework import is still unavailable: `run_actual_framework_contract.py` exits 4 (`No module named 'lycheetah'`), and zero native integration tests executed.

## Current technical finding

The local `Fence` correctly serializes challenges and dispatch claims within **one shared SQLite write domain** (`BEGIN IMMEDIATE`). Its proof obligation is deliberately narrow: an unresolved, matching challenge committed *before* a local claim is visible at that claim, provided the declared source graph is right and clients cannot bypass the broker. Once a claim is committed (`DISPATCHING`), a later challenge does not undo it. All results are synthetic.

**A concrete failure has been reproduced:** a C006 signed challenge was accepted in the in-memory registry but not relayed to the C007 dispatch database. The C007 fence then permitted dispatch because its own records were unchanged. Mirroring first rejects the stale witness. **The relay itself is still unprotected; no distributed transaction or end-to-end safety guarantee is established.**

## Source files

- `earned_trust_cycle_007/dispatch_fence.py`: new synthetic shared-domain permission/dispatch controller (not part of Lycheetah production code)
- `earned_trust_cycle_007/test_dispatch_fence.py`: 42 deterministic/concurrency tests
- `earned_trust_cycle_007/test_governance_mirror.py`: 4 tests, including intentional split-store counterexample
- `earned_trust_cycle_007/test_process_challenge_race.py`: 1 test with 8 cross-process races
- `earned_trust_cycle_007/run_scenarios.py` + `scenario_results.json`: 20 fixed case outcomes
- `earned_trust_cycle_007/upstream_cycle_006/`: byte-identical local upstream C006 source needed for the split-store experiment
- `earned_trust_cycle_007/run_actual_framework_contract.py`: four unexecuted sequential tests importing real `lycheetah` classes, with explicit import failure when unavailable
- `earned_trust_cycle_007/CLAIMS.json`: narrow evidence statuses and falsifiers
- `earned_trust_cycle_007/RESEARCH_REPORT.md` and `INTEGRATION_HANDOFF.md`: evidence, limits, next experimental steps

## Reproduce C007 in a standalone extract

```bash
cd earned_trust_cycle_007
python3 -m unittest -v test_dispatch_fence test_governance_mirror test_process_challenge_race
python3 run_scenarios.py
sha256sum -c SHA256SUMS.txt
```

All C007 local experiments use only standard-library Python and synthetic inputs. No GitHub commit, live customer effect, live payment, external API write, publication or deployment was authorized or performed.

## Next research objective (C008)

1. Obtain the actual pinned Framework checkout and execute the four real-class sequential tests, retaining failures.
2. Choose one durable governance/approval/evidence/dispatch authority, or define an external provider conditional commit. Show that a challenge *cannot disappear in an unmirrored gap* even across crash/restart.
3. Exercise crash injection between event acceptance, local dispatch claim, provider submission and provider acknowledgement. Maintain `UNKNOWN` and reconcile before reissue.
4. Introduce a trusted third-party review of source genealogy, independently labelled ground-truth cases, throughput/false-review measurements, and a matched conventional SQL/idempotency baseline. Do not claim product safety or novelty without these.
5. Keep live side effects disabled, approvals human-controlled, keys isolated, and no private data in public repositories.

**Veritas before victory.**
