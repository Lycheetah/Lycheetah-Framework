# Research note: Action Guard v0.6 — from approval tokens to durable effect state

**Date:** 16 October 2026  
**Status:** Local prototype and synthetic verification only; not deployed.

## Question

Can an agent-safety boundary go beyond “the user approved this tool” and preserve the exact authorization decision across concurrency, restarts, revocation, and uncertain external effects?

## Result in this pass

A standard-library Python + SQLite prototype makes the approval/effect relation durable and single-use. It persists approvals, distinct approver and executing-agent identities, the executor's authority epoch, effect state, and audit events. It transactionally validates authorization and a trusted current pull-request snapshot before moving an intent from `PREPARED` to `DISPATCHING`.

The approval row records an approver identity separately from the executing agent identity; at this prototype stage, the approver label is not cryptographically authenticated, so production must bind it to a verified identity/session and immutable approval event.

The most important semantic distinction is that local authorization and a remote side effect are not one atomic transaction. A revocation can reliably block an intent that is still `PREPARED`. If the intent has already crossed to `DISPATCHING`, the external request may be in flight; a local epoch increment cannot promise cancellation. A timeout after sending a request yields an `UNKNOWN` outcome until provider state can be reconciled or the provider guarantees idempotency.

## Synthetic tests

The bundled tests cover normal dispatch, action mutation, expired approvals, revocation before preparation and after preparation, changed pull-request head before dispatch, a simulated state change between local claim and provider call, one-time approval consumption, persistence across reopening the database, audit persistence, unknown-outcome fail-closed behavior, definitive reconciliation after an ambiguous result, a simulated crash after provider effect but before local result recording, and eight concurrent attempts to consume one approval. The separate verification runner executes 1,000 parameter-mutation cases, 100 exact-action positive controls, and 25 eight-way races (200 concurrent attempts).

Run the tests locally to obtain exact current output. These are authored tests against this prototype, not independent validation. The fake provider includes conditional SHA checks and stable idempotency-key deduplication by design, so it cannot be used to claim that a real provider has the same semantics.

## External grounding

- OWASP's AI Agent Security Cheat Sheet recommends least privilege, explicit approval for high-impact actions, action-bound approvals, replay protections, audit trails, fail-closed behavior, and separation of model proposal from independent execution enforcement: https://cheatsheetseries.owasp.org/cheatsheets/AI_Agent_Security_Cheat_Sheet.html
- OWASP's Excessive Agency guidance says authorization should be enforced at the downstream action boundary, not entrusted to the LLM: https://genai.owasp.org/llmrisk/llm062025-excessive-agency/
- NIST NCCoE is actively exploring standards-based identity and authorization for software/AI agents, including identification, authorization, audit, non-repudiation, and prompt-injection risks: https://www.nccoe.nist.gov/projects/software-and-ai-agent-identity-and-authorization
- GitHub REST API documentation states the merge endpoint accepts `sha`, which is the expected pull-request head SHA; a mismatch returns HTTP 409. The asynchronous merge endpoint also accepts `sha` and documents canceling a merge if the PR head changes between request and execution. These provider checks are essential because a local re-read alone is subject to a read/write race: https://docs.github.com/en/rest/pulls/pulls
- AWS describes the transactional outbox as a pattern for avoiding inconsistent writes across a database and downstream messaging system, and warns about duplicate messages and idempotent consumers: https://docs.aws.amazon.com/prescriptive-guidance/latest/cloud-design-patterns/transactional-outbox.html

## Benchmark discipline

This pass intentionally does not report a model-capability score or safety superiority percentage. It evaluates software properties in controlled test cases. The comparator from v0.5 was a deliberately weak role/tool ACL, not a representative mature access-control system. No claim is made that the new design is superior to all ACLs, nor that SQLite by itself proves end-to-end safety.

## Proposed next experiment

Create a provider-specific, dry-run-only GitHub adapter over a disposable repository:

1. Authenticate a narrowly scoped GitHub App or test credential, read PR/repository state, and pin repository + PR ID + head SHA + base SHA + merge method into the action digest.
2. Obtain explicit human approval of a visible rendering of that exact action digest.
3. Persist a single-use effect intent, then re-read state and check the authority epoch immediately before dispatch.
4. Use GitHub's expected-head-SHA conditional merge parameter; do not invent a provider idempotency guarantee.
5. If a request times out after possible transmission, enter `UNKNOWN`; query authoritative PR/merge state or use the asynchronous merge UUID path when available. Never blindly retry an uncertain merge.
6. Test stale head/base, approval expiry, concurrent revocation, duplicate event delivery, crash before send, crash after send, and timeout after provider commit. Capture request IDs and provider responses without exposing tokens.
7. Keep execution dry-run or guarded to a disposable test repository; independent review is required before any production scope.

## Lycheetah/cybernetics interpretation

This is a small concrete instance of the closed-loop/open-instrument distinction: the model proposes and explains; the execution boundary stores authority, constrains effect identity, samples updated provider state, and records outcome. Audit logs are only sensors until a policy reacts to them. Correct closure still depends on trustworthy identity, a provider enforcing conditional writes, reliable outcome sensing, and a bounded path from observation to action.
