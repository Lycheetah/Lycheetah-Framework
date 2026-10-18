# SXP-L × LAMAGUE v2.0 — Validation Forge

**Status:** pre-human-data, experimental, local software-tested pilot instrument. Not a verified improvement in communication or human comprehension. No deployed agent permissions or external communications.

## What changed

v2.0 **adds zero vocabulary and changes no v1.9 grammar**. The historical `mi liva ti` expression remains untouched. Its new contribution is a testable, four-arm pilot specifically investigating the semantics of `soraviko` and `tumerako`: short-form SXP-L vs fully named SXP-L vs controlled English vs JSON.

The study has **32 scenarios** in eight four-case blocks. Each participant's cohort file contains eight cases in each of the four formats; across cohorts A–D each individual scenario appears once in every format. Order is deterministically shuffled per cohort to reduce simple position-by-format confounding. Cohort generation seeds: `20261018 + cohort index`.

### Sharing rules — important

- Volunteers should receive **one** file from `participants/SXP-L_v2.0_Cohort_*.html`, not this complete ZIP. The complete ZIP includes **researcher answer keys and all alternative representations**.
- Ask for informed, voluntary consent before requesting exported CSV results. This is exploratory research, not an approved formal study.
- Participants can opt out or abstain. The HTML transmits no data; it exports to the participant's machine on request. Do not request names or sensitive information.
- To avoid bias, distribute A, B, C, D evenly and avoid giving participants multiple cohort files.
- Before a serious external study, arrange external review of question equivalence, instruction bias, accessibility, power/sample size, and recruitment procedure.

## Quick start

1. Open one `participants/SXP-L_v2.0_Cohort_A.html` file offline.
2. Review the teaching card; answer 32 questions; export your own local CSV.
3. As organizer, validate and score an explicitly consented exported file:

```bash
python score_study.py path/to/SXP-L_v2.0_A_responses.csv
```

Rebuild the instrument and rerun new tests from the v2.0 directory:

```bash
python build_study.py
python -m unittest -v test_validation20
python browser_qa20.py  # requires playwright Python + local Chromium
```

Rerun selected unchanged v1.9 tests:

```bash
cd baseline
PYTHONPATH=runtime:. python -m unittest -q test_reference19 test_repair18 runtime.test_continuity13 runtime.test_perspective14
```

Browser QA exports in `results/SYNTHETIC_BROWSER_QA_COHORT_*.csv` are **machine-generated**; they must never be misrepresented as participant responses.

## Files

- `participants/` — four independently shareable offline HTML study files, **with no hidden researcher key**.
- `researcher/ANSWER_KEY_DO_NOT_SHARE.json` — the private scoring key.
- `researcher/FOUR_ARM_FIXTURES_DO_NOT_SHARE.json` — all 32 cases in each representation, for research auditing.
- `build_study.py` — generator based on the v1.9 parser, independent restricted reader, and explicit English/JSON correspondence.
- `score_study.py` — local CSV validation and descriptive scoring (no p-values).
- `test_validation20.py` — allocation, parsing, key consistency, and tamper tests.
- `browser_qa20.py` — real Chromium export tests with synthetic answers only.
- `STUDY_PROTOCOL_v2.0.md` — scope, metrics, bias, ethics, and planned follow-up.
- `LOSS_LEDGER_v2.0.md` — information preserved/lost across formats.
- `ARGON_AUDIT_BRIEF_v2.0.md` — adversarial independent audit.
- `baseline/` — unchanged copy of the v1.9 working release files.
- `history/RELEASE_v1.9_ORIGINAL.zip` — exact preexisting v1.9 archive, including older bundled lineage.

## Main limitation

The four representations were aligned using deterministic SXP-L parsers and **manually authored English/JSON renderings**. This does *not* prove formal English semantic equivalence. A participant study has **not** happened. There are no genuine comprehension, learnability, or listening results.
