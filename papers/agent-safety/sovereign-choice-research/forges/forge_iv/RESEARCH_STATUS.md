# Research status — evidence claims and exclusions

- `[PROPOSED]`: Charter v0.4, philosophical treatment of reasons-responsive choice, revised intentions, the right to refuse, and exit obligations.
- `[IMPLEMENTED-LOCAL]`: `IntentAuthorityBridge`, small persistence layer translating a human-authorised revision/withdrawal into `CommitFence`-shaped revoke/activate calls, with exact-action comparison.
- `[TESTED-LOCAL CONTRACT]`: 24 self-authored tests with **FakeFence**; tests exercise business logic, sequencing, concurrent bridge instances, invalid/stale actions, and no-free-will-inference policy.
- `[PREPARED-NOT RUN]`: Four additional tests that import the **actual** upstream `CommitFence` and `research_support.Action`. Environment variable `LYCHEETAH_REPO_ROOT` must target the real checkout. This forge's machine has no mounted checkout.
- `[DEMONSTRATION]`: HTML/JSON simulation; all effects synthetic and in-memory. No real email was sent.
- `[NOT TESTED]`: trusted host/identity authentication, semantic consent, coercion, real provider cancellation, actual upstream integration, tamper-resistant journal, external audit, production crash consistency, end-user comprehension, comparative task utility, longitudinal effect, and independent security review.
- `[NOT CLAIMED]`: physical units of will, free-will proof, AI moral status, unique invention of fencing, improved production safety, real-world efficacy.

## What would count against the research

A passing unit test is narrow. Material failure would be:

1. A validly revoked action produces a **new** protected effect after revocation's finality point.
2. A new version silently retains old powers or accepts an altered recipient/message without a fresh exact-action approval.
3. A user cannot identify what they approved or is manipulated into agreement in realistic UX trials.
4. A real provider accepts stale in-flight requests at unacceptable levels without the product disclosing those limitations.
5. A well-matched existing control architecture demonstrates equal or better safety/utility with fewer components.

**Test rule:** preserve negative results and demote claims rather than rename a failure as symbolic success.
