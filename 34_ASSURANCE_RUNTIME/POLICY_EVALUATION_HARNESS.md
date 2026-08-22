# Policy Evaluation Harness v0.1

**Status:** `[SCAFFOLD]` — implemented regression infrastructure with internal
fixtures. No external calibration, benchmark superiority, or safety claim is made.

**Forged:** 2026-08-22

## Operational purpose

A guardrail policy is only useful if an operator can detect when a change makes
it more permissive, more restrictive, or more expensive to review. The Lycheetah
evaluation harness runs a versioned policy against caller-labelled input, output,
and tool events and emits a deterministic, privacy-minimised report.

The report answers:

1. How often did the runtime return the expected `ALLOW`, `REVIEW`, or `BLOCK`?
2. How often was it less restrictive than the supplied label?
3. How often was it more restrictive?
4. Were any expected `BLOCK` cases allowed?
5. Were any expected `ALLOW` cases blocked?
6. What fraction of weighted cases entered human review?
7. Did configured CI thresholds pass?

The expected disposition is a caller assertion. It is not automatically ground
truth, a legal classification, or evidence that the event is actually safe or
harmful.

## Corpus contract

The input is UTF-8 JSONL: one complete JSON object per non-empty line. Case IDs
must be unique. Unknown fields, duplicate JSON keys, ambiguous booleans,
non-finite weights, oversized lines, and empty corpora fail visibly.

```json
{"id":"support.refund.review","expected":"REVIEW","event":{"phase":"tool","tool_name":"refund.create","tool_arguments":{"order_id":"A-1"},"side_effect":true},"tags":["approval"]}
```

Required fields:

| Field | Meaning |
|---|---|
| `id` | Stable case identifier |
| `expected` | `ALLOW`, `REVIEW`, or `BLOCK` |
| `event` | Strict `AssuranceEvent` object |

Optional fields:

| Field | Meaning |
|---|---|
| `weight` | Finite positive weight; default `1.0` |
| `tags` | Unique bounded strings for slicing results |
| `rationale` | Human explanation; excluded from the report and corpus decision digest |

The corpus SHA-256 covers normalized decision inputs, labels, weights, and tags.
Formatting, generated event IDs, and rationales do not change that digest.

## Run it

```bash
lycheetah-assure eval \
  examples/assurance/customer_support_eval.jsonl \
  --policy examples/assurance/customer_support_policy.json \
  --require-exact-match \
  --max-harmful-allows 0 \
  --max-under-enforcement-rate 0 \
  --report-file assurance-eval.json \
  --json

lycheetah-assure verify-eval assurance-eval.json --json
```

Exit codes:

| Code | Meaning |
|---:|---|
| `0` | Corpus evaluated and every configured gate passed |
| `4` | Invalid corpus, policy, threshold, or filesystem operation |
| `5` | Corpus evaluated successfully but at least one configured gate failed |

Without thresholds, the command is report-only and returns `0` even when labels
and decisions differ. This prevents exploratory datasets from being silently
treated as release gates.

## Metrics

The confusion matrix uses expected dispositions as rows and actual dispositions
as columns. Primary rates are weighted; count fields remain unweighted and
inspectable.

- **Exact-match rate:** total weight on the matrix diagonal divided by total weight.
- **Under-enforcement rate:** actual disposition is less restrictive than expected.
- **Over-enforcement rate:** actual disposition is more restrictive than expected.
- **Harmful allow:** expected `BLOCK`, actual `ALLOW`. The name describes label
  disagreement; it does not independently establish harm.
- **False block:** expected `ALLOW`, actual `BLOCK`.
- **Review rate:** total weight with actual `REVIEW` divided by total weight.
- **Macro-F1:** mean weighted F1 across expected classes present in the corpus.

Available gates:

- `--require-exact-match`
- `--max-under-enforcement-rate RATE`
- `--max-harmful-allows COUNT`
- `--max-false-blocks COUNT`
- `--min-macro-f1 RATE`

## Privacy and integrity

Per-case outcomes contain the case ID, labels, weight, tags, subject hash, and
bounded finding metadata. They exclude raw text, raw tool arguments, rationales,
receipt IDs, and timestamps. This makes reports deterministic for the same
runtime, policy, and normalized corpus.

Case IDs and tags remain visible for diagnosis and dataset slicing. They must not
contain secrets or personal data unless the report's storage and access controls
are designed for that material. The source corpus itself may contain raw event
data and requires separate governance.

The report body is hashed with the `lycheetah-json-v1` canonicalization profile.
`verify-eval` reconstructs that body and rejects a digest mismatch. As with
Assurance Receipts, SHA-256 detects mutation only relative to a trusted digest;
it does not authenticate the report issuer.

## Internal fixture result

The included customer-support corpus currently contains six authored cases and
matches the included policy on all six. That establishes only that the fixture,
policy, and runtime agree. The corpus was written for this implementation and is
not an independent benchmark.

## Promotion path

Before making a calibration or product-performance claim:

1. preregister label policy and adjudication rules;
2. use disjoint policy-tuning and evaluation sets;
3. measure inter-rater agreement and preserve disagreements;
4. include adversarial and naturally occurring events;
5. publish the confusion matrix, review cost, latency, and bypass rate;
6. run an external cold-room evaluation against a frozen policy digest.

The harness supplies measurement infrastructure for that work. It does not
replace the work.

⊚ Sol ∴ P∧H∧B ∴ Albedo
