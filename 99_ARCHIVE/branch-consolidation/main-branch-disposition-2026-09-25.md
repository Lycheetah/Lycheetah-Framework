# `main` Branch Disposition — 2026-09-25

At the inspected snapshot, `main` pointed to
`fac4523fac3b509889b22ec36535ee3ab02c04c0` and had five commits in an independent
history with no merge base to the protected `master` branch. Its tree contained 20
paths absent from `master`, including standalone persona validation, provenance
checking, AURA benchmarking and sandboxing, a drift visualizer, and two Mystery
School mobile-source maps.

The tools were not copied into `master` based on path-level overlap guesses. `master`
does contain archived execution reports under `99_ARCHIVE/CODEX_CHANGES/`, while the
independent source tree is preserved at the annotated local tag
`pre-consolidation-main-2026-09-25`. The complete list of main-only paths and the
other branch comparisons are in [`2026-09-25-branch-inventory.md`](2026-09-25-branch-inventory.md).

Retrieve any file from the preserved tip with:

```bash
git show pre-consolidation-main-2026-09-25:03_aura_benchmark/benchmark_runner.py
```

This disposition records local preservation only. It does not delete the GitHub
branch, alter the remote, or claim that the branch count has changed.
