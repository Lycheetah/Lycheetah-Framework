# Next experiment — R2 harmless repository task with independent correctness review

## Current decision

The lab currently reports **166 test methods across six separately executed suites**: 66 legacy tests, 26 v0.7 crash/recovery tests, 18 v0.8 trusted-catalog tests, 21 v0.9 catalog/issuance tests, 28 v0.9 crash/recovery tests, and 7 source-equivalent parser-fixture tests. This is an aggregation of independent local suite runs, not a single unified run. v0.9 adds **21 catalog/issuance tests** and **28 crash/recovery tests**, run as two separate interpreter processes via `python -S run_v0_9_tests.py`. These are separate records, not one aggregate pass: one combined `unittest discover` run timed out. See `test_output_v0_9.txt` and `PACK_MANIFEST.md`.

v0.8 responds to a source-level trust boundary in the current Guard interface: the caller-visible `assure_tool` input accepts `side_effect` and `scopes`; the documented design expects the caller to declare these truthfully and enforce returned dispositions. The source audit is in `authority_boundary_lab_v0_8/SIDE_EFFECT_CLASSIFICATION_AUDIT_v0.8.md`. This is not a report of an actual deployed bypass—the MCP server returns receipts and is not a tool dispatcher.

v0.8's catalog adapter only let the model propose `tool_name` and `arguments`, but it delegated to an older host that did not independently enforce the catalog binding. v0.9 fixes the research harness: host and fake provider rederive action metadata from the catalog; the action envelope and policy pin the catalog digest; invalid stamped metadata and invalid schemas are rejected at the boundary. The reviewer and provider remain fixtures, and no real external effect occurs.

## What is now demonstrated locally

- v0.1-v0.6 suites: 66 tests pass in `python run_all_tests.py`.
- v0.7: 26 crash/recovery tests pass when run with `python run_v0_7_tests.py`.
- v0.8: 18 catalog-stamping tests pass with `python run_v0_8_tests.py`.
- v0.9: 21 catalog/issuance tests and 28 separate-process crash/recovery tests pass with `python -S run_v0_9_tests.py`.
- The v0.8 bypass reproducer confirms the old local host accepted a handcrafted invalid action; v0.9 rejects the old action envelope, while a valid stamped action still completes in the fake provider. This is a local lab regression, not a production vulnerability finding.
- An untrusted proposal cannot set its own `side_effect`, scopes, dispatcher ID/version, agent ID, workspace ID or operation ID.
- An action's catalog class, route and scopes are derived from the catalog. Catalog drift fails the policy digest binding unless the trusted policy is updated.
- A stamped action can traverse the separate-process fake host/provider flow; mutating the stamped `side_effect` after approval prevents dispatch.
- v0.7's independent suite exercises crashes before and after a fake provider commit, recovery after host restart, replay protection, policy updates and revocation race serialization.

These are authored local tests, not model-based efficacy rates. The test-harness flaw in Base64URL tampering was corrected in v1.1 and is described in `TEST_HARNESS_FINDING_v1.1.md`. The `declaration_only_decision` comparison in v0.8 is a projection of the relevant source branch rather than a full execution of the current repository package; we inspected the actual source through read-only GitHub tools but could not clone the complete repository into this environment.

## Next gate: R2 real but harmless repository task

Use a disposable copy/branch of Lycheetah-Framework. Choose a narrow, non-consequential maintenance task such as adding an independently specified regression test to a pure helper. Freeze the task contract, exact accepted behaviors and held-out edge cases before running an agent.

Compare two workflows with the same model, workspace permissions, tools, token/time budget and test commands:

1. Conventional scoped workspace + tests + human review.
2. Same controls + independently checked postconditions + trusted tool catalog + authority/recovery instrumentation.

Blindly adjudicate correctness from the final diff and held-out contract. Record useful completion, false acceptance, false rejection, regressions, test failures, task time, review burden, attempted unauthorized operations and recovery. Include no-op patches, valid alternative implementations, deceptive caller metadata, wrong tests, and regressions that pass visible tests. Start in a harmless disposable workspace with no credentials and no consequential external tools.

## Remaining hard boundaries

- The v0.7 policy/revocation fence uses a shared local SQLite authority store; a remote provider needs native idempotency and provider-side conditional/fencing semantics. Local locking does not span a network boundary.
- A timeout with unavailable or eventually consistent provider lookup must not be interpreted as proof the effect did not happen.
- Reviewer names are test fixtures; no authenticated reviewer UI/IdP or distinct OS principal is in place.
- v0.9 catalog enforcement is still a local reference adapter, not integrated into `Lycheetah Guard MCP`; the real MCP tool remains an advisory receipt issuer. No live host adapter was validated.
- The tool catalog is fixed and authored for the synthetic test; no real provider's tool schema or effect semantics have been audited.

## Promotion gates

- **R0 — local research:** achieved for the prototype and source audit.
- **R1-harness — synthetic multi-process recovery:** exercised by v0.7, 26 tests.
- **R1-catalog — trusted effect classification/stamping:** exercised by v0.9, 21 catalog tests plus 28 process-recovery tests (independent suites).
- **R2 — one harmless repository task with independent correctness adjudication:** next.
- **R3 — paired held-out multi-task pilot:** only after R2.
- **R4 — bounded consequential pilot:** only after authenticated identity, key lifecycle, real provider idempotency/reconciliation, real revocation semantics, separate-principal containment, and independent security review.


## v1.1: test-harness integrity correction

The v0.4 and v0.5 local tests and v0.4 demo previously mutated the final character of an unpadded Base64URL token. For a 32-byte HMAC, the final character contains unused pad bits; replacing `A` with `B` can decode to the same signature. A fresh test run caught the false negative in v0.5. The helper now decodes the HMAC, flips a real byte, and re-encodes; a regression test asserts the decoded bytes differ. This strengthens the evidence quality of the existing local tests, not the security status of any deployed system.

## v1.4 result: receipt schema/parser contract

The newest R4 audit identifies reciprocal drift between the receipt schema and parser. The parser normalizes some invalid wire types into the same in-memory body, while the schema accepts malformed nested control properties and unknown finding fields the parser rejects. In the source-equivalent 20-row matrix, 18 cases were accepted by the modeled parser, 10 were rejected by the current schema, and the strict parser/schema candidates rejected all 20. Eight HMAC-sealed, normalization-preserving mutations still verify against the same digest; this does not forge HMAC, because the canonical body remains identical.

**Next gate:** run `PROPOSED_UPSTREAM_TESTS_v1.4.py` in a clean checkout with the parser and schema changes applied together; check persisted-receipt compatibility, then run assurance receipt, schema, CLI, OTel, regression and packaging suites on a known-green CI baseline. The current GitHub write path was denied, and no upstream files were changed. Do not extend this synthetic matrix further unless integration produces a new falsifiable question.
