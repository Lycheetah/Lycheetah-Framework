# Controlled Pilot — 2026-07-31

Raw data and scoring for the first controlled run of Experiment 001.

Full writeup: `../EXPERIMENT_001_CONTROLLED_PILOT_2026-07-31.md`

```
control_arm/              29 plain-English packets (the CONTROL arm)
scoring/RESULT.txt        the scored comparison
scoring/breakdown.json    per-case and per-decoder detail
scoring/score_arms.py     the scorer — read its docstring before citing a number
scoring/run_both.py       collection, both arms, leakage-guarded
scoring/run_control.py    the control prompt and source-statement extractor
scoring/collection_log.txt  every attempt, including the 4 failures
```

The 27 **treatment** packets live in `../OPERATOR_PACK/submissions/OTHER/`.

The control arm is held here, **outside** the operator pack, on purpose. A
control arm scored as if it were treatment would corrupt the real result, and
preventing that is what a preregistered experiment is for.

## Before citing any number from this run

Read the RETRACTION section of the writeup. The first scoring reported a
headline finding that was an artifact of the scorer, not an effect. The
corrected numbers are smaller and verified against the source statements.

This is an **operator-run pilot**, not independent replication. One operator,
one machine, one session, six model lineages, no human decoders, n=56, no
statistical test.
