# Output 6: Final report

**Reviewer:** Sol (Claude Opus 5.5, xhigh effort) · **Reviewed:** 2026-10-20 to 2026-10-23 · **Scope:** the whole `Lycheetah-Framework` tree on `master`, in 38 batch ledgers plus a close-out (B39).

**This is an AI review of a repository by the same AI family that helped write much of it. It is not independent validation.**

## Verdict in one paragraph

The engineering is in better shape than the public claims. The shipped package has a clean boundary, its suite is green (1,571 passed, ×3), and its claims gate holds. The weak point is the line between what the canon says and what the evidence shows:

- 23 claim references point at missing files.
- 4 ACTIVE claims meet counterexamples or mismatches.
- 11 of 13 defense receipts cannot be regenerated.
- "Pre-registered" means drafted.
- No human outside the project has replicated anything.

Every one of these can be fixed, and the fixes are listed in order in [OUTPUT5](OUTPUT5_REPAIR_SEQUENCE.md).

## What survived (MEASURED or DERIVED, each with its ledger)

- **The package boundary.** `lycheetah/` imports no research folder, and `examples/` imports only `lycheetah/` (B37 A5).
- **The test suite.** 1,571 passed, 1 skipped, 2 strict xfails that hold known mathematical departures on purpose.
- **The gates that have been seen to fail:**
  - The claims gate pins the public numbers; HOLDING, 3 unmarked.
  - The scripture hash gate.
  - The LOOP_MAP gate refused an unregistered reader.
- **The UCC verdicts** in `33_APPLICATIONS` (B22).
- **About two-thirds of the checked mathematical items** (M1–M18), under the conditions stated in [B38](BATCH38_FINDINGS_AND_LEDGER.md).
- **26 findings were re-checked and hold.** See the "checked, holds" rows in [OUTPUT1](OUTPUT1_FINDINGS_REGISTER.md).

## What failed and was fixed in the tree

170 findings, all listed in OUTPUT1. The most consequential:

- The crisis page said lines are open 24/7 when they close at midnight.
- A renamed blind pack was counted as a second reviewer.
- A living scholar's iwi was misattributed.
- Two false facts about named people were in an outreach draft.
- The status register reported an INVALID registry as VALID.
- One module had two identities.
- The closed-loop lab broke on a clean clone.
- A persona result was called "not significant" because of a statistics error.
- The private repository's name appeared in public files.

## What failed and is still open

There are 300 open findings and 21 staged patches, counting the B39 close-out. The ones that matter most:

- G-TP-ANNOTATION-INTEGRITY has a deadline.
- The outbox payload binding is broken, and the shipped `finality` has not been probed for the same defect.
- G-M-1 (4 ACTIVE claims against counterexamples).
- The 23 missing references.
- The master equation and the Lyapunov argument.
- Hosted CI is locked.
- The cascade-pc local API.

## What was not examined

- **8 areas (127 files) and 9 root files** were never named by a batch. They had a README-level census only (B39-R5).
- **583 of 606 folders** keep their census-only label. A per-folder relabel was never computed.
- Inside reviewed areas, many files were classified by folder rather than read. For example, about 60 in `14_MYSTERY_SCHOOL`, and 44 in `18_EXPERIMENTAL`'s hybridisation line.
- **Prior art and novelty are UNVERIFIED for all 71 claims.**
- The private app repository and the personal vault's contents were out of scope by rule.

## What did not run

| Item | Reason |
|---|---|
| Hosted CI | GitHub billing lock |
| ruff and mypy | No venv after the reboot |
| Wheel build and install | Not run |
| cascade-pc as an app | Not launched |
| `generate_defense_bundle.py` | `fpdf` missing |
| `promote.py` | A launch decision, which is Mac's |
| v0.8 collector | Forbidden until its secrets patch lands |
| Paid providers | Never called under review-only authority |
| History secret scan | Not run (G-RV35-4) |

## What needs outside validation

Everything in the canon that is called a result: the 71 claims, the AI Future wings added on 2026-10-23, and this review itself. The first outside witness should be a human mathematician on M1–M18. The second should be a security reviewer on T0.

## Where the outputs are

[OUTPUTS_INDEX.md](OUTPUTS_INDEX.md)
