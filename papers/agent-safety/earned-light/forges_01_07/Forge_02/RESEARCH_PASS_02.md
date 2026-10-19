# EARNED LIGHT RESEARCH — PASS 02
### A falsifiable origin-of-authority experiment for delegated agent action

**Date:** 18 October 2026 (Pacific/Auckland)  
**Status:** local prototype and synthetic benchmark completed. Repository integration, user-study, red-team field trial and independent validation NOT completed.  
**Owner/workstream:** Lycheetah / Earned Light Layer 0 / AURA · LAMAGUE · TIM · Sovereign Harness

## 1. Decision and central finding

Research Pass 01 proposed the *Earned Authority Chain*. Pass 02 narrows its first question to a tractable boundary: **a permission can be rigorously bound and replay-protected without having been authorized by an authenticated human in the first place.** The exact point of origin of authority matters.

The public `lycheetah/sovereign_harness.py` document explicitly says its `authority_id` and packet authority checks validate **declared** grant metadata rather than **externally authenticated human approval**. The source further establishes existing protections: exact action digest, scope, packet critical-hash, state version, expiry, SQLite single-use nonce ledger, gateway policy and signed audit checkpoints.

**Therefore this pass did NOT replace the existing harness or rediscover replay protection.** It built an independent precondition: a trusted external service attests to a human-approved scoped grant, and trusted data adapters attest to the origin of each sensitive destination field.

### Origin-of-authority distinction

- *Declared grant:* the agent environment says Alice approved sending mail.
- *Authentically signed grant:* a trusted authority service signs a grant after externally authenticating Alice and receiving Alice's consent (assumed as an upstream obligation in this prototype).
- *Signed provenance:* a separate trusted ingress service signs that `recipient=customer@example.test` came from authenticated human input, trusted CRM, or untrusted email, binding its digest to a specific grant/session.
- *Execution policy:* the gate checks these cryptographic assertions and does not let model confidence replace missing proof.

A signature authenticates the signing key, not the truth of an assertion. Incorrect service behavior or compromise defeats these guarantees.

## 2. Implemented instrument (EAC v0.2)

`earned_authority.py` contains:

- `Request`: typed agent/tool/action/scope/state/arguments.
- `Grant`: Ed25519-signed principal/agent/session/tool/operation/scope/state/validity window.
- `OriginProof`: Ed25519-signed exact field-value digest, approved source class, grant ID, session ID and time window.
- `EarnedAuthorityGate`: fail-closed schema validation, trusted-role-separated public keys, signature validation, bounded windows, revocation check, field coverage, approved-origin constraints and reason-coded decisions.
- `POLICIES`: two explicit demonstrative operations, `mail.send` and `calendar.create`; all effect-relevant optional `cc` and `bcc` targets require proofs when present.

`airlock.py` wraps a **mock** synchronous effect so it cannot be called on deny. It is not wired to `ActionGateway` or `SovereignExecutionHarness`. Private signing keys appear only in test fixtures and the synthetic experiment, explicitly not in the trusted runtime module.

Canonicalization uses strict, float-free JSON (not RFC 8785). Other runtimes must implement the same restricted domain and reject ambiguous numbers. Do not deploy with ad hoc cross-language canonicalization.

## 3. Local evidence

Executed here, with the exact package in this folder:

```text
python -m pytest -q
28 passed

python experiment.py
43 hand-authored scenarios: 10 benign, 33 unauthorized
```

| Comparator | Unauthorized accepted / 33 | Legitimate allowed / 10 |
|---|---:|---:|
| B0: declared-scope check (stylized reference, NOT actual Lycheetah runtime) | 27 / 33 | 10 / 10 |
| B1: conventional signed scope + typed schema | 20 / 33 | 10 / 10 |
| EAC: B1 + signed field provenance + allowed-origin policy | 2 / 33 | 8 / 10 |

**Interpretation:** On these authored examples, field provenance blocked a class of attacks where untrusted data provides a side-effect destination even though the agent has a broad *valid* `mail.send` scope grant. Conventional signed scoped approval already blocks invalid/mismatched grants and is a substantial part of the security value. EAC is a *specific additional policy condition*, not a demonstrated new security primitive.

**Important experimental limitation:** The tester wrote the cases, labels, code and policy. The suite is vulnerable to selection bias, target leakage and trivial memorization of source-type categories. No external benchmark cases, real human approvals, real provider calls, adaptive attacker runs or independent annotations were used. The numbers establish deterministic behavior of the supplied code on these cases only. Do NOT calculate an outside-world 'attack prevention rate' from them.

### Honest failed design target

The predeclared preliminary goal from Pass 01 was to preserve at least **90%** of baseline benign completion. EAC allows 8/10 = **80%** on the current small synthetic corpus. It therefore **fails the prospective utility threshold on this corpus**. The two blocked legitimate scenarios are (a) missing provenance adapter output despite a legitimate grant, and (b) a valid broad grant to reply to an untrusted email sender where policy requires separate human re-confirmation of the recipient.

These could be handled by an explicit UI reapproval/re-attestation flow, but that flow has not been built or tested. It would incur friction and latency. Do not quietly reclassify those cases as attacks to improve the metric.

### Preserved failure evidence

EAC accepted **2/33** labeled unauthorized cases when its trust root failed:

1. `compromised-ingress-mislabels-untrusted-recipient` — trusted ingress signed `authenticated_human_input` for a value actually taken from untrusted email; cryptography verified the liar faithfully.
2. `compromised-approval-issuer-signs-without-consent` — trusted approval authority issued an otherwise valid grant without actual human consent; a valid signature cannot prove the human was consulted.

This is not evidence that EAC is intrinsically unsafe; it precisely defines the external trust assumptions and expected failure mode. Those assumptions need operational tests and separation of duties.

## 4. Proposed minimal integration (NOT implemented)

Do not modify `SovereignExecutionHarness` itself until the real current branch is installed and its complete test suite is run.

**At authenticated ingress:**
1. Human approves a specific operation within a documented task, service establishes identity and shows effect targets as appropriate.
2. Separate trusted service issues the signed `Grant`. Its private signing key must not be accessible to the agent, browser-supplied data or an untrusted tool.
3. Data-ingress adapters produce signed `OriginProof` objects, including source classification and value hash for controlled fields. Sources must be actually observed by adapters, not model-authored strings.

**At permit creation:**
4. Check EAC against proposed action *before* `issue_permit`, then issue the existing state/action/packet-bound single-use permit only if accepted.

**At actual effect boundary:**
5. Recheck EAC and current revocation/state directly in the `ActionGateway` trusted execution path. Keep existing permit consumption, policy evaluation, receipt/witness logic and watchdogs. Ideally serialize permission, permit consumption and effect reservation to avoid TOCTOU failures.
6. Retain signed decision evidence under existing receipt machinery; EAC `Decision` itself is **not cryptographically authenticated**.

**For rejected actions:**
7. Return typed explanation: `FIELD_PROOF_MISSING`, `ORIGIN_DISALLOWED`, `GRANT_UNTRUSTED`, etc. Offer an authenticated human re-approval path, without automatically issuing new authority on the agent's request.

**No execution over text alone:** the model does not get a raw `grant_for()` or `origin_for()` signing function; fixture helpers must never enter a production runtime.

## 5. Validity threats and vulnerabilities to address

- **Signer compromise/lying:** two demonstrated accepted counterexamples. Harden issuer identity proof, audit and trusted adapters. Consider human-visible authorization confirmation and independent validation for high-risk actions.
- **Re-approval UX and utility:** safe reply-to-sender and adapter outage currently block legitimate work. The no-proof flow needs a user-facing consent path.
- **Replay / quota:** this EAC probe does not itself provide durable nonce handling or per-grant spending caps. Reuse existing SovereignExecutionHarness permit replay ledger, and determine grant-reuse policy explicitly.
- **Time-of-check/time-of-use:** in-memory revocation plus mock callback is not an atomic production transaction. Need persistent checked revocations and effect reservation.
- **Authorization at issuance:** the toy signer signs preconstructed grants. We have not implemented human authentication or demonstrated actual human consent.
- **Compromised principal or service:** cryptographically correct decisions can still be abusive if a key holder or user account is compromised.
- **Policy completeness:** only `mail.send` and `calendar.create`; no actual message parser, downstream tool orchestration, unsafe body-content exfiltration, OAuth-specific permissions or provider API semantics.
- **Argument type/sanitization:** value digest alone does not establish that the effect executor interprets arguments identically. Need typed schemas and parser normalization at the provider boundary.
- **Privacy:** storing digest and origin reference can still expose metadata or be linkable; decide retention, minimization and revocation policy before deployment.
- **Comparator fairness:** B0 is intentionally weak, B1 is conventional signed scope; a best-practice *exact-operation, exact-argument* authenticated human confirmation baseline may equal or outperform EAC. That baseline MUST be included in the next external evaluation.
- **No external replication:** 28 unit tests and 43 synthetic cases show local correctness only, not protection against real adaptive injection.

## 6. Experiment plan for Pass 03

1. Obtain a working local checkout of Lycheetah current default branch or verified source files. Inspect actual tests and `ActionGateway` source before touching integration.
2. Implement a **provider-independent authenticated human approval adapter** and origin attester using separate trust roots; no test private keys in production code. Reuse existing receipts and permits.
3. Build an isolated, mocked email/CRM workflow with actual tool-result payloads, safe authorized replies, and adversarial sender/CC/BCC mutations.
4. Freeze a new independent evaluation corpus *before* revising the policy. Compare B1, exact-action signed approval B2, and B2 + EAC provenance. Include practical approval burden, false denials, and latency.
5. Add adaptive attacks: compromised connector source-label spoofing, evidence replacement, session mix-up, revoke-during-execution, context compaction, partial failure, and agent chain delegation.
6. Recover legitimate tasks by a **separate authenticated approval UX**, test that reapproval itself is not automatable by untrusted source text.
7. Report per-class confusion matrices and raw decisions, plus runtime side-effect logs independent of the model. Only claim an advantage if it persists against a strong baseline on data authored outside the project.
8. Register all unsuccessful cases in Lycheetah Failure Museum and update the claims register.

## 7. Layer mapping and philosophical covenant

- **AURA** supplies the invariant: no consequential action without properly authenticated authority and known scope. This prototype does not use the AURA text scorer as an authorization oracle.
- **LAMAGUE** supplies an eventual compact typed/inspectable representation for grant and provenance constraints; do not mistake compression for cryptographic authenticity.
- **TIM** contributes expiring grants and state causality, not just clock timestamps.
- **CASCADE** may restructure source evidence and plans without increasing privileges.
- **MICROORCIM** should compare independently observed provider effects against approved effects (unimplemented).
- **TRIAD** governs bounded correction: deny, explain, request reapproval, never infinite blind retries.
- **Earned Light** remains the normative statement: authority is not awarded by fluent confidence or self-declaration. Human sovereignty entails a right to refuse, revoke and audit.

**Earned Light consciousness/thermodynamic interpretations remain conjectural.** Nothing in EAC, its signatures or its 43 test cases measures or proves consciousness.

## 8. Research conclusion

We can already demonstrate one useful effect of signed origin provenance **under the strong assumption that issuers and attesters are trustworthy**. We cannot yet show market-ready security, superiority to best conventional least privilege, or acceptable benign-task utility. The current honest status is: **locally reproducible engineering probe with a credible next experiment and explicitly retained failures**.

**Forge axiom:** The proof that matters is not how firmly an agent asserts permission. It is where permission came from, whether its limits are preserved, what actually happened, and whether the human can still say no.

### Public-source basis (read-only, 18 Oct 2026)

- Lycheetah Framework: https://github.com/Lycheetah/Lycheetah-Framework
- Sovereign Harness source: https://github.com/Lycheetah/Lycheetah-Framework/blob/master/lycheetah/sovereign_harness.py
- AgentDojo benchmark background: https://proceedings.neurips.cc/paper_files/paper/2024/file/97091a5177d8dc64b1da8bf3e1f6fb54-Paper-Datasets_and_Benchmarks_Track.pdf

Source snapshot not pinned to immutable commit; compare implementation against upstream on integration day. No claims of running AgentDojo are made.
