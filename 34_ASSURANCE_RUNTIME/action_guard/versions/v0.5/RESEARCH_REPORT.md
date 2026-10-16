# Lycheetah Research Pass 2 — Action-Bound Authority for Agent Tools

**Date:** 2026-10-16  
**Status:** Local reference prototype; deterministic unit tests and synthetic benchmark passed; not deployed.

## Executive result

This pass takes the previous Action Boundary / cybernetics work into a concrete, narrowly scoped use case: an AI coding agent proposes a high-impact action such as merging a pull request. A conventional role/tool ACL can answer “may this identity invoke the merge tool?” but does not necessarily answer “did a human approve this exact repository, pull request, head commit, base commit, and scope, and is that approval still live at the effect boundary?”

I built **Lycheetah Action Guard v0.5**, a standard-library-only Python reference monitor that binds an approval to the canonical JSON action, actor, scope, validity window, current authority epoch, and unique effect ID. The prototype records allow/deny decisions and fails closed on missing, changed, expired, revoked, wrong-actor, wrong-scope, and replayed approvals.

## What changed

1. **Exact-action binding:** approval includes SHA-256 over canonicalized action parameters, not merely a tool name.
2. **Revocation epoch:** increasing an actor's authority epoch invalidates approvals minted under the old epoch.
3. **Expiry:** approval is denied at `now >= expires_at`.
4. **Scope binding:** requested scope must match the approved scope exactly.
5. **Replay prevention:** effect IDs are accepted once within this process.
6. **Audit trace:** allow/deny, reason, actor, approval, timestamp, scope, and action digest are recorded.
7. **Conventional baseline:** a role/tool ACL is included to show the specific failure this adds protection against.

## Test evidence

### Unit tests

`python -m unittest discover -s tests -v` — **10/10 passed**.

Coverage: exact approved action accepted; altered parameters denied; scope mismatch denied; expired approval denied; revoked approval denied; duplicate effect denied; missing approval denied; wrong actor denied; baseline allows altered action; direct baseline-vs-guard differential.

### Synthetic mutation benchmark

`python run_benchmark.py` — deterministic seed `20261016`, **1,000** post-approval mutation cases.

| Measure | Role/tool ACL baseline | Action Guard |
|---|---:|---:|
| Tampered actions accepted | 1,000/1,000 | 0/1,000 |
| Tampered-action rejection rate | 0% | 100% |
| Exact approved actions accepted (positive control) | 1,000/1,000 | 1,000/1,000 |

Each case mutates one of repository, pull-request ID, head SHA, or base SHA after approval. The baseline has a rule allowing `github.merge`; it has no artifact-bound approval concept. The guard's approval hash therefore detects the mutation.

**Interpretation boundary:** these numbers prove only that this prototype's deterministic checks catch the mutation class used in the benchmark. They do not demonstrate safety against all agent attacks, production races, or a real GitHub integration. The baseline is intentionally narrow and is not a claim that mature GitHub protections are ineffective.

## Cybernetic interpretation

The design turns the safety claim into an effect-bound feedback loop:

`proposal -> canonical action -> scoped approval -> final authority/revocation check -> effect record -> audit`

The LLM is a proposal generator, not the authority source. The deterministic guard is the comparator/gate. The provider executor is the actuator/effect boundary. The audit record is a sensor for subsequent review. If revocation state is not read by the final executor, or if the effect occurs outside the guarded path, the loop is open and this guard cannot claim control over it.

A key cybernetic invariant is:

`effect(action) => approval_hash == hash(action) AND approval_live AND scope_match AND authority_epoch_current AND not_replayed`

This implication is only enforced within the local prototype's method call. It is not a proof about a distributed system.

## Connection to LAMAGUE

LAMAGUE's typed fields—authority, unknowns, invariants, participants, value flow, and recovery—can describe the decision record. But a semantic record alone does not enforce a permission. This prototype keeps the distinction explicit: LAMAGUE may represent the proposed action and its obligations; the guard enforces authorization at the execution boundary. A future adapter could serialize these fields into a typed LAMAGUE packet, but this pass does not claim such an adapter exists.

## What it enables today

- A developer can run the tests and benchmark locally with Python 3 and no external dependencies.
- The code can serve as a design reference for approval-bound GitHub, deployment, email-send, or destructive-tool workflows.
- The tests can become regression cases when wiring an actual tool executor.
- The action digest makes review target explicit and inspectable instead of relying on a generic “approved” boolean.

## What remains unverified / required before deployment

1. **Distributed atomicity:** local approval check and remote provider effect are not one transaction. Production needs provider-side revalidation and/or idempotency keys plus a transactional outbox pattern.
2. **Concurrent races:** this in-memory code is not a concurrent, multi-process authority service. Locks or database transactions and linearization guarantees are required.
3. **Durability/crash recovery:** approvals, revocations, effect IDs, and audit records are not persisted.
4. **Trustworthy clock and authority:** callers supply `now`; production must obtain time and current authority from trusted infrastructure.
5. **Provider integration:** no GitHub API, OAuth scope enforcement, merge queue, or branch protection is invoked here.
6. **Human approval UX:** the UI must render the canonical target and parameters faithfully and defend against approval fatigue.
7. **Policy coverage:** this only checks the stated approval contract; it does not decide whether the proposed action is wise, safe, legal, or within broader organizational policy.
8. **Independent replication:** benchmark and tests were authored and run in this research pass; they are not external validation.

## External alignment

OWASP's Excessive Agency guidance recommends minimizing tool permissions and functionality, enforcing authorization downstream, and requiring human approval for high-impact actions. The prototype is consistent with those principles and makes one part concrete: approval is bound to the exact action and rechecked against current authority. See:

- https://genai.owasp.org/llmrisk/llm062025-excessive-agency/
- https://cheatsheetseries.owasp.org/cheatsheets/AI_Agent_Security_Cheat_Sheet.html
- https://www.nccoe.nist.gov/sites/default/files/2026-02/accelerating-the-adoption-of-software-and-ai-agent-identity-and-authorization-concept-paper.pdf

## Recommended next experiment

Integrate the reference monitor into a *dry-run* GitHub merge workflow using a test repository. Use a real pull-request head SHA as the action identity; generate approvals through a separate human confirmation UI; re-read PR head/base and authority immediately before calling the merge API; record provider response and idempotency behavior. Test concurrent revocation, head changes after approval, replay, timeout, process restart, and network failure. Keep merge execution disabled until the dry-run demonstrates expected denials and trace integrity.
