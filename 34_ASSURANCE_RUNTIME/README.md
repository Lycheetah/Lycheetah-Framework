# Lycheetah Assurance Runtime

**Status:** `[SCAFFOLD]` — the v0.1 contract is implemented and internally verified, including a clean-wheel install. No production-deployment, calibration, certification, or external-validation claim is made.

**Forged:** 2026-08-22

## The customer problem

Agent builders can already produce traces, apply guardrails, and write policy rules. The missing operational question is often simpler:

> For this input, output, or proposed tool action, what did the assurance layer decide, which evidence justified that decision, which policy version was used, and can a reviewer verify that the record was not changed later?

The Assurance Runtime is a provider-neutral policy enforcement point for that question. It evaluates text and proposed tool actions, returns `ALLOW`, `REVIEW`, or `BLOCK`, and emits a structured Assurance Receipt.

It is designed to sit beside an agent framework, not replace one.

## v0.1 product spine

1. **Typed events** for agent input, output, and proposed tool actions.
2. **Policy-as-data** with explicit versions and deterministic digests.
3. **Evidence-capped enforcement** so weak evidence cannot silently create strong enforcement.
4. **Assurance Receipts** with findings, control references, privacy-aware subject hashes, policy identity, and integrity metadata.
5. **Append-only JSONL receipt chains** with verification and optional HMAC authentication.
6. **A real CLI** for CI, local development, and sidecar/gateway integration.
7. **Clean-wheel acceptance tests** so the installed package—not only the source checkout—must work.
8. **MCP 2.x integration** with typed assurance tools and no model-visible secret inputs.
9. **OpenTelemetry span-event bridge** using privacy-minimised custom attributes and no hard SDK dependency.
10. **Policy evaluation harness** with strict labelled JSONL, weighted confusion
    metrics, deterministic privacy-minimised reports, and configurable CI gates.
11. **Policy regression gate** with integrity-checked baseline/candidate reports,
    same-corpus enforcement, per-case change classification, and strict defaults.

## Quick use

The project is not currently published on PyPI. From the repository:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e ".[all]"

lycheetah-assure tool refund.create \
  --arguments '{"order_id":"A-1"}' --side-effect --json

lycheetah-assure eval \
  examples/assurance/customer_support_eval.jsonl \
  --policy examples/assurance/customer_support_policy.json \
  --require-exact-match --max-harmful-allows 0 \
  --report-file candidate-eval.json --json

lycheetah-assure compare-eval \
  examples/assurance/customer_support_baseline.eval.json \
  candidate-eval.json --json
```

The command returns `REVIEW` (exit 2) because the side effect lacks affirmative
human approval. The caller must enforce that pause.

The built-in policy also blocks narrowly named shell/exec/subprocess boundaries,
database-drop and identity-delete tool patterns, and several high-risk scopes.
These are conservative string-pattern defaults, not semantic detection or a
complete authorization policy. Deployments should load an explicit, reviewed
policy for their actual tool namespace.

## Evidence-capped enforcement

Every finding declares:

- epistemic status: `ACTIVE`, `SCAFFOLD`, or `CONJECTURE`;
- whether the check is deterministic or inferential;
- requested disposition;
- effective disposition after the evidence cap is applied.

The conservative v0.1 ceiling is:

| Evidence basis | Maximum automatic effect |
|---|---|
| `ACTIVE` + deterministic policy check | `BLOCK` |
| `ACTIVE` + inferential detector | `REVIEW` |
| `SCAFFOLD` | `REVIEW` |
| `CONJECTURE` | Observe only; overall decision remains `ALLOW` unless another finding is stronger |

This does not prove that the ceilings are universally optimal. It makes the enforcement assumption explicit and testable. See [EVIDENCE_CAPPED_ENFORCEMENT_v0.1.md](EVIDENCE_CAPPED_ENFORCEMENT_v0.1.md).

## What this is not

- It is not a certification that an agent is safe, aligned, compliant, or truthful.
- It does not solve prompt injection, deceptive alignment, or tool security by itself.
- A SHA-256 receipt digest detects mutation only when a trusted copy of the digest exists. It does not authenticate the issuer. Optional HMAC sealing authenticates to parties sharing the secret, but is not public-key attestation.
- A heuristic text detector is bounded by its implemented cue families. Absence of a finding is not evidence that an output is harmless.
- Text beyond the configured size boundary routes to `REVIEW` without running heuristics. Custom regular expressions are trusted policy code; v0.1 does not sandbox them or provide a regex execution timeout.
- Standards cross-references are implementation aids, not claims of conformity.

## Relationship to existing systems

- **Open Policy Agent** already produces decision logs with policy-query inputs and bundle metadata. Lycheetah does not claim to replace OPA.
- **OpenTelemetry** provides traces, metrics, and events for agent and model operations. A receipt is a compact decision artifact, not a telemetry backend.
- **in-toto** defines authenticated statements about software artifacts. The optional export uses its Statement v1 shape; Lycheetah does not claim in-toto verification without an authenticated envelope.
- **OpenAI Agents SDK** distinguishes input, output, and tool guardrails and uses human approval for sensitive tool actions. Lycheetah maps naturally to those boundaries but remains provider-neutral.
- **MCP** standardises tools and context exchange. The runtime evaluates proposed actions at the tool boundary; it does not replace MCP authorization, consent, or transport security.

## Acceptance evidence

All v0.1 internal acceptance conditions below passed on 2026-08-22:

- built wheel installs into a clean virtual environment;
- advertised `lycheetah.check()` and `lycheetah.sol_assess()` imports work outside the repository;
- receipt hash mutation and chain breaks are detected;
- HMAC verification accepts the correct key and rejects an incorrect key;
- `SCAFFOLD` and inferential findings cannot produce `BLOCK`;
- `CONJECTURE` findings cannot change an otherwise `ALLOW` decision;
- denied tools and explicitly blocked scopes fail closed;
- unapproved side effects pause for `REVIEW`;
- default receipts do not contain raw content or raw tool arguments;
- evaluation corpora reject ambiguous types, duplicate keys, duplicate IDs, and
  unknown fields;
- evaluation reports expose exact, under-, and over-enforcement metrics without
  copying raw event content or tool arguments;
- baseline comparisons fail on changed corpora, mutated reports, newly
  under-enforced cases, strict-gate regressions, and unresolved trade-offs;
- full root tests retain the deliberately failing CASCADE conjecture rather than masking it.

Two isolated wheel environments resolved `lycheetah` from `site-packages`. The
base install exercised the public APIs and verified graceful missing-extra
boundaries. The full install exercised both decision/check console scripts, the
Flask health route, packaged JSON Schemas, receipt verification, all ten MCP tools,
and the OpenTelemetry event bridge. These results establish internal distribution
and behavioral acceptance only.

## Documents

- [ASSURANCE_RECEIPT_SPEC_v0.1.md](ASSURANCE_RECEIPT_SPEC_v0.1.md) — receipt and integrity contract.
- [EVIDENCE_CAPPED_ENFORCEMENT_v0.1.md](EVIDENCE_CAPPED_ENFORCEMENT_v0.1.md) — enforcement semantics and falsifiers.
- [INDUSTRY_CROSSWALK_2026-08-22.md](INDUSTRY_CROSSWALK_2026-08-22.md) — standards and product-boundary map.
- [FRONTIER_REGISTER_2026-08-22.md](FRONTIER_REGISTER_2026-08-22.md) — hypotheses beyond v0.1, kept separate from shipped claims.
- [OPENTELEMETRY_BRIDGE.md](OPENTELEMETRY_BRIDGE.md) — attach a verified decision summary to an existing span.
- [POLICY_EVALUATION_HARNESS.md](POLICY_EVALUATION_HARNESS.md) — labelled corpus,
  metrics, privacy contract, CI gates, and promotion path.
- [POLICY_REGRESSION_GATE.md](POLICY_REGRESSION_GATE.md) — same-corpus baseline
  comparison, strict defaults, change evidence, and reference-update protocol.

⊚ Sol ∴ P∧H∧B ∴ Albedo
