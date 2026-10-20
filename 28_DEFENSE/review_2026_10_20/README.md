# Reproduce the 20 October 2026 review

**Status: [SCAFFOLD] Project review artifacts, not independent peer review.**
Framework creator: Mackenzie Conor James Clark. Review: Caelorynth / Codex.

Read the [substantive review](../FULL_FRAMEWORK_REVIEW_2026-10-20.md) first.
`math_probes.py` reproduces 18 counterexamples or proof-gap observations against
36 exact source files at the reviewed baseline. Its three assertion controls
include deliberately false expectations. A reproduced observation is not a
passing author claim.

The mathematical receipt and baseline claims audit describe the state before
source-location repairs and review notices. To reproduce that historical state,
use a detached baseline
checkout; the script deliberately refuses changed source bytes or another HEAD:

```sh
git worktree add --detach /tmp/lycheetah-review-baseline 6ba483af3f125ec725eb4e0f44074d0887183255
python3 -B 28_DEFENSE/review_2026_10_20/math_probes.py \
  --repo /tmp/lycheetah-review-baseline \
  --output-dir /tmp/lycheetah-review-results
```

Run from the current Framework checkout with Python 3.10+ and NumPy installed.
Choose unused temporary paths if either example path already exists. The source
checkout is read-only during the probes; JSON outputs go to the named output
directory. No server, model provider, paid API or broad test suite is started.

| Artifact | Meaning |
|---|---|
| [math-probes.json](math-probes.json) | Values, scope, controls and source hashes for all 18 observations |
| [claim-evidence-audit.json](claim-evidence-audit.json) | Baseline 71 claims, 107 literal pointers, 37 missing references |
| [evidence-path-repairs.json](evidence-path-repairs.json) | Fourteen source-location repairs; 23 references remain missing |
| [claim-assessments.json](claim-assessments.json) | Explicit reviewer assessment of all 71 rows, separate from author statuses |
| [source-review-notices.json](source-review-notices.json) | Dated notices, with source-body preservation receipts |
| [coverage.json](coverage.json) | All 50 areas, with explicit inspection and execution limits |
| [folder-coverage.json](folder-coverage.json) | All 606 folders in the deeper-pass snapshot; source reading, metadata and unread content are distinct |
| [deeper-reproductions.json](deeper-reproductions.json) | Primary reproduction of interrupted-review leads, including frozen consent, duplicate policy groups and mixed review cases |
| [verification.json](verification.json) | Executed check counts, artifact consistency and unresolved gates |
| [chorus-probe.json](chorus-probe.json) | Empty-agent and empty-audit cases that expose misleading health reports |
| [oct19-preservation.json](oct19-preservation.json) | Current hashes of all 225 imported files; manual coverage beyond the existing automatic gate |
| [lint-baseline-comparison.json](lint-baseline-comparison.json) | All six files with lint findings match the reviewed baseline |

The baseline claims audit measures pointer existence, not mathematical support.
The original author statuses remain visible; the review does not silently turn
its own judgments into author-issued retractions.

The 21 October extension includes 64 distinct new boundary cases across focused
runs. The 167-case implementation/sheaf/gateway run and 92-case compaction/harness
run overlap; do not add them. The earlier 999-case maintained collection was not
rerun. Three high-reasoning reviewers were interrupted by a service usage limit,
so the deeper source review remains incomplete even though every folder is listed.
