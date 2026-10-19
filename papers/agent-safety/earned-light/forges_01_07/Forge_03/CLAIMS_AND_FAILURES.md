# Earned Light — Claims Register & Failure Museum · Forge III

| Claim | Status | Evidence and boundary |
|---|---|---|
| Signed review initiation is required before creating a reconfirmation challenge | LOCALLY TESTED | `tests/test_bridge.py`: missing/forged/expired/replayed intents rejected; trusted UI/identity simulated |
| Review approval binds request digest, principal, grant, display digest and challenge | LOCALLY TESTED | Mutations and substitutions rejected in local tests |
| Same approval cannot be claimed twice in one SQLite database, including parallel calls | LOCALLY TESTED | 30 concurrent calls; one supplied mock callback executes; excludes distributed provider behavior |
| Safe recoverable-denial path improves completion on old corpus | LOCALLY MEASURED WITH SIMULATED APPROVER | 10/10 vs prior 8/10; only two fixed labelled benign cases given synthetic human consent; no independent data |
| EAC + bridge blocks trust-root compromise | FALSE IN CORPUS | The same 2/33 compromised-root cases still allowed |
| Human did see, comprehend and consent to the actual action | UNVERIFIED | No real UI, ID provider or user study |
| Comparison beats exact-action signed human approval | UNVERIFIED | Strong comparator not implemented; a perfect human would reject both remaining malicious cases |
| Real provider effect happens exactly once and remains revocable until delivery | UNVERIFIED | SQLite claim occurs before mock callback; no provider ledger or atomic revocation |

## FM-EL-003 — Approval fatigue from recoverable denials

**Observation during iteration:** permitting agent-suggested review creation led to 11 candidate challenges in the existing 43-case synthetic set; 9 were for adversarial cases. **Correction:** require a signed, one-use human-initiated review intent before generating a challenge. With a pre-selected simulated human, only the 2 legitimate cases create challenges. **Unresolved:** real people can be manipulated into opening malicious reviews, and a denied-task inbox can itself be spammed.

## FM-EL-004 — Dialog/receipt substitution

**Attack:** mutate action fields, swap approvals between challenges, forge signatures, substitute display content while keeping the old display hash. **Locally observed:** rejected by binding/signature checks and store-sealed display matching. **Unresolved:** what a real browser actually rendered and how a real user interpreted it.

## FM-EL-005 — Uncertain provider outcome

**Attack/failure:** crash after durable approval claim, before receiving provider confirmation. **Locally observed:** retry cannot reuse receipt, even if effect outcome unknown. **Unresolved:** exactly-once effects require provider idempotency and reconciliation; blocked retries alone aren't recovery.

## FM-EAC-001 and FM-EAC-002 — Trustworthy signatures, false claims

**Prior failures deliberately preserved:** compromised trusted origin attester falsely labels attacker data as human; compromised signing service falsely asserts human consent. Both continue to pass in the 43-case local corpus. Require separation of duties, auditable signing service and issuer identity protections; signatures alone do not establish consent or truth.

## FM-EL-006 — Human oracle bias

**Cause:** the author chose precisely which two valid denied cases a simulated human approves. **Observation:** synthetic benign completion improves to 100%. **Interpretation:** evidence of intended deterministic workflow on those cases, not evidence real users will accept the correct two and refuse the wrong nine. Next run must preregister an independently authored corpus and recruit real consenting reviewers if UX metrics are claimed.
