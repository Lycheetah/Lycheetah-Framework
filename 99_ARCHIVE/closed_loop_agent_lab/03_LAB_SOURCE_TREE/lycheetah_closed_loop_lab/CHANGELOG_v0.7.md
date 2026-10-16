# v0.7 change log — 2026-10-16

- Added separate-process host/provider harness with two durable SQLite stores.
- Added durable authority policy revisions and explicit `set-policy`; file edits alone no longer silently change the active policy.
- Added provider-side local policy and approval-revocation fencing during fake effect commit.
- Added stable operation ID + exact payload digest idempotency and foreign-payload conflict handling.
- Tightened recovery: `APPROVED` is not dispatchable via recovery, `COMPLETED` with a missing provider record routes to review, and effects lacking a durable claim are surfaced as conflicts.
- Added crash injection before provider commit, after provider commit, after provider response, and during recovery; added update/revoke race tests.
- New v0.7 suite: 26 tests passed. Combined retained suite target: 91 tests, if all previous 65 remain green.
- This pack remains local research and is not committed to GitHub or integrated into Lycheetah Guard.
