# Forge IV — Sovereignty Horizon

A **read-only exploratory analysis**, extending the philosophical and empirical program of Earned Light while leaving Forges I–III security prototypes unchanged.

## Run
```bash
python scenarios.py
python counterexamples.py
python -m pytest -q test_horizon.py
```
Python 3.10+ and pytest required. The example assessor itself has no third-party dependencies.

## Files
- `RESEARCH_PASS_04.md`: theoretical reach, existing literature, precise limitations, human evaluation design.
- `sovereignty_horizon.py`: small Pareto-frontier/read-only toy instrument.
- `scenarios.py` + `results.json`: ten designed cases and their outputs.
- `counterexamples.py` + `counterexample_results.json`: spoofing attacks the instrument **does not detect**.
- `test_horizon.py`: fourteen checks, including two intentionally demonstrating failures.
- `CLAIMS_AND_FAILURES.md`: epistemic limits and next research.
- `SHA256SUMS.txt`: contents for reproducible integrity comparison.

## Research discipline
The tool computes hypothetical *outcome accessibility under declared assumptions*. It does not measure free will, show a user a trustworthy rendered interface, or execute agent tasks. A larger frontier is not inherently ethically superior; only people can define meaningful goals and commitments for themselves.
