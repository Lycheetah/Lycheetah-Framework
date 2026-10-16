# First-run protocol: CASCADE safety and utility

## Purpose
Test whether dependency-aware review helps researchers notice material downstream implications without falsely converting coherence into truth.

## Hypotheses
- H1 (utility): dependency-aware review finds more materially affected downstream claims than a static evidence ledger.
- H2 (safety): the conservative implementation never changes claim status automatically.
- H3 (workload): review-queue precision is high enough to be useful, without an excessive rate of irrelevant alerts.
- H4 (epistemic quality): the system preserves conflicting hypotheses and distinguishes normative commitments from empirical claims.

## Current automated unit tests
1. Direct and transitive dependents are queued.
2. An explicit contradiction partner and that partner's dependents are queued.
3. Unrelated blocks are not queued in the synthetic test.
4. No status changes occur automatically.
5. Contradictory claims remain stored and discoverable.
6. A status decision creates an audit record.
7. Missing dependencies fail fast.
8. Empty decision rationale is rejected.
9. Unknown status labels are rejected.
10. A dependency cycle terminates without returning the starting block as its own affected item.
11. Self-dependency is rejected.

## Not yet implemented as automated behavior tests
- Source withdrawal and provenance propagation.
- Prompt injection in untrusted source text.
- Semantic false cascades from irrelevant wording changes.
- Inter-reviewer agreement and evidence calibration.
- Political symmetry under matched claims, labels, and value profiles.

## Baselines
A. Static evidence ledger with manual search.
B. Dependency/contradiction graph with manual review (current prototype).
C. Proposed AURA metric-triggered cascade (only after metric formulas are fully specified and independently tested).

## Metrics
- Recall of known affected downstream blocks.
- Precision of review alerts.
- False automatic status changes (target: zero).
- Contradictions retained and discoverable.
- Provenance completeness.
- Reviewer time and inter-reviewer agreement.
- Evidence calibration on a separate prediction task (not inferred from coherence score).

## Pre-registration checklist
Before comparative tests, freeze the test corpus and expected affected-block labels; define “materially affected” and “false alert”; set scoring rules and adjudication; record model versions/prompts if an LLM is used; record random seeds and code commit; specify exclusion criteria and the reporting template.

## Stop conditions
Pause deployment if the system automatically removes a claim due only to value disagreement; upgrades a hypothesis to fact without evidence; loses provenance or history; presents an uncalibrated score as probability or truth; or shows material political asymmetry under matched test cases.

## Structural conformance pilot (v0.1)
A researcher-authored 12-case synthetic fixture suite is included in `structural_benchmark_cases.json`, with a runner and machine-readable results. It checks traversal mechanics only (direct/transitive dependencies, contradiction closure, disconnected blocks, cycles, and protection against automatic status changes). The current implementation matches all 12 declared expected sets. These expected sets were authored from the written traversal rule and have not been independently adjudicated. The result is **not** evidence of real-world usefulness, factual accuracy, political neutrality, or superiority to manual review. The next evaluation gate remains a 30–50 graph set with two independent reviewers labelling material review impacts before testing.
