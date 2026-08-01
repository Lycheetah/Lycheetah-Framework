# LAMAGUE Runtime v0.3 — Cross-Intelligence Equivalence Harness

Runtime v0.3 is an offline laboratory for testing whether independent humans or AI systems recover the same protected meaning from a LAMAGUE expression.

It does not call external models. It supplies:

- a blind decoder prompt;
- a strict JSON packet schema;
- five benchmark cases;
- semantic and critical hashes;
- field-by-field loss detection;
- equivalence classification;
- consensus clustering;
- a command-line runner;
- a standalone HTML report viewer.

## Equivalence classes

```text
EXACT_EQUIVALENT
INVARIANT_EQUIVALENT
PARTIAL_EQUIVALENT
UNSAFE_COLLAPSE
DIVERGENT
UNDECODABLE
```

`UNSAFE_COLLAPSE` is reserved for the loss of protected unknowns, authority, participants, affected parties, dissent, or value flow.

## Consensus states

```text
SAFE_CONSENSUS
SAFE_MAJORITY_WITH_DISSENT
SPLIT
NO_SAFE_CONSENSUS
```

The harness never hides dissenting decoder outputs.

## Quick start

```bash
python -m unittest discover -s tests -v
python examples/cross_intelligence_equivalence_demo.py

python -m lamague_runtime.cli validate-packet benchmark/sample_packets/C01_UNPROVEN_CLAIM__SIM_DECODER_SAFE.json

python -m lamague_runtime.cli benchmark \
  benchmark/challenge_pack.json \
  benchmark/sample_packets \
  --output benchmark/reports/my_report.json
```

## Real cross-model workflow

1. Open `benchmark/CROSS_INTELLIGENCE_BLIND_DECODER_PROMPT.md`.
2. Give the same case to each model or human without the reference packet.
3. Save each returned JSON as `CASE_ID__DECODER_ID.json`.
4. Place the files in one directory.
5. Run the benchmark command.
6. Inspect every collapse, extension, divergence, and split.

The included outputs are simulations used to verify the harness. They are not evidence that any external model passed.
