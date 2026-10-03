# Verification Receipt

**Historical packet receipt:** Agent Safety Research · public working paper v0.3 · 3 October 2026

**Scope:** publication of the research packet, its paper-index entry, and a focused CI workflow in the public Lycheetah Framework repository. The author authorised backup, adversarial evaluation, and GitHub upload on 3 October 2026. A private pre-publication snapshot preserves the original 25 files; archive contents were checked against their SHA-256 manifest before publication preparation. No language-model experiment, participant study, paid model call, or real-service experiment is performed. GitHub publication is the explicitly authorised external effect.

## Highest gate passed

**PASS — focused unit tests, scripted synthetic control comparison, two additional counterexamples per arm, artifact read-back, and authoring-seat adversarial review.** This is not independent security review, a real-agent benchmark, or production safety certification.

The observed command `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -v`, rerun in the public packet's simulator directory, completed with exit code zero: **53 methods, no failures or errors**. Methods include subtests, including both permission stores and deliberately preserved counterexamples. The [test receipt](simulator/reports/unit-tests.json) records the runtime and observation; [raw output](simulator/reports/unit-tests.txt) is retained. No performance comparison is inferred from the timing.

The report generator executed **19 scripted cases in each of two arms** and returned exit code zero. All cases met their expected outcomes; matched aggregate observations were identical. Raw traces, admission/revocation events, provider effects, and Python fingerprints are in [scripted-controls.json](simulator/reports/scripted-controls.json). The renderer produced the [result table](simulator/reports/RESULTS.md).

Each arm deliberately permits a synthetic harmful-content marker under its incomplete policy. Each also allows previously admitted work to complete after revocation. These are exposed limits, not protective successes. A separate test shows that source faithfulness can preserve a false arithmetic assertion. An explicit mediation-bypass negative control discloses a synthetic private document, showing why the simulator's trust assumption matters.

The additional `adversarial_checks.py` run reproduced two counterexamples in each arm: instance-local broker ledgers can multiply a nominal shared root budget, and a context change after admission does not cancel the admitted write. [Raw adversarial results](simulator/reports/adversarial-checks.json) and [review dispositions](ADVERSARIAL_REVIEW.md) preserve these stronger-contract failures. The simulator behavior is retained rather than relabelled as production-safe.

## Focused structural checks

Read-back confirmed both top-level JSON files parse; all 21 manuscript claim identifiers, 12 external source identifiers, and 11 Framework/packet source identifiers resolve; claim statuses and evidence references resolve; all relative Markdown links exist in the public checkout; all nine public-source/report digests match; and all Python fingerprints in both reports match the tested files. Two unpublished background entries have no private path or distributed file. There are 14 Python files, each below 400 lines. The recorded 53-method count matches the test definitions. A focused publication scan checked the exact changed file set for private paths, private-repository identifiers, credential patterns, and stale publication-status claims.

Manual drafting-seat review checked the action predicate, ancestor invalidation, fixed interpretation assumptions, budget induction, revocation ordering, actual synthetic effects, and matched comparison boundaries. It narrowed qualifier validation to the exact allowed set: retaining old qualifiers while admitting arbitrary added instructions would not preserve the intended closed contract. This was an implementation-review correction made before the passing test run, not a claimed independently discovered vulnerability.

## Source and ownership boundaries

External primary-source inspection depth is recorded in [SOURCES.json](SOURCES.json); several entries are metadata/abstract checks, not full-paper audits. Publisher/OpenReview access failures remain disclosed. Internal Framework labels and codec benchmark reports are not promoted into independent validation.

Public preparation used a clean checkout of the public repository at revision `8925e3ead2e85a1a121086e814cdc971fe21a2c1`. Six cited Framework documents match the inspected source bytes at that revision. The public change set contains this packet, its papers-index entry, and the focused workflow. Private workspace history, sibling-app files, internal control-plane state, existing website edits, and other manuscripts are excluded.

The packet-local claim register preserves conditional and untested claims and records four bounded MEASURED observations, including the new counterexamples. These measurements are author-assisted and self-authored; no independent reviewer, annotator, or peer reviewer is implied. Public sharing permission is not scientific approval. Main-branch integration remains subject to the repository's review rule; the GitHub commit/PR records establish upload and merge state separately from this local scientific receipt.

## Unwalked evidence

- Credential/process isolation, remote authentication, and hostile-code containment.
- Crash-safe persistence, distributed admission, and actual provider billing/cancellation.
- Independently designed challenges and external security review.
- Natural-language interpretation, a complete harm policy, and general information-flow tracking.
- Persistent memory/deletion, tested restoration, model motivation, and deception research.
- Model-agent comparison, human comprehension, and affected-party outcome studies.
- Novelty, safety improvement, independent replication, and peer review.
- Multi-broker shared accounting and dispatch-time evidence revalidation.

Final artifact hashes are recorded in [artifact-manifest.json](simulator/reports/artifact-manifest.json). That manifest omits its own digest to avoid self-reference. Experimental source fingerprints are also preserved separately in the raw report.

## Current v0.4 focused repair witness

The counts and original report fingerprints above describe the v0.3 publication
snapshot, not today's changed files. The [new repair note](BUDGET_REPAIR.md) records
46 passing methods from the broker, authority and shared-accounting modules,
19 scripted cases per arm with matching expected aggregates, and one repaired
budget probe plus one still-reproduced freshness limit in each arm. Current Python
fingerprints are retained in `simulator/reports/budget-repair/`; original reports
remain unchanged and pinned to `c998df9f8118cdc4ca1e1d7659fd186d49d84bd7`.

No full repository or complete simulator suite was run for this repair. No model
or provider call, production integration, independent audit or peer review occurred.
The new measured claim C22 is bounded to one live shared control plane.
