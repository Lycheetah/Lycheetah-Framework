# BATCH 33 — RV34 · Licensing, attribution and publication metadata

**Reviewer:** Sol (Claude Opus 5.5, xhigh) · **Date:** 2026-10-22 · **Branch:** `review/full-framework-2026-10-20`, working tree only, nothing staged or committed. **This batch chooses no licence and removes no authorship.** The licence decision belongs to Mac. Nothing here is legal advice.

## Coverage, stated honestly

- **Read whole:** root `LICENSE`, `CITATION.cff`, `CONTRIBUTING.md` § Attribution, and `28_DEFENSE/ATTRIBUTION_REQUIREMENTS.md`.
- **Read in part:**
  - the head of `28_DEFENSE/CITATIONS.md`, which already carries an RV30 note;
  - the licence fields of `pyproject.toml`;
  - the heads of all 10 subproject `LICENSE` files;
  - the defense-index entry for these three files. It holds no hash pin, so the files count as maintained.
- **Census (`git grep`):**
  - every "Earned Sovereignty Clause": 14 files, 1 of which also names a "Resonance Preservation Clause";
  - every arXiv, Zenodo or publication-status line: 358 arXiv/Zenodo lines, sorted by hand into status claims versus citations of other people's work;
  - "Lycheetah Foundation": 78 files, 117 lines.
- **Primary records queried (read-only GETs; nothing was sent but the search terms):**
  - the Zenodo REST API for records 20020828 and 21122441;
  - the arXiv API for `all:Lycheetah` and for author `Clark M` with CASCADE or Lycheetah in the title or abstract;
  - `gh release list` and `git tag`.
- **DID NOT RUN:**
  - a search of other preprint servers (SSRN, OSF, PhilPapers);
  - an arXiv search under other name forms;
  - any legal or trademark search.

## Findings

| # | Status | Finding |
|---|---|---|
| F1 | MEASURED | **The licence texts conflict.** Root `LICENSE` is plain MIT (© 2026 Mackenzie Conor James Clark). `CONTRIBUTING.md` says "The MIT license with Earned Sovereignty Clause applies". It then lists "Attribution is required", "You may not rebrand this work as your own original creation" and "Forks are sovereign instances — they carry the axioms forward". **No text of that clause exists anywhere in the repository**: not in `LICENSE`, not in the archive, not in any proposal. It is a name with no terms. |
| F2 | MEASURED | **The clause ships inside the distributed package.** Three of the ten files whose headers say "MIT with Earned Sovereignty Clause" sit in `12_IMPLEMENTATIONS/applications/`, which the wheel ships as `lycheetah.applications`. Their package metadata says `License: MIT`, so the same artifact makes two different licence statements. One of those headers (`cascade_resonance_engine.py`) adds a second undefined "Resonance Preservation Clause". |
| F3 | DERIVED | **The attribution guide asks more than MIT grants.** `ATTRIBUTION_REQUIREMENTS.md` says "The MIT license requires attribution" and then sets a "minimum required attribution" for papers and products, plus a bar on relabelling the symbolic architecture. MIT's one condition is that the copyright and permission notice travels with copies of the Software. The page's further standards are requests and scholarly norms. It also says capture without attribution "is standard academic plagiarism covered by the MIT license". MIT is a copyright licence on code and text: it does not reach ideas or mathematical results. |
| F4 | MEASURED (Zenodo API) | **The public record exists, and it is MIT.**<br>• 10.5281/zenodo.20020828 was published 2026-05-04 (version `v1.0.0-c1.1`, Software, licence `mit-license`, creator Clark, Mackenzie Conor James).<br>• 10.5281/zenodo.21122441 was published 2026-07-02 (version `tianxia-v0.2`, also MIT).<br>• Concept DOI: 10.5281/zenodo.20020827.<br>Both records are titled "Lycheetah Framework: A Sovereign System for Human-AI Co-Creation". `CITATION.cff` cites the first record with a different title ("…Nine Formal Frameworks…") and version (`C-1.1`). The attribution page still says "Zenodo DOI when minted". |
| F5 | MEASURED (arXiv API) | **No arXiv record exists, yet nine files claim one.**<br>• Query results: 0 for `all:Lycheetah`, and 0 for author Clark M with CASCADE or Lycheetah in the title or abstract.<br>• Claims still standing before this batch: "preprint, endorsed, live" (`MEDIA_PITCH.md`, `NZIAT_APPLICATION_DRAFT.md`, `MARCH_2026_SYNTHESIS.md`); "arXiv paper (March 2026, endorsed) formally proves" (`NZ_CASCADE_CASE.md`); "HARMONIA is on arXiv. The mathematics is proven." (`NZ_MAORI_AI_SOVEREIGNTY_BRAINSTORM.md`); "The relevant paper is on arXiv" (`NZ_KAI_TAHU_APPROACH.md`); a table row in `THE_ENGINEERS_DOOR.md` marking a theorem [ACTIVE] as "Proven in arXiv paper"; and `THE_JOURNALISTS_DOOR.md`, which says the work lacks journal review because "it is in arXiv preprint".<br>• BATCH28 and BATCH29 struck the same claim in `papers/` and `24_`, and these copies were missed. An NZIAT application or media pitch carrying "endorsed, live" would put a false status in front of a funder or a journalist. |
| F6 | MEASURED | **Publication status, sorted:**<br>• **Accepted publications:** none found.<br>• **Submissions:** none found. There is no arXiv record and no journal submission receipt.<br>• **Releases:** GitHub `v1.0.0` (2026-03-25, "pip installable"), `Sol.v3.12.0` (2026-04-08), `v1.0.0-c1.1` (2026-05-04, archived on Zenodo) and `tianxia-v0.2` (2026-07-02, archived on Zenodo, and marked **Latest** on GitHub under the release title **"M app"**).<br>• **Drafts:** `papers/CASCADE_ARXIV.tex` and the CITATIONS "in preparation" entries.<br>• **Package versions:** the package says 1.3.0, which has no tag or release. The canonical body is C-1.1. Four version schemes run side by side (package semver, canonical body C-x, release tags, Zenodo version strings), and nothing maps them. |
| F7 | MEASURED | **The repository mixes licences, and the root says nothing about it.** Four subtrees are Apache-2.0: the retired LAMAGUE kernel v0.8 (© "Mackenzie Clark"), and `earned-light/forges_01_07/Forge_05`–`07` (© **"Lycheetah research collaborators"**). Six are MIT, under three spellings of the author's name. Apache-2.0 and MIT are both permissive and can sit in one repository. No `NOTICE` file exists, so Apache's NOTICE duty does not arise. None of the Apache paths are in the wheel. |
| F8 | DERIVED | **"Lycheetah Foundation" is cited as an institution** in 78 files, including the `institution` field of the CITATIONS BibTeX entries. A citation's institution field reads as a legal or academic body. This review found no record either way and did not search, so it is UNVERIFIED. |
| F9 | MEASURED | **Package metadata is consistent.** `pyproject` `license = {text = "MIT"}` matches the root LICENSE, and the sdist includes `LICENSE` (BATCH32 F6). |

## Repairs (working tree)

All are dated notes or strike-throughs. Every body is kept.

1. **Arxiv claims, eight files** (`23_NZ_AI_GOVERNANCE/` ×5, `13_SYNTHESIS_REPORTS/MARCH_2026_SYNTHESIS.md`, `14_MYSTERY_SCHOOL/THE_ENGINEERS_DOOR.md` and `THE_JOURNALISTS_DOOR.md`).
   - Each file gets a dated note under its title giving the query and the result, and pointing to the real Zenodo record.
   - The 11 exact status phrases are struck in place and marked `[RV34 … no arXiv record exists]`.
   - The rest of the author's text is untouched.
2. **`CONTRIBUTING.md` § Attribution.**
   - A dated note: the LICENSE is the only licence text; the clause has no text; MIT's single condition; the listed bullets are requests and norms.
   - It also points Mac to the options. The bullets themselves are kept.
3. **`28_DEFENSE/ATTRIBUTION_REQUIREMENTS.md`.** A dated note covering:
   - what MIT requires and what it does not reach;
   - the Zenodo record and its versions, and that no arXiv preprint exists;
   - the Apache-2.0 subtree inventory;
   - the clause conflict.
4. **`CITATION.cff`.**
   - A YAML comment saying that the abstract's counts describe the 2026-05-04 release.
   - It records the Zenodo record's own title and version, and the concept DOI.
   - No field values changed; the file still parses (version `C-1.1`, DOI 20020828).
5. **Staged, NOT applied:** `FOR-REVIEW/2026-10-22_OPUS_REVIEW/RV34_OPTION_B_LICENSE_HEADERS.patch`.
   - It changes 11 lines across 10 maintained files so they say MIT only (Option B below).
   - `git apply --check` passes against this tree.
   - `99_ARCHIVE/` and `28_DEFENSE/FULL_FRAMEWORK_REVIEW_2026-10-20.md` are deliberately excluded: one is a historical record and the other is a review that quotes the conflict.

## Witnesses

- **Full suite after the edits:** 1540 passed, 1 skipped, 1 xfailed, the same as BATCH32's local run.
- **`tools/verify-links.py`:** 1866 files, 2736 links, 0 dead outside the archive (22 inside `99_ARCHIVE`, held as a frozen record, unchanged).
- **The edit script** asserted that each struck phrase occurred exactly once, and refused any file that already carried an RV34 note. Backups are in `$S/rv34_bak/`.
- **Patch census:** 11 changed lines. That matches the 11 clause mentions outside the archive, FOR-REVIEW and 28_DEFENSE. The 12th hit is this batch's own note, which names the clause in order to explain it.

## Decision for Mac: the licence (G-RV34-1)

**What cannot change.** Everything already released under MIT stays MIT for anyone who took it: GitHub `v1.0.0`, both Zenodo versions, and every past commit. A new licence binds only future versions. That is DERIVED from how licences work generally; confirm it with a lawyer if it matters to a decision.

| Option | What it means | Cost |
|---|---|---|
| **A. Write the clause and adopt it** | Draft the "Earned Sovereignty Clause" text, add it to `LICENSE` and relabel everything "MIT + clause". | It is no longer MIT or OSI open source. The `License: MIT` field in `pyproject`, CITATION and Zenodo becomes false and needs changing. Many companies and universities cannot use custom-licensed code. Enforcing a bespoke clause needs a lawyer to write it. |
| **B. MIT only, and say so everywhere** | Apply the staged patch. Keep the attribution page as the author's requests. | The name "Earned Sovereignty Clause" disappears from the licence vocabulary. |
| **C. MIT plus a named covenant** | Option B, plus a short `EARNED_SOVEREIGNTY.md` stating the clause as a **covenant**: the author's ethical request (attribute, don't rebrand, carry the axioms forward), explicitly not a licence condition. | Mac would need to write or approve the covenant text. |

**Sol's stance: C.** The fight is about provenance, and a licence is the wrong weapon for it.
- **The licence is not the protection.** MIT already makes stripping the notice a breach. The timestamped Zenodo DOI and the git history settle who came first. Any protection of the *name* "Lycheetah" against rebranding would come from trademark, not from a copyright licence. That trademark point is DERIVED, not legal advice.
- **The cost of A is real.** A bespoke licence would cost the adoption that makes provenance worth defending.
- **C keeps what is Mac's.** The name lives on as the covenant, and the false legal claim goes.

## Other G-items

- **G-RV34-2, CITATION title and version.** Make `CITATION.cff` match the Zenodo record, or retitle the next Zenodo version to match CITATION. Consider citing the concept DOI 10.5281/zenodo.20020827 so "cite the latest" always resolves.
- **G-RV34-3, the GitHub release titled "M app".** It is marked Latest, sits on tag `tianxia-v0.2`, and Zenodo archived it under the framework's title. Rename it, or mark the C-1.1 release as Latest. This is an external mutation, so it is yours to do or to authorise.
- **G-RV34-4, "Lycheetah research collaborators".** Who holds the copyright on Forge_05–07? If it means AI seats, AI authorship of copyright is contested, and naming Mac as holder is the conservative line. If it means people, name them.
- **G-RV34-5, "Lycheetah Foundation".** Is it a registered body? If not, the BibTeX `institution` field should read "Independent researcher" (as CITATION.cff does), and the 78 mentions need a pass.
- **G-RV34-6, a version map.** Write one line each for package 1.3.0, canonical body C-1.1, tag `v1.0.0-c1.1` and Zenodo `tianxia-v0.2`, saying which is which. Otherwise a future release will mint a fifth scheme.
- **G-RV34-7, the arXiv strikes.** If an endorsement or a submission exists that this search missed (another name form, or another server), give the identifier and the strikes lift. BATCH28 G-KNOX-ENDORSEMENT is the same question.
