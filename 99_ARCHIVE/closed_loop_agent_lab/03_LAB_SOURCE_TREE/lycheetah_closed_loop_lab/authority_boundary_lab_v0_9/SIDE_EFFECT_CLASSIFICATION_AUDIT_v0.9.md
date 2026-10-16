# Side-Effect Classification and Catalog Enforcement — v0.9

**Status:** source-level audit plus local regression reproduction. This is not a finding that the deployed Lycheetah Guard MCP server can execute an unauthorized external action.

## Source observations

The currently inspected [Guard MCP handler](https://github.com/Lycheetah/Lycheetah-Framework/blob/master/12_IMPLEMENTATIONS/applications/lycheetah_guard_mcp.py) exposes `tool_assure_tool(tool_name, arguments, scopes, side_effect)`. It forwards the caller's declared `scopes` and `side_effect` to `AssuranceEvent`, and sets `human_approved=None`; approval is not an MCP argument. In the [Assurance Runtime](https://github.com/Lycheetah/Lycheetah-Framework/blob/master/lycheetah/assurance/runtime.py), the approval-review finding is conditional on `event.side_effect` being true (as well as policy requiring approval and `human_approved` being `None`).

The [Guard setup contract](https://github.com/Lycheetah/Lycheetah-Framework/blob/master/12_IMPLEMENTATIONS/applications/LYCHEETAH_GUARD_SETUP.md) explicitly describes `assure_tool` as a receipt issuer and says the caller must truthfully declare side-effect metadata and enforce the returned `ALLOW`/`REVIEW`/`BLOCK` decision. It also says this service cannot prevent a caller from ignoring a receipt. The MCP server is therefore an advisory evaluator in this architecture, not the downstream dispatcher.

This creates a **host integration requirement**: untrusted model-facing metadata must not be the source of truth for whether an operation is mutating, which scopes it needs, or which concrete implementation executes it. A host that treats these fields as authoritative would violate the stated contract. This source-level observation does not establish that any deployed host does so.

## Failure discovered in our own v0.8 harness

v0.8 placed `check_policy_catalog_binding` in the catalog stamping utility and tested the happy path, but reused the older v0.7 host, whose `load_action` checked only a fixed route and `side_effect=True`. It did not require the catalog digest or rederive argument validation itself. Consequently, a handwritten action file in the old lab schema could bypass the stamping command.

`reproduce_v0_8_catalog_bypass.py` demonstrates the bounded fixture failure with a deliberately invalid synthetic refund (`amount_minor=-1`, `currency="BTC"`): the older fake host/provider accepts and records the fake effect, while v0.9 rejects the old unstamped action and accepts a properly catalog-stamped valid one. The effect is a local SQLite record only. This is a regression in our **research harness**, not a demonstrated vulnerability in the actual Guard MCP server.

## v0.9 correction

The host now independently validates the action against `DEFAULT_CATALOG` before issuing approval and again before claiming execution. The canonical action contains the catalog digest. The active policy is schema-checked and must pin the same digest; its stored JSON body must hash to the stored durable policy digest. The fake provider checks the catalog and policy binding again inside its own boundary before committing the fake effect.

The validation rejects:

- old action schemas that omit the catalog digest;
- unexpected action metadata;
- altered effect classification, scope, dispatcher identity, or dispatcher version;
- invalid/missing/unknown argument fields, Boolean-as-integer amounts, nonpositive amounts and unsupported currency values;
- policy/catalog digest mismatch at issuance, claim, retry, or provider commit.

Recovery is intentionally asymmetric: it must not dispatch a new effect under a changed catalog, but if an existing provider effect can be looked up and its exact action digest matches the durable operation record, the host should reconcile that fact rather than refuse to acknowledge reality merely because the current catalog has changed.

## Local results

- 21 catalog and issuance integration tests passed.
- 28 separate-process crash/recovery tests passed.
- The retained bypass reproducer passed its expected comparison: the old lab accepts the invalid action; the v0.9 host rejects that old action schema; a valid catalog-stamped action succeeds in the fake provider.
- Both test suites ran in separate interpreter processes using `python -S run_v0_9_tests.py`.

These tests are authored deterministic fixtures. They do not measure the effectiveness of an AI model, an authenticated human approval UI, a real MCP client host, a real provider or production deployment.

## Remaining requirements before real integration

1. Put the catalog, policy, issuer key, human identity and dispatcher registry behind a trusted host boundary that model-executed code cannot write to or invoke arbitrarily.
2. Bind displayed approval to the exact human-visible action, including recipient/resource, amount, side effects, workspace and provider route/version.
3. Use provider-native idempotency keys and result lookup; represent unknown outcomes as unknown, not as failure.
4. Test host and provider under distinct OS/service identities, then independently review the security boundary.
5. Perform the R2 harmless repository task with a frozen contract and independent correctness adjudication before claiming agent capability improvement.
