# Batch 23 — RV24: NZ governance and policy coherence

**Reviewer:** Sol (Claude Opus 5.5, xhigh). **Date:** 2026-10-22.
**Branch:** `review/full-framework-2026-10-20` at HEAD `d7ae0ad`. Working tree only: nothing committed or pushed.

**Brief (RV24):** review all of `23_NZ_AI_GOVERNANCE/`:

- the six-rights proposal;
- the 26 historical drafts;
- the background candidates;
- Anon Politician.

Check for conflicting current recommendations and for legal or adoption language. Consult primary
official sources for current law and date each finding. Keep five things apart:

- Privacy Act scope;
- proposed rights;
- implementation;
- adoption;
- civic-metadata validation versus representative sampling.

---

## Coverage — what actually ran

| Item | Method | Result |
|---|---|---|
| `DATA_SOVEREIGNTY_FOR_NEW_ZEALANDERS.md` (the current proposal) | read in full; law section checked against sources | F1, F2 |
| 26 historical drafts | first 20 lines of each checked for a status notice | **26/26** carry "Historical draft — superseded" with original text kept. MEASURED |
| 9 background documents | notice check; `COMMUNITY_AI_WOF.md` read for conflicts | 9/9 carry "Background research — requires reconciliation". F2. MEASURED |
| `anon_politician/SHA256SUMS.txt` | `sha256sum -c` | **121/121 OK**. MEASURED |
| v1.3 handoff `SHA256SUMS.txt` | `sha256sum -c` | **103/103 OK**. MEASURED |
| Civic Signal kit tests | `python3 -m unittest discover -s tests` on a `git archive HEAD` copy | **16 OK**. MEASURED |
| Policy Lab v0.2 tests | the same command | **16 OK**. MEASURED |
| Civic Signal validator, adversarial | known-bad, benign and claim-shape probes | F3. MEASURED |
| `docs/nz-governance.html` | law section read | already says the six rights are not law and that no endorsement is claimed; IPP 3A added (F1) |
| Adoption/endorsement language repository-wide | grep outside `23_` | no live claim that NZ or any agency adopted anything. `24_LAMAGUE_CROSS_CULTURAL/CATALYST_NZ_CHINA_APPLICATION.md:104,158` lists scholar endorsement and regional-body endorsement as *targets* → moved to RV25 |

**Primary sources (dated 2026-10-22, with verification level):**

- **OPC, IPP 3A** (privacy.org.nz/privacy-principles/3a/): **FULLTEXT**. The page says "IPP3A came
  into force in May 2026". The statutory text requires reasonable steps to tell the person about the
  fact of collection, the purpose, the intended recipients, and their access/correction rights.
- **OPC, IPP 12** (privacy.org.nz/privacy-principles/12/): **FULLTEXT**. Covered overseas disclosure
  requires one of:
  - authorisation after being expressly informed;
  - the recipient is subject to the Act;
  - comparable safeguards;
  - a prescribed scheme or country;
  - an agreement.
- **Privacy Amendment Act 2025**: Royal assent 23 September 2025 (legislation.govt.nz/act/public/2025/53;
  Ministry of Justice news). **METADATA** only, because the legislation site returned HTTP 403 to the
  fetcher.
- **Algorithm Charter for Aotearoa NZ** (July 2020, voluntary, agency signatories) and its **Year 1
  review** (December 2021): **ABSTRACT**, from search results. The data.govt.nz page returned an empty
  body.
- **NZ AI Strategy** (July 2025: relies on existing law, prefers it to a standalone AI Act) and the
  **Public Service AI Framework** (guidance, not binding): **ABSTRACT**, from search results. The
  MBIE and digital.govt.nz pages returned empty bodies to the fetcher.
- **NOT VERIFIED:** whether the Privacy Act contains any GDPR Article 22-style right covering
  automated decisions. The full Act text could not be fetched, so the answer stays UNVERIFIED and is
  labelled that way in the repository note.

---

## Findings

### F1 — The six-rights law section was missing the law that changed this year. ✅ annotated

**The gap.** The proposal's "builds on the law" section was checked on 19 October 2026 and lists
IPP 6, 7 and 12 only. It omits:

- **IPP 3A**, in force since **1 May 2026** and inserted by the Privacy Amendment Act 2025. It requires
  notice when personal information is collected indirectly.
- IPP 3 (direct collection).

Together these sit directly under Right 1 ("Right to know").

**Two more omissions:**

- The **Algorithm Charter** (2020). Its human-oversight commitment already promises signatory agencies'
  challenge/appeal channel, which is the voluntary ancestor of Rights 4 and 6.
- **Current government direction.** The July 2025 AI Strategy prefers existing law to a standalone AI
  Act, and the Public Service AI Framework is non-binding.

**Why it matters.** A pitch that says "the Act was not written for telling people…" without naming
IPP 3A will be corrected by the first privacy lawyer who reads it. Next step 3 already asks for that
reader.

**Repair.** A dated review note goes after the IPP list, with each source and its verification level.
The original paragraph is kept. The note adds that **neither IPP 3 nor IPP 3A requires disclosing AI
use**, so Right 1 is still new. It is an extension of existing notice law, not a blank page.
`docs/nz-governance.html` gains IPP 3A and the Charter in its law section. DERIVED from the sources
above.

### F2 — The current proposal points at a WOF that requires superseded standards. ✅ annotated

**The conflict.**

- `DATA_SOVEREIGNTY_FOR_NEW_ZEALANDERS.md` says "A system that fails these rights should not get its
  WOF".
- The only WOF that exists, `COMMUNITY_AI_WOF.md` v0.1, makes check #7 require **Three Worlds
  Disclosure** compliance (line 37). Its documentation list requires **Whakapapa Disclosure** (lines
  50–51, 151–153).
- Both are historical drafts that this proposal superseded.
- The v0.1 WOF tests none of the six rights.

The README already says "A WOF v0.2 aligned with the six rights has not been implemented or piloted",
but the proposal's own text did not say so. That is a live current-recommendation conflict.

**Repair.** A dated note under the WOF paragraph says it describes the intended relationship, not a
working check, until v0.2 exists. MEASURED (line numbers) and DERIVED (the conflict).

### F3 — The Civic Signal validator's claim gate can be bypassed by the shape of the claim. 📦 staged

**The gate.** `civic_signal_validator.validate` blocks population claims such as `representative`,
`national_consensus` and `public_mandate` from opt-in, targeted and submission designs. This is the
code behind the brief's "civic metadata does not prove representative sampling", and the gate works
for the canonical form. MEASURED.

**The bypass.** `claims = set(record.get("claims", []) or [])` has three faults:

| Input on an `open_opt_in` record | HEAD result |
|---|---|
| `"claims": "representative"` (a bare string) | `set("representative")` is a set of letters → **no claim error** |
| `["Representative"]`, `[" national_consensus "]` | exact-match only → **no claim error** |
| `[{"x": 1}]` | **crash**: `TypeError: unhashable type: 'dict'` |

- The CLI never applies `schemas/civic_signal_record.schema.json`.
- Even if it did, the schema only requires an array of strings, with no enum, so the capitalised form
  passes the schema too.
- The browser checker is a second implementation in `Civic_Signal_Integrity_Checker_v0.3.html`. It
  builds `claims` from fixed checkboxes, so it cannot be bypassed this way. It has drifted from the
  Python on other findings, though:
  - it merges `PRIVACY_NOTICE_MISSING` and `LEGAL_BASIS_UNREVIEWED` into one code;
  - it lacks `EVIDENCE_BRIEF_UNSOURCED`;
  - it lacks `PANEL_QUESTIONING_NOT_DOCUMENTED`.

**Why staged, not edited.** Both `SHA256SUMS.txt` lists pin the file.

**The patch.** `RV24_civic_signal_claim_shape.patch` (+8 −1) does three things:

- it wraps a bare string;
- it raises `INVALID_CLAIMS` for anything not a list of strings;
- it lowercases and strips before the gates.

**Witness** (`stage_rv24_patches.py`, which runs two `git archive HEAD` copies of the kit):

- HEAD: all four probes bypass, one of them by crashing.
- Patched: all four are caught.
- The benign control (`participant_themes`) gains no claim error.
- The kit's own suite still runs 16 OK.

MEASURED.

### F4 — Anon Politician states its own boundaries correctly

- `README_START_HERE.md:18`: tests "do not establish policy efficacy, predictive accuracy, political
  neutrality, representative public opinion or an advantage over ordinary policy analysis".
- The validator's docstring and CLI footer say the same.
- `README.md:78` records that the suites prove preservation and bounded contracts only.
- The claimed counts reproduce: 121 hashes, 16 + 16 tests.

One trap remains. Running the Policy Lab with **pytest** (the repository's default runner) errors at
collection, because `tests/test_evaluation.py` and `evaluation/test_evaluation.py` share a basename.
The documented `unittest` command works. This is a note for the README, not a defect. MEASURED.

### F5 — History preservation holds

- All 26 historical drafts and all 9 background documents carry a status notice above their unaltered
  original body.
- The 7 MB of Anon Politician source is checksum-intact.
- No document in or outside `23_` claims adoption, enactment or endorsement as present fact.

What remains is language *inside* the historical bodies: "Four Standards Ready for Adoption", outreach
plans, `[ACTIVE]` tags. The notices neutralise it, which is the agreed preservation rule. MEASURED.

---

## Keeping the five things apart (brief's distinction)

| Layer | Status, 2026-10-22 |
|---|---|
| **Current law** | Privacy Act 2020 as amended: access (IPP 6), correction (IPP 7), overseas disclosure (IPP 12), and notice of direct and indirect collection (IPP 3, IPP 3A from 1 May 2026). No AI-use notice right. An automated-decision right is UNVERIFIED (not found, full Act not read). |
| **Government policy** | Voluntary Algorithm Charter (2020); AI Strategy (2025) preferring existing law; Public Service AI Framework (guidance). |
| **This proposal** | Six rights, `[PROPOSAL]`, not reviewed by a lawyer, not adopted, no endorsement claimed. Rights 3, 5 and 6 have no tool. |
| **Implementation in this repository** | Local scaffolds only: assure receipts, sovereign permits, the civic-signal checker. Nothing is deployed and nothing is piloted. |
| **Civic validation** | Metadata screening of declared designs. It cannot show that sampling was followed, that a sample is representative, or that outcomes improve. |

---

## Decisions for Mac (G-items)

- **G-CIVIC-CLAIM-SHAPE.** Apply `RV24_civic_signal_claim_shape.patch` and re-mint both `SHA256SUMS.txt`
  lists with a dated note? The QUICK_ACCESS zip copies would stay at the original v0.3 bytes as a
  record.
- **G-WOF-V0.2.** Write the six-rights WOF v0.2, or drop the "should not get its WOF" sentence until it
  exists.
- **G-NZ-LEGAL-READ.** The proposal's own next step 3, a NZ privacy lawyer. With IPP 3A now in force,
  this read is the highest-value step left for Right 1.

---

## Files changed by this batch

| Path | Kind |
|---|---|
| `23_NZ_AI_GOVERNANCE/DATA_SOVEREIGNTY_FOR_NEW_ZEALANDERS.md` | edit: two dated review notes (law; WOF conflict) |
| `docs/nz-governance.html` | edit: IPP 3A and Algorithm Charter in the law section |
| `FOR-REVIEW/2026-10-22_OPUS_REVIEW/stage_rv24_patches.py` | new |
| `FOR-REVIEW/2026-10-22_OPUS_REVIEW/RV24_civic_signal_claim_shape.patch` | new, staged, **not applied** |

Reproduce:

```
python3 -B FOR-REVIEW/2026-10-22_OPUS_REVIEW/stage_rv24_patches.py . <scratch>
(cd 23_NZ_AI_GOVERNANCE/anon_politician && sha256sum -c SHA256SUMS.txt)
```
