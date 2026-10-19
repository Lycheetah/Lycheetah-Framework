# Earned Light — Research Pass 03: The Human Reconfirmation Bridge

**Date:** 18 October 2026 (NZDT)  
**Phase:** Local computational research, security engineering; production integration NOT performed.  
**Prior artifacts:** Earned Light Research Pass 01; Forge II EAC v0.2 handoff.

## Executive finding

An otherwise legitimate effect can be stalled because the current agent lacks trusted provenance for one controlled field. A natural response is to ask the human to confirm. However, **a human confirmation dialog is itself an attack surface**: an adversarial message can both demand approval and manipulate the explanation of what is being approved. Forge III makes *requesting review* and *approving a specific effect* separate, signed, one-use ceremonies outside model-generated content. It is a protocol prototype, not a claimed invention of new cryptography.

The original 43 cases, labels and v0.2 code have not been edited to improve the scores. Two fixed, already-documented benign false denials are replayed using simulated human approvals; nine other recoverable denials lack a signed review initiation and remain blocked. Synthetic benign completion rises from 8/10 to 10/10. The two compromised-root counterexamples remain accepted (2/33 unauthorized). **This does not demonstrate real human usability or reliable user decisions.**

## A newly visible failure: approval prompt amplification

The first iteration of this pass allowed the agent to request a review challenge for each recoverable denial. In the 43-case test set, that yielded 11 possible challenge prompts; only 2 corresponded to authorized, legitimate cases. This presented a plausible **approval fatigue** / dialog-forging attack even though execution still required signed consent.

Revision: only a signed, single-use `ReviewIntent` produced by a separate trusted UI can open a new review. The model can return typed denial information but not call an authority signer. The fixture now creates two challenges and zero unrequested ones, **by assuming the human initiates review only for the two legitimate exceptions**. This is an architectural test, not a behavioral measurement; a real user might still choose to review a malicious action.

## Implemented protocol

```
agent-proposed Request + EAC Grant + OriginProofs
        │
        ▼
EAC evaluates: allowed → existing protected execution path (not rebuilt here)
        │
        └── denied → is reason explicitly reconfirmable?
                         │ no → hard deny
                         │ yes
                         ▼
              signed trusted-UI ReviewIntent?
                         │ no → deny, no prompt
                         │ yes, bound to full request and grant
                         ▼
              SQLite records single-use challenge + sealed full display
                         ▼
              separate authenticated approval service reviews sealed content
                         │ refuses → deny
                         │ approves
                         ▼
              Ed25519-signed exact-action ReviewReceipt
                         ▼
              Check EAC current state, grant, sealed display, binding, TTL,
              issuer and recorded approval; atomic SQLite claim
                         ▼
              mock side-effect callback (NO actual external effect)
```

For a real Lycheetah integration, EAC must be checked at both permit issuance and actual provider effect boundary. Use the existing permit replay checks, gate, receipts, and policy machinery rather than replacing them. Authority and one-use revocation should ultimately be coupled to effect reservation in a shared durable service.

## Local evidence

| Instrument | Result | What it establishes |
|---|---|---|
| Pytest (v0.2 + v0.3) | 76 passed | Regression behavior on our implementations and chosen cases only |
| Original v0.2 corpus | 43 scenarios (10 benign, 33 unauthorized) | Historical comparable input set, labels chosen by developer |
| v0.2 EAC | 8/10 benign; 2/33 unauthorized allowed | Baseline on same test set |
| v0.3 EAC + signed reconfirmation | 10/10 benign; 2/33 unauthorized allowed | Simulated recovery of the two prior legitimate denials without change to two adversarial root compromises |
| Trusted review initiations | 2 simulated | Does NOT measure human motivation, comprehension, time, or deception |
| Suppressed unauthenticated review requests | 9 case-level denials | Signed review intent gates challenge issuance in this synthetic corpus |
| Concurrent replay calls | 30 competing SQLite claims, exactly one test callback executed | Within one SQLite database and these threads, one-use consumption holds |

### Why a strong conventional baseline may win

Imagine a conventional **exact-action, authenticated, unspoofable approval UI** that requires explicit human review for every effect. With a perfectly accurate simulated human refusing all 33 adversarial cases, that policy would yield 10/10 benign and **0/33** unauthorized in this artificial set. It would also require ten legitimate effect reviews instead of selective review. This is a conceptual upper-bound example, **not a coded baseline or measured experiment**. A future fair comparison must include human error, approval friction, prompt volume and usability—and must not assume a perfect human oracle.

## Main design decisions

1. **Authorization scope cannot compensate for bad provenance:** EAC must first identify the bounded reason for denial. The bridge never converts a bad signature or unknown tool into approvable authority.
2. **Opening a dialog is itself permissioned:** review-initiation signature and nonce are unique to the exact request/grant; a model-generated `approve` string cannot initiate a prompt.
3. **User review is about an exact action, not a task summary:** the display contains all fields, including `cc`/`bcc` and the body. JSON escapes control characters and avoids silent markdown/HTML rendering in this research path.
4. **Bind approval to rendered evidence:** the approval service rereads the sealed display from the trust store; the signed approval binds both `request_digest` and `display_digest`.
5. **Revocable, temporary and one-use:** do not infer that yesterday's permission survives context change. SQLite records approved/rejected/consumed and rejects replays.
6. **Mark uncertain effects as uncertain:** claim-before-effect means a provider crash consumes approval and blocks blind retries. Exactly-once execution requires a provider outbox, idempotency key and effect reconciliation.
7. **Human sovereignty is not delegated to a classifier:** the agent may explain a denial and present data, but must not impersonate the principal, create signed approvals or hide the real action.

## Formal candidate invariants

Let `R` be the complete action request; `G` a grant; `P` existing origin proofs; `I` signed review intent; `C` sealed display challenge; `A` the approval receipt; `S` the single-use ledger; `T` the current time.

- **Review eligibility:** `EAC(R,G,P) ∈ {FIELD_PROOF_MISSING, ORIGIN_DISALLOWED}`.
- **Independent initiation:** `Verify(I) ∧ I.request_digest = H(R) ∧ I.grant_id = G.id ∧ I.principal = G.principal`.
- **Exact-action consent:** `Verify(A) ∧ A.request_digest = H(R) ∧ A.display_digest = H(C.display) ∧ A.principal = G.principal`.
- **Temporal and state integrity:** `T < min(G.expiry,I.expiry,C.expiry,A.expiry)` AND current scoped grant valid and not revoked.
- **Consumption:** `AtomicClaim(S,A.challenge_id) = fresh`; all later claims fail.

A proof of those syntactic invariants says nothing by itself about the truthfulness of a compromised service, or the accuracy of the human's interpretation of the displayed action.

## Priorities for Forge IV

**1. Independently authored test corpus.** Freeze outside-authored legitimate and adversarial cases BEFORE policy changes; measure helpfully blocked requests and misleading valid-looking prompts as well as overt injections.

**2. Human-interface instrumentation.** Prototype a trustworthy UI that obtains the exact action from a trusted backend, presents recipients/CC/BCC/attachments/data disclosure prominently, uses origin-bound phishing-resistant authentication where appropriate, and records actual deliberate click events. WebAuthn *authentication intent is not equivalent to understanding every transaction detail*.

**3. Effect reconciliation.** Integrate an outbox/idempotency ledger with the actual provider adapter; distinguish reserved, submitted, externally confirmed, uncertain, and compensated state. For unknown results, never silently repeat an effect.

**4. Trust roots and cross-checks.** Separate keys, stronger authentication, monitor attester falsification and issuer misbehavior. Consider independent evidence of human consent, but retain signer-compromise assumptions transparently.

**5. Version-pinned real integration.** Review `lycheetah/sovereign_harness.py`, `ActionGateway`, all permit/receipt consumers and tests in an actual pinned checkout before changing enforcement paths. GitHub connector returned no accessible repos during this pass; no repository changes or integration tests were performed.

## External grounding and limits

- NIST SP 800-63B-4 (2025): phishing resistance, replay resistance, authentication intent and binding: https://pages.nist.gov/800-63-4/sp800-63b.html . NIST provides authentication guidance, **not a validation of this implementation**.
- OWASP Excessive Agency (LLM06:2025): recommend user approval for high-impact actions and minimum privilege: https://genai.owasp.org/llmrisk/llm062025-excessive-agency/ .
- OWASP HITL Dialog Forging (Lies-in-the-Loop): untrusted material can manipulate approval dialog content: https://community.owasp.org/attacks/Lies_in_the_Loop .
- W3C WebAuthn: verification of user presence differs from user verification, and UI/consent is a distinct concern: https://www.w3.org/TR/webauthn/ .

These references inform threat models and requirements; no external certification or benchmark was achieved.

## Earned Light covenant

The meaningful distinction isn't *AI can always act* versus *AI can never act*. It is that a bounded, human-traceable process exists for uncertainty, correction, deliberate refusal and audit. The system may earn eligibility to ask; it never earns the right to manufacture an answer on behalf of a human.

**The philosophy's consciousness/thermodynamics hypothesis remains a separate, unverified workstream.** This engineering work does not measure it.
