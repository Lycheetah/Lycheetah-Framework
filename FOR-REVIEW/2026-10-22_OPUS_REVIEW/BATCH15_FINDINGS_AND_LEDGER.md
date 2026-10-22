# Batch 15: RV16, SXP-L and the authority-bridge proposal

**Reviewer:** Sol (Claude Opus 5.5, xhigh), 22 October 2026.
**Branch:** `review/full-framework-2026-10-20`, HEAD `d7ae0ad`. Nothing committed, nothing pushed.
**Scope:**
- `03_LAMAGUE_L1/26_SXP_L_RESEARCH/`: the audit script, the v2.0 runtime (parser, bridge,
  repair) and the README and INTEGRATION_REVIEW claims;
- Aetheron's `FOR-REVIEW/2026-10-21_PROPOSALS/03_SXPL_AUTHORITY_BRIDGE_REVOCATION_PROPOSAL.md`.

**Frozen boundary.** The v2.0 tree is byte-pinned by
`28_DEFENSE/RESEARCH_INTAKE_2026-10-18_SOURCE_MANIFEST.json`. **MEASURED:**
`tools/verify_research_intake.py` checks 444 files and 59,124,466 bytes, and passes. No v2.0 file
was edited. The repair is a staged patch, tested on scratch copies.

**Witness tool:** `repro_batch15.py <root> [<runtime-dir>]`. It runs the inherited audit, then 13
extra probes, against any runtime copy. Three arms were run: the frozen baseline, proposal 03
applied word for word, and the Sol counter-patch.

---

## 1. All eight inherited findings reproduce

**MEASURED:** `audit_known_limitations.py` exits 1 and prints `OPEN_REPRODUCED` for all eight
findings:
- `USR_NATIVE36_ALIAS`: `USR:A` comes back as `N36:A`;
- `ARRIVE_VALENCY`: `ti ariva.` raises `E_COMPACT_ENTITY`;
- `ATTITUDE_SCHEMA_SPLIT`: the two hope clauses parse as `proposition` and `attitude_report`;
- `MEANING_DIFF_CONSENT`: raises `E_V08_PROPOSITION`;
- `MEANING_DIFF_PARTICIPANTS`: a target swap is rated `inspect`, not `high`;
- `LINGUISTIC_DENIAL_REVOCATION`: `nelora` and `revona` give allowed, no flag, 0 boundaries;
- `SUPERSEDED_REFUSAL`;
- `SUPERSEDED_REPAIR_TARGET`.

INTEGRATION_REVIEW's table matches what the code does.

## 2. The v2.0 runtime suite: 17 tests DID NOT RUN, now witnessed 181/181

**MEASURED:** in the committed tree, discovering all of `baseline/runtime/test_*.py` runs 181
tests and gives 17 errors. Every one is a `FileNotFoundError` for `runtime/examples/*.sxh`. The
112-file v2.0 extraction never shipped that directory, so those 17 tests have never run here.
This is DID NOT RUN, not FAILED.

The README's selected suites avoid them, and still pass: `test_validation20` OK, and the four
baseline suites OK.

**Witness:** the fixtures are in the v0.8 to v1.8 archives. Restored from v1.8 into a scratch
copy, the frozen baseline gives **181 / 181 OK**. **Proposed (G-FIXTURES):** the next SXP-L
version should carry `runtime/examples/`, so that its own suite can run.

Checksums of the fixtures were read from the v1.8 copy only. Whether they are byte-identical
across the archives is **UNVERIFIED**.

## 3. Proposal 03 (Aetheron): ruling

**ACCEPT, with an amendment.**

**What is right.** `denial_report` (`nelora`) and `revocation_report` (`revona`) are the two
boundary-like kinds the bridge leaves out. The census agrees: the only speech-act kinds are
`trust_report`, `delegation_proposal`, `delegation_refusal`, `explanation_request`,
`recommendation_request`, `decision_reservation`, `grant_report`, `permission_request`,
`denial_report` and `revocation_report`. None carries polarity, so no negated grant exists.
The proposal's key `e['old']` matches the real repair event schema.

**MEASURED:** applied word for word, proposal 03 closes `LINGUISTIC_DENIAL_REVOCATION` and
`SUPERSEDED_REFUSAL`. The other six findings stay open.

**What is wrong.**

1. **It breaks an inherited test that its author could not have run.**
   `test_sovereignty.test_transcripts_do_not_control_gate` fails on the proposal arm. Its "no
   boundary" document still contains `withdrawworda ^ mi revona …`, so it asserts that a spoken
   revocation is **not** worth a review. The test enshrines finding 6. In the committed tree it
   errors on the missing fixture, so this conflict was invisible. The proposal's claim of being
   "completely isolated" fails on that test. **MEASURED.**
2. **A speech repair silently clears the review flag.** Probe C2: the owner says a refusal
   (`resama`), then repairs it into `mi liva ti devora` ("I love you"). Proposal 03 returns
   `review_advised: false` while the host policy allows the action. The transcript's speaker
   labels are not authenticated: the fixture itself says so, and `dialogue10` resolves
   "discourse labels, not real authenticated agent identities". So a text edit can remove a
   reviewer's warning right before an allowed action. A speech repair is not an authenticated
   permission change. **MEASURED.**
3. **"Guarantees … immediately flag review_advised = True"** overstates it. The flag is raised
   only when host policy already allows the action (probe B3), and correctly so.

**What holds in the parser (MEASURED controls, every arm):**
- a cross-speaker repair is refused: the grantee cannot repair the owner's refusal (C1);
- a repair declared before its replacement exists is refused (C8);
- a reverse-order repair is refused (C9).

The issuer check is therefore at the level of discourse labels, never authentication.

## 4. Counter-patch (staged): `RV16_SXPL_bridge_and_repair_chain.patch`

It touches three files in the frozen runtime. It applies to HEAD with `patch -p1`, `cmp` matches
for all 3 files, and it contains 0 CR bytes.

- **`authority_bridge.py`:**
  - all four boundary kinds count;
  - a superseded boundary moves from `reported_boundaries` to a new `superseded_boundaries`
    list;
  - `review_advised` stays raised when any in-scope boundary was ever voiced.

  A withdrawn objection is reported as withdrawn, not as active, and never by itself clears the
  human look.
- **`dialogue10.py`:** adds `or new in repaired`. The parser's own comment already says "the new
  line cannot have already been consumed as a repair target", and the code never checked it.
  This is the root of finding 8.
- **`test_sovereignty.py`:**
  - the document that carries `mi revona` is now expected to be review-advised;
  - a truly clean document (`revona` changed to `periva`) is still expected not to be.

**MEASURED witnesses:**

| Check | Frozen baseline | Proposal 03 | Sol counter-patch |
|---|---|---|---|
| Inherited findings closed | 0 / 8 | 2 / 8 | **3 / 8** (6, 7, 8) |
| Runtime suite, fixtures restored | 181 OK | **1 FAIL** | **181 OK** |
| C2: refusal repaired into unrelated speech | flag raised | **flag cleared** | flag raised; u1 listed as superseded |
| C3: revocation repaired into a grant report | no flag (kind ignored) | no flag | flag raised; u1 listed as superseded |
| C5: chain onto an already-superseded line | accepted, nothing reported | accepted, nothing reported | **refused by the parser** |
| C6: grant then revocation, no repair | no flag | flag | flag |
| B2 / B3 controls (no boundary / policy denies) | false / false | false / false | false / false |

The updated test **fails on the frozen baseline** (`FAILED (failures=1)`) and **passes on the
counter-patch**.

Probe C7 (MEASURED, a known over-report): a denial spoken by the *grantee* about the owner's
resource also raises the flag. The bridge does not compare the speaker with `ownership`. For an
advisory flag this errs toward a look; it is documented, not changed.

**Where the patch should land:** INTEGRATION_REVIEW says to work in "a subsequent version,
preserving these counterexamples". Putting the patch into place therefore means either a v2.1
directory with the restored fixtures, or a decision to re-pin v2.0. That decision is G-SXPL-LAND.

## 5. Still open (reproduced, not repaired here)

These five findings belong to grammar and schema design, and a parser change would decide them:
- `USR_NATIVE36_ALIAS`: the v0.2 operator namespace has no `USR`, so it folds to `N36`;
- `ARRIVE_VALENCY`: `ariva` is typed as needing a target;
- `ATTITUDE_SCHEMA_SPLIT`;
- `MEANING_DIFF_CONSENT`: meaning_diff predates v0.9 consent clauses;
- `MEANING_DIFF_PARTICIPANTS`: priority rules.

Each needs a ruling on intended meaning before code, so they are recorded for Mac with their
reproductions. Acoustic confusability and wider grammar composition are open as well, and there
is no listening data.

**No genuine participant outcome exists.** There are 0 human results. All the browser CSVs are
synthetic QA, and the researcher keys sit beside the study HTML. The README says all of this
honestly.

## 6. Decisions for Mac

- **G-SXPL-LAND:** land the counter-patch as a v2.1 next to the frozen v2.0, or re-pin v2.0.
- **G-FIXTURES:** restore `runtime/examples/` from v1.8 in the landing version.
- **G-REPAIR-FLAG:** confirm the policy that a same-label repair moves a boundary to
  "superseded" but keeps `review_advised`, rather than clearing it as proposal 03 does.
- **G-SXPL-GRAMMAR:** rule on the five grammar and schema findings, one by one.

## 7. Status

- **RV16 is reviewed.** All eight findings reproduce. The proposal was tested and given a
  ruling. A counter-patch is staged and witnessed on a scratch copy. The checklist's three
  questions (denial and revocation, scope and issuer, repair chronology and cycles) are each
  answered by a probe.
- **Not done:** an independent semantic review of the English glosses, any study run, and any
  listening test.
