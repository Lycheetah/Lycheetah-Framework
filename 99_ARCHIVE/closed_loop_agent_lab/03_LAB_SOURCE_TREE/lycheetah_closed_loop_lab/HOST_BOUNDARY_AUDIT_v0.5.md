# Host boundary audit — v0.5

**Audit date:** 2026-10-16  
**Evidence type:** read-only source inspection through GitHub; no live host session or remote effect  
**Status:** [R0 research]. This report does not claim a deployed bypass.

## Scope inspected

- [`lycheetah_guard_mcp.py`](https://github.com/Lycheetah/Lycheetah-Framework/blob/master/12_IMPLEMENTATIONS/applications/lycheetah_guard_mcp.py): MCP tool handlers and server registration.
- [`LYCHEETAH_GUARD_SETUP.md`](https://github.com/Lycheetah/Lycheetah-Framework/blob/master/12_IMPLEMENTATIONS/applications/LYCHEETAH_GUARD_SETUP.md): published integration contract.
- [`tests/test_mcp_guard.py`](https://github.com/Lycheetah/Lycheetah-Framework/blob/master/tests/test_mcp_guard.py): scaffold-level MCP tests.
- [`lycheetah/assurance/runtime.py`](https://github.com/Lycheetah/Lycheetah-Framework/blob/master/lycheetah/assurance/runtime.py) and [`finality.py`](https://github.com/Lycheetah/Lycheetah-Framework/blob/master/lycheetah/assurance/finality.py): policy receipt and finality boundaries.

## Findings

### 1. Guard is an assessor, not the external tool dispatcher

`tool_assure_tool()` constructs a `Phase.TOOL` event, explicitly sets `human_approved=None`, evaluates it, and returns a structured receipt. It does not dispatch the declared action. The setup guide states that the caller must enforce `ALLOW`, `REVIEW`, or `BLOCK` and that the MCP server cannot prevent execution by a caller that ignores the receipt.

**Interpretation:** This is a clearly documented architectural boundary. It is not evidence that the live application ignores its decision; an outer host could enforce it correctly. The code inspected here cannot prove how an uninspected host behaves.

### 2. Human approval is intentionally not an MCP argument

The scaffold test asserts `human_approved` is absent from the `assure_tool` schema, and the handler fixes it to `None`. That is preferable to letting an agent self-assert approval in a tool argument, but it is not equivalent to authenticating a human and tying their UI confirmation to the exact dispatched request.

### 3. Tests prove the assessor contract, not enforcement in a host

The published MCP test calls `assure_tool` and verifies the structured `REVIEW` receipt and receipt-integrity handling. It does not invoke a real downstream tool dispatcher or a real approval UI. The test module is marked `scaffold` and can skip if the compatible MCP SDK is unavailable. No real host-adapter integration result was established during this source-only audit.

### 4. The current local v0.4 prototype had a narrower guarantee than its name suggested

A bounded counterexample is included at `authority_boundary_lab_v0_5/reproduce_v0_4_dispatcher_substitution.py`. It approves an `ActionIntent` declaring `refund_order`, then supplies a callback that records a differently named operation. The v0.4 reference gate invokes that callback because it receives the callback separately and does not resolve the destination from a trusted dispatcher registry.

No external provider was contacted. This is a reproducible gap in the local prototype's contract, not a finding against the deployed Lycheetah MCP host.

## Corrective design in v0.5

- A host-owned `DispatchRegistry` is resolved by tool name.
- The approved canonical action includes the dispatch target ID and semantic version.
- The gate chooses the handler internally; `execute()` no longer accepts an arbitrary callback.
- Current policy is fetched from a trusted provider configured at construction; callers cannot pass a digest override at dispatch time.
- Clock access is injected as a trusted host dependency rather than supplied for each execution.
- The signed token is bound to an audience/deployment identifier.
- A local revocation table can prevent a token from being consumed if revocation commits before the atomic nonce claim.
- Restart and concurrent replay tests verify the local SQLite claim remains one-use across gate reconstruction using the same database.

## Remaining limits

The prototype does **not** authenticate a reviewer, implement an approval UI, protect a key against the model if they share a process, independently attest that a dispatcher version accurately represents code semantics, or atomically commit a local nonce claim with a remote effect. A deployment needs provider idempotency/reconciliation, key lifecycle, a trusted approval issuer, durable revocation semantics, and independent adversarial review.

## Conclusion

The actionable current repository finding is an **integration contract to verify**, not a proven vulnerability: the Guard MCP server returns evidence-capped decisions, while enforcement belongs to the outer host. The local v0.4 experiment also had a callback-selection gap; v0.5 fixes that design gap in the reference code. The next valid step is a fake-provider integration harness at the true host dispatch boundary, not a safety superiority claim.
