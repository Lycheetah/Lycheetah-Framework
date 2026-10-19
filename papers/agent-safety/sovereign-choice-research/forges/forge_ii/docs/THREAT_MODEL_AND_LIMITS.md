# Threat model and known limitations

**Status:** `[DRAFT — NOT SECURITY REVIEWED]`

## Narrow property evaluated

When policy state, clock and owner-control calls are trusted, this local program's `decide()` only allows a specified request whose current grant is unrevoked, unexpired, within scope, on the correct intent version, with use-count available; high-impact operations additionally need a bound one-use approval. A SQLite transaction serializes the decision and bookkeeping.

`decide()` never executes the request. Its results speak only to policy admission; they do not show enforcement in a real provider.

## Explicitly excluded / unresolved threats

1. **No real identity:** `owner="human"` is a name, not cryptographic authentication. An attacker able to invoke `issue_grant`, `approve_once` or `revise_intent` can mint authority. The owner-control API must be external and protected.
2. **No privileged-code isolation:** The same Python process has access to `db` and policy methods. A malicious agent with shell access could bypass it. This module is for local research and must never serve as an untrusted agent's sole security boundary.
3. **No protected finality sink:** Admission at `decide()` and execution by an external provider are separate events. Revocation between them might not stop the external effect. The existing Lycheetah commit-time fence handles a narrower atomic local-finality case and should be the integration target.
4. **Payload substitution after the check:** High-impact approval binds a SHA-256 digest supplied in a request; the actual tool dispatcher must independently hash the exact outgoing bytes before an effect, and reject mutation.
5. **Untrusted recipient semantics:** An exact resource string does not establish that an address represents the intended human or that the user understood the consequence.
6. **Harm under valid permission:** A human can authorise something harmful, exploitative or illegal; authorisation cannot override safety, third-party rights or applicable law.
7. **Consent quality:** A log saying “approve” does not establish informed, voluntary or uncoerced consent. The prototype tests none of that.
8. **Time and expiry:** Clock trust is assumed. In the demo the host clock is injected and fixed. Distributed clock trust and monotonicity need design and adversarial tests.
9. **Audit chain:** HMAC only authenticates a local chain to a holder of the shared key. It is not public verifiability. Without an independently anchored head/tail, truncation of the last entries is not detectable from the shorter ledger alone; a privileged actor with the key can rewrite history.
10. **Data handling:** Resource names and policy metadata can reveal private information. Real deployments need retention, minimisation, encryption and export policies.
11. **Session ownership and replay:** Client-controlled identifiers are not proof of actor identity. An attacker may reserve an identifier unless requests are issued and authenticated by a trusted gateway.
12. **Risk taxonomy:** The fixed operation catalog is illustrative. Read operations can leak secrets. Real products need typed schema validation, tenant binding, data classification and context-specific policy.
13. **No user study:** No measures of subjective autonomy, understanding, coercion, user trust or ease of exit are supported.
14. **No machine moral status:** Operational constraint fidelity does not imply a machine has will, consciousness, rights, interests or inner experience.

## Stop/go rule

Do **not** connect any payment, email, social-posting, file-writing or production tool to this prototype. Before any pilot: independently authenticate approval; isolate model access; reuse exact-action permit and commit fence; execute against fake provider; test race, cancellation, accepted-but-lost-response, rollback limits, unsafe-but-authorised effects and provider reconciliation; assess whether humans understand the controls. Publish failures.
