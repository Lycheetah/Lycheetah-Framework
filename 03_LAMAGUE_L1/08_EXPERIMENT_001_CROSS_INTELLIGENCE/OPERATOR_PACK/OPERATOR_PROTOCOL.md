# Operator Protocol

## Before collection

1. Publish or timestamp the reference commitment file.
2. Keep `sealed_references/` hidden from every decoder.
3. Send only the Decoder Pack.
4. Do not discuss expected answers.

## Collection

Store untouched outputs under:

```text
submissions/GPT/
submissions/CLAUDE/
submissions/GEMINI/
submissions/GROK/
submissions/HUMAN/
submissions/OTHER/
```

Use the exact filename:

```text
CASE_ID__DECODER_ID.json
```

Never repair a decoder packet manually.

Invalid packets remain evidence and must be logged.

## Analysis

Run:

```bash
python run_experiment.py
```

The script validates submissions, checks reference commitments, evaluates equivalence, writes JSON and CSV reports, and creates a Markdown summary.

## Publication

Publish:

- preregistration;
- reference commitment;
- untouched submissions;
- machine report;
- human-readable summary;
- invalid-submission log;
- exact runtime version.

Do not report simulations as external-model results.
