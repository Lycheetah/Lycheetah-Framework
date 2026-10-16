# Prioritized next experiment

## Goal
Validate whether the authorization/evidence contract survives separation between the guard and its witness, followed by interaction with a real provider's read-only API surface.

## Phase A — independent checkpoint boundary
1. Run the checkpoint authority under a separately administered host/account or managed signing service; do not share administrator access or backup control with the guard host.
2. Provision the public key through a trusted out-of-band process; use authenticated workload identity or mutually authenticated TLS and rotate credentials.
3. Retain signed checkpoint receipts in independent, append-only/off-site storage or obtain a second witness so coordinated rollback of service database and key is detectable.
4. Test authority outage, network partition, key rotation, restore from backup, stale checkpoint, fork, replay, truncated history and a producer trying to append semantically invalid events.
5. State threat assumptions clearly: cryptographic chain continuity does not prove that new events are truthful or that the model's proposed action is wise.

## Phase B — GitHub read-only/dry-run
1. Use a disposable test repository and a narrowly scoped GitHub App that has no merge/write permission for the first pass.
2. Fetch pull-request head/base/number from the real API and render the approved exact-action request locally; verify the expected-head SHA request field from the official API contract.
3. Test missing permissions, stale head/base, protected branch rules, rate limits, duplicated webhooks, lost responses, restart during workflow and revocation at each state boundary.
4. Compare observed API state with the approval record; archive scrubbed fixtures and test output. No merge write.

## Phase C — only after independent review
Consider a tightly scoped test merge only after threat-model review, code review, authenticated human approval and failure recovery tests. The expected head SHA is a useful provider-side condition, but does not atomically enforce every field in the approval record, and a local effect ID is not a GitHub idempotency guarantee.
