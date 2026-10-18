# Lycheetah · Earned Trust · Cycle 004

**Research date:** 18 October 2026, Pacific/Auckland  
**Research status:** `LOCAL / SYNTHETIC / AUTHOR-DESIGNED / NOT DEPLOYED`  
**Theme:** A valid provider receipt is not automatically evidence of a correct external outcome.

## What changed

Cycle 003 proved bounded local SQLite commits and signed local provider receipts. Cycle 004 adds an outcome reconciliation control: a current, separately HMAC-authenticated observer claim, stored in a different lab SQLite database, must corroborate the provider's signed local receipt and exact action/token identity before returning `CONFIRMED`. Missing or stale evidence routes to `REVIEW`, disagreement to `CONFLICT`, and no recorded provider commit to `UNKNOWN`.

The observer's records are **supplied by a trusted test harness**. Neither separate files nor separate cryptographic keys establish real-world epistemic independence. The oracle cannot observe actual refunds. The system can still confirm an incorrect outcome when both sources are wrong.

## Run locally (no external dependencies)

Requires Python 3.10+ with standard-library SQLite.

```bash
cd earned_trust_cycle_004
python3 -m unittest -q test_independent_witness test_matched_baseline
python3 run_scenarios.py > reproduced_scenarios.json
```

Expected: **38 passing local tests**; ten scripted scenarios with two-record outcomes **2 CONFIRMED, 4 REVIEW, 3 CONFLICT, 1 UNKNOWN**. Eight cases are marked `CONFIRMED` by a receipt-only ablation. A matched conventional two-record baseline agrees with the proposed control in **10/10** scenarios. These figures are authored scripted case counts, **not** empirical safety rates or external performance measurements.

## Execute the real-Framework contract, later

The package `lycheetah` was **not locally installed** on 18 Oct 2026. The four tests in `test_framework_bridge_candidate.py` were attempted and failed at import (`ModuleNotFoundError`), so they provide **zero executed integration evidence**. To run them with the real package:

```bash
cd /path/to/Lycheetah-Framework
python3 -m pip install -e .
PYTHONPATH=/path/to/earned_trust_cycle_004:$PWD \
    python3 -m unittest -v test_framework_bridge_candidate
```

First rerun the 18 existing Cycle 002 import-based tests and investigate any API drift. The bridge's `human_approved=True` and `approver_id` remain **trusted fixture assertions, not authenticated human approvals**. The bridge invokes a local SQLite fake provider; it does not execute a payment or externally sourced readback.

## Files

- `independent_witness.py`: typed result and independent local observation verifier.
- `authenticated_provider.py`: **unchanged, byte-identical snapshot** of Cycle 003 reference implementation, SHA-256 `4e1e08f4470b9989f8546feac37fac3cac02097fa996f9ecbffa28f2edcc3256`.
- `conventional_baseline.py`: same-controls conventional comparator, not a weaker baseline.
- `test_independent_witness.py`: 30 local signed-provider/observer tests.
- `test_matched_baseline.py`: 8 matched-controls tests.
- `run_scenarios.py` + `scenario_results.json`: ten fixed scenarios; outcomes preserved.
- `framework_bridge_candidate.py` + `test_framework_bridge_candidate.py`: **UNEXECUTED** real-package integration candidate.
- `real_framework_not_executed.txt`: exact import blocker evidence.
- `RESEARCH_REPORT.md`, `CLAIMS.json`: falsifiers and interpretation.
- `SHA256SUMS.txt`: integrity digest of handoff files.

## Guardrail

Do not report this as an improved alignment detector, independently verified truth oracle, authenticated human-consent system, commercial release, external transaction safety result, or evidence that Lycheetah beats standard controls. No GitHub changes were made.
