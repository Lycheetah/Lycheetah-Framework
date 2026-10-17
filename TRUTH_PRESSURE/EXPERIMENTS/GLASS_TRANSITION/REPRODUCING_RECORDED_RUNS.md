# Recorded source revisions and integration

Author: Mackenzie Conor James Clark / Lycheetah Framework.
Integration review: Caelorynth / Codex, 17 October 2026.

## Reproduce the recorded data

The JSON/CSV and figures are historical experiment outputs. They are preserved
byte for byte. The following revisions are retained in this repository's history:

| Recorded experiment | Exact source revision | Rows |
|---|---|---:|
| Fixed service and measured-work snapshot/commit | `87daa86173a507232afc8c4c87d9a500a4b809c5` | 864 each |
| Aetheron's dependency-policy extension | `60a77da683f07534cabd91b5c9133ab2b7de3552` | 768 |

Both used `cascade_engine.py` from base
`f8e30c99aef4797aa363b3d077b1f029d0ab16b7`, SHA-256
`25c9f81d29c4d423914ae120b9b1fca46d075b7dad07bf7d0d904b5bcfeaa92c`.
The integrated engine now verifies postconditions, including additional
contradiction comparisons. Its isolated 12-concept calibration is 182 operations
rather than the recorded 25. Identical experiment code on the new engine is a new
measurement, not a reproduction of the old timing calibration.

From a clone with the project dependencies installed:

```bash
git worktree add --detach /tmp/lycheetah-glass-recorded 87daa86173a507232afc8c4c87d9a500a4b809c5
cd /tmp/lycheetah-glass-recorded
# Follow README.md and LOAD_AWARE_RESULTS.md in this directory:
# TRUTH_PRESSURE/EXPERIMENTS/GLASS_TRANSITION/
```

For the extension, start from the original source revision:

```bash
git worktree add --detach /tmp/lycheetah-topology-recorded 60a77da683f07534cabd91b5c9133ab2b7de3552
cd /tmp/lycheetah-topology-recorded
python3 12_IMPLEMENTATIONS/core/topological_cascade_glass.py --output /tmp/topological-reproduction.json
```

The original extension's `theorem`/`b1` output keys are historical labels, not proof
claims. Read [the reviewed interpretation](TOPOLOGICAL_RESULTS.md). The current
source adds this limitation to generated output without changing the archived run.

## Artifact hashes

`source_sha256` inside each original JSON identifies the sources used at run time.
The artifact manifests distinguish current documentation from a source pinned to a
historical `revision`. Resolve a pinned entry with `git show REVISION:PATH`; do not
compare its old engine hash to the current engine and silently rewrite the hash.
The original protocols, data, figures and A1/A2 implementation sources are retained.

## Integration checks

The first combined check ran 228 tests across 13 selected files: 227 passed and
one topology assertion still expected the old engine's literal 25-operation cost.
That assertion now compares against the independent zero-hop calibration and
requires exactly two added operations for each of the star hub's 11 children.
This preserves the dependency-work check while accounting for the new diagnostics.

The C successor independently passed all 61 selected harness, consensus,
compaction and assurance-runtime checks, including the empty-grant and read-only
scope counterexamples. The B callback threshold and trace findings are addressed
in the integrated successor.

Final focused rerun: **228 passed in 29.91 seconds** across those 13 files.
Ruff checked all **23 changed Python files** with no findings. The loop-audit
self-test caught **7/7 deliberately planted mutations**. These checks include
cut-actuator, false-work, threshold-mutation, trace-isolation, authority-scope and
replay cases. No full-repository CI or real-world validation is implied.
