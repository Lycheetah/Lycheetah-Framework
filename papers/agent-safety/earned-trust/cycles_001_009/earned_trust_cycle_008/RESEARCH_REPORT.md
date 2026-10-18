# EARNED TRUST C008 — No Challenge Left Behind?

**Date:** 2026-10-18 NZST/NZDT (Pacific/Auckland)  
**Status:** Synthetic, author-designed, local tests; neither native Framework integration nor production validation.

## Research question

Can governance challenges, evidence revisions and dispatch reservations be ordered durably in one authority, while treating uncertain provider outcomes honestly after the controlling process crashes?

### Hypothesis H1: local commit order

If `CHALLENGE(C)` commits *before* `SEND_RESERVED(E)` under the same SQLite serialized writer domain, and `C` belongs to `Anc(E)` while unresolved, `E` must not reserve a send. The rule requires: declared source ancestry is complete, all writers use the one authority DB, keys and ledger are trusted, and clients cannot bypass the provider through another channel.

**Evidence:** Cycle 008 repeats C007 challenge fencing while atomically recording the outbox send reservation. The 6 process races and case matrix meet the condition. This is a bounded SQLite property, not distributed consensus.

### Hypothesis H2: ambiguous remote outcomes remain unknown

When the process dies after reserving a send, it might have sent nothing. When it dies after the remote provider committed but before local acknowledgment, it might already have caused an irreversible effect. These histories are observationally indistinguishable from the local ledger alone. A conservative restart moves both histories from `SENDING` to `UNKNOWN` and does not automatically submit another request.

**Evidence:** `crash_worker.py` exits with codes 90 (reservation committed, no provider effect) and 91 (provider committed, no local ack). `test_crashsafe_authority.py` reopens separate databases and reconciles only when a signed simulated provider record is present. This prioritizes avoiding duplicates over automatic liveness. `UNKNOWN` is not a guarantee that the provider did or did not act.

### Hypothesis H3: provenance, identity and outcome authentication are separable

The outbox binds effect ID, exact action hash, subject, evidence revision and governance head. The signed provider receipt binds effect ID, action hash and claimed outcome. Deliberately changing the receipt outcome, signing key or action hash results in rejected acknowledgment. A matching signature still does not prove that the upstream evidence or provider's report is correct.

**Evidence:** 46 unit tests; four targeted receipt-authentication tests; one false-evidence negative control. The toy keys are all visible to the test process and are not genuine independent trust anchors.

## Experimental results

```text
46 / 46 Cycle 008 unittest methods passed (Python 3.13, stdlib, locally)
22 / 22 fixed scenario outcomes matched (22 hand-authored cases)
16 concurrent thread reservation attempts -> 1 accepted
8 concurrent process reservation attempts -> 1 accepted
6 two-process challenge vs reservation races -> consistent local order
subprocess exits after reservation, provider write and governance commit -> recovered expected SQLite states
```

The fixed scenario classification (not real-world rates):

| Observed state | Number | Interpretation |
|---|---:|---|
| NORMAL | 2 | Valid local reservation under tests |
| STOP | 13 | Stale, invalid, substituted, revoked, corrupted or duplicated path paused |
| UNKNOWN | 2 | Provider outcome absent; no automatic retry |
| CONFIRMED | 1 | Recovery after signed provider status query |
| NOT_RETROACTIVE | 1 | Late challenge did not undo prior send reservation |
| FALSE_EVIDENCE_PASSED | 1 | Incorrect trusted fact still authorizes action |
| BYPASS | 1 | Direct provider call outside the authority succeeds |
| SPLIT_STORE_GAP | 1 | Challenge accepted by other DB is invisible to this authority |

The `pass` fields in `scenario_results.json` mean *observed==predeclared expected*, including expected counterexamples. They are **not** success/failure labels for system safety.

## Failure found during development and corrected

The first draft of Cycle 008 accepted an arbitrary caller-supplied provider result as proof of success. It was tightened to require HMAC of `{effect_id,outcome,action_hash}` with a separate fixture key, plus an exact action-hash check. A second review found that the audit-chain hash alone did not attest mutable outbox state. The revised implementation checks expected event transitions and reservation audit sequence against materialized effects/outbox tables, detecting tested rewinds. These are internal integrity checks; if an attacker can rewrite the database **and** all hashes, this local log is not trustworthy.

## Historical audit — important test counting clarification

The seven prior archives were rechecked from `earned_trust_cycles_001_007_complete.zip` in this environment. C001:20, C002:29, C003:50, C006:59 and C007:47 pass. For C004 and C005, the full default unittest selection **fails** with 4 errors apiece because the named native bridge tests try to import the absent `lycheetah` package. Running their expressly synthetic test modules only gives C004:38 and C005:42 passing. We preserve both outcomes. Therefore **331 = 285 earlier synthetic tests + 46 C008 tests** under selected synthetic scopes; this is not a claim that all default test suites pass.

Native C007 bridge attempted: exit code 4, `No module named 'lycheetah'`. It is **not executed**. `prior_cycle_recheck.json` reports both the raw default results and the selected synthetic results. No source in prior archives was rewritten to conceal failures.

## External comparison and prior-art boundary

SQLite WAL `FULL` and serialized write transactions, the transactional outbox, and an idempotent receiver are established conventional techniques. See SQLite docs and the microservices.io patterns listed in the README. Cycle 008 did **not** independently implement a modern matched-control conventional comparator: it uses the conventional database protocol directly. No performance, security or uniqueness advantage for the Lycheetah branding has been shown.

## What isn't established

- Not real-world power-loss/hardware durability testing, network partitions, Byzantine actors, or multihost coordination. SQLite WAL requires writers on the same host and dependable filesystem sync semantics.
- Not an atomic transaction that spans our local authority and a remote provider. A provider write can happen after a later challenge if reservation occurred first.
- Not delivery liveness or exactly-once network delivery. We choose local **no automatic retry of UNKNOWN**. A real provider's idempotency window may expire, and a past absent query does not certify the request cannot still arrive.
- Not authenticated humans, genuine separate organizations, independently secured keys, trusted provisioning, an anchored append-only log, or proof that the configured source graph is complete.
- Not protection against direct provider access outside the authority. `direct_provider_bypass` demonstrates failure of full mediation.
- Not truth certification. False signed `PASS` evidence and matched false testimony remain unsolved.
- Not deployment-ready or native Lycheetah integration. C007 source was reused byte-for-byte, not the real `lycheetah.assurance` module.

## Next research action (C009 candidate)

Replace the toy self-declared provider identity with a provider-side authorization contract, enforce restricted credentials and a conditional request referencing the same durable authority revision, and model request-in-flight after revocation. Run actual Framework classes from a pinned checkout before announcing integration. A separately reviewed threat model and a true matched-control baseline must precede claims of superiority.
