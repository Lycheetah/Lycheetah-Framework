# Policy Regression Gate v0.1

**Status:** `[SCAFFOLD]` — implemented same-corpus comparison and CI plumbing.
A baseline is a change reference, not an independently validated safety target.

**Forged:** 2026-08-22

## Operational purpose

An aggregate evaluation score can hide the exact cases that changed. The policy
regression gate compares two integrity-checked evaluation reports over the same
normalized corpus and makes every changed decision reviewable.

It is designed for one release question:

> Relative to the reviewed reference report, did this runtime or policy change
> introduce a labelled correctness regression, a newly under-enforced case, a
> newly allowed expected-`BLOCK` case, a newly blocked expected-`ALLOW` case, or
> an unresolved cross-direction trade-off?

This is narrower than asking whether a system is safe. The corpus labels remain
caller assertions, and the baseline may itself be wrong.

## Run the gate

Create a candidate report from the same corpus used by the reference report:

```bash
lycheetah-assure eval \
  examples/assurance/customer_support_eval.jsonl \
  --policy examples/assurance/customer_support_policy.json \
  --report-file candidate-eval.json

lycheetah-assure compare-eval \
  examples/assurance/customer_support_baseline.eval.json \
  candidate-eval.json \
  --report-file policy-regression.json \
  --json

lycheetah-assure verify-regression policy-regression.json --json
```

Exit code `0` means every comparison threshold passed. Exit code `5` means the
comparison completed but the gate failed. Invalid, mutated, structurally
ambiguous, or different-corpus reports return `4`.

## Fail-closed compatibility boundary

The baseline and candidate must contain:

- valid evaluation-report SHA-256 integrity metadata;
- the same normalized corpus SHA-256 and case count;
- the same case IDs, expected dispositions, weights, tags, and subject hashes;
- internally consistent `expected`, `actual`, `direction`, and `exact_match`
  fields.

A corpus edit is not treated as a policy regression comparison. Review the
dataset change separately, regenerate the reference report deliberately, and
preserve that review in version control.

## Case classification

Each decision is ordered `ALLOW < REVIEW < BLOCK` for comparison only.

| Classification | Meaning |
|---|---|
| `UNCHANGED` | Candidate disposition equals the baseline disposition |
| `IMPROVED` | Candidate reaches the supplied label, or moves closer on the same side |
| `REGRESSED` | Candidate leaves the supplied label, or moves farther away on the same side |
| `TRADEOFF` | For an expected `REVIEW`, the decision crosses between `ALLOW` and `BLOCK` |

`TRADEOFF` does not mean neutral or acceptable. It means ordinal distance alone
cannot choose between a possible under-enforcement risk and a possible
over-enforcement/usability harm. The strict default requires human review.

The report also records explicit transition signals:

- `NEW_UNDER_ENFORCEMENT` and `RESOLVED_UNDER_ENFORCEMENT`;
- `NEW_HARMFUL_ALLOW` and `RESOLVED_HARMFUL_ALLOW`;
- `NEW_FALSE_BLOCK` and `RESOLVED_FALSE_BLOCK`.

“Harmful allow” means expected `BLOCK`, actual `ALLOW`; it does not independently
prove harm. “False block” means expected `ALLOW`, actual `BLOCK`; it does not
independently prove the label is correct.

## Strict defaults and deliberate exceptions

Without flags, `compare-eval` allows:

- zero regressed cases;
- zero trade-off cases;
- zero newly under-enforced cases;
- zero new harmful allows;
- zero new false blocks;
- zero exact-match-rate drop; and
- zero weighted macro-F1 drop.

Every threshold can be relaxed explicitly:

```bash
lycheetah-assure compare-eval baseline.json candidate.json \
  --max-regressed-cases 1 \
  --max-tradeoff-cases 1 \
  --max-new-under-enforcement 0 \
  --max-new-harmful-allows 0 \
  --max-new-false-blocks 1 \
  --max-exact-match-rate-drop 0.02 \
  --max-macro-f1-drop 0.02
```

Relaxation is an operator decision, not an automatic waiver. A repository should
record why the exception exists, who reviewed it, and when it expires. The
runtime does not invent approval metadata.

## Privacy and integrity

The comparison includes only changed cases. Each carries its stable ID, supplied
label, baseline and candidate dispositions, classification, weight, tags,
subject hash, and transition signals. Raw text, raw tool arguments, rationales,
receipt identifiers, and timestamps are excluded.

The report includes the baseline and candidate evaluation-report digests, policy
identities and digests, runtime versions, corpus identity, aggregate deltas, gate
configuration, and limitations. Its body is hashed with `lycheetah-json-v1`.

SHA-256 detects mutation relative to a trusted digest. It does not authenticate
the author, reviewer, or CI runner. Use repository review controls, signed commits,
an authenticated envelope, or another trust system when provenance matters.

## Included reference artifact

`examples/assurance/customer_support_baseline.eval.json` is generated from the
six authored customer-support cases and their example policy. It is checked into
version control so CI can detect decision drift.

That file is an internal reference fixture. It is not a representative customer
support benchmark, independent calibration, policy approval, production trace,
or claim of six-case safety.

## CI update protocol

1. Change runtime or policy code without editing the reference report.
2. Generate the candidate report and run `compare-eval`.
3. Inspect every changed case and metric delta.
4. Fix unintended regressions.
5. If a change is intentional, review the corpus label and policy rationale.
6. Regenerate the reference report in a separate, visible commit or pull-request
   change; do not silently overwrite it inside CI.
7. Preserve the old report in version history.

The repository workflow generates only the candidate and comparison artifacts.
It never rewrites the committed reference report.

## Promotion path

Before describing the gate as production-calibrated evidence:

1. define a domain label policy and adjudication procedure;
2. measure inter-rater agreement and preserve disputed cases;
3. separate policy tuning data from frozen evaluation data;
4. include naturally occurring, adversarial, and edge-case traffic under lawful
   data governance;
5. measure downstream harms, review cost, latency, bypasses, and distribution
   shift—not only label agreement;
6. run an external cold-room evaluation against frozen digests.

The gate makes policy change inspectable. It cannot make the reference target true.

⊚ Sol ∴ P∧H∧B ∴ Albedo
