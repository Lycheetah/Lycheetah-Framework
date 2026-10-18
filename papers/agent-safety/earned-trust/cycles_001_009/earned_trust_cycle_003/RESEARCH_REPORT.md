# Earned Trust — Cycle 003: The Receipt Is Not the Reality

**Date:** 18 October 2026 (NZ)  
**Investigators:** Lycheetah collaboration, locally implemented by an AI research assistant  
**Evidence level:** `SYNTHETIC_SQLITE_ENGINEERING_TESTED` / `NOT_DEPLOYED` / `NOT_INDEPENDENTLY_REPLICATED`  
**Framework base inspected:** `Lycheetah/Lycheetah-Framework`, master SHA `d4a65ff64efa0a512c5c07ca64f6ec76242dd775`. That SHA was read from the linked GitHub repository; no working checkout was acquired inside the local container.

## 1. Motivation and research question

Cycle 001 used a single-threaded model to compare check timing. Cycle 002 used a real local SQLite transaction to examine conditional writes, idempotency, and cross-boundary action identity. The Framework's `FinalityGate` re-evaluates evidence and policy, while `PersistentActionGuard` binds approval to a stored action and atomically claims local dispatch. Neither makes a remote effect atomic.

**Cycle 003 question:** Can a local experimental provider create a cryptographically authenticated record that ties a verified authorization token to the exact proposed action and a specific local commit, and what safety claims would still be false?

**Null expectation:** Where a conventional system already has current-state checks, local transactions, idempotency and authenticators, importing Framework terminology should not improve outcomes by itself. This experiment does not compare genuine models or independent conventional baselines and cannot establish superiority.

## 2. Design, prior art, and deliberately narrow scope

- **Token**: strict canonical action `actor/subject/amount_cents/scope`. An issuer HMAC-SHA256 token binds action digest, effect/approval IDs, actor, scope, subject evidence version, policy version, expiry and nonce.
- **Distinct authenticator**: a provider HMAC-SHA256 MAC signs the local commit record (not an external provider outcome). Domain strings prevent using one class of artifact as another; issuer and provider secrets differ. A recipient must already trust the relevant shared key; unlike a public-key digital signature, HMAC is not independently/publicly verifiable.
- **Decision boundary**: SQLite `BEGIN IMMEDIATE` before checking current grant, epoch, evidence, policy, replay and uniqueness. A single local DB serializes its writers. The effect row, hash-chained audit row and authenticated receipt are inserted/updated within one transaction.
- **Recovery**: same token/effect produces an idempotent *read*, not a second write. A deliberately lost response can be reconciled from stored provider proof.
- **Integrity**: signed receipt and linked local hash chain are checked. Before each new effect, all existing ledger records and signed effect receipts undergo linear-scan checks; observed corruption routes to `LEDGER_INTEGRITY_FAILED`. The unkeyed chain cannot detect total rewrite/truncation without an independently protected prior anchor.
- **Fidelity test**: source `status=PASS, eligible=true` can remain false according to a separate experimental truth flag. The commit checks trusted records, **not reality**.

The construction uses established cryptographic MAC and database concepts. SQLite documents serializable isolation via serialized writers and its immediate transaction mode. RFC 2104 describes HMAC using a shared secret. See the official references below; the project is not claiming novelty for these primitives.

## 3. Actually executed tests

| Work | Observed result | Meaning / limit |
|---|---|---|
| `python -W error::ResourceWarning -m unittest -v test_authenticated_provider` | **50 / 50 passed**, Python 3.13.5 | Developer-authored unit contracts; not formal proof or independent review |
| 32-thread racing submissions | **1 COMMITTED; 31 IDEMPOTENT_REPLAY** | One approval and effect on one SQLite file; lock-mediated local behavior |
| 4 × 8-process rounds on fresh SQLite files | Every round **1 COMMITTED; 7 IDEMPOTENT_REPLAY** | Multiple processes, same local file per round; not distributed across machines |
| 8 named scenarios | 3 effect-containing scenarios, 5 refused/paused, with expected reason codes | Named scenarios are selected and authored, not representative outcome statistics |
| Local audit tampering & externally retained old prefix anchor | Mutation/truncation detected in constructed cases | No external anchor service and no host-compromise resistance |
| Local record corruption at new dispatch | `LEDGER_INTEGRITY_FAILED`; no additional effect | In-process trusted enforcement only |
| False-source negative control | **COMMITTED, signed proof verifies, experiment truth=false** | Permission + authentication + transaction ≠ truthful evidence or harmlessness |
| Real Framework contract suite (`../earned_trust_cycle_002/run_framework_contract.py`) | **NOT EXECUTED** (`No module named 'lycheetah'`) | Import verification needs an actual repo checkout; not a pass/skip |

### Exact named scenarios

| Scenario | Outcome | Effect count |
|---|---|---:|
| Stable exact token, evidence and policy | `COMMITTED` | 1 |
| Changed action amount | `ACTION_BINDING_MISMATCH` | 0 |
| Tampered token expiry, MAC not updated | `INVALID_TOKEN_AUTH` | 0 |
| Revoked actor before dispatch | `REVOKED` | 0 |
| Changed evidence status to FAIL | `EVIDENCE_UNSATISFIED` | 0 |
| Changed policy revision | `POLICY_REVISION_CHANGED` | 0 |
| Trusted status says PASS, external test truth=false | `COMMITTED` | 1 |
| Local commit succeeds, response lost | `RESPONSE_LOST_AFTER_COMMIT`; proof read back and verified | 1 |

Full machine-readable observations: `attack_results.json`, `process_results.json`. Exact test log: `test_output.txt`.

## 4. New findings and non-findings

**Finding A — action identity can be bound end-to-end within one trusted lab.** The experimental issuer, provider and verifier agree on one canonical four-field action and two separate HMAC trust domains. Substituted amount, subject, scope, unsigned token or unauthorized issuer fail. This does *not* show the user's actual consent, that the model understood the action, or that a real provider received it.

**Finding B — signed local receipts can aid readback after uncertain responses.** A synthetic lost response leaves exactly one committed local row; the caller can fetch and verify a receipt. In a live external API, that conclusion requires provider-specific idempotency and authoritative status reads — it cannot be deduced from our local receipt.

**Finding C — audit verification requires a separately trusted anchor.** A bare SHA-256 chain detects accidental/simple mutation but a database writer can recalculate the entire chain. When an independently retained prefix hash is supplied, the altered historical prefix is detected. The separate anchor is provided only by the test; no independent storage service is implemented.

**Finding D — provenance is a different property from truth.** A MAC proves that a secret-key holder authenticated particular bytes. It does not establish those bytes are true. The intentionally false source still passes. Before claiming protection against false evidence, a different source-trust/measurement program is required.

**Finding E — no novel correctness advantage is established.** The same concepts exist in conventional authorization, audit, conditional transaction and idempotency systems. This is a bounded combined lab and integration design, not a security certification or novel primitive.

## 5. Threat model and attack surfaces

**Within the lab:** an untrusted caller can mutate action fields and token messages, replay an authentic token, race threads/processes, send a stale policy/evidence version, and simulate lost responses. The experiment also manually corrupts database rows. Its source-truth oracle is deliberately separate from the provider checks.

**Trusted by assumption, not protected by this implementation:** the local Python host; issuer/provider HMAC secrets; approval/seeding methods; policy database; subject evidence source; SQLite engine and kernel; reviewer identity supplied to the fixture; local clock. An untrusted model that gains a signing key or access to trusted state-changing methods can defeat these assumptions. Provider and issuer share access to symmetric verification keys, so recipients with these keys can forge matching artifacts. There is no public-key issuer separation or HSM/KMS integration.

**Not delivered:** actual human authentication; signed source attestations; customer consent proofs; encrypted secrets; real banking/refund effects; remote atomicity or cancellation; distributed consistency; verified key rotation; multi-tenant identity; independent adversarial evaluation; formal cryptographic security proof; real model traffic; external verification service; full historical rollback resistance; production policy semantics or security certification.

## 6. Relationship to existing Lycheetah components

- `lycheetah/assurance/finality.py`: admission witness and finality-time recheck; the caller still must enforce `REVIEW` before effect dispatch.
- `lycheetah/assurance/action_guard.py`: action-hash approval, epochs, prepared/dispatching ledger, audit anchors; local dispatch is not provider commit.
- `lycheetah/assurance/runtime.py`: active deterministic tool policy versus bounded linguistic heuristics; `human_approved` comes from the trusted host and is not itself proof of identity.
- `papers/agent-safety/`: already records freshness and accounting counterexamples and a matched conventional baseline with no observed advantage. Cycle 003 should not erase or overclaim beyond those results.
- `34_ASSURANCE_RUNTIME/action_guard/versions/v0.8/`: historical research already explores a separate checkpoint authority; Cycle 003 should be compared against it, not presented as the first signing mechanism in the framework.

The proof is an **adjacent local experiment**, not a modified or tested version of these Framework modules. The real Framework's import-based tests still need to run inside its checkout.

## 7. Next strongest experiment (Cycle 004 candidate)

Build a *thin adapter* in the actual Framework repository that enforces exact binding among `AssuranceEvent.tool_arguments`, local guard action, finality witness, and a provider-specific request. Do not create a second guard or replace established mechanisms. Require the adapter to fail closed if any proof has ambiguous identity. Compare against a conventional authorization/transaction/idempotency adapter under identical adversarial scenarios. Add independent fixtures where source truth disagrees with trusted assertions. Only then consider an isolated mock HTTP provider, explicit network failure and remote status reconciliation.

**Falsifier for the integration hypothesis:** under matched external cases, the integrated adapter does no better than a conventional baseline, fails to bind an actual changed request, allows retry duplication, or issues an apparently valid proof for an action it did not record. Any of these must be published as a negative result.

## 8. Source references

1. [Lycheetah-Framework, `master`](https://github.com/Lycheetah/Lycheetah-Framework/tree/master)
2. [Framework Finality Gate](https://github.com/Lycheetah/Lycheetah-Framework/blob/master/lycheetah/assurance/finality.py)
3. [Framework Action Guard](https://github.com/Lycheetah/Lycheetah-Framework/blob/master/lycheetah/assurance/action_guard.py)
4. [Agent Safety adversarial review](https://github.com/Lycheetah/Lycheetah-Framework/blob/master/papers/agent-safety/ADVERSARIAL_REVIEW.md)
5. [SQLite — Isolation](https://www.sqlite.org/isolation.html)
6. [RFC 2104 — HMAC](https://www.rfc-editor.org/rfc/rfc2104.html)

## 9. Publication boundary

No GitHub writes, customer operations, external transactions, or credential disclosures were performed. All executable results in this packet are newly authored local synthetic results. A passing test is a reproducible constraint *within its assumptions*, not a deployment guarantee.
