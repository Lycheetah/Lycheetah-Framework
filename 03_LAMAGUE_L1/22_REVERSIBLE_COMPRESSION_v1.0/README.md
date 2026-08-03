# LAMAGUE Reversible Compression Milestone v1.0

This package is the article-worthy threshold for LAMAGUE compression.

## Measured headline

```text
Structured packets                           36
Dictionary training                          24
Held-out packets                             12
Exact round trips                            36 / 36
Constructed mutation matches                 324 / 324
Held-out warm reduction vs minified JSON     33.8%
Held-out cold reduction including codebook   30.7%
Dictionary break-even vs compact L1          3 packets
```

## Run

```bash
python src/benchmark.py
python -m unittest discover -s tests -v
```

## Encode

```bash
python src/cli.py encode packet.json --codebook corpus/codebook.json -o packet.lmgc
```

## Decode

```bash
python src/cli.py decode packet.lmgc --codebook corpus/codebook.json -o restored.json
```

## Read first

1. `reports/BENCHMARK_REPORT.md`
2. `docs/CLAIM_BOUNDARY.md`
3. `article/ARTICLE_DRAFT.md`

## Status

```text
Reversible structured codec        WORKING
Training-only dictionary            WORKING
Held-out benchmark                  COMPLETE
Exact full and critical receipts    COMPLETE
Protected-loss mutation suite       COMPLETE
Unrestricted prose compression      NOT CLAIMED
External human/model validation     NOT YET RUN
```
