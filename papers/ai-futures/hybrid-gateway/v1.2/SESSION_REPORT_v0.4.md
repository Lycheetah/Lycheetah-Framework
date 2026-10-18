# Lycheetah Hybrid Gateway — Cycle 4 verification report

**Date:** 2026-10-18. **Status:** offline Python implementation and author-built regression checks. **No actual live model, genuine CASCADE execution, production deployment, authenticated reviewer, real external customer data, or GitHub commit.**

## Question and implementation

A model can return an authentic quote that supports the wrong field, from an example, a different policy scope, or an invented effective date. We added a new conservative `TrustedClause` / `TrustedContractRegistry` / `ContractedHybridPipeline` path that verifies the **operator-selected exact clause, subject, predicate, scope, effective time and authorized revision edge** before staging and again before committing. Malformed batches fail as a whole; no staged item modifies the ledger.

The first supported grammars cover `Refunds allowed within X days.`, `Online orders: refunds within X days.`, and `Loyalty members earn X points per order.`. Unknown natural language must be reviewed rather than auto-admitted. The repository's old core/neural/cascade modules remain intact.

## Executed and observed

- `python -m unittest discover -s tests -q` → **71 tests, all passed**, on this research container.
- `python demo_contracts.py` → refused 60-day example; staged current 14-day policy; without approval returned `REVIEW`; caller approval admitted 14; historical `known_at` earlier than admission abstained; later query answered 14; anchored hash chain checked true.
- `python run_contract_eval.py` → **33 author-generated cases**, nine authorized; lexical baseline 21 wrong admissions, narrow regex baseline nine wrong admissions and six missed authorized cases, contracted path no mismatches relative to its own labels.
- v0.3 inherited **54 tests** continued passing. No original code removed.
- `demo_cascade_canonical.py` produced but **NOT RUN** because canonical original checkout was not present. Its example weights are placeholders; no CASCADE empirical claim is made.
- v0.3's real-model inference adapter remains optional, no actual model used this cycle.

## Research interpretation

**Established:** In this controlled fixture, explicit human-selected clause metadata prevents certain quote-field, wrong-scope, example-only and effective-date substitutions that pure string containment permits. Rechecking a whole source identity and the validator at finality catches two local integration regressions.

**Not established:** Independent model extraction precision, calibrated truth/contradiction estimates, semantic coverage, cost-effectiveness versus manual tagging, robust security against malicious application code, benchmark superiority over temporal RAG, or successful integration of canonical CASCADE.

## Conventional comparator and literature

VersionRAG (Huwiler et al., 2025) explicitly tracks evolving versions, and reports 90% on its own VersionQA benchmark; **we did not run VersionQA**. Xing, Baldwin & Lau (NAACL 2025) show evidence attribution in language models is not always accurate. Claimify (ACL 2025) makes ambiguity-aware claim extraction central. These motivate evidence alignment and abstention, not a novelty claim for clause contracts.

See `RESEARCH_REFERENCES.md` for verified sources and `FAILURE_MUSEUM_v0.4.md` for retained limitations.

## Next external experiment

Build 100+ independently labelled policy clauses with authentic scope/date changes, labelled decoys and novel paraphrases; split by **source document**, not just claim. Measure model-supported precision/recall, operator annotation minutes, approval burden, false admission, false rejection, wrong-time/scope answers, and citation validity. Add a genuine model and canonical CASCADE smoke only when corresponding source/version and consent are available. Do not compare 33 conformance probes with VersionRAG's 100-question benchmark.
