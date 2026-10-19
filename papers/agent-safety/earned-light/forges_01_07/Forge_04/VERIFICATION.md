# Verification record (18 October 2026, NZDT)

- Existing Forge III suite, extracted from original Forges I–III consolidated ZIP: `python -m pytest -q tests` → **76 passed**.
- Forge IV suite: `python -m pytest -q test_horizon.py` → **14 passed**.
- Forge IV examples: `python scenarios.py` → **10 authored scenarios**, of which **8** return multiple non-dominated alternatives by deliberate design.
- Forge IV attack demonstrations: `python counterexamples.py` → **1 actual outcome mislabeled as 20; 0 real independently executable outcomes mislabeled as 1; thirty outcomes with review burden unmodeled**.
- Neither suite exercises live providers, human identity, real consent, longitudinal competence or independent external red teams.

The outcome IDs and evidence are asserted in fixture data; do not treat them as validated real-world truths.
