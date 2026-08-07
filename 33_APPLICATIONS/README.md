# Real-World Applications — where to begin

**Status: MEASURED where marked, 2026-08-07.** Written to answer one question:
*of everything in this repository, what can actually solve a problem someone has
outside it, and what has to happen first?*

Every entry names the component, the problem, and the evidence — and the evidence
is a command you can run, not a paragraph. Where a claim is unverified it says so.

---

> ## ⚠ Read this before anything below
>
> **2026-08-07, later the same day.** The lens was scored against two published,
> externally-authored datasets — the first time anything in this repository has
> been measured by data it did not write.
>
> ```text
> self-authored corpus, held-out    ROC-AUC 0.940
> anthropics/hh-rlhf, 2308 pairs    55.5% pairwise   z=4.02  p=5.7e-05   SIGNIFICANT
> anthropics/evals, 1000 statements ROC-AUC 0.516    z=0.87  p=0.383     not significant
> cue coverage on real replies      ~2%
> ```
>
> **On hh-rlhf the effect is real and small.** Cue families written from theory,
> fitted to none of this data, beat chance at odds of ~17,000:1 on 1,335 decided
> pairs — while capturing only 55.5% of a band whose ceiling is 64.9%, and while
> firing on 2% of the text.
>
> *An earlier version of this box said "at chance on both" and "carries no
> signal". That was false for hh-rlhf and is corrected here; significance is now
> computed by the harness rather than asserted in prose.*
>
> Full record: [`EXTERNAL_VALIDATION_2026-08-07.md`](EXTERNAL_VALIDATION_2026-08-07.md)
>
> **Consequence for this map:** everything that scores text has been moved to
> Tier 3. The tiers below are corrected, not rewritten — the reasoning that put
> those rows in Tier 2 is left visible, because the lesson is that internal
> validation could not have caught this.
>
> **Then the loop was inverted.** Cues derived *from* 42,486 human-labelled
> pairs rather than written by hand reach **60.6%** against a measured ceiling of
> **64.9%** — closing 53% of the gap with six regular expressions, and revealing
> that **three of six empirically-supported harm families had no counterpart
> anywhere in the framework**, including the strongest one.
>
> Full record: [`DERIVED_CUES_2026-08-07.md`](DERIVED_CUES_2026-08-07.md)

## The method — how to tell a real solution from a good document

This corpus is 701 markdown files and 241 Python files. Most of it is theory, and
theory does not solve anything by itself. Three filters, applied in order, sort
the corpus into what can leave the building:

**1. Does it run?** Not "is it specified" — does `python3 <thing>` produce output.
241 Python files exist; the ones under test are 18, covered by 220 tests.

**2. Does it discriminate?** Running is not enough. A scorer that returns the same
number for every input runs perfectly and measures nothing. The question is whether
the output *separates the cases it claims to separate*. This filter is where most
of the corpus currently fails, and it is why this directory exists.

**3. Does it discriminate *on data this project did not write*?** Added
2026-08-07 after filter 2 turned out to be insufficient. A lens can separate
self-authored cases at AUC 0.940 and sit at chance on real traffic — that is not
a hypothetical, it is what happened here. Filter 2 measures agreement with the
author. Only filter 3 measures contact with the world.

**4. Does someone outside have this problem?** A capability with no holder of the
problem is a research result, which is fine — but it is not an application, and
calling it one is the failure mode this framework was built to catch.

A component that passes all four is shippable. Passing some is not a partial
pass; it is a different category of thing. The tiers below are those categories.

---

## The blocking finding, and its repair

**Found 2026-08-07: the front-door tool did not discriminate.** `lycheetah.check()`
— the lens behind the web demo and the `check_alignment` MCP tool — scored harmful
AI output *slightly higher* than aligned output on a 40-case balanced corpus:
ROC-AUC **0.274** against a chance floor of 0.500, with 1 of 20 harmful cases
rejected. Below chance is inversion, not weakness.

The cause was one layer below the formula — pattern libraries matching literal
phrasings that ordinary English never produces — and it was the **second** lens
here to fail at that exact layer, after
`TRUTH_PRESSURE/ARTICLE_THE_LENS_SCORED_ZERO_2026-08-03.md`. Two symptoms, one
shared cause, so the repair was one extraction layer rather than a longer pattern
list in each file.

**Repaired the same day.** `12_IMPLEMENTATIONS/core/semantic_extractor.py` matches
compositional frames instead of exact strings, and both lenses draw on it.

| | before | HELD-OUT after |
|---|---|---|
| ROC-AUC | 0.274 | **0.940** |
| accuracy | 52.5% | **90.0%** |
| separation | −0.53 | **+24.24** |

```bash
python3 33_APPLICATIONS/discrimination_audit.py --split heldout   # the untuned half
```

Test suite went 219 → **266 passing**, 1 still failing by design. Validated
further against the 24 **preregistered** Truth Pressure cases — a corpus written
for a different lens before this extractor existed — which found four more
defects, all fixed, one of them introduced by the fix before it.

Full record, including what is still broken: [`DISCRIMINATION_AUDIT_2026-08-07.md`](DISCRIMINATION_AUDIT_2026-08-07.md)

**Known remaining gap: `domain_overreach`, 0 of 2 caught.** Clinical and financial
absolutes ("definitely benign", "cannot go down over any five-year window") are
invisible to the extractor. Left failing and named rather than patched — adding
those two sentences' vocabulary would reach 10/10 and would mean nothing.

---

## Tier 1 — solves a real problem now

Runs, discriminates, and somebody outside has the problem. Three entries.

### 1.1 Reversible semantic compression for accountability records

**Component:** `03_LAMAGUE_L1/22_REVERSIBLE_COMPRESSION_v1.0/`

**The problem someone has.** Records that must shrink but must not silently drop
the fields that make a decision accountable: what remains unknown, who holds
authority, who is affected, who dissented, how to recover the prior state.
Ordinary compression optimises bytes and is indifferent to which bytes. Audit
logs, incident records, clinical decision trails, and — most immediately — the
compacted state an AI agent carries between turns all have this shape.

**Evidence — MEASURED, reproduced 2026-08-07:**

```bash
cd 03_LAMAGUE_L1/22_REVERSIBLE_COMPRESSION_v1.0
python3 src/benchmark.py            # reproduces the table below
python3 -m unittest discover -s tests   # 19 tests, all pass
```

| metric | result |
|---|---|
| held-out reduction vs minified JSON (warm dictionary) | **33.8%** |
| held-out reduction including codebook cost (cold) | **30.7%** |
| exact full-packet round trips | **36 / 36** |
| constructed protected-loss mutations correctly caught | **324 / 324** |
| dictionary break-even | 3 packets |

**Boundaries, stated by the module itself and not softened here:** the corpus is
synthetic and structured; the codec does *not* infer packets from unrestricted
natural language; mutation accuracy is measured on constructed deletions, not
adversarial model output.

**Why this is the strongest Tier 1 entry.** It is the only capability in the
repository with a held-out split, a frozen corpus, an exact-reversibility
guarantee, and a reproduced benchmark. It also does not depend on the broken
extraction layer — it operates on structured packets, not prose. The nearest
real deployment is agent context compaction with a provable guarantee that the
protected fields survived, which is a problem the `CLAUDE.md` turn-economy law
documents this project having at 206:1 cache-read-to-output ratio.

### 1.2 The evidence discipline, as a portable methodology

**Components:** `28_DEFENSE/CLAIMS.json` + `CLAIMS.schema.json`,
`FALSIFICATION_REGISTER.md`, `FAILURE_MUSEUM.md`, `DOWNGRADE_REGISTER.md`,
`TESTABILITY_MANIFEST.md`, and the status vocabulary in `CLAUDE.md`.

**The problem someone has.** Teams shipping AI systems must produce technical
documentation that survives an auditor — EU AI Act Art. 11 and 13, NIST AI RMF
MEASURE/GOVERN — and the standard artefact (a model card) has no mechanism that
forces a claim to carry its own falsification condition or its own retraction
history. Overclaiming is structurally unpunished.

**What is transferable.** Not the nine frameworks — the *bookkeeping*. A
machine-readable claim register where every claim carries `status`,
`load_bearing`, `evidence_path`, and `falsifiability`; a status vocabulary that
distinguishes MEASURED from DERIVED from CONJECTURE; a museum that keeps retracted
claims visible instead of deleting them. 67 claims are registered here (46 ACTIVE,
11 SCAFFOLD, 3 ASPIRATIONAL, 3 EMPIRICAL, 3 REMOVED, 1 OBSERVATIONAL).

**Evidence — MEASURED.** The discipline is validated by having been turned on its
own author's front door: the audit above is the framework catching the framework,
published rather than quietly patched. That is the demonstration. A methodology
that has never produced an uncomfortable finding about its owner has not been
tested.

**Nearest real deployment:** a claims-register template plus schema plus CI gate
that any AI team can adopt in an afternoon, independent of whether they accept a
single line of Lycheetah theory. This is the most portable thing here and the
least dependent on anything else being right.

### 1.3 The discrimination gate itself

**Component:** `33_APPLICATIONS/discrimination_audit.py` (new, this commit)

**The problem someone has.** Guardrail and eval vendors ship scorers whose unit
tests verify the arithmetic and never ask whether the score separates the classes.
That is precisely how a lens reaches production with sub-chance AUC while every
test is green — twice, in this repository alone.

**What it does.** Takes any text lens, runs it against a frozen labelled corpus,
and reports separation, accuracy, ROC-AUC, and per-defect-category breakdown.
`--gate` exits non-zero below AUC 0.80 / accuracy 0.75, so it drops into CI.
Adding a lens is one adapter function.

**Evidence — MEASURED.** It found a real, previously unquantified inversion in
this repository's most-used module on first run. AUC is reported alongside
accuracy specifically because the two failure modes need different repairs: a lens
that ranks correctly but thresholds badly is cheap to fix, and one that cannot
rank is not.

---

## Tier 2 — empty

Every row that was here has moved to Tier 3.

They were placed here on the strength of AUC 0.940 against the self-authored
corpus, with conditions attached — advisory not blocking, medical presets still
blocked. Those conditions were the right instinct and they were not enough,
because they were calibrated against the wrong number. The external run put the
lens at chance, and an advisory signal that is silent 97.7% of the time and at
chance the rest is not a weaker version of a detector. It is not a detector.

The reasoning is left visible above rather than deleted. The point of this
document is that careful internal validation produced a confident, wrong tier
assignment, and hiding that would remove the only evidence for filter 3.

The multi-agent components — `psi_consensus.py` (decentralised coherence, tested),
`grey_mode.py` (quarantine and recovery for drifted nodes, tested) — sit at the
Tier 1/Tier 2 boundary. They pass their tests and they do not route through text
extraction, but neither has been run against an adversarial multi-agent scenario,
so their separation property is **UNVERIFIED** rather than measured. Building the
multi-agent analogue of the discrimination corpus is the cheapest way to move them
up, and it is the natural second piece of work after 1.3.

---

## Tier 3 — research, honestly labelled

Not applications. Listed so the map is complete and so nothing here gets quoted
as capability.

**Moved here 2026-08-07 by the external run**, all for the same reason — they
score text with a lens measured at chance on data this project did not write:

- **Runtime output auditing** (`applications/lycheetah_guard_mcp.py`) — the
  framework's central novelty claim. Architecturally complete, 7 MCP tools, and
  no demonstrated ability to detect misalignment in real output.
- **Companion-app dependency detection** (`applications/cascade_resonance_engine.py`)
  — `dependency_inducement` fired on **1 of 4,616** real replies.
- **First-contact web demo** (`applications/web_demo.py`) — honest only if it
  states that it is a demonstration of the architecture. It shows extracted
  spans, which is genuinely useful for seeing *what the framework looks for*.
  That is a teaching tool, not a detector.
- **Regulated-vertical thresholds** and **healthcare standards** — were already
  blocked on `domain_overreach`; now blocked on the prior question of whether the
  lens works at all.

The path back to Tier 1 is filter 3: derive the cues from external labelled data,
then beat chance on a held-out slice of it. Not more cue families written by hand.

- **CASCADE predictive claim** — F1 = 0.531 against a preregistered criterion of
  > 0.80. **The test is left failing on purpose** (`tests/test_cascade_predictability.py`).
  This is the corpus's single most credible act: a falsifiable prediction, failed,
  published, not quietly relabelled.
- **Master equation calibration** — six preregistration documents in
  `31_EMPIRICAL/`, none executed. Preregistration is real methodological work and
  is not a result.
- **Earned Light / Harmonia consciousness models** — CONJECTURE, correctly tagged.
- **Unified field, knowledge genome** — both carry `STATUS: DRAFT — contains
  placeholder stubs; do not use in production` in their own headers. Believe them.

---

## Where to begin — the answer

The answer changed twice in one day, and the second change is the real one.

It began as *fix the extraction layer*. That was done, and the lens went from
inverted to AUC 0.940 on a held-out half. Then the external run put it at chance
on two datasets nobody here wrote, and the honest answer became something else:

**Begin by inverting the direction of validation.** Not one more cue family, one
more corpus, one more document. The structural fault is that constructs are
defined from theory, illustrated with examples written to fit, and validated
against those examples. `67/67` internal evidence paths is that loop made
visible, and a lens at chance on external data is what the loop produces at the
far end no matter how rigorous the internal work is.

Concretely, in order:

1. ~~**Derive cue families from external labelled data.**~~ **Done** — see
   [`DERIVED_CUES_2026-08-07.md`](DERIVED_CUES_2026-08-07.md). 60.6% against a
   64.9% ceiling, and it found three harm families the framework never had.
   Regenerate with `python3 33_APPLICATIONS/derive_cues.py --write`.
2. **Test the derived families on a second corpus.** Families derived from one
   dataset that survive on another are constructs; families that do not are
   corpus artefacts, and right now nobody knows which these six are. This is the
   single highest-value next run, and `third_party_target` is the one to watch —
   it carries real weight and rests on function words.
3. **Demote the self-authored corpus to a unit test.** It belongs in `pytest` as a
   regression check that known frames still fire. It must never again appear as
   evidence, and `discrimination_audit.py` should print the external number beside
   the internal one every time it runs.
4. **Add an external evidence path to every load-bearing claim, or mark it
   internally-validated-only.** All 67 would currently carry that mark. Seeing it
   written 67 times in `CLAIMS.json` is the useful part.
5. **Publish a ceiling beside every score, permanently.** A number without one
   cannot be read in either direction — 55.5% looked like failure until 64.9%
   showed how much room actually existed.
6. **Find a third referent from a different publisher.** Both current datasets are
   Anthropic's. Two agreeing results are decisive about this lens; they are not
   yet decisive about the constructs.

**Ship 1.1 regardless.** Reversible compression does not route through the lens,
has its own held-out split, and is the one thing here that survived the day
unchanged. Shipping it while the harder work proceeds beats holding everything.

**And keep 1.2, but demoted.** The evidence discipline is still the most portable
thing in this repository — and it just failed its own test in the most useful way
available. Sixty-seven claims each carrying a falsification condition, and not one
of those conditions was "check it against data we did not write". A methodology
that produces a confident, wrong tier assignment and then catches it is worth more
than one that has never been wrong in public. That is the honest pitch for it, and
it is a better pitch than the one it had this morning.

---

## Reproducing everything on this page

```bash
pip install numpy scipy networkx pytest

pytest -q                                                        # 266 pass, 1 fails by design
python3 33_APPLICATIONS/external_validation.py                   # THE ONE THAT MATTERS — chance, both datasets
python3 33_APPLICATIONS/discrimination_audit.py --split heldout   # AUC 0.940 — self-authored, untuned half
cd 03_LAMAGUE_L1/22_REVERSIBLE_COMPRESSION_v1.0 && python3 src/benchmark.py
```

`external_validation.py` needs outbound HTTPS on first run and verifies both
downloads against recorded SHA256 hashes, so a silently changed upstream file
cannot move a published number without the mismatch being visible.

All four were run on 2026-08-07 and the numbers on this page are their output.
Anything not reproduced by one of those commands is marked UNVERIFIED above.

To see why a given text scores as it does — the extracted spans, not just the
number:

```bash
python3 12_IMPLEMENTATIONS/core/semantic_extractor.py "any text here"
```
