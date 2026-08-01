# LAMAGUE Experiment 001 — Decoder Pack

## Your role

You are an independent decoder.

You must not see the reference packets or another decoder's output before submitting your own.

## Procedure

1. Read `BLIND_DECODER_PROMPT.md`.
2. Read `OPERATION_DEFINITIONS_REQUIRED.md`.
3. Decode each file in `cases/`.
4. Return one JSON object per case matching `decoder_packet.schema.json`.
5. Set `decoder_id` to your model, system, or anonymous human identifier.
6. Name each file:

```text
CASE_ID__DECODER_ID.json
```

Example:

```text
C01_UNPROVEN_CLAIM__GPT56.json
```

## Integrity rule

Do not praise or improve LAMAGUE.

Do not resolve missing information.

Do not infer authority, consent, evidence, affected parties, or recovery.

The purpose of the experiment is to discover where meaning survives and where it collapses.
