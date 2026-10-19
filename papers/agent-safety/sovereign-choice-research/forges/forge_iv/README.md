# Lycheetah Sovereign Choice — Forge IV

**18 October 2026 · Proposal + local reference implementation + offline demonstration**

> **An instruction is not perpetual ownership of the person who gave it.**

**Research outcome:** added an *intention semantics bridge* designed to sit over Lycheetah's **existing** commit-time authority fence, instead of duplicating its security mechanism. The adapter turns a recorded revision or withdrawal into a revocation plus a new generation, while preserving a human-readable intention version and exact action hash.

### What's here

- `intent_bridge.py`: thin trusted-host adapter to upstream `CommitFence`-shaped interface; separately journalled intention revisions; no duplicate protected sink.
- `epistemic_boundary.py`: deliberately refuses to infer consent, coercion, free will or worth from plan adherence.
- `tests/test_intent_bridge.py`: **24/24 passed** local contract tests using a clearly labelled synthetic `FakeFence` (not original upstream code).
- `tests/test_real_upstream.py`: **4 tests prepared, skipped locally**, runnable in a real `Lycheetah-Framework` checkout.
- `demo.py`: small reproducible text/JSON simulation.
- `prototype/sovereign_choice_demo.html`: attractive, self-contained offline choice/revision/cancellation interface. No external effects.
- `docs/SOVEREIGN_WILL_CHARTER_v0.4.md`: the philosophical result and counterfactual measurement proposal.
- `docs/INTEGRATION_LIMITS_AND_HANDOFF.md`: exact known limits, threat model and adoption path.
- `results.json`: reproducible output and test footing.
- `lineage/FORGE_III_COMPLETE.zip`: full historical Forge III archive (containing Forges II and the original v0.1 charter).
- `MANIFEST_SHA256.json`: file integrity manifest.

### Tests

Run with Python 3.10+ (standard library):

```sh
cd sovereign_choice_forge_iv
python -m unittest discover -s tests -v
python demo.py
```

To run **actual upstream integration tests** from a repository checkout:

```sh
export LYCHEETAH_REPO_ROOT=/path/to/Lycheetah-Framework
python -m unittest -v tests.test_real_upstream
```

**Evidence status:** 24 local contract tests passed and 4 actual-upstream tests skipped in this environment. No claims of real-provider guarantees, authenticated identity, user comprehension, universal safety or independent validation. No GitHub writes made.

**Philosophical result:** An authentic change of intention must not be scored as an inherently defective act of will. Human sovereignty is tested most sharply when the human disagrees with the machine's earlier plan.

*The light you carry is not given; it is earned. And it remains yours.*
