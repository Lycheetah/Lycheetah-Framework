# Shadow Evidence Review Protocol

## Purpose

Use privacy-safe local comparison records to decide whether the candidate engine is technically stable enough for a visible research preview.

This protocol does not calibrate Truth Pressure and does not establish scientific validity.

## Collection state

Initial app mode:

```text
shadow
```

The historical result remains visible.

Collect at least:

```text
100 deliberate user-submitted analyses
```

Do not analyze on every keystroke.

## Mandatory engineering gates

- 100 privacy-safe records.
- No NaN or infinite outputs.
- Candidate normalized pressure remains within `[0,1]`.
- Every text record remains `TRIAGE_ONLY`.
- No raw analyzed text appears in the dataset.
- Every comparable trigger disagreement receives human review.

No acceptable disagreement rate is invented in advance.

## Review questions

For each disagreement that can be reconstructed while the user still has the result open:

1. Which engine moved higher?
2. Was the movement caused by evidence, explanation, strain, or rhetoric?
3. Did either engine reward repetition, certainty language, jargon, or citation appearance?
4. Did the candidate punish honest uncertainty?
5. Did the candidate explanation accurately name its own cause?
6. Would displaying the candidate have helped or confused the user?

## Article rule

The article may report only values present in an exported evidence report.

Do not write:

- “validated”;
- “accurate”;
- “scientifically proven”;
- “detects truth.”

Before human ratings and held-out validation, the strongest permitted engineering statement is:

> The candidate completed a privacy-safe shadow run of N cases without automatic restructuring, non-finite output, or raw-text logging, while exposing its disagreements with the historical engine for review.
