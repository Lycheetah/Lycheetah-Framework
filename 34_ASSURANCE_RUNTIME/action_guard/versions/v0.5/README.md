# Lycheetah Action Guard v0.5 — research prototype

## Use case
A coding agent proposes a high-impact action such as merging a specific pull request. A role-only ACL may allow the tool while failing to bind approval to the exact artifact, parameters, expiry, and current authority.

## What changed
- Canonical action hash binds approval to exact JSON parameters.
- Actor and required scope are checked.
- Approval is time-bounded.
- Monotonic authority epoch invalidates prior approvals after revocation.
- Effect IDs are replay-protected in-process.
- Denials and allowed actions are audit-recorded.
- A weak role/tool ACL baseline is included.

## Run
```bash
python3 -m unittest discover -s tests -v
```

## Evidence classification
- TESTED HERE: deterministic unit tests in the supplied local prototype.
- SIMULATED: in-memory authorization and effect registry.
- NOT DEPLOYED: no GitHub API, provider transaction, durable database, remote revocation, or real agent integration.
- NOT PROVEN: distributed atomicity, race safety across processes, crash recovery, protection against compromised host/runtime, correctness of the human approval UI, or policy completeness.

## Important boundary
`authorize_and_commit` is only atomic within this single Python process. A real provider side effect cannot be made atomic by inserting a local effect ID. Production deployment needs a transactional outbox or provider-supported idempotency key plus downstream revalidation at the moment of effect. Revocation must be checked by the authoritative executor at that same boundary.

## Research target
For a workflow of exact-artifact approval:
`proposal -> canonical action -> human approval -> final authority check -> effect`.
The model proposes; deterministic code enforces; external provider remains the final enforcement boundary.
