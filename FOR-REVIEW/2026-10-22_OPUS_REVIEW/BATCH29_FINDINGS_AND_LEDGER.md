# Batch 29: RV30, the footing gate and the documents it flagged

**Reviewer:** Sol (Claude Opus 5.5), 22 October 2026. **Branch:** `review/full-framework-2026-10-20`,
working tree only, nothing committed.
**Workstream:** RV30 in `FOR-REVIEW/FULL_FRAMEWORK_REVIEW_CHECKLIST.md`. The checklist box is not ticked.
This batch also does RV31's first item: wire the later 225-file import into
`tools/verify_research_intake.py`.

## Result

`python3 tools/verify-claims.py` listed **78** claim-bearing documents with no footing at the start of
this batch. Its baseline was 30, so the gate was already over its own line. It now lists **3**, and
`BASELINE` is lowered from 30 to 3. No label was pasted into a frozen file to get there:

- **60 frozen research files** now take their footing from a reviewed, maintained wrapper. They inherit
  it only while their bytes match the manifest.
- **15 maintained documents** were read and given dated notes or in-place repairs.
- **3 are left unmarked** on purpose. They are honest in prose that no vocabulary matches (F10).

## Findings

### F1: The 225-file research import had no path to footing. ✅ fixed (MEASURED)

`28_DEFENSE/RESEARCH_INTAKE_2026-10-19_SOURCE_MANIFEST.json` records the Earned Light and Sovereign
Will handoffs. `tools/verify_research_intake.py` checked only the four earlier releases, so nothing
held those files to their recorded bytes. Their docs could only lose the "unmarked" flag by having
labels written into them. That edit would break the frozen record.

`tools/verify_research_intake.py` now has three checks:

- **`verify_later`** pins every manifest entry that is unchanged since import (210 files). An edited
  entry must be a named maintained file. Every entry needs a named home. The 14 entries that live
  elsewhere must match their expected counts exactly (`ORIGINAL_NARRATIVES` 3, `SOVEREIGN_WILL` 11).
  The tree may hold only pinned files plus maintained ones.
- **`verify_sums_bundles`** reads `23_NZ_AI_GOVERNANCE/anon_politician/SHA256SUMS.txt` (121 files). It
  refuses duplicate lines, changed bytes, extra files and a wrong count.
- **`verify_all`** merges both checks with the four releases. Its footing feeds `verify-claims.py`
  through `frozen_research_footing`.

A package's footing counts only if its wrapper README carries `**[SCAFFOLD]**` and the word
"experimental". The three wrappers got real footing paragraphs:

- `papers/agent-safety/earned-light/README.md`
- `papers/agent-safety/sovereign-choice-research/README.md`
- `23_NZ_AI_GOVERNANCE/anon_politician/README.md`

Accounting: 210 pinned + 14 elsewhere + 1 maintained edited wrapper (the SCR README) = 225, which
matches the manifest.

### F2: A manifest records a stale hash. G-item (MEASURED)

The 10-19 manifest says `35_ABSTRACT_AND_GENERATIVE/SOVEREIGN_WILL/VALIDATION_AND_LIMITATIONS.md` is
unchanged since import. RV22 (this review) added a correction to it, so its `current_sha256` is now
wrong. The new gate does not pin maintained `35_` documents, so nothing fails. The manifest still
says something false. **G-RV30-1:** regenerate `current_sha256`, or drop the field for maintained files.

### F3: Outgoing templates carried claims the evidence does not support. ✅ repaired (MEASURED/DERIVED)

These pages are written to be sent, so their wording gets copied as is.

- **`papers/ARXIV_ENDORSEMENT_EMAIL.md`.** The results sentence ("100% invariant rate", "100% to 48%")
  is struck. A note above it gives a corrected sentence. The 100% counts invariants CASCADE is built
  to keep, the 48% comes from an ablation inside the author's own simulator, and CASCADE ties an
  additive baseline on historical cases (RV19).
- **`24_LAMAGUE_CROSS_CULTURAL/CATALYST_PROPOSAL_FRAME.md`.** Struck: "already on arXiv", "an arXiv
  paper", "This is not speculative" and "extends proven foundations". `git grep` found no arXiv
  identifier for any Lycheetah paper. Every hit was a third-party citation.
- **`24_LAMAGUE_CROSS_CULTURAL/CHINESE_PARTNERS.md`.**
  - "Formally proven" (3 times) and 正式证明的 now read "formally specified" (形式化的).
  - "Already being considered for government adoption" is struck. This review found no source for it.
  - "Significant structural convergence" is softened in English. The Chinese clause 显著的结构收敛 is
    left for a fluent speaker (**G-RV30-5**).

### F4: All nine component URLs in `28_DEFENSE/CITATIONS.md` were dead. ✅ fixed (DERIVED)

They used `tree/main/` and the folder names from before D-1.1 (`08_CHRYSOPOEIA`, `09_HARMONIA`, …).
The default branch is `master` (`origin/HEAD → origin/master`) and the folders carry layer suffixes.
The script checked that each target folder exists before rewriting. `git grep "tree/main/"` now finds
nothing. `verify-links` could not see these because they sit inside BibTeX `note` fields.

The note also covers:

- **Titles wider than the proofs.** TRIAD's "Banach Fixed-Point Guarantee" covers its model's update
  rule. CHRYSOPOEIA's holds only for c ≤ 13/30, and Ξ is stochastic (F21, measured earlier).
  **G-RV30-4:** retitle the two citations.
- **Papers in preparation.** Their July and October 2026 targets have passed, and no submission
  record exists.
- **Counts.** The April counts are dated, and the note points to the commands that print current ones.

### F5: `28_DEFENSE/TRANSLATION_CODEX.md` pointed at retired and nonexistent files. ✅ repaired (MEASURED)

- **Paths.** Spec paths under `08_CHRYSOPOEIA/` and `09_HARMONIA/` were rewritten after checking
  that the targets exist.
- **Missing file.** `CHRYSOPOEIA_THEOREMS.md` exists nowhere in the repository, so its reference is
  struck.
- **Missing implementations.** Five implementation cells name files that do not exist:
  `earned_light_demo.py`, `anamnesis_tc.py`, `chrysopoeia_demo.py`, `harmonia_demo.py` and
  `system_integration.py`. They are noted as intended implementations.
- **"Closes threats".** This means the page answers those objections. It does not mean the risks are
  closed.
- **VIP's "guaranteed non-empty response".** This one is accurate: the guarantee holds by
  construction. `apply_vip` returns a guidance string, and `tests/test_tri_axial_checker.py` checks
  that. `block_and_redirect` always returns a redirect. The note says the code guarantees *a*
  response, not a useful one.
- **Draft correction.** My draft said this guarantee was untested. The dry run's grep showed the
  test, so the note was corrected before anything was written.

### F6: The D-1.1 link rewrite erased its own plan's record. noted (MEASURED)

In `28_DEFENSE/D1_REPO_CLEANUP_PLAN.md`, the Phase 1 table's "Current" column shows the *new* names
(`01_CASCADE_L4 → 01_CASCADE_L4`). The global rewrite also ran over the plan that describes it. The
note restores the old names. **Lesson:** a global rewrite has to exempt historical records, or it
destroys the evidence of what it changed.

### F7: The incident protocol treats uncited ideas as licence breaches. noted (DERIVED from `LICENSE`)

`29_GOVERNANCE/INCIDENT_RESPONSE.md` is a careful, proportionate protocol. Its Classes 2–4 talk about
"license compliance" for uncited terminology and adopted structure. The licence is MIT, and `LICENSE`
line 12 requires only that copies keep the notice. Citing ideas is a scholarly norm, not a licence
term. The note asks anyone using the protocol to tell the two apart before sending a "formal notice
citing license terms". "The 1,402-page archive" is not in this repository and was not checked.

### F8: Three CASCADE planning papers call synthetic results proof. ✅ repaired (DERIVED)

- **`papers/EXPERIMENTAL_ROADMAP_2026_2028.md`.** "The synthetic validation proves the mathematics" is
  struck. A note covers the ✅ list (p < 10⁻⁴⁶, t = 70.29, 100%/48%, the March test count). This
  review found no results from Experiments 1 onward, so whether any has started is UNVERIFIED.
- **`papers/LIMITATIONS_AND_FUTURE.md`** (CRLF kept). "The core claim is supported" is struck. The
  page's own Limitation 5 already says all the quantitative validation is synthetic.
- **`papers/ARXIV_SUBMISSION_PLAN.md`.** "Submission-ready" and "results are solid" are dated to
  March 2026. Check the author email before use (`lycheetah.com` lapsed; `.org` was not checked).

### F9: Templates and dated lists. noted

- **`docs/PLAYGROUND_BUILD_SPEC.md`.** The playground is a phrase checker, not an alignment check.
  `docs/README.md` already says so.
- **`docs/GRANTS/MANIFUND_README.md` and `LONGTERM_FUND_README.md`** (CRLF kept). Fill claims from
  `CLAIMS.json`. The example wording "mathematical proofs" is replaced with an accurate phrase.
- **`docs/COMMUNITY/FREE_AI_TOOLS.md`** (CRLF kept). The free tiers have not been rechecked since
  March 2026.
- **`28_DEFENSE/READING_PATHS.md`.** "Share card included" is struck. RV27 retired the card.

### F10: The gate cannot see honest prose. G-item (MEASURED)

Three documents remain unmarked, and each is honest in its own words:

- `docs/THE_SOVEREIGN_MANIFESTO.md` opens "This is a stance, not a finding."
- `28_DEFENSE/RELEASE_AUDIT_2026-10-19.md` states "Evidence: Self-authored local research fixtures…".
- `docs/THE_CREATION_MYTH.md` is the author's own story, told as myth. Labelling a person's account
  of their own crisis is not a truth-pressure question, so it is left as written.

`BASELINE = 3` holds them, with a comment naming each. **G-RV30-2:** a reviewed-footing register
(path + sha256 + reason). A reviewed document would keep its footing only while its bytes stay the
same, which would replace a bare count.

### F11: The vocabulary check matches a word, not a status. G-item (MEASURED, reading `tools/verify-claims.py:44-62`)

The registers are bare, case-sensitive words matched anywhere in the file: `MEASURED`, `SCAFFOLD`,
`EDGE`, `FOUNDATION`, and so on. A document saying "this is not a SCAFFOLD" passes, while
`**Status:** [ACTIVE]` alone does not. The gate therefore says "some status word appears". It does not
say "the footing is right". This batch's notes pass because they contain those words. Reading the
documents is what did the work. **G-RV30-3:** require a status token in a recognised position
(`[TAG]` or `**TAG**`). That is Mac's call, because it would re-flag many documents.

## Validator audit (known-bad must fail, benign must pass)

| Check | Benign control | Known-bad cases refused | Witness |
|---|---|---|---|
| `verify_later` | real tree passes; synthetic package passes | changed bytes, extra file, missing file, entry with no home, edited non-maintained source, missing footing, wrong elsewhere count | `tests/test_research_intake.py` |
| `verify_sums_bundles` | real bundle passes (121) | changed bytes, extra file, duplicate line, wrong count, missing footing | same |
| real anon bundle | clean scratch copy passes, 121 | one byte changed in `CONTINUATION_ADDENDUM_v1.3.md`, refused "source bytes changed" | scratch copy, MEASURED |
| `verify-claims` baseline | `BASELINE=3` → rc 0 "HOLDING" | `BASELINE=2` → rc 1 "REGRESSION — 3 unmarked, baseline 2" | importlib run, MEASURED |

## Gates and suite (MEASURED, 2026-10-22)

- **`verify_research_intake.py`:** rc 0. It checked 4 releases, 210 later files and 1 bundle, and
  accounted for 14 entries that live elsewhere. That is **775 files**, 67,301,417 bytes.
- **`verify-claims --quiet`:** rc 0, "3 unmarked, at baseline". 114 historical documents inherit
  footing.
- **`verify-claims --register`:** 71 records (52 ACTIVE · 12 SCAFFOLD · 4 CONJECTURE · 3 RETRACTED).
  22 pinned counts agree.
- **`verify-links`:** 0 dead outside the archive, 22 inside `99_ARCHIVE` (frozen).
- **Full suite:** **1537 passed, 1 skipped, 1 xfailed, 1 warning**. That is up from 1522 because of
  the new RV30 tests.
- **Lint:** DID NOT RUN, because `ruff` is not installed.

## Coverage, stated honestly

- **Read in full:** `29_GOVERNANCE/INCIDENT_RESPONSE.md` and the `CITATIONS.md` BibTeX.
- **Read at the head and claim-bearing sections:** the other 13 noted documents, located by grep for
  their claims.
- **Read at the head plus a claims grep only:** the three unmarked documents.
- **Not done:** no external check of the Zenodo DOI or the author email, because no network call was
  made (**G-RV30-6**, **G-RV30-7**).

## Changed paths (this batch)

- **Tools and tests:**
  - `tools/verify_research_intake.py`
  - `tools/verify-claims.py`: `verify_all` wiring; `BASELINE` 30 → 3
  - `tests/test_research_intake.py`
- **Wrappers:**
  - `papers/agent-safety/earned-light/README.md`
  - `papers/agent-safety/sovereign-choice-research/README.md`
  - `23_NZ_AI_GOVERNANCE/anon_politician/README.md`
- **Notes and repairs:**
  - `papers/ARXIV_ENDORSEMENT_EMAIL.md`
  - `papers/ARXIV_SUBMISSION_PLAN.md`
  - `papers/EXPERIMENTAL_ROADMAP_2026_2028.md`
  - `papers/LIMITATIONS_AND_FUTURE.md`
  - `28_DEFENSE/CITATIONS.md`
  - `28_DEFENSE/TRANSLATION_CODEX.md`
  - `28_DEFENSE/D1_REPO_CLEANUP_PLAN.md`
  - `28_DEFENSE/READING_PATHS.md`
  - `24_LAMAGUE_CROSS_CULTURAL/CATALYST_PROPOSAL_FRAME.md`
  - `24_LAMAGUE_CROSS_CULTURAL/CHINESE_PARTNERS.md`
  - `docs/PLAYGROUND_BUILD_SPEC.md`
  - `docs/GRANTS/MANIFUND_README.md`
  - `docs/GRANTS/LONGTERM_FUND_README.md`
  - `docs/COMMUNITY/FREE_AI_TOOLS.md`
  - `29_GOVERNANCE/INCIDENT_RESPONSE.md`
- **Frozen files:** none touched. The 775 pinned files verify byte for byte.

## G-items for Mac

| ID | Decision |
|---|---|
| G-RV30-1 | Regenerate or drop `current_sha256` for maintained files in the 10-19 manifest |
| G-RV30-2 | Replace `BASELINE` with a byte-pinned reviewed-footing register |
| G-RV30-3 | Tighten the vocabulary to positioned status tokens |
| G-RV30-4 | Retitle the TRIAD and CHRYSOPOEIA citations to the proven scope |
| G-RV30-5 | Have a fluent speaker revise the Chinese convergence sentence |
| G-RV30-6 | Check that DOI 10.5281/zenodo.20020828 resolves to the C-1.1 record |
| G-RV30-7 | Confirm a working author email before any submission or pitch |
