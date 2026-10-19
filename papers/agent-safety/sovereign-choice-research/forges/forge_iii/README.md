# Lycheetah — The Right to Change Your Mind
## Sovereign Choice Protocol, Research Forge III

**Date:** 18 October 2026  
**Status:** `[LOCAL REFERENCE IMPLEMENTATION / REPRODUCIBLE SYNTHETIC COMPARISON]`  
**Human founder / final canonical authority:** Mackenzie Conor James Clark  
**Collaborative research and reference code:** Lycheetah × GPT-6  
**Repository status:** This packet has NOT been committed to GitHub. No external effects were executed.

> **An instruction is not perpetual ownership of the person who gave it.**

### What changed since Forge II

Forge II established an intention-versioned gate that decides whether to admit a request. It explicitly did **not** execute or control actual effects. Forge III extends that question to the **moment of local finality**: a person's revised intention or revocation is checked in the same SQLite transaction that records the mock consequential effect. The human's choice is treated as an **authority transition**, not an undesirable drift measurement of the person's character or free will.

We also compare against a deliberately weak pre-dispatch-only baseline holding the same original action and sequence of events. It demonstrates a familiar time-of-check/time-of-use failure, **not** superiority over Lycheetah's existing commit-time fence or any vendor.

### Files

- `choice_fence.py` — standard-library reference; host-owned clock, exact-action binding, versioned intention, revocation, local atomic finality, HMAC audit chain, toy weak baseline.
- `test_choice_fence.py` — unit, concurrency, interleaving, expected-boundary and negative tests.
- `benchmark.py` — six matched synthetic precheck/intervention/finality comparisons and two boundary examples.
- `results.json` — machine-readable, reproducible benchmark output.
- `docs/SOVEREIGNTY_DESIGN_CHARTER_v0.3.md` — refined Lycheetah definitions, brand promises, and user-experience obligations.
- `docs/ADVERSARIAL_FINDINGS.md` — evidence, threats, negative results, novelty boundaries, and integration constraints.
- `docs/USER_STUDY_PROTOCOL.md` — consent comprehension and meaningful-exit comparative study plan (not run).
- `docs/INTEGRATION_HANDOFF.md` — reuse existing GitHub `CommitFence`, `SovereignExecutionHarness`, and receipt infrastructure; no second production engine.
- `lineage/forge_ii/` — preserved Forge II source and prior v0.1/0.2 philosophy documents.
- `MANIFEST_SHA256.json` — digest inventory for this handoff (excludes itself and the ZIP).

### Run locally

```sh
cd sovereign_choice_forge_iii
python -m unittest -v test_choice_fence
python benchmark.py
```

Python 3.10+, standard library; no network or provider calls. Test counts in this draft: **37 unit tests passed** (including intentionally successful demonstrations of known limitations) and **6/6 synthetic comparison cases passed**. Verify in your own environment.

### Observed narrow results

Six intentionally constructed post-admission interventions each showed:

- Toy pre-dispatch-only baseline: remote-like simulated effect still accepted **6/6** times.
- SQLite-local commit fence: invalid local effect committed **0/6** times.
- The benchmark does **not** estimate real-world failure frequency; the weak baseline is intentionally insufficient.
- In the valid-control example, pre-revision work can be committed; a fresh ticket for a new intention can also be committed. Subsequent revision does **not** undo previously committed work.
- In 12 concurrent attempts to commit the same ticket, exactly one committed in the tested local run.

### Most important limits

- **No identity verification:** Owner-control methods (`issue`, `revise`, `revoke`) are trusted-host-only conventions; they are not protected from a malicious caller of this Python API.
- **No real effect boundary:** The only protected effect is `INSERT INTO local_effects` inside SQLite; a real email, payment, repository mutation, or platform posting is not atomically coupled to this SQLite database.
- **No special new cryptography:** Transactional fencing, least privilege, versioned authorization, idempotency, hashing and HMAC are established techniques. This is a composition and explanatory research artifact.
- **No proof of genuine autonomy:** No score or test here determines whether a person's intention was autonomous, informed, coerced, or morally worthy.
- **No independent audit anchor:** A valid prefix after suffix truncation can pass the local chain verifier. Anyone holding the key and database can potentially rewrite events.
- **No harm filter:** An appropriately approved but harmful action is not automatically safe. A test intentionally demonstrates that gap.
- **No remote cancellation promise:** A provider may accept a request after it has left a protected boundary. The effect may occur despite a later revocation and require reconciliation.

### Foundational claim

**Sovereignty is not demonstrated by an AI doing what it was first told. It is tested when its original plan conflicts with the person's current legitimate choice.**

The light you carry is not given; it is earned. And it remains yours.
