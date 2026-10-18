# Lycheetah — Earned Trust / Cycle 005

**Research target:** The Independent Witness Problem — does agreement arise from distinct authenticated evidence pathways, or from copies of the same source?

**Evidence status:** `LOCAL_SYNTHETIC_ENGINEERING_TESTED`, **NOT DEPLOYED**, no external validation or unique comparative advantage. 18 October 2026 NZ.

## Fast reproduction

From this folder, Python 3.10+ standard library only:

```bash
python3 -m unittest -v test_provenance_gate test_baseline_consistency
python3 run_scenarios.py > fresh_scenarios.json
python3 metamorphic_probe.py > fresh_metamorphic.json
```

Observed here: **42/42** local tests; **16 fixed scripted scenarios**. Counts: naive signer quorum 8 CONFIRMED; provenance-aware gate 4 CONFIRMED, 11 REVIEW, 1 CONFLICT; matched conventional implementation 0 decision disagreements. A separate seeded probe ran 1,000 synthetic cases without a baseline disagreement, order-dependence finding, substituted-action confirmation, or single-root confirmation. These are code-consistency properties, not independent validation. Both the provenance gate and matched control CONFIRM a deliberately false common-world assertion supplied by different declared source roots.

The 16 scenarios are author-designed, not sampled operational requests. No relative safety, prediction, accuracy, security certification, or novelty claim is made.

## What the gate actually does

- HMAC-verifies separate witness statements against a **preconfigured, trusted registry** of signers.
- Binds each assertion to one effect ID, action digest, token digest, observation timestamp and revision.
- Requires a trusted caller to supply the **current witness revision** for every statement; missing or mismatched revisions trigger REVIEW.
- Traverses transitive source dependencies and controlling organizations and seeks a subset with disjoint ultimate roots **and** disjoint controllers (at least two by default).
- Returns `CONFIRMED` only for agreeing, current, authenticated statements with distinct declared paths; returns `CONFLICT` for authenticated negative claims; routes uncertainty, invalid authentication, stale readback or insufficient path independence to `REVIEW`.

`CONFIRMED` means **declared-path agreement**, not truth, harmlessness, third-party independence, or a real provider effect.

## Files

| File | Role |
|---|---|
| `provenance_gate.py` | Candidate reference implementation, source DAG + HMAC + quorum gate |
| `conventional_baseline.py` | Equal-controls decision algorithm using shared input verifier and registry |
| `test_provenance_gate.py` | 38 new structural/adversarial tests |
| `test_baseline_consistency.py` | 4 comparison checks |
| `run_scenarios.py`, `scenarios.json` | 16 cases and raw local decisions |
| `metamorphic_probe.py`, `metamorphic_results.json` | 1,000 seeded synthetic permutations and mutation checks |
| `real_framework_bridge_candidate.py` | Prepared actual `lycheetah.assurance` integration, NOT executed |
| `test_real_framework_bridge_candidate.py` | 4 tests blocked on missing real `lycheetah` package |
| `actual_framework_execution.txt` | Exact `ModuleNotFoundError` evidence; not a successful run |
| `historical_recheck.txt` | Prior 4 cycles' unit tests rerun in this container |
| `CLAIMS.json` | Falsifiable bounded claims |
| `RESEARCH_REPORT.md` | Findings, controls, limitations and future design |
| `INTEGRATION_HANDOFF.md` | Next verified engineering step |
| `SHA256SUMS.txt` | Checksums, excluding self |

## Prior cycle assets

Previous cycles remain unmodified beside this folder as `earned_trust_cycle_001` through `earned_trust_cycle_004`. A combined archive is available, with full hierarchy. For historical details refer to the master handoff, not only short summaries.

## NO production claims

HMAC identities are local fixture secrets. Source provenance and controller relationships are asserted by the researcher, not independently audited; a dishonest registry can make a common source appear independent. `provider_receipt_valid` is a trusted **input flag** into this narrow module, not a real provider verification performed by this module. Neither current revisions nor source independence are autonomously discovered. Tests intentionally confirm a false assertion when both supposedly independent observers say TRUE. No live orders, business data, real transfers, remote provider writes, or GitHub writes.
