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
| [swarm-hardening.json](swarm-hardening.json) | Later bounded swarm: stable snapshots, policy/receipt repair and retained handoff workflow; 329 focused cases |
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

A later bounded swarm completed its three assigned reviews and implemented the
retained handoff workflow and snapshot/receipt repairs. Its 329-case focused run
contains 90 new cases; see `swarm-hardening.json`. This newer batch does not turn
the earlier folder census into completed semantic review.

## Second-reviewer note (2026-10-22, RV36)

The receipts above were re-checked by a second AI reviewer (Sol, Claude Opus 5.5). The JSON receipts
are left byte-for-byte as issued. This is AI review of AI review. It is not independent scientific
validation.

- **Reproduced exactly.** In a detached baseline worktree, `math_probes.py` gave 18 of 18 probes,
  with every probe's values, the 36 source receipts and the script hash identical to
  `math-probes.json`. `claim-evidence-audit.json` was identical except for its timestamp. A mutated
  pinned source was refused, and so was the current HEAD.
- **Recomputed and holding.**
  - All 32 notices: the before-hash equals the baseline blob, the after-hash equals HEAD, and no
    original line was deleted.
  - `coverage.json` counts 4822 files, 50 directories and 35 root files.
  - All 606 folders of the snapshot tree.
  - 23 missing references and 16 claims whose pointers are all missing, with all 71 statements and
    statuses unchanged.
  - The `oct19-preservation.json` hashes at HEAD.
- **Not reproducible as labelled.** `verification.json` reports a maintained suite of 999 collected,
  997 passed. Collection at its `baseline_commit` gives 981. At the commit that added the receipt
  (`cf6ff23`) it gives 1058. The 999 was measured on a working tree that no commit records.
- **Hardcoded control.** `resolver_controls` in the claims audit is written as literal `true`. The
  sentinel check asserts that a file is absent; it never passes that file through the resolver.
- **No generator.** Only `math-probes.json` and `claim-evidence-audit.json` have a committed producer.
  The booleans in the other receipts (`notice_hashes_match`, `all_current_hashes_match`,
  `missing_folder_negative_control_detected`) are written values. Most of them were recomputed above
  and hold.
- **Describe HEAD, not later working trees.** `oct19-preservation.json` and the `source_sha256` block
  in `swarm-hardening.json` describe HEAD. The uncommitted 2026-10-22 review has since changed 2
  intake files and 5 swarm-pinned sources, and each change is disclosed in its own batch ledger.

Full ledger: `FOR-REVIEW/2026-10-22_OPUS_REVIEW/BATCH35_FINDINGS_AND_LEDGER.md`.
