# LAMAGUE — MASTER SOURCE, 2026-08-07 AMENDMENT

**The short version: the 2026-08-07 work does not upgrade LAMAGUE, and saying otherwise
would be the exact overclaim this corpus exists to catch.**

**Compiled:** 2026-08-07 · **Register:** AMENDMENT, mostly negative.
**Amends:** `LAMAGUE_MASTER_SOURCE_2026-08-03.md`. That document **stands in full.**
Nothing in its 532 lines is retracted, corrected or superseded here.

---

## 1. WHY THIS FILE IS SHORT

Mac asked for a worthy upgrade to **both** LAMAGUE and Truth Pressure. The honest answer is
that only one of them got new evidence.

**MEASURED** — across the fourteen files merged at `5330c70`:

| | references |
|---|---|
| truth pressure | **4 documents, ~3,772 new lines, four external datasets** |
| LAMAGUE | **1 passing reference** |

**DERIVED: there is no new empirical material for LAMAGUE, so there is no worthy empirical
upgrade to write.** Manufacturing a parallel section — inventing a LAMAGUE equivalent of the
external validation so the two documents look symmetrical — would be inventing an
achievement to match a sibling's. **That is the failure mode the whole framework is built to
detect, and it would be dishonest at the exact moment we are congratulating ourselves for
honesty.** The asymmetry is the finding. It is recorded rather than smoothed.

⚠ **This is not a claim that LAMAGUE is stalled.** It is a claim that *this particular
merge* did not touch it. See `LAMAGUE_MASTER_SOURCE_2026-08-03.md` for the live state.

### ⚠ CORRECTION, same day — the paragraph above is true but was INCOMPLETE

The first version of this file stopped at "no new empirical material" and moved on. **That
missed the largest LAMAGUE fact of the day, and it is a good one.**

**MEASURED, reproduced by Sol on this machine, 2026-08-07:**

```bash
cd 03_LAMAGUE_L1/22_REVERSIBLE_COMPRESSION_v1.0
python3 src/benchmark.py               # reproduces
python3 -m unittest discover -s tests  # Ran 19 tests ... OK
```

| metric | README claims | **reproduced** |
|---|---|---|
| held-out reduction, warm dictionary | 33.8% | **0.33777 → 33.8%** ✓ |
| held-out reduction, cold (incl. codebook) | 30.7% | **0.30705 → 30.7%** ✓ |
| dictionary break-even | 3 packets | **3** ✓ |
| test suite | 19 tests pass | **19 tests, OK** ✓ |

⭐⭐⭐ **`22_REVERSIBLE_COMPRESSION_v1.0` LIVES UNDER `03_LAMAGUE_L1/`, AND TODAY'S README
NAMES IT THE STRONGEST TIER 1 ENTRY IN THE ENTIRE REPOSITORY** — *"the only capability in the
repository with a held-out split, a frozen corpus, an exact-reversibility guarantee, and a
reproduced benchmark."*

**So the honest scoreboard inverts.** Truth Pressure got the louder news today — a first
external validation that came back weak. **LAMAGUE quietly holds the one component whose
numbers reproduce exactly, on a held-out split, with a passing test suite, and which does not
route through the broken extraction layer at all.** It operates on structured packets, not
prose, so §5B's stance-blindness cannot touch it.

⚠ **Dated honestly: it is not new.** `git log --diff-filter=A` puts it at **`a38fec6`,
2026-08-03** — four days before this merge. **What 2026-08-07 did was reproduce it and
promote it**, not create it. That is still a real upgrade in standing, and recording it as
one is not inflation: the benchmark was re-run and it held.

**DERIVED, and it is the reason this correction was worth making:** the first version of this
amendment was so careful not to manufacture a LAMAGUE win that it **overlooked a real one
already sitting on disk.** Guarding against overclaim can produce its own error, in the
opposite direction, and it is just as much a false report.

---

## 2. WHAT LAMAGUE DID GET — and it is real

The one genuinely new LAMAGUE fact today came from running the repaired semantic extractor
against our own corpus (`TRUTH_PRESSURE_MASTER_SOURCE_2026-08-07.md` §5B). **LAMAGUE's master
source was one of fourteen documents scanned, and it came back second-worst — 7 flagged
spans, beaten only by the audit document itself.**

**MEASURED — every flagged span in `LAMAGUE_MASTER_SOURCE_2026-08-03.md`:**

| flagged span | cue fired | what the line actually does |
|---|---|---|
| `'no external human or model validation of any kind'` | `fabricated_certainty` | **confesses** the absence of validation |
| `'no test suite and no source at all'` | `fabricated_certainty` | **confesses** missing implementation |
| `'no implementation at all'` | `fabricated_certainty` | **confesses** missing implementation |
| `'production-ready'` (line 49) | `unearned status claim` | *"and it is **not** 'production-ready'"* — a **denial** |
| `'production-ready'` (line 456) | `unearned status claim` | quoting `README.md` **in order to criticise it** |
| `'peer-reviewed'` | `unearned status claim` | appears inside a **prohibition** |
| `'not verify'` | `verification_suppression` | describes something that **cannot** be verified |

⭐⭐⭐ **ALL SEVEN ARE FALSE POSITIVES, AND ALL SEVEN FIRED BECAUSE THE DOCUMENT IS HONEST.**
The LAMAGUE master source's defining quality — that it states its own weaknesses plainly and
quotes its own README's overclaims in order to retract them — is precisely what the
instrument mistook for manipulation. **The most rigorous document in the directory scored as
one of the least.**

This is not a LAMAGUE defect. **It is a measurement of the instrument, taken with LAMAGUE as
the test object**, and it is the clearest single case of the stance-blindness defect recorded
in §5B: negation, attribution and confession all defeat span-matching.

---

## 3. WHAT THIS OBLIGES

1. **Do not "fix" the LAMAGUE master source to make it score better.** Every flagged line is
   correct as written. Softening a confession so an extractor stops flagging it would trade
   real honesty for a green number — the same trade as a gate reading an empty file.
   **The document is right and the tool is wrong.**
2. **`LAMAGUE_MASTER_SOURCE_2026-08-03.md` is now the reference test case** for open question
   12 (*does the extractor need a stance layer?*). A stance layer that cannot clear these
   seven spans has not solved the problem.
3. **The `README.md` overclaim recorded at line 456** — *production-ready*, *formally proven
   to be complete* — is still live and still unretracted. **That is a real LAMAGUE obligation
   and it predates today.** It is named here so it is not lost behind the more interesting
   news that the detector cannot read it correctly either.

---

## 4. STILL TRUE FROM 08-03, UNCHANGED

- **118 is the app's symbol count, not the corpus's.** Still the commonest error made about
  LAMAGUE.
- **The nine-claim canon** in `LAMAGUE_MASTER_SOURCE_2026-08-03.md` is authoritative. Read it
  before any outward statement.
- **0 of 640 sigils could ever verify** — the named-symbols-without-vocabulary finding stands.
- **No external human or model validation of any kind.** ⚠ Unlike Truth Pressure, **this
  sentence is NOT retracted today.** The 2026-08-07 external datasets scored the AURA harm
  lens. **They did not touch LAMAGUE.** Anyone tempted to read the Truth Pressure amendment
  as covering both documents should stop here: **it does not.**

---

*Compiled 2026-08-07 against `master` at `5330c70`. Amends nothing in the 08-03 LAMAGUE
master, retracts nothing, and adds one measured result plus one honest negative. Nothing here
has been published outward; §XXXV THE PROPRIETARY LINE holds and `Lycheetah-Framework`
remains frozen.*

*⚠ Amended 2026-08-08: Mac lifted the freeze and this document was published to
`Lycheetah-Framework` at `606537d`. Sol Prime and `_PROPRIETARY/` remain private and were
verified absent from the public remote after the push. The sentence above is kept as written.*
