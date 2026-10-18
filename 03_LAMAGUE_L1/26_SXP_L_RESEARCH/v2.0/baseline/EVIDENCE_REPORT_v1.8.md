# SXP-L v1.8 — Engineering evidence

**Version:** 1.8 experimental research snapshot, 18 October 2026.

## Verified locally

- **49 of 49** Python unittest methods passed in one focused regression run; transcript stored in `TEST_RUN.txt`. This includes the v1.8-specific suite, inherited v1.3 continuity tests, and inherited v1.4 perspective tests.
- **700 seeded generated dialogue cases** in the v1.8-specific suite completed with exact source round trip and artifact verification.
- A separate restricted regex-based reader agreed with the main implementation on the speech-act classification of all 700 generated dialogues; it does not independently validate the full inherited leaf grammar.
- Correct rejections of wrong-speaker corrections, wrong-target clarification, future/unknown references, correction forks, malformed repair scopes, `mi`/`ti` in clarification propositions, bad spacing, and mismatched sidecars.
- `mi liva ti devora` remained unchanged; `mi jiva ti` remained outside the accepted inherited lexicon.
- Both new roots passed the written CV phonotactics and screened one-edit spelling collision constraint. No acoustic or listening experiments were performed.
- The v1.8 browser learner passed a headless Chromium smoke test including sample parsing, error display, reset, local file export, quiz feedback and zero JavaScript errors. See `BROWSER_QA_v1.8.png` and the script `browser_smoke18.py`.
- Original v1.7 ZIP is preserved as a byte-identical file under `history/` and directly reused historical runtime modules retain identical bytes.

## Limits

The first development attempt detected a viewpoint ambiguity in clarification proposals. Before release, the grammar was tightened to require explicit names in clarification candidates and to retain the original addressee in corrections. The regression total above refers to the **final revised version**.

The focused 49-test run is not the full history-wide test collection, and does not imply a complete linguistic validation. No real people were studied. No cloud/host security system was deployed. The browser lab is an educational subset, not a full independent parser. The cryptographic hashes are integrity checks only, not signatures or authentication.
