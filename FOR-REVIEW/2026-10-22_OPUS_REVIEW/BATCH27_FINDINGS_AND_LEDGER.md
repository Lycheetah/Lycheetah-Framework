# Batch 27 — RV28: Creative corpus and source ownership

Reviewer: Sol (Claude Opus 5.5, xhigh), 2026-10-22. Working tree only. Nothing is committed or pushed.

**Scope boundary.** This is a census and an ownership review, not a literary review. Nothing here judges whether a story is good. That is Mac's verdict, and a reader's. The validators below check structure and data. They do not establish literary quality, how the native School app behaves, or educational outcomes.

## Coverage

| Area | Files | What was done |
|---|---|---|
| `35_ABSTRACT_AND_GENERATIVE/` | 34 | Read `README.md` and the `REGISTER.md` header. Ran a claim-word grep over all `.md` files. The other bodies were not read. |
| `LYCHEETAH_EPIC/` | 70 (128 MB, almost all comic PNGs) | Read the router header and the `RELATIONAL_LOVE_MATHEMATICAL_LAW` truth boundary. Rebuilt the listening edition on a scratch copy. Hashed every `.md` for duplicates. The art was not inspected. |
| `LYCHEETAH_MYTHOS/` | 140 | Read the `SCRIPTURES_AND_STORIES` README and `rebuild.py` (head and receipt). Ran a numeric-claim grep over the Twelve Books. Did a byte census of every `TEXTS/` copy against its original. Ran all four Living Scripture gates, plus one known-bad control. |
| Lighthouse / story imports | 3 (`TEXTS/ORIGINAL_NARRATIVES/`) | Checked status only. They are labelled fiction and "not approved as epic canon". |

## What is sound (MEASURED unless marked)

- **The labels hold.**
  - 35_ says "Wonder is allowed. False certainty is not." It keeps an epistemic axis and a generative axis apart.
  - The Relational Law of Love says it is "mathematics for the fictional reality … not an empirically validated physical law".
  - The Living Scripture gate refuses a false systematic-review claim. Known-bad control: setting `systematic_review: true` fails with exit 1.
  - The Book I validator prints its own boundary: "data validation only; native School behavior remains unimplemented."
  - The Twelve Books contain no percentage, effect size, p-value or "proves" claim (grep).
- **The generated editions reproduce.**
  - `rebuild.py` was run on a scratch copy. It produced byte-identical `MASTER_SCRIPTURES_AND_STORIES.md`, `.html`, `CONDENSED_READING.md` and `SOURCE_MANIFEST.json`.
  - `VERIFICATION.json` differs only in its timestamp, and `browser_visual_witness` reads NOT_RUN because no browser was run here. The ZIP was not compared.
  - The Epic listening build also reproduces all 5 files byte for byte.
- **The gates pass:**
  - forge v0.4: PASS (12 books / 144 chapters);
  - forge v0.5: PASS (9,266 core words);
  - `validate_book_i`: PASS;
  - `test_book_i`: 10 passed, 13 subtests.
  - None of these four is under pytest's `testpaths`, so the full suite never runs them (G-STORY-GATES-IN-SUITE).

## Findings

**F1 — Two places to edit the same text, and nothing enforced which one.** (fixed by a guard test)
- The collection's rule (`SOURCE_MANIFEST.json`) says: "Edit collected texts here; original paths retain provenance." Yet 48 texts still exist at full length in their old paths, and those originals carry no pointer to the collection. The Twelve Books, the Epic chapters, The Emerald Work and The Night Garden all lack one.
- `rebuild.py` *reports* originals that have drifted into `VERIFICATION.json`, but it fails nothing, and nothing runs it automatically.
- The census on 2026-10-22:
  - 42 `TEXTS/` copies are byte-identical to their originals;
  - 6 differ only by relative versus absolute GitHub links, or by the pointer lines on two navigation pages;
  - 3 exist only in `TEXTS/`;
  - all 46 non-navigation originals still match their import hashes.
- Nothing has drifted yet. The risk is the next edit, and it is the edit every reviewer, including this one, makes by default: fixing the file at the path they are reading.
- Fix: `tests/test_scripture_collection_one_home.py` (5 tests).
  1. Originals must still match their import bytes. The two navigation pages are allowed to differ.
  2. Collected texts must match their manifest hash, so no edit can skip `rebuild.py`.
  3. The generated editions must match the receipt, so no hand edits reach the outputs.
- Mutation witness on a full scratch copy:

  | Case | Result |
  |---|---|
  | Benign copy | 5 passed |
  | Edit an original book | `test_originals_unchanged_since_import` fails |
  | Edit an Epic chapter original | the same test fails |
  | Edit a TEXTS copy without rebuild | `test_collected_texts_match_manifest` fails |
  | Hand-edit the master | `test_generated_outputs_match_receipt[MASTER…md]` fails |
  | Edit an allowed navigation page | 5 passed |

- An earlier witness run on an *incomplete* copy failed on the benign case. That run is RETRACTED: the copy lacked origin files.
- The failure message tells the editor what to do: revise under the collection and rebuild, or record Mac's decision to move that text's home.

**F2 — The Epic listening tool reads the old paths.** (proposal: G-EPIC-LISTENING-SOURCE)
- `LYCHEETAH_EPIC/tools/build-listening-edition.mjs` reads `LYCHEETAH_EPIC/01–03_*.md`, which are the originals.
- A revision made in the collection, as the rule asks, would never reach the listening edition. A revision made at the original reaches the listening edition but not the master.
- The F1 test now makes this conflict fail loudly instead of drifting silently.
- Which home wins for the Long Light is a canon/production decision. This review does not make it.
- Options:
  - (a) point the tool at `SCRIPTURES_AND_STORIES/TEXTS/LYCHEETAH_EPIC/`;
  - (b) declare the Epic folder the home for Long Light and drop those texts from the collection's "edit here" rule.

**F3 — The 26_FOR_AI and Epic duplicates are link variants of one text.**
- The RV27 note on the mythos mirror is confirmed here: the collection rewrites relative links to absolute GitHub URLs on import.
- That is a deliberate portability choice, so the ZIP reads outside the repo. It is not a defect.
- It does mean `TEXTS/` and the originals can never be compared by plain hash once links differ. The F1 test compares each original against its own import hash, which avoids that trap.

**F4 — The repository's "edit here" navigation is partial.**
- `LYCHEETAH_MYTHOS/00_INDEX.md`, its `README.md` and `00_EPIC_COVENANT.md` point to the collection.
- The individual books and chapters do not.
- Proposal (G-ORIGINAL-POINTERS): add a one-line dated pointer under each original's title. This review did not add them: 48 creative originals are Mac's authored bodies, and the Epic tool slices from headings (F2). F1's test already lists the two navigation pages that legitimately differ. If pointers are added, each origin's `import_sha256` must be re-recorded deliberately, by re-import, not by hand.

**F5 — An attribution string to check.** (ledger only)
- The Living Scripture manifest entry reads "AI co-author attribution supplied as OpenAI GPT-5.6 Sol".
- In this repository "Sol" also names the Claude seat.
- The string is labelled *supplied*, so it is recorded as supplied. Whether that seat name is right is for Mac to confirm (G-SCRIPTURE-ATTRIBUTION). Nothing was changed.

## Verification

- New guard test: 5 pass on the tree, plus the mutation table above.
- Full suite: see below.

## Decisions for Mac

- **G-EPIC-LISTENING-SOURCE:** which file is the Long Light's home? See F2 (a) or (b).
- **G-ORIGINAL-POINTERS:** add pointer lines to the 48 originals, with a deliberate hash re-record?
- **G-STORY-GATES-IN-SUITE:** add the four Living Scripture gates to the pytest suite? They pass now (~0.2 s).
- **G-SCRIPTURE-ATTRIBUTION:** confirm the "GPT-5.6 Sol" co-author string.
- **G-COMIC-ART-WEIGHT:** 128 MB of comic PNGs live in the Framework's heart repo. Keep them, or move them to Git LFS or a release asset? This is storage only, not taste.

## Files changed

| File | Change |
|---|---|
| `tests/test_scripture_collection_one_home.py` | NEW, 5 tests (one-home guard) |
| `FOR-REVIEW/2026-10-22_OPUS_REVIEW/BATCH27_FINDINGS_AND_LEDGER.md` | this ledger |

No creative text was edited.

**Full suite (2026-10-22):** 1522 passed, 1 skipped, 1 xfailed, 1 warning in 68.74s (0:01:08)
