# SXP-L v2.0 — Local Evidence Report

**Research maturity:** reproducible software validation of a **pilot instrument**, not independent human comprehension, fluency, auditory reliability or real-world safety assurance.

## Executed evidence

- `test_validation20.py`: **12/12** passed, including 32 real parser-grounded stimuli, independent limited reader agreement on 24 clarification cases, allocation balance, answer-key isolation, scorer checks, and malformed CSV rejections.
- Focused inherited v1.9 regression: **71/71** passed (`test_reference19`, `test_repair18`, `runtime.test_continuity13`, `runtime.test_perspective14`). This is **not** a claim that every historical test in every older release was rerun.
- Four Chromium study sessions: **4/4** simulated end-to-end sessions; each displayed **32** cases and produced a valid CSV export; **zero JavaScript runtime errors**.
- Cohort A browser was deliberately fed correct answers: **32/32 synthetic QA**. Cohorts B/C/D were deliberately fed `unsure`: **0/32 correct** each. These results validate the scorer and **have nothing to do with human proficiency**.
- The HTML does not contain the researcher answer key or alternative representations of the same scenario. It does contain the participant's own assigned prompts and answers *options*.
- Across 4 cohorts, each of the 32 cases appears once in each of four conditions. Within a cohort: eight conditions per format; two actor, two target, two proposal-status, and two direct-utterance-status questions per format.
- Original v1.9 source and archives preserved. See the integrity manifest for hashes.

## Engineering decisions

The study compares **compact SXP-L**, **fully named SXP-L**, **controlled English**, and **JSON**. Every scenario has a canonical SXP-L source; the v1.9 parser's scoped expansion is compared to the independent limited reader in clarification cases. English glosses were written against the canonical roles, but were **not** parsed by an independent English semantics engine.

The 32 questions are deliberately constrained to `mi`, `ti`, `soraviko`, `tumerako`, three verbs (`liva`, `luma`, `rava`), four names, one clarification request structure, and direct-utterance controls. No new SXP-L linguistic roots were introduced.

## Open evidence gaps

- **Zero consenting independent participants tested**.
- **No audio or blind listening study**.
- **No comprehension advantage, confidence interval, statistical significance, or human learning result**.
- **No live agent action or authenticated authorization**.
- **No claim of a complete language**.
- Counterbalanced assignments cannot eliminate prior familiarity, unequal item difficulty, fatigue, accessibility differences or within-session learning.

All exact new test traces: `results/TEST_NEW_20.txt`, `results/TEST_INHERITED_19.txt`, `results/BROWSER_QA_REPORT.json`. Browser CSVs begin with `SYNTHETIC_` to eliminate ambiguity.
