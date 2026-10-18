# Hybrid Gateway v0.8 — next-agent handoff

Do **not** restart. The full v0.2–v0.8 lineage is included with original and new source. Do not push to GitHub without the operator requesting it.

## Reproduce now

```bash
python -m unittest discover -s tests -q     # 154 passing (as packaged)
python demo_sql_comparison.py                # 2/4 latest, 4/4 temporal SQL, 4/4 ledger
python demo_atomic.py                        # transactional v0.6 boundary intact
python demo_temporal_audit.py                # v0.7 fixture CASCADE boundary
```

For optional canonical CASCADE, provide the trusted checkout and NumPy:

```bash
python demo_cascade_isolated.py --framework-root /path/to/Lycheetah-Framework
```

If pin mismatch, stop, inspect the upstream diff, update pin only after the operator approves. A passing toy subprocess test does NOT establish canonical execution.

## Important corrected claim

The better SQLite baseline ties Lycheetah on the four fictional temporal lookups. Never again cite a 4/4 vs 2/4 comparison as an improvement over state-of-the-art bitemporal retrieval. It only showed the weak comparator ignored history. Temporal data models are established technology; the potential research contribution is the integrated human-authority, admission-evidence, temporal-review and read-only symbolic diagnostic workflow.

## Cycle 9 priority (in order)

1. On operator's trusted environment, run genuine pinned CASCADE engine out of process with several conflict/withdrawal profiles, save exact environment hashes and tests, compare with SQLite ledger disposition. Read-only only.
2. Freeze an **externally sourced**, independently annotated small temporal-document test split. Use the protocol in `EXTERNAL_BENCHMARK_PLAN_v0.8.md`. Document adjudication and disagreement, not just one model's answers.
3. Run a real local model via `probe_live_model.py`, then evaluate raw generation, simple quote verification, v0.4 contract, v0.5 coverage and latest full gateway under identical input and review budgets. Include a SQL-only control.
4. Measure time to review and false abstentions. A gate that merely abstains everywhere is not useful.
5. Treat identity/authentication, private memory, tamper-evident external anchors, genuine sandboxing and recovery as distinct production-hardening workstreams; none are delivered here.

## Non-claims

Not a trained hybrid LLM, not a model-weight editor, not a production guardrail, not externally validated, not a new temporal database, no actual canonical engine run on this cycle, and no GitHub branch created.
