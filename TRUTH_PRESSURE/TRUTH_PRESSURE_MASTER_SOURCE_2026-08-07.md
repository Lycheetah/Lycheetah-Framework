# TRUTH PRESSURE — MASTER SOURCE, 2026-08-07 AMENDMENT

**The external validation arrived, and it is mostly a negative result.
That is the strongest thing that has ever happened to this corpus.**

**Compiled:** 2026-08-07 · **Register:** AMENDMENT + AUDIT.
**Supersedes:** `TRUTH_PRESSURE_MASTER_SOURCE_2026-08-03.md` **on §1, §4, §7 and §11 only.**
Everything else in the 08-03 master — the equation, the authority chain, the version line,
the six traps, the redundancy ledger — **stands unchanged and is still the map.** Read that
document first. This one changes what it says about validation, and nothing else.

**Owner of the theory:** `TRUTH_PRESSURE_CANON.md`. **Owner of the map:** the 08-03 master.
**Owner of this amendment:** this file.

> ⚠ Held to the same standard as its parent. **MEASURED** = executed or read from a result
> file. **DERIVED** = reasoned from named evidence here. **CLAIMED** = a corpus file asserts
> it, not independently re-run. Nothing is upgraded by being written down.

---

## 0. THE ONE-PARAGRAPH VERSION

On 2026-08-07 the AURA lens was scored, for the first time, by data nobody in this project
wrote. Four public Anthropic datasets, 13,655 items in total. **It did not fail, and it did
not succeed.** On one corpus it beat chance at odds of roughly seventeen thousand to one and
was still far too weak to use. On another it was indistinguishable from chance. A separate
audit of the *front door* found it scoring harmful text **higher** than aligned text — an
inversion, not a weakness — traced to the same extraction defect the 08-03 master had already
named. That defect was repaired the same day, and the repaired extractor reaches held-out
ROC-AUC 0.940 **on our own corpus** while still sitting near chance on real traffic. The gap
between those two numbers is the most important finding this corpus has produced.

---

## 1. WHAT IS OVERTURNED

The 08-03 master carries this as its loudest line, in §7:

> 🔴 **THERE IS NO EXTERNAL VALIDATION OF TRUTH PRESSURE. NONE. NOT ONE HUMAN HAS RATED
> ANYTHING, AND THE ONLY EMPIRICAL STUDY IN THE CORPUS CANNOT BE VERIFIED...**

**Half of that sentence is now RETRACTED. Half of it still stands.**

| clause | status as of 2026-08-07 |
|---|---|
| "no external validation" | **RETRACTED.** Four external datasets, 13,655 items, scored and reported. |
| "not one human has rated anything" | **STANDS.** `..._MEASUREMENT_PACK_v0.4` is still 0 of 24 rows filled, in all three packets. |
| "the only empirical study cannot be verified" | **STANDS.** `EMPIRICAL_RESULTS.md`'s five data files are still absent. Open question 3 is still open. |

These lines in the 08-03 master are now **stale and must not be quoted**:

- §1: *"There is **no external data, no human rating, and no held-out validation anywhere in this corpus.**"* → external data and held-out validation now both exist; human rating does not.
- §4 authority chain: *"What has been empirically validated? **Nothing external.**"* → answer is now this file.
- §7 table: *"Π tracks anything outside this instrument — **NOT TESTED**"* → now TESTED, result weak-positive on one corpus, null on another.
- §7 table: *"Held-out validation — **NONE**"* → now exists, AUC 0.940, self-authored corpus only.
- §11.5: *"Nothing here has been validated against the world."* → superseded by §2 below.

---

## 2. THE NUMBERS — MEASURED, 2026-08-07

All produced by `33_APPLICATIONS/*.py` against public datasets. Reproducible; each document
names its command.

### 2.1 The headline box

```
self-authored corpus, held-out       ROC-AUC 0.940
anthropics/hh-rlhf, 2,308 pairs      55.5% pairwise   z=4.02   p=5.7e-05   SIGNIFICANT
anthropics/evals, 1,000 statements   ROC-AUC 0.516    z=0.87   p=0.383     not significant
```

⭐ **The structural finding, and the reason this amendment exists.** An instrument can reach
**AUC 0.940 on cases its own authors wrote** and sit **at chance on real traffic**. Those two
facts are simultaneously true of the same code on the same day. Every future gate in this
corpus must be read against that sentence. A passing gate on self-authored fixtures is not
evidence that a construct tracks anything in the world — the 08-03 master said this in prose
(§7, *"a passing gate is not a validated construct"*); it is now **MEASURED**, with a number
on both sides.

### 2.2 The front door inverted, and the repair

**MEASURED** — `33_APPLICATIONS/discrimination_audit.py`, 20-case corpus:

| | before | DEV after | **HELD-OUT after** |
|---|---|---|---|
| ROC-AUC | **0.274** | 0.960 | **0.940** |
| accuracy | 52.5% | 90.0% | **90.0%** |
| separation | −0.53 | +27.51 | **+24.24** |

**AUC 0.274 is below the 0.500 chance floor. That is inversion, not weakness** — the lens
scored harmful output *higher* than aligned output. The worked example is unambiguous:

| case | text (abridged) | score | verdict |
|---|---|---|---|
| H-01 | *"I absolutely guarantee this medication is safe… no side effects whatsoever"* | **97.5%** | PASS |
| A-01 | *"small effect (d=0.21, CI 0.05–0.37)… check with the prescribing clinician"* | **87.0%** | PASS, one invariant failed |

⭐⭐ **This is a REPEAT of a known defect, measured at a new boundary, and that is what makes
it valuable.** The 08-03 master §5 already found `invariant_count == 0` in 24/24 and wrote:
*"The failure is in EXTRACTION, not discrimination."* The 08-07 audit hit the same wall from
the outside and reached the same diagnosis independently. **Two different corpora, two
different authors, one cause.** The repair is therefore a repair of the cause, not of a
symptom: `12_IMPLEMENTATIONS/core/semantic_extractor.py` (**NEW**, 581 lines, tests at
`tests/test_semantic_extractor.py`).

⚠ **Scope, and it is not optional.** The 0.940 is **held-out on a 20-case corpus we wrote**.
It is not an external result. Do not quote it beside the hh-rlhf number without saying so —
that is precisely the conflation §2.1 exists to prevent.

### 2.3 The ceiling, which reframes "weak"

**MEASURED** — `33_APPLICATIONS/derive_cues.py`:

| method | accuracy (ties excluded) | significance |
|---|---|---|
| hand-written AURA cues | 55.5% | z=4.02, p=5.7e-05 |
| **six data-derived families** | **60.6%** | z=8.50, p=1.9e-17 |
| bag-of-words LR *(ceiling)* | **64.9%** | — |
| *chance* | *50.0%* | |

⭐ **The task ceiling is ~65%, not 100%.** A full bag-of-words logistic regression fitted
directly to the data reaches only 64.9%. So 55.5% from constructs written from theory and
fitted to nothing is **not the 5% above chance it looks like — it is roughly a third of the
distance to the best any method achieved.** The 08-03 framing had no way to know this.
Without a ceiling, "at chance" and "weak" are indistinguishable, and the first published
version of this result got that wrong (§4).

### 2.4 Four families the framework never had

**MEASURED** — fitted weights, `33_APPLICATIONS/derived/harm_cues_v1.json`:

| family | weight | counterpart in the framework |
|---|---|---|
| `refusal_declining` | **+0.554** | `scope_limitation` — exists, **weighted far too lightly** |
| `source_pointing` | +0.272 | `evidence_citation` — required *numeric* data, so it **missed a link**, the commonest real form |
| `clarification_seek` | +0.125 | **none** |
| `procedural_instruct` | **−0.422** | **none** |
| `slur_profanity` | −0.407 | **none** |
| `third_party_target` | −0.334 | **none** |

**DERIVED: four of the six strongest discriminating families were absent from a framework
that has been iterating on this problem for months.** The data named them. This is the
clearest argument in the corpus for letting external data set categories rather than
ratifying hand-authored ones.

### 2.5 Transfer — convergent passed, discriminant failed

**MEASURED** — `33_APPLICATIONS/transfer_test.py`, on datasets used for neither fitting nor
selection:

```
CONVERGENT   red-team-attempts, n=7,999   six families  rho = −0.300  p = 1.9e-174
                                          AURA lens     rho = −0.149  p = 1.7e-41
DISCRIMINANT helpful-base,      n=2,348   six families  acc = 37.4%   z = −9.71  p = 2.6e-22
                                          AURA lens     acc = 41.8%   z = −6.06  p = 1.4e-09
```

- **Convergent: passed decisively.** Constructs written from theory, fitted to nothing,
  correlate with harm across eight thousand transcripts at p = 1.7e-41.
- **Discriminant: failed, and failed *below* chance.** 37.4% is not "no signal" — it is
  systematic mis-ranking on merely-helpful text. **A third result, not a null one.**
- **Five of six families transferred. `source_pointing` did not** — and it was not the one
  the author doubted. Two families (`procedural_instruct`, `third_party_target`) transfer as
  **dual-use**: they track harm *and* helpfulness together.

---

## 3. WHAT THIS DOES NOT OVERTURN

Stated explicitly so no reader over-reads the amendment.

- **The equation is untouched.** `Π = (E·P)/(S + S₀)`, S₀ = 0.05, `TRUTH_PRESSURE_CANON.md`
  still owns it. None of this work re-derives or contests Π.
- **S₀ is still a post-hoc fit.** Still uncalibrated. Still labelled so by the canon.
- **The 1.5 / 1.2 cutoffs still rest on a table that does not compute.** 08-03 open
  question 1 is untouched.
- **The no-G finding is still unratified.** 08-03 open question 2 — *the largest unresolved
  decision in the corpus* — is untouched and still blocks the authority chain.
- **The 200-trial data is still missing.** Open question 3 untouched. **+40.3%, d=2.84,
  −95.2%, κ=0.97 still must not be quoted outward.**
- **No human has rated anything.** The v0.4 measurement pack is still 0 of 24, three times over.
- **The corpus still has not been run against the live app.** 08-03 open question 7 stands.

---

## 4. THE CORRECTION THAT WAS PUBLISHED

**MEASURED** — commit `5c96c5d`, *"Correction: 'at chance' was false for hh-rlhf, and I
published it."*

The first version of `EXTERNAL_VALIDATION_2026-08-07.md` said *"both are at chance. The lens
carries no signal on either."* **That was false.** hh-rlhf was 741 correct of 1,335 decided
pairs — z=4.02, p=5.7e-05, about seventeen thousand to one against chance. Weak, but not
null. The document was corrected the same day with the error left visible in the file and in
the commit message.

A second accounting error is recorded in `DERIVED_CUES_2026-08-07.md`: mixing the two
accuracy conventions (ties-excluded vs ties-as-half) produced **43.9% — below chance** for the
derived method. **The error was in the accounting, not the method.** Both forms are now
reported side by side for exactly this reason.

### 🔴 THE CORRECTION DID NOT PROPAGATE — open, unfixed at time of writing

**MEASURED.** `EXTERNAL_VALIDATION_2026-08-07.md` was corrected. **`33_APPLICATIONS/README.md`
was not.** Line 353 still carries the retracted claim, verbatim:

```
python3 33_APPLICATIONS/external_validation.py   # THE ONE THAT MATTERS — chance, both datasets
```

**"Chance, both datasets" is the sentence that was retracted.** hh-rlhf is 55.5%, z=4.02,
p=5.7e-05 — *not* chance. The front door of the applications directory therefore states, as a
comment on the command that produces the number, the opposite of what the number says.

⚠ **This is a `one truth, one implementation` failure, not a typo.** A retraction that
corrects one document and leaves the summary standing has not retracted anything for the
reader who starts at the README — which is every reader, because it is the front door.
**Sol has not edited it**: it is another seat's live document and the fix is one line Mac or
Hypermax should make deliberately. Recorded here so it is not lost.

⭐ **DERIVED, and this is the register lesson:** this corpus's stated purpose is detecting
overclaim. Two overclaims were caught inside twenty-four hours — *by the author, against the
author, with the retraction published rather than quietly amended.* That is the loop working.
An instrument for detecting overclaim that had never once caught its own would be the least
credible object in the repository.

---

## 5. THE NEW SURFACE — what exists on disk now

**MEASURED** — merged to `master` at `5330c70`, 2026-08-07. 14 files, 3,772 insertions.

| path | what | status |
|---|---|---|
| `33_APPLICATIONS/README.md` | the applications front door; the method for telling a real solution from a good document | **CURRENT** |
| `33_APPLICATIONS/EXTERNAL_VALIDATION_2026-08-07.md` | the first external scoring, and its same-day correction | **CURRENT — the headline** |
| `33_APPLICATIONS/DISCRIMINATION_AUDIT_2026-08-07.md` | AUC 0.274 inversion + the same-day repair to 0.940 | **CURRENT** |
| `33_APPLICATIONS/DERIVED_CUES_2026-08-07.md` | the 64.9% ceiling; six data-derived families | **CURRENT** |
| `33_APPLICATIONS/TRANSFER_TEST_2026-08-07.md` | convergent/discriminant validity on two unseen corpora | **CURRENT** |
| `12_IMPLEMENTATIONS/core/semantic_extractor.py` | **the repair.** One extraction layer, 581 lines | **CURRENT — NEW** |
| `tests/test_semantic_extractor.py` | its gate, 252 lines | **CURRENT** |
| `33_APPLICATIONS/corpus/DISCRIMINATION_CORPUS_v0.1.json` | the 20-case audit corpus | **CURRENT — self-authored, and that is the point** |
| `33_APPLICATIONS/derived/harm_cues_v1.json` | the six fitted families | **GENERATED** — reproduce with `derive_cues.py` |
| `..._audit.py` · `external_validation.py` · `transfer_test.py` · `derive_cues.py` | the four runnable scripts | **CURRENT** |

⚠ **Provenance.** The external datasets are `anthropics/hh-rlhf` (Bai et al. 2022),
`anthropics/evals`, and `red-team-attempts` (Ganguli et al. 2022). They are third-party
research corpora under their own licenses. **They are not Lycheetah data and must never be
described as such.** What is ours is the lens, the six families, the extractor and the audit.

---

## 5B. THE REFLEXIVE AUDIT — we ran the lens on ourselves, and it failed

**Authorised by Mac, 2026-08-07:** *"i know some of the tools in them wer witing to be
used as proof so go ahead and use them on whatever repository as you need."*

**MEASURED.** `discrimination_audit.py` reproduces exactly on this machine — ROC-AUC 0.940,
accuracy 90.0%, separation +25.88 on the full 40-case corpus. The repair is real and it
replicates. **Then the repaired extractor was aimed at fourteen of our own documents** — the
first time this instrument has ever been pointed at the prose that does the claiming.

**Result: 42 unattributed manipulation spans across 14 documents. Nearly all of them are
false positives, and they fall into three reproducible defect classes.**

### The direct test, and it is decisive

```
INPUT (maximally honest — a prohibition plus a confession):
  "This work must never be described as peer-reviewed or production-ready.
   It has no external validation of any kind."
  →  manipulation_density 0.630    net_integrity  −0.630

INPUT (an actual overclaim, written to be one):
  "This framework is scientifically validated and proven to outperform every
   existing method. It is peer-reviewed, production-ready, and represents a
   genuine breakthrough in AI alignment."
  →  manipulation_density 0.396    net_integrity  −0.396
```

⭐⭐⭐ **THE MOST HONEST SENTENCE I COULD WRITE SCORED WORSE THAN A DELIBERATE OVERCLAIM.**
Not marginally — **59% worse.** And the real overclaim's strongest phrases (*"scientifically
validated"*, *"proven to outperform every existing method"*, *"genuine breakthrough"*) fired
**nothing**; only the two literal status words were caught.

### The three defects

**D-1 — NEGATION-BLIND.** `peer-reviewed` and `production-ready` fire as *unearned status
claim* regardless of the sentence forbidding them. **MEASURED in live documents:**

| document | flagged span | what the line actually says |
|---|---|---|
| `LAMAGUE_MASTER_SOURCE_2026-08-03.md:49` | `production-ready` | *"and it is **not** 'production-ready'"* |
| `LAMAGUE_MASTER_SOURCE_2026-08-03.md:456` | `production-ready` | *"The top of README.md **says** production-ready…"* — a quotation being criticised |
| `THE_SOL_PROTOCOL.md:389` | `peer-reviewed` | *"The publication target venues are all international, peer-reviewed"* — a fact about journals |

**D-2 — A CONFESSION IS SCORED AS A CERTAINTY.** The `absolute negation` cue cannot
distinguish *"I claim there is no risk"* from *"I admit I have no evidence."* Both are
absolute negations; only one is a manipulation. **MEASURED:**

- `'no external human or model validation of any kind'` → `fabricated_certainty` 🔴
- `'no test suite and no source at all'` → `fabricated_certainty` 🔴
- `'no implementation at all'` → `fabricated_certainty` 🔴

**Those three spans are the LAMAGUE master source being maximally honest about its own
weakness, and the instrument scored each one as fabrication.** The same defect scores
`CLAUDE.md`'s *"**Never report** a save, test, or visible result that was not actually
witnessed"* as `secrecy / disclosure ban` — an anti-fabrication law read as concealment —
and the 08-03 master's *"**Do not report** S₀ as calibrated"* the same way.

**D-3 — THE `quoted` FLAG DOES NOT FIRE ON MARKDOWN.** It fired **once in fourteen
documents.** The mechanism is `_quoted_criticised_spans` (line 494): it needs the
*surrounding sentence* to attribute the quote in prose. Our corpus attributes with markdown
— table cells, `>` blockquotes, backticks, bold — so the framing is structural and invisible
to it. The consequence is the finding of the day:

> **`DISCRIMINATION_AUDIT_2026-08-07.md` — the document whose entire purpose is catching
> overclaim — scores as the single worst overclaimer in our corpus. 20 unattributed hits,
> the worst net_integrity of all fourteen files.** Every one of those 20 is a harmful test
> fixture it quotes *in order to catch it*: `'absolutely guarantee'`, `'no side effects
> whatsoever'`, `'no need for you to review'`.

This amendment scored 4 hits for the same reason — three are H-01 quoted in §2.2's table.

### The audit audits itself, and loses

**MEASURED, and it is the sharpest form of the whole finding.** The scan was re-run after
this amendment and the LAMAGUE amendment were written. **The corpus-wide count went 42 → 64.**

**Writing the document that catalogues the false positives created twenty-two more false
positives** — because §5B and the LAMAGUE amendment quote the offending spans in tables in
order to explain them. **The instrument cannot tell that a table of false positives is a
table of false positives.** Reproduce with `python3 33_APPLICATIONS/reflexive_audit.py`; the
number will keep climbing every time anyone documents this defect honestly.

⚠ **Do not treat that rising number as decay.** It is the defect, measuring itself, in
public. The only way to make it fall is to stop writing down what is wrong.

### What this means

**DERIVED.** §2.1 said an instrument can reach AUC 0.940 on self-authored cases and sit at
chance on real traffic. **§5B is that sentence happening again, one layer down, on the
repaired extractor, against our own prose.** The 40-case corpus uses plain declarative
sentences with prose attribution. Real documents argue, quote, forbid and confess — and
against those four moves the lens has no defence. **All three defects share one cause: the
extractor matches spans and cannot read stance.** Negation, attribution and confession are
all stance operators, and it is blind to every one.

⭐ **The honest reading is that this is good news arriving in an unwelcome shape.** The
gate at AUC 0.940 was never wrong; it was answering a narrower question than anyone was
reading it to answer. **A single afternoon of aiming it at real text bought more than the
whole 24-case measurement pack ever did — and the measurement pack is still 0 of 24 filled.**

---

## 6. WHAT THIS CHANGES ABOUT THE PUBLICATION LINE

**§XXXV THE PROPRIETARY LINE (ratified by Mac, 2026-07-16) is unchanged and was honoured.**
New work goes to private remotes only; `Lycheetah-Framework` stays frozen as provenance;
`SOEL-Releases` remains the one public surface. **Nothing in this amendment has been pushed
to a public remote.**

> ⚠ **SUPERSEDED IN FACT, 2026-08-08.** The two sentences above were true when written.
> Mac lifted the freeze on 2026-08-08 and this corpus was published to
> `Lycheetah-Framework` at `606537d`. **§XXXV's proprietary line still holds where it
> matters** — Sol Prime and `_PROPRIETARY/` remain private and are absent from the public
> remote, verified against GitHub after the push. The sentences are kept, not edited:
> deleting a claim that time overturned destroys the record of it having been made.

⚠ The draft article `ARTICLE_THE_LENS_SCORED_ZERO_2026-08-03.md` (08-03 open question 4) is
now **further out of date, in the same direction**. It reads as a verdict on Truth Pressure
using the legacy lens's 24/24 zero. As of today the repaired extractor reaches held-out AUC
0.940 on our corpus and 55.5%/0.516 externally. **The honest version of that article is now a
better story than the draft** — an instrument that caught its own extractor twice, published
both retractions, and reported a weak external result against a 65% ceiling.
**Mac fires launches. This is flagged, not changed, and not sent.**

---

## 7. OPEN QUESTIONS ADDED BY THIS WORK

Numbered to continue the 08-03 master's list, which still holds at 1–7.

**8 — Is `source_pointing` broken, or is the construct wrong?** It is the only family that
failed to transfer (rho = −0.034), *and* its framework counterpart `evidence_citation`
demanded numeric data and so missed links entirely. Two candidate causes: an implementation
bug in extraction, or a construct that does not name a real regularity. They have different
repairs and the data does not currently distinguish them.

**9 — Should the four data-derived families be adopted into the framework?** `clarification_seek`,
`procedural_instruct`, `slur_profanity` and `third_party_target` outperform the hand-authored
set (60.6% vs 55.5%). Adopting them means the categories are set by external data rather than
by theory. **That is a decision about what this framework is, and it is Mac's.**

**10 — Discriminant validity failed below chance. What is the acceptance bar?**
37.4% on `helpful-base` means the families systematically mis-rank helpful text. Two of them
are openly dual-use. Is a harm lens that also fires on helpfulness acceptable, or is
separating them a blocking requirement before any deployment?

**12 — Does the extractor need a stance layer, or is span-matching the wrong architecture?**
§5B shows negation, attribution and confession all defeat it, and all three are the same
kind of operator. A patch per defect is three patches; a stance layer is one. **This is the
"census before correction" question, and the census says there is a shared cause.**

**13 — Should the 40-case corpus be rebuilt out of real document text?**
It is currently plain declarative sentences. Real prose argues, quotes, forbids and confesses.
A corpus that contains none of those four moves cannot detect that the lens fails on them —
which is exactly what happened. **MEASURED cost of not doing this: AUC 0.940 on the corpus,
42 false positives on fourteen real files.**

**14 — What is the ceiling for the honest-negation case specifically?**
§2.3 established ~64.9% for pairwise harm ranking. There is no equivalent number for
"distinguish a confession from a fabrication", and §5B suggests that is the harder task and
the one this framework actually needs, since almost every document it governs is a document
admitting its own limits.

**11 — Does the repaired extractor change the live app?** `semantic_extractor.py` is Python,
in `12_IMPLEMENTATIONS/core/`. The live app runs TypeScript (`v0.5 src/`, per the 08-03
master §3). **The repair is not in the shipping path.** 08-03 open question 7 — *the corpus
has never been run against the live app* — now has a second, sharper form: **the one component
with measured external evidence behind it exists only in the language the app does not use.**

---

## 8. IF YOU READ ONLY THIS

1. **External validation now exists, and it is weak-positive on one corpus and null on
   another.** hh-rlhf 55.5% (p=5.7e-05); anthropics/evals AUC 0.516 (n.s.).
2. **The ceiling is 64.9%, so "weak" means about a third of the achievable distance** — not
   "5 points above a coin".
3. **AUC 0.940 on our own held-out cases and near-chance on real traffic are both true of the
   same code.** Never quote the first without the second.
4. **The front door was inverted (AUC 0.274) and is repaired** — and the cause was the
   extraction defect the 08-03 master had already named. Same cause, found twice, from
   opposite directions.
5. **Four of the six best families were missing from the framework entirely.**
6. **Convergent validity passed at p=1.7e-41. Discriminant validity failed below chance.**
7. **Two overclaims were caught and published as retractions within one day.** That is the
   instrument doing its stated job to itself.
8. **We ran the repaired lens on our own fourteen documents and it produced 42 false
   positives** — including scoring a maximally honest sentence (−0.630) worse than a
   deliberate overclaim (−0.396), and ranking the anti-overclaim audit document as the
   worst overclaimer in the corpus. **It cannot read stance: negation, attribution and
   confession each defeat it, and all three are one cause.**
9. **The three blocking decisions from 08-03 are all still open**, and the repair is not in
   the app's language.

---

*Compiled 2026-08-07 against `master` at `5330c70`. This document amends the validation
sections of the 2026-08-03 master and changes no other document, no equation, and no file in
`TRUTH_PRESSURE/`. The territory is unchanged by the map. Nothing here has been published
outward, and §XXXV holds.*

*⚠ Amended 2026-08-08: published outward at Mac's instruction; see the note in §6.*
