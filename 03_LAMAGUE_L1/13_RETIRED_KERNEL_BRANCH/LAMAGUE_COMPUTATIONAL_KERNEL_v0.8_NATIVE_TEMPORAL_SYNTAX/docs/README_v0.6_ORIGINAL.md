# LAMAGUE Computational Kernel v0.6

## Thesis

Most programming languages type-check data.

LAMAGUE aims to type-check consequential meaning.

This release is a bounded reference implementation of that thesis. It compiles a small textual language into a typed semantic intermediate representation and executes immutable abstract state transitions while preserving:

```text
evidence
unknowns
invariants
authority
affected parties
dissent
value flow
recovery
lineage
```

## Pipeline

```text
LAMAGUE source
→ parser
→ typed program model
→ semantic IR
→ type and effect checks
→ immutable runtime
→ cryptographic state lineage
→ bounded output
```

## Supported operation surface

The kernel registers all twenty-six Native-36 semantic operations:

```text
A Anchor       N Novelty
B Bridge       O Observe
C Cycle        P Prove
D Drift        Q Query
E Evidence     R Resolve
F Fold         S State
G Guard        T Transition
H Horizon      U Unknown
I Invariant    V Vector Invert
J Junction     W Weave
K Kernel       X Exchange
L Limit        Y Yield
M Merge        Z Compress / Expand
```

The nine-operation Public Core remains the public entrance:

```text
O E U I G V F Y Z
```

## Hard computational failures

The compiler rejects consequential execution without typed authority, `MayAffect` without affected parties, value transfer without visible flow, risk without recovery, irreversibility without all four gates, erased protected unknowns, unlocked invariants, dissent suppression, fake resolution, and yield without prior fold.

`RECOVERABLE` means execution is forced through a safe machine response. Unsafe compression becomes `Z_UP`; it is not ignored.

## Quick start

```bash
python -m lamague_kernel run examples/controlled_release.lmg
python -m unittest discover -s tests -v
```

## Current boundary

This kernel executes abstract semantic state transitions. It does not understand unrestricted natural language, prove real-world safety, control production systems, or establish that the full hundred-plus-symbol corpus is canonical.


## v0.6 Semantic Integrity Benchmark

This release adds a deterministic benchmark harness and a synthetic seed corpus.

```text
20 frozen reference cases
200 candidate packets
6 equivalence classes
7 protected critical fields
```

Run the benchmark:

```bash
python -m lamague_benchmark benchmark_corpus/manifest.json -o benchmark_reports/report.json
```

The included 100% label match verifies the scorer against deliberately constructed mutations. It is not model or human performance evidence.
