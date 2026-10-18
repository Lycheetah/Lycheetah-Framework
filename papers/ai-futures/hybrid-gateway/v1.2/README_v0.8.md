# LYCHEETAH HYBRID GATEWAY v0.8 — fair comparator and isolated diagnostic

**18 October 2026 · Experimental local research prototype · no deployed customer validation**

This is a continuation of **v0.2 → v0.7**, not a new project. It retains source-grounded bitemporal knowledge, operator-authored clause contracts, optional neural extraction, coverage checks, append-only records, atomic SQLite transactions and reproducible evaluation utilities. v0.8 adds a **real SQL temporal comparator** and an **out-of-process CASCADE integration boundary**.

## Start here

```bash
python -m unittest discover -s tests -q          # 154 tests at packaging
python demo_sql_comparison.py                     # naive 2/4; SQL 4/4; gateway 4/4 (synthetic)
python demo_atomic.py                             # inherited atomic batch demo
python demo_temporal_audit.py                     # test-double CASCADE profiles
```

The SQL baseline is independently implemented with SQLite recursive queries and consumes the exact same *already-admitted* event history as the gateway. It does not call the gateway's query functions. On 30 generated histories × 40 seeded queries it matched the gateway's disposition, value and surviving claim IDs in **1,200 additional synthetic comparisons**. The original four-case test showed **no advantage over this fairer baseline**. This is a negative result we explicitly preserve.

## Optional genuine CASCADE execution (NOT run in build environment)

```bash
# Obtain and inspect an operator-trusted checkout of Lycheetah/Lycheetah-Framework.
# Ensure Python has numpy installed.
python demo_cascade_isolated.py --framework-root /path/to/Lycheetah-Framework
```

The subprocess worker checks the pinned upstream Git blob identity before importing the file and exposes diagnostic outputs only; no gateway pointer or approval authority is passed. Tests run a *toy engine* to exercise this boundary. The canonical file was inspected through the connected GitHub repo but **not downloaded/executed** in the Python build environment. The boundary is **not a sandbox**: child code retains its operating-system user's privileges.

## Evidence and limitations

- 154 passing tests = 138 inherited + 16 new, checked on one environment; this is **software regression testing**, not independent scientific validation.
- A four-case synthetic comparison is not model accuracy, human-reviewed gold, proof of novelty, or performance against published temporal RAG systems.
- No local inference endpoint, independently annotated corpus or canonical CASCADE execution was available for Cycle 8. No external effects, customer data, or live deployment.
- Inputs labelled `calibrated_weights` must come from an operator. We have **not** calibrated them. No CASCADE diagnostic can authorize a persistent write.
- The current approval flag is a trusted-caller boolean rather than authenticated reviewer identity.

Detailed findings: [`SESSION_REPORT_v0.8.md`](SESSION_REPORT_v0.8.md) · [`FAILURE_MUSEUM_v0.8.md`](FAILURE_MUSEUM_v0.8.md) · [`RESEARCH_HANDOFF_v0.8.md`](RESEARCH_HANDOFF_v0.8.md) · [`EXTERNAL_BENCHMARK_PLAN_v0.8.md`](EXTERNAL_BENCHMARK_PLAN_v0.8.md) · [`CANONICAL_SUBPROCESS_GUIDE_v0.8.md`](CANONICAL_SUBPROCESS_GUIDE_v0.8.md).

No branch has been pushed. Proposed destination remains `research/hybrid-intelligence-architecture` when the operator requests upload.

**Research claim:** This project's direction is an evidence-controlled, reversible neural–symbolic workflow—not a new temporal database, verified universal alignment system, or trained frontier model.
