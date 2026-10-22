# Batch 24 — RV25: Māori and cross-cultural claims

**Reviewer:** Sol (Claude Opus 5.5, xhigh). **Date:** 2026-10-22.
**Branch:** `review/full-framework-2026-10-20` at HEAD `d7ae0ad`. Working tree only: nothing committed or pushed.

**Brief (RV25):** review `24_LAMAGUE_CROSS_CULTURAL/`, `32_TIANXIA/`, the NZ drafts and the
foundational prose they link to. Check:

- whakapapa, tikanga and sovereignty;
- Wu Chang mappings and Chinese terminology;
- attribution and claimed independence;
- community permission, endorsements, partnerships and outreach status.

State where human or community review is still required rather than inventing agreement.
Analogy is not endorsement.

---

## Coverage — what actually ran

| Item | Method | Result |
|---|---|---|
| `24_LAMAGUE_CROSS_CULTURAL/` (16 files) | census of status notices; grep for endorsement, partnership, permission and review language; claim lines read | F1–F5 |
| `32_TIANXIA/` (41 files) | status census (33 `[SCAFFOLD]`, 4 `[ACTIVE]` position or registry files, 4 without a tag); README, Mandarin registry and Prediction 5 read | F6 |
| Named people in outreach drafts | 4 web searches plus a UN page fetch | F1, F2 |
| Te reo macrons | grep for unmacroned Maori, Pakeha, Ngai Tahu, whanau, hapu, kaumatua and matauranga across both folders, the six-rights proposal and two public pages | **0 hits.** MEASURED |
| Wu Chang dating | grep for Confucius, Mencius and Dong Zhongshu attributions | F4 |
| Simplified and traditional script mix | count per character | 義, 禮, 無為 and 勢 appear in 7 files, mostly in classical quotations inside `32_TIANXIA/papers/`. Recorded as an observation, not a defect |
| Public surfaces | `docs/mystery-school.html`, `docs/lamague-encoder.html`, `docs/LAMAGUE_CROSS_CULTURAL_PAPER.md` | The encoder already marks its tikanga as `[PROPOSAL]` pending iwi review (lines 769–770). The other two are fixed (F3, F5) |
| `llms.txt` | grep | no cross-cultural convergence claim |
| Full suite after the edits | `pytest -q` | **1504 passed, 1 skipped, 1 xfailed.** MEASURED |
| Not done | — | no reading of the 33 TIANXIA scaffolds' operator mathematics (Batch 20 covered `ren_zheng` and `wang_dao` code); no check of the Mandarin translation quality beyond the claims named here |

**Primary sources (dated 2026-10-22, with verification level):**

- **UN High-level Advisory Body on AI, member page** (un.org/en/ai-advisory-body/members): **FULLTEXT**,
  through the fetch agent with verbatim quotes. The members with Chinese affiliations are **Yi Zeng**
  (Chinese Academy of Sciences) and **Zhang Linghan** (China University of Political Science and Law).
  "Xue Lan" does not appear.
- **University of Otago senior leadership profile**: **ABSTRACT** (search result). It lists Jacinta Ruru
  as Raukawa, Ngāti Ranginui, and as Deputy Vice-Chancellor, Māori since March 2024. Other profiles
  also name Ngāti Maniapoto.
- **Tsinghua I-AIIG and Schwarzman pages**: **ABSTRACT**. Xue Lan is Dean of I-AIIG and chair or
  director of the National Expert Committee on New Generation AI Governance; the sources differ on the
  title.
- **Peking University IAI pages**: **ABSTRACT**. The dean is Zhu Songchun (朱松纯).
- Wu Chang history (Mencius 四端; Dong Zhongshu 五常): **from memory**. It is standard history, and the
  repository's own paper §2 and `CHINESE_MAORI_CONVERGENCE.md:24` agree with it.

---

## Findings

### F1 — A living Māori scholar's iwi was misattributed. ✅ corrected

**The error.** `TE_TUMU_OUTREACH.md:9,12` and `CATALYST_NZ_CHINA_APPLICATION.md:204` name Professor
Jacinta Ruru as **Ngāi Tahu** and call that "correct cultural ground". Her university lists **Raukawa,
Ngāti Ranginui**.

**Why it matters.** For a project whose Māori material rests on "pending iwi validation", assuming a
named person's whakapapa is the most serious error in this batch. The draft would have opened a first
contact with it. The profile is also stale: she has been DVC Māori since 2024.

**Repair.** A review note at the top of the outreach draft. The original words are struck through and
the correction sits beside them in both files, so the record keeps both. MEASURED (the repository
text) and ABSTRACT (the source).

### F2 — The Chinese outreach draft carries two false facts about named people. ✅ corrected

| Draft says | Source says |
|---|---|
| Xue Lan is a "Member of the UN Secretary-General's High-level Advisory Body on AI" | Not on the UN member list. The Chinese members are Yi Zeng and Zhang Linghan. FULLTEXT |
| "Professor Zhu Songbo (朱松波) — PKU AI Institute", with an "AI ethics and governance track record" | No such person was found. The PKU-IAI dean is **Zhu Songchun (朱松纯)**, a computer vision and general-AI researcher. ABSTRACT |
| Xue Lan has a "Deep Confucian-inflected governance philosophy background" | He is a science and technology policy scholar. The characterisation is UNVERIFIED |
| Fu Ying is "Chair, IAIIG Advisory Committee" | UNVERIFIED |

These have the pattern of model-generated contact lists: a plausible title on a real person, and a
near-miss name. Sending them would have discredited the approach on its first line.

**Repair.** A top note plus strike-throughs; nothing deleted. DERIVED (the pattern) and MEASURED (the
corrections).

### F3 — "Independent convergence" is asserted as a finding, but the argument has two common causes. ✅ annotated

The claim recurs in seven places:

- the Catalyst abstract and its One Paragraph;
- `CHINESE_MAORI_CONVERGENCE.md:14,90`;
- `MANDARIN_GOVERNANCE_SUMMARY.md:66,69`, in both languages;
- `CONVERGENCE_MAP.md`;
- the `CELTIC_CONVERGENCE.md` table;
- the public paper's abstract and contribution 2;
- the public `docs/mystery-school.html` card ("Independent convergence across 2,500 years").

The claim: three traditions independently discovered the same constraint structure.

**Common cause 1 — AURA is not an independent tradition.** It was written in 2025–26 by an author with
access to Confucian and Māori thought, directly and through AI assistance. Counting it as a
"discovery" alongside traditions it was later mapped onto is circular.

**Common cause 2 — the encodings share one encoder.** The traditions may well have developed without
contact; the paper's timeline argues this. But **all three LAMAGUE encodings were produced by one
author with one operator vocabulary**. Shared primitive operators, which are the paper's P1 test and
the application's ">80% shared operators" rule, can therefore come from the encoder. The design that
would actually test the hypothesis is the application's own Phase 1, done properly: encoders from
within each tradition, working blind.

The repository already hedges in places: the 24 README ("Similarity does not establish equivalence,
independent discovery or endorsement"), the "What This Does Not Mean" section, and the closing
`[CONJECTURE]`. The headline claims still overrun those hedges.

**Repair.** Dated notes in each file, including a Chinese note in the Mandarin summary written for
its Chinese-reading audience. The public card now reads "A proposed convergence across 2,500 years,
not yet reviewed by scholars within the tradition". DERIVED.

### F4 — Wu Chang is dated to Confucius in three places; the repository itself knows better. ✅ annotated

These three places date the five constants (仁义礼智信) to Confucius, ~500 BCE / 6th century BCE:

- `CONVERGENCE_MAP.md:27`;
- `CELTIC_CONVERGENCE.md:185`;
- the paper's Introduction (line 35, "formalised from approximately 500 BCE").

Against them:

- The Analects centre on 仁 and 礼.
- Mencius named the four sprouts (四端: 仁义礼智).
- The five-term set with 信 is credited to **Dong Zhongshu** (Han, 2nd c. BCE). That is how
  `CHINESE_MAORI_CONVERGENCE.md:24` and the paper's own §2 (line 95) date it.

`CONVERGENCE_MAP.md:30`'s "Four Social Bonds" garbles 四端 (the four sprouts) with 五伦 (the five
relationships). This is an internal inconsistency, and a Confucian scholar reviewer would see it at
once.

**Repair.** Notes; no body text rewritten. From memory, corroborated by in-repository text.

### F5 — The Catalyst application has stale counts, an affiliation it lacks, and an unverified entity. ✅ annotated

- **The counts contradict each other.** The abstract says "thirteen Python implementations" and "a
  formal arXiv preprint". The table says 26 implementations, 80 tests, and a preprint "awaiting cs.AI
  endorsement", so not posted. Today the suite runs 1,504 tests.
- **The ethics plan depends on an affiliation it does not have.** It names the University of Otago
  Human Ethics Committee. The partner plan only proposes to *ask* Otago about affiliation (lines
  199–200).
- **The entity is unverified.** "Lycheetah Foundation" appears in 46 markdown files. No registration
  record was found in the repository. A grant application must name the applicant's real legal form.
  UNVERIFIED, so it becomes a G-item.
- **Endorsements are targets.** "Reviewed and endorsed by Chinese philosophy scholars" (line 104) and
  regional-body endorsement (line 158) are written as outputs and KPIs, not present facts. The note
  says so explicitly.

The 24 README already marks the whole folder: "No institutional partnership, grant award or community
approval is established". The repository has no evidence that any email in this folder was sent.

### F6 — TIANXIA's "primary intellectual partnership" is an aim; the module's own registry says so. ✅ qualified

`32_TIANXIA/README.md:8` calls the module "primary intellectual partnership". Two facts cut against
that:

- `MANDARIN_PRIMARY_REGISTRY.md` logs **zero** direct Mandarin readings: "the framework has not yet
  logged a direct Mandarin reading of any primary governance document".
- No scholar from within the tradition has reviewed the module.

`POSITION_PAPER_v0.1.md` Prediction 5 already makes this falsifiable: engagement in a
Chinese-tradition venue by end-2028, or a downgrade to `[CONJECTURE]`. That is honest and good.

**Repair.** The README sentence now says "an aim, not yet a relationship", states both facts, and
links to the falsifier. The module's disclaimers are otherwise strong: every operator file has a
negative-space section stating that it endorses no programme. MEASURED.

### Preserved, by design

- The historical outreach drafts keep their full bodies. Corrections are struck through beside the
  original words.
- The tikanga columns stay `[PROPOSAL]` everywhere they appear. No file claims iwi validation.
- The NZ drafts in `23_` were covered in Batch 23. `NZ_LAMAGUE_STANDARD.md`'s Māori encodings are
  listed as "pending iwi validation".

---

## Where human and community review is required

Sol cannot supply any of these, and nothing in the repository supplies them yet:

1. **Māori knowledge holders**, through a permissioned process the community chooses, not one the
   project designs: every tikanga mapping, Te Pūkōrero encodings, and whether these concepts should be
   encoded at all. `CHINESE_MAORI_CONVERGENCE.md:144` itself asks whether formalisation loses the
   relational quality.
2. **Confucian scholars, ideally Mandarin-native**: the Wu Chang–AURA mapping, the CONFUCIAN_LAMAGUE
   encodings, and the Mandarin summary's translation, which is self-declared AI-assisted.
3. **Encoders from within each tradition, working blind**: the only design that can test "structural
   isomorphism" (F3).
4. **A NZ constitutional scholar**: the Te Tiriti "constitutional partnership" framing.
5. **Mac**: whether any of these outreach messages were ever sent. The repository cannot tell.

---

## Decisions for Mac (G-items)

- **G-OUTREACH-SENT.** Were any of the Te Tumu, MBIE or Chinese-partner emails sent with the old
  errors? If one reached Professor Ruru with "Ngāi Tahu", a short correction would be the right
  follow-up. Sol has no way to check.
- **G-FOUNDATION-ENTITY.** Is "Lycheetah Foundation" a registered entity? If not, the 46 files that use
  it, two of them in grant drafts, should say "Lycheetah Framework (independent researcher)".
- **G-LAMAGUE-EXPANSION.** Four expansions of the acronym are in use:
  - 9× "Language of Alignment, Measurement, and Governance for Universal Ethics";
  - 4× "Language for Autonomous Mathematical Alignment and Universal Grammar Evolution";
  - 1× "Language for Everything";
  - 1× "Language-Agnostic Multi-Tradition Governance Universals".

  Pick one, under the one-truth law.
- **G-CONVERGENCE-HEADLINE.** Recast the cross-cultural headline from "independent discovery" to "a
  proposed mapping awaiting blind encoding by each tradition"? That would mean rewriting the abstracts
  of the paper draft and the application rather than annotating them. This is an authorship choice.

---

## Process note (Sol's own error, caught)

The batch edit read `docs/LAMAGUE_CROSS_CULTURAL_PAPER.md` in text mode, which silently converted its
438 CRLF line endings to LF. The result was an 890-line diff for a 14-line note.

- **Caught by:** `git diff --stat`.
- **Fixed:** CRLF restored byte-for-byte. The diff is now +14 −0, and `git diff --ignore-cr-at-eol`
  agrees.

Future bulk edits must check `\r` counts first, as the stage scripts already do.

---

## Files changed by this batch

| Path | Kind |
|---|---|
| `24_LAMAGUE_CROSS_CULTURAL/TE_TUMU_OUTREACH.md` | note + strike-through corrections (F1) |
| `24_LAMAGUE_CROSS_CULTURAL/CHINESE_PARTNER_OUTREACH.md` | note + strike-through corrections (F2) |
| `24_LAMAGUE_CROSS_CULTURAL/CATALYST_NZ_CHINA_APPLICATION.md` | note (F3, F5) + iwi correction (F1) |
| `24_LAMAGUE_CROSS_CULTURAL/CHINESE_MAORI_CONVERGENCE.md` | note (F3, the Te Tiriti claim) |
| `24_LAMAGUE_CROSS_CULTURAL/MANDARIN_GOVERNANCE_SUMMARY.md` | bilingual note (F3) |
| `24_LAMAGUE_CROSS_CULTURAL/CONVERGENCE_MAP.md` | note (F3, F4) |
| `24_LAMAGUE_CROSS_CULTURAL/CELTIC_CONVERGENCE.md` | note (F3, F4) |
| `docs/LAMAGUE_CROSS_CULTURAL_PAPER.md` | note (F3, F4, acronym), CRLF preserved |
| `docs/mystery-school.html` | public card wording (F3) |
| `32_TIANXIA/README.md` | partnership qualified (F6) |
