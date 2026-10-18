# SXP-L v2.0 integration review

**[SCAFFOLD] Restricted software behaviour; pre-human-data · 18 October 2026**  
Creator: Mackenzie Conor James Clark. Review: Caelorynth / Codex.

## Preservation and executed checks

The 46-file compilation is intact, including 20 overlapping original ZIPs.
All 45 outer manifest entries match. Archive inspection read 1,639 members
across 20 distinct archives, including nested history; no unsafe member paths,
CRC errors, obvious credential patterns or private home-directory paths were
observed in that bounded inspection. This is not an exhaustive privacy or
security audit. The latest release is also extracted as 112 byte-matching files
under `v2.0/`; none of the historical code was patched.

On Python 3.12, **12 new v2.0 tests and 71 focused inherited tests passed** with
no failures or skips. These are the release's selected reference, repair,
continuity and perspective suites. A complete rerun of every historical suite
and independent semantic judgement of all English paraphrases was not performed.

[Structured evidence](../../28_DEFENSE/evidence/research-intake-2026-10-18/suite-results.json)
and [archive inspection counts](../../28_DEFENSE/evidence/research-intake-2026-10-18/archive-inspection.json)
are retained. Supplied Chromium reports remain historical synthetic QA unless
an additional dated runtime receipt says otherwise.

## Eight inherited defects reproduced

[Executable reproducer](audit_known_limitations.py) ·
[recorded findings](../../28_DEFENSE/evidence/research-intake-2026-10-18/sxp-known-limitations.json).

| Finding | Observed in the frozen v2.0 baseline |
|---|---|
| Native-36 alias | `USR:A` renders and reparses as `N36:A` in the inherited v0.2 module |
| Verb valency | `ti ariva.` is rejected as missing a target |
| Attitude dispatch | The two authored hope clauses get incompatible proposition/attitude node kinds |
| Meaning difference coverage | Consent reports raise an unsupported-expression error |
| Participant changes | A target swap receives `inspect` rather than `high` priority |
| Linguistic denial/revocation | A valid synthetic host grant remains allowed without the advisory review flag |
| Superseded refusal | An explicitly repaired refusal remains a reported boundary |
| Repair-chain target | An already-superseded utterance is accepted as a later repair target |

```bash
python3 03_LAMAGUE_L1/26_SXP_L_RESEARCH/audit_known_limitations.py
```

**Expected exit: 1, because OPEN findings reproduce.** Exit 2 means the probe
did not complete. This does not alter the host capability policy or execute an
action; the linguistic review flag is a separate advisory channel.

The earlier independent audit is retained unchanged. These findings are not
closed by a higher release number or the study-generator tests. Acoustic
confusability and broader grammar-composition findings remain open, without a
new listening experiment here.

## Next research boundary

Work in a subsequent version, preserving these counterexamples. Address semantic
scope, participant identity, denial/revocation and repair precedence before any
agent-authorization integration. Have independent reviewers judge the four-arm
question equivalence, teaching bias and accessibility before recruiting a
consented pilot. Public researcher keys can unblind a study and require an
explicit recruitment design. There are **zero genuine human results** here.
