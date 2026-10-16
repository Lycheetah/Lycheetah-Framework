# Authority Boundary Lab v0.9 — Catalog-Bound Host and Provider

**Status: R0 local research prototype.** This iteration repairs a weakness found in the lab's own v0.8 handoff: the trusted catalog was used by the stamping tool and tests, but the older host did not independently enforce the catalog/policy binding at approval and execution boundaries.

## What changed

- Every stamped action carries the exact catalog digest.
- The host derives tool metadata and validates the action against the catalog at approval issuance and execution claim.
- The active policy must have exactly the lab's required fields and a matching catalog digest. The stored policy body is checked against its durable digest.
- The fake provider validates the complete action against the same catalog before opening its effect transaction, then checks the durable policy body, policy digest, approval claim, operation ID, action digest, and revocation state while holding the fixture's authority-store fence.
- Recovery validates stored-action integrity first. If the provider already committed an effect with the expected operation/action digest, the host can reconcile that recorded fact even if the current catalog no longer authorizes a *new* dispatch. Current catalog and policy checks are required before retrying an absent effect.
- The v0.8 bypass is retained as a red-team reproducer rather than erased.

## Run

From the lab root:

```bash
python -S run_v0_9_tests.py
python -S authority_boundary_lab_v0_9/reproduce_v0_8_catalog_bypass.py
```

The runner uses two separate interpreter processes: 21 catalog/issuance integration tests and 28 crash/recovery tests, 49 total. A previous combined `unittest discover` invocation timed out once; no claim is made that a single combined discovery process passes. Use the runner above as the reproducible gate.

## Minimal model proposal

```json
{"tool_name":"refund_order","arguments":{"order_id":"ORD-42","amount_minor":2500,"currency":"NZD"}}
```

The host supplies agent/workspace identity, operation ID, scopes, effect classification, dispatcher identity/version and catalog digest. Unknown fields or invalid arguments are refused.

## Trust boundaries and limitations

- Both host and provider are local fake services running under the same OS user in these tests. The code's catalog is not isolated from other code in the same process or installation.
- Reviewer identity and approval reference are fixtures, not an authenticated UI or identity-provider assertion.
- SQLite authority-store fencing is shared only by the local fake provider. A remote API requires its own idempotency and conditional/fencing behavior.
- This is not connected to the real Lycheetah Guard MCP server and does not prove the production host enforces receipts correctly.
- The fake provider only performs the `refund_order` operation; `read_order` is used to test the catalog's read-only classification, not to exercise a real read provider.
- No live model, external payment provider, customer data, or production credentials are used.

Read `SIDE_EFFECT_CLASSIFICATION_AUDIT_v0.9.md` before interpreting results.
