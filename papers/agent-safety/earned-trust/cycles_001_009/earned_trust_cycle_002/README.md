# LYCHEETAH — Earned Trust Cycle 002

**18 October 2026 (New Zealand)**  
**Status:** `LOCAL SYNTHETIC SQLITE EXPERIMENT` + `UNEXECUTED REAL-REPOSITORY CONTRACT SUITE`.  
**No live provider actions, remote transactions, GitHub writes, financial writes, or customer information.**

## What to run here

Requires Python 3.10+ with SQLite, no third-party dependencies.

```bash
cd earned_trust_cycle_002
python3 -m unittest -v test_transactional_provider test_binding_contract
python3 run_probe.py > fresh_results.json
python3 process_probe.py > fresh_process_results.json
```

Expected locally: **29 passing tests**; in `fresh_results.json`, 32 concurrent submissions of one exact intent produce **1 COMMITTED** and **31 IDEMPOTENT_REPLAY** responses against a single shared SQLite database. All experiments use invented customer/order identifiers. A separate multi-process probe ran four rounds of eight processes sharing one SQLite database per round; each round committed once and served seven replays.

## What to run *inside the actual Framework checkout*

This is a **prepared, not executed** suite. It imports the real classes. No mocks of the framework are substituted.

```bash
cd /path/to/Lycheetah-Framework
python3 -m pip install -e .
PYTHONPATH=. python3 /path/to/earned_trust_cycle_002/run_framework_contract.py
```

Expect 18 tests **if compatible with the repository revision**. At the time of this handoff, the repository package was not available locally. The suite's implementation was checked against GitHub source method signatures and Python bytecode compilation, **not executed against real Framework modules**. If an API differs, record the failure and patch the test or implementation explicitly; never mark a skip as evidence.

## Files

- `transactional_provider.py` — single-DB conditional effect simulation, exact matching and idempotency
- `binding_contract.py` — strict cross-boundary action-shape equality check
- `test_transactional_provider.py`, `test_binding_contract.py` — **executed** tests
- `run_probe.py`, `results.json` — reproducible representative scenarios and thread-concurrent outputs
- `process_probe.py`, `process_results.json` — separate-process SQLite concurrency probe
- `run_framework_contract.py` — **unexecuted** real-repository contract suite (18 cases)
- `real_contract_not_run.txt` — recorded missing-import state
- `RESEARCH_REPORT.md` — threat model, measured outcomes, inference limits and next iteration
- `claims.json` — bounded claims with falsifiers
- `SHA256SUMS.txt` — file hashes of this handoff

## Relationship to Cycle 001

Cycle 001 proved a narrow specification pattern in a deterministic single-threaded toy environment: finality rechecks do not make remote effects atomic. Cycle 002 substitutes a **real SQLite transaction** for the toy conditional commit, adds concurrent callers, lost-response recovery, and a strict action binding contract. Neither cycle has executed a real refund or measured genuine business outcomes.
