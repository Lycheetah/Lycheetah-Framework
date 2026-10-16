# Research note: Lycheetah Action Guard v0.7

**Date:** 16 October 2026  
**Area:** Agent safety, cybernetics, effect authorization, evidence integrity  
**Status:** Local implementation + synthetic verification; no deployment

## 1. The question

A guard can enforce an approval correctly and still leave weak evidence of whether it did so. If its audit table is freely editable, then the system's own account of approval, revocation and effect outcome can be falsified. Can the action boundary make its operational history verifiable—and refuse a high-impact action if the integrity of the relevant history cannot be established?

## 2. The practical use case

A coding agent proposes merging a pull request. The desired authorization is not “this agent may use `github.merge`.” It is a bounded statement about the exact repository, pull request, head SHA, base SHA, merge method, actor, scope, validity window and authority epoch.

The v0.6 work already bound approval to that action, made approval consumption single-use, persisted effect state, and handled uncertain provider outcomes explicitly. v0.7 strengthens the evidence substrate used at the dispatch boundary.

This use case has direct external relevance. On 29 September 2026, NIST/NCCoE announced that its first implementation use case for software/AI-agent identity and authorization would be within the software development lifecycle, in collaboration with the DevSecOps project. This is not validation of Lycheetah; it indicates that agent identity and authorization in software workflows is an active standards/practice problem. [NIST announcement](https://www.nist.gov/news-events/news/2026/09/comments-software-and-agentic-ai-identity-concept-paper).

## 3. v0.7 change

Each audit event is serialized canonically and hashed with its sequence, timestamp, actor, approval and effect references, event type, reason, details and prior event hash. A chain verifier checks sequence continuity, predecessor links and event digests.

A chain alone is insufficient against a writer who can alter the database and recompute the hashes. It also cannot identify removal of the newest events when no later event remains to point back to them. Therefore v0.7 requires a previously captured checkpoint to be supplied to `claim_dispatch`. The checkpoint contains event count, last sequence and root hash, and it must be stored outside the database's trust boundary. The verifier then checks that the complete journal is internally consistent and still contains the exact checkpointed prefix. New legitimate events may extend the chain after the checkpoint.

If the caller omits the checkpoint, changes the checkpointed prefix, truncates it, edits a middle event, or rewrites the old chain so its current root differs from the retained anchor, dispatch is denied. This is **tamper-evident, not magically tamper-proof**: the separately held checkpoint and the mechanism that authenticates/updates it are part of the security boundary.

The package also migrates v0.6 audit rows by adding hash fields and computing a new chain. This is a schema migration and new baseline, not retroactive proof of the old history's integrity.

## 4. Test design and observed results

Commands run in the package directory:

```bash
python3 -m unittest -v test_action_guard_v07.py
python3 run_verification.py
python3 run_synthetic_scenario.py
```

| Check | Observed outcome | What it supports |
|---|---:|---|
| Unit tests | 23/23 passed | The authored behaviors in the suite currently pass |
| Exact action mutations | 0/1,000 allowed | The action digest binding rejects the tested changes |
| Deliberately weak tool-only baseline | 1,000/1,000 mutated actions allowed | Tool-name-only permission is too coarse for this toy merge action |
| Positive controls | 100/100 accepted | The tested exact approved action remains usable |
| Concurrent prepare races | 25 rounds; 25 winners, 175 denied | SQLite transaction + single-use approval admitted only one intent per approval in these tests |
| Audit chain after generated benchmark | 2,250 events; valid | Appended rows matched the implemented hash-chain verifier |
| Edit + recompute attack | Internal chain passes, saved-anchor verification fails; dispatch denied | Independent checkpoint adds evidence that a local hash chain alone lacks |
| Tail truncation | Internal remaining chain alone may pass; previously saved anchor causes dispatch denial | A retained external checkpoint detects deletion of the checkpointed suffix |
| Legacy audit migration | Test legacy row survives and verifies after migration | v0.6-schema migration path functions for the fixture |
| Live provider calls | 0 | All tests are synthetic; no GitHub merge was attempted |

This is not a benchmark of general model safety. The comparator was intentionally weak and the tests are self-authored. They do not show superiority against mature authorization, logging, database hardening or audit services. They do not cover a compromised host that can also alter the external anchor store.

## 5. Cybernetics interpretation

The system can be modeled as a controlled loop:

`proposal → canonical action → human-bound approval → durable intent → current-state/authority check → integrity check → provider-conditional effect → observed result → audit checkpoint`

A model supplies interpretation and candidate plans; a deterministic boundary decides whether the candidate is authorized. But the audit trail is a sensor only if its evidence can be trusted. A control loop with unverifiable observations can confidently regulate the wrong state. The external checkpoint adds an independent reference value against which the local sensor history can be checked.

In Lycheetah terms, this separates the open interpretive instrument (model, rationale, and suggested action) from the closed authority regulator (typed action, approval, live state, dispatch, and recorded effect). The descriptive language can make intended action legible; it does not itself grant authority. The checkpoint is a provenance control, not an intelligence metric.

## 6. External grounding

- [OWASP AI Agent Security Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/AI_Agent_Security_Cheat_Sheet.html): recommends least privilege, explicit approval for high-impact actions, approvals bound to the exact action, replay protection, and fail-closed enforcement at the execution boundary.
- [NIST/NCCoE identity and authorization announcement, 29 September 2026](https://www.nist.gov/news-events/news/2026/09/comments-software-and-agentic-ai-identity-concept-paper): selects software development lifecycle / DevSecOps as the first implementation use case for demonstrating AI-agent identity, authentication and authorization.
- [GitHub REST API: pull requests](https://docs.github.com/en/rest/pulls/pulls): the merge API accepts `sha` as the head commit that must match; a mismatch returns HTTP 409. This is an example of a provider-side conditional check needed to close a local read/write race. It is not a claim that GitHub offers a generic client idempotency key for merge requests.
- [AWS Prescriptive Guidance: transactional outbox](https://docs.aws.amazon.com/en_en/prescriptive-guidance/latest/cloud-design-patterns/transactional-outbox.html): discusses cross-service consistency, duplicate delivery and why consumers should be idempotent.

## 7. What remains unproven

1. **External checkpoint operations:** build an actual separately authenticated checkpoint service or use a storage system with immutability/retention guarantees. It must record checkpoints reliably and reject rollback to older roots.
2. **Identity:** authenticate the human approver and the executor; bind approval to a visible action rendering and verified session, not an arbitrary `approver_id` string.
3. **Provider adapter:** implement a dry-run GitHub API adapter in a disposable repository; pass the approved head SHA to the merge endpoint; record provider response IDs and authoritative state.
4. **Recovery:** inject timeouts before send, after send, after provider success but before local recording, restarts, duplicate webhooks and concurrent revocation. Reconcile `UNKNOWN` with authenticated provider evidence rather than retrying blindly.
5. **Independent review:** test threat assumptions, database tampering, checkpoint service failure, compromised agent credentials, provider permission scope and whether failure modes are actually fail-closed.

## 8. Conclusion

The result is narrower but stronger than saying “we added audit logs.” v0.7 makes integrity of the previously checkpointed audit history a condition for dispatch and demonstrates that an independently retained root can detect an attacker who rebuilds the local chain. The security property depends on actually retaining that root elsewhere; without that integration, the internal chain alone does not establish trustworthy history.

The next best investment is not another abstract layer. It is the external checkpoint service plus an authenticated dry-run provider adapter, followed by fault-injection tests against real API semantics while keeping actual merges disabled until independently reviewed.
