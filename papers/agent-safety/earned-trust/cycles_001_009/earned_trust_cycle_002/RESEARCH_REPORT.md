# LYCHEETAH — EARNED TRUST / RESEARCH CYCLE 002

**Date:** 18 October 2026 (NZ)  
**Research title:** The Execution Boundary — What evidence can a decision actually bind?  
**Status:** `SYNTHETIC_SQLITE_ENGINEERING_TESTED`; real Framework suite `UNEXECUTED`; `NOT_DEPLOYED`.

## Executive finding

A SQLite transaction that checks current authority and evidence before inserting a consequential effect can reject stale permissions, policy limits and mismatched intents at the same *local database* commit point. In 32 concurrent submissions of the **same exact effect ID and approval**, the local fixture committed one effect and served 31 idempotent replays. A response deliberately lost after commit was recovered by an authoritative read without another write.

However, this works because the simulation deliberately places **approval, evidence, policy and effect records under one trusted database transaction**. Real APIs often cannot atomically inspect all those facts. An effect remained possible when the trusted evidence said PASS but a separate ground-truth oracle said the customer was ineligible. No agent-safety, production, deployment, payments or novelty claim follows.

## What was inspected in the real repository

All read-only from GitHub `Lycheetah/Lycheetah-Framework` (default branch `master`), 18 October 2026:

- [`lycheetah/assurance/finality.py`](https://github.com/Lycheetah/Lycheetah-Framework/blob/master/lycheetah/assurance/finality.py): `FinalityGate.admit/finalize`, evidence subject/status versus exact revision, policy digest, receipt verification, and explicit non-atomicity limit.
- [`lycheetah/assurance/action_guard.py`](https://github.com/Lycheetah/Lycheetah-Framework/blob/master/lycheetah/assurance/action_guard.py): `issue_approval`, `prepare_effect`, `claim_dispatch`, `revoke_all`, `record_result`, `reconcile_effect`; persistent local guard and hash-chain verification. `PREPARED -> DISPATCHING` is a **local** linearization point.
- [`lycheetah/assurance/models.py`](https://github.com/Lycheetah/Lycheetah-Framework/blob/master/lycheetah/assurance/models.py): typed `AssuranceEvent` and `Disposition`.
- [`lycheetah/assurance/policy.py`](https://github.com/Lycheetah/Lycheetah-Framework/blob/master/lycheetah/assurance/policy.py): policy identity/version and side-effect restrictions.
- [`lycheetah/assurance/runtime.py`](https://github.com/Lycheetah/Lycheetah-Framework/blob/master/lycheetah/assurance/runtime.py): tools are checked against declared allow/deny/review patterns; a declaration of human approval is input from a trusted host, not authenticated by the model's words.
- [`papers/agent-safety/ADVERSARIAL_REVIEW.md`](https://github.com/Lycheetah/Lycheetah-Framework/blob/master/papers/agent-safety/ADVERSARIAL_REVIEW.md): existing demonstrated admission-only freshness counterexample and matched conventional control without an advantage.

**Important:** the import-based Framework tests in this deliverable have **NOT** run. They are a runnable handoff for a real checkout, not evidence that the Framework currently passes them. No repository file was modified.

## Threat model

Invented refund amounts in cents; an agent proposes an exact payload. A trusted reviewer issues a scoped approval expiring at a known time. Evidence and policy may change after a preliminary check. Concurrent workers may submit the same effect. A provider may commit a transaction but lose its response. An adversarial or buggy caller may substitute subject, amount, scope or an idempotency key. Separately, a potentially false authoritative record may disagree with independently modeled actual eligibility.

Not in threat model: hostile code compromising SQLite/the machine, forged human authentication, malicious kernel, remote API behavior, cryptographic attestation, distributed database consensus, unbounded network partitions, payment processor operations, arbitrary agent text truthfulness, or physical-world safety.

## Experiment / local contract

1. `preview()` is a read-only snapshot: it does not authorize a later write.
2. `commit()` opens `BEGIN IMMEDIATE`, looks up any existing effect id, checks exact grant payload, actor epoch, approval time/scope, subject evidence status, optional subject revision, and policy amount; then **inserts the effect inside the same transaction**.
3. If a committed effect ID reappears with the *same approval and payload*, the provider reports an idempotent replay without writing. If a different action reuses the id, it reports conflict.
4. `reconcile()` reads the provider's authoritative effect ledger after an intentionally lost response.
5. `binding_contract.py` requires the same exact, minimal, canonical payload at the AI tool event, local guard and proposed provider action boundaries. It does not authenticate sources or grant permission.
6. `recorded_truth` is a **separate experiment oracle** intentionally not visible to `commit()`. This catches false-authority cases that perfect transaction handling cannot catch.

### Reproduced local results

`python3 -m unittest -v test_transactional_provider test_binding_contract`: **29 / 29 passed**. These are developer-authored tests, not independent stress testing.

`python3 run_probe.py`: seven named representative cases plus 32 parallel thread submissions of one effect. Fixed scenario outcomes:

| Scenario | SQLite commit result | Effect rows |
|---|---|---:|
| Stable eligibility and approval | `COMMITTED` | 1 |
| Approval revoked after preview | `REVOKED` | 0 |
| Eligibility revoked after preview | `EVIDENCE_NOT_PASS` | 0 |
| Policy maximum reduced after preview | `POLICY_LIMIT` | 0 |
| Evidence status changed to FAIL | `EVIDENCE_NOT_PASS` | 0 |
| Authoritative status PASS but independent truth false | `COMMITTED` (**negative safety control**) | 1 |
| Commit succeeds but reply lost | `RESPONSE_LOST_AFTER_COMMIT`; reconcile reads `RECONCILED_COMMITTED` | 1 |

Concurrency fixture: 32 submissions, 16 worker threads, **one** `COMMITTED`, **31** `IDEMPOTENT_REPLAY`, **one** effect row. This is concurrency over SQLite's single database and writer-lock, **not multi-host distributed exactly-once**. It does not prove all possible thread interleavings or platform behaviors.

**Additional executed probe:** `python3 process_probe.py` ran four independent database rounds, each with eight Python processes and one shared SQLite file. Each round observed **one** `COMMITTED`, **seven** `IDEMPOTENT_REPLAY`, and **one** effect row (four committed effects across four different round-specific databases). This is not a distributed or networked system.

### New interface issue to investigate

The Framework's `FinalityGate` hashes the entire `AssuranceEvent` (including metadata), whereas `PersistentActionGuard` hashes its caller-provided action dictionary. A provider may use a third payload representation. Unless the caller establishes that all three refer to the same intent, individually correct checks may describe *different* actions.

`binding_contract.py` provides a minimal schema and exact-equality check for action payloads (`actor`, `subject`, `amount_cents`, `scope`). It rejects action substitution, extra or omitted fields, and boolean currency amounts. This is a **candidate caller-side guard**, not currently woven into the Framework.

**Do not silently equate different hashes.** The proposed real-repository suite includes a targeted parity test for canonical action payload hashing, but no real Framework import was possible in this environment. The entire set of receipts, authorization subjects and effect identities should eventually be carried in one authenticated execution envelope, with versioned schema and a trusted issuer. This is not yet implemented.

## Prepared real-Framework contract probes

`run_framework_contract.py` contains **18 tests**, designed against the public source of the *actual* `AssuranceRuntime`, `FinalityGate`, `PersistentActionGuard`:

- original evidence admitted then finalized;
- changed or wrong-subject evidence pauses at finality;
- `SUBJECT_STATUS` allows benign revisions but `EXACT` does not;
- altered event or changed policy refuses readiness;
- approval issued and single-use claim dispatched; revoked, altered or replayed claims refused;
- local dispatch requires an audit anchor;
- `UNKNOWN` effects are reconciled through explicit evidence;
- local ledger survives reopening;
- caller composes finality and local dispatch without asserting provider atomicity;
- missing shared revocation across a separately seeded provider is a **negative control**: remote effect proceeds; propagated revocation stops it.

**Execution status: not run**, because local GitHub DNS access is unavailable and the real package is not mounted. `real_contract_not_run.txt` records the failing import. The test suite is written to exit without running rather than quietly substitute Framework stubs. Execute in a real checkout and record any failures honestly.

## Interpretation and existing prior art

SQLite transactions and HTTP conditional requests/`If-Match` already support transactional and conditional update semantics. Idempotency keys and authoritative reconciliation are conventional payment/workflow engineering. The value of this work, if any, must be measured at the **integration and evidence discipline level**, not called invention of concurrency control. See:

- [SQLite transaction semantics](https://www.sqlite.org/lang_transaction.html)
- [MDN `If-Match` conditional requests](https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Headers/If-Match)
- [Stripe idempotent requests](https://docs.stripe.com/api/idempotent_requests)
- Framework [agent safety study](https://github.com/Lycheetah/Lycheetah-Framework/tree/master/papers/agent-safety)

The strongest current falsifier is the false-evidence negative control: an apparently compliant and transactionally well-controlled action can still be genuinely harmful. Source authentication, independent correctness tests, and consequence evaluation require distinct sensors and safeguards.

## Next cycle (003): actual integration or clear failed contract

1. Run the **18 unexecuted** tests inside a pinned Framework checkout; save exact commit SHA, dependencies, pass/fail transcript; correct the harness without concealing negative results.
2. Build one versioned *action/evidence/permission* envelope with a single canonical action schema, authenticated issuer, policy digest, admission and finality references, effect id, time bounds, evidence dependency identifiers and external outcome state. Ensure sensitive data does not land in public receipts.
3. Introduce a provider-capability declaration: `CONDITIONAL_COMMIT_SUPPORTED`, `IDEMPOTENCY_ONLY`, `READ_ONLY`, or `UNSUPPORTED`. For effects needing atomic preconditions, if unsupported, **pause** instead of pretending that a local finality check is enough.
4. Compare against a conventional ACL/OPA + equivalent idempotent provider using identical test data, authority access and operator burden. Preserve parity, even if it shows no unique Framework advantage.
5. Add adversarial source forgery, delayed revocation, multiple processes, crash/restart and independent reviewer cases. Test against realistic service semantics only after a safe mock/dry-run phase.

## Claim boundaries

- **MEASURED_LOCALLY:** 29 self-authored tests pass; the SQLite fixture handles these programmed cases, 32 thread-concurrent duplicate submissions, and four separate eight-process races on one SQLite file per round.
- **NEGATIVE_CONTROL:** false trusted evidence can still cause an unsafe modeled effect; unlinked authority revocation remains a possible integration fault (real Framework test pending).
- **SOURCE_REVIEWED_ONLY:** public Framework methods and documented limits, not their behavior in the new suite.
- **UNEXECUTED:** 18 real-Framework contract tests.
- **UNVERIFIED:** actual network and provider effects, multi-host semantics, novel contribution, real business safety, independent validation.

> The right claim is not “the AI is trustworthy.” It is “these explicitly defined consequences were refused, for these checkable reasons, in this limited test environment.”
