# EARNED TRUST — Cycle 007: The Last Responsible Moment

**Date:** 18 October 2026, Pacific/Auckland  
**Status:** `LOCAL_SYNTHETIC_ENGINEERING_TESTED / NO LIVE EFFECTS / REAL_FRAMEWORK_INTEGRATION_NOT_EXECUTED`  
**Working name:** Last Responsible Moment Dispatch Fence (LRM-DF)

## Run this research without any external services

Python 3.10+, standard library only. The upstream Cycle 006 source snapshots required by the mirror experiment are included byte-for-byte in `upstream_cycle_006/`.

```bash
cd earned_trust_cycle_007
python3 -m unittest -v test_dispatch_fence test_governance_mirror test_process_challenge_race
python3 run_scenarios.py
sha256sum -c SHA256SUMS.txt
```

The native Lycheetah bridge is **separate** and requires a genuine framework checkout:

```bash
# Run only in a pinned Lycheetah-Framework checkout with its dependencies installed:
PYTHONPATH=. python3 /path/to/earned_trust_cycle_007/run_actual_framework_contract.py
```

In the authoring container this exits code **4**, with `No module named 'lycheetah'`. **Zero real Framework tests executed.** The four cases in the file are candidates, not passing observations.

## Lab mechanism

- A *single* SQLite file stores approvals, authority epochs, evidence revisions, challenges, prepared effects and dispatch claims.
- Mutations and dispatch claims obtain `BEGIN IMMEDIATE` write transactions. A challenge committed before a claim is necessarily visible to that claim among cooperating clients of this DB.
- A bound witness snapshot signs the exact action hash, governance head/revision, actor authority epoch and required evidence records. Changed values cause refusal; a new snapshot cannot bypass a still-open challenge.
- Trusted source ancestry is immutable, checked for cycles, and expanded transitively when preparing an effect. The source-graph fingerprint is fixed at database initialization.
- An operator-signed approval is bound to the exact action; an auditor-signed challenge opens a dispute; two distinct reviewer organizations are required for resolution. **Lab fixture keys are kept in this same process; no real identity or organizational independence is established.**
- A successful dispatch claim means only `DISPATCHING`—it is *not* a provider success. Timeout/ambiguous results transition to `UNKNOWN` and the local dispatch claim cannot be replayed.
- A SHA-256 local event chain can detect some corruption, but has **no independent anchor or immunity to attacker-controlled rehashing**.

### Most important result: the unavoidable split-store gap

`test_governance_mirror.py` imports the actual **Cycle 006** experimental `GovernedRegistry` (copied without changing its bytes). It first applies a signed `CHALLENGE` there, *but does not relay it* to the separate dispatch database. A still-valid C007 witness can then claim dispatch. If relayed before claim, it pauses as intended. Both components can be internally consistent while their **joint interpretation is unsafe**.

Therefore copying Cycle 006 events into C007 is **not** an atomic integration. It needs one durable authority for the condition, or an authenticated provider-side conditional commit that fences stale intent.

## Research results

| Verification | Observation |
|---|---|
| Cycle 007 tests | **47/47 passing** on local fixtures |
| Cross-process contest | Eight processes contend for a single effect, exactly one local claim succeeds |
| Two-process challenge vs dispatch | Eight races; if a claim was accepted, its audit position preceded the challenge |
| Two-thread challenge vs dispatch | Twenty races; same observed audit ordering |
| Fixed case matrix | 20 cases: 8 local dispatch claims, 12 pauses |
| Negative control | 1/20 claimed dispatch with deliberately false trusted evidence |
| Cycle 006 → Cycle 007 mirror | Missing relay permits claim despite accepted Cycle 006 challenge |
| Real native Framework | **NOT EXECUTED**, missing local Python package |
| Novelty vs identical conventional controls | **NOT ESTABLISHED**; SQLite and idempotency are established primitives |

These counts are conditional outcomes of scripted toy scenarios, not rates of safety, effectiveness, or generalization.

## Scope and caveats

1. This is a **single SQLite writer domain**. It does not commit a remote refund transaction atomically and does not control noncooperating workers or external provider state.
2. The source dependency graph, reviewers, auditor and `PASS` evidence are trusted inputs. False evidence can authorize an incorrect action; a source omitted from the trusted graph is not automatically discoverable.
3. The model does not itself verify ground truth, distinguish genuinely independent organizations, perform durable external registry-key management, prove crash-safe Cycle 006 event relay, or authenticate real humans.
4. Hostile clients with arbitrary database writes, key access or direct provider API access bypass the boundary. Do not connect the lab to customer-facing actions.
5. A challenge after the dispatch claim cannot retroactively cancel a remote request, regardless of whether a local provider response has arrived.
6. Native Lycheetah integration is not demonstrated; the new class tests are plainly import-gated.

See `RESEARCH_REPORT.md`, `INTEGRATION_HANDOFF.md` and `CLAIMS.json` for evidence, proposed next steps and exact falsifiers. No push, publication, live refund, external API write or production action occurred.
