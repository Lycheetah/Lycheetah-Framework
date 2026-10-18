# Hybrid Gateway v0.5 — next-agent handoff

**Do not restart this project.** Extend this archive or a GitHub branch containing it. Prior v0.1–v0.4 lineage and reports are preserved.

## State at handoff

- Main location: `hybrid_gateway/coverage.py` (operator-plan completeness and false-omission/duplicate review).
- Supporting modules: `core.py` (temporal ledger), `neural.py` (provider adapter), `contracts.py` (exact source authority), `cascade_bridge.py` (diagnostic only).
- Runnable scripts: `demo_coverage.py`, `run_coverage_eval.py`, `probe_live_model.py`.
- Verified: 95/95 standard-library unit tests; 32 author-constructed protocol cases.
- NOT verified: actual neural inference, original CASCADE engine execution in this environment, external benchmarks or production security.
- No remote repo write was performed. Proposed path: `research/hybrid-intelligence/`; proposed branch: `research/hybrid-intelligence-architecture`.

## Highest-value next experiment

1. Install/connect one real local OpenAI-compatible language model; run `probe_live_model.py --model <model>` first. Freeze prompt, engine/version, parameter settings, document corpus and ground-truth before inference, then record *positive extraction* and *correct abstention* separately. Real model scores must not reuse mock scores.
2. Expand to at least 100 documents that were *not written to match the validator*. Include missing fields, exceptions, conditionals, periods, version conflicts, bilingual passages, misleading instructions, and source ambiguity. Use independent annotators; if feasible, publish anonymized examples and adjudication rules.
3. Compare four conditions on the same corpus: raw structured LLM extraction, LLM + quote check, LLM + v0.4 clause binding, LLM + v0.5 coverage audit. Report precision, recall, abstention, wrong-field rate, reviewer minutes, annotations per page, and **coverage on answerable cases**; a fully abstaining model must not appear good.
4. Run the optional `demo_cascade_canonical.py` with a pinned actual checkout of `Lycheetah-Framework`. Record exact repo commit SHA and any errors; do not vendor undocumented adaptations. Then add checks that CASCADE diagnostics cannot alter ledger results for conflict/withdrawn scenarios.
5. Add authenticated, durable, atomic batch review before using any real customer's documents or actions. Existing approval booleans aren't signatures; receipt hashes aren't a security boundary.

## Never claim

- “Neural-symbolic integration validated” without live provider and canonical engine tests.
- “100% accuracy” from conformance to the same contracts that define the labels.
- “No hallucinations” on any natural-language documents.
- “Safe production gateway” without identity, durable persistence, transactions, sandbox/tool guard and adversarial audits.

The next measurement worth celebrating is one that could genuinely falsify our hypothesis.
