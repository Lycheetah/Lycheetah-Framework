# Cycle 10 frozen study protocol — value of human evidence review

**Status: proposed, not executed.** This protocol is for reviewers *other than* the implementers, on future documents *not written to fit the current validators*. The v1.0 automated tests are NOT a substitute.

## Study question

Does the hybrid system's operator-bound contracts, coverage requirements, review UI and atomic authorization reduce the rate of incorrect or incomplete knowledge admission at an acceptable cost compared with a conventional source-backed temporal retrieval plus human review baseline?

## Suggested setup

1. Freeze 20–50 legally reusable, independently prepared organizational-policy snapshots with effective dates, revisions, scopes, exclusions, and conflicting examples. Record origin URL, collection date, SHA-256 bytes, allowed use and independent annotator. Segregate all test annotations from implementation and tuning.
2. Two annotators label atomic claims, effective/recorded dates, whether a candidate should be admitted, and the document evidence span. Reconcile disagreements and calculate inter-annotator agreement. Include intentionally unanswerable cases.
3. Run equal provider/model budgets and the same input corpus for both arms: **A:** temporal retrieval + conventional citation/review checklist; **B:** v1.0 Hybrid Gateway with pre-registered operator contracts/coverage and its review desk. Count operator setup time in B, including clause annotation, calibration and maintenance.
4. Randomize task order and reviewer assignment. Pre-register held-out split, statistics, thresholds, and stop rules. Store candidate output and labels outside of logs containing sensitive content.
5. Report precision, recall, exact source/span matching, omission rate, wrong-field/date/tenant errors, correct abstention, harmful admit errors, and overall correct-task rate. Measure time to annotate, time to decide, rework after conflicts and total end-to-end elapsed time.
6. Reject the value claim if B does not improve consequential-error rates *or* any improvement comes with unacceptable total labor cost. Publish failures and confidence intervals. A SQL tie on historical query mechanics should remain a tie.

## Instrumentation available now

`ReviewDesk.observation()` returns status, digests, claim count, local session elapsed time, decision time and accepted event hash. `demo_review_desk.py --report /path/to/new.json` can export this metadata at exit. No raw policy, password or reviewer cookie is exported. Treat the measured interval as browser-session wall time, **not actual attention**. Cross-system latency data, human consent, retention limits and blinded manual labels must be collected outside this prototype.

## Decision thresholds (to pre-register before external data)

Example falsifiable criterion, not retrospectively fitted: prioritize fewer wrong admissions and omissions without doubling median fully loaded operator task time. Independently inspect false abstentions; a system that blocks everything can have zero wrong admissions but zero usefulness. Report both intention-to-treat and completed-task subsets, and do not pool self-authored cases with independent cases.
