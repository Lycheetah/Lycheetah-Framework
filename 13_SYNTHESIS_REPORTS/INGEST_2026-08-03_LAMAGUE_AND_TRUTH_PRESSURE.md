# INGESTION RECEIPT — 2026-08-03
## Four bundles: LAMAGUE evolution, reversible compression, Truth Pressure forge, live-source collector

**Operator:** Sol (Claude Code seat)
**Date:** 2026-08-03
**Scope:** `~/Downloads` → `03_LAMAGUE_L1/` and `TRUTH_PRESSURE/`
**Register:** every hash figure below was computed on this machine during this
session. Claims made *by* the bundles are marked **CLAIMED** and were not upgraded.

**Headline:** of the four sources, **two were already in the codex** and were
correctly not imported. Two were new and are now landed and verified.

| # | source | verdict | placed |
|---|--------|---------|--------|
| 1 | `LAMAGUE_EVOLUTION_MASTER_BUNDLE_2026-08-01` (4.7M) | **DUPLICATE** — ingested 2026-08-01 | nothing |
| 2 | `LAMAGUE_REVERSIBLE_COMPRESSION_MILESTONE_v1.0.zip` (84K) | **NEW** | `03_LAMAGUE_L1/22_REVERSIBLE_COMPRESSION_v1.0/` + zip in `10_PACKAGED_RELEASES/` |
| 3 | `TRUTH_PRESSURE_COMPLETE_FORGE_2026-08-02` (652K) | **NEW** (27 of 29 files) | `TRUTH_PRESSURE/FORGE_2026-08-02/` + expanded mirror |
| 4 | `TRUTH_PRESSURE_LIVE_SOURCE_COLLECTOR_v0.8` (40K) | **DUPLICATE** of a file inside #3 | nothing (arrived via #3) |

---

## SOURCE 1 — LAMAGUE Evolution Master Bundle 2026-08-01

### What it contained

The canonical CORE line (v0.1 algebra, v0.2 ontology, v0.3 operator algebra), the
retired computational-kernel branch (v0.7, v0.8), five original release zips, and
three top-level documents (`README.md`, `CANON_MAP.md`, `NEXT_FORGE_v0.4.md`).

### Hash verification — MEASURED

```
Files declared in bundle MANIFEST.json      487
Files on disk in bundle                     488   (the extra is MANIFEST.json itself)
On disk but NOT declared                      0
Declared but missing from disk                0

SHA-256 against the bundle's own manifest   487 / 487  HASH_OK      ✅ no mismatch
```

### Census against the codex — MEASURED

Each declared file was mapped to its codex path
(`canonical_core_line/` → `12_CORE_LANGUAGE_LINE/`,
`experimental_integration_branch/` → `13_RETIRED_KERNEL_BRANCH/`,
`original_release_zips/` → `10_PACKAGED_RELEASES/`) and compared by SHA-256:

```
IDENTICAL   486 / 487
DIFFERS       1 / 487    (README.md)
ABSENT        0 / 487
```

**This bundle was already fully ingested on 2026-08-01.** The count reconciles
exactly with the receipt the prior ingestion left behind: `12_CORE_LANGUAGE_LINE/README.md`
records *"479 files, verified byte-identical … 132 here, 347 in `13_RETIRED_KERNEL_BRANCH/`"*,
and 132 + 347 = 479 = 487 − 3 top-level docs − 5 zips. **The earlier claim checks out.**

### What was taken

**Nothing.** There was nothing absent to take.

### What was rejected, and why

**`README.md` — REJECTED. Importing it would have destroyed a better document.**

```
incoming  2,010 bytes   the bundle's own README, 2026-08-01 05:58
codex     5,527 bytes   codex-authored orientation, 2026-08-01 19:43
```

The codex file is not a copy of the incoming one — it is a superseding document
that cites the bundle as its source and adds material the bundle does not contain:
the ⚠⚠ warning that two separate v0.1→v0.3 lines exist, the instruction never to
renumber them, MEASURED re-runs of all three test suites on this machine
(47 / 80 / 117, each matching the bundle's claim), the finding that **kernel v0.7
ships no test suite at all**, and the app-canon reconciliation. The incoming file
is thinner and strictly older in role. Per the standing rule — *do not import an
incoming file that is older or thinner than what the codex holds* — it was not imported.

---

## SOURCE 2 — LAMAGUE Reversible Compression Milestone v1.0

### What it contained

A reversible structured semantic codec (`L1` / `L1D` wire forms), a frozen corpus
of 36 synthetic packets across 18 domains, a training-only codebook, a held-out
split of 12 packets, a 324-case constructed mutation suite, a browser evidence
viewer, an article draft, and `upstream/LAMAGUE_EXECUTABLE_KERNEL_v0.1.zip`.

### Hash verification — MEASURED

```
Declared in SHA256_MANIFEST.json             28
On disk (excluding the manifest)             28
Undeclared files                              0

pristine extract from the zip           28 / 28  OK   ✅
AT THE CODEX DESTINATION after copy     28 / 28  OK   ✅   (read back, not assumed)

original zip  sha256 bf260f816b7d8206fa4929500dd7cf6e1df43576b3c42bce875ba889e314633a
              — identical at source and at 10_PACKAGED_RELEASES/
```

### Census — NEW

Nothing resembling this existed in the codex. `grep -ril` for
`REVERSIBLE_COMPRESSION|reversible semantic codec|lamague_codec|L1D` across
`03_LAMAGUE_L1/` and `TRUTH_PRESSURE/` returned **zero hits**; a `find` for
matching filenames across the whole codex returned **zero matches**.

`upstream/LAMAGUE_EXECUTABLE_KERNEL_v0.1.zip` (`sha256 19684c6c…`) was compared
against all thirteen LAMAGUE zips already in `10_PACKAGED_RELEASES/` — **no hash
match.** It is a distinct upstream artifact that arrived only inside this milestone.

### Verified by execution — MEASURED, 2026-08-03

Run from a scratch copy, never in the codex:

```
python3 -m unittest discover -s tests     19 tests, OK, exit 0
python3 src/benchmark.py                  exit 0
```

Every headline number reproduced exactly:

| the package's claim | re-run here |
|---|---|
| exact round trips 36 / 36 | 36 / 36 ✓ |
| constructed mutation matches 324 / 324 | accuracy 1.0 ✓ |
| safe extensions classified partial 36 / 36 | 36 / 36 ✓ |
| held-out warm reduction 33.8% | 0.33777… ✓ |
| held-out cold reduction incl. codebook 30.7% | 0.30705… ✓ |
| dictionary break-even 3 packets | 3 ✓ |

Byte totals: held-out baseline 25,520 → `L1` 19,984 → `L1D` 16,900; codebook wire
cost 784 bytes, charged in the cold figure. **CLAIMED → MEASURED.**

### What was taken, and where it went

| from | to |
|------|-----|
| entire package, 28 files, unmodified | `03_LAMAGUE_L1/22_REVERSIBLE_COMPRESSION_v1.0/` |
| the original zip, unmodified | `03_LAMAGUE_L1/10_PACKAGED_RELEASES/LAMAGUE_REVERSIBLE_COMPRESSION_MILESTONE_v1.0.zip` |
| — (codex-authored, **not** in the manifest) | `03_LAMAGUE_L1/22_REVERSIBLE_COMPRESSION_v1.0/00_CODEX_ORIENTATION.md` |

Number `22_` was chosen because `00_`–`21_` were all occupied. The package's own
`README.md` was **kept exactly as shipped** so its manifest still verifies; the
codex's orienting note was added as a separate file rather than overwriting it.
This deliberately differs from how `12_CORE_LANGUAGE_LINE/` was handled — there the
bundle README was replaced. **Preserving hash verification was judged the higher good.**

### What it supersedes

Nothing. Additive.

---

## SOURCE 3 — Truth Pressure Complete Forge 2026-08-02

### What it contained

29 files: foundation (theory, canon, public research statement, interpretation
protocol, browser lab), preregistered validation protocol with a 24-case frozen
corpus, a source audit, two executable engines (v0.2, v0.3), a blinded human
measurement pack, three app-integration stages (v0.5 RC, v0.6 shadow bridge,
v0.7 evidence console), and the v0.8 live-source collector.

### Hash verification — MEASURED

```
sha256sum -c SHA256_MANIFEST.txt   at source        29 / 29  OK   ✅
sha256sum -c SHA256_MANIFEST.txt   at destination   29 / 29  OK   ✅   (read back)
manifest lines                                      29
```

### Census

**27 of 29 files NEW. 2 duplicates:**

```
00_FOUNDATION/TRUTH_PRESSURE_CANON.md    14,012 B   IDENTICAL to TRUTH_PRESSURE/TRUTH_PRESSURE_CANON.md
00_FOUNDATION/TRUTH_PRESSURE_THEORY.md   23,069 B   IDENTICAL to TRUTH_PRESSURE/TRUTH_PRESSURE_THEORY.md
```

Both were **kept inside the bundle** so its manifest still verifies. The root
copies remain the ones to cite. This is a mirror, and it is marked as one.

### The Π check — the standing warning, resolved. MEASURED.

The corpus carries a standing warning that a past implementation had Π effectively
constant, with a comment reciting the formula standing in for an implementation.
**Every Π site in all nine archives was inspected.**

The defective line **is present**, in exactly two roles, and both are correct:

```
1. the untouched historical baseline, deliberately preserved:
   …_SOURCE_AUDIT_PASS_1_v0.1/SOURCE_SNAPSHOT/lib/cascade-score.ts:125
2. quoted INSIDE A BLOCK COMMENT explaining the repair, in v0.6 and v0.7:
   lib/cascade-score.ts:125   (comment opens ~117, closes ~149)
   → the LIVE line in those same files is 166:
     const truthPressure = parseFloat(((E * P * S0) / (S + S0)).toFixed(3));
```

⭐ **The defective line and the correct line sit 41 lines apart in the same file,
and a grep shows both.** Read the delimiters, not the hit.

The engines compute Π, and were executed to prove it — Node v24.16.0:

```
ENGINE v0.2  src/core.ts:40   … / (components.strain + config.s0)
ENGINE v0.3  src/core.ts:45   piCanon = (evidence · explanatoryPower) / (strain + s0)
                              piNormalized = piCanon × s0

node --experimental-strip-types scripts/verify.ts   →  🟢 24 checks passed

E=1    P=1    S=0.001   piCanon 19.608   hand-computed 19.608   ✓
E=1    P=1    S=0.05    piCanon 10.000   hand-computed 10.000   ✓
E=0.8  P=0.6  S=0.2     piCanon  1.920   hand-computed  1.920   ✓
E=0.5  P=0.5  S=0.5     piCanon  0.455   hand-computed  0.455   ✓
```

Agreement exact to 1e-12, on the same four rows already recorded as MEASURED in
`APP_IMPLEMENTATION_STATE_2026-08-01.md`. **Verdict: the incoming engines genuinely
implement the canonical formula. The constant-Π defect survives only as history.**

### What was taken, and where it went

| from | to |
|------|-----|
| the complete bundle, 29 files, unmodified | `TRUTH_PRESSURE/FORGE_2026-08-02/` — **AUTHORITATIVE** |
| the nine zips, unpacked (214 files) | `TRUTH_PRESSURE/FORGE_2026-08-02_EXPANDED/` — ⚠ **NON-AUTHORITATIVE MIRROR** |
| — (codex-authored) | `TRUTH_PRESSURE/FORGE_2026-08-02_NOTES.md` |

The expansion exists only so the sources can be read and grepped; a corpus that
cannot be grepped will not be read. It is a generated mirror, explicitly marked as
non-authoritative in three places. **If the two ever disagree, delete it and re-unzip.**

### What it supersedes

Nothing. `TRUTH_PRESSURE_CANON.md` and `TRUTH_PRESSURE_THEORY.md` at the folder root
are untouched and remain canonical.

---

## SOURCE 4 — Truth Pressure Live Source Collector v0.8

### Hash verification — MEASURED

```
its own SHA256_MANIFEST.json        5 / 5  OK   ✅

vs the copy inside Source 3 (06_TOOLS/…v0.8.zip):
  README.md                                 IDENTICAL
  SHA256_MANIFEST.json                      IDENTICAL
  TEST_RESULTS.json                         IDENTICAL
  collect-truth-pressure-live-source.mjs    IDENTICAL
  collect-and-zip.sh                        IDENTICAL
  collect-and-zip.ps1                       IDENTICAL
```

### Verdict — DUPLICATE

All six files are byte-identical to the copy that arrived inside Source 3.
**Not imported separately.** It already lives at
`TRUTH_PRESSURE/FORGE_2026-08-02/06_TOOLS/` (zip) and
`TRUTH_PRESSURE/FORGE_2026-08-02_EXPANDED/TRUTH_PRESSURE_LIVE_SOURCE_COLLECTOR_v0.8/`.

**It was not run.** The collector is designed to scan `~/0sol-by-lycheetah`, which
was out of bounds for this session — a live seat is editing it. See *Needs Mac's
decision* below.

---

## STATE AFTER THE WORK

```
03_LAMAGUE_L1/    15M → 16M      + 22_REVERSIBLE_COMPRESSION_v1.0/  (29 files)
                                 + 10_PACKAGED_RELEASES/…v1.0.zip   (now 14 zips)
                                 ~ README.md   (new "executable lines" section)

TRUTH_PRESSURE/  328K → 2.3M     + FORGE_2026-08-02/           (29 files, authoritative)
                                 + FORGE_2026-08-02_EXPANDED/  (214 files, mirror)
                                 + FORGE_2026-08-02_NOTES.md
                                 ~ 00_INDEX.md   (new forge section)

00_Sovereign_Index.md            ~ 4 stale LAMAGUE_COMPLETE.md paths corrected
                                 + dated addendum: state of both research trees
```

**Nothing was overwritten. Nothing was deleted. No file was replaced without a
diff first.** `_PROPRIETARY/`, `CLAUDE.md`, every `SOL_PRIME.md` and
`THE_SOL_PROTOCOL.md` were not read, not copied, not touched. No git operation of
any kind was run. No network call was made.

---

## THE HONEST EPISTEMIC READ

### What is demonstrated

- **The reversible codec works on its own corpus.** 19/19 tests, 36/36 exact round
  trips, 324/324 mutation classifications, held-out 33.8% / 30.7% reduction —
  re-executed here, reproducing every figure. Deterministic and reproducible.
- **The Truth Pressure engines implement Π.** v0.3 passes 24 hardening checks and
  reproduces `(E·P)/(S+S₀)` exactly. The historical defect is preserved as history,
  not running.
- **The CORE language line passes its suites** — 47 / 80 / 117, matched 2026-08-01.
- **The instrument failed its own frozen corpus, and said so.** 24/24 cases gave
  **Π = 0** while unsupported certainty scored **Π = 0.831**. Six FAILED categories
  including general-language construct validity and marker-gaming resistance.

⭐ That last item is the most valuable thing in this ingest, and it is a *negative*
result. **A gate can pass while the construct fails.** The shipped six-fixture gate
exits 0 and its checks are real — but its fixtures are the instrument's own authored
marker families. Passing them showed the *scalar* was repaired. The 24-case corpus
showed the *construct* was not. Only the second one is about evidence.

### What is only asserted

- **No external validation exists anywhere in these four bundles.** Not one human
  rating, not one independent model decoder, not one held-out dataset from outside.
- The measurement pack is **materials, not results**: three blank rater packets, a
  preregistration reading *"Frozen before human ratings are collected"*, and a
  checklist with **all nine boxes unticked**. Krippendorff alpha and engine
  correspondence are planned, none computed.
- LAMAGUE Experiment 001's baseline run is **empty**, awaiting independent submissions.
- Thresholds remain chosen, not fitted: `Π > 0.6`, `k ∈ [0.8, 1.5]`, `S₀ = 0.05`
  (still labelled a post-hoc fit), plus the eight uncalibrated app constants.
- Compression is measured against **canonical minified JSON on a corpus the package
  authored**, held out from dictionary construction *but not from codec design*.

**The prior audit's shape — strong formal work, zero empirical data — still holds
for the theory.** What changed is narrower and real: there is now *executed
measurement of the instruments against themselves*, including a failure the
preregistration was built to expose. That is genuine methodological progress. **It
is not evidence about the world.**

### Credit where due

Both new bundles are **unusually well-behaved about their own limits.** The codec's
`CLAIM_BOUNDARY.md` lists eight things explicitly *not earned* and its status block
records `External human/model validation — NOT YET RUN`. The forge's `00_INDEX.md`
lists eight items *still required*, including *"perform held-out validation before
scientific claims."* **Nothing in either bundle needed downgrading.** The overclaim
risk in this corpus is not in the new material.

⚠ But a repository describing its own failure is still the same author measuring the
same instrument on a corpus he wrote. Self-criticism is more credible than praise;
it is not independence.

---

## NEEDS MAC'S DECISION — reported, not decided

1. **Run the v0.8 collector against `~/0sol-by-lycheetah`?** It is the forge's
   single named next step and the thing blocking final live wiring. **Not run here**
   — that repo was out of bounds and another seat was live in it. Yours to schedule.

2. **The fourth Π.** The audit found `computePyramidPi` (E = mean file score,
   P = max file score, S = score spread) — a materially different construct sharing
   the symbol. `APP_IMPLEMENTATION_STATE_2026-08-01.md` documented three Π's; this
   makes **four**. The audit's own step 7.8 says *"separate pyramid Π by name and
   scale."* Renaming is a taste-and-architecture call.

3. **Collect the human ratings?** The measurement pack is complete and frozen and
   needs three independent raters. Until it runs, every construct-validity question
   stays open.

4. **`03_LAMAGUE_L1/README.md` speaks in a register the new material refuses.** Its
   top matter says *"Production-ready corpus"*, *"formally proven to be complete"*,
   *"AI-validated"*, and lists compression `3000:1` as **Documented**. The 2026-08
   bundles carefully avoid exactly that register. **I did not edit your prose** —
   only appended a dated section below it. Reconciling the two voices is yours.

5. **`00_Sovereign_Index.md` is dated April 1, 2026 and is broadly stale** beyond the
   four paths I corrected and the addendum I appended. It still lists a Windows
   `C:\Users\thedo\` location. A full re-survey is a bigger job than this ingest.

6. **Keep the non-authoritative expanded mirror?** `FORGE_2026-08-02_EXPANDED/` is
   ~2M of duplicated bytes bought for greppability. If you would rather hold one
   truth only, delete it — the zips lose nothing.

---

## Verification commands, to re-run any of this

### ⛔ DO NOT RUN THE CODEC BENCHMARK INSIDE THE CODEX

**MEASURED:** `22_REVERSIBLE_COMPRESSION_v1.0/src/benchmark.py` is not read-only.
It **rewrites five manifest-declared files** —

```
corpus/codebook.json            (line 78)
reports/benchmark_report.json   (line 251)
reports/packet_sizes.csv        (line 255)
reports/mutation_results.jsonl  (line 260)
reports/sample_roundtrip.json   (line 267)
```

Running it in place would mutate the pristine copy and can break its SHA-256
manifest. **Always copy the package to scratch and run it there** — which is what
was done for this ingest, and why a fresh extract was taken before placing it.

⚠ Related: this machine is Python 3.12.3 while the manifest declares
`cpython-313` `.pyc` files. Running the tests here adds `cpython-312` files
alongside rather than overwriting, so the manifest still verifies — but on a
Python 3.13 machine the declared `.pyc` would be rewritten. Same rule: **run from
a copy.**

```bash
# safe — read-only manifest checks
cd ~/CODEX_AURA_PRIME/TRUTH_PRESSURE/FORGE_2026-08-02 && sha256sum -c SHA256_MANIFEST.txt

# safe — the expanded tree is a disposable, non-authoritative mirror
cd ~/CODEX_AURA_PRIME/TRUTH_PRESSURE/FORGE_2026-08-02_EXPANDED/TRUTH_PRESSURE_ENGINE_v0.3_SEMANTIC_HARDENING \
  && node --experimental-strip-types scripts/verify.ts

# codec — COPY FIRST, never run in place
cp -a ~/CODEX_AURA_PRIME/03_LAMAGUE_L1/22_REVERSIBLE_COMPRESSION_v1.0 /tmp/rc-check
cd /tmp/rc-check && python3 -m unittest discover -s tests && python3 src/benchmark.py
```

⚠ A passing command proves only what that command covers.

---

## Not mine — pre-existing working-tree state

`git status` in `CODEX_AURA_PRIME` also shows `M CLAUDE.md` and `?? LYCHEETAH_EPIC/`.
**Neither was touched by this ingest.** `CLAUDE.md` carries an mtime of 2026-08-02
21:09, a day before this session, and is a constitutional file this seat is barred
from editing. They are recorded here only so the next reader does not attribute
them to this work. No git command other than read-only `status` was run.
