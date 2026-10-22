# Batch 25 — RV26: Mystery School, learning, psychological and consciousness claims

**Reviewer:** Sol (Claude Opus 5.5, xhigh). **Date:** 2026-10-22.
**Branch:** `review/full-framework-2026-10-20` at HEAD `d7ae0ad`. Working tree only: nothing committed or pushed.

**Brief (RV26):** review `14_MYSTERY_SCHOOL/` and `17_LEARNING_EMERGENCE/` for clinical, diagnostic,
therapeutic, learning-gain and consciousness claims. Check crisis resources. Separate educational
design, philosophy, fiction and empirical claims.

---

## Coverage — what actually ran

| Item | Method | Result |
|---|---|---|
| `THE_THRESHOLD.md` (crisis page) | NZ list checked line by line against current sources | **F1**. MEASURED |
| Crisis lines elsewhere (`THE_PARENTS_DOOR.md`, `THE_FIRST_MAP.md`) | read | PARENTS: hours missing (F1). FIRST_MAP: correct list, 111 added |
| The doors (FIRST_MAP, THERAPISTS, EDUCATORS) | read in full against their 21-Oct notices | **F4, F5** |
| "Diagnostic" wording, folder-wide | grep | 4 files (**F6**) |
| Three generated protocol pages | read in full; every anchor recomputed by hand | **F2, F3**. All 7 anchors reproduce from the formula. MEASURED |
| `12_IMPLEMENTATIONS/applications/cascade_curriculum_architect.py` | read the anchor, report and course code | **F2**: fixed, new test |
| `12_IMPLEMENTATIONS/systems/aura_sovereign_codex.py:962` | read | second curriculum architect with a different formula (G-item) |
| `IDENTITY_AND_RETURN/source/return_validator.py` | 5 known-bad probes plus a benign control on scratch copies | **F7**. MEASURED |
| `17_LEARNING_EMERGENCE/` (2 essays) | read; grep for proven/guarantee/gain | **F8** |
| `AI_CONSCIOUSNESS_SCHOOL.md` | consciousness wording checked | L124 already says "not sentient". No change |
| Remaining ~60 School files | **not read one by one.** Classified by a folder-level reading key (README) | DID NOT RUN at file level |
| Full suite | `pytest -q --strict-markers` | **1511 passed, 1 skipped, 1 xfailed** (was 1504; +7 new). One UserWarning from `visualization_system.py:109` `plt.show()` under Agg, which predates this batch |

**Sources (read 2026-10-22, with level and grade):**

- **Lifeline Aotearoa**, "Lifeline Aotearoa reduces operating hours due to funding constraints",
  6 Nov 2025: **FULLTEXT**, organisation notice. The new hours are "7.00am – midnight, seven days per
  week. There will be no service between midnight and 7.00am". This covers 0800 LIFELINE, 0508
  TAUTOKO (the Suicide Crisis Helpline) and text 4357. A later Lifeline item (9 Oct 2026) was **not
  opened**. If it restored 24/7 service, the struck "24/7" would be right again (G-CRISIS-LIST-OWNER).
- **Mental Health Foundation, helplines list** (last updated 22 Oct 2025): **FULLTEXT**, organisation
  list. It lists 1737, Youthline (0800 376 633 / text 234), Samaritans (0800 726 666) and Healthline as
  24/7. **Kidsline is not on it.**
- **He Waka Tapu**: 0800 HE WAKA (0800 439 252), Christchurch kaupapa Māori service (HealthPoint/MHERC):
  **ABSTRACT**, directory listings.
- **Goyal M. et al. (2014)**, *Meditation programs for psychological stress and well-being*, JAMA
  Intern Med, PubMed 24395196: **ABSTRACT**, systematic review/meta-analysis. 8-week anxiety d 0.38 (CI
  0.12–0.64) and depression d 0.30 (0.00–0.59). No superiority over active treatments.
- **Stein M. (1998)**, *Jung's Map of the Soul: An Introduction*, Open Court: **METADATA**, book.
- From memory, **not verified this session**: Lehrer et al. (2000) is an HRV-biofeedback protocol paper.
  Zaccaro et al. (2018) and Brown & Gerbarg (2005) are reviews. Box-breathing evidence is small (for
  example Balban et al. 2023, where cyclic sighing beat box breathing). Fixed-stage grief models are
  weakly supported. Khoury et al. (2015) figures were **not retrieved**.

---

## Findings

### F1 — The crisis page told people two lines were open 24/7 when they close at midnight. ✅ fixed

`14_MYSTERY_SCHOOL/THE_THRESHOLD.md` is the page a person in crisis is sent to. Its NZ list had four
faults. MEASURED against the sources above:

| Line (HEAD) | Said | Fact |
|---|---|---|
| 31 | Lifeline 0800 543 354, **24/7** | 7am – midnight since Nov 2025; no service midnight–7am |
| 32 | Suicide Crisis Helpline 0508 828 865, **24/7** | same reduction |
| 33 | Kidsline 0800 543 754, 24/7 | not on the current national list |
| 34 | He Waka Tapu **0800 435 496**, "Māori mental health" | wrong number; the service is 0800 HE WAKA (0800 439 252), and it is a Christchurch kaupapa Māori service, not a crisis line |

**Why it matters.** At 2am, someone following this page would call a closed line.

**Repair** (struck lines kept as the record, following the preservation rule):

- A dated note with sources and a pointer to the MHF list.
- 111 for immediate danger.
- Hours corrected.
- Youthline and Samaritans added, both 24/7.
- An explicit "between midnight and 7am" line.

`THE_PARENTS_DOOR.md:169` gets the Lifeline hours, 1737, and 111. `THE_FIRST_MAP.md`'s note adds 111 and
the Lifeline hours.

### F2 — The protocol generator inflated every forecast about 4–6× and promised an evaluation that does not exist. ✅ fixed at source

**The inflation.** `cascade_curriculum_architect.py` (HEAD lines 409–415) computed
`expected_delta = ±effect_size × (max − min)`. Cohen's d is in **standard deviations**, so multiplying
by the scale **range** is a unit error. Breathwork anxiety came out as 0.55 × 21 = 11.6 GAD-7 points
where about 2–3 is plausible. Every one of the 7 published anchors in the three protocol pages
reproduces exactly from this formula (MEASURED by arithmetic). The inflation factor is range/SD. Its
size, 4–6×, is DERIVED and depends on a typical-SD assumption, because no sourced SD was used.

**Two more faults:**

- The baseline is a placeholder at 70% of the scale maximum, printed as "Baseline".
- "Validation Strength: VERY_STRONG" rates the questionnaire's psychometrics, not the forecast.

**The false promise.** Each page ended: "will be automatically evaluated against measured reality
through the Reality Bridge system … will be automatically demoted or removed". The generator does not
import or call the reality bridge (DERIVED from its imports and call graph). No measurements exist.

**Repair** (code; this is a maintained generator, not canon):

- `ValidatedScale.population_sd` (optional, default None).
- Anchors carry `expected_delta_sd = ±d`, `baseline_is_placeholder: True`, and a raw `expected_delta`
  only when a sourced SD exists. Otherwise it is None, rather than an invented number.
- The renderer prints SD units and labels the baseline a placeholder.
- The QA text now says what is true.

The three committed pages are generated outputs. They keep their original figures struck through,
with SD units beside them and a dated note, so a reader of the old page sees the correction.

**Witness:** `tests/test_curriculum_reality_anchors.py`, 7 tests.

- Against a `git archive HEAD` copy of `applications/`: **7 failed**.
- On the working tree: **7 passed**.

The tests check:

- d stays in SD units;
- a raw change appears only with an SD, and then equals d × SD;
- no forecast exceeds 1.5 SD;
- the report carries no auto-demotion promise;
- shadow work is not labelled COHORT and does not cite "Stein (2004)".

MEASURED.

### F3 — Evidence labels on the protocols overstate their sources. ✅ fixed / annotated

- **Shadow work** was labelled **COHORT (Level 3)**, but it cites no cohort study, only Jung (1951),
  Whitmont (1991) and "Stein (2004) — empirical validation". The Stein book is *Jung's Map of the Soul:
  An Introduction*, 1998, an introductory text (METADATA). The label is now EXPERT_OPINION and the
  citation is corrected. Its four effect sizes (0.72, 0.58, 0.65, 0.80) have no source, and
  "Psychological Integration" has no instrument.
- **Mindfulness** forecasts d 0.63 for anxiety and 0.53 for depression. The meta-analysis it rests on
  most naturally, Goyal 2014, reports 0.38 and 0.30 (ABSTRACT). The source of the higher figures is
  UNVERIFIED and is now marked in code and on the page.
- **Breathwork** says "RCT (Level 4)", but none of its three citations is a trial of this protocol
  (from memory; see the sources section). Annotated, not relabelled: that call needs Lehrer 2000 read
  in full (G-MINDFULNESS-EFFECT-SOURCE covers the sourcing pass).

### F4 — Two doors had claims their 21-Oct notices did not cover. ✅ annotated

**`THE_FIRST_MAP.md`.** The notice covers diagnostic and guarantee wording, but the body also says:

- the four stages "map to established research on post-traumatic growth, grief processing … formally
  proven";
- Microorcim is "mathematically proven";
- "He proved them mathematically";
- box breathing's evidence base is "strong".

None of these holds as stated. A second dated note names each one and keeps the useful advice standing
on its own. The "100% survival" line is pastoral and was left alone.

**`THE_THERAPISTS_DOOR.md`.** It says the Framework "was built independently and arrived at the same
structures … convergence is not coincidence". The Framework names its stages Nigredo to Rubedo and
calls ψ* "Jung's Self" (L48), so the match has a **common cause** and is not independent discovery.
This is the same pattern as RV25 F3. Also unsupported:

- "its stages are reliable" (no reliability study);
- the Lyapunov line, which concerns the model's update rule, not clients.

Annotated. "Non-duality … is the mathematical structure" (L175) is INTERPRETIVE and is recorded here only.

### F5 — The Educators door states universal empirical claims. ✅ annotated

The door makes three claims:

- TRIAD "underlies every effective teaching practice you've ever used" (L38);
- "every effective feedback loop runs" its three phases (L85);
- teachers can "diagnose whether your feedback loop has λ < 1" (L206).

No study here tests the first two, and no procedure in the repository estimates λ from classroom data
(UNVERIFIED: a grep found none). A note classifies the door as educational design and analogy.

### F6 — "Diagnostic" means a reflective map. ✅ annotated

`MYSTERY_SCHOOL_COMPLETE.md` ("the four stages as diagnostic states"), `VOID_CATALOGUE.md` and
`VOID_CATALOGUE_V2.md` ("real-time diagnostic of the practitioner's coherence state") each get one
line: this is not a clinical diagnosis or a validated assessment.

Both VOID files are CRLF. They were edited with line endings preserved: 388/388 and 401/401 CRLF after
the edit, against 386 and 399 before plus two added lines each. MEASURED.

`THE_CHAOS_MAGES_DOOR.md:149` "Diagnostics for what doesn't" is INTERPRETIVE and recorded here only.

### F7 — The return validator enforces the no-manipulative-retention law, but only on a declaration

`return_validator.py` checks `return_constitution.json`. Probes on scratch copies, MEASURED:

| Probe | Result |
|---|---|
| benign (unchanged) | PASS, exit 0 |
| `guilt_notifications` removed from forbidden list | ERROR, exit 1 |
| `skip_penalty_allowed: true` | ERROR, exit 1 |
| `max_default_return_doors: 7` | ERROR, exit 1 |
| `absence_resets_progress: "false"` (truthy string) | ERROR, exit 1 (fails safe) |
| an extra forbidden item | PASS (correct) |

**Limits:**

- It validates a **declared policy file**, not any running product. A product could declare all of
  this and still ship a streak.
- A missing key crashes with `KeyError` instead of reporting.
- `test_validator.py` in the same folder tests `validator.py` (the naming forge), **not**
  `return_validator.py`, which has no test of its own.

Aligned with the engine law's "no manipulative retention loops", and also with Mac's continuity ruling
(memory is required, guilt is banned): `absence_resets_progress` must be false. No change made.

### F8 — `17_LEARNING_EMERGENCE/` makes no gain claims

The two essays (315 and 457 lines, "Written by Sol + Mac") are philosophy and self-reflection. A grep
for proven, guarantee, learning gain and percent-improvement claims found nothing that needs a note.
MEASURED (grep). No change.

---

## Classification of `14_MYSTERY_SCHOOL/` (now in its README)

| Kind | Examples | How to read it |
|---|---|---|
| Educational design | the doors, curricula, IDENTITY_AND_RETURN | teaching structure; not evidence of learning gains |
| Philosophy / interpretation | alchemy, Hermetic and Jungian readings | INTERPRETIVE |
| Fiction / myth | stories, mythic return language | fiction |
| Mathematical models | TRIAD, Microorcim, CASCADE references | proofs hold for the model, not for people |
| Practice protocols | `protocol_*.md` | real literature, forecast effects, nothing measured |
| Crisis resources | `THE_THRESHOLD.md` | must be current; re-check periodically |

---

## Decisions for Mac (G-items)

- **G-CRISIS-LIST-OWNER.** Someone should re-check NZ helpline hours on a schedule. Open the Lifeline
  item of 9 Oct 2026 first: if it restored 24/7 service, the hours note needs updating.
- **G-CURRICULUM-ONE-ARCHITECT.** `systems/aura_sovereign_codex.py:962` holds a second
  `CurriculumArchitect` with a different, also arbitrary forecast formula
  (`-baseline × effect_size × 0.3`, L1043/1046). Retire it, or point it at the fixed generator?
  It was not edited.
- **G-MINDFULNESS-EFFECT-SOURCE.** Do one full-text sourcing pass for the protocol effect sizes and
  population SDs (Goyal 2014, Khoury 2015, Lehrer 2000, GAD-7/PHQ-9/WEMWBS norms). After it,
  `population_sd` can be filled in and the pages regenerated with raw points.
- **G-RETURN-VALIDATOR-TEST.** Give `return_validator.py` its own test, using the probe table above as
  its fixtures?

---

## Files changed by this batch

| Path | Kind |
|---|---|
| `14_MYSTERY_SCHOOL/THE_THRESHOLD.md` | edit: crisis list corrected, struck lines kept, dated note |
| `14_MYSTERY_SCHOOL/THE_PARENTS_DOOR.md` | edit: hours, 1737, 111 |
| `14_MYSTERY_SCHOOL/THE_FIRST_MAP.md` | edit: second dated note |
| `14_MYSTERY_SCHOOL/THE_THERAPISTS_DOOR.md` | edit: dated note (common cause) |
| `14_MYSTERY_SCHOOL/THE_EDUCATORS_DOOR.md` | edit: dated note |
| `14_MYSTERY_SCHOOL/MYSTERY_SCHOOL_COMPLETE.md` | edit: one-line note |
| `14_MYSTERY_SCHOOL/VOID_CATALOGUE.md`, `VOID_CATALOGUE_V2.md` | edit: one-line note, CRLF kept |
| `14_MYSTERY_SCHOOL/README.md` | edit: folder reading key |
| `14_MYSTERY_SCHOOL/protocol_breathwork.md`, `protocol_shadow_work.md`, `protocol_mindfulness.md` | edit: notes, SD units, struck originals |
| `12_IMPLEMENTATIONS/applications/cascade_curriculum_architect.py` | fix: SD units, placeholder flag, truthful QA, shadow label and citation |
| `tests/test_curriculum_reality_anchors.py` | new: 7 tests (fail on HEAD, pass on tree) |

Reproduce:

```
python3 -B -m pytest -q -p no:cacheprovider tests/test_curriculum_reality_anchors.py
```
