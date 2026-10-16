# Trusted Tool Catalog / Side-Effect Classification — v0.8

**Status:** `[R0 local prototype]`. Nothing in this iteration modifies the public Lycheetah repository.

## Finding from the read-only source audit

The current `12_IMPLEMENTATIONS/applications/lycheetah_guard_mcp.py` defines:

```python
def tool_assure_tool(
    tool_name: str,
    arguments: dict[str, Any] | None = None,
    scopes: list[str] | None = None,
    side_effect: bool = False,
) -> dict[str, Any]:
```

It passes `scopes` and `side_effect` into an `AssuranceEvent`. The same handler's docstring says the caller is responsible for truthful side-effect declarations and enforcing the returned decision. `LYCHEETAH_GUARD_SETUP.md` says the MCP server cannot prevent a caller from ignoring the receipt.

In `lycheetah/assurance/runtime.py`, human-approval review is conditional on the event declaring `side_effect=True`, the policy requiring approval, and `human_approved is None`. If a caller declares `side_effect=False`, that particular review condition does not fire. The default policy does not deny the illustrative `refund_order` name. For an event with ordinary arguments and no other findings, the source logic can therefore return `ALLOW` for a mutating operation falsely declared read-only.

This is a **source-level deduction about an advisory decision interface**, not a finding that the actual MCP server executes refunds or has a bypass. The server is documented as a receipt issuer, not a downstream tool dispatcher. A host that trusts model-provided effect classification as authoritative would violate the documented trust boundary.

Sources inspected read-only:

- https://github.com/Lycheetah/Lycheetah-Framework/blob/master/12_IMPLEMENTATIONS/applications/lycheetah_guard_mcp.py
- https://github.com/Lycheetah/Lycheetah-Framework/blob/master/12_IMPLEMENTATIONS/applications/LYCHEETAH_GUARD_SETUP.md
- https://github.com/Lycheetah/Lycheetah-Framework/blob/master/lycheetah/assurance/runtime.py
- https://github.com/Lycheetah/Lycheetah-Framework/blob/master/lycheetah/assurance/policy.py
- https://github.com/Lycheetah/Lycheetah-Framework/blob/master/tests/test_mcp_guard.py

## Proposed integration pattern

The model proposes exactly:

```json
{
  "tool_name": "refund_order",
  "arguments": {
    "order_id": "ORD-42",
    "amount_minor": 2500,
    "currency": "NZD"
  }
}
```

A trusted host catalog—not the model—binds the exact name to:

- mutating versus read-only classification;
- fixed dispatcher identity and version;
- the complete required scope set;
- strict argument schema and value constraints;
- the catalog digest bound into the active approval policy.

The model cannot send `side_effect=False`, replace scopes, choose its own dispatcher, choose the workspace, or choose the stable operation ID. Extra fields are rejected rather than silently ignored.

The v0.8 adapter stamps the canonical action shape expected by the v0.7 synthetic host harness. The existing harness then binds the approval token to the whole stamped action and policy digest. Editing the catalog changes the catalog digest and fails policy binding until the trusted policy is explicitly updated.

## Results

Seventeen unit and integration tests passed. In one end-to-end local test, a minimal model proposal is stamped from the trusted catalog, approved by a fixture issuer, and sent through the v0.7 separate-process fake host/provider; one durable simulated effect is recorded. A second test alters the stamped side-effect flag after approval and confirms dispatch does not occur.

Other cases verify that untrusted proposals cannot set effect class, scopes, dispatcher, operation ID, agent ID, or workspace; unknown tools/arguments are rejected; invalid amounts/currency are rejected; and a catalog revision change invalidates the policy's declared catalog digest.

The comparison called `declaration_only_decision` in the tests is a bounded projection of the relevant source branch. It is **not** a call to the full Lycheetah Assurance Runtime, because this environment does not contain a checkout of the repository's complete package and dependencies. The actual source was inspected through read-only GitHub access.

## Remaining limits

- The registry and caller are not isolated in separate OS principals; this is a reference pattern, not a security boundary against code running inside the trusted host process.
- The policy/catalog digest convention is local glue. A real host must load a pinned catalog revision from trusted storage and enforce the same digest at approval and dispatch.
- The current fake provider only executes `refund_order`; `read_order` is used to test catalog classification, not exercised as a provider tool.
- Reviewer identity is still a test fixture. No real approval UI, identity provider, credential lifecycle or external provider is used.
- Local SQLite recovery tests remain separate from this suite. A real remote provider needs native idempotency and status reconciliation; local locking does not cross network boundaries.
- No model capability or safety superiority claim follows from these tests.
