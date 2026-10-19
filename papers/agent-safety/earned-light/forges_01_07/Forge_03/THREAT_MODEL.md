# Forge III threat model and assurance boundaries

## Protected assets

Exact action arguments, authority grant, human identity session, truthful approval display, review-intent nonce, review receipt, single-use record and downstream side-effect state.

## Attackers assumed

Untrusted inbound emails/webpages/retrieved files, prompt-injected agent reasoning, a malicious agent proposing altered effects, compromised intermediate context, attackers who possess previously signed approvals but **not** a trusted signing key, users exposed to deceptive approval requests.

## Explicitly trusted components

- Human authentication / trusted UI **outside the model**; currently mocked.
- Ed25519 private keys not available to the agent. The research `TrustedReviewAuthority` combines initiator and approver test keys; production should separate those roles and trust boundaries.
- EAC signer and data-source attester, subject to known compromise risks.
- SQLite file integrity and OS authorization; corruption or external writes invalidate the demo's security story.
- Shared trustworthy time in the fixture; no trusted clock has been implemented.

## Attacks locally tested

Wrong principal; wrong action digest; forged review intent or approval; missing initiation; action mutation in body, destination, cc/bcc, state and scope; reply to an untrusted recipient with deliberate approval; review display substitution; data/control character escaping; expired ticket; refusal; replay and races; revocation after review; crash after consumption; forged data provenance. See `tests/test_bridge.py` and inherited Forge II tests.

## Known unresolved risks

- **Real human intent**: test code accepts a string `authenticated_principal` as a stand-in. A production IdP/session must supply an unforgeable identity signal and deliberate, trustworthy review event. Exposing signing methods to an agent defeats this system.
- **Approval-dialog deception**: a correctly shown malicious effect can still persuade a person to approve; a trusted UI cannot eliminate social engineering. An end-to-end study with real participants is absent.
- **Signer/attester compromise**: Forge II's two acknowledged accepted synthetic counterexamples persist. Signatures attest to a signer's assertion, not its truth.
- **Presentation ambiguity**: ASCII-escaped JSON avoids invisible control characters but may be hard for humans to understand, especially URLs, large messages, lookalike strings and attachments. Real UI must show exact effect and field categories accessibly, not render untrusted HTML.
- **Prompt fatigue/DoS**: signed initiation stops automatic challenge creation only if signer is protected and user actually chooses to enter review. Attackers may still fill an inbox with denied actions or socially engineer approval.
- **TOCTOU**: in-memory grant revocation and SQLite approval claim are not committed in one transaction. Revocation could race across the boundary. No distributed atomicity with the email/calendar provider.
- **Effect state uncertainty**: claim-before-effect blocks retries after crash but does not guarantee the effect happened. Require durable outbox and reconciliation.
- **Data retention**: the demo SQLite stores complete plaintext action and event metadata. Privacy policy, encryption at rest, retention/erasure, audit signing not implemented.
- **Schema coverage**: only inherited `mail.send` and `calendar.create` typed policy; no attachment types, semantically equivalent addresses, OAuth scopes, delegated agent chains or object reference normalization.
- **Test validity**: homogeneous hand-authored corpus, fake approver that approves exactly the two hand-selected benign cases, no independent adversary, no timing performance/user study, no provider.

## Rejected security claims

Do not claim: "human has verified this," "phishing-proof UI," "zero prompt injection," "exactly-once side effect," "100% accuracy," "proven new security primitive," or "model consciousness proven." None follow from this study.
