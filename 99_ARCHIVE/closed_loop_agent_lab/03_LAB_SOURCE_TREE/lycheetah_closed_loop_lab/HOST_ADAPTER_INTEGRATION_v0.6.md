# Fake-host integration experiment — v0.6

**Status:** synthetic local integration test. No external provider, authenticated reviewer, production host, or live model was used.

## Purpose

The v0.5 gate fixes the v0.4 callback-selection gap in the local reference design by resolving an approved action through a host-owned dispatcher registry. The next engineering question is whether the pieces behave correctly when connected through an outer-host-shaped workflow and a provider can commit an effect but return a timeout.

## Harness

- `fake_host_adapter.py` wires together a registry, a deterministic fake approval UI, `ApprovalAuthority`, `ConsequenceGate`, and an in-memory `FakeProvider`.
- Every proposal receives a host-generated `operation_id`, included in the canonical approved action and passed to the provider.
- The fake provider records an operation by ID. It can return normally, time out before commit, or commit then time out.
- After a timeout, the adapter queries the provider by operation ID. If the operation exists, it reports reconciled success. If the outcome cannot be found, it stops for human reconciliation. It never blindly replays the consumed approval token.

## Observed local cases

The eight tests cover: exact action displayed and dispatched, no approval means no token/effect, policy drift, changed action, revocation before dispatch, timeout after commit, timeout before commit, and eight concurrent duplicate calls.

Results of this deterministic fixture:

- valid approval yields one fake-provider effect;
- changed action, changed policy, or revoked token yields zero provider effects;
- eight parallel attempts sharing one token result in one committed fake-provider effect and seven replay denials;
- after-commit timeout is reconciled by operation ID with one recorded effect;
- pre-commit timeout remains uncertain at the adapter boundary, so the system stops rather than retries blindly.

These results verify authored code paths for the fake provider. They are not probability estimates and do not prove provider semantics in a real integration.

## Limits

- The approval UI is a test double. Its `reviewer_id` and `approval_ref` are fixture strings, not authenticated identity evidence.
- The gate and adapter run in one process. This does not prove isolation of the signing key or issuer from a model process.
- Fake-provider state is in memory, not durable across a process restart. The gate's SQLite replay table is local persistence, but the combined test does not simulate a host crash between provider commit and reconciliation.
- There is no live Lycheetah host dispatcher in this harness; the inspected Guard MCP service is a receipt-producing assessor and explicitly leaves enforcement to the client host.

## Correct next step

Promote the harness to a separate-process test with a durable fake-provider journal and authenticated test-only approval service. Inject crashes at these boundaries: before nonce claim, after nonce claim/before provider, after provider commit/before response, and after response/before local completion journal. Assert single effect or explicit unknown state, never silent duplicate execution. Continue to use a fake provider until those semantics are established.
