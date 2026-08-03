# Truth Pressure Measurement Pack v0.4

A blinded human-annotation package for testing whether `E`, `P`, and `S` are understandable and reproducible constructs.

This is a **development-corpus construct pilot**, not held-out validation.

## What to send raters

Send each person only:

- `RATER_INSTRUCTIONS.md`
- one file from `rater_packets/`

Do not send:

- `admin/BLINDING_KEY.json`
- the engine outputs;
- case titles or families;
- expected directions;
- another rater's packet or answers.

## Rater minimum

Use three independent raters. They should complete their packet separately and avoid discussing cases until all files are locked.

## After collection

Place the completed files in one directory and run:

```bash
python scripts/analyze_annotations.py \
  --key admin/BLINDING_KEY.json \
  --ratings completed/RATER_A_PACKET.csv completed/RATER_B_PACKET.csv completed/RATER_C_PACKET.csv \
  --engine-results ../TRUTH_PRESSURE_ENGINE_v0.3_SEMANTIC_HARDENING/reports/DEVELOPMENT_CORPUS_RESULTS.jsonl \
  --output reports/HUMAN_PILOT_RESULTS.json
```

The analysis reports component-level agreement and engine correspondence. It does not validate Truth Pressure as truth detection.
