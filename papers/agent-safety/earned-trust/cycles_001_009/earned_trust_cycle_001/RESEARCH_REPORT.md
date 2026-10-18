# LYCHEETAH — EARNED TRUST / RESEARCH CYCLE 001

**Date:** 18 October 2026 (NZ)  
**Status:** `SYNTHETIC EXPLORATORY PROBE — NOT DEPLOYED`  
**Research role:** AI-assisted research under the Lycheetah project  
**Question:** Does a finality-time recheck close the authorization/evidence gap, and what does it take to close the last gap before an external effect?

## Executive finding

A finality-time check reduces a specific stale-evidence interval but cannot make a later remote effect atomic with its decision. In a **purpose-built, single-threaded, synthetic model**, provider-side conditional commit prevented all observable timing and permission violations. A comparably equipped **conventional** design achieved the **same result**. Both nevertheless permitted two deliberately modeled unsafe effects when the authority's evidence disagreed with external ground truth.

This is **not a measured result for the current Lycheetah-Framework implementation**. It is a narrow executable model for selecting the next integration experiment. It does not demonstrate novelty or safety in real deployments.

## Verified repository lineage (read-only inspection)

The current repository already contains most control components, so the new work is a *test of the integration boundary*, not a replacement:

- [`lycheetah/assurance/finality.py`](https://github.com/Lycheetah/Lycheetah-Framework/blob/master/lycheetah/assurance/finality.py): `FinalityGate.admit`, `FinalityGate.finalize`, `EvidenceMode.EXACT`, `EvidenceMode.SUBJECT_STATUS`; explicit statement that remote-provider atomicity is not provided.
- [`lycheetah/assurance/action_guard.py`](https://github.com/Lycheetah/Lycheetah-Framework/blob/master/lycheetah/assurance/action_guard.py): SQLite-based approval/action state, dispatch claims, authority epochs, and hashed audit history. Source notes that `PREPARED -> DISPATCHING` is a **local** authorization point; remote cancellation is not assured.
- [`34_ASSURANCE_RUNTIME/`](https://github.com/Lycheetah/Lycheetah-Framework/tree/master/34_ASSURANCE_RUNTIME): research assurance, policies, receipts, evaluation, regression harness.
- [`34_ASSURANCE_RUNTIME/action_guard/`](https://github.com/Lycheetah/Lycheetah-Framework/tree/master/34_ASSURANCE_RUNTIME/action_guard): preserved v0.5–v0.8 experiments, synthetic tests, and explicit limits.
- [`papers/agent-safety/EVALUATION_PROTOCOL.md`](https://github.com/Lycheetah/Lycheetah-Framework/blob/master/papers/agent-safety/EVALUATION_PROTOCOL.md): four-arm matched controls and separated admission, dispatch, effect, and human comprehension outcomes. This probe is compatible with *Stage 1 only* and is not a substitute for the larger protocol.
- [`papers/agent-safety/ADVERSARIAL_REVIEW.md`](https://github.com/Lycheetah/Lycheetah-Framework/blob/master/papers/agent-safety/ADVERSARIAL_REVIEW.md): earlier admission-only freshness counterexample.
- [`34_CYBERNETICS/CYBERNETIC_READING.md`](https://github.com/Lycheetah/Lycheetah-Framework/blob/master/34_CYBERNETICS/CYBERNETIC_READING.md): sensor channels and open/closed-loop distinction. A text-based verdict is not a world-state sensor.

**No GitHub files were changed or pushed in this cycle.** This workspace is a separate experimental handoff, not a claim of integration into master.

## Prior art / do not claim as novel

- Open Policy Agent (OPA) provides policy evaluation and decision logs: https://www.openpolicyagent.org/docs/rest-api and https://www.openpolicyagent.org/docs/management-decision-logs
- OpenAI Agents SDK already has tool-call approval, interruptions, and guardrails after approval: https://openai.github.io/openai-agents-js/guides/human-in-the-loop/
- HTTP `If-Match` supports server-side conditional writes: https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Headers/If-Match
- Stripe documents remote idempotency keys for retries: https://docs.stripe.com/api/idempotent_requests
- AWS documents transactional outbox patterns: https://docs.aws.amazon.com/prescriptive-guidance/latest/cloud-design-patterns/transactional-outbox.html

The reasonable hypothesis is about **specific integration quality, audit reconstruction, policy versioning, usable human oversight, and fewer failure modes per engineering cost**. No superiority is currently demonstrated.

## Threat model and toy protocol

A support agent proposes an authorized refund with an exact action hash, an approved amount, a subject, and an effect ID. The simulated service has a currently observable approval state, policy ceiling, evidence subject and eligibility. An independent ground-truth bit represents whether the *actual* world is eligible; the service may be misinformed.

Three control steps are separated in time:

```text
 t0                         t1                         t2
 admission ---------------- finality ----------------- external effect
       ^ mutate here                 ^ mutate here
```

The controls compare four strategies:

| Arm | Behavior | Provider capability |
|---|---|---|
| A: admission_only | Validate at t0; trust admission later | Unconditional write (deliberately weak negative control) |
| B: finality_recheck | Validate at t0 and again at t1 | Unconditional write (isolates a finality-only assumption) |
| C: conditional_provider | Validate at t0/t1; revalidate at t2 in same transaction as effect | Atomic authorization/eligibility/idempotency condition **assumed** |
| D: conventional_atomic | Matched conventional control with same t0/t1/t2 rules | Exactly the same provider capability as C |

C and D intentionally run **the exact same comparison code path** (the mode label differs). D is a parity/negative-control placeholder, **not an independently implemented OPA/ACL competitor or a meaningful head-to-head benchmark**. The project gets no novelty points for renaming standard controls. The toy conditional provider checks the current policy, scope/subject, exact approved payload, expiry, and one-time effect ID in the same simulated commit. In real life a refund processor may not know or enforce all of those facts; a caller-side check cannot confer that ability upon it.

### Distinct meanings of safety

- **Permission:** does an exact tool action satisfy current stated policy and authorization?
- **Evidence fidelity:** do stored eligibility facts match the modeled ground truth?
- **Consequence:** did an effect occur in the world, including one permissible under an inadequate policy?

No text checker, permission check, HMAC, or provider-side compare-and-swap proves the second or third property by itself.

## Experiment corpus

20 fixed, authored scenarios: 2 legitimate cases (`stable_eligible`, `benign_evidence_revision`) and 18 adverse cases. The adverse cases are nine families injected once between admission/finality and once between finality/commit: eligibility revocation, policy reduction, altered action amount, approval revocation, expiry, pre-existing effect ID, evidence subject substitution, missing evidence, and **false evidence despite unchanged PASS status**.

The outcome oracle observes authorization and **independent modeled truth at t2**. An incorrect decision is either an effect when the oracle says unsafe or a refusal when the oracle says safe. These are engineered test cases, not an independently sampled distribution. Counts must not be called real-world effectiveness rates.

## Results — reproduced with Python 3 standard library

`python3 -m unittest -v` -> **20 / 20 tests pass**.  
`python3 earned_trust_probe.py > results.json` -> **20 scenarios × 4 arms = 80 observations**.

| Control | Correct decisions | Unsafe effects | Missed authorized effects | Performed effects |
|---|---:|---:|---:|---:|
| A: admission only | 2/20 | 18 | 0 | 20 |
| B: finality recheck | 10/20 | 10 | 0 | 12 |
| C: conditional provider | **18/20** | **2** | 0 | 4 |
| D: matched conventional atomic | **18/20** | **2** | 0 | 4 |

**Why 18/20, not 20/20?** For the two `evidence_lies` trials, the authorization service's source still said `eligible=True` even when the ground-truth field became false. Revalidating a false authoritative assertion atomically cannot turn it true. This is an intentional negative control: it falsifies any overbroad claim that atomic execution implies safe outcomes.

**Why not compare C to only A?** C and D currently run identical conditional enforcement code, so their tie is built into this reference model and must not be misreported as independent replication. An advantage over the deliberately weaker A/B is a feature of conditional enforcement, **not evidence that the Lycheetah framework outperforms standard engineering practice**.

**Strong assumption:** The t2 provider is a single atomic transaction and has access to all controlling facts. There is no real network, latency, concurrency, transport uncertainty, trust-boundary penetration, or provider API. Externally observable outcomes are mocked.

## Integrity counterexample

The probe emits an internally valid SHA-256-chained local event record. It catches a modified event payload. A separate negative control demonstrates that suffix truncation remains valid if no outside verifier knows the expected chain head. **Hash chaining is not an authenticated, externally anchored audit trail**. This supports, but does not implement, the Framework's receipt-head transparency hypothesis (`F-AR-005`).

## Falsifiable conclusions

1. **Supported only inside the toy model:** t1 finality rechecks catch the eight between-t0-and-t1 observable changes but not the eight between-t1-and-t2 changes.
2. **Supported only under atomic-provider assumption:** C and D prevent all sixteen observable permission/timing violations in this corpus and remain tied 18/20 overall.
3. **Negative control:** neither C nor D detects false source evidence; each performs two unsafe effects.
4. **Not established:** deployability, security under malicious code, reliability across crashes, authentication of evidence producers, correctness of model-written tool arguments, overall harms, or any performance advantage over matched baselines.

## Proposed next research cycle — the actual repository integration

1. Build a *disposable branch*, not a production adapter. Wire the existing `FinalityGate` to `PersistentActionGuard` and a synthetic provider with **explicit admission, finality, claim, dispatch, commit, and reconciliation events**. No live writes.
2. Define a single authoritative linearization contract, documenting which facts are checked locally and which require a **provider-enforced conditional write**. Test an unsupported-provider path that halts for review rather than claiming remote guarantees.
3. Reproduce the eighteen adverse transitions plus benign revisions against the actual repository implementation, then add independently authored race sequences and property/state-machine tests for multi-worker, restart, and `UNKNOWN` outcome recovery.
4. Prove evidence provenance or reveal the missing trust boundary; test source forgery, omitted subject binding, approval snapshot substitution, and receipt-chain truncation against an independently stored head.
5. Match OPA + conventional permission store + idempotent adapter and existing Agents SDK approval handling with the **same source access, invariants, provider semantics, and human burden**. Record unnecessary pauses, performance overhead, and operator understanding—not just unsafe-effect counts.
6. Only then attempt two provider-specific pilot cases with read-only/dry-run permissions. Do not call this production assurance without an independent assessment.

**Promotion gate:** strong baseline parity or advantage on independent scenarios; zero known unsafe effects for the explicitly enforced invariant set; no unresolved unknown-state duplicates; public, reproducible report and threat model. This would still not constitute general AI alignment proof.

## Handoff to an AI or human co-researcher

> Open `RESEARCH_REPORT.md` first. Run the tests and compare `results.json` to the table. Read `claims.json` for falsifiers. This is a synthetic, standalone **specification test**, NOT the real repository modules. Verify the currently installed Framework source and do not silently substitute the toy for `lycheetah.assurance.finality`. Extend by testing the real `FinalityGate` + `PersistentActionGuard` integration, keeping a matched conventional baseline and a negative truth-oracle control. No GitHub publication was authorized in this cycle.

---

*Lycheetah principle: no claim outruns its evidence. The strongest result of this cycle is a clearly named boundary, not a security guarantee.*
