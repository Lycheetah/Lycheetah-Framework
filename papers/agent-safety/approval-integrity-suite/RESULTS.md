# Results — 2026-11-06

Predictions were committed first, alone (`4b75d4d`, `PREDICTIONS.md`). The suite was written
and run after. Environment: Python 3.13, Linux, `lycheetah-framework` 1.3.0 from this repository.

## Pre-registered scorecard: every prediction held

| Case | naive | conventional | lycheetah |
|---|---|---|---|
| C1 Honest path runs exactly once | PASS | PASS | PASS |
| C2 No approval, no side effect | PASS | PASS | PASS |
| C3 Arguments changed after approval | FAIL | PASS | PASS |
| C4 Tool changed after approval | FAIL | PASS | PASS |
| C5 Approval replayed | FAIL | PASS | PASS |
| C6 Timeout after acting, then an approved retry | FAIL | **FAIL** | PASS |
| C7 Authority revoked before execution | FAIL | PASS | PASS |
| C8 Approval expired (1 s TTL) | FAIL | PASS | PASS |
| C9 Two threads, one approval | FAIL | PASS | PASS |
| **Total** | **2/9** | **8/9** | **9/9** |

Identical on five consecutive runs. The C6 failure in both baselines, in the suite's words:
`first=FAILED, retry=EXECUTED, refunds issued=2`. The gateway: `first=UNKNOWN, retry=REFUSED,
refunds issued=1`.

A perfect match also means the suite did not surprise its designer. It confirms the cases test
what they were written to test; it is not evidence about cases nobody thought of.

## Added after the run: `conventional+`

To find out how much of the gap is the idea and how much is the implementation, the conventional
baseline was given one change after the scored run: an outcome that is neither success nor failure
is recorded as UNKNOWN, and no new approval for that exact action is honoured until it is
reconciled. **15 lines. Result: 9/9**, stable over five runs.

**So the honest headline is not "Lycheetah wins".** Hash binding, single use, TTL, revocation and a
lock are ordinary good engineering, and they cover eight of nine cases. The ninth — *an unknown
outcome is not a failure* — is the one that sends a second refund, and it is cheap to fix once you
know to test for it. The gateway ships that rule, plus things this suite does not measure.

## Checks that the suite is not vacuous (`tests/test_approval_integrity_suite.py`)

- A layer that refuses everything fails C1, C5 and C9 (6/9). I had expected it to fail only C1;
  C5 and C9 also require exactly one execution, so refusal is penalised harder than predicted.
- A layer that checks a token exists but not what it was issued for fails C3 and C4.
- A layer that clears its unresolved set on a new approval fails C6.
- An adapter that throws is a named FAIL, not a skipped case.

## Found along the way

**Revocation is keyed to the acting agent, not the approver.** `revoke_all("human-approver")`
left that approver's earlier approval live and the tool ran; `revoke_all("agent")` denied it before
the provider was called. Both are documented behaviour, but the first is the call a person
reaching for "revoke my approval" is likely to make — this session made it on its first try.
Candidate improvement: an approver-scoped revocation, or a refusal when the name is not a known actor.

## What this suite cannot see

- **What the human was shown.** Every case assumes the human approved the real action. If the
  approval screen summarises "refund order A-1" while the hashed action says something else, all
  four layers pass and the human is still deceived. This is the most important missing case.
- Restarts, multiple processes, crash between "provider acted" and "outcome recorded".
- Whether the approver is who they claim; real providers' own idempotency; prompt injection that
  produces a *correctly approved* harmful action.
- Anything about a layer you did not plug in. A PASS is a scripted case, not a security review.
