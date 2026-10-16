# Crash/Recovery Results v0.7

**Run date:** 2026-10-16  
**Scope:** synthetic, deterministic, separate-process Python harness  
**Suite result:** 26 tests passed; see `authority_boundary_lab_v0_7/test_output_v0_7.txt`.

## Findings we can support

1. **Durable claim + eight-process replay:** eight host processes submitted the same approved token; exactly one dispatched and one provider effect was present. Seven replays were denied.
2. **Crash after claim, before provider request:** process exited after the durable claim. A fresh host process recovered using the same operation ID and produced one fake-provider effect.
3. **Provider exit before commit:** no provider effect was present. Recovery retried the same claimed operation and produced one effect.
4. **Provider exit after commit:** a durable provider record existed despite the missing response. Recovery reconciled it and did not create a second effect.
5. **Host exit after provider response:** the provider effect survived while the host ledger remained `CLAIMED`. A new host process reconciled the recorded effect.
6. **Recovery exit after provider response:** a second recovery found the existing provider record and completed reconciliation without duplication.
7. **Action/policy/approval binding:** changed action digests, wrong signing keys, stale policy revisions, revoked approvals, unclaimed approvals, and replayed approvals were denied or routed to review/conflict.
8. **Authority-state recovery rules:** recovery did not dispatch an operation that was merely `APPROVED`; it also did not redispatch a `COMPLETED` operation after its provider record was deliberately removed.
9. **Policy-update fence:** a competing policy update waited for the synthetic provider's authority-store lock and committed after the effect in the controlled race. A provider request carrying an old policy revision after an explicit policy update was refused.
10. **Revocation fence:** a revocation started while the synthetic provider held the dispatch fence serialized after that effect; future use of the same token was denied. Revocation before provider entry stopped the operation in the recovery path.
11. **Idempotency-key payload conflict:** the fake provider refused an operation ID whose stored action digest conflicted with the approved request.

## Why this is meaningful

Earlier iterations protected local approval tokens but had weaker recovery assumptions. v0.7 treats process death, durable authority state, provider effect records, and recovery status as separate things. It specifically prevents the recovery mechanism from becoming an alternate authorization path.

This follows established engineering practice rather than introducing a novel distributed transaction. Stripe documents idempotency keys and parameter matching as a mechanism for safely retrying API requests; AWS discusses safe retries and semantic equivalence; SQLite documents the scope of its local transaction guarantees. References:

- Stripe, *Idempotent requests*: https://docs.stripe.com/api/idempotent_requests
- AWS Builders' Library, *Making retries safe with idempotent APIs*: https://aws.amazon.com/builders-library/making-retries-safe-with-idempotent-APIs/
- SQLite, *Transactions*: https://www.sqlite.org/lang_transaction.html

## Limits that remain

The provider/authority fence uses one local SQLite authority store to serialize policy/revocation changes against a fake effect ledger. That is not transferable to a remote provider. The external equivalent must be part of the provider contract—e.g. request idempotency, a conditional version/fencing token, and durable lookup/reconciliation semantics. If the provider cannot authoritatively determine whether an effect occurred, automatic retry is not justified.

The approval identity values are fixture inputs. No model-generated tool calls were run, no actual MCP client/server was exercised end-to-end, no real money moved, no production secrets were used, and no independent security review was performed. These test results validate only the specific local implementation and authored test cases.
