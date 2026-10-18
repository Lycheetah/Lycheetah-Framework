# EARNED TRUST C007 — The Last Responsible Moment

**Research question:** Under what boundary does a later governance challenge, authority revocation or evidence mutation reliably invalidate a previously accepted action *before local dispatch*?

**Research source:** Lycheetah-Framework public `master` commit `d4a65ff64efa0a512c5c07ca64f6ec76242dd775` as inspected during Cycles 001–006. The Cycle 006 handoff contains the file IDs and original integration call sequence. The C007 source code is new synthetic reference implementation, **not** code installed from the public framework.

## Executive finding

A one-database transaction can impose an unambiguous local order between a signed challenge and a dispatch claim. If a challenge commits before the dispatch claim and is directed at the action's declared source dependency graph, the claim cannot succeed under the implemented rules. If dispatch claims first, no amount of subsequent local checking cancels an unknown or already executed provider effect.

This is conditional local concurrency control, not a proof of real-world safety, and not a novel alternative to conventional database isolation.

**The most important negative finding is the two-store mirror gap:** A signed challenge can be properly accepted in Cycle 006's GovernedRegistry, then fail to reach Cycle 007's separate SQLite authority. In that interval the dispatch fence can accept a claim. There is no crash-safe shared transaction across the two systems. Making a stronger external safety claim would be incorrect.

## Engineering additions over C006

1. `dispatch_fence.py`: local policy and state registry in one SQLite file, single-use effect claims, authority epochs, exact action digests, subject-specific evidence, local audit chain, signed snapshots, ancestry expansion, challenge and resolution signatures.
2. `test_dispatch_fence.py`: deterministic negative and happy-path tests; 20 thread races; eight-process single-effect contenders.
3. `test_governance_mirror.py`: 4 boundary tests using the unchanged C006 implementation. One deliberately demonstrates a *failure* of the combined two-store composition despite both individual integrity checks passing.
4. `test_process_challenge_race.py`: eight fresh two-process challenge-versus-claim races with committed audit ordering assertions.
5. `run_scenarios.py`: explicit 20-case fixed scenario matrix, including false authoritative evidence.
6. `run_actual_framework_contract.py`: four real-class sequential contract candidates; import fails in this environment, so no native test ran. Does not pretend a native joint atomic transaction exists.

## Core ordering invariant

Let `C(source)` be a committed, unresolved challenge, `D(effect)` the local dispatch claim, `Anc(witness)` its registered ancestry, and `s(X)` the monotonically increasing audit sequence in the **same SQLite database**.

Under the assumptions that (a) every governance mutation and dispatch claim uses that one database; (b) the configured graph correctly names all relevant ancestors; (c) the signed authorities are trusted; (d) the database engine correctly serializes writers; and (e) the broker's predicate implementation matches its tests:

**If** `s(C) < s(D)` and the challenged source lies on the effect's declared dependency closure, an accepted `D` must not occur while that challenge remains unresolved.

The claim holds only for the local reference system. A maliciously direct provider write is outside it. A challenge with `s(D) < s(C)` is **not** grounds to claim retroactive prevention of D. An admission-time snapshot is not a grant to act later without rechecking.

## Reproduction evidence

Commands run in this conversation's local environment:

```bash
python3 -W error::ResourceWarning -m unittest -q test_dispatch_fence test_governance_mirror
# Ran 46 tests: OK
python3 -m unittest -q test_dispatch_fence test_governance_mirror test_process_challenge_race
# Ran 47 tests: OK
python3 run_scenarios.py
# 20 fixed cases: 8 allowed, 12 paused; 1 false-truth allow negative control
python3 run_actual_framework_contract.py
# exit code 4, NOT EXECUTED: No module named 'lycheetah'
```

The 8-process single-effect test produced one claim with state `DISPATCHING` and nonwinning clients were refused. The eight two-process challenge-versus-dispatch races all satisfied the recorded causal order; this is not a comprehensive concurrency proof or a distributed consensus result.

### Fixed scenario matrix

| Scenario family | Observed effect |
|---|---|
| Fresh, exact approval/evidence | Local dispatch claim admitted |
| Source challenged before claim | Cached witness stale; fresh witness denied |
| Unrelated source challenge | Conservative stale witness refusal; newly bound witness admitted |
| Actor revoked | Denied, including with refreshed witness |
| Evidence status/revision changed | Denied |
| Action/witness substitution | Denied |
| Expired approval | Denied |
| Unsigned or malformed challenge | Ignored/refused; does not freeze valid work |
| Proper resolution after challenge | Newly bound witness admitted |
| Challenge after claim | Claim remains `DISPATCHING`; later challenge does not rewind it |
| False `PASS` from trusted producer | Claim still admitted: truth remains unverified |
| Duplicate dispatch | Second claim denied |

The 20-case JSON artifact records the exact per-case decisions, not only the aggregates. A cached-admission-only controller is a **deliberately weaker** comparator that can miss changes after admission; it is not a fair benchmark of mature authorization systems. An equally configured conventional SQL control is expected to have the same security properties. We make **no Lycheetah-specific superiority claim**.

## Challenge relay counterexample

The mirroring tests run against a byte-identical snapshot of the C006 `GovernedRegistry`, which in turn verifies the signed challenge and its local history. The test then intentionally omits the relay into C007. Result: C007 admits the still-locally-valid dispatch claim. There is no contradiction: the dispatch authority simply has no knowledge of the external event.

When mirroring succeeds first, the dispatch claim sees the new governance head and refuses the stale witness. A refreshed witness also sees the open challenge and refuses. This *repair for an ordinary race* is insufficient to solve a relay failure, shared storage crash, compromised relay, or remote provider race.

## Security and assurance limits

- The code uses HMAC keys co-located with the fixture. No key isolation, rotation, actual operator identification, independent organizational proof, or certificate authority.
- The source graph is trusted at configuration; although acyclicity and transitive closure are checked, real provenance may be omitted, false or disputed. Graph changes cannot be applied safely through the current running protocol; they require a designed and transactional policy upgrade path.
- Audit hashes provide internal integrity checks but no immutable external anchor, issuer authentication or protection from privileged DB tampering.
- An evidence producer may sign false data. Source correctness is not established by signatures, quorum, or recency labels.
- `DISPATCHING` marks a *local permission claim*. No provider transaction is executed here. Two independent datastores cannot be made atomic by a last-second local recheck alone.
- After a timeout we preserve `UNKNOWN`; the local effect ID is not retried. The provider's final status must be queried through an authoritative provider API before a new decision.
- Test scenarios and assertions were authored by the same AI seat, not third parties. All evidence is synthetic; no model benchmark, customer deployment, security audit or verified safety rate.
- A shared-DB convention is only as strong as full mediation. A direct bypass of the broker invalidates the guarantee.

## Conventional comparison and prior art

This design relies on standard technology. SQLite's `BEGIN IMMEDIATE` and single-writer serialization are documented at https://www.sqlite.org/isolation.html. More general Serializable transaction concepts and conditions are described at https://www.postgresql.org/docs/current/transaction-iso.html. Remote requests need recipient-supported idempotency and/or conditional writes; Stripe's idempotency model is one illustrative existing pattern (https://docs.stripe.com/api/idempotent_requests). **These are prior art, not Lycheetah inventions.**

## Findings to carry into C008

**Highest priority:** deploy neither code nor assertions, but design the storage boundary first. Either (1) move governance, evidence, approval, dispatch and authority epochs under one durable owner; (2) have the provider enforce an atomic conditional command using a signed, short-lived, action-bound authorization; or (3) use a durable outbox with reconciliation and explicitly limited cancellation semantics. Test crashes *between* ledger updates and any provider acknowledgement.

An authentic next experiment should use **the real Framework classes** from a pinned installed GitHub checkout and compare against a modern conventional policy/transaction implementation with exactly matched controls and threat models. Until then this lab is a reproducible engineering probe, not an integrated product.

**Research posture:** Veritas before victory. No real-world effects.
