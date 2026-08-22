# Industry Crosswalk — Assurance Runtime v0.1

**Status:** `[SCAFFOLD]` — implementation-oriented mapping, not certification or legal advice.

**Reviewed:** 2026-08-22

## Purpose

This crosswalk keeps the runtime pointed at real integration surfaces. A row means “the Lycheetah feature can provide evidence relevant to this concern.” It does not mean the runtime satisfies an entire standard, control family, law, or certification scheme.

| External surface | Relevant concern | Lycheetah v0.1 response | Explicit gap |
|---|---|---|---|
| NIST AI RMF + NIST AI 600-1 GenAI Profile | Govern, map, measure, and manage risk across the AI lifecycle | Versioned policy identity, runtime findings, receipts, limitations, review decisions, and labelled policy-regression metrics | No organization-wide risk programme, impact assessment, representative benchmark, or NIST conformity assessment |
| OWASP Top 10 for Agentic Applications 2026 | Goal hijacking, tool misuse, identity/privilege abuse, memory poisoning, cascading failures | Input/output review signals, tool allow/deny boundaries, scope checks, approval pause, trace lineage | No sandbox, identity provider, memory isolation, or prompt-injection proof |
| OpenAI Agents SDK | Input/output/tool guardrails, resumable human approvals, trace-driven evals | Matching event phases and three-way disposition; `REVIEW` intended to pause application flow; provider-neutral labelled regression reports can join an external eval dataset | No claim that a receipt automatically wires itself into every SDK boundary or that internal fixtures represent production traffic |
| Model Context Protocol 2026-07-28 | Consent, user control, tool execution, authorization, secure transports | Official Python SDK 2.x server exposes typed pre-execution checks and structured receipts; approval is deliberately absent from model-visible arguments | Does not implement OAuth, token audience validation, per-client consent, SSRF defense, or production transport security |
| OpenTelemetry GenAI semantic conventions | Vendor-neutral spans, events, model/tool/agent observability | Dependency-free bridge adds a verified, privacy-minimised `lycheetah.assurance.decision` event to an existing span | Uses custom `lycheetah.assurance.*` attributes, not standardized `gen_ai.*`; no collector/exporter or convention-conformity claim |
| Open Policy Agent | Policy-as-code decisions and decision logs | Policy digest, decision ID, compact findings, offline verification | Not a Rego engine, bundle service, distributed policy control plane, or OPA replacement |
| in-toto Attestation Framework | Statements binding subjects to typed predicates; authenticated envelopes | Optional Statement v1-shaped export with subject digest and receipt predicate | No DSSE/public-key signing, transparency log, or in-toto verification claim |

## Primary sources

- NIST, [Artificial Intelligence Risk Management Framework: Generative Artificial Intelligence Profile](https://www.nist.gov/publications/artificial-intelligence-risk-management-framework-generative-artificial-intelligence), NIST AI 600-1.
- OWASP GenAI Security Project, [Top 10 for Agentic Applications for 2026](https://genai.owasp.org/resource/owasp-top-10-for-agentic-applications-for-2026/).
- OpenAI, [Guardrails and human review](https://developers.openai.com/api/docs/guides/agents/guardrails-approvals), [Evaluate agent workflows](https://developers.openai.com/api/docs/guides/agent-evals), and [Integrations and observability](https://developers.openai.com/api/docs/guides/agents/integrations-observability).
- Model Context Protocol, [2026-07-28 Specification](https://modelcontextprotocol.io/specification/2026-07-28) and [Security Best Practices](https://modelcontextprotocol.io/docs/2026-07-28/tutorials/security/security_best_practices).
- OpenTelemetry, [GenAI Semantic Conventions repository](https://github.com/open-telemetry/semantic-conventions-genai).
- Open Policy Agent, [Decision Logs](https://www.openpolicyagent.org/docs/management-decision-logs).
- in-toto, [Attestation Framework Specification](https://github.com/in-toto/attestation/blob/main/spec/README.md) and [Statement v1](https://github.com/in-toto/attestation/blob/main/spec/v1/statement.md).

## Design consequences

1. **Guard every side-effect boundary.** Agent-level input/output checks do not cover every nested tool call.
2. **Preserve human control.** A review decision must pause and resume the same application operation where possible.
3. **Do not put secrets in receipts by default.** MCP and agent traces may contain tool arguments, tokens, or user data.
4. **Separate trace from decision artifact.** A trace explains the path; a receipt records the assurance decision.
5. **Use exact scope and audience controls outside this runtime.** Text heuristics cannot substitute for authorization.
6. **Make evaluation repeatable.** Receipt IDs and policy digests should join runtime traces to offline eval datasets.

⊚ Sol ∴ P∧H∧B ∴ Albedo
