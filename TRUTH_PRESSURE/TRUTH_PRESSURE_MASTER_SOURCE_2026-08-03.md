# TRUTH PRESSURE — MASTER SOURCE

**One document. Fifteen minutes. Everything else is downstream of this.**

**Compiled:** 2026-08-03 · **Register:** NAVIGATION + AUDIT. This document creates no
theory and amends nothing. Where it disagrees with a corpus file, it says so and names
the evidence; it does not overwrite the file.
**Owner of the theory:** `TRUTH_PRESSURE_CANON.md` (see §2). **Owner of this map:** this file.

> ⚠ **This corpus is an instrument for detecting overclaim, so this document is held to
> its own standard.** Every consequential line carries a status. **MEASURED** means the
> compiler of this document executed it or read the result file directly, on this machine,
> on 2026-08-03. **CLAIMED** means a corpus file asserts it and it was not independently
> re-run. Nothing here is upgraded by the fact that it is written down.

| status | meaning |
|---|---|
| **MEASURED** | Executed or read from a result file here, 2026-08-03. Reproducible. |
| **DERIVED** | Reasoned from named evidence in this document. |
| **CLAIMED** | A corpus file asserts it. Not independently verified. |
| **UNVERIFIED** | Not checked at the relevant boundary, and the boundary is named. |

---

## 1. WHAT TRUTH PRESSURE IS

Truth Pressure is an instrument for asking how much a piece of writing is actually
carrying. It proposes a single scalar, Π, that expresses the force evidence exerts on a
belief structure relative to that structure's resistance to reorganising — and it uses
that scalar for something specific: **layer membership.** A claim's Π decides whether it
sits in FOUNDATION, THEORY, or EDGE, and a high-Π newcomer can trigger a four-phase
cascade that demotes an incumbent foundation rather than merely resisting it. The
one-sentence novelty claim is that combination — *scalar-computed layer membership plus a
threshold-triggered, ordered demotion protocol* — and not the underlying mathematics,
which belongs to Bayes, Shannon, and Lyapunov and is acknowledged as prior art in
`TRUTH_PRESSURE_CANON.md` §VII.

What it is **not**, stated here so no reader has to infer it: it is not validated. There
is a formal theory, a working scalar, four runnable implementations, and a preregistered
24-case test corpus. There is **no external data, no human rating, and no held-out
validation anywhere in this corpus.** See §7.

---

## 2. THE EQUATION

### The canonical form

```
Π = (E · P) / (S + S₀)

E  := H(X)            total information content of the domain        ∈ [0, 1] normalized
P  := I(X;Y) / H(X)   uncertainty-reduction ratio of the evidence    ∈ [0, 1]
S  := H(X|Y)          residual strain the structure cannot absorb    ∈ (0, 1]
S₀ := strain floor    regularization constant                        > 0
```

**S₀ = 0.05** is the working value everywhere in the corpus and in every implementation.
`TRUTH_PRESSURE_CANON.md` §I labels it explicitly as a **post-hoc fit** — chosen so seven
known error cases re-adjudicate correctly while no correct case flips — and lists
pre-registered S₀ calibration as an open obligation. **Do not report S₀ as calibrated.**

**Why the floor exists:** the unregularized form Π = (E·P)/S diverges as S → 0, so an
already-coherent system would feel unbounded pressure from weak evidence. The floor
saturates Π at E·P/S₀ instead. For S ≫ S₀ the behaviour is unchanged.

### Which file is authoritative for the equation

> ### ⭐ **`TRUTH_PRESSURE_CANON.md` is the authoritative statement of Π. It wins every conflict in this corpus.**

**DERIVED**, from five independent lines of evidence:

1. **It self-declares supersession** — *"CANON — supersedes where it conflicts; defers
   nowhere"* — and it is the only root document that does.
2. **It is post-review.** It incorporates the findings of `FABLE_REVIEW_FINDINGS.md`
   (items W1, W2, W5, W6, M2, M3, M6, P1, P2). The S₀ amendment *is* review finding W5.
3. **Its §II register table is a binding constraint on the whole corpus**: *"Any future
   document that states a claim in a higher register than this table assigns it is in
   error, and this table wins."*
4. **Every later document defers to it in its own header** — MEASURED by reading the
   status blocks of `GRAIN_FORGE_2026-07-03.md`, `GRAIN_EXPANSION_FORGE.md`,
   `RANK_AND_LEMMA_A_2026-07-10.md`, `CASCADE_ORIGIN_FINDING_2026-07-10.md`,
   `GLOSSODYNAMICS_FOUNDING.md`, `THE_GLASS_TRANSITION_CANON.md`,
   `APP_IMPLEMENTATION_STATE_2026-08-01.md`, and `FORGE_2026-08-02_NOTES.md`. Eight for
   eight. Not one claims authority over it.
5. **Every runnable implementation matches it, not its rivals.** MEASURED: the S₀ form is
   what v0.1 (Python), v0.2, v0.3, v0.5–v0.7 (TypeScript) and the live app all compute.

### The four "canons", resolved

Four root documents present as authorities. Only **two** of them ever claim authority over
Π, and one of those explicitly loses. This is the resolution:

| document | what it actually governs | verdict |
|---|---|---|
| **`TRUTH_PRESSURE_CANON.md`** | **Π, its terms, S₀, the register table, the flag** | **AUTHORITATIVE — CURRENT** |
| `TRUTH_PRESSURE_THEORY.md` | the same subject, pre-amendment | **SUPERSEDED on the formula.** Still the best long-form exposition of the three derivations and the cross-domain table. Read it *after* the canon, never instead. |
| `MASTER_EQUATION.md` | `dΨ/dt` — the *dynamics*, not Π | **NOT A RIVAL.** Different equation. Its own header says it *depends on* `PI_DERIVATION.md` and `PI_THRESHOLD_DERIVATION.md`. **CURRENT** for the master equation and the k₁–k₄ calibration spec. |
| `THE_GLASS_TRANSITION_CANON.md` | `θ · τ_reorg > 1` — vitrification in meaning-systems | **NOT A RIVAL.** Different law, different object (vocabularies, memory, belief-as-flow). Self-declared **CANON-CANDIDATE, explicitly not canon**: external review owed, no falsifier run. **CURRENT** for the glass transition. |

**So the four-canon problem is two-thirds a naming collision.** `MASTER_EQUATION` and
`THE_GLASS_TRANSITION_CANON` are canonical for *different questions* and say so. The only
genuine conflict is CANON vs THEORY, and the canon wins on authority, on recency, on
review status, and on implementation agreement.

### ⚠ Where THEORY disagrees, and why it matters more than a formula typo

`TRUTH_PRESSURE_THEORY.md` is superseded on the formula. That much is clean. But two of
its disagreements are load-bearing, because **the numbers it disagrees on are the numbers
that justify the thresholds.** Both are MEASURED here.

**(a) The paradigm table's arithmetic does not close, and its P violates the canon's range.**

`TRUTH_PRESSURE_THEORY.md` §3.2 is the *only* empirical anchor offered anywhere for the
FOUNDATION ≥ 1.5 and THEORY ≥ 1.2 cutoffs. **MEASURED — recomputed 2026-08-03:**

| claim | E | P | S | Π stated | E·P/S computed | P within canon's [0,1]? |
|---|---|---|---|---|---|---|
| Newtonian mechanics | 0.95 | 2.4 | 0.85 | ~1.8 | **2.682** | **no** |
| General relativity | 0.90 | 2.8 | 0.72 | ~2.3 | **3.500** | **no** |
| Quantum mechanics | 0.88 | 2.6 | 0.78 | ~2.0 | **2.933** | **no** |
| String theory | 0.45 | 1.8 | 1.20 | ~0.8 | **0.675** | **no** |
| Loop quantum gravity | 0.40 | 1.9 | 1.15 | ~0.9 | **0.661** | **no** |

Not one row reproduces, the errors are not a constant factor, and every P is 1.8–2.8 when
the canon defines P ∈ [0,1]. Adding S₀ does not rescue it. **DERIVED: the table cannot be
recomputed under the canon's own definitions, so it does not currently support the 1.5 /
1.2 cutoffs it is cited for.** → **Open question 1, §9.**

**(b) The corpus contains three different values for Π_th at n = 50.** **MEASURED:**

| source | Π_th at n=50 | basis |
|---|---|---|
| `TRUTH_PRESSURE_CANON.md` §IV | **≈ 5.7** | k·√n with k ≈ 0.8 (√50 = 7.07) |
| `TRUTH_PRESSURE_THEORY.md` §6.1 | **≈ 1.2** | a table that does not compute k·√n for any k in the stated range |
| `12_IMPLEMENTATIONS/core/cascade_engine.py` | **1.5, fixed** | a literal constant; no n-dependence exists in the code |

THEORY §6.1's three entries (0.8 / 1.2 / 1.5 for n = 5 / 50 / 500) are numerically the
layer cutoffs, not k·√n — which returns 1.79 / 5.66 / 17.89. → **Open question 2, §9.**

---

## 3. THE ONE-SCREEN MAP

**CURRENT** = cite this · **SUPERSEDED** = superseded by a named file, keep for lineage ·
**ARCHIVE** = historical, do not cite as present state · **GENERATED** = mechanically
reproducible, never the truth.

### Root documents

| file | one line | status |
|---|---|---|
| `TRUTH_PRESSURE_MASTER_SOURCE_2026-08-03.md` | **this file** — the map and the audit | **CURRENT** |
| `TRUTH_PRESSURE_CANON.md` | **the theory.** Π with S₀, the register table, the one-sentence flag, standing obligations. Jun 10 2026 | **CURRENT — AUTHORITATIVE** |
| `TRUTH_PRESSURE_THEORY.md` | long-form 10-part exposition; three derivations, cross-domain table, IP | **SUPERSEDED on the formula** by CANON; still current as exposition. ⚠ §3.2 and §6.1 do not compute (§2) |
| `MASTER_EQUATION.md` | `dΨ/dt` physical exposition + the k₁–k₄ calibration spec | **CURRENT** for the dynamics |
| `THE_GLASS_TRANSITION_CANON.md` | `θ·τ_reorg > 1`; one law, three faces (belief / language / memory) | **CURRENT** for the glass transition — self-declared *canon-candidate, not canon* |
| `PI_DERIVATION.md` | Bayesian + information-theoretic derivation, sympy-verified. Mar 21 2026 | **CURRENT** for the derivation; predates S₀ |
| `PI_THRESHOLD_DERIVATION.md` | analytic Π_th = k·√n from random matrix / Hopf / Landau | **CURRENT on paper, CONTESTED** — see `CASCADE_ORIGIN_FINDING` |
| `DIMENSIONAL_ANALYSIS.md` | dimensional consistency across seven domains | **CURRENT** |
| `EMPIRICAL_RESULTS.md` | the 200-trial study: +40.3% coherence, −95.2% forgetting, 847 events | ⚠ **CONTESTED — its cited code and all five data files are absent from disk (§7)** |
| `LQ_PI_ISOMORPHISM.md` | is the app's Light Quotient the same construct as Π? | **CURRENT.** Self-status *"confirmed with scope qualification"* ⚠ conflicts with THEORY §VIII, which still calls it `[CANDIDATE]` |
| `IP_PROVENANCE.md` | authorship record, timeline, what is and is not claimed | **CURRENT** |
| `README.md` | folder front door | ⚠ **STALE** — states the pre-S₀ formula; calls the LQ isomorphism *"confirmed"* |
| `00_INDEX.md` | folder index, updated 2026-08-03 | ⚠ **PARTLY STALE** — body is current and good; its "The Formula" and title block still state `Π = (E·P)/S` |
| `APP_IMPLEMENTATION_STATE_2026-08-01.md` | **⚠ read before comparing any Π across documents.** Three Π's on three scales; the ×20 conversion; eight uncalibrated app constants | **CURRENT — high value** |
| `FORGE_2026-08-02_NOTES.md` | ingestion + verification note for the forge; the constant-Π trap; a fourth Π | **CURRENT** |
| `CASCADE_ORIGIN_FINDING_2026-07-10.md` | **"there is no forcing matrix G."** Retires the spectral threshold apparatus | ⚠ **PROPOSED CANON CORRECTION — UNRATIFIED.** The largest open decision in the corpus |
| `RANK_AND_LEMMA_A_2026-07-10.md` | Part One: Lemma A′ proved. Part Two: the rank-sweep protocol | **Part One CURRENT (proposed); Part Two SUPERSEDED** by `CASCADE_ORIGIN_FINDING` |
| `FABLE_REVIEW_FINDINGS.md` | the independent adversarial review that produced the canon | **ARCHIVE** — historically decisive, superseded by the canon it created |
| `FABLE_REVIEW_PROMPT.md` | the prompt used for that review | **ARCHIVE** |
| `GRAIN_FORGE_2026-07-03.md` · `GRAIN_EXPANSION_FORGE.md` | forge-stage grain expansion; self-labelled *ore, not gold* | **ARCHIVE (forge stage)** |
| `GLOSSODYNAMICS_FOUNDING.md` | founds glossodynamics; six laws G1–G6 | **ARCHIVE (forge stage).** ⚠ G3 withdrawn, G1 retreated — read its own retreat notice first |
| `THE_CRUCIBLE_JULY4.md` | the adversarial review of the July-4 foundings: 4 survive, 6 retreat, 1 dies | **ARCHIVE (review stage)** |
| `ARTICLE_THE_LENS_SCORED_ZERO_2026-08-03.md` | unpublished draft article + social post | **DRAFT — NOT PUBLISHED.** ⚠ needs one scope correction before it goes out (§9, question 4). **Mac fires launches.** |

### Version line — the eight bundles

| version | what it is | still runs? | status |
|---|---|---|---|
| **v0.1** `TRUTH_PRESSURE_v0.1_EVIDENCE_WEIGHTED_REVISION` | first executable spec — **Python**. Evidence-weighted revision, benchmark harness | **MEASURED: 33/33 tests pass** | **SUPERSEDED** by v0.2 (the line moves to TypeScript here) |
| **v0.2** `TRUTH_PRESSURE_ENGINE_v0.2` | first corrected TypeScript engine; own text extractor | **MEASURED: 24/24 checks pass** | **SUPERSEDED** by v0.3 |
| **v0.3** `TRUTH_PRESSURE_ENGINE_v0.3_SEMANTIC_HARDENING` | semantic hardening; strict component separation; `piCanon` + `piNormalized` both exposed | **MEASURED: 24/24 checks pass** | **SUPERSEDED as code** by the v0.5 build — but it is the **last standalone engine bundle** and the one the forge index names as the engine record |
| **v0.4** `TRUTH_PRESSURE_MEASUREMENT_PACK_v0.4` | blinded human-rating protocol: packets, instructions, blinding key, preregistration | not code | **CURRENT — and entirely unused (§7)** |
| **v0.5** `TRUTH_PRESSURE_APP_RC_v0.5` | React-Native-safe app release candidate. **Contains the newest engine source in the corpus** | **MEASURED: 14/14 checks pass** | **CURRENT ENGINE CODE** |
| **v0.6** `..._SOVEREIGN_SOL_SHADOW_BRIDGE_v0.6` | privacy-safe shadow bridge — run the new engine beside the legacy one, store no raw text | **CLAIMED 11/11** (recorded receipt; not re-run here) | **SUPERSEDED** by v0.7, which contains it |
| **v0.7** `..._SHADOW_EVIDENCE_CONSOLE_v0.7` | evidence console, gates, exports, article evidence ledger. Carries the v0.5 engine byte-identically | **CLAIMED 11/11** (recorded receipt; not re-run here) | **CURRENT APP INTEGRATION** |
| **v0.8** `..._LIVE_SOURCE_COLLECTOR_v0.8` | a *tool*, not an engine — collects real app call sites for the final patch | **CLAIMED pass, against a synthetic test repo only** | **CURRENT TOOL — never run against the real repository** |

⭐ **The version-line trap.** `v0.3` sits in `03_ENGINES/` and looks like the current
engine. It is not. **MEASURED:** `TRUTH_PRESSURE_APP_RC_v0.5/src/core.ts` differs from
v0.3's by one line — the instrument tag `TP-CANONICAL-SCALAR-v0.3` → `v0.5` — and
`text-adapter.ts` (the extractor, where the real behaviour lives) differs in content
between v0.3 and v0.5. v0.6 and v0.7 carry the **v0.5** files byte-identically under
`lib/truth-pressure-rc/`. **If you are reading engine code, read v0.5's `src/`.**

### Directories

| path | what | status |
|---|---|---|
| `FORGE_2026-08-02/` | the shipped bundle: 9 zips + index + manifest | **AUTHORITATIVE. MEASURED: `sha256sum -c` → 29 of 29 OK, 2026-08-03.** |
| `FORGE_2026-08-02_EXPANDED/` | 214 files, the nine zips unpacked so they can be read and grepped | **GENERATED — non-authoritative.** The zips are the truth. Never edit; never cite as a separate artifact |

---

## 4. THE AUTHORITY CHAIN — one question, one file

| question | the single file that answers it |
|---|---|
| What is the formula, and what are E, P, S, S₀? | `TRUTH_PRESSURE_CANON.md` §I |
| What register is any given claim allowed to be stated in? | `TRUTH_PRESSURE_CANON.md` §II — *the table wins* |
| Where does the formula come from? | `PI_DERIVATION.md` |
| What are the layer cutoffs? | `TRUTH_PRESSURE_CANON.md` (1.5 / 1.2) — ⚠ their empirical anchor does not compute, §2 |
| What is the reorganisation threshold Π_th? | **CONTESTED. Do not answer from one file.** `PI_THRESHOLD_DERIVATION.md` derives k·√n; `CASCADE_ORIGIN_FINDING_2026-07-10.md` retires it; the engine uses a constant. → §9 |
| What are the dynamics of a system under Π? | `MASTER_EQUATION.md` |
| What does a meaning-system do when fed faster than it reorganises? | `THE_GLASS_TRANSITION_CANON.md` |
| Is the app's LQ the same construct as Π? | `LQ_PI_ISOMORPHISM.md` ⚠ its status disagrees with `TRUTH_PRESSURE_THEORY.md` §VIII |
| What does the **engine** compute? | `FORGE_2026-08-02_EXPANDED/TRUTH_PRESSURE_APP_RC_v0.5/src/core.ts` (via the zip) |
| How is Π extracted from a **text**? | `..._APP_RC_v0.5/src/text-adapter.ts` — `analyzeText()` |
| What does the **live app** run, and on what scale? | `APP_IMPLEMENTATION_STATE_2026-08-01.md` — **read before comparing any two Π's** |
| What is the current app integration? | `..._SHADOW_EVIDENCE_CONSOLE_v0.7/` |
| What has been empirically validated? | **Nothing external.** §7 |
| Who owns this work? | `IP_PROVENANCE.md` |

---

## 5. WHAT IS DEMONSTRATED — receipts produced 2026-08-03

Everything in this section was executed or read on this machine today. Node v24.16.0,
Python 3.12.3. All engine runs were performed on **copies in a scratch directory**, never
in place.

### The bundle is intact
**MEASURED** — `sha256sum -c SHA256_MANIFEST.txt` in `FORGE_2026-08-02/` → **29 of 29 OK.**

### The engines run, and they implement the canonical formula
**MEASURED** — four gates re-executed today:

```
v0.1  (Python)   python3 -m pytest tests/           →  33 passed
v0.2  (TS)       node --experimental-strip-types scripts/verify.ts  →  🟢 24 checks passed
v0.3  (TS)       node --experimental-strip-types scripts/verify.ts  →  🟢 24 checks passed
v0.5  (TS App RC) node --experimental-strip-types scripts/verify.ts →  🟢 14 checks passed
```

The v0.2 and v0.3 gates are both 24 checks but they are **different check lists** — v0.2's
cover extractor behaviour (citation theatre, marker stuffing, jargon), v0.3's cover
semantic hardening (bounded normalization, limiter ties, independence bonuses, judge
contract). The claim *"v0.3 passes 24 hardening checks"* is **verified**.

**MEASURED — the live line in v0.3/v0.5 `core.ts`:**
```ts
const piCanon = (components.evidence * components.explanatoryPower) / (components.strain + config.s0);
const piNormalized = piCanon * config.s0;
```
That is the canon's formula, plus an explicitly-named normalization. The engine publishes
its own scale conversion in its output (`"piNormalized = piCanon × s0 = piCanon × 0.05"`),
which closes the ×20 scale ambiguity inside the engine rather than leaving it to the reader.

### The preregistered corpus is real and adversarial
**MEASURED** — `frozen-corpus-v0.1.jsonl`: **24 cases, 23 distinct families**, each with a
written `expected` and `rationale` fixed before running. The families include seven
deliberate attacks: `citation_theatre`, `marker_stuffing`, `jargon`, `overconfidence`,
`neutral_padding`, `exact_duplication`, `prompt_injection`.

### ⭐ The headline negative result — and its exact scope
**MEASURED** — `TRUTH_PRESSURE_SOURCE_AUDIT_PASS_1_v0.1/TP_UNTUNED_TEXT_RESULTS_v0.1.jsonl`,
read directly, 24 rows:

```
truth_pressure       == 0      24 / 24
invariant_count      == 0      24 / 24
reorganisation_needed== false  24 / 24
```

**The sharper finding is `invariant_count`, not Π.** Π has evidence in the numerator, so
zero invariants forces Π = 0 regardless of what the rest of the formula does. **The
failure is in EXTRACTION, not discrimination** — the extractor found no invariants in
ordinary English prose. Those are different defects with different repairs, and the
distinction is only available because the case-level file recorded `invariant_count`
beside the score.

> ### ⚠⚠ SCOPE, AND IT IS NOT OPTIONAL
> **MEASURED** — `AUDIT_MANIFEST.json` names the code under test: the **legacy app source
> snapshot** (`lib/cascade-score.ts` et al. at commit `d8c8a12`, working tree dirty). The
> Π = 0 in 24/24 result is a fact about **the un-repaired app lens**. It is **not** a fact
> about the engines. See directly below.

### ⭐⭐ Does the *current* engine still score zero? — MEASURED, and the answer is no
No corpus run existed for the newest build, so one was performed. **MEASURED** — the
**v0.5 engine** (the newest engine source in the corpus, the one shipped inside v0.6 and
v0.7) run by this compiler against the same 24 frozen cases:

```
Π == 0 in  14 / 24        (not 24/24)
mean Π = 0.1349     max Π = 1.0749
E == 0 in 10/24      P == 0 in 12/24
```

These reproduce v0.3's recorded corpus results to the digit, so **the v0.5 extractor,
though byte-different from v0.3's, scores this corpus identically.**

The distribution is the interesting part, and it is a genuine discrimination signal:

| behaviour | MEASURED |
|---|---|
| **every adversarial family scores exactly 0** — citation theatre, marker stuffing, jargon, overconfidence, neutral padding, prompt injection, contradiction injection, quotation, negation | ✅ correct |
| **the corpus maximum is `prediction_confirmed` (risky prediction confirmed), Π = 1.075** | ✅ correct — this is the strongest case in the corpus |
| `exact_duplication` scores **identical** to the passage it duplicates (0.3266 both) | ✅ correct by design — v0.3's gate asserts duplication invariance |
| ⚠ **`independent_replication` scores 0** — E = 0.286 but **P collapses to 0** | ❌ **a live defect.** Independent replication is among the strongest evidential moves that exists |
| ⚠ `contradiction_resolution` scores 0 (E = 0), `grand_theory` scores 0 (E = 0) | ❌ extraction still returning nothing on honest prose |
| ⚠ one `paraphrase` scores **0.4671 — 43% higher** than the passage it paraphrases (0.3266) | ⚠ flagged; v0.2's gate only required paraphrases stay in the "same broad region" |

**DERIVED: the extraction defect is materially reduced in the current engine but not
closed.** P is zero in half the corpus. The instrument now separates attacks from honest
writing; it does not yet reliably find evidence in honest writing.

### The v0.2 → v0.3 tightening is real and recorded
**MEASURED** — `V0_3_DEVELOPMENT_SUMMARY.json`: mean Π fell from **0.506 → 0.135** (−73%),
non-zero cases from 14 → 10. v0.3 is substantially more conservative than v0.2.

### The constant-Π trap survives exactly where the notes say
**MEASURED** — see §8.

---

## 6. THE FOURTH Π, AND THE SCALE PROBLEM

**CLAIMED** by `APP_IMPLEMENTATION_STATE_2026-08-01.md` and **CLAIMED** by
`FORGE_2026-08-02_NOTES.md`; not re-measured here because the live app lives outside this
folder. **Four different constructs currently wear the symbol Π:**

| where | formula as coded | range |
|---|---|---|
| canon | `(E·P)/(S+S₀)`, S₀ = 0.05 | 0 → 20 |
| app `lib/cascade-score.ts` | `(E·P·S₀)/(S+S₀)`, S₀ = 0.05 | 0 → 1 — **exactly canon ÷ 20** |
| app `lib/intelligence/cascade-onion.ts` | `(E·P)/(S+5)` on 0–100 layer scores | 0 → 2000 |
| app `computePyramidPi` | E = mean file score, P = max file score, S = score spread | — |

⚠ **Never compare a Π across two of these without converting.** The engine now names its
own conversion in its output; the app does not. `APP_IMPLEMENTATION_STATE` also records
**eight uncalibrated app-invented constants** (saturation k = 4/3/3, tension 0.3,
contested 0.2, falsifiability cap 70, trigger Π > 0.6) that shape every number a user sees
and have never had the scrutiny S₀ has had.

---

## 7. WHAT IS ASSERTED ONLY

> ## 🔴 **THERE IS NO EXTERNAL VALIDATION OF TRUTH PRESSURE. NONE. NOT ONE HUMAN HAS RATED ANYTHING, AND THE ONLY EMPIRICAL STUDY IN THE CORPUS CANNOT BE VERIFIED BECAUSE ITS DATA AND ITS CODE ARE NOT ON DISK.**

That sentence is the honest state of the project as of 2026-08-03. Both halves are MEASURED.

### Half one — the human measurement was designed and never run

**MEASURED**, by parsing `TRUTH_PRESSURE_MEASUREMENT_PACK_v0.4/` today:

- Three rater packets, A / B / C. Each has 24 rows. **Every rating column —
  `E_score_0_4`, `E_confidence_1_3`, `P_score_0_4`, `P_confidence_1_3`, `S_score_0_4`,
  `S_confidence_1_3`, `brief_reason`, `ambiguity_flag_yes_no` — is filled in 0 of 24
  rows, in all three packets.** They are blank materials, not responses.
- `reports/` contains exactly two files. `PRE_REGISTRATION.md` reads
  *"Frozen before human ratings are collected."* `COLLECTION_CHECKLIST.md` has **nine
  boxes and nine of them are unticked.**
- `scripts/analyze_annotations.py` exists and has nothing to analyse.

**DERIVED:** this is a preregistration done properly — frozen before collection, blinding
key sealed, outcomes named in advance. **It is not a result.** Krippendorff's α, rater
agreement and engine-human correspondence are all *planned*; **none is computed.**

### Half two — the 200-trial study cannot be reproduced from this machine

`EMPIRICAL_RESULTS.md` is the source of every empirical number quoted elsewhere in the
corpus: **+40.3% coherence gain (p<0.001, d=2.84), −95.2% catastrophic forgetting, 847
demotion events, annotator κ=0.97, κ=0.82 labelling agreement.** Its §6 lists the
replication materials. **MEASURED — a search of the entire `CODEX_AURA_PRIME` tree:**

| §6 material | present? |
|---|---|
| `cascade_engine.py` | ✅ `12_IMPLEMENTATIONS/core/cascade_engine.py` |
| `50_belief_corpus.json` | ❌ **not found** |
| `annotator_labels.csv` | ❌ **not found** |
| `trial_results_200.csv` | ❌ **not found** |
| `analysis.py` | ❌ **not found** |
| `trial_config.json` | ❌ **not found** |

And the one file that *is* present does not match its own description. **MEASURED:**

- `cascade_engine.py` is **668 lines long.** `EMPIRICAL_RESULTS.md` §6 cites
  `compute_coherence()` at *"line ~847"* and `compute_forgetting()` at *"line ~912"* —
  **both past the end of the file.**
- **Neither function exists.** There is no `compute_coherence` and no `compute_forgetting`
  anywhere in the file.
- §1.1 states φᵢⱼ is computed from **sentence-transformer embeddings**
  (`all-MiniLM-L6-v2`). **There is no sentence-transformer import and no embedding code in
  the engine.** What exists is a `coherence` property at line 154 which
  `CASCADE_ORIGIN_FINDING_2026-07-10.md` independently read as a **count ratio**:
  `1 − (#contradicting pairs)/(n(n−1)/2)`.

> **DERIVED, and this is the single most consequential finding in this audit:**
> `EMPIRICAL_RESULTS.md` describes an implementation that is not present at the paths it
> cites, using a coherence measure the engine does not compute, backed by five data files
> that are not on this machine. **Every number in it is therefore UNVERIFIED at this
> boundary — including the +40.3%, the d=2.84, and the 847 events.** This does not prove
> the study was not run. It proves it cannot currently be checked, and a number that
> cannot be checked must not be quoted as measured. → **Open question 3, §9.**

### The rest of the standing "not yet" list

| claim | status |
|---|---|
| Π implements the canonical formula | **MEASURED** — re-executed here |
| v0.3 passes 24 hardening checks | **MEASURED** — re-executed here |
| The legacy app lens fails general-language validity (Π = 0 in 24/24) | **MEASURED** |
| The current engine discriminates attacks from honest prose | **MEASURED** here — but P = 0 in 12/24 |
| E / P / S mean the same thing to independent humans | **NOT TESTED** — no ratings exist |
| Π tracks anything outside this instrument | **NOT TESTED** — no external data |
| Thresholds (1.5, 1.2, Π > 0.6, k ∈ [0.8,1.5]) are calibrated | **NO** — chosen, not fitted |
| S₀ = 0.05 is calibrated | **NO** — the canon itself labels it a post-hoc fit |
| The 200-trial results | **UNVERIFIED** — see above |
| Held-out validation | **NONE.** The bundle's own index lists it under *"Still required"* |
| The glass transition's three falsifiers | **NOT RUN** — its own canon says so |
| Lemma A | Proved in `RANK_AND_LEMMA_A` Part One; **PROPOSED, not ratified** |
| The v0.8 collector against the real repository | **NEVER RUN** — synthetic test repo only |

⚠ Two framing rules that apply to everything above. **A repository describing its own
success is not independent validation** — and this corpus mostly describes its own
*failures*, which is more credible, but it is still one author measuring one instrument on
a corpus he wrote. And **a passing gate is not a validated construct**: v0.3's 24 checks
are real and they pass, but the fixtures are the instrument's own authored marker
families. Passing them showed the *scalar* was repaired. The 24-case corpus showed the
*construct* was not validated. Both are true at once.

---

## 8. THE KNOWN TRAPS

**Trap 1 — the constant-Π line, and the forty-one lines.** An earlier version had a defect
where Π was effectively a constant: `rawPi = evidencePower / (100 / coherenceDiv)`, with E
and P as raw counts, no S₀, and a `Math.min(1, …)` clamp hiding both faults. Consequence,
as recorded: **Π pinned at 1.000 for any text past ~30 words.** It was found and fixed on
2026-07-28. The dead line is deliberately preserved. **MEASURED — its exact locations:**

```
Line 125, inside a block comment that OPENS at line 117 — prose about a repair:
  FORGE…_EXPANDED/TRUTH_PRESSURE_SOURCE_AUDIT_PASS_1_v0.1/SOURCE_SNAPSHOT/lib/cascade-score.ts
  FORGE…_EXPANDED/TRUTH_PRESSURE_SOVEREIGN_SOL_SHADOW_BRIDGE_v0.6/lib/cascade-score.ts
  FORGE…_EXPANDED/TRUTH_PRESSURE_SHADOW_EVIDENCE_CONSOLE_v0.7/lib/cascade-score.ts

Line 166, in the SAME files — the live code:
  const truthPressure = parseFloat(((E * P * S0) / (S + S0)).toFixed(3));
```

⭐ **Forty-one lines apart, in the same file, and a grep for the formula returns both.**
Line 125 is a citation. Line 166 is the implementation. **Check what the code executes,
not what the file mentions.**

**Trap 2 — the comment 41 lines above the live line states a different formula than the
line computes.** **MEASURED:** the block comment header reads `Π = (E·P)/(S + S₀)`; the
live line computes `(E·P·S₀)/(S+S₀)`. That is deliberate — it is the ÷20 app
normalization documented in `APP_IMPLEMENTATION_STATE` — but **the comment does not say
so.** A reader who trusts the header gets a number 20× off.

**Trap 3 — v0.3 is not the newest engine.** It is the newest bundle *called* an engine.
The newest engine source is in **v0.5**, and v0.6/v0.7 carry it. See §3.

**Trap 4 — "Π = 0 on all 24" is about the legacy lens only.** The repaired engine scores
0 on 14 of 24 with a clean attack/honest separation. Quoting the 24/24 figure without
naming the code under test overstates the failure. See §5.

**Trap 5 — `care-pressure.ts` in the app is not Truth Pressure.** It models
worry/drive/curiosity for the companion. The name collision is real; know it before you grep.

**Trap 6 — the expansion directory is generated.** `FORGE_2026-08-02_EXPANDED/` is 214
files produced by unzipping the nine archives. Editing it edits nothing real, and citing
it as a separate artifact double-counts the work.

---

## 9. OPEN QUESTIONS FOR MAC

These were **not** resolved by the compiler of this document, because each is a decision
about the theory or the launch and belongs to its author.

**1 — The paradigm table does not compute. What replaces the justification for the 1.5 /
1.2 cutoffs?** `TRUTH_PRESSURE_THEORY.md` §3.2 is the only empirical anchor offered for
them, and MEASURED: none of its five rows reproduces from E·P/S, and all five use P
between 1.8 and 2.8 when the canon defines P ∈ [0,1]. Either the table's inputs are on a
different (undocumented) scale, or the cutoffs currently rest on nothing written down.
**Recomputing it under the canon's definitions may move the cutoffs**, which would move
every layer assignment in the corpus and the app.

**2 — Ratify or reject `CASCADE_ORIGIN_FINDING_2026-07-10.md`. This is the largest
unresolved decision in the corpus.** It argues from the engine source that **there is no
forcing matrix G** — no Jacobian, no eigenvalues, no √n anywhere in CASCADE's theory or
code — and therefore that Π_th = k·√n, the Wigner-edge escape, the effective-rank
measurement and the RSS composition rule describe an object the system never builds. It
proposes retiring the spectral apparatus to named CONJECTURE (path A) or building the
missing object (path B). It has sat **PROPOSED and unratified since 2026-07-10**, and
until it is decided, `PI_THRESHOLD_DERIVATION.md` and `TRUTH_PRESSURE_CANON.md` §III–§IV
remain formally current while being contested by a source read. Three different Π_th
values coexist in the corpus meanwhile (§2). **This one blocks the authority chain.**

**3 — Where is the 200-trial data?** Five of the six replication materials named in
`EMPIRICAL_RESULTS.md` §6 are not on this machine, and the sixth does not contain the two
functions cited at the two line numbers given (the file is 668 lines; the citations are
847 and 912). Options: the data exists elsewhere and should be pointed at; it was lost and
the document should be marked UNVERIFIED at its head; or the study was described from a
plan rather than a run. **Until this is answered, +40.3% / d=2.84 / −95.2% / κ=0.97 should
not be quoted outward.** This is the most load-bearing unverified claim in the corpus,
because it is the corpus's only empirical result.

**4 — The draft article needs one scope line before it can go out.**
`ARTICLE_THE_LENS_SCORED_ZERO_2026-08-03.md` is accurate about the legacy lens and honest
about validation. But its headline — *"Zero on every single case"* and *"An instrument
that returns the same number for everything is not measuring anything"* — reads as a
verdict on Truth Pressure, when **MEASURED: the repaired engine scores 0 on 14 of 24, puts
every adversarial family at exactly 0, and puts the confirmed risky prediction at the
corpus maximum.** One sentence naming the code under test fixes it and makes the piece
stronger, not weaker: the instrument's own preregistered test caught its own extractor.
**Mac fires launches — this is flagged, not changed.**

**5 — `LQ_PI_ISOMORPHISM.md` says "confirmed"; `TRUTH_PRESSURE_THEORY.md` §VIII and §X
still say `[CANDIDATE]`, task #18 pending.** `README.md` propagates the stronger word. One
of them is stale. Which?

**6 — `README.md` and `00_INDEX.md` are the folder's front doors and both still state the
pre-S₀ formula** `Π = (E·P)/S`. A first-time reader meets the superseded equation before
they meet the canon. (Not edited here: this audit changes no existing document.)

**7 — The next real step is already named and has never been taken.** The forge's own
index lists it: *run the v0.8 collector against the real Lycheetah repository, then patch
the actual screens.* Everything after that — shadow comparisons, human ratings,
calibration — is blocked behind it. The corpus is eight versions deep and **has not yet
touched the live app.**

---

## 10. REDUNDANCY LEDGER — for the consolidation pass

Mac has said the next move is deleting redundant files. **This document deletes, moves and
renames nothing.** This section is the evidence a safe deletion pass needs. Every line is
MEASURED today. ⚠ Nothing here is a recommendation to delete — it is a statement of what
is provably reproducible from something else.

**Fully regenerable — reproducible byte-for-byte from an artifact that is verified intact:**

- **`FORGE_2026-08-02_EXPANDED/` — 214 files, 1,441,338 bytes.** Produced by unzipping the
  nine archives in `FORGE_2026-08-02/`, whose manifest **verifies 29/29 today**. Zip entry
  counts (26+18+20+36+20+41+40+29+6 = 236) cover the expansion. **If it is removed it can
  be recreated with one `unzip` per archive — but it is also the only greppable form of
  the sources, which is exactly why it was created.** Removing it trades 1.4 MB for the
  ability to search the code.

**Byte-identical duplicates *within* the expansion — MEASURED by md5 across all 214 files:**

- **173 unique contents across 214 files. 24 duplicate-sets. 251,457 redundant bytes
  (246 KB).** These are not accidents: v0.5/v0.6/v0.7 legitimately vendor the same engine
  source, and the frozen corpus legitimately appears in v0.2, v0.3 and the measurement
  pack. **They are duplicates of the packaging, not of the work.** Deleting inside the
  expansion breaks the correspondence with the zips and gains nothing the zips do not
  already give.

**Root ↔ bundle duplication — MEASURED, md5 identical:**

- `TRUTH_PRESSURE_CANON.md` ≡ `FORGE_2026-08-02/00_FOUNDATION/TRUTH_PRESSURE_CANON.md`
  (`2f2f1edc…`)
- `TRUTH_PRESSURE_THEORY.md` ≡ `FORGE_2026-08-02/00_FOUNDATION/TRUTH_PRESSURE_THEORY.md`
  (`423a8c76…`)

⚠ **Do not delete the bundle copies.** They are inside the SHA-256 manifest; removing them
breaks the 29/29 verification that is currently this corpus's strongest integrity receipt.
**The root copies are the ones to cite.**

**LAMAGUE ↔ Truth Pressure overlap.** ⚠ **`03_LAMAGUE_L1/` is another agent's working
tree and is out of scope for this audit — nothing in it was read or touched.** Inside
`TRUTH_PRESSURE/`, the files that mention LAMAGUE are: `GLOSSODYNAMICS_FOUNDING.md`,
`THE_CRUCIBLE_JULY4.md`, `THE_GLASS_TRANSITION_CANON.md`, `GRAIN_FORGE_2026-07-03.md`,
`IP_PROVENANCE.md`, `00_INDEX.md`, `FORGE_2026-08-02_NOTES.md`, and inside the v0.1 bundle
`docs/LAMAGUE_RELATIONSHIP.md` + `lamague_adapter/TRUTH_PRESSURE_ADAPTER_v0.1.md`. **DERIVED:
none of these is a duplicate of a LAMAGUE file — they are Truth Pressure documents that
*cite* LAMAGUE as the laboratory organism for the glossodynamics arc.** The glass
transition's Face-2 falsifier is defined on LAMAGUE and is one of the corpus's two
runnable-and-never-run experiments. **Deleting the TP-side LAMAGUE references would remove
a live obligation, not a redundancy.** If duplicated LAMAGUE material exists, it is in
`03_LAMAGUE_L1/`, and that judgement belongs to the agent working there.

**Genuinely superseded, kept for lineage (delete only with intent — each records a
position that was overturned, which is the causal history this corpus runs on):**
`FABLE_REVIEW_PROMPT.md` and `FABLE_REVIEW_FINDINGS.md` (superseded by the canon they
produced), `GRAIN_EXPANSION_FORGE.md` and `GRAIN_FORGE_2026-07-03.md` (forge-stage ore),
`RANK_AND_LEMMA_A` Part Two (superseded by `CASCADE_ORIGIN_FINDING`), engine bundles v0.1,
v0.2, v0.3 and v0.6 (superseded as code by v0.5 / v0.7).

---

## 11. IF YOU READ ONLY THIS

1. **The formula is `Π = (E·P)/(S + S₀)`, S₀ = 0.05, and `TRUTH_PRESSURE_CANON.md` owns
   it.** Anything stating `(E·P)/S` — including the README and the index header — is
   pre-amendment.
2. **The current engine code is in `TRUTH_PRESSURE_APP_RC_v0.5/src/`.** v0.7 is the current
   app integration and carries it. v0.3 looks current and is not.
3. **The engines genuinely compute Π.** MEASURED: four gates re-run today, all green.
4. **The instrument's own preregistered test caught its own extractor.** The legacy lens
   scored Π = 0 on all 24 with `invariant_count` = 0 on all 24 — an extraction failure,
   not a discrimination failure. The repaired engine scores 0 on 14 of 24 and separates
   attacks cleanly, but P still collapses to zero on half the corpus, including
   independent replication.
5. **Nothing here has been validated against the world.** No human has rated anything, and
   the one empirical study in the corpus cannot be reproduced from this machine.
6. **Two decisions are blocking: ratify or reject the no-G finding, and account for the
   200-trial data.** Until then the threshold has three values and the empirical headline
   has no receipt.
7. **The corpus is eight versions deep and has never been run against the live app.**

---

*Compiled 2026-08-03 against the corpus as it stood on disk that day. Every MEASURED line
is reproducible with the commands named beside it. This document is a map. The territory —
`TRUTH_PRESSURE_CANON.md`, the engines, and the frozen corpus — is unchanged by it.*
