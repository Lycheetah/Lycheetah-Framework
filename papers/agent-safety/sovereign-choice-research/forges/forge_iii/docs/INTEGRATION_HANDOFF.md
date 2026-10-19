# GitHub Integration Plan — Reuse, Do Not Duplicate

**No GitHub writes performed by this forge.**

The existing [Lycheetah-Framework](https://github.com/Lycheetah/Lycheetah-Framework) `master` branch already contains:

1. [`papers/agent-safety/frontier-controls/01_commit_time_authority_v0_7/commit_fence.py`](https://github.com/Lycheetah/Lycheetah-Framework/blob/master/papers/agent-safety/frontier-controls/01_commit_time_authority_v0_7/commit_fence.py) — tested local serialisation and generation-fencing for protected effects; explicitly notes limits of remote providers.
2. [`lycheetah/sovereign_harness.py`](https://github.com/Lycheetah/Lycheetah-Framework/blob/master/lycheetah/sovereign_harness.py) — exact-action/state/time/scope single-use permit with SQLite nonce ledger and caveats about identity authentication.
3. [`34_ASSURANCE_RUNTIME/ASSURANCE_RECEIPT_SPEC_v0.1.md`](https://github.com/Lycheetah/Lycheetah-Framework/blob/master/34_ASSURANCE_RUNTIME/ASSURANCE_RECEIPT_SPEC_v0.1.md) — auditable decision receipt spec with explicitly limited evidence.
4. [`05_MICROORCIM_L5/essentials.md`](https://github.com/Lycheetah/Lycheetah-Framework/blob/master/05_MICROORCIM_L5/essentials.md) — conceptual/computable drift monitor with deceptive-alignment limitations.
5. [`docs/X_ARTICLE_SOVEREIGNTY.md`](https://github.com/Lycheetah/Lycheetah-Framework/blob/master/docs/X_ARTICLE_SOVEREIGNTY.md) — sovereignty is not dominion.

## Proposed non-destructive merge

**Phase A: documentation**
- Add `docs/SOVEREIGNTY_DESIGN_CHARTER_v0.3.md` under the philosophical/brand docs with `[PROPOSAL]` status.
- Register MICROORCIM symbolic-event and numerical-monitor variants as distinct semantic objects in `35_ABSTRACT_AND_GENERATIVE`, preserving lineage.
- Add a bounded property to the agent-safety paper: `intent_version` is part of a current grant and changes invalidate old permits for new effects.

**Phase B: test-only extension**
- Instead of merging this package's new SQLite gate, introduce tests/fixtures around the *existing* CommitFence and sovereign harness. Make an intention revision increment the appropriate **authority generation** or invalidate the correct scoped permit.
- Add tests: altered intention after admission, revocation before protected finality, revocation after finality, same-actor changed payload, duplicate effect, crashed provider response, restart, concurrent actors, wrong tenant, missing proof of authentic human authorization.
- Match equal workloads against the existing conventional generation-fence reference; do not compare only against a deliberately weak baseline.

**Phase C: usability study**
- Build a user-facing receipt, revision and cancellation interface in a disposable sandbox.
- Assess comprehension, meaningful refusal, choice alternatives and exit, not just code correctness.
- Report false blocks, valid user task completion, operator burden, and effect discrepancy rates.

**Stop/go:** No real email posting, payment, repo writes or remote provider until authentication, dispatch isolation, exact payload binding, monitoring, provider reconciliation and security review are working end to end.

## Maintainer judgment

Treat `choice_fence.py` as a small independent **teaching and falsification fixture**, not production-core architecture. The improvement to transplant is the **intention-change semantics and associated human-facing test requirements**, not another second security implementation with competing state.
