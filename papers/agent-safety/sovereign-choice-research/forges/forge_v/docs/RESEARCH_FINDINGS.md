# Forge V — Findings, limitations and research agenda

**18 October 2026. Status: local integration verified; external provider/identity security unverified.**

## What changed

- Retrieved the original upstream `commit_fence.py` and `research_support.py` from the connected Lycheetah GitHub repository. Source bytes are verified against Git's blob SHA-1 IDs (`0af8050808569a098e11fb72a9f7d6c4c15044bb` and `0f623b6614be03a2f7bf65f2a5ea3fe1b12e51e9`). This is *not* a commit SHA or security attestation.
- Ran all four previously deferred Forge IV integration tests against those exact files: all passed. This is a genuine improvement in evidence status compared with Forge IV's fake-fence-only verification.
- Created `AtomicChoiceLedger`: the *intention metadata* and *upstream authority generation* now change together within the **same SQLite transaction**. The original upstream `issue_handle` and `commit` remain untouched.
- Added focused tests for crash rollback, altered action, withdrawal and regrant, thread/process concurrency, a revocation-vs-commit scheduling case, audit history, and intentionally bypassing the trusted host.
- Built a concrete comparison reproducing the prior separate-DB mismatch after an injected interruption; the new shared transaction rolls back both changes.
- Added an offline HTML demo with no network requests, identities or external effects.

## Why this belongs in Sovereign Will

The useful part of MICROORCIM is the recognition that *a change of intention can be a choice, not a failure*. This technical project cannot observe that freedom. It can make a narrower promise: a trusted local system can reject a newly committed effect if it was only authorized by a superseded or revoked version of intent, subject to the limits below.

In the old model the human's expressed revision and the execution authority could diverge across a crash window. In this model they cross one protected local transaction boundary together. That makes the relation between choice and consequence more reconstructable, not metaphysically more free.

## Threat model and limitations

1. **Trusted human approval is not implemented**. Principal strings and exact action digests cannot demonstrate real identity, voluntariness, informed consent or lack of manipulation. Add authenticated host UI, verifiable action preview and explicit operator intent.
2. **Trusted host must mediate every path.** The direct `CommitFence` API can bypass the added choice journal; the repository mirror contains an explicit proof of this bypass. No untrusted model, plugin or tool runner should access the fence DB or high-privilege methods directly. A hardened host API boundary is missing.
3. **The semantics are local.** Upstream fenced commit is a SQLite-protected effect record. It cannot atomically revoke an email, payment or other provider effect in a separate system. At least-once delivery, ambiguous acceptance and external reconciliation remain open problems.
4. **Already completed work cannot be erased.** An idempotent recheck of an already committed effect can return `CONFIRMED` after withdrawal. This is not a fresh effect. Operators must not display it as a new authorisation.
5. **Revocation and commit are ordered at the DB linearisation point.** A commit that wins before revocation may legitimately succeed. Later revocation does not undo it. A revocation that commits first blocks a stale-generation new effect.
6. **New code depends on upstream internal SQLite tables** (`authorities`, `audit`, `handles`, `effects`) instead of a stable public extension interface; schema drift could break it. Upstream versions must be pinned and compatibility tested before adoption.
7. **Expiry isn't supported by the new intention records.** Existing upstream `CommitFence` generation handles have no time-bound token check in this path. Deadline/TTL authority needs dedicated trusted-clock design.
8. **Audit log is local, not cryptographically tamper-evident.** Metadata records may be edited by anyone with DB write rights. Integrate upstream assurance receipts with externally anchored roots for stronger claims.
9. **Privacy:** `purpose` text is persisted and could reveal sensitive context. Store minimal metadata or encrypted content according to a defined retention/privacy policy, and test erasure requirements.
10. **Database connection warnings:** the original upstream fence uses `with self.connect()` in places; SQLite's connection context manager commits but does not by itself close connections. Python 3.13 displayed `ResourceWarning` about unclosed upstream SQLite connections. This is a separately actionable upstream lifecycle improvement, not evidence of exploit.
11. **No independent evaluation or deployment:** tests are self-authored synthetic local tests. No live AI decisions, user study, provider integration, external pen-test or production warranty. There is no claim of novel cryptography or invention of generation fencing.
12. **Original aim preserved:** no score of human worth, metaphysical free will, consciousness or emotional health is inferred.

## Results and falsifiers

**Verified in local tests:** SHA-verified upstream source; previous 4 integration scenarios; atomic local grant/revise/withdraw; interrupted transaction rollback; stale handle blocked after committed revocation; metadata-only event records; 6-process and 16-thread ordering; one local effect despite 20 retries.

**Observed known negative control:** a deliberately weaker external `PreDispatchOnlyBaseline` still accepts a stale request after local revocation, illustrating a remote-provider limitation. Another negative-control test shows a privileged caller directly accessing the raw fence can bypass the added choice journal — the host boundary must be enforced.

**Falsifier for new narrow claim:** a deliberately interrupted intention update leaves different committed versions for the choice row and the `authorities` row in the same protected SQLite database. Tests should inject interruptions at multiple write boundaries and recovery scenarios.

**Falsifier for broader product claim:** a real human cannot understand the scope of approval, easily revoke it, or prevent stale tool effects, despite green unit tests.

## Recommended upstream integration path

1. Place this adapter on an experimental branch **only after** code review and migration planning, rather than silently replacing `CommitFence`.
2. Introduce a stable upstream transaction extension interface; remove direct dependence on internal table structure.
3. Bind authenticated user sessions and previews to exact canonical action hashes and explicit scope, expiry, affected parties and purpose.
4. Wire one host-controlled mediation point for all action issuance and commit; defend against direct permission-store access.
5. Add recovery/reconciliation for unknown remote outcomes, external cancellation and retry budgets; preserve effect receipts.
6. Test with a mock provider supporting delayed acceptance, ambiguous timeout, and out-of-order cancellation, then test a disposable real integration under explicit permission.
7. Carry out a user comprehension study: users identify what was authorised, refuse proposals, revise goals and interpret cancellation receipts under realistic workload.
8. Compare a matched standard generation-fence baseline, preserving identical information and APIs; do not claim novelty or superiority without evidence.

## Related sources

- [Current upstream commit fence](https://github.com/Lycheetah/Lycheetah-Framework/blob/master/papers/agent-safety/frontier-controls/01_commit_time_authority_v0_7/commit_fence.py)
- [Exact Action helper](https://github.com/Lycheetah/Lycheetah-Framework/blob/master/papers/agent-safety/frontier-controls/research_support.py)
- [Lycheetah MICROORCIM](https://github.com/Lycheetah/Lycheetah-Framework/blob/master/05_MICROORCIM_L5/essentials.md)
- [Sovereignty Is Not Dominion](https://github.com/Lycheetah/Lycheetah-Framework/blob/master/docs/X_ARTICLE_SOVEREIGNTY.md)
- [From Constitutional Commitments to Testable Agent Controls](https://github.com/Lycheetah/Lycheetah-Framework/blob/master/papers/agent-safety/PAPER.md)

**Foundational phrase:** *An instruction is not perpetual ownership of the person who gave it.*
