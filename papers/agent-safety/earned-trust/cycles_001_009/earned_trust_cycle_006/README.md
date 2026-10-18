# Earned Trust Cycle 006 — Who Watches the Witnesses?

**Date:** 18 October 2026, NZ · **Status:** `LOCAL_SYNTHETIC_ENGINEERING_TESTED / NOT DEPLOYED`

This continuation addresses Cycle 005's main ungoverned trust assertion: two signed reports count as independent only when a trusted source graph says they are. Cycle 006 experiments with a *revisioned, challenged, dual-reviewed* source graph. It does **not** verify that the graph's assertions are true.

## Reproduce (Python 3.10+, standard library)

```bash
cd earned_trust_cycle_006
python3 -m unittest -v test_governed_registry test_baseline_comparison
python3 run_scenarios.py > regenerated_scenarios.json
python3 recheck_history.py > rechecked_tests.json  # requires sibling cycles 001–005
sha256sum -c SHA256SUMS.txt
```

Observed in this environment: **59/59** local Cycle 006 unit tests. The authored 20-case corpus produced naive signed quorum **13 CONFIRMED / 6 REVIEW / 1 CONFLICT**, governed registry **6 CONFIRMED / 13 REVIEW / 1 CONFLICT**, and a matched conventional policy with **identical 20/20 decisions** to the governed path. Counts are synthetic mechanism observations, not field accuracy or reduced harms. A separate rerun recorded **238 passed test method runs** across Cycles 001–006, all locally authored.

## Delivered components

| File | Role |
|---|---|
| `governed_registry.py` | Reference authority roster, two-organization review, signed challenge, immutable event copy, hash-linked revisions, review/dispute state, witness-registry binding, checkpointed decisions |
| `provenance_gate.py` | Unchanged Cycle 005 reference module included for reproducibility |
| `conventional_governance_baseline.py` | Equal-control policy using a separate pairwise lineage decision but shared trust validation |
| `test_governed_registry.py` | 51 authored contract/adversarial tests, including 12 concurrent proposal attempts and admission-before-challenge counterexample |
| `test_baseline_comparison.py` | 8 explicit corpus comparisons and negative controls |
| `run_scenarios.py`, `scenario_results.json` | Fixed 20-case synthetic comparison and outcomes |
| `historical_recheck.json`, `recheck_history.py` | Cross-cycle test rerun results and exact commands |
| `framework_bridge_attempt.txt` | Real-framework integration import failure preserved, **not a pass** |
| `CLAIMS.json` | Bounded claims with counterexamples and falsifiers |
| `RESEARCH_REPORT.md`, `INTEGRATION_HANDOFF.md` | Interpretation, threats, next engineering gate |
| `EARLY_TEST_EXPECTATION_FAILURE.txt` | Preserved first-run test assertion mismatch (wrong expected rejection reason), subsequently corrected and rerun green |
| `SHA256SUMS.txt` | Checksums over all exported Cycle 006 files other than self |

## Scope limits that matter

- The source graph, identities, organization boundaries, and HMAC keys are **lab-controlled fixtures**. Reviewer separation is a configured declaration, not an independently administered trust domain.
- The Python object itself holds all signing keys through a convenience signing method; this is **not** operational key isolation or a deployed authorization service.
- A single authenticated auditor can halt affected paths: a legitimate conservative pause and also a denial-of-service risk.
- A verified HMAC says who knew a shared secret, not that a claim was true, nor which individual approved it.
- A `CONFIRMED` decision is only current *declared-path agreement*. It does not establish human authorization, provider effect safety, real-world source independence or truthful evidence.
- Atomicity is limited to one Python process's lock and in-memory event list; no durable multi-process log, remote provider transaction, public-key certification, secure checkpoint store or independent adversarial evaluation.
- False but mutually corroborated source claims still produce `CONFIRMED`. Two reviewer organizations may agree on a wrong dependency graph.
- The separate conventional implementation intentionally implements the same controls; its identical decisions mean **no Lycheetah-specific gain demonstrated**.
- A signer with its key can rewrap a **pre-change observation** at a new governance head without obtaining new real-world evidence. Registry-binding freshness is not observation freshness.
- A past confirmation **cannot be revoked** once a caller has acted. A current gate recheck may say `REVIEW`; connecting this to the actual dispatch boundary is still necessary.
- The actual `lycheetah.assurance` runtime was **not imported or executed**; repeated test invocation raised `ModuleNotFoundError: No module named 'lycheetah'`.

No repository writes, live providers, real customers, refunds or network side effects.
