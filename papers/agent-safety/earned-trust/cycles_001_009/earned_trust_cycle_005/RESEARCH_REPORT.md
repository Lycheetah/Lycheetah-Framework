# The Independent Witness Problem — Research Report

**Date:** 2026-10-18 NZ | **Track:** EARNED TRUST | **Cycle:** 005
**Evidence level:** Local synthetic tests only. **Authoring seat:** Lycheetah + AI coding collaborator.

## Question

Can an agent-action receipt verify that its supporting observations have *distinct provenance* rather than simply distinct signatures? What fails even after enforcing distinct provenance?

## Origin in Lycheetah

The pinned public repo `Lycheetah/Lycheetah-Framework` at `d4a65ff64efa0a512c5c07ca64f6ec76242dd775` implements `FinalityGate` (admission and evidence recheck), `AssuranceRuntime` (policy evaluation + receipt) and `PersistentActionGuard` (single-use dispatch and local journal). The live framework is marked `[SCAFFOLD]`. The actual git repo was not installable here, and the full integration suite remains unexecuted.

Cycle 004 supplied a provider HMAC receipt plus a separately keyed, lab-authored observer. It correctly reported disagreement, but two signed statements could both rely on the same source. Cycle 005 introduces a **declarative trusted registry** of witnesses, ultimate source nodes, intermediate copies and control domains. The graph is inspected before counting agreeing witnesses.

## Control invariant

For every accepted witness, require:

1. A registered signer and valid HMAC over exact action, token, effect and observation metadata.
2. Current, version-consistent revision supplied by a trusted readback caller.
3. A valid acyclic, predeclared provenance path from signer to ultimate source root(s).
4. At least `k` mutually disjoint sets of root IDs **and controller IDs**, among agreeing TRUE/COMMITTED observations.
5. A separately verified provider receipt *supplied as a trusted gate input*; this gate is not itself the provider verifier.

If any check fails, do not claim independent confirmation. A signed negative observation is reported as CONFLICT, not silently dropped or promoted to an automatic destructive block.

Conservative decisions: `CONFIRMED` = authenticated agreement across declared disjoint paths; `REVIEW` = insufficient/untrusted/unknown; `CONFLICT` = authenticated negative or contrary report. It is *not* a moral correctness judgment.

## Executed results

Local unit tests: `python -m unittest -v test_provenance_gate test_baseline_consistency` → **42 tests passed**. The 16 author-designed scenarios yielded:

| Control | CONFIRMED | REVIEW | CONFLICT | Other |
|---|---:|---:|---:|---:|
| Naive count of signed witnesses (ablation, deliberately weaker) | 8 | 7 | 1 | 0 |
| Root/controller-aware gate | 4 | 11 | 1 | 0 |
| Matched conventional rules | 4 | 11 | 1 | 0 |

The naive control counts two separately signed copies of one CRM record as two confirmations; the lineage check routes those to REVIEW. The matched conventional control uses the same trusted registry and input verifier with a separately implemented combination search; it agreed on all 16 cases. **No demonstrated Lycheetah-specific advantage.**

### Seeded mutation/permutation check

`metamorphic_probe.py` evaluated 1,000 seeded synthetic signer subsets: zero matched-baseline mismatches, zero order-dependent decisions, zero accepted substituted action hashes, and zero confirmed cases when only one declared ultimate root was present. There were 723 confirmations among these *author-constructed* samples. These cases are not field observations, do not test dishonest registries, and cannot establish robustness against an independent adversary.

### Four decisive examples

- `same-origin-two-signatures`: naive CONFIRMED → provenance REVIEW because both signers depend on `original-crm`.
- `same-controller-different-originals`: naive CONFIRMED → provenance REVIEW because controller overlap survives disjoint root IDs.
- `three-signers-two-origins`: provenance CONFIRMED; the algorithm identifies two independent declared lineages despite a duplicated source.
- `two-sources-agree-on-false-evidence`: provenance CONFIRMED even though the manually supplied independent fixture truth label is FALSE. Independent signing does not prove veracity.

### Negative control — dishonest registry

`test_registry_misclassification_can_fake_independence` registers two *actually related* experimental sources as if they were distinct origins. The resulting cryptographic attestations satisfy the graph and produce CONFIRMED. **Registry provenance must be independently governed to support real independence claims.**

## Prior-cycle recheck in the same environment

- Cycle 001: 20/20 tests passed.
- Cycle 002: 29/29 passed (some resource warnings were emitted).
- Cycle 003: 50/50 passed.
- Cycle 004: 38/38 passed (some resource warnings were emitted).

Together with Cycle 005's 42 tests: **179 test method runs**, not 179 independent real-world demonstrations. Historical tests are locally authored and some exercise overlapping code paths. Verify archives / checksums for exact versions.

## Real framework integration status

The 4 prepared new real-framework bridge tests were actually *attempted*, each producing `ModuleNotFoundError: No module named 'lycheetah'`. No test body reached the Framework methods. We confirmed pinned GitHub source paths and signatures through the GitHub connector, but could not perform `git clone` in the container (DNS resolution fails). **Zero successful real-framework integration tests.** This is a blocker, not an accidental skip.

## Why this is not an independence proof

1. **Source graph is an operator assertion.** The framework does not audit upstream information flows, ownership or out-of-band communication. Colluding operators can misrepresent roots.
2. **Current revision readback is another trusted input.** Our local map is not a network lookup to authoritative registry services. A malicious caller can assert old revision is still current.
3. **HMAC keys are fixture secrets.** HMAC authenticates to shared secret holders but does not provide public attribution or hardware isolation. Key compromise permits signed falsehoods.
4. **Provider receipt validity is supplied as a flag.** This module does not directly verify actual Lycheetah receipts. The bridge candidate uses the Cycle 003 local provider for that check, pending execution.
5. **No evidence of correctness.** Independent evidence pathways can jointly report a false fact, and no ground-truth oracle is available in a real business deployment.
6. **Disjoint roots are a conservative heuristic.** Two independent systems can share a parent fact and still corroborate some claims; conversely, formally disjoint roots may have correlated error processes. Neither false positives nor false negatives were calibrated on externally authored data.
7. **Availability and denial-of-service.** Conservative routing to REVIEW can impose costly human review or be triggered by a malicious contradictory witness. Review and dispute-resolution policies are not implemented.
8. **Complexity / input bounds.** The selector is for <=32 witnesses in a small synthetic reference; no throughput benchmark, fuzzing campaign, independent security review, service tests, or production hardware threat model.

## Relation to core work

- **AURA**: policy disposition and escalation, not evidence oracle.
- **CASCADE**: expose contradictions without silently merging them into agreement; no CASCADE code imported in this experiment.
- **LAMAGUE**: candidate compact packet for provenance, exact record recovery; no LAMAGUE compression used here.
- **TIM**: observation freshness must be defined at finality and be backed by authoritative timestamps, not loose text; no separate TIM verification performed.
- **Action Guard / FinalityGate**: exact action authorization and evidence recheck should be integrated *before* any claim of full effect accountability.

## The next falsifiable hypothesis

H005-6: A provenance-aware triage mechanism can reduce *undetected common-source duplicates* on an externally designed corpus **without unacceptable false-review rates**, compared with a conventional dependency-aware rule engine and a simple signature quorum. Define independence labels with third-party operators, freeze rules first, then measure missed shared dependencies, unnecessary escalations, case coverage and auditability. The current results do **not** establish that hypothesis.

## Publication discipline

Archive local; no GitHub writes. Keep original failure records, commit SHA, test output, signed local fixtures and limitations. Promotion beyond `SCAFFOLD` requires real repo execution, trusted authenticated outside-model approvals, independently governed witness registry, current readback, provider effect verification and external attack review.
