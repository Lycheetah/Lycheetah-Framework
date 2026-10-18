# Cycle 8 research report — fair comparator, process boundary

**Date:** 2026-10-18 (Aotearoa NZ)  
**Status:** Runnable research prototype, synthetic results; no production use.  
**Lineage:** v0.7 archive preserved, 138 original tests + 16 new tests = **154 tests passed**.

## New experiment 1 — a genuinely better comparison

- Implemented an independently written SQLite query evaluator in `hybrid_gateway/sql_temporal_baseline.py` rather than using `HybridGateway.query` or a fake CASCADE engine.
- Both receive the **same pre-admitted structured events**, including effective and recorded times, withdrawals and explicit supersession edges. SQL recursively calculates visible survivors without calling gateway query utilities.
- On the four original synthetic v0.7 cases: deliberately naive latest-known 2/4; independent temporal SQL 4/4; HybridGateway 4/4. This **removes** the earlier apparent temporal-query advantage against a weak baseline. It is not an AI extraction or product win.
- 30 seeded artificial histories × 40 randomized queries = **1,200 additional differential queries** agreeing in disposition, value and surviving citation IDs. Also tested tenant and scope separation, expired claims, late-known updates, same-value citations, batch admission and transitive suppression across a withdrawn intermediate.
- This confirms agreement over generated legal cases; two implementations could share an undetected semantic flaw. Gold remains self-authored.

## New experiment 2 — read-only CASCADE in a child process

- Added `hybrid_gateway/isolated_cascade.py` + `_cascade_worker.py` and optional `demo_cascade_isolated.py`.
- The parent extracts only relevant claim IDs and values plus validated operator-supplied weight triples, then asks an isolated Python interpreter (`-I`) to execute a separately pinned local CASCADE file.
- Eight tests use a **toy substitute only** to verify pin rejection, timeout, child failure, missing weights, empty citations, diagnostic shape and that child modifications to `os.environ` don't mutate the parent. They do not prove sandboxing or canonical engine behavior.
- The original 138 tests remain present; old in-process adapter retained as historical research, but the new subprocess path should be preferred for diagnostics from external code.
- The actual canonical CASCADE checkout **was not available** in the runtime. Consequently a canonical subprocess execution has **not** been observed.

## Model and benchmark availability

A probe of common local inference endpoints (127.0.0.1 ports 11434, 1234 and 8000) found no available service. No live model evaluation was performed. This environment cannot directly download the outside corpus into Python. Current public research offers fairer future baselines: TDBench (ICLR 2026) and ChronoQA (Scientific Data 2025), see `EXTERNAL_BENCHMARK_PLAN_v0.8.md`.

## What is and is not established

**Established internally:** event-to-SQL temporal query agreement on explicit generated cases; separate process packet handoff and failure handling; identical inherited ledger behavior; tests passing locally.  
**Not established:** a unique advantage over conventional temporal SQL; independently labelled extraction accuracy; calibrated CASCADE knowledge weights; canonical execution; prompt-injection resistance; a hostile-code sandbox; authenticated review; deployment or customer value.

**Guiding result:** Our novelty hypothesis must shift from *temporal querying outperforms retrieval* to whether **end-to-end, reversible, evidence-governed neural–symbolic workflows** produce net user benefit beyond existing retrieval and review systems under equal costs.
