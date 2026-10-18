# Failure Museum — Cycle 10

## F10-01: A signed permit is not a reviewed screen

v0.9 enabled a test script to sign an exact batch, but there was no reviewer interaction. v1.0 now has a local evidence screen, session and explicit action. It still cannot attest that a person read or understood the screen. **Preserved limitation:** a scripted browser with the correct local password can approve the batch.

## F10-02: Effective dates were initially schema-only

First reviewer screen exposed `valid_from` and `valid_until` only as raw field names. A usability test expected the human-readable concept *effective*. We added explicit 'Effective from/until' labels and re-ran the tests. Cosmetic fix, not an external usability study.

## F10-03: Review session time may be idle time

`session_elapsed_seconds` is the monotonic interval between opening the review and pressing the action. It cannot measure reading or comprehension. Present it as **local session elapsed time**, never verified reviewer effort or a cost saving.

## F10-04: The signer and reviewer share a process

The loopback server holds the HMAC secret. Password possession gets a session that can request signatures through the server's normal approval flow. It is not isolated from Python process compromise, OS account compromise, or filesystem writes. Protected signer and per-reviewer identity remain open work.

## F10-05: Rejection history is not durably committed

A local rejection changes no knowledge and is kept only as a `ReviewOutcome` in memory. Accepted HMAC permits are durable via v0.9; rejected choices and browser-screen digests are not part of that committed event. An optional JSON export is not transactional. Need signed, immutable review-attempt records and privacy rules before a deployable workflow.

## F10-06: Temporal SQL still ties the gateway

Cycle 8's stronger SQL baseline matched the Hybrid Gateway on 4/4 self-authored temporal cases and 1,200 generated differential queries. Cycle 10 changes approval mechanics, not temporal answer accuracy. No independent benchmark or live model results were produced. Do not describe v1.0 as a neural-symbolic learning breakthrough.
