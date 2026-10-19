# Earned Light and Sovereign Will — integration review

**Date:** 19 October 2026.  
**Framework creator:** Mackenzie Conor James Clark.  
**Integration and local reproduction:** Caelorynth, an AI coding assistant.  
**Evidence:** Self-authored local research fixtures, philosophical proposals and fiction.

## What was imported

Two supplied handoffs contain 225 files (2,180,704 bytes before integration edits):

- Earned Light Forges I–VII, the expanded *Last Lighthouse of Eternity* and its earlier short edition: 93 files.
- Sovereign Will charters I–VIII, Sovereign Choice Forges II–VIII, seven original ZIP archives and *The Ninth Road Beneath the Sleeping Stars*: 132 files.

The [source manifest](RESEARCH_INTAKE_2026-10-19_SOURCE_MANIFEST.json) records all
225 relative source paths, destinations, import/current hashes and adaptation
flags. The original two input directories remain untouched. Two imported entry
guides were adapted for working links and reproduction; the manifest identifies
them. Forge code, tests, historic results, charters, stories and seven source
ZIPs retain their supplied bytes. Original notes under each research home's
`intake/` preserve pre-publication wording and original placement suggestions.

The supplied checksum lists checked 86 Earned Light files and 131 Sovereign Will
files. The intake independently hashed all 225. The seven original ZIPs and
their nested lineage archives passed 22 recursive CRC/path-safety checks.
Neither checksums nor packaging integrity validate research claims.

The whole pending diff reports 144 whitespace warnings across seven unchanged
imported files, mainly CSV carriage returns plus supplied code/HTML whitespace.
Those bytes are retained for archival integrity. Integration-authored changes
are checked separately; the whole diff is not described as whitespace-clean.

## Checks actually executed

| Research suite | Passing test executions |
|---|---:|
| Earned Light II | 28 |
| Earned Light III | 76 |
| Earned Light IV | 14 |
| Earned Light V | 28 |
| Earned Light VI | 30 |
| Earned Light VII | 31 |
| **Earned Light total** | **207** |
| Sovereign Choice II | 28 |
| Sovereign Choice III | 37 |
| Sovereign Choice IV–VIII, preserved original VIII replay | 142 |
| **Sovereign Choice total** | **207** |

Counts are executions, with overlapping historical coverage, rather than 414
independent experiments or distinct security properties. No missing-dependency
skips are counted as passes. Python 3.12, pytest and cryptography were available;
Node ran the Forge VIII JavaScript parity check against 16 Python fixture
outcomes. The archive's fixture, trajectory and supplied manifest comparisons
also passed.

The original 142-test replay covers IV–VIII. The supplied validation summary's
description of that count as covering II–VIII is too broad; this integration
ran II and III separately. The original summary is preserved as history.

Earned Light VII initially encountered seven sandbox socket errors. A permitted
rerun outside that restriction passed all 31 methods, including localhost
provider crash, restart, replay, irreversible notification and unresolved-effect
cases. This is a local synthetic provider, not a real external service.

Two controls deliberately disabled provider deduplication and exact-action
binding in disposable copies. Each corresponding one-test check failed as
expected. The preserved sources were not mutated. Existing counterexamples and
neutral results remain visible; a passing test may intentionally confirm a
limitation rather than prove its absence.

Reproduce from each research home using `python3 verify.py`:
[Earned Light](../papers/agent-safety/earned-light/README.md) ·
[Sovereign Choice](../papers/agent-safety/sovereign-choice-research/README.md).
The integration commands use temporary copies so archived results stay intact.
The extracted Sovereign Choice tree intentionally omits nested archive copies;
its historical verification scripts require the original source ZIP. The new
entry command uses that ZIP and adds the two earlier suites.

## Reading and scientific boundaries

The [Sovereign Will charters](../35_ABSTRACT_AND_GENERATIVE/SOVEREIGN_WILL/README.md)
remain philosophical proposals under the Abstract and Generative register.
Three original narrative files are registered in the
[existing collection](../LYCHEETAH_MYTHOS/SCRIPTURES_AND_STORIES/README.md).
The expanded Lighthouse and Ninth Road are complete readings; the earlier
Lighthouse remains context. Collection does not approve epic canon. Browser,
Markdown and portable ZIP editions are rebuilt from those sources; no audio
recording is supplied.

The rebuilt local reader passed 11 Chromium checks: all 34 reading sections,
new-story hash navigation and content, fiction status, the earlier-edition link,
desktop and 390px geometry, no script exceptions and no external asset requests.
Desktop Lighthouse and narrow Ninth Road screenshots were inspected. No physical
phone, outside reader, narration or live Pages deployment was tested for this batch.

Preserved findings include trust-root failures, gamed choice frontiers,
conventional export/recovery ties, the 18/18 conventional goal-aware policy tie,
and seven differing reachability outcomes in eight paired fictional graphs
with an unchanged negative control. A valid signature is not evidence of
informed human consent. A local fence cannot undo an already accepted remote
effect. Author-declared graphs do not measure human free will or dependency.

No real participant study, independent security audit, model-behaviour trial,
production deployment, external-provider security result, novelty or superiority
claim follows from this intake. The older consciousness-thermodynamics theory
is not validated by these agent-control experiments. Existing individual
licence notices are retained; no blanket relicensing is performed.

## Publication state

This batch is prepared for a public topic branch and pull request. Links above
resolve within that branch before merge. The repository requires an approving
review for master; no branch-rule bypass or billing changes are authorised by
this review. Hosted CI and deployment status must be read from the actual PR,
separately from the local results recorded here.
