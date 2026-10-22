# Batch 28 — RV29: READMEs, synthesis and current navigation

**Reviewer:** Sol (Claude Opus 5.5, xhigh), 2026-10-22. Working tree only; nothing committed.
**Scope (checklist RV29):** root entry points, every folder's purpose/status, `13_SYNTHESIS_REPORTS/`,
`30_MAPS/`, `docs/`, `WORKING_HOME.md`, quickstarts and package entry points. Find stale promises,
duplicate truth sources, contradictory dates or counts, dead links and inaccessible local paths.
A new website is out of scope.

## Headline

The navigation layer is in better shape than the checklist assumed. `WORKING_HOME.md` (19 Oct),
`00_Sovereign_Index.md`, `README.md`, `FIVE_MINUTE_BRIEF.md`, `13_SYNTHESIS_REPORTS/README.md` and
`docs/README.md` are current. They already label the dated plans and older packets as dated. Every
tracked top-level folder appears in the Sovereign Index (MEASURED: 0 missing).

The real damage was in documents a reader reaches **directly**, without the index:

- the root "Public Evidence Document" for AURA enforcement says "Live — demonstrated" for a
  hardware stack that does not exist in this repository;
- three root plans still read as live instructions;
- the papers guide says "arXiv submission ready" for CASCADE, with simulator figures presented as
  results;
- the 30_MAPS register quotes April counts.

All of these now carry dated notes. Their original bodies are kept, with strike-throughs where a
line is contradicted by repository evidence.

The repository's own link gate was **red** on the working tree because of one untracked proposal
file. It is green again.

## Findings

| ID | Severity | Status | Finding |
|---|---|---|---|
| F1 | High | FIXED (note + 3 strikes) | `AURA_CONSTITUTIONAL_ENFORCEMENT-1.md` claims a working enforcement system that is not implemented |
| F2 | Medium | FIXED | `tools/verify-links.py` (CI + pre-commit) was red: a `file://~/...` link in an untracked BNF proposal |
| F3 | Medium | FIXED (notes) | Root plans still read as current: `ZENODO_RELEASE_v1.md`, `OPUS_MASTER_PLAN_2026.md`, `START_HERE_FORGE_CHECKPOINT_2026-08-22.md` |
| F4 | Medium | FIXED (note) | `papers/README.md` CASCADE entry: "arXiv submission ready", simulator figures read as results |
| F5 | Low | FIXED (note) | `30_MAPS/COHERENCE_REGISTER.md` claim distribution (39/23/12/1) is April data |
| F6 | Low | PROPOSAL | Root `AGENTS.md:3` carries a local absolute path |
| F7 | Low | OPEN, G-item | 11 folders have no README |
| F8 | Low | OPEN, G-item | Claim counts are copied by hand into many documents and drift |
| F9 | — | DEFERRED to RV32 | `27_SOL_AI_APP/README.md` "[ACTIVE] — Planning complete" |
| R1 | — | RETRACTED | My own "1 dead link" in `28_DEFENSE/D1_REPO_CLEANUP_PLAN.md` |
| R2 | — | RETRACTED | My own "the BNF `file:///` link is no longer present" |
| R3 | — | RETRACTED | My own claim breakdown "ACTIVE 49, SCAFFOLD 11, ASPIRATIONAL 4, EMPIRICAL 3, REMOVED 3, OBSERVATIONAL 1", written into `ZENODO_RELEASE_v1.md`, `30_MAPS/COHERENCE_REGISTER.md`, `26_FOR_AI/DEAR_AI.md` (RV27) and F5. It counted the raw `status` field. The published and pinned counts use `status_normalized`: ACTIVE 52, SCAFFOLD 12, CONJECTURE 4, RETRACTED 3. All four places now quote the normalized counts and name the command that prints them. Found by running `--register` (MEASURED). |

### F1 — AURA enforcement document

The status line says "Live — demonstrated on Sol App (public)". The body says it is "a technical
record of something that actually works", that the hardware stack "is not software policy. This is
silicon-level constraint", and that "There is no escape at any layer."

What the review measured or derived:

- **No implementation (MEASURED).** A search of tracked `.py/.js/.ts/.c/.rs/.sh` files for
  `tpm2`, `tpm_`, `unseal` and `kernel module` found only two comments in `lycheetah/assurance/`
  that use the word "unsealed" for a digest. There is no LSM, BPF program, seccomp filter or TPM
  policy.
- **The design cannot work as written (DERIVED).** A seccomp filter sees system-call numbers and
  raw argument values. It cannot dereference a pointer, so it cannot score an output's C_sol on
  `write()`.
- **A named flag does not exist (MEASURED).** `MAP_NOEXTEND` is absent from `/usr/include` on the
  reviewing machine, which does define `MAP_LOCKED`.
- **The document contradicts itself (MEASURED).** Its own "Known Limitations" calls the C_sol window
  5 seconds; Layer 2 already uses 30.
- **The formula is just a minimum (DERIVED).** `C_sol = (w·p)/max(w,p) = min(w,p)`. It cannot say
  which side dominates, so it cannot by itself separate "Cold Death" from "Mystical Inflation".
- **The headline claim is not shown.** "Any LLM routed through the AURA layer produces
  alignment-consistent behaviour regardless of training": the Sol App's code is not in this
  repository, and no evaluation of it is recorded. The AURA scorers that are here are text
  heuristics: `docs/README.md` says the playground's output "is not validated alignment
  detection", and RV27 showed hedge words outscoring a manipulative instruction.
- **Two outside claims are UNVERIFIED with no source.** "Anthropic published a report this week
  calling for a global pause" has no citation or date. "CASCADE arXiv preprint: Endorsed (Prof.
  Knox)" has 1 occurrence in the whole repository, and the repository records no arXiv identifier
  for CASCADE: the arXiv IDs in `papers/CASCADE_*` are all citations of other people's papers.

**Repair.**

- Three lines were struck with dated corrections: the status line, "something that actually works"
  and "no escape at any layer".
- One review note was added under "What This Document Is". It also credits what stands: the seven
  invariants as stated commitments, the honest Known Limitations section, and "not a complete
  solution".
- `00_Sovereign_Index.md:150` already filed the document as an "earlier specification". The repair
  puts that status where a direct reader sees it.

### F2 — the link gate was red

`python3 tools/verify-links.py` on the tree, before the fix:
`✗ FOR-REVIEW/2026-10-21_PROPOSALS/02_BNF_GRAMMAR_HARMONIZATION_PROPOSAL.md:11 →
file://~/Lycheetah-Framework/03_LAMAGUE_L1/04_BNF_GRAMMAR.md`, followed by
`✗ BROKEN — 1 dead link(s)`, exit 1.

The whole `FOR-REVIEW/2026-10-21_PROPOSALS/` folder is untracked. The gate lists files with
`--others`, so it saw this file, while my own checker (`git ls-files` only) and `git grep HEAD` did
not.

**Fix.** The link now reads `../../03_LAMAGUE_L1/04_BNF_GRAMMAR.md`. It is a navigation link in a
proposal. The BNF document itself, which is pinned, was not touched.

**Witness.**

- After the fix: `✓ THE LINKS RESOLVE — 0 dead outside the archive · 22 inside 99_ARCHIVE`, exit 0.
- The pre-fix run above is the known-bad that failed.
- A minimal scratch repository with one valid link also passes (benign control).

**Gate quirk (MEASURED, minor).** The gate counts a link written inside inline code or a fenced
block as a real link: in the scratch repository both cases fail. This errs toward red, which is the
safe direction. A document that shows link syntax as an example can trip it.

### F3 — dated plans at the root

| File | Problem | Repair |
|---|---|---|
| `ZENODO_RELEASE_v1.md` | "**Status:** `[ACTIVE]` — ready for Mac to execute" | Struck as executed. `CITATION.cff` and `28_DEFENSE/CLAIM_STATUS_LEDGER.md:219` record DOI `10.5281/zenodo.20020828`, minted 2026-05-04. That is a repository record: this review did not query Zenodo. The May counts are noted against the 71-row register. |
| `OPUS_MASTER_PLAN_2026.md` | 1 May 2026 plan with an `[ACTIVE]` header | Note: a dated plan, not current priorities |
| `START_HERE_FORGE_CHECKPOINT_2026-08-22.md` | Named "START HERE" at the root | Note: the handoff marker for one branch; start at `README.md` and `WORKING_HOME.md` |

### F4 — papers guide, CASCADE entry

The guide says "Status: arXiv submission ready" (March 2026), with "all three invariants hold at
100%", "100% with truth pressure; 48% without" and p < 10⁻⁴⁶.

The note scopes these figures:

- The invariants are built into the update rule, so holding on 1,000 generated events is a
  conformance check, not an outside result.
- The 48% figure is an ablation inside the same simulator.
- p-values on simulated runs grow with the number of runs chosen.
- RV19 found CASCADE tying an additive baseline on the historical cases.
- C1 audit D-01 had already flagged the "100% accuracy" wording.

`papers/CASCADE_ARXIV.tex` was not edited. It is a manuscript, and the figures are in its own
tables (L441–443, L506, L513).

### F5 — 30_MAPS register counts

Ten of the eleven 30_MAPS files are dated 2026-04-25. `FORMAL_SPINE.md` carries the 20 October
review notice. The Sovereign Index labels the folder "dated summaries may predate later
corrections". The one place where a stale number is likely to be quoted is the claim-distribution
line, and it now points to `CLAIMS.json`. On 2026-10-22 the register has 71 rows; normalized status
ACTIVE 52, SCAFFOLD 12, CONJECTURE 4, RETRACTED 3 (`python3 tools/verify-claims.py --register`,
"✓ AGREED — 22 pinned counts"). See R3: an earlier draft of this line quoted the raw field.

### F6 — local absolute path (proposal only)

Root `AGENTS.md:3` names `~/Lycheetah-Framework` as the corpus location. That is an
agent-instruction surface, so this review does not edit it.

**Proposal:** say "this repository (`Lycheetah-Framework`, branch `master`)" instead. It is the
only local absolute path left in a tracked `.md` file outside the archive (MEASURED by grep), now
that F2 is fixed.

### F7 — folders without a README

The folders are: `000_1404RawSourceTranslate`, `16_SOL_VEYRA_ARCHITECTURE`,
`17_LEARNING_EMERGENCE`, `20_DOMAIN_SPECIALISTS`, `21_MEMORIA`, `22_INTERFACE_INTELLIGENCE`,
`29_GOVERNANCE`, `30_MAPS`, `.github`, `LYCHEETAH_EPIC` and `tools`.

Each has a one-line purpose and status in `00_Sovereign_Index.md`, so none is unreachable. On
GitHub, however, a reader who opens one of these folders sees a bare file list. No README was
created in this batch: writing eleven new guides is a scope decision, and a second description of
each folder risks a duplicate truth source.

### F8 — counts copied by hand

Claim counts appear as typed numbers in at least five places, and each is a different snapshot:

| Document | Counts |
|---|---|
| `DEAR_AI.md` (fixed in RV27) | 37/14/6/3 |
| `ZENODO_RELEASE_v1.md` | 17/40/16 |
| `COHERENCE_REGISTER.md` | 39/23/12/1 |
| `CLAIMS.json` | 71 rows today |
| CI / `verify-claims.py` | maintains its own baseline |

A repeated count with no gate drifts. **Proposal:** documents link to `CLAIMS.json` (or to one
generated count line) instead of typing numbers.

### Retractions (R1, R2)

**R1.** My checker read `` `](29_GOVERNANCE/GOVERNANCE.md)` `` at `D1_REPO_CLEANUP_PLAN.md:110`
as a dead link. It is link syntax shown inside inline code, in a sentence about how to scope a
rewrite. With code spans stripped, my checker reports 0 dead links among 2,032 relative links
(tracked `.md`, archive excluded).

**R2.** In recon I recorded the BNF `file:///` link as gone. I had searched only tracked files and
`HEAD`; the link was in an untracked file. F2 above is the true state.

## What lives where, and what actually runs

`00_Sovereign_Index.md` already answers *where*, and `WORKING_HOME.md` answers *which copy to
edit*. This batch does not add a third map. The table below records only what **this review**
ran. Earlier batch ledgers hold the evidence for each area.

| Surface | Command / evidence | Result (2026-10-22) |
|---|---|---|
| Python test suite | `pytest -q --strict-markers` (testpaths `tests/`) | See "Full suite" below |
| 11 console scripts | `lycheetah.cli:<fn>` with `--help` for check, web, guard, assure, compact, consensus, sovereign, handoff, sol, alexandria, cascade | 11/11 print usage and exit 0. This proves the parsers import and build; it is not a functional test (RV33 owns that). |
| Link gate | `tools/verify-links.py` | Green after F2; it was red before |
| Scripture collection | `rebuild.py`, validators, `tests/test_scripture_collection_one_home.py` | RV28: byte-identical rebuild; 5 guard tests with mutation witness |
| AI self-check | `26_FOR_AI/tools/invariant_self_check.py`, `tests/test_invariant_self_check.py` | RV27: fixed, 6 tests, HEAD copy fails 5 |
| AURA hardware enforcement | none | Not implemented (F1) |
| Sol App / mobile | separate repository | Not in this tree; not checked here |

## Coverage (honest)

| Item | Coverage |
|---|---|
| Root `.md` entry files (20) | Read head/status of all. Fully read: `AURA_CONSTITUTIONAL_ENFORCEMENT-1.md`, `WORKING_HOME.md` (head and ownership table), index rows L146–152 |
| `00_Sovereign_Index.md` | Folder coverage checked mechanically; dated-plan rows read |
| `13_SYNTHESIS_REPORTS/README.md`, `docs/README.md` | Read; current (19 Oct) |
| `30_MAPS/` (11) | Date/status line of every file; register L318–335; `ARCHITECTS_GUIDE` L140–150 (VIP wording, already G-VIP-WORDING) |
| `papers/README.md` | L1–100 |
| Relative links | 2,032 checked by my checker; repository gate run on the tree plus scratch controls |
| `QUICKSTART.md`, `EXPLORE_WITH_AI.md`, `LINEAGE.md`, `CHANGELOG.md`, `VISUAL_IDENTITY.md` | **NOT REVIEWED** in body this batch (head only or not at all) |
| `CLAUDE_AUGMENTED.md`, `THE_SOL_PROTOCOL.md`, `AGENTS.md`, `CLAUDE.md` | Agent/protocol surfaces: not edited (cross-seat and RV27 rule) |
| Per-folder README bodies | Not re-read here. Folders 01–35 were reviewed in their own RV batches. |
| Hosted Pages site | NOT CHECKED (no network check; out of scope) |

## Changed paths (this batch)

- `AURA_CONSTITUTIONAL_ENFORCEMENT-1.md`: 3 strikes and 1 note
- `ZENODO_RELEASE_v1.md`: 1 strike and 1 note
- `OPUS_MASTER_PLAN_2026.md`: note
- `START_HERE_FORGE_CHECKPOINT_2026-08-22.md`: note
- `papers/README.md`: note
- `30_MAPS/COHERENCE_REGISTER.md`: note
- `FOR-REVIEW/2026-10-21_PROPOSALS/02_BNF_GRAMMAR_HARMONIZATION_PROPOSAL.md`: one link made
  relative (an untracked file)

Edit script: `$S/rv29_edit.py`. It was dry-run on a scratch copy, then applied; all anchors are
exact-one and all files are LF.

## Decisions for Mac (G-items)

| G-item | Decision |
|---|---|
| **G-AURA-DOC-STATUS** | Keep the AURA enforcement document at the root as an annotated design, move it to an archive or design folder, or rewrite it as a proposal. Was it part of the Zenodo deposit? If so, the deposited version is frozen and only the repository copy carries the note. |
| **G-KNOX-ENDORSEMENT** | Is there a record of an arXiv endorsement for CASCADE? If yes, add the receipt. If no, strike the line. |
| **G-ANTHROPIC-PAUSE-SOURCE** | Source the "this week" report, or strike the paragraph. |
| **G-AGENTS-LOCAL-PATH** | Approve the F6 wording change in the root `AGENTS.md`. |
| **G-FOLDER-READMES** | Choose: thin READMEs that point to the index row, or leave the index as the only description. |
| **G-COUNTS-ONE-SOURCE** | Stop hand-typing claim counts (F8). |
| **G-PROPOSALS-TRACKING** | `FOR-REVIEW/2026-10-21_PROPOSALS/` is untracked. The link gate reads it locally, but a clean checkout and CI will not see it until it is tracked. Decide whether to track it. |

## Full suite

`timeout 900 python3 -B -m pytest -q -p no:cacheprovider --strict-markers` on the tree after the
RV29 edits:

```
1522 passed, 1 skipped, 1 xfailed, 1 warning in 72.73s
```

This matches the RV28 count. RV29 added no tests: the link gate `tools/verify-links.py` already
existed, and it runs in CI and pre-commit, not in pytest. The warning is the same as before
(`plt.show()` in `14_MYSTERY_SCHOOL/implementations/visualization_system.py:109`).
