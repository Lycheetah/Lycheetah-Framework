# Forge VI — The Right of Return

Runnable offline Python research prototype testing revocation, in-flight effects, reconciliation, compensations, human overwrite conflicts, and irreversibility.

Quick start (Python 3.10+):

```bash
python -m unittest discover -s tests -v
python experiment.py
```

- `right_of_return.py` — simulated provider, SQLite controller, HMAC operator request, strict typed statuses, conventional baseline implementations.
- `tests/test_right_of_return.py` — 30 deterministic unit tests.
- `experiment.py` — 11 reproducible manually authored scenarios and four strong saga comparison cases.
- `results/` — JSON and CSV output from most recent run.
- `RESEARCH_PASS_06.md` — full interpretation and proposed falsifiers.
- `CLAIMS_AND_FAILURES.md` — conservative claim register.
- `THREAT_MODEL.md` — what is and isn't protected.
- `SHA256SUMS.txt` — corruption check only; no independently authenticated signature.

**Warning:** Do not attach live tools or customer data. Operator identity is simulated; provider records are not independent verification; reversible data edits are not universal rollback.
