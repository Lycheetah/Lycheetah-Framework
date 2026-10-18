# Cycle 10: Review Desk security and evidence boundary

## Motivation

v0.9 cryptographically bound signed permits to an atomic batch, but its demonstration issued permits directly from test code. That is **operator key possession**, not a usable review interaction. v1.0 introduces a trusted, local server entrypoint where an operator can inspect evidence and give an explicit yes/no decision.

## Data flow

```text
Trusted source registration + operator clause contracts
  -> neural/scripted proposals (always untrusted)
  -> CoverageAuditor (coverage-ready but NOT authorized)
  -> ReviewDesk(configured by trusted caller; source, contract & batch are fixed)
  -> local password-gated, read-only presentation on 127.0.0.1
  -> session + synchronizer CSRF + exact presentation digest + explicit POST
  -> backend issues v0.9 single-use HMAC permit
  -> SQLiteLedger.commit_batch: BEGIN IMMEDIATE, permit check, stale head check
  -> one event containing all admitted claims + consumed permit
```

The browser may submit only decision type, its CSRF token and the exact digest already displayed. It cannot choose a claim, change policy scope, inject a new source, choose keys/nonces/timing or directly call the ledger. All displayed source/candidate/contract strings are escaped as text.

## Security properties exercised by tests

- Source body is not disclosed to anonymous GET clients.
- Requests with incorrect Host/Origin, missing cookie, invalid session or CSRF fail.
- Client-modified digest, unexpected extra form fields, duplicated form fields and overlong bodies fail.
- Session expiration, explicit local password check and bounded login attempts work in a toy threat model.
- Mutated registered plan/batch, stale ledger head and replayed actions refuse admission.
- One positive local HTTP review atomically commits two fictional claims; a reject changes no claim.
- Full signed event attachment and chain audit inherited from v0.9 remains available.
- Minimal observation export excludes secret/session material and source text.

## Explicit exclusions and open issues

1. **Not identity proofing or informed consent.** Anyone with local password and browser cookie can approve. A checkbox is not evidence of attention, and one local password is not per-user accountability.
2. **No TLS.** Loopback-only HTTP means no `Secure` cookie; sharing via proxy or remote port-forwarding is unsafe. This is not a production web service.
3. **Not privilege-isolated.** The reviewer-server process holds the signing key and the SQLite file path. A compromised process or attacker with the password can approve. A future service needs protected identity, key management and separate signer permissions.
4. **No durable rejection or screen-consent receipt.** Accepted approvals are durable HMAC envelopes; local rejections and displayed-screen digests live only in process until shutdown. The optional observation JSON is external and not included atomically in the ledger.
5. **Hostile source content remains hostile.** HTML escaping controls markup execution only. A perfectly rendered document can still lie, impersonate authority or contain prompt injections. Model reasoning is not trusted as a policy oracle.
6. **Clock limitations remain.** `recorded_at` is the trusted requested logical knowledge timestamp, not a time attestation. Local session duration does not prove review effort; it includes idle time.
7. **No broad benchmarking yet.** Both proposed and existing clauses are fictional fixtures. No human participant, independently labeled corpus or live LLM was evaluated.
8. **No OS-level sandbox.** Strict HTTP URL routing is not isolation of the Python process from local machine compromise.

## External security references

- OWASP *Cross-Site Request Forgery Prevention Cheat Sheet*: synchronizer CSRF token and Origin as complementary defenses, SameSite not sufficient alone. https://cheatsheetseries.owasp.org/cheatsheets/Cross-Site_Request_Forgery_Prevention_Cheat_Sheet.html
- OWASP *Session Management Cheat Sheet*: HttpOnly, SameSite, expiration and TLS/Secure-cookie requirement for real deployments. https://cheatsheetseries.owasp.org/cheatsheets/Session_Management_Cheat_Sheet.html

The reference desk implements only a subset, for local experimentation. No security audit or certification is claimed.
