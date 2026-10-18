# Cycle 8 — External benchmark design, without invented results

The v0.8 package has **not** run external neural inference, fetched an independent corpus into its test runtime, or measured outside annotators. Do not promote deterministic SQL agreement into model accuracy. Operator-labelled author-constructed cases are not independently adjudicated gold.

## Public research to compare with

- **TDBench (ICLR 2026)**: Soyeon Kim et al., *Harnessing Temporal Databases for Systematic Evaluation of Factual Time-Sensitive Question-Answering in LLMs*. https://proceedings.iclr.cc/paper_files/paper/2026/hash/2cbeff05cd646fcc09f6c3c48ba56f74-Abstract-Conference.html and https://github.com/ssoy0701/tdbench. The paper includes temporal SQL and a time-reference accuracy metric. Import/align licensing and dataset schemas before evaluation; the temporal SQL baseline in v0.8 is independently written and is **not** the TDBench reference implementation.
- **ChronoQA (Scientific Data, November 2025)**: Chen et al., *A Question Answering Dataset for Temporal-Sensitive Retrieval-Augmented Generation*, https://www.nature.com/articles/s41597-025-06098-y and https://github.com/czy1999/ChronoQA. Chinese multi-document QA questions with sourced news fragments; does not directly provide operator-approved knowledge-time/effective-time truth contracts in Lycheetah's schema. Do not treat automatic conversion as neutral.

## Proposed study protocol (not executed)

1. Pre-register evaluation questions and gold rules before looking at model output. Use externally sourced documents with at least two annotators and adjudication for field, tenant/scope, effective interval, observed/admitted time, supersession and withdrawal. Track uncertainty/ambiguous labels separately.
2. Freeze hashes of documents, golden annotations, model configuration, prompt, retrieval index and code commit; keep the independent test set out of hyperparameter selection.
3. Compare, on the **same documents and time budget**: raw model, a quote-only extractor, contract+coverage gateway, version-aware SQL/document retriever, and (where appropriate) a published version-aware RAG baseline. SQL itself is a strong comparator for already-structured facts but cannot substitute for extraction.
4. Stratify outcomes: supported correct, wrong value, wrong field, wrong scope, temporal leak, failure to abstain, unjustified abstention, missed required extraction, conflicting evidence correctly escalated, stale approval and source/provenance errors.
5. Report document-level and claim-level exact match, precision, recall, calibration (if provided), time-reference accuracy, abstention coverage, reviewer correction minutes and end-to-end cost/latency. Include all-abstain and SQL-only baselines.
6. No meaningful product claim until a frozen outside corpus and a real model produce measured results. Do not compare the gateway's *permitted* answers against its own ledger as external truth.

## Immediate evaluation limitation

v0.8 compares two independent query algorithms on identical admitted structured events. It evaluates neither source truthfulness, neural semantic extraction, nor whether CASCADE helps users. The actual value hypothesis is the combined workflow from proposal to verified, reviewed, reversible knowledge—not exclusive ownership of bitemporal databases or temporal reasoning.
