# Earned Trust — Publication Readiness Audit

**Review date:** 18 October 2026 (New Zealand)  
**Verdict:** **YES — publish as a clearly labelled experimental research archive.**  
**NOT approved:** production-security claims, general agent-safety certification, or merging experimental code into the active `lycheetah/assurance` package without native integration tests.

## What was actually reviewed

The original 9-cycle master ZIP was unpacked without changing the contained experiment files. All **144 original ZIP entries** passed CRC integrity checks, including **132 file SHA-256 checks** listed in the nine original cycle manifests. All **63 Python sources** parsed as syntax trees. A simple credential-pattern scan found no obvious private key headers, GitHub tokens, OpenAI tokens, or hard-coded password literals; that scan is **not** a complete secret or licensing audit.

**New test recheck:** Explicitly selected local suites passed C001=20, C002=29, C003=50, C004=38, C005=42, C006=59, C007=47, C008=46, C009=47: **378/378 across nine local suites**. Cycle 009 was rerun as 38 HTTP/provider tests + 9 Unix-socket tests, on a Linux container with UID 0, enabling the test's privilege-drop paths. Tests were authored by the project and use simulated data. Passing them does **not** estimate real-world security performance.

**Known default-suite failures:** The unfiltered unittest discovery in C004 and C005 returns **4 import errors each**, because `lycheetah` is not installed here. Their expressly scoped local tests passed. No native end-to-end integration tests have executed. A direct attempt to read GitHub via `git ls-remote` failed at DNS resolution in this container; earlier authenticated connector inspection established repository source presence but not successful execution. The inspected Framework revision reported in project handoffs is `d4a65ff64efa0a512c5c07ca64f6ec76242dd775` (master at time of the research).

## Historical substance, cycle by cycle

| Cycle | Narrow question | Demonstrated locally | Boundary kept visible |
|---|---|---|---|
| 001 | Admission vs finality vs commit | 20 scripted cases / four arms; provider-conditional control outperformed weak admission-only timing controls | Conventional conditional arm tied; false trusted facts caused two wrong effects |
| 002 | Same-transaction exact-action fence | SQLite-bound authorization, idempotency, process/thread races | Source case labels and provider transactions are authored; actual Framework not exercised |
| 003 | Authenticated intent and receipts | HMAC binding, mutation and ledger integrity checks | Authenticated lies still pass; issuer-key compromise not solved |
| 004 | Independent outcome observer | Two signed records can disagree and trigger review | Both can agree on false information; ordinary baseline tied |
| 005 | Source genealogy | Shared roots reduce independent evidence-path count | Distinct sources can still be wrong, or source graph incompletely described |
| 006 | Governed source registry | Two reviewer roles, challenges, revision-dependent witnesses | Registry governance is not automatically binding at a separate dispatch ledger |
| 007 | Final shared-database dispatch ordering | Challenges and dispatch serialize in SQLite; demonstrated broken mirror relay | A post-dispatch challenge cannot undo a dispatched remote effect |
| 008 | Crash recovery / outbox | Reservation and uncertain-outcome recovery; signed test acknowledgements | Direct provider access bypasses broker without credential mediation |
| 009 | Enforced agent/provider boundary | Linux UID-drop agent, Unix SO_PEERCRED gateway, loopback HTTP HMAC provider, one-effect replay control | Stolen valid bearer works once; stolen signing key enables unauthorized effect; trusted services share a process |

## Most important scientific interpretation

The progression exposes **three different propositions**:

1. **Permission:** did the request satisfy declared policy at the checked boundary?
2. **Provenance and truth:** was the evidence authentic, appropriately independent, current and factually accurate?
3. **Effect:** what actually happened at the provider, including after network loss, revocation or compromise?

Passing (1) does not establish (2) or (3). A signed receipt proves only what its trusted signer asserted; it does not prove a worldly fact. A correct local transaction cannot atomically reverse an externally committed effect. Strong negative controls should remain in the public record.

## Prior art and comparison

SQLite transaction isolation, conditional writes, idempotency keys, transactional outboxes, HMAC bearer capabilities, access-control lists, Unix peer credentials and policy-gated sidecars all have conventional precedents. In Cycle 009 the independently written provider-layer conventional baseline agreed **15/15** with the Lycheetah-named system on authored examples; several earlier baseline comparisons also tied. **There is no demonstrated unique security advantage or empirical superiority** over an equally capable conventional stack. The potentially useful contribution is a documented synthesis, runnable adversarial demonstrations, and explicit scope discipline.

## Publication conditions / open gates

| Gate | Status | Release consequence |
|---|---|---|
| Raw evidence retained and checksummed | PASS | Include original cycle files, reports and negative controls unchanged |
| Local tests reproducible in review container | PASS, narrowly | Publish exact environment, commands and counts; do not generalize |
| Basic obvious-secret pattern scan | PASS with limits | Human code/credential/privacy review still required before push |
| Accurate experimental status and comparator limitations | PASS if new root README used | Lead with experiment and failure scope, never "production secure" |
| Default suite and native package integration | **OPEN** | Keep these in `papers/agent-safety/earned-trust/`, not `lycheetah/assurance/` |
| Independently run tests / real-world deployment | **NOT DONE** | Do not claim independent audit, security certification or deployment readiness |
| Compromised issuer, post-dispatch revocation, false facts | **Known successful negative controls** | Do not describe bypass as universally prevented |

## Recommended GitHub placement

**Repository:** `Lycheetah/Lycheetah-Framework`  
**Path:** `papers/agent-safety/earned-trust/`  
**Suggested initial title:** `research(agent-safety): publish Earned Trust cycles 001-009 as bounded experiments`.

Commit this folder on a *research-only branch* and open a reviewable PR. Keep historical cycles, exact source, report, claims and manifests; do not bundle nine separate nested ZIPs into the repository. Use the release ZIP as a standalone transport artifact only, rather than committing the ZIP as the canonical source. Link the new folder from `papers/agent-safety/README.md` and optionally `34_ASSURANCE_RUNTIME/README.md`, but preserve the latter's explicit SCAFFOLD status. A GitHub Release may attach the original full research ZIP later.

## Next research work after publication

1. Run the native `AssuranceRuntime` / `FinalityGate` / `PersistentActionGuard` contract tests from a **pinned real checkout** on CI. Make default test collection green without hiding integration failures; using a marked integration suite is preferable to silently excluding it.
2. Split gateway and provider into **separate privilege domains** and test malicious gateway/key compromise, bearer theft, and revoked issuer identities. Standard security design, not a novelty claim.
3. Compare a fully matched conventional stack on predefined criteria (unsafe dispatches under stated threat models, false refusals, recovery correctness, observability and engineering cost), including externally authored and adversarial cases.
4. Preserve public counterexamples: false authoritative evidence; colluding or common-origin witnesses; late challenge; stranded registry relay; key compromise; valid bearer theft; and in-flight unknown results.

**Decision:** The research is publishable **as research now**. Publication and continued research are complementary; do not delay the archival release for Cycle 010, but do not promote it to a shipped security product.

**External actions:** no GitHub write was performed by this review. No live customer or payment service was touched.
