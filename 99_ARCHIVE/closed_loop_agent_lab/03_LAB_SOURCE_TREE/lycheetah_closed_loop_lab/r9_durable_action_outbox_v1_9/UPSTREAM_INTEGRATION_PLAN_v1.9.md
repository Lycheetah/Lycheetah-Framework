# Upstream Integration Plan v1.9

## Stage 1 — adapt contracts, not copy the mock runtime

- Put a narrow adapter around the real `AssuranceRuntime.evaluate(event)` and use the actual verified receipt and policy digest.
- Keep trusted `EvidenceRequirement` policy server-side; callers cannot downgrade it per request.
- Bind the witness to the exact event, policy digest, requirement digest, receipt reference and operation ID semantics.

## Stage 2 — make authorization and intent durable atomically

- In one local transaction, verify the gate-owned issued witness registry entry, mark it consumed and insert one outbox row.
- Enforce unique constraints on witness ID and operation ID.
- On repeated enqueue after client timeout, return the existing operation record only when the exact event digest matches.
- Validate persisted canonical action bytes against their digest before every remote dispatch.

## Stage 3 — provider idempotency adapter

- Define a provider contract with `execute(operation_id, request)` and explicit durability semantics.
- Verify the real downstream service's dedupe row and business mutation share a transaction or provider-native atomic operation.
- Reject key reuse with altered payload.
- Define retention so delayed retries cannot outlive the deduplication record.
- Unsupported/ambiguous providers route to reconciliation; never blindly retry by default.

## Stage 4 — evidence consistency

A local SQLite transaction cannot freeze another service's evidence state. Choose one authoritative mechanism per dependency:

- provider-signed versioned evidence lease;
- conditional operation using an expected evidence version / ETag;
- provider-side compare-and-swap or transaction;
- or an explicit manual reconciliation path where no atomic condition exists.

Document whether requirement mode means exact evidence version or merely a predicate such as subject+status.

## Stage 5 — acceptance and release gate

- Run existing model, finality, MCP Guard, schema, runtime, finality, execution-cell and package-install tests in a clean full checkout.
- Add real integration tests for worker restart, killed process, provider response loss, idempotency key conflict, evidence-version change, and concurrent workers/processes.
- Run a controlled fake provider and then sandboxed integration; do not use real customer actions for first validation.
- Capture the complete CI baseline and all changed test outcomes.
- Promote only after human review of key management, trusted-host boundary, provider contract, retention and operational reconciliation.

## Limitation

No upstream branch or patch is created by this research pack. The earlier GitHub branch creation returned HTTP 403 via the connected integration. The proposed integration needs to be applied and tested against the actual upstream checkout.
