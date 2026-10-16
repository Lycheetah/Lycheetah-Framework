# Research note: Lycheetah Action Guard v0.8

**Date:** 16 October 2026  
**Area:** Agent safety, cybernetics, high-impact effects, trusted operational evidence  
**Status:** local code + synthetic verification + separate-process checkpoint-service smoke test; not deployed

## 1. Research question

Can an agent execution boundary require independently verifiable evidence of its own control history, rather than trusting a mutable local journal or signing whatever digest a client submits?

The concrete use case remains a coding agent proposing to merge a pull request. The approved action binds the executor principal to an exact repository, pull-request number, head SHA, base SHA, merge method, scope, validity window and authority epoch. A model may explain and propose; the deterministic boundary controls whether an effect may be released.

## 2. New work in v0.8

### Independent checkpoint authority

`checkpoint_authority.py` is a runnable HTTP service intended to run separately from the guard ledger. It uses SQLite for checkpoint history and Ed25519 signatures for receipts. The signing private key is held by the service process rather than returned to the client. The service binds to loopback only by default and uses bearer-token authentication. Each client must pin the public key through a trusted provisioning path.

Checkpoints contain journal ID, generation, event count, final sequence, root hash, timestamp and the hash of the previous signed checkpoint. Duplicate submissions of the exact latest root are idempotent; rollback and same-sequence forks are rejected. The service verifies that stored prior envelopes still match their signatures and metadata before advancing them.

### Independently verified journal extension

The service no longer just signs a client-supplied root. To advance from a trusted checkpoint, the client submits the event rows since the previously checkpointed sequence. The service recomputes each event hash, verifies continuous sequence numbering and predecessor hashes, and checks that the proposed event count / last sequence / root match the verified extension before signing the new receipt. Empty batches are valid only when the proposed checkpoint is exactly the already-known checkpoint.

This narrows a notable design weakness: a signing service that accepts any monotonically larger sequence and root can become a signing oracle for an unrelated chain. Extension validation binds the new root to the previous externally signed root. It still does not prove that the events are semantically true; a compromised writer credential can append fabricated but correctly hashed new events. Authentication of the event producer and review of authorization semantics remain separate controls.

### Workflow integration and fail-closed checkpoint cadence

`CheckpointedWorkflow` is the integration path. It verifies that the current local journal exactly matches the latest signed receipt before each mutation. It performs one mutation, extracts the event delta after the prior checkpoint, and waits for an independently verified checkpoint before declaring the operation checkpointed. For dispatch claims, the provider call is released only when the **post-claim** audit state has been externally checkpointed.

If an operation commits locally but the external checkpoint write fails, the wrapper returns `checkpointed=False`. The local journal is then ahead of the last trusted receipt and later automatic operations stop. This intentionally sacrifices availability rather than silently attesting uncheckpointed history. Recovery needs explicit operator investigation to distinguish a legitimate interrupted write from changed local history.

### Operational state versus audit history

An important second-order failure was found while wiring the checkpoint: a valid audit chain does not by itself prove that the current `approvals`, `authority` and `effects` tables still match that history. A database writer could leave the event journal intact but flip a terminal effect row back to `PREPARED`, change an approval's scope, or lower the authority epoch. A simple audit-chain check would miss those state-table edits.

The protected workflow now reconciles materialized rows to the checkpointed events before each state-changing operation. It verifies the approval table's exact membership and values against `APPROVAL_ISSUED`, verifies authority epochs against ordered `AUTHORITY_REVOKED` events, and reconstructs each effect's expected legal lifecycle from `EFFECT_PREPARED`, `DISPATCH_CLAIMED`, `EFFECT_CANCELLED`, `PROVIDER_RESULT` and `PROVIDER_RECONCILED`. It checks current action digests, scope, ownership, timestamps, status, reason and result JSON. Dispatch also runs that check inside its SQLite transaction.

Regression tests mutate a successful/ready effect state, approval scope and authority epoch without touching the audit journal; each edit is detected and provider dispatch is blocked. The claim method in the protected workflow also requires the live journal tail to equal the signed checkpoint exactly inside its transaction, closing the straightforward race in which a concurrent uncheckpointed append could otherwise slip between the wrapper's pre-check and the dispatch claim.

This check is deliberately narrow rather than a fully event-sourced database: every new operational column or state transition must be added to the consistency rules and tested. Direct calls that bypass the wrapper are outside the supported secure path.

### Request construction and provider condition

`github_rest_adapter.py` creates a merge request preview matching GitHub's documented REST endpoint shape: `PUT /repos/{owner}/{repo}/pulls/{pull_number}/merge`, with the approved head commit SHA in `sha` and the merge method in the body. This is a pure request builder with no HTTP transport. The end-to-end example invokes only a fake provider.

The expected-head SHA is a provider-side conditional control: GitHub documents that a mismatch returns HTTP 409. The endpoint does not offer a comparable expected-base-SHA parameter; base SHA therefore remains approval metadata and needs suitable protection/checks outside this single endpoint. A real implementation must validate current pull-request state, use the provider's conditional head check, record response evidence and treat ambiguous network outcomes as unknown. GitHub's merge endpoint does not supply a generic idempotency key just because the local fake provider uses `effect_id` for deduplication.

### Audit sequence fix

During integration hardening, I tightened the local verifier to require the first audit sequence to be 1, not merely to require continuity after whichever row happens to be first. This prevents a rehashed suffix beginning at sequence 2 from masquerading as a fresh genesis chain. The regression test deletes sequence 1 and recomputes subsequent hashes; verification rejects it.

## 3. Observed verification

Commands executed:

```bash
python -W error::ResourceWarning -m unittest -v test_action_guard_v07.py test_action_guard_v08.py
python run_verification_v07.py
python run_service_smoke_test.py
python run_v08_demo.py
python -m py_compile *.py
```

| Check | Result | Interpretation |
|---|---:|---|
| Combined unit/integration/regression tests | **50/50 passed** | 23 carried from v0.7, plus 27 v0.8 cases; `ResourceWarning` promoted to an error |
| Action mutation benchmark | **0/1,000 accepted** | Each case changes repository, PR number, head SHA, base SHA or merge method |
| Deliberately weak role/tool-only baseline | **1,000/1,000 accepted** | Demonstrates why tool-name authorization alone is insufficient in this toy case; not a production ACL comparison |
| Exact-action positive controls | **100/100 accepted** | Tested valid approvals remain usable |
| Concurrency benchmark | **25 winners / 200 attempts** | In 25 rounds of eight concurrent prepare attempts, exactly one prepared effect used each approval; 175 denied, no harness errors |
| Hash audit generated by benchmark | **2,250 events** | Local verifier considered the benchmark chain valid |
| Checkpoint extension validation | **Pass** | An intentionally invalid next-event hash was rejected without advancing the checkpoint |
| Checkpoint replay/rollback/fork | **Pass** | Exact repeat is idempotent; lower checkpoint and same-sequence different root rejected |
| Forged recomputed prior chain | **Blocked** | Recomputing hashes after rewriting a previously checkpointed row cannot match the prior signed receipt |
| Operational-state table edits | **Blocked** | Edits to effect status, approval scope or authority epoch disagree with checkpointed journal events and deny dispatch |
| Concurrent uncheckpointed append | **Blocked** | The dispatch transaction requires the current journal tail to match the signed checkpoint exactly |
| Concurrent revocation through same workflow object | **Serialized** | The per-instance effect-session lock queues revocation until the provider call and result checkpoint finish |
| Unicode provider evidence | **Pass** | Materialized result JSON is compared semantically, avoiding false alarms from escaped vs literal Unicode |
| Checkpoint outage after dispatch claim | **Provider not called** | The effect adapter does not receive an allowed-to-dispatch result without a post-claim receipt |
| Provider result with checkpoint outage | **Future work blocked** | Simulated effect can occur, but the uncheckpointed local tail blocks subsequent automatic effects |
| Separate-process authority restart | **Pass** | A signed empty-journal checkpoint survives process restart with the same envelope hash, pinned public key and mode-0600 private key |
| Live GitHub requests | **0** | No GitHub credentials, repository writes, or remote provider operations occurred |

The benchmark's output is saved in `v07_synthetic_benchmark_results.json`. `run_service_smoke_test.py` starts the authority through `subprocess.Popen`, calls it over loopback HTTP, restarts it and checks signature identity / persistence. The larger integration test suite hosts the HTTP server in a dedicated thread while exercising the real HTTP client and separate checkpoint database. These remain local, self-authored tests—not an independent audit or deployment.

## 4. Cybernetics interpretation

The closed execution loop is now:

`proposal → canonical action → human-identity field + scoped approval → durable intent → live-state/authority check → locally committed dispatch claim → independently verified and signed audit extension → provider conditional effect → outcome record → independently verified and signed result extension`

The model is an open interpretive instrument: it reasons, describes uncertainty and proposes actions. The deterministic boundary is the regulator: it enforces action identity, scope, expiry, revocation, single-use consumption and state transitions. The checkpoint service is an external reference for the regulator's history; it validates cryptographic continuity but does not inspect whether the action itself was wise or policy-compliant. Those are distinct jobs and should not be collapsed into a single “AI safety score.”

One control-theoretic caveat remains: no local transaction can be atomic with an arbitrary remote effect. A revocation after the dispatch claim cannot reliably cancel a request already in flight. The design defines the claim transaction as the local authorization linearization point and places a checkpoint barrier before the provider call, but a real system still needs provider-side conditions, explicit `UNKNOWN` handling and tested recovery logic.

## 5. External grounding

- **OWASP, AI Agent Security Cheat Sheet:** recommends separating decision-making from execution, binding high-impact approvals to the exact action, short-lived authorization, replay protection, idempotency where available, and fail-closed enforcement. [Source](https://cheatsheetseries.owasp.org/cheatsheets/AI_Agent_Security_Cheat_Sheet.html)
- **NIST NCCoE, Software and AI Agent Identity and Authorization:** focuses on standards-based ways to identify, manage and authorize software/AI agents and their actions; the 29 September 2026 update identifies secure software development / DevSecOps as the first implementation use case. [Project overview](https://www.nccoe.nist.gov/projects/software-and-ai-agent-identity-and-authorization) · [29 Sep 2026 announcement](https://www.nist.gov/news-events/news/2026/09/comments-software-and-agentic-ai-identity-concept-paper)
- **GitHub REST API, pull requests:** documents the merge `sha` parameter as the expected head commit and HTTP 409 when the supplied SHA does not match. [Source](https://docs.github.com/en/rest/pulls/pulls)

These sources ground the practical problem and provider API behavior. They do not validate Lycheetah's implementation or test results.

## 6. Remaining limitations and next experiment

1. **Separate trust domain:** current process smoke test uses a local process, local service database and local key file. Move it to a separately administered host/account or managed key service, enable TLS, add service workload identity, off-site retention and an independent rollback witness.
2. **Producer authentication and event truth:** bearer-token control is prototype-level. Authenticate the guard process using workload identity/mTLS, restrict which principal can append which journal, and define whether some event classes need a second signature. A checkpoint proves hash continuity, not truthfulness of newly appended events.
3. **Human and agent identity:** `approver_id` is still only a string. Add an authenticated approval interface, signed approval artifact, session/identity validation and a visible action preview.
4. **Real GitHub adapter in read-only/dry-run mode:** use a disposable test repository and narrowly scoped GitHub App credentials; exercise `GET` state, current head/base checks and request rendering with actual responses, but keep merge `PUT` disabled initially. Test wrong permissions, stale head, protected branch rejection, rate limits, webhook duplicates, and request timeouts.
6. **Failure injection:** simulate service restart or outage before and after a provider response, OS crash between transaction and checkpoint, lost HTTP responses, duplicate delivery and revocation during dispatch. Verify that recovery uses authenticated provider state instead of blind retries.
7. **Legacy migration:** the included v0.7 schema migration does not create an external genesis witness. Existing histories need a separately reviewed, supervised migration ceremony (or a fresh ledger) before the v0.8 workflow can trust them.
8. **External review:** conduct threat-model review and independent code review before anyone relies on this for real high-impact actions.

## 7. Conclusion

v0.8 is a meaningful engineering step over a hash chain in a local database: a separate signing service enforces a monotonic history, verifies each event in a proposed extension from the old trusted root, and signs only a consistent new anchor. A workflow wrapper makes successful external checkpointing a prerequisite for releasing a dispatch claim. A separate-process smoke test and synthetic fault tests exercise these mechanics.

The next best investment is not another conceptual framework. It is a separately administered checkpoint service and a read-only/dry-run GitHub adapter against real API responses, with live merge still disabled. The target property is simple to state and difficult to achieve: **no high-impact action is released unless the exact authorization state and the evidence that state was checked are both current, authentic and externally verifiable.**
