# Lycheetah Closed-Loop Agent Lab — v1.6 upstream readiness

**Status: R0 research prototype. v1.6 consolidates receipt/policy parser hardening and adds source-pinned preflight plus a read-only persisted-record compatibility inventory.** This pack combines a synthetic regulator comparison, observer-sensitivity analysis, evaluator calibration, a local authority-boundary prototype, separate-process crash recovery, and catalog-bound host/provider enforcement. It is not a production agent, hardened sandbox, live-model evaluation, or evidence of deployment safety.

## Research question

Can an explicit task-outcome observer detect failures missed by conventional coding-agent controls—and can we trust the evaluator enough to authorize that observer to change decisions? The program is to establish useful capability while preserving observability, controllability, recoverability, and human review.

## What's new in v1.1

- `TEST_HARNESS_FINDING_v1.1.md`: corrected a false-negative test mutation caused by unpadded Base64URL pad bits.
- `run_v1_1_verification.py` and `aggregate_v1_1_verification.py`: run suites separately and aggregate only completed records. Six isolated suites currently report 166 test methods passed; no upstream package suite is claimed.
- `r2_policy_parser_audit/`: expanded the source-equivalent malformed-type matrix to 24 cases (baseline accepts 21, strict candidate rejects 24), added an upstream-ready pytest file, and a no-mutation patch preflight.
- `UPSTREAM_INTEGRATION_STATUS_v1.1.md`: records the read-only GitHub permission boundary and unresolved base CI state.

## What's new in v0.9

- `authority_boundary_lab_v0_9/tool_catalog.py`: canonical tool proposals are rederived against a trusted catalog at the actual host and fake-provider boundaries, not only in a separate stamping utility.
- Action envelopes include the catalog digest; current policy JSON must be bound to that catalog at approval issuance, execution claim, provider commit, and recovery retry.
- `authority_boundary_lab_v0_9/reproduce_v0_8_catalog_bypass.py`: retains a reproducible local failure from the earlier research harness: v0.7 accepted a handwritten invalid refund action; v0.9 rejects the unstamped schema and accepts a valid catalog-stamped action. Fake SQLite only.
- 21 catalog/issuance tests and 28 separate-process crash/recovery tests passed independently (49 total across two subprocess suites). See `test_output_v0_9.txt`.
- `authority_boundary_lab_v0_9/SIDE_EFFECT_CLASSIFICATION_AUDIT_v0.9.md`: documents the source-level concern, the old lab bypass, the correction, and remaining security boundaries.

## What's new in v0.8

- `authority_boundary_lab_v0_8/tool_catalog.py`: trusted host catalog stamps the model proposal's canonical tool/arguments with side-effect class, scopes, dispatcher identity/version and host context. The proposal schema rejects model-supplied approval metadata.
- v0.8 added catalog digest binding at the stamping utility and demonstrated a local happy path; v0.9 found that the older host itself did not enforce the binding when passed a handwritten action envelope.
- `authority_boundary_lab_v0_8/test_tool_catalog.py`: 18 tests, including an end-to-end local run through the v0.7 separate-process fake host/provider and post-approval action-tampering rejection.
- `authority_boundary_lab_v0_8/SIDE_EFFECT_CLASSIFICATION_AUDIT_v0.8.md`: source-level finding and limits; this is not evidence of a deployed Guard dispatch bypass.

## What's new in v0.7

- `authority_boundary_lab_v0_7/`: distinct host/provider OS processes, durable SQLite approval/operation and effect ledgers, crash injection, policy/revocation fence and recovery protocol.
- `CRASH_RECOVERY_RESULTS_v0.7.md`: 26 passing crash/recovery tests and explicit limitations, including why the shared SQLite fence is only a fake provider contract.
- The v0.7 suite is run separately from legacy suites because the combined nested runner did not finish reliably; see `NEXT_EXPERIMENT.md`.

## What's new in v0.6

- `HOST_ADAPTER_INTEGRATION_v0.6.md`: a synthetic outer-host workflow connected to the v0.5 reference gate and an in-memory idempotent fake provider.
- `authority_boundary_lab_v0_5/fake_host_adapter.py`: stable operation IDs, fake-reviewer display, trusted-registry dispatch, and reconciliation after provider timeouts.
- Eight additional tests cover approved dispatch, denial without approval, changed action/policy, revocation, concurrent duplicate use, timeout-after-commit reconciliation, and timeout-before-commit stop behavior.
- The legacy runner executes 66 tests across its four retained suites; v0.7 and v0.8 use independent runners.

## What's new in v0.5

- `HOST_BOUNDARY_AUDIT_v0.5.md`: read-only source audit of the actual Lycheetah Guard MCP component and its outer-host enforcement contract. The inspected server returns structured decisions; it does not dispatch external actions.
- `authority_boundary_lab_v0_5/`: corrective reference design after reproducing a callback-selection gap in v0.4. The execute API uses a trusted dispatcher registry and no longer accepts a per-call callback, current-policy digest, or time override.
- Dispatcher identity/version and deployment audience are signed; policy and clock are read from trusted host dependencies; local revocation and single-use consumption are covered by tests.
- `reproduce_v0_4_dispatcher_substitution.py`: bounded local counterexample. It records a mismatched callback label in memory and contacts no external system.
- `CHANGELOG_v0.5.md`: iteration record and limits.

## What's new in v0.4

- `authority_boundary_lab/`: host-signed, action-bound, time-limited, single-use approval gate for consequential actions, backed by a SQLite replay registry in this local prototype. It binds token validity to the canonical action and policy digests and dispatches the approved snapshot.
- `authority_boundary_lab/run_demo.py` / `demo_results.json`: seven synthetic cases compare a deliberately unsafe boolean-claim baseline against the candidate. The baseline is a failure-mode illustration, not a claim about the deployed Lycheetah integration.
- `authority_boundary_lab/test_authority_gate.py`: fourteen tests including wrong action/policy, expiry, tampering, sequential replay, concurrent token replay, frozen action snapshots, and uncertain effect handling.
- `AUTHORITY_BOUNDARY_FINDINGS.md`: evidence status, limitations, relation to established security practice and next engineering gate.
- `VERIFICATION_RESULTS.md`: recorded test counts, synthetic scenario outcomes and evidence limitations.
- `run_all_tests.py`: single project-root runner for all suites; it runs each suite from its required working directory, fixing the brittle cross-folder invocation.

## What's new in v0.3

- `observer_probe_v0_3/`: a local microtask with one explicit behavioral contract, a weak three-case public suite, a 19-check contract suite, two valid implementations with different structures, and six planted defects.
- `PROBE_RESULTS.md` and `probe_results.json`: candidate-by-candidate results. The public suite accepts four deliberately flawed candidates; the contract suite rejects these six authored defects and accepts both known-valid implementations.
- `COMMON_MODE_ERRORS.md`, `correlated_observers.py`, `correlated_observer_grid.csv`, and `correlated_observer_results.json`: formula and sensitivity grid showing how correlated observer errors can undermine an assumption of independent evidence.
- `CYBERNETIC_INTERPRETATION.md`: maps plant, target, controller, actuator, sensors, comparator, feedback, disturbances, and stop conditions to the coding-agent use case.

These results are calibration evidence about a small locally authored fixture, not results from a model or a representative benchmark.

## Earlier work retained

- `harness.py`: fourteen authored cases comparing conventional process gates with an extra postcondition/change-set observer.
- `test_harness.py`: eight tests of that synthetic decision fixture.
- `observer_stress.py`: 72 analytical sensitivity scenarios across assumed prevalences, sensitivities and specificities.
- `OBSERVER_VALIDATION_PROTOCOL.md`: frozen contract, trusted execution evidence, blinded adjudication, adversarial test checks, metrics, and promotion gates.
- `NEXT_EXPERIMENT.md`: proposed path to an instrumented real-task dry run and paired trial.

## Reproduce

Requires Python 3.10+ and only standard-library modules. Run retained suites separately from this directory:

```bash
python run_all_tests.py          # legacy suites: 66 tests
python run_v0_7_tests.py         # separate-process crash/recovery: 26 tests
python run_v0_8_tests.py         # original catalog-stamping integration: 18 tests
python -S run_v0_9_tests.py      # catalog-bound host/provider + crash recovery: 49 tests
```

Six test suites were run independently and their completed per-suite result files were aggregated by `aggregate_v1_1_verification.py`; this is not one single-process test run. A prior combined `unittest discover` invocation timed out once. v0.9 ran two independent interpreter suites: 21 catalog/issuance tests and 28 crash/recovery tests. See `VERIFICATION_RESULTS_v1.1.md`, `CRASH_RECOVERY_RESULTS_v0.7.md`, `NEXT_EXPERIMENT.md`, and `UPSTREAM_INTEGRATION_STATUS_v1.1.md` for the boundaries. Reproduce the original authority boundary demo and the v0.4 callback-gap counterexample with:

```bash
python authority_boundary_lab/run_demo.py
python authority_boundary_lab_v0_5/reproduce_v0_4_dispatcher_substitution.py
```

Run the original fixture and its tests from this directory:

```bash
python harness.py
python observer_stress.py
python -m unittest -v
```

Run the v0.3 calibration probe and tests:

```bash
cd observer_probe_v0_3
python run_probe.py
python correlated_observers.py
python -m unittest -v
```

The separate commands below remain available for focused debugging. They validate authored logic, not real-world accuracy.

## Key result from the local probe

The three-case public suite accepted 6/8 candidates, including four of six deliberately defective candidates. The larger contract suite accepted the two known-valid candidates and rejected all six planted defects. Crucially, a second valid implementation with a different internal structure was accepted; the suite checks behavior rather than matching the reference code's shape.

The result is deliberately scoped: all candidates and labels were authored in one fixture. That a hand-authored contract test passes planted examples is not proof that the contract is complete, and it says nothing directly about model quality.

## Cybernetic interpretation

A loop is not trustworthy merely because it closes. The reference state may be underspecified, a sensor may miss the essential variable, multiple sensors may share the same mistake, evidence may become stale, or the actuator may fail to enforce a stop. See `CYBERNETIC_INTERPRETATION.md` and `COMMON_MODE_ERRORS.md`.

## External context

OpenAI's July 8, 2026 audit of SWE-bench Pro estimated around 30% of tasks in the audited benchmark were broken, describing overly strict tests, underspecified prompts, low-coverage tests, and misleading prompts. This motivates evaluation quality controls but does not validate this prototype: https://openai.com/index/separating-signal-from-noise-coding-evaluations/

METR describes task-completion evaluations using repeated attempts, fixed environments and human review for potential reward hacking. This is relevant methodology to study when designing a paired pilot; it is not an endorsement of this particular prototype: https://metr.org/time-horizons/

## Current status and limits

- 14-case original decision fixture: authored deterministic scenarios.
- 72-row sensitivity grid: hypothetical parameters, no measured rates.
- v0.3 calibration task: eight local candidates, two labeled valid and six planted defects, no LLM-generated patch.
- Common-mode results: formula-based expectations, no observed correlation data.
- No live model was called; no real Lycheetah repository-maintenance task was executed; no sandbox or external effect was tested; no GitHub repository files were changed. The assurance and MCP source was inspected through read-only repository access; the local checkout did not include the full repository.
- v0.4 callback-selection gap is reproducible in the lab reference API. v0.5 removes the per-call callback and binds dispatch to a host-owned target ID/version, but trusted-host isolation and external effect reconciliation remain outside this prototype.
- The authority gate assumes a trusted host protects the HMAC key and issuance route, and authenticates the human. It does not do this itself. The current repository MCP server is a receipt issuer, not a downstream tool dispatcher; no live MCP host dispatch path was exercised. v0.7 models a durable fake provider using local SQLite and shared-store fencing; a local lock cannot provide remote atomicity. v0.8 initially bound the catalog at stamping time only; v0.9 corrects the lab host/provider to check it at the actual boundaries, but no authenticated reviewer, OS-separated trusted host, or real provider is present.
- No safety superiority, general model capability, or production reliability claim is supported.
- Established prior art matters here: SQLite guarantees atomicity within a local database transaction, while remote retry safety requires provider-native idempotency semantics (for example, Stripe's idempotency keys). Neither source makes a local lock atomic with an arbitrary remote API: https://www.sqlite.org/transactional.html and https://docs.stripe.com/api/idempotent_requests.

Repository context: https://github.com/Lycheetah/Lycheetah-Framework

## Current research iteration: v1.1 — parser microtask + test-harness integrity

The `r2_policy_parser_audit/` folder records a narrow source audit of `TextRule.from_dict` in the current upstream `lycheetah/assurance/policy.py` file. A source-equivalent fixture accepted 17 of 20 deliberately malformed field-type inputs; the strict candidate rejected all 20 while preserving valid strings and defaults. The upstream patch and pytest regression tests remain proposed and are not committed or run against the full upstream package. See `r2_policy_parser_audit/R2_REPORT.md` and `PACK_MANIFEST_v1.0.md`.


## v1.1 test-harness correction

A fresh run caught a flawed signature-tampering test: changing only the last unpadded Base64URL character could alter unused pad bits without changing decoded HMAC bytes. The v1.1 correction decodes the signature, flips a significant byte, re-encodes it, and tests that decoded bytes actually changed. The old test result is not used as evidence of a cryptographic weakness; this was a test-method defect.

## Latest research pass — v1.3

The R3 wire-schema audit examines coercion in assurance record deserializers. The local source-equivalent fixture passed 5 unit tests and 8 authored malformed-wire examples. The proposed patch is not upstream-applied; an early sparse-context check was inconclusive, and a later reconstructed-context check passed. No real-checkout `git apply --check` or full package suite was available. See [`r3_wire_schema_audit_v1_3/VERIFICATION_RESULTS_v1.3.md`](r3_wire_schema_audit_v1_3/VERIFICATION_RESULTS_v1.3.md) and [`r3_wire_schema_audit_v1_3/PATCH_VALIDATION_LIMITS_v1.3.md`](r3_wire_schema_audit_v1_3/PATCH_VALIDATION_LIMITS_v1.3.md).



## v1.3 evidence boundary

The newest wire-type audit adds a receipt-shaped digest normalization probe: 5 of 5 controlled type mutations normalized back to the original receipt body in the source-equivalent fixture; all 5 were rejected by its strict candidate. Seven local unit-test methods pass. This is not a run of the real upstream package. The proposed patch passes a synthetic context reconstruction, but the full-checkout `git apply --check` and upstream CI have not been run. See `r3_wire_schema_audit_v1_3/VERIFICATION_RESULTS_v1.3.md`.

## Latest research iteration — v1.4: schema/parser parity

The R4 audit widens the earlier parser investigation: it compares the packaged receipt JSON Schema, source-level deserialization behavior, and canonical digest/HMAC verification. In a 20-row source-equivalent matrix, the modeled parser accepts 18, the current schema rejects 10, and the strict parser/schema candidates reject all 20. Eight HMAC-sealed type mutations continue to validate under the modeled parser because they normalize to the same canonical body; this is not an HMAC break, but evidence that wire representation and canonical-body authentication are distinct contracts. The current schema is also open in nested control and finding objects, producing mismatches in the other direction. See `r4_schema_parser_parity_v1_4/SCHEMA_PARSER_PARITY_AUDIT.md` and `VERIFICATION_RESULTS_v1.4.md`.

The schema in the R4 directory is a readable semantic reconstruction, not a byte-for-byte archive. `PROPOSED_UPSTREAM_TESTS_v1.4.py` is intended for a clean checkout but has not been run there. The local differential test is source-equivalent; it is not proof of production impact or a full upstream package result.

## Latest research iteration — v1.5: policy contract parity

R5 moves upstream from receipts to policy configuration. The 20-case source-equivalent matrix found string coercion in policy text-rule fields and mismatches between the current schema and parser. The candidate schema/parser model agrees on 17 of 20 cases; remaining disagreements are explicitly scoped to regex compilation, cross-item rule-ID uniqueness, and JSON Schema integer semantics. Five local test methods passed. No upstream commit or full package test is claimed. See `r5_policy_contract_v1_5/POLICY_CONTRACT_AUDIT_v1.5.md` and `PACK_MANIFEST_v1.5.md`.


## Latest research iteration — v1.6: upstream readiness and migration compatibility

R6 consolidates the receipt wire-type work (R3/R4) with the policy parser/schema work (R5). The changes are staged as three ordered source patches and two candidate JSON Schemas. New regression tests cover text-rule type coercion, receipt schema-version normalization, `policy.sha256`, control extensions, and explicit-null `cap_reason` normalization.

The new `r6_upstream_readiness_v1_6/scan_migration_compat.py` is designed to inventory actual persisted policy/receipt JSON and receipt JSONL logs against the inspected base parser/schema and candidate contract **before** the stricter changes are applied. It is read-only and refuses non-base or modified checkouts, and writes reports outside the repository. The companion preflight checks exact source blobs and simulates all patches in a temporary copy.

Local evidence: 12 compatibility-tool tests pass; the combined R3–R6 standalone suites pass 31 test methods and 77 subtests; all three patches pass a synthetic hunk-context smoke check; both schemas pass Draft 2020-12 meta-validation. This is still not a full checkout apply check, full upstream test run, CI result, PR, or production claim. The GitHub branch creation attempt returned HTTP 403, so no source changes were written. See `r6_upstream_readiness_v1_6/RESULTS_v1.6.md`, `INTEGRATION_STATUS.md`, and `UPSTREAM_PROMOTION_CHECKLIST.md`.

## v1.8 — Trusted admission witness prototype

The newest focused experiment models witness provenance with an HMAC-authenticated body, trusted server-configured evidence requirements, a SQLite issuance registry and atomic one-use consumption. It passes 16 local reference tests, including 25 repeated two-thread race trials. The pack also includes an intentional demonstration that a separate evidence provider can change immediately after returning its snapshot; local one-use consumption cannot solve that external TOCTOU race or make a remote side effect atomic.

[Download the v1.8 research pack](sandbox:/mnt/data/lycheetah_closed_loop_agent_lab_v1.8.zip)

The prototype is not an upstream patch or a production-ready effect broker. It is not wired to the actual AssuranceRuntime, and the full upstream package test suite/CI has not been run. See `r8_trusted_witness_v1_8/README.md` and `UPSTREAM_INTEGRATION_PLAN.md` for boundaries and the recommended next step.

## v1.9 — Durable authorization-to-effect handoff

The latest iteration adds a local transactional outbox tied to witness consumption and a separate idempotent provider model. See `r9_durable_action_outbox_v1_9/README.md`, `FAULT_MATRIX_v1.9.md` and `DESIGN_AND_THREAT_MODEL_v1.9.md` for the testable protocol and explicitly open evidence-provider race.

Latest local verification: 27/27 v1.9 test methods passed, including 25 independent two-dispatcher races. The v1.7 and v1.8 reference suites also passed in this session (5/5 and 16/16 respectively). This does not establish full upstream integration or production guarantees.


## v2.0 — Evidence lease and TOCTOU closure experiment

Latest iteration: [`r10_evidence_lease_v2_0/`](r10_evidence_lease_v2_0/). The local prototype is designed to close the v1.9 snapshot-to-effect evidence race under an explicit cooperative authority contract. The authority atomically validates evidence and issues a version-bound, HMAC-authenticated dispatch token. Before the provider call begins, the token is claimed `IN_FLIGHT`; that state pins evidence even after TTL until the provider outcome is confirmed or reconciled. The simulated provider binds operation ID and action digest and atomically records the effect with its idempotency result.

Verification: 49/49 combined local test methods passed (27 preserved v1.9 tests + 22 new lease tests). A separate 200-round threaded SQLite race had zero invariant violations (79 update-first, 121 lease-first). The inherited v1.9 `test_external_evidence_can_change_after_dispatch_snapshot` intentionally reproduces the old TOCTOU weakness as a negative control; its pass is not a safety claim.

Boundary: single-host reference prototype only. It assumes all evidence mutations honor the lease authority and the downstream effect provider supports a suitable lease/conditional-commit and durable idempotency contract. A started IN_FLIGHT action remains pinned past TTL until its outcome is reconciled; this intentionally trades availability for safety. No actual upstream source has changed; the upstream suite/CI and a real provider integration remain unrun.


## v4.5 — Process-bound shared ingress leases

The v4.5 reference binds shared ingress leases to Linux PID plus process-start ticks and to the shared PID namespace configuration. Expiry alone no longer releases an active slot from a live/ambiguous owner; the slot is reclaimed after TTL only once owner death/PID reuse is demonstrated. A forked child must reinitialize the store. Boot changes clear stale monotonic state; same-boot config mismatch fails closed.

Verification: 20 ingress + 13 coordinator + 38 quorum + 51 mTLS gateway methods passed across four invocations (122 total). Python compilation and 14 exact source fingerprints passed. This is local reference evidence only. Scope is same-host/same-PID-namespace SQLite; no upstream source, pull request, CI or hosted service was changed/called. See `r35_process_bound_ingress_v4_5/RESULTS_v4.5.md`.
