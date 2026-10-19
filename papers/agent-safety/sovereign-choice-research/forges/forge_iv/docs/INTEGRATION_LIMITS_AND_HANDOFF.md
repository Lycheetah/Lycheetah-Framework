# Forge IV — Integration status, failure boundaries and recommended upstream work

**Current status:** `[LOCAL CONTRACT TESTED / ACTUAL UPSTREAM INTEGRATION TESTS PREPARED BUT NOT EXECUTED]`.

## Source inspection

The connected Lycheetah GitHub repository's `master` branch was consulted, specifically:

- `papers/agent-safety/frontier-controls/01_commit_time_authority_v0_7/commit_fence.py` — existing commit-time generation fence, protected SQLite local effects and a deliberately weaker pre-dispatch baseline;
- `papers/agent-safety/frontier-controls/research_support.py` — `Action` dataclass and hash shape;
- `lycheetah/sovereign_harness.py` — action hash, scope, expiry, authority metadata and nonce ledger;
- `34_ASSURANCE_RUNTIME/ASSURANCE_RECEIPT_SPEC_v0.1.md` — evidence/receipt conventions;
- `05_MICROORCIM_L5/essentials.md` — drift monitor's deceptive-alignment limitations;
- `35_ABSTRACT_AND_GENERATIVE/REGISTER.md` — generative/epistemic separation.

The repository contents were read via the connected GitHub connector. This environment did not have an authenticated git checkout or network transport to mount and import the upstream Python files, so **the new bridge has not been executed against upstream source**. Tests below use a synthetic fake implementing the documented upstream method shapes. Four real-upstream tests will run only in a checkout when `LYCHEETAH_REPO_ROOT` is configured. Do not misstate the current status as integrated or deployed.

## What the bridge actually contributes

`intent_bridge.py` adds a **trusted-host intention registry** to an existing fence:

- records a versioned current human-endorsed plan with an exact action hash;
- invalidates prior protected handles by calling upstream `revoke` first;
- calls existing `activate` to establish a fresh authority generation;
- serializes revisions via a separate SQLite journal's `BEGIN IMMEDIATE` transaction;
- checks journal generation and action hash before and after handle issuance;
- delegates commit-time finality **entirely to upstream** `CommitFence.commit`;
- stores no private narrative for refusal, only a coarse reason class;
- never computes a human free-will or worth score.

It is intentionally not another standalone security engine. Any effect-bound guarantee is inherited from upstream and limited by upstream's threat model.

## What this bridge does NOT provide

1. **Authentication:** the host must prove the human authorised the exact action. Strings and hashes do not authenticate people.
2. **Isolation:** the host must prevent untrusted agents from directly calling `CommitFence`, the bridge's owner operations, or the provider. Otherwise the bridge is bypassable.
3. **Atomicity across the two databases:** journal and fence cannot commit as one ACID transaction in this adapter. Serialisation protects the journal; revoke-first and generation matching force new **wrapper-issued** handles to fail closed on incomplete writes, but cross-store crash recovery and external call bypass must be formally audited before production.
4. **An immutable journal:** its event table is not signed, externally anchored or access controlled; it is a test fixture, not a trustworthy forensic log.
5. **External provider finality:** no real email, payments, network or other irreversible effects are under a shared SQLite commit fence. Already dispatched provider calls might succeed after revocation.
6. **Semantic consent:** understanding, coercion, manipulated defaults and information asymmetry require separate human study.
7. **Harm prevention:** even correctly authorised actions can be dangerous or unlawful; policy review is separate.
8. **Data portability / deletion compliance:** the offline interface and ledger do not implement those commitments.
9. **Machine sentience claims:** no mechanism here detects free will or consciousness.

## Correct integration path

Do **not** copy `choice_fence.py` from Forge III into production as an alternative gate.

1. Create a temporary branch in the user's actual repository checkout.
2. Copy only Forge IV's bridge, tests, and charter to a research directory; do not modify canonical source yet.
3. Run `PYTHONPATH=<ForgeIV> LYCHEETAH_REPO_ROOT=<RepoRoot> python -m unittest -v tests.test_real_upstream`.
4. Confirm the tests execute **without skips** and resolve any API divergence.
5. Add process-restart/crash-injection, external provider acceptance, shared-host authentication, alternate policy, and simultaneous-principal tests.
6. Review whether the intention journal should instead be implemented inside the upstream fence's *same* trust boundary/database, with an atomic grant transition. Consider an explicit `revoke_and_regrant_exact_intent` API rather than an independent adapter as production design.
7. Compare against a conventional generation-fencing baseline, not merely a deliberately weak pre-dispatch baseline.
8. Implement a human-facing comprehension test. Refusal should not require a narrative justification.
9. No release or effectful host integration until independent security review, reconciliation and documented provider limits.

## Safe reproducibility commands

```
cd sovereign_choice_forge_iv
python -m unittest discover -s tests -v
python demo.py
LYCHEETAH_REPO_ROOT=/path/to/Lycheetah-Framework python -m unittest -v tests.test_real_upstream
```

The `demo.py` program and the HTML prototype are offline educational simulations. Neither sends messages.
