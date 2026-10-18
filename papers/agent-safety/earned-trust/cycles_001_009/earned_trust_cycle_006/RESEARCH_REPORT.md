# Research Report — Who Watches the Witnesses?

**Track:** Lycheetah / EARNED TRUST · **Cycle:** 006 · **Date:** 2026-10-18 NZ
**Evidence:** `LOCAL_SYNTHETIC_ENGINEERING_TESTED`. No external validation, real-framework test, deployment, calibration or general agent safety claim.

## Research question and baseline

C005's witness quorum accepted evidence when a trusted source registry described two HMAC-authenticated observers as having disjoint ultimate roots and control domains. However the registry was an ungoverned operator assertion. Could auditable governance of source assertions distinguish an *unchallenged claim of independence* from *a contested one*, without falsely presenting policy process as proof of independence or truth?

Control A: C005 naive distinct-signer quorum, which knows signatures but not source ancestry or governance events. Control B: C006 governed provenance quorum, adding two reviewer organizations to changes and an authorized auditor's contested-source suspension. Control C: conventional independent pair-selection with equivalent governance checks and the same trusted input verification. Control C is not independent security review: it shares witness signature verification, source graph and event-history validation with B.

## Exact experimental contract

An operator roster declares reviewer/auditor roles, organization affiliation and lab HMAC keys. The signed governance event binds sequence, previous head, operation type, target source and exact fields. Source patches require two different reviewer organizations, neither identified as the source controller; challenges require an auditor; dismissing or remedying a dispute requires two independent reviewer organizations. `REMEDIATED` also requires a source patch after the challenge (but does not prove the patch was adequate). Event history is replayed and checked against an **externally supplied** exact checkpoint. The code itself cannot establish that checkpoint came from an independent and durable authority.

Every observed witness binds its C005 signed statement digest to an exact governance head with an additional lab HMAC. A later governance revision invalidates old bound reports even if the underlying statement has not changed. A live challenge suspends descendant witness pathways during evaluation, but not unrelated witnesses. The local registry serializes updates within one Python process, with accepted event content copied before storage.

One narrow notation for accepted evidence: for a candidate witness set W, each source lineage must be current and uncontested, and there must exist at least two witnesses whose **declared** root sets and controller sets do not overlap. This is a logical test of declarations, not a measurement of actual information independence.

## Executed results

- **59/59** local Cycle 006 tests passed (51 contract/adversarial tests, eight comparisons).
- A 12-thread simultaneous reuse of one exact signed operation yielded **one accepted registry revision and 11 rejected stale/replayed attempts**, in the local in-memory control.
- The 20 fixed, author-authored scenarios had these decision counts:

| Mechanism | CONFIRMED | REVIEW | CONFLICT |
|---|---:|---:|---:|
| C005-style naive signer quorum | 13 | 6 | 1 |
| C006 signed governance + provenance | 6 | 13 | 1 |
| Matched conventional governance rules | 6 | 13 | 1 |

The governed path differed from naive confirmation on cases including shared-origin disclosure, signed challenge, stale registry binding, missing/stale external checkpoint, forged binding MAC and duplicated witnesses. It also left genuinely separate, declared uncontested paths available during an unrelated challenge. **No empirical false-positive/false-negative rates can be inferred from an authored corpus.** The extra seven reviews could have substantial operational costs.

All 20 candidate/baseline decisions agreed. No framework terminology conferred a performance advantage over equivalent conventional rules. Across the archived six research cycles, **238 passed locally authored test-method runs** were rerun in this container (20, 29, 50, 38, 42, 59); these tests are neither externally constructed cases nor independent validation.

## Four important negative controls

1. **False independent-world assertion:** both genuinely disjoint declared sources attest TRUE to a fact the fixture separately marks FALSE. C006 returns `CONFIRMED`. Cryptography and procedure preserve a false statement faithfully.
2. **Concealed common origin:** the registry declares two roots as disjoint even though the synthetic underlying world flag says both rely on the same origin. It still `CONFIRMED`. Dual review cannot reveal dependencies its administrators do not know or disclose.
3. **Observation rebinding:** the observer can sign an unchanged old statement under the new registry head. The gate `CONFIRMED` after an unrelated registry patch or dismissed challenge without proving that a new source observation occurred. Ledger-version freshness is not observation freshness.
4. **Admission-to-dispatch timing:** an initial `CONFIRMED` is obtained. A signed source challenge then arrives; the fresh C006 evaluation becomes `REVIEW`. The old `CONFIRMED` object remains in the caller's hands and could be used if dispatch fails to revalidate. This is the next exact action-boundary target, not something C006 solves.

An auditor can also submit a technically valid but spurious dispute and halt a path, while two reviewer organizations can dismiss a genuine objection or approve a false source update. Both are policy/governance failure possibilities rather than cryptographic failures.

## Security and provenance ceilings

- HMAC does not provide nonrepudiation or independent human identity. Keys, authority roster, claimed organization boundaries and graph links are all lab-authored.
- Event hashes and HMACs are tamper-evidence within a model with protected keys and an independently retained current checkpoint, not protection from wholesale key compromise or complete state replacement.
- This implementation is in-memory and process-local; it has no durable multi-host consensus, crash recovery, replay protection across service replacement, or provider-backed compare-and-swap.
- Operator-specific authority checks and witness binding rely on application inputs. Missing true authorization, wrong human approval flags, wrong source truth, malicious insiders and credential compromise remain out of scope.
- Source disagreement routes to `REVIEW`, not a guaranteed external pause. The caller must enforce that pause at the effect boundary.
- The naïve baseline is intentionally weaker, but the matched conventional baseline has identical rules and outcomes. No novelty or increased real-world safety is claimed.

## Real-framework status

GitHub `Lycheetah/Lycheetah-Framework` master was independently inspected through its connected repository API at commit `d4a65ff64efa0a512c5c07ca64f6ec76242dd775` (2026-10-17 UTC). Earlier source inspection found `FinalityGate`, `AssuranceRuntime` and `PersistentActionGuard`, but this container cannot resolve the GitHub host to clone a checkout. Re-running the existing Cycle 005 four-case bridge locally yielded `ModuleNotFoundError: No module named 'lycheetah'`. **Zero real-framework code paths were exercised in Cycle 006.** See `framework_bridge_attempt.txt` and `INTEGRATION_HANDOFF.md`.

## Next falsifiable target: dispatch-time governance fencing

A service accepting an effect must capture an exact governance head and apply the current verification and action claim within one trusted dispatch decision, then require remote state reconciliation or provider conditional-write enforcement. This should be measured against a **matched, ordinary conditional transaction plus audited policy controls**, under adversarial revocation/appeal races. A formerly accepted action must not be permitted to bypass a later challenge merely by replaying its admission witness, unless a clearly documented provider linearization point has already been crossed. Test both adverse effects and false reviews, including an auditor-triggered denial-of-service cost.

### Preregister before doing external claims

Use a frozen attack corpus written outside the implementation team; pre-label source overlap, authority identity, permitted side effects and later provider state. Measure wrongful confirmed actions, missed false assertions, legitimate-action review rates, race outcomes, operator workload and false challenge impact. External operators should manage signing keys, registry assertions, anchors and outcome observation independently of the agent under test.

**Bottom line:** C006 formalizes governance of declared witness independence and can reliably pause on a challenge in a local experiment. It does not make a declaration true, a witness independent, or a past authorization revocable. Veritas before victory.

An initial assertion in an early unit test expected the wrong rejection reason on substituted statements; the actual MAC check correctly fired first. `EARLY_TEST_EXPECTATION_FAILURE.txt` preserves that failed test output, and the assertion was corrected before the final passing run.
