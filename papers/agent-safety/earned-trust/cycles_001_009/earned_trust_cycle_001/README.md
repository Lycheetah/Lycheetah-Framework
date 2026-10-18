# EARNED TRUST — Research Cycle 001

**Date:** 2026-10-18 · **Status:** Synthetic research; not a production system; no live effects.

Start with [RESEARCH_REPORT.md](RESEARCH_REPORT.md). This package studies the difference between a valid decision at admission, a fresh decision immediately before dispatch, and an atomic check by the external provider when a consequential effect actually happens. It is **not** a checkout of `Lycheetah-Framework`, nor is it a test of the real Framework code.

## Reproduce

Requires Python 3.10+ only; no third-party packages.

```sh
python3 -m unittest -v
python3 earned_trust_probe.py > results-new.json
```

Expected: 20 unittest methods pass; 20 cases × 4 strategies = 80 synthetic observations. See `results.json` for the captured initial run and `test_output.txt` for its actual test transcript. A passing test doesn't certify a safety mechanism.

## Package

- `earned_trust_probe.py`: deterministic scenario generator and four-arm toy enforcement comparison
- `test_earned_trust_probe.py`: unit tests, including known-bad negative controls
- `RESEARCH_REPORT.md`: lineage, prior art, methods, interpretation, blockers, next experiments
- `claims.json`: structured claims and falsifiers
- `results.json`: original execution rows and hash-linked trace (not externally anchored)
- `test_output.txt`: actual unittest run output
- `SHA256SUMS.txt`: reproducible artifact file hashes

No API keys, third-party services, live GitHub effects, or customer records required.
