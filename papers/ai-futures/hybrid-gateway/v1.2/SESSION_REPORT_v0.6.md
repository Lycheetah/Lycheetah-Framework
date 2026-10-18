# Cycle 6 research report — Lycheetah Hybrid Gateway v0.6

**Date:** 2026-10-18, NZ · **Milestone:** whole-batch local revision + external-dataset-ready scorer · **GitHub:** not pushed.

## Origin

Continues the verified v0.5 gateway code and 95-test suite. v0.5 could only commit reviewed claims individually; after admitting one claim, other stages became stale. This was safe against stale mutation but allowed partially applied business policy changes. v0.5 also lacked a standard interface for scoring extraction on separately annotated outside documents.

## Changes

- `core.py`: additive `HybridGateway.ingest_batch` shadow preflight, dependency order and single `BATCH_ADMIT` hash-chain event, with matching deterministic restoration path. Existing single `ADMIT` and `WITHDRAW` semantics retained.
- `durable.py`: new SQLite-backed event store; operator sources persisted separately and validated by digest; strict stage/plan/receipt validation under `BEGIN IMMEDIATE` and one transaction. Conflicting writers, replay attempts and altered sources fail locally.
- `evaluation.py` + `run_external_eval.py`: exact ID + digest-locked JSONL evaluation. Metrics include precision, recall, F1, wrong-field/scope, document exactness, positive coverage, correct negative abstention and reviewer minutes. Predictions and gold loaded from distinct files.
- `generate_eval_fixture.py`: explicitly fictional 14-case scorer smoke, including negative documents, wrong scopes, duplicates and partial outputs. `EVALUATION_PROTOCOL_v0.6.md` documents the proposed real measurement and falsifiers.
- New tests and replayable demo; v0.2–v0.5 historical reports, prior source and failure museums preserved.

## Verification

- `python -m unittest discover -s tests -q`: **120/120** pass, with **95 inherited + 25 new**.
- `python demo_atomic.py`: incomplete batch refused; complete batch requires separate approval, applies two claims in one event, stale receipt refused, restart rebuilds the same two claims and returns the historically supported 14-day answer.
- SQLite intentional insert abort: atomic transaction rolls back, with no recorded event or claim. Two concurrent writers with same review snapshot: one `ALLOW`, one `REVIEW`. Abrupt child-process exit before commit: pending SQL insert not present after restart.
- Hash chain event tampering detected on replay; externally pinned head mismatch rejected.
- Fictional scoring sample: scripted fixture precision **0.60**, recall **0.667**, F1 **0.632** on 14 self-authored cases (6 TP, 4 FP, 3 FN); all-abstain fixture recall **0**, correct negative abstention **1.0**. **Not live model scores, not external results, not independent validation.**

## What is enabled now

An integrator can explore an end-to-end *offline* workflow in which model-shaped claim proposals become a fully checked review batch, and all members are admitted together or not at all into one SQLite-backed, replayable historical ledger. An evaluation runner can score real third-party annotations once they are provided. No production integration, real-customer data, independent labeling or real neural inference was performed.

## What remains unverified

1. Real provider inference on held-out third-party data; compare with version-aware retrieval and standard LLM baselines.
2. Independent ground-truth annotations of scope, semantics, effective dates and true absence; reviewer effort and annotation time.
3. Authentic reviewer identity, protected external head anchoring, no model access to privileged handles.
4. Canonical Lycheetah CASCADE engine checkout and real execution against gateway snapshots. No Π weights are inferred from quotes.
5. Crash/power-loss characteristics beyond SQLite documented transaction semantics, multi-tenant stress, backups, restore drills, throughput and multi-service effects.

### Relevant conventional database baseline

SQLite documents `BEGIN IMMEDIATE` and transaction control at https://www.sqlite.org/lang_transaction.html, and atomic commit semantics at https://www.sqlite.org/atomiccommit.html. This work uses SQLite rather than claiming a novel transaction engine.

**Evidence category: local tested software contract and unverified research hypothesis.**
