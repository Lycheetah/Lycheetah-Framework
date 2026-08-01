# Π — WHAT THE APP ACTUALLY IMPLEMENTS

**Status:** MEASURED, 2026-08-01. Every number below was read from running code in
`~/0sol-by-lycheetah`, not from prose about it.
**Written because:** Mac, 2026-08-01 — *"our truth pressure engine has evolved
inside the app more than it has in our codex."* That is correct, and this
document is the reconciliation.
**Register:** this is an IMPLEMENTATION REPORT. It does not amend the canon.
Where the app diverges from `TRUTH_PRESSURE_CANON.md`, the canon is the theory
and the app is a fact about a program.

---

## ⚠⚠ READ THIS FIRST — THERE ARE THREE Π's AND THEY ARE ON THREE SCALES

This is the single most important thing to hold while studying Π in Codex. All
three call themselves Π. All three implement `(E·P)/(S + S₀)`. **None of them
produces the same number for the same belief.**

| where | E, P, S range | formula as coded | Π range |
|---|---|---|---|
| **canon** `TRUTH_PRESSURE_CANON.md` | `[0,1]` | `(E·P)/(S+S₀)`, S₀ = 0.05 | **0 → 20** |
| **app** `lib/cascade-score.ts` | `[0,1]` densities | `(E·P·S₀)/(S+S₀)`, S₀ = 0.05 | **0 → 1** |
| **app** `lib/intelligence/cascade-onion.ts` | `[0,100]` layer scores | `(E·P)/(S+S₀)`, S₀ = 5 | **0 → 2000** |

**MEASURED, exactly:**

```
E=1  P=1  S=0.001   canon 19.608    cascade-score 0.980    ratio 20.0x
E=1  P=1  S=0.05    canon 10.000    cascade-score 0.500    ratio 20.0x
E=0.8 P=0.6 S=0.2   canon  1.920    cascade-score 0.096    ratio 20.0x
E=0.5 P=0.5 S=0.5   canon  0.455    cascade-score 0.023    ratio 20.0x

onion, all nine layers at 50  → Π 31
onion, all nine layers at 100 → Π 182
onion, coherence 100 / no tension → Π 2000
```

`cascade-score` multiplies the canonical formula through by S₀. **It is exactly
`canon Π ÷ 20`** — a pure, order-preserving rescaling chosen so the result lands
in 0–1 with no clamping. That is a defensible engineering choice and it is
**nowhere documented in the codex**.

### What this means for the threshold work

`PI_THRESHOLD_DERIVATION.md` derives `Π_th = k·√n` with `k ∈ [0.8, 1.5]`
**MEASURED**. That k is on the **canon scale**.

- The app's `cascade-score` reorganisation trigger is `truthPressure > 0.6`.
  On the canon scale that is **Π > 12**.
- `library.tsx` teaches cascade regimes at `Π > 0.7` and `Π > 0.5` — canon-scale
  **14** and **10**.

⚠ **Do not compare an app Π to a canon Π_th without converting.** They are the
same quantity in different units, and the factor is 20.

**This is not a defect to fix by fiat.** Rescaling to 0–1 is right for a UI;
canon scale is right for the theory. What was missing is the conversion being
written down anywhere. It is written down now.

---

## I. WHAT THE APP HAS THAT THE CODEX DOES NOT

The codex holds ~4,800 lines of theory across 20 documents — derivation,
dimensional analysis, threshold spectral argument, empirical results, the
glass-transition canon. **That is not what the app added.**

The app added **operationalisation**: the step from a formula over abstract
E, P, S to something that runs on a real text or a real knowledge block. Every
item below exists only in the app.

### 1. E, P and S as marker DENSITIES

The canon defines `E := H(X)`, `P := I(X;Y)/H(X)`, `S := H(X|Y)` — information-
theoretic quantities. Nothing in the codex says how to obtain them from a piece
of writing.

`cascade-score.ts` operationalises them as **regex marker densities per 100
words**, then squashes each through a saturation function:

```ts
per100 = (hits) => (hits / words) * 100
sat    = (d, k) => d / (d + k)

E = sat(per100(theoryHits),      4)   // evidence density
P = sat(per100(invariantHits),   3)   // explanatory power
S = sat(per100(incoherenceHits*2 + edgeHits), 3)   // entropy / strain
```

⚠ **The saturation constants k = 4, 3, 3 are UNDOCUMENTED AND UNCALIBRATED.**
They are not the canon's k₁–k₄ from the E-1.0 programme. They are app-side
choices that shape every Π the app reports, and they owe the same calibration
S₀ owes.

**Why densities:** so document length cancels. See §II.

### 2. A five-layer text lens — AXIOM · FOUNDATION · THEORY · EDGE · CHAOS

`cascade-score.ts` classifies text into five layers. **`AXIOM` and `CHAOS` appear
nowhere in the codex** — the canon's pyramid is Foundation → Theory → Edge.

It also derives two structural flags the codex does not define:

- **`paradoxical`** — `AXIOM > 50 AND CHAOS > 50`. Recorded in-code as
  *"Π diverges mathematically"*.
- **`structuralContradiction`** — `FOUNDATION > 50 AND EDGE > 50`: a claim both
  load-bearing and contested.

### 3. A nine-layer knowledge-block engine

`lib/intelligence/cascade-onion.ts` (351 lines) scores blocks across nine layers:

```
AXIOM · FOUNDATION · STRUCTURE · COHERENCE · RESONANCE
TENSION · CONTESTED · SPECULATIVE · FRONTIER
```

Its Π mapping is its own:

```
E = (FOUNDATION + STRUCTURE) / 2
P = AXIOM
net coherence = COHERENCE − TENSION×0.3 − CONTESTED×0.2
S = 100 − net coherence          (strain is the ABSENCE of net coherence)
Π = (E·P) / (S + 5)
```

It adds two governance rules with no codex counterpart:

- **Falsifiability gate** — `AXIOM` marked unfalsifiable caps the block at **70**.
- **Layer dependencies** — `FOUNDATION ≤ AXIOM×1.1`, `STRUCTURE ≤ FOUNDATION×1.2`.
  A structure cannot be better supported than what it rests on.

---

## II. TWO DEFECTS THE IMPLEMENTATION FOUND IN ITSELF

Both were measured and repaired on **2026-07-28**. Both are empirical findings
about instantiating Π that the theory could not have produced on paper, and
**neither is recorded in the codex.**

### DEFECT 1 — Π was a constant. The instrument had the fallacy it was built to attack.

The original `cascade-score.ts` line:

```ts
evidencePower = (theoryHits + 1) * (invariantHits + 1)
rawPi         = evidencePower / (100 / coherenceDiv)
truthPressure = Math.min(1, rawPi)
```

Three compounding faults:

1. **E and P were RAW COUNTS**, so they grew with document length. A product of
   two counts grows **quadratically** — Π measured how MUCH was written, not how
   well it was supported. *That is the "more words = more true" fallacy, running
   inside the instrument built to attack it.*
2. **There was no S₀.** The denominator was the constant `100`.
3. `Math.min(1, …)` **hid both faults behind a hard clamp.**

**MEASURED CONSEQUENCE: Π pinned at 1.000 for any text past ~30 words** —
including text with coherence 0, i.e. maximum self-contradiction. Every entry in
the Library read Π 1.00. The headline number of the feature was a constant.

⭐ **The lesson, and it is a Π-shaped lesson:** the comment above that code
recited the correct formula. *A comment reciting a formula is not an
implementation of it.*

### DEFECT 2 — S was inverted, in the one direction the framework depends on.

`cascade-onion.ts` computed:

```ts
S = coherence − tension×0.3 − contested×0.2     // then divided by S
```

So **S rose with COHERENCE**, and a more coherent block scored *lower* truth
pressure.

**MEASURED before the fix: coherence 20 → Π 280 · coherence 90 → Π 62.**

The canon is the exact opposite, and says why:

> A belief resting on chaotic foundations (high S) cannot be moved much by any
> single finding — too many degrees of freedom to be pinned.

That is the framework's whole counter-intuitive claim: **a coherent structure is
the one a decisive piece of evidence can actually move**, which is why coherent
systems are the ones that cascade. Inverted, the app taught the reverse of the
theory it was built from — to every seeker who opened that screen.

The repair keeps the author's composite as a good **net coherence** and defines
`S` as its absence, which is what strain means.

---

## III. WHERE THE APP INHERITS, AND WHERE IT INVENTS

| quantity | app value | provenance |
|---|---|---|
| `S₀` (0–1 scale) | **0.05** | **INHERITED** from canon §I. Carried with the canon's own "post-hoc fit, calibration pending" label intact. |
| `STRAIN_FLOOR` (0–100 scale) | **5** | **DERIVED** — 0.05 rescaled ×100. Same status. |
| `k` for E | **4** | ⚠ **APP-INVENTED. Uncalibrated.** |
| `k` for P | **3** | ⚠ **APP-INVENTED. Uncalibrated.** |
| `k` for S | **3** | ⚠ **APP-INVENTED. Uncalibrated.** |
| tension weight | **0.3** | ⚠ **APP-INVENTED.** |
| contested weight | **0.2** | ⚠ **APP-INVENTED.** |
| falsifiability cap | **70** | ⚠ **APP-INVENTED.** |
| reorganisation trigger | **Π > 0.6** (canon-scale 12) | ⚠ **APP-INVENTED.** |

⚠ **Eight uncalibrated constants shape every Π the app displays.** The canon is
scrupulous that S₀ is a post-hoc fit awaiting pre-registered calibration. These
eight have not even had that scrutiny. They are not wrong — they are **unexamined**,
and they are load-bearing for every number a seeker reads.

---

## IV. THE HONEST SUMMARY

**The codex has the theory. The app has the only working instantiation — and the
instantiation found two real defects that the theory, on paper, could not have.**

That is what Mac meant, and it is true in a precise sense worth stating: an
implementation is an experiment the theory runs against reality. Both defects
were the implementation disagreeing with the theory, and **both times the theory
was right and the code was wrong.** That is the good direction for a framework
to fail in.

**What the codex should absorb from this document:**

1. **The three scales, and the ×20 conversion.** Nothing else here matters as
   much. A Π compared across scales is a wrong number quietly.
2. **The density operationalisation** — the first concrete answer to "how do you
   get E, P and S out of a text at all".
3. **The two defects**, as empirical results about instantiating Π.
4. **The eight uncalibrated constants**, as an open calibration debt beside S₀.

**What this document does NOT claim:**

- Not that the app's operationalisation is *correct*. Regex marker density is a
  proxy for evidence, and a crude one. It is a first instantiation, not a
  measurement of truth.
- Not that any threshold has been validated. `Π > 0.6` is a chosen number.
- Not that the five- or nine-layer structures are derived. They are authored.
- Nothing here upgrades `TRUTH_PRESSURE_CANON.md`'s own register table.

---

## V. FILE MAP — where to read the running code

```
~/0sol-by-lycheetah/
  lib/cascade-score.ts               258  5-layer text lens · Π ∈ [0,1] · densities
  lib/intelligence/cascade-onion.ts  351  9-layer block engine · Π ∈ [0,2000]
  lib/intelligence/cascade-judge.ts  253  auto-scores the 9 layers
  lib/intelligence/cascade-reorganise.ts   the Π > τ trigger
  lib/talk/truth-lens.ts              62  conversational truth categories
  lib/mystery-school/truth-covenant.ts 43 the School's epistemic contract
  lib/care/care-pressure.ts           95  a SEPARATE pressure — not Π
  scripts/verify-truth-pressure.ts        the gate over cascade-score
```

⚠ `care-pressure.ts` is **not** Truth Pressure. It models worry/drive/curiosity
for the companion. The name collision is real and worth knowing before grepping.
