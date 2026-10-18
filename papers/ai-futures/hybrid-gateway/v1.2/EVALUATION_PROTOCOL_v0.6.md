# External evaluation protocol — pre-registration scaffold, NOT completed evaluation

**Goal:** Determine whether the Lycheetah Hybrid Gateway improves the factual precision, recall, abstention calibration and traceable updating of a real neural extraction agent against practical alternatives, after accounting for annotation and review costs.

## Corpus design

- Obtain at least 100 previously unseen documents with rights to use and publish derived statistics. Prefer heterogeneous real policies or specifications and a purposeful distribution of positives, negatives, exceptions, substitutions, historic amendments, bilingual cases, multiple dates and competing scopes. Do not take source text from the model provider's private systems or a real customer's confidential data without authorization.
- Have independent annotators label `(subject, predicate, scope, value, valid_from, valid_until)` and cite source passages. Resolve differences through documented adjudication, retaining agreement metrics. Annotators should not see experimental model outputs or validator source code.
- Record document origin, legally shareable corpus digest, selection strategy, sample size by domain, annotator counts, exclusions, pre-registration date and decisions made before looking at outcome metrics.
- Freeze the gold JSONL file. Record its SHA-256 out of band and pass it to `--expected-corpus-digest` for every report. Keep training/dev vs locked test split separate. No adjusting regexes to the locked test examples then reusing them as unseen test cases.

## Four conditions to compare (same base LLM and source split)

A. Direct model structured extraction, with no extra guard.

B. Model + verbatim quote/value check.

C. Model + operator-annotated v0.4 clause binding.

D. Model + v0.5 coverage plan + v0.6 atomic admission. Admission needs explicit operator review; score extraction separately from commit eligibility to avoid comparing different targets.

Freeze provider, model version, temperature, context limit, prompt version, max tokens, retries, retrieval settings, seed where supported and total inference cost before locked holdout. Instrument annotation/review time honestly with observed timings, not zero-filled examples.

## Scorecard

- Claim TP, FP, FN; micro precision, recall and F1.
- Wrong-field/scope, wrong-date, unsupported-reference errors (separate adjudication required beyond this simple script).
- Positive-document recall and completely missed positive documents.
- Correct abstention rate on true negative documents; show these **alongside** positive recall to prevent reward for always abstaining.
- Exact document match, refusal/review rates, full end-to-end task completion after human approval.
- Median/p95 elapsed review time, cost per accepted correct claim, operator time for markup. Existing scorer aggregates supplied review minutes; it does not automatically measure real clocks.
- Replay integrity, stale-write rejection, atomic failure under injected SQL write error and controlled concurrency (v0.6 test suite covers local cases).

## Falsifiers

- The gateway's *end-to-end* correct, authorized completions are no better than version-aware retrieval + human review at equal operator time.
- Human annotation burden exceeds time saved, especially on heterogeneous documents.
- Recall becomes impractically low on conditionals, exceptions or bilingual policies; strict whitelisting can reduce false positives yet miss too many real facts.
- An independently annotated invalid admission passes operator-plan and contracted review more often than baseline.
- A failed SQL batch writes any subset of its claims, or stale review can overwrite a later revision.

## Current status and limitation

No third-party labeled holdout was acquired in this cycle. The included 14-case JSONL is self-authored and the fixture predictions are manually scripted; all scores are instrument demonstrations only. Independent annotator status cannot be proven by JSON metadata; the research team must document provenance externally.
