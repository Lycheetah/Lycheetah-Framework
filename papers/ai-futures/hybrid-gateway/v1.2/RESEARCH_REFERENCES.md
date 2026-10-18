# Research references and positioning (checked October 2026)

## Existing Lycheetah sources

- CASCADE's admitted limitations: <https://github.com/Lycheetah/Lycheetah-Framework/blob/master/papers/LIMITATIONS_AND_FUTURE.md>. Synthetic trials do not imply production generalization; contradiction detection is not semantic, and core does not edit weights.
- CASCADE's proposed hybrid plan and related work: <https://github.com/Lycheetah/Lycheetah-Framework/blob/master/papers/RELATED_WORK_EXPANDED.md>. Historical prospect, **not** proof of field-wide novelty in 2026.
- Reference code: <https://github.com/Lycheetah/Lycheetah-Framework/blob/master/12_IMPLEMENTATIONS/core/cascade_engine.py>. Its `contradicts` proxy cannot be trusted across time/scope.
- Assurance Runtime: <https://github.com/Lycheetah/Lycheetah-Framework/tree/master/34_ASSURANCE_RUNTIME>. Already experimental scaffold; existing integration boundaries must be preserved.
- README evidence discipline: <https://github.com/Lycheetah/Lycheetah-Framework/blob/master/README.md>. Independent failure evidence narrows allowed claims.

## External comparators, not origin claims

- Snodgrass et al. (1996), *Semantics of time-varying information*, Information Systems. The distinction between valid time and transaction time predates Lycheetah. <https://doi.org/10.1016/0306-4379(96)00017-8>
- Ouyang et al. (2025), *HoH: A Dynamic Benchmark for Evaluating the Impact of Outdated Information on Retrieval-Augmented Generation*, ACL. Demonstrates failures from outdated retrieved information and provides a relevant future benchmark. <https://aclanthology.org/2025.acl-long.301/>
- Huwiler, Stockinger, Fürst (2025), *VersionRAG: Version-Aware Retrieval-Augmented Generation for Evolving Documents* (preprint), relevant strong future baseline. <https://arxiv.org/abs/2510.08109>
- Gupta et al. (2024), *Model Editing at Scale leads to Gradual and Catastrophic Forgetting*, ACL Findings. Motivates keeping weight editing optional and rigorously evaluated. <https://aclanthology.org/2024.findings-acl.902/>

**Positioning:** This checkpoint aims to be a small, auditable *composition* of prior ideas and existing Lycheetah concepts. Bitemporal records, source provenance, guarded actions and version-aware retrieval are not novel as independent methods. Any distinctive effectiveness must be established by comparison, not prose.

## Research cycle 3 references checked 2026-10-18

- Gupta, Rao & Anumanchipalli (2024), *Model Editing at Scale leads to Gradual and Catastrophic Forgetting*, Findings of ACL 2024. https://aclanthology.org/2024.findings-acl.902/ — motivates reversible external knowledge stores before high-frequency neural model edits; does **not** evaluate this gateway.
- Huwiler, Stockinger & Fürst (2025), *VersionRAG: Version-Aware Retrieval-Augmented Generation for Evolving Documents*, https://arxiv.org/abs/2510.08109 — relevant strong temporal retrieval research comparator; benchmarks should not be compared directly to this project's 22 fictional cases.
- Ollama docs, *OpenAI compatibility*, https://github.com/ollama/ollama/blob/main/docs/api/openai-compatibility.mdx — `/v1/chat/completions` interface for local model servers (verify provider/model-specific schema support).
- Ollama docs, *Structured Outputs*, https://github.com/ollama/ollama/blob/main/docs/capabilities/structured-outputs.mdx — JSON-schema constrained inference; structured format is not entailment verification.
- OpenAI API, *Structured model outputs*, https://developers.openai.com/api/docs/guides/structured-outputs — API-format expectations; model-dependent availability and behavior.

## Research cycle 4 (verified 2026-10-18)

- Xing, Baldwin & Lau (2025), *Evaluating Evidence Attribution in Generated Fact Checking Explanations*, NAACL 2025. <https://aclanthology.org/2025.naacl-long.282/>. Model-generated explanations can contain inaccurate evidence attribution. Distinct problem from clause-authority stamping; motivates testing source alignment.
- Metropolitansky & Larson (2025), *Towards Effective Extraction and Evaluation of Factual Claims*, ACL 2025. <https://aclanthology.org/2025.acl-long.348/>. Ambiguity and correct interpretation of source text are active research problems, not solved by exact-string inclusion.
- Filice et al. (2025), *Generate but Verify: Answering with Faithfulness in RAG-based Question Answering*, IJCNLP 2025. <https://aclanthology.org/2025.ijcnlp-long.56/>. Motivation for explicit verification and abstention.
- Huwiler et al., *VersionRAG: Version-Aware Retrieval-Augmented Generation for Evolving Documents*, v1 October 2025. <https://arxiv.org/abs/2510.08109>. Competitive retrieval benchmark that we **did not run**.

Novelty note: source span attribution, policy-as-data, claim parsing, bitemporal history, review gates and version-aware retrieval are existing ideas; this is an unvalidated composition and a bounded lab study.

## Cycle 6 storage and evaluation references (2026-10-18)

- SQLite transaction control / `BEGIN IMMEDIATE`: https://www.sqlite.org/lang_transaction.html
- SQLite atomic commit explanation: https://www.sqlite.org/atomiccommit.html
- SQLite transactional behavior and limitations: https://www.sqlite.org/transactional.html
- The 14-case v0.6 scoring sample is explicitly self-authored and does not constitute a cited external dataset.
