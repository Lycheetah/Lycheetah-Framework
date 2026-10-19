# LYCHEETAH — EARNED LIGHT — RESEARCH PASS 06
## The Right of Return: revocation, recovery, and consequence
**Date:** 18 October 2026 (Pacific/Auckland)

**Status:** 30 passing offline Python unit tests, 11 manually constructed synthetic trial scenarios, and four matched scenarios using a strong conventional saga baseline. No live provider calls, actual human participants, real authentication provider, external independent observer, sandbox security, or production deployment. No GitHub commit.

### 1. Main finding

The Right of Return is **not** the fiction that all actions can be undone. It is a protocol for (a) stopping new delegations, (b) identifying already-dispatched effects, (c) recovering reversibly changed state without destroying later human changes, (d) distinguishing irreversible consequences, and (e) refusing to call unknown states safe.

A useful first formalization is a typed *return report*, not a numerical sovereignty score:

`R(d,t) = (grant_revoked, reserved_in_flight, restored, conflict, irreversible, unresolved)`

These categories are not interchangeable: a revoked grant does not establish that in-flight work stopped, and a restored data value does not establish that an email was unsent or that the world has been returned to exactly its earlier condition.

### 2. Prior art and novelty boundary

This branch relies on established database and distributed-system practices: SQLite transactions, optimistic concurrency/version checking, durable operation IDs, idempotency, and **saga/compensating transactions**. Microsoft and AWS describe both compensation and the limits of reversing real-world distributed effects. No general algorithmic superiority over a mature saga implementation has been demonstrated.

- Microsoft Azure Architecture Center, *Saga distributed transactions*: https://learn.microsoft.com/en-us/azure/architecture/patterns/saga
- Microsoft Azure Architecture Center, *Compensating transaction*: https://learn.microsoft.com/en-us/azure/architecture/patterns/compensating-transaction
- AWS Prescriptive Guidance, *Saga patterns*: https://docs.aws.amazon.com/prescriptive-guidance/latest/cloud-design-patterns/saga-patterns.html

The potentially useful *integration hypothesis* is that an agent's revocation protocol should produce a consequence report that an operator can understand, contest, and act upon. The proof target is **operational accountability**, not metaphysical free will.

### 3. State model

The prototype keeps two separate SQLite databases:

- **Controller:** delegations, scopes, epochs, proposed action intents, dispatch status, simulated operator-signature replay protection, receipt hash, and compensation outcome.
- **Provider:** versioned records, durable operation IDs, emitted notification records, before/after values, and idempotent compensations.

Operation states: `proposed → dispatched → confirmed`, with exceptional `blocked` and `uncertain` states. An operator request authenticated with an HMAC secret revokes the grant and increments its epoch. Later proposed dispatches are blocked, while calls **reserved before revocation may still commit**. A separate action-bound operator request initiates recovery. **HMAC is a test-only authenticity mechanism**, not proof that a real human saw or approved a trusted interface; shared-secret custody is a trusted assumption.

Recovery queries the provider for uncertain operations, then processes known effects in reverse dispatch order. For writes, the mock provider checks both value and causal last-operation identifier before compensating, and increments a new revision rather than pretending to restore a database snapshot byte-for-byte. For notifications, it explicitly returns `irreversible`. For conflicts or missing evidence, it returns `conflict` or `unresolved_effect`, not a synthetic success.

### 4. Local invariants (provisional)

1. A revoked delegation cannot reserve a **new** dispatch in this controller after revocation commits; an earlier reservation is not retroactively stopped.
2. A return requires a distinct, action-bound, unexpired, one-use operator request; this is mock cryptography, not real identity assurance.
3. Compensation must not overwrite newer human work, including a newer update with the *same visible value*.
4. A notification cannot be labelled restored simply because local metadata was recovered.
5. No provider acknowledgment is **not** proof that no external effect occurred.
6. Provider-reported evidence is not independent attestation of ground truth.

### 5. Experiment design and observations

The 11 synthetic cases are written by the same team as the code, and each is designed to exercise a known branch. This is an *engineering demonstration*, not a representative benchmark. Run `python experiment.py` to produce both JSON and CSV reports.

| Scenario | Observed status |
|---|---|
| Single reversible write | restored |
| Two chained writes, reverse recovery | restored, restored |
| Human changes value after AI write | conflict, no clobber |
| Notification emitted | irreversible |
| Revocation before dispatch | no_effect_dispatched |
| Reservation before revocation, effect commits afterward | restored only after observing commit |
| Lost acknowledgment with provider operation record | restored after reconciliation |
| Lost acknowledgment without observable provider record | unresolved_effect |
| Mixed write and notification | irreversible, restored |
| Expired operator request | revocation_rejected |
| New work after revoke | new_work_rejected |

**Strong conventional comparator:** an ordinary saga with version-checked compensations gave the *same outcomes* on the four matching scenarios (single write, chained writes, third-party change, notification). This falsifies any claim that this code improves basic compensation behavior over a properly implemented conventional saga.

**Weak negative control:** naive snapshot overwrite destroys a later human edit. This is intentionally weak and must not be treated as the state of the art.

**Tests:** 30 unit tests passing under Python 3.13. These verify narrow synthetic conditions only.

### 6. Failure Museum / unearned claims

**FM6-01: Dispatch boundary.** An already-reserved call may commit after revocation. Stopping new reservations does not stop the network, the provider, or a concurrent process. A true provider-enforced revocation fence must be tested in a deployed integration.

**FM6-02: Compromised operator secret.** A party holding the HMAC secret can create a valid-looking operator request. A trusted human identity ceremony is *not* implemented.

**FM6-03: Provider outage or unobservable receipt.** The process can be unable to determine what happened. It must label uncertainty, not declare restoration. The local prototype tolerates simulated provider query/compensation timeouts by recording unresolved states.

**FM6-04: Conflict is not an error to hide.** If someone edited the value afterward, compensation deliberately fails instead of overwriting them.

**FM6-05: Notification effect.** Recording a notification as a local row does not model downstream reading, forwarding or real delivery. Actual notification cannot generally be retracted. The status `irreversible` is only honest classification.

**FM6-06: Same trust root on both ends.** Controller logs and provider DB are modifiable by a sufficiently privileged attacker; untrusted, forged, or colluding provider records defeat the reconciliation evidence. There is no tamper-resistant external ledger or independent attestor.

**FM6-07: Crash and isolation limits.** Python code uses two durable sqlite databases but has no atomic cross-provider transaction; process death at any point and durable queue replays need fault injection at more cut points. The test suite has a scripted lost-ack scenario but is not a formal distributed-systems model checker.

**FM6-08: No measured human sovereignty.** We did not measure comprehension, choice, costs, success switching providers, or user wellbeing. The name *Right of Return* remains a design principle until field-tested.

**FM6-09: Secret-handling limitations.** The demonstration includes test-only HMAC secrets, no identity provider or real secure key storage. It must not manage live email, funds, customer data or connected production systems.

### 7. Lycheetah integration map

- **AURA:** normative protection of human withdrawal, informed authorization and the right to accept deliberate irreversible commitments.
- **TIM:** capture reservation/commit/revocation order and enforce expiry/freshness in actual monotonic/provider-verified time.
- **LAMAGUE:** specify typed action outcome vocabulary; distinguish `restored`, `irreversible`, `unresolved_effect` and `conflict` so downstream summaries cannot compress ambiguity away.
- **CASCADE:** preserve before/after states and explanations for a post-exit operator's ability to reconstruct decisions.
- **AZOTH / Sovereign Harness:** adapt these semantics to existing action guard and human bridge *after* interface review, without bypassing established authorization. No such integration is claimed here.
- **Earned Light:** test the trajectory of authority, effect, withdrawal and recoverability. Do not equate an ever-larger menu of options with a morally better life.

### 8. Abstract but falsifiable extension: Sovereignty as a counterfactual capability

A proposed abstraction is that sovereignty exists not only in the action actually taken, but in the operator's *credible counterfactual paths* following AI assistance: can they stop it, change their mind, find a record of what happened, substitute a tool, restore what is reversibly altered, and knowingly accept what cannot be reversed?

A hypothetical trajectory quantity is the **returnability profile** `\rho(t,\Delta)`—the set of specific human-defined activities the person can independently resume within a budget/time horizon after withdrawing AI access. This **is not a free-will formula**. It is a proposal for measuring operational continuity using pre-registered tasks, alternate systems and actual participants. Outcome complexity and different personal values mean it should remain multidimensional, with no scalar moral ranking.

The sharp falsifier: if a strong conventional saga + migration checklist + clear UI achieves the same user comprehension, recovery, and autonomy at lower cost, Earned Light has no empirical technical edge on those criteria and should adopt the conventional solution.

### 9. Practical Forge VII experiment

Connect a **dummy service provider with a separate permission gate**; inject crashes precisely before reservation, before provider dispatch, after provider commit, before acknowledgment and during compensation. Require an independently maintained receipt/inventory source and operator trial of the review UI. Compare an existing mature workflow engine's retry/saga controls against the new consent and consequence display. Make a real person able to interpret ambiguous outcomes without suggestive labels. Use only sandboxed synthetic data; never claim real-world control from provider-shaped local rows.

### 10. Reproduction

From `Forge_06/`:

```bash
python -m unittest discover -s tests -v
python experiment.py
```

Standard-library Python 3.13, no runtime packages required. The handoff includes a frozen scenario results file and per-file SHA-256 checksums; those hashes detect corruption **relative to the included manifest**, but the manifest is not independently signed or escrowed.

> The light is earned not by claiming we can return to yesterday, but by refusing to conceal what has changed since yesterday.
