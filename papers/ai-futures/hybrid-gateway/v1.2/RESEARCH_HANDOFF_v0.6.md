# Hybrid Gateway v0.6 — next-agent handoff

**KEEP THIS STATE. DO NOT RESTART.** Start from the v0.6 ZIP (the source, test suite, reports, prior lineage and SHA256 manifest).

## Working components

- `hybrid_gateway/core.py`: bitemporal ledger; newly supports replayable atomic in-memory `BATCH_ADMIT` (one event for N claims).
- `hybrid_gateway/durable.py`: SQLite-backed source and event store; `SQLiteLedger.commit_batch` revalidates trusted contracts and coverage, enforces optimistic head, and writes via one SQL transaction. No external actor can execute a side effect through this interface.
- `hybrid_gateway/coverage.py` + `contracts.py`: trusted operator annotation and expected clause coverage. Model output never authorizes itself.
- `hybrid_gateway/neural.py`: OpenAI-compatible model adapter and optional offline fixture test; no real model run.
- `hybrid_gateway/cascade_bridge.py`: read-only CASCADE diagnostic bridge, not yet run with canonical checkout.
- `hybrid_gateway/evaluation.py`: external-gold JSONL scorer; independent real-world study not run.

## Verification commands

```bash
python -m unittest discover -s tests -q            # 120 standard-library tests
python demo_atomic.py                                 # whole-batch SQLite demonstration
python generate_eval_fixture.py
python run_external_eval.py --gold fixtures/external_eval_example/SELF_AUTHORED_gold.jsonl --predictions fixtures/external_eval_example/SELF_AUTHORED_scripted_guesses.jsonl
python probe_live_model.py --model <real-local-model>  # requires locally running provider; NOT done here
python demo_cascade_canonical.py --framework-root <checkout>  # requires pinned canonical repo; NOT done here
```

## Highest-value Cycle 7

1. Freeze a *third-party* policy/document holdout (100+ if possible); obtain independent annotations, scope and effective-period adjudication. Use `EVALUATION_PROTOCOL_v0.6.md`. Keep gold out of prompts and development tuning. Report operational annotation/review time rather than mock timing.
2. Run an actual local model against those docs; save prediction JSONL. Compare raw LLM vs quote verification vs trusted contract vs coverage under identical model, data and review budgets.
3. Run the existing read-only bridge with the actual pinned `Lycheetah-Framework` commit. Probe historical conflicts/withdrawals. CASCADE must never silently rewrite ledger history or supply policy authority.
4. Add real identity proof for approvals and protected off-DB event head, then backup/restore and hostile-process threat-model validation.
5. If planning commercial use, measure annotation burden, task completion rate, latency and operator minutes. Beware event-chain replay cost for growing stores.

## Claims not established

No neural-symbolic model intelligence performance, external corpus generalization, production policy accuracy, deployment-grade identity security, arbitrary source semantics, distributed transactions or multi-node consensus. Passed local tests establish intentionally bounded behavior only.

**Branch proposal remains:** `research/hybrid-intelligence-architecture`. No push performed.
