# Research history and technical progression

This archive follows one practical use case: a coding agent proposes a high-impact action such as merging a particular pull request. The central design rule is that the model proposes; deterministic controls decide whether the exact effect is authorized; the downstream provider is still the final enforcement boundary.

## v0.5 — bind approval to a precise action

The early prototype canonicalizes action parameters and binds approval to the exact action hash, actor, required scope, expiration and authority epoch. It records allow/deny decisions and includes a deliberately weak role/tool-only comparator. Its effect registry and authorization flow are in memory and single-process. It does not prove persistence, remote revocation, distributed concurrency or provider atomicity.

## v0.6 — persist authorization and effect state

SQLite stores approvals, actor/approver fields, authority epochs, effect states and audit events. One approval is intended for one exact effect. The state machine makes uncertainty explicit rather than treating a timeout as a safe retry signal. Tests cover mutation, expiration, revocation, changed pull-request state, restarts, simulated crash windows, reconciliation and concurrent use. The provider remains simulated.

## v0.7 — make history tamper-evident

Audit events are linked by a hash chain. A previously retained checkpoint anchors a known prefix, because a database writer could otherwise change old rows and recompute the chain. This advances tamper evidence but does not make the history magically immutable; the checkpoint and its authenticity must live outside the database's trust boundary.

## v0.8 — independent checkpoint process and state reconciliation

A separate local HTTP process stores checkpoint history in its own SQLite database and signs checkpoint receipts with Ed25519. The authority validates each proposed extension's sequence, predecessor links, event hashes and final root instead of blindly signing a submitted digest. Checkpoint history is monotonic and rejects rollback/forks. The workflow wrapper requires checkpointed state around protected mutations and dispatch. It cross-checks operational approval/effect/authority tables against journal events. The GitHub adapter constructs a request preview with an expected head SHA, but has no network transport; the fake provider is only a simulator.

## What the reported tests establish

The v0.8 report documents 50/50 local tests passing with Python `ResourceWarning` treated as an error; a 1,000-case synthetic action-mutation benchmark with zero altered actions accepted by the guard; 100 exact-action positive controls accepted; and 25 eight-way concurrency rounds with one winner per approval. It also documents the separate-process checkpoint-service restart test and local failure/tampering checks.

The mutation baseline is intentionally weak (role/tool name only), not a mature production ACL. The tests are authored alongside the prototype and are not independent validation. Results should be treated as reproducible evidence about these specific code paths, not as broad claims of safety.

## Remaining gap — independent operation and real provider semantics

The checkpoint service still runs on the same host. A host administrator who can rewrite the guard database, checkpoint database, signing key and environment can defeat this trust arrangement. The next experiment should use a separately administered checkpoint service or managed key service, authenticated workload identity, off-host witness/retention, and a GitHub App in read-only/dry-run mode against a disposable repository. Read real API state and render expected requests, but keep merge writes disabled. Inject stale SHAs, revocation races, duplicate delivery, service failure, restarts and ambiguous responses. Never blindly retry an unknown remote outcome.
