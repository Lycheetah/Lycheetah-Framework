# Hybrid Gateway v0.7 — continuation handoff

**DO NOT RESTART.** This archive includes v0.2–v0.6 lineage, unchanged v0.6 atomic SQLite core, new v0.7 temporal audit and pins, tests, demos and a hash manifest.

## What is runnable now

```bash
python -m unittest discover -s tests -q
python demo_atomic.py
python demo_temporal_audit.py
```

At packaging time 138 tests pass; 120 were inherited, 18 added. The temporal fixture's naive latest-known baseline matched 2 of 4 ledger outcomes. Under two authored weight profiles, one scenario changed **test-double** CASCADE diagnostics without changing the ledger's disposition. Don't mistake the weak baseline or test double for an independent comparator.

## Canonical CASCADE run — immediate priority

The original `cascade_engine.py` was inspected via linked GitHub (Git blob SHA-1 `bf90a47ab17da11c0266d078fc4d74a5d95c9235`). The trusted upstream checkout was **not downloaded/executed** in this environment. On a machine with the repo available:

```bash
git clone https://github.com/Lycheetah/Lycheetah-Framework.git
cd Lycheetah-Framework
# verify file pin as documented; if upstream changes, DO NOT silently bypass the pin
python -m pip install numpy
cd /path/to/unzipped/lycheetah_hybrid_architecture_v0_7
python demo_cascade_canonical.py --framework-root /path/to/Lycheetah-Framework
```

If the engine file changes upstream, record the new commit and file SHA, audit the diff, *then* intentionally update the pin and rerun tests. Never silently accept the moving `master` head. Pinning a file alone doesn't freeze transitive dependencies, so record environment versions.

## Next substantive science

- Freeze a 100+-document temporal dataset sourced outside this project, with 2 annotators for claim/field/scope/effective/knowledge-time and dispute adjudication; record annotation and review minutes.
- Compare raw model, quote-only gate, contract gate, coverage gate and state-of-the-art version-aware retrieval under identical source, prompting and human review budgets. Keep gold separate from model prompts.
- Run canonical CASCADE in read-only mode across conflict and withdrawal cases, publish both its output and disagreement with the ledger, and perform weight-sensitivity/ablation analysis with independently calibrated inputs.
- Never promote CASCADE output or a heuristic score to permission for durable writes. Atomic commit must stay under trusted reviewer control.
- Bring reviewer identity proof, external anchored head, backup/recovery and privacy assessment to a separate production-hardening track.

## Current failure boundaries

No actual neural run, canonical CASCADE execution, unbiased externally annotated gold, production identity assurance, hostile-code containment, or deployed customer result. Keep these statements near any demonstration metric.

**Branch remains proposed**: `research/hybrid-intelligence-architecture`. No branch created and no push executed.
