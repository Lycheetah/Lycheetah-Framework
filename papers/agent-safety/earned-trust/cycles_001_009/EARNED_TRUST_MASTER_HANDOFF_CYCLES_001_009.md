# EARNED TRUST — Master Research Handoff (Cycles 001–009)

**Updated:** 18 October 2026 · **Stewardship:** Lycheetah research · **Status:** local experiments, not independent security validation

## Why this work exists

Test the transition from AI language about trust to concrete externally consequential tool boundaries. Record *both* protected cases and the places where trusted-looking records still authorize incorrect or unauthorized outcomes. No deployed payment, customer or live provider service has been used.

## Historical research progression

- **001 — Admission vs finality vs provider commit:** synthetic action-check timings; false authority remains fatal.
- **002 — Atomic local dispatch:** SQLite identity and idempotency, concurrent attempts; provider and caller's declared action must match.
- **003 — Authenticated intent and receipt:** local HMAC seals; authentication preserves false claims.
- **004 — Two-record reconciliation:** separately signed observation and provider event; two sources can agree on the same false fact.
- **005 — Source independence:** ancestry matters more than number of signatures; false independent witnesses remain possible.
- **006 — Governed source registry:** signed challenges and review of source lineage; accepted challenges may not reach dispatch at the correct time.
- **007 — Shared transactional dispatch fence:** governance/dispatch ordering within one SQLite DB, but external relay and post-dispatch gaps remain.
- **008 — Crash-observable outbox:** reserve before send, unknown after crash, authenticated provider reconciliation; bypass via direct provider credentials remains an open risk.
- **009 — Enforced boundary:** actual UID-dropped subprocess and Unix peer-credential gateway, plus local HTTP provider enforcing action-bound HMAC capability and SQLite idempotency. C009 removes the specific *unsigned direct-provider bypass* for the tested unprivileged route. Compromised issuer key and stolen bearer capability remain successful attacks.

## Cycle 009 new results

- **47/47** local Cycle 009 tests passed, including OS UID-drop, local HTTP, source challenge, approved socket path, replay/concurrency, credential compromise negative controls.
- **46/46** Cycle 008 tests re-passed in this cycle.
- **15/15** constructed provider-layer scenarios matched a separately implemented conventional baseline; this is not full-system equivalence or improvement.
- **32 concurrent signed attempts** for a single effect produced 1 new effect and 31 idempotent HTTP responses.
- The native `lycheetah` Python package was **not importable**; Framework class integration remains **NOT EXECUTED**. Earlier named candidates should not be counted as passing.

## Critical negative claims to preserve

1. **False evidence:** no signature or atomic write guarantees factual truth.
2. **Late challenge:** a local revocation after dispatch claim cannot necessarily stop a signed capability already eligible for remote execution.
3. **Compromised signer:** knowledge of an issuer HMAC key enables unauthorized direct provider commits in C009.
4. **Stolen bearer:** an unexpired action-bound capability authorizes its exact effect once even when presented by an attacker.
5. **Process assumptions:** kernel UID provenance matters only when the trusted service is isolated from the caller; root or equivalent compromises bypass the local file protections.
6. **No demonstrated Lycheetah-specific superiority:** the matched conventional provider baseline delivered the same 15 fixed outcomes.
7. **Official Framework integration remains unverified:** synthetic C007/C008 code is carried verbatim; it is not the actual `lycheetah.assurance` package.

## Files and reproducibility

Read the individual cycle `RESEARCH_REPORT.md` and `CLAIMS.json`. The latest runnable focus is `earned_trust_cycle_009/`, containing exact source/test/side-effect boundaries, raw test output, scenario results, and SHA-256 manifest. All prior cycles are included byte-for-byte in the complete ZIP as retained research evidence.

## Next prioritized experiment (010)

**Split the trusted gateway and provider into genuinely separate confined services; replace symmetric provider-issuer HMAC with a verifiable asymmetric signer and independent key lifecycle.** Test an agent with the same UID as the gateway, a stolen bearer capability, compromise of signer credentials, issuer revocation at provider boundary, and crash recovery across separate processes. Run the native Framework contract suite on an authentic pinned Git checkout *before* making any claim about Lycheetah integration. Compare against an equally equipped ordinary gateway.

**External effects: DISABLED. GitHub: unchanged.**
