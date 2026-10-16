# Observer Probe v0.3 — a test of the evaluator, not the agent

This is a tiny local evaluator-calibration task nested in the Closed-Loop Agent Lab. It implements one bounded Python helper and compares a weak three-case visible test suite with a more complete behavioral contract suite.

## Why this exists

A feedback controller can appear effective because the benchmark is easy to satisfy. Before using a postcondition observer to influence agent actions, validate that the check suite detects plausible wrong solutions while allowing structurally different correct solutions.

The microtask is deliberately conventional: zero-indexed exponential retry delay, finite nonnegative numeric delays, a hard cap, strict invalid-input handling, and behavior that remains bounded for huge retry attempts. It is only a test fixture, not a new Lycheetah runtime module or a recommended production library.

## Contents

- `retry_policy.py`: reference implementation of the explicit contract.
- `candidates.py`: two valid implementations (different structures) and six deliberately flawed candidates.
- `run_probe.py`: runs public checks and contract checks; emits JSON and Markdown results.
- `test_probe.py`: verifies the probe discriminates the planted variants without rejecting the known-valid alternative.

## Run

```bash
python run_probe.py
python -m unittest -v
```

Python 3.10+; standard library only. `python run_probe.py` regenerates `probe_results.json` and `PROBE_RESULTS.md`.

## What counts as evidence

A successful run demonstrates only that this locally authored suite distinguishes these known variants. The reference implementation, defects, and labels were all authored for this fixture. No LLM generated a patch and no live agent was evaluated. A contract test suite is not truly independent simply because it lives in another file.
