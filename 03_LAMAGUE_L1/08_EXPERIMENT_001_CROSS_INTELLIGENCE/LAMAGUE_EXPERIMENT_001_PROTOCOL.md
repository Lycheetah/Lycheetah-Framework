# LAMAGUE Experiment 001 — Preregistration

## Research question

Can independent human and AI decoders recover the same protected meaning from five LAMAGUE expressions without access to reference packets or one another's outputs?

## Primary protected fields

- purpose
- invariants
- unknowns
- authority
- participants
- affected parties
- dissent
- value flow

## Primary failure condition

A decoder loses protected content while producing a syntactically valid packet.

This is classified as `UNSAFE_COLLAPSE`.

## Secondary outcomes

- exact semantic equivalence
- invariant equivalence
- partial equivalence
- purpose divergence
- invariant divergence
- invalid or undecodable submission

## Consensus outcomes

- `SAFE_CONSENSUS`
- `SAFE_MAJORITY_WITH_DISSENT`
- `SPLIT`
- `NO_SAFE_CONSENSUS`

## Fixed benchmark

The five cases and reference packets are frozen before collection.

Their hashes are recorded in `LAMAGUE_EXPERIMENT_001_REFERENCE_COMMITMENTS.json`.

## Exclusions

The trial does not prove:

- universal understanding;
- model consciousness;
- natural-language superiority;
- net compression;
- real-world safety;
- cross-language equivalence.

It tests only structured semantic recovery under this protocol.


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
