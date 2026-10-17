# LAMAGUE Research Cycle 23 — Post-crash per-file observation evidence

**Status: experimental, not production safe.**

Run: `python -m unittest discover -s tests -v` and `PYTHONPATH=src python src/cycle23.py`.

This cycle preserves Cycle 22 as an untouched inherited ZIP, reuses the *actual namespaced publisher* and fault injection, then records individual **post-crash filesystem observations** using an HMAC-chained per-file record format. The observer's journal is checked against the original signed grant and anchored to a separate local witness checkpoint.

**Do not confuse post-crash observation with atomic per-commit witness attestation.** A trusted local observer and quiescent filesystem are assumed. See RESEARCH_CYCLE_23_MASTER.md for evidence boundaries.
