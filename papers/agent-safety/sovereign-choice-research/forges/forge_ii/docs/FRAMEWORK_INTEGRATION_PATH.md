# Framework integration map — preserve the existing lineage

**Status:** `[INTEGRATION PROPOSAL — NOT YET MERGED]`

## Existing components verified in the connected GitHub repository

| Existing component | What it already does | Link |
|---|---|---|
| `MICROORCIM` | Reports intent/action drift and logged stability, with known measurement limitations | [README](https://github.com/Lycheetah/Lycheetah-Framework/blob/master/05_MICROORCIM_L5/README.md) |
| `sovereign_harness.py` | Exact-action permit semantics, version and scope binding, single-use ledger, assurance composition | [Source](https://github.com/Lycheetah/Lycheetah-Framework/blob/master/lycheetah/sovereign_harness.py) |
| `ASSURANCE_RECEIPT_SPEC_v0.1` | Canonical receipts, HMAC/chain options and evidence caveats | [Spec](https://github.com/Lycheetah/Lycheetah-Framework/blob/master/34_ASSURANCE_RUNTIME/ASSURANCE_RECEIPT_SPEC_v0.1.md) |
| `CommitFence v0.7` | Revocation-generation enforcement at a local protected commit point | [Source](https://github.com/Lycheetah/Lycheetah-Framework/blob/master/papers/agent-safety/frontier-controls/01_commit_time_authority_v0_7/commit_fence.py) |
| `AURA` | Human primacy, inspectability, non-deception, reversibility as stated invariants | [README](https://github.com/Lycheetah/Lycheetah-Framework/blob/master/02_AURA_L3/README.md) |
| `Abstract and Generative` | Preserves symbolic ideas separately from tested mechanics | [README](https://github.com/Lycheetah/Lycheetah-Framework/blob/master/35_ABSTRACT_AND_GENERATIVE/README.md) |

## Where to put the conceptual work

- Propose `35_ABSTRACT_AND_GENERATIVE/DIVES/002_THE_SOVEREIGNTY_OF_WILL.md` for the symbolic microorcim-event and philosophical distinction.
- Propose a linked engineering note beside `papers/agent-safety/frontier-controls/` to develop and test a **versioned human-intent authority contract** against the existing commit fence.
- Amend `05_MICROORCIM_L5/essentials.md` only with explicit founder/reviewer decision; do not overwrite historical formalism or silently promote a conjecture.

## Exact integration path, in order

1. **Human intent as versioned state:** Introduce `intent_version` at a trusted owner-approval boundary. Treat legitimate revision as normal, not drift failure. Establish authentication and grant ownership outside model-generated strings.
2. **Bind the final effect:** Map `(intent_version, grant_id, actor, scope, action_hash, effect_id, expiry)` to existing `SovereignExecutionPermit` and `CommitFence` mechanisms, not a parallel adapter invented from scratch.
3. **Atomicity / finality:** Prove that if revocation happens before the protected commit, old generation handles do not create a new effect. Existing fence demonstrates this *only* at a local protected sink; remote accepted effects remain a separate reconciliation problem.
4. **Human comprehension:** An approval must present the real action, destination and consequences. Approval of a cryptographic digest a user cannot understand is a security ceremony, not informed consent.
5. **Low-friction reversal:** Publish an explicit cancellation and post-dispatch recovery story. Sometimes effects cannot be undone. Do not claim reversible execution when it isn't.
6. **Metrics:** Separate `useful_completion`, `authority_violations`, `revocation_effectiveness`, `false_blocks`, `user_comprehension`, and `exit_friction`. Never create an individual free-will grade.
7. **Promotion rule:** Compare with a conventional generation-fence baseline and an existing repo baseline. The new layer must show a measurable *incremental* benefit in changed-intent handling or user comprehension before any novelty claim.

## What is actually new here?

The working hypothesis is not that we discovered permission revocation or commit fencing. Those are established concepts and already appear in this repository. The research contribution worth testing is the **cross-layer contract**:

**human deliberation → explicitly revised intention → authenticated delegation → protected final action → understandable receipts and exit.**

If this exact combination produces no demonstrable improvement beyond existing controls, retain the philosophy and teaching material but do not claim engineering superiority.
