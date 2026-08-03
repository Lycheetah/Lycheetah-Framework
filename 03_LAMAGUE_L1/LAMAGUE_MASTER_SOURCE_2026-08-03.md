# LAMAGUE — MASTER SOURCE

**The one document to read first. Written 2026-08-03.**
Corpus: `/home/guestpc/CODEX_AURA_PRIME/03_LAMAGUE_L1/` — 842 files, 16 MB, 134 markdown, 149 Python.
Author of the corpus: Mackenzie Conor James Clark. Author of this map: Sol ⊚.

---

## HOW TO READ THIS FILE

This is a **map, not a merge**. Nothing was deleted, moved, renamed, or edited to
produce it. Every other file remains exactly where it was.

It exists because **nine separate files in this corpus each claim to be the
complete, master, or canonical one**, and a person arriving cold cannot tell which
wins. Section 7 resolves that. Section 4 tells you which single file answers any
given question.

Every consequential statement carries a status:

| tag | means |
|---|---|
| **MEASURED** | I ran it or read the bytes directly on 2026-08-03 |
| **DERIVED** | reasoned from named evidence, shown inline |
| **CLAIMED** | a document in this corpus asserts it and I did not verify it |
| **UNVERIFIED** | not checked at the boundary that would settle it |

⚠ **This document was NOT written by summarising the existing documents.** Where a
document's own prose disagrees with what the files do, the files win and the
disagreement is named. Section 6 lists what this corpus asserts without data.

---

## 1. WHAT LAMAGUE IS

LAMAGUE is a symbolic notation for writing down states, transformations,
invariants and compression levels in a compact, typed, machine-parseable form —
built by one person, in the open, over roughly ten months. In this corpus it
exists in three unrelated concrete forms: a **formal core language** with a
grammar, a type lattice and machine-readable operator contracts; an **experiment
harness** that tests whether a meaning survives being handed between different AI
systems; and a **wire codec** that encodes structured semantic packets compactly
and reversibly. Around those sit a large body of earlier design prose, a 36-glyph
visual alphabet, eight speculative domain extensions, and a retired research
branch. **DERIVED** from the file census and the executed suites below.

What it is **not**, on this corpus's own evidence: it is not validated science, it
is not peer-reviewed, it has no external human or model validation of any kind,
and it is not "production-ready". Section 6 details this. The strongest honest
summary is: **substantial, internally coherent formal engineering with two small
pieces of real reproducible data and no independent replication.**

---

## 2. THE ONE-SCREEN MAP

Status vocabulary: **CURRENT** = the live thing to use or continue ·
**SUPERSEDED** = a later file answers the same question better ·
**ARCHIVE** = preserved history, do not continue it ·
**GENERATED** = mechanically produced from other files, never edit by hand.

### Directories

| entry | files | what it is | status |
|---|---:|---|---|
| `02_NATIVE36/` | 19 | 36-glyph visual alphabet + machine registries (v0.1→v0.3), SVG/PNG sheets, interactive HTML, validator | **CURRENT** for the visual alphabet only |
| `03_LAMAGUE_1C/` | 4 | "one-cell" seal language spec + interactive page | **CURRENT**, self-contained, narrow |
| `04_FRONTIER_CANON/` | 1 | Frontier Canon Addendum I (71 KB) — forward-looking architecture essay, LAMAGUE Ω, "five bodies" | **CURRENT** as vision; **not** a spec |
| `05_RUNTIME_v0.1/` | 4 | ⚠ **report + 2 JSON examples only — the code is NOT here** | **ARCHIVE** (see §5.4) |
| `06_RUNTIME_v0.2_SEMANTIC_CONTINUITY/` | 32 | runtime: identity hashes, breathing compression, dissent path, migration outcomes | **SUPERSEDED** by `07_` |
| `07_RUNTIME_v0.3_CROSS_INTELLIGENCE_EQUIVALENCE/` | 55 | runtime: blind-decoder packets, equivalence classification, consensus clustering | **CURRENT** head of the RUNTIME line |
| `08_EXPERIMENT_001_CROSS_INTELLIGENCE/` | 149 | preregistered blind-decoder trial + **the controlled pilot that produced the only cross-model data in the corpus** | **CURRENT** — and richer than the root README says |
| `09_ARTICLE_AND_VISUAL_ASSETS/` | 7 | banner + copies of the Native36 / 1C art | **GENERATED** (6 of 7 are byte-identical duplicates) |
| `10_PACKAGED_RELEASES/` | 14 | 14 release zips, unmodified | **ARCHIVE** — but see §5.4, two of them are the *only* copy of their code |
| `11_HISTORICAL_INDEXES_AND_PROVENANCE/` | 4 | provenance decision + root manifest + file index | **ARCHIVE**; 2 of 4 duplicate top-level files |
| `12_CORE_LANGUAGE_LINE/` | 147 | **the language itself** — CORE v0.1 algebra, v0.2 ontology, v0.3 operator contracts | **CURRENT — this is the authoritative line** |
| `13_RETIRED_KERNEL_BRANCH/` | 347 | Computational Kernel v0.7 + v0.8, temporal-evidence structures | **ARCHIVE** — explicitly retired, preserved on purpose |
| `22_REVERSIBLE_COMPRESSION_v1.0/` | 30 | reversible packet codec + held-out compression benchmark | **CURRENT**, newest artifact (2026-08-03) |

### Top-level files

| entry | date | what it is | status |
|---|---|---|---|
| `README.md` | Aug 3 | reading guide; **top half is 2026-March marketing prose, bottom half is accurate 2026-August measurement** | ⚠ **MIXED** — see §7.1 |
| `README_MASTER_CODEX.md` | Aug 1 | archive-level map + the two-lines warning | **CURRENT** but its directory map is wrong (§7.2) |
| `LAMAGUE_MASTER_SOURCE_2026-08-03.md` | Aug 3 | **this file** | **CURRENT** |
| `CHANGELOG_2026-07-31.md` | Jul 31 | what the Codex Drop added | **ARCHIVE**, accurate for its date |
| `MASTER_MANIFEST.sha256.json` | Jul 31 | 229-file hash manifest of the Codex Drop | **GENERATED** — ⚠ 23 entries do not resolve (§7.3) |
| `DEDUPLICATION_AUDIT.json` | Jul 31 | 47 identical-content groups | **GENERATED** — same path defect |
| `LAMAGUE_FIRST_CORPUS_MASTER_SOURCE_2026-07-15.md` | Jul 15 | 243 KB verbatim concatenation of 17 root `.md` files, each with SHA-256 | **GENERATED CONTAINER** — supersedes nothing (§7.4) |
| `LAMAGUE_ROOT_PROVENANCE_AND_CANON_DECISION_2026-07-15.md` | Jul 15 | lineage reconstruction + canon decisions **C-01…C-07** | **CURRENT** for provenance & naming law |
| `AURA_CODEX_INGESTION_LEDGER_BATCH_01_2026-07-15.md` | Jul 15 | ingestion record, contradiction ledger, claim registers | **CURRENT** for "what was known to conflict, as of July" |
| `LAMAGUE_ROOT_SHA256_MANIFEST_2026-07-15.txt` | Jul 15 | hashes of the 17 root files | **GENERATED** |
| `00_LAMAGUE_COMPLETE_EXTRACTION.md` | Jun 12 | biggest root prose doc: 8 symbol classes, 8-D vectors, translations | **ARCHIVE** (design prose, §7.5) |
| `01_LAMAGUE_COMPLETE.md` | Mar 21 | "Complete Specification" — grammar, type system, Python | **ARCHIVE** — self-labelled *"90% READY"* |
| `02_README_LAMAGUE.md` | Jun 12 | "The Canonical Language Specification" — three-tier stack | **ARCHIVE** |
| `03_LAMAGUE_OPERATING_GUIDE.md` | Jun 12 | how to compress a thought, speak it, sign it | **ARCHIVE**, still the friendliest on-ramp |
| `04_BNF_GRAMMAR.md` | Apr 29 | four-class BNF grammar | **SUPERSEDED** by CORE v0.3 EBNF — ⚠ **and it contradicts it** (§7.6) |
| `05_NOTATION_GUIDE.md` | Apr 29 | four-tier notation stack | **ARCHIVE** |
| `06_LAMAGUE_RAW_MATH.md` | Jun 12 | every formula extracted | **ARCHIVE** |
| `07_GEOMATRIA_COMPLETE_SPECIFICATION.md` | Mar 25 | GEOMATRIA — seven geometries | **ARCHIVE** (separate layer, canon C-03) |
| `08_LAMAGUE_WHAKAPAPA_ENCODING.md` | Mar 24 | AI-governance application, four obligation layers | **ARCHIVE** |
| `09_TRI_LINGUISTIC_DEEP_DIVE.md` | Mar 25 | AI-written synthesis essay | **ARCHIVE** — ⚠ synthetic commentary, not evidence |
| `10_essentials.md` | Apr 28 | one-page cheat sheet | **ARCHIVE** |
| `14_`…`21_` (8 files) | Jun 12 | EX NIHILO · COSMOS · QUANTUM · CONTINUUM · CHORA · THANATOS · PAIS · SOMA | **ARCHIVE / SPECULATIVE** — none implemented (§6) |
| `📘 PART X — LAMAGUE.docx` | Jul 31 | the primary formal root, as Word | **ARCHIVE** — the historical origin document |

---

## 3. THE SINGLE MOST IMPORTANT THING IN THIS CORPUS

**There are THREE independently numbered lines, and their version numbers have
nothing to do with each other.** "LAMAGUE v0.3" is a sentence with no meaning
until you say which line.

| line | what it is | operators | where | head |
|---|---|---|---|---|
| **CORE** | the **language** — algebra, ontology, operator contracts | 6 symbolic: `⊗ → ⇌ ⟲ ↯ ↗` | `12_CORE_LANGUAGE_LINE/` | **v0.3**, next is v0.4 |
| **RUNTIME** | the **experiment harness** — does meaning survive crossing intelligences? | — | `05_` `06_` `07_` | **v0.3** |
| **PACKET** | the **wire codec** — consequential semantic packets | 9 letter: `O E U I G V F Y Z` | `22_REVERSIBLE_COMPRESSION_v1.0/` | **v1.0** |

**MEASURED:** the CORE and PACKET operator alphabets are **disjoint — not one
symbol in common**. Read directly from
`12_CORE_LANGUAGE_LINE/LAMAGUE_CORE_OPERATOR_ALGEBRA_v0.3/schema/lamague_operator_contracts_v0.3.json`
(6 operators) and `22_REVERSIBLE_COMPRESSION_v1.0/docs/SOURCE_LINEAGE.md` (9 letters).

Separately, `13_RETIRED_KERNEL_BRANCH/` holds a **fourth** numbering — Computational
Kernel v0.7 and v0.8 — which is retired and continues nothing.

⚠ **Never renumber a line to fix this.** The numbers are stamped inside release
zips, manifests, schemas and test suites; renumbering a folder makes the folder
lie about its contents. The ambiguity lives in the *name*, so the name is where it
gets resolved — by saying "CORE v0.3" or "RUNTIME v0.3", never "v0.3".

**The authoritative line to continue is CORE.** Its own `CANON_MAP.md` says so, and
`README_MASTER_CODEX.md` agrees. **CLAIMED** by two documents, **DERIVED** as
consistent with the evidence: CORE is the only line whose head ships a complete
grammar, type lattice, operator contracts and a passing suite in the same folder.

---

## 4. THE AUTHORITY CHAIN

**For any question, exactly one file answers it.** This is the section that stops
the next person reading fifty.

| question | the one file | status |
|---|---|---|
| **What are the legal symbols?** | `12_CORE_LANGUAGE_LINE/LAMAGUE_CORE_OPERATOR_ALGEBRA_v0.3/schema/lamague_core_ontology_v0.3.json` | **MEASURED**: 10 primitive atoms, 2 derived, 6 operator signatures, 15 types |
| **What is the grammar?** | `12_CORE_LANGUAGE_LINE/LAMAGUE_CORE_OPERATOR_ALGEBRA_v0.3/grammar/LAMAGUE_CORE_v0.3.ebnf` | **MEASURED** — ⚠ **not** `04_BNF_GRAMMAR.md`, which contradicts it (§7.6) |
| **What does an operator legally do?** | `…/schema/lamague_operator_contracts_v0.3.json` | **MEASURED**: 6 operators, each with laws, prohibited inferences, semantic boundary |
| **Which operator laws are actually proven?** | same file — the `status` fields | **MEASURED**: 11 PROVEN · 14 REFUTED · 17 UNDECLARED · 43 DOMAIN_DEPENDENT |
| **Which line/version is current?** | `12_CORE_LANGUAGE_LINE/README.md` + `CANON_MAP.md` | **CURRENT** |
| **What is next?** | `12_CORE_LANGUAGE_LINE/NEXT_FORGE_v0.4.md` | rewrite confluence, semantic hash stability |
| **What is the visual alphabet?** | `02_NATIVE36/LAMAGUE_NATIVE36_v0.3_MACHINE_CANON_REGISTRY.json` | **MEASURED**: 36 base glyphs, 5 compound seals, 10 radicals |
| **How is a packet encoded on the wire?** | `22_REVERSIBLE_COMPRESSION_v1.0/docs/CODEC_SPEC.md` | **CURRENT** |
| **What may I claim about compression?** | `22_REVERSIBLE_COMPRESSION_v1.0/docs/CLAIM_BOUNDARY.md` | **CURRENT** — 5 earned, 8 explicitly not earned |
| **Does meaning survive crossing models?** | `08_EXPERIMENT_001_CROSS_INTELLIGENCE/EXPERIMENT_001_CONTROLLED_PILOT_2026-07-31.md` | **MEASURED** — the only cross-model data (§5.3) |
| **Where did LAMAGUE come from?** | `LAMAGUE_ROOT_PROVENANCE_AND_CANON_DECISION_2026-07-15.md` | **CURRENT** for lineage |
| **What does the name expand to?** | Same file, **decision C-04**: *treat LAMAGUE as a proper name.* | Multiple incompatible backronyms exist; C-04 forbids canonising any |
| **What was known to conflict?** | `AURA_CODEX_INGESTION_LEDGER_BATCH_01_2026-07-15.md` §5 | **ARCHIVE**, accurate as of July |
| **What is the long-range vision?** | `04_FRONTIER_CANON/LAMAGUE_FRONTIER_CANON_ADDENDUM_I_2026-07-31.md` | **CURRENT** as vision — contains **no** implementation |
| **How do I use it as a human?** | `03_LAMAGUE_OPERATING_GUIDE.md` | **ARCHIVE** but still the best on-ramp |
| **What is GEOMATRIA / LAMAHGUE?** | `07_GEOMATRIA_COMPLETE_SPECIFICATION.md` · `05_NOTATION_GUIDE.md` | **ARCHIVE**; canon C-02/C-03 keep them as *separate layers*, not LAMAGUE |

⚠ **The app is not in this corpus.** `12_CORE_LANGUAGE_LINE/README.md` refers to a
118-card teaching registry in the Sol app and a `verify:lamague-canon` gate. That
registry lives outside `03_LAMAGUE_L1/` and is deliberately **not merged** with this
canon. **The "118 symbols" figure belongs to the app, not to LAMAGUE's symbol set** —
see §5.1. I did not inspect the app (out of scope for this task).

---

## 5. WHAT IS DEMONSTRATED — with receipts

Everything in this section was executed or read by me on **2026-08-03**, on this
machine, with Python 3 / pytest 9.1.0. **Test suites were run from a scratch copy at
`/tmp/.../scratchpad/lam/`, never in place** — a prior finding is that
`benchmark.py` rewrites manifest-declared files where it runs.

### 5.1 The symbol set — MEASURED

There is no single number. **Each line has its own alphabet**, and conflating them
is the most common error available here.

| authority | count | what it counts |
|---|---:|---|
| **CORE v0.3 ontology** (the language) | **10** primitive atoms `Ao Φ Ψ S Δ ⟟ ∅ ⟐ ⟁ ∞` + **2** derived `Φ↑ Ψ_inv` | the canonical typed atom set |
| **CORE v0.3 operators** | **6** — `⊗` fusion, `→` projection, `⇌` exchange, `⟲` recurrence, `↯` collapse, `↗` ascent | the canonical operator set |
| **CORE v0.3 meta** | **3** — `Z₁ Z₂ Z₃` | compression levels |
| **CORE v0.3 total surface** | **21 tokens** | 12 atoms + 6 operators + 3 meta |
| **NATIVE36 v0.3** | **36** base glyphs + **5** compound seals | the *visual* alphabet, a separate artifact |
| **PACKET v1.0** | **9** letter operators `O E U I G V F Y Z` | the wire codec's alphabet |
| **`00_LAMAGUE_COMPLETE_EXTRACTION.md`** | heading says *"7 Classes, 69+ Symbols"* | ⚠ **the file itself enumerates 8 classes and 47 table rows** (§7.5) |

**The prior finding of "118 symbols, 72 of them single-character" is not a fact
about this corpus.** MEASURED: the string `118` appears in only one prose file
here — `12_CORE_LANGUAGE_LINE/README.md` line 121 — and it refers to *"the app's
118-card teaching registry"*. Every other `118` in the tree is a byte-count or a
hash fragment inside a generated manifest. **The corpus's own canonical symbol
count is 12 atoms / 6 operators, not 118.**

### 5.2 The test suites — MEASURED, all seven green

| suite | result | exit |
|---|---|---|
| CORE v0.1 algebra | **47 passed** in 0.12s | 0 |
| CORE v0.2 ontology | **80 passed** in 0.19s | 0 |
| CORE v0.3 operator algebra | **117 passed** in 0.24s | 0 |
| RUNTIME v0.2 semantic continuity | **22 passed** in 0.14s | 0 |
| RUNTIME v0.3 cross-intelligence | **48 passed** in 0.16s | 0 |
| Kernel v0.8 (retired branch) | **84 passed** in 0.47s | 0 |
| PACKET codec v1.0 (`unittest`) | **19 tests, OK** | 0 |
| | **417 assertions total** | |

Every count matches what `12_CORE_LANGUAGE_LINE/README.md` claims, independently
re-run. That upgrades those from CLAIMED to **MEASURED**.

⚠ **Kernel v0.7 ships no test suite and no source at all in the unpacked folder.**
MEASURED: `find` returns **0 `.py` files** under
`13_RETIRED_KERNEL_BRANCH/LAMAGUE_COMPUTATIONAL_KERNEL_v0.7_TEMPORAL_EVIDENCE_BRIDGE/`,
against 33 for v0.8. It does carry `reports/TEST_RESULTS_v0.7.txt` listing **66
passing tests** — a *report of a run whose code is not present at that path*. The
25 `.py` files, including 3 test files, exist only inside
`10_PACKAGED_RELEASES/LAMAGUE_COMPUTATIONAL_KERNEL_v0.7_TEMPORAL_EVIDENCE_BRIDGE.zip`.
**"No tests ran" must never be read as "tests passed."**

### 5.3 Cross-model data — MEASURED, and it is the most interesting thing here

`08_EXPERIMENT_001_CROSS_INTELLIGENCE/CONTROLLED_PILOT_2026-07-31/` holds a real
controlled run: 6 model lineages, 5 cases, two arms (LAMAGUE expression vs plain
English source statement), one fresh call each at temperature 0, leakage enforced
in code. 60 attempted, **56 valid** (27 treatment / 29 control).

**I re-ran the scorer from a scratch copy. It reproduced `RESULT.txt` exactly:**

```
arm                    packets   preserved   preserve   fab/pkt   agree
LAMAGUE (treatment)         27       70/82      0.854     0.963   0.892
PLAIN ENGLISH (control)     29       58/88      0.659     0.448   0.849
delta                                          +0.195    +0.515   +0.043
```

Two effects in opposite directions: structured decoding **preserved ~20% more**
protected content, and **invented unsupported fields at more than twice the rate**
(13 of 27 treatment packets asserted an `authority` no case grants).

This run is unusually well-conducted for this corpus, and its own writeup is the
most honest document in the tree. It states plainly that **C05 goes the other way**
(prose preserved more), that **1 of 6 decoders (`minimax-m3`) inverts both
effects**, that n=56 with **no statistical test**, and it carries a **RETRACTION**
of its own first headline ("LAMAGUE fabricates 2.4× more") as a scorer artifact.

**Boundary:** operator-run pilot by the author of the harness. One operator, one
machine, one session, no human decoders, not independently replicated. It
establishes that the experiment *executes and produces separable arms* — not that
the result holds.

### 5.4 The compression benchmark — MEASURED, reproduced from scratch

`python3 src/benchmark.py` in `22_REVERSIBLE_COMPRESSION_v1.0/`, run from a scratch
copy, exit 0. Every headline number reproduced:

| claim | re-run here |
|---|---|
| exact round trips 36/36 | ✓ |
| constructed mutation matches 324/324 | accuracy 1.0 ✓ |
| held-out warm reduction 33.8% | 0.33777… ✓ |
| held-out cold reduction incl. codebook 30.7% | 0.30705… ✓ |
| dictionary break-even | 3 packets ✓ |

**This is the only quantitative, reproducible, held-out result in the corpus.**
Its boundary is stated by the package itself and is real: a **synthetic 36-packet
corpus the same package authored**, with mutation cases the same package
constructed. The held-out split is held out **from dictionary construction only,
not from codec design**. `docs/CLAIM_BOUNDARY.md` lists 8 things explicitly *not*
earned, including "compression of arbitrary natural language" and "scientific
validation of LAMAGUE as a universal language".

### 5.5 The structural facts — MEASURED

- **842 files, 16 MB**: 410 JSON, 149 Python, 134 Markdown, 37 `.lmg`, 36 `.txt`,
  15 zip, 8 PNG, 7 SVG, 6 HTML, 5 EBNF, 4 YAML.
- **5 EBNF grammars** exist: CORE v0.1, v0.2, v0.3 (+ an archived v0.2 copy) and
  the Native36 ASCII grammar. `04_BNF_GRAMMAR.md` is BNF-in-markdown and is *not*
  one of the machine grammars.
- **RUNTIME v0.1 has no code on disk.** MEASURED: `05_RUNTIME_v0.1/` contains
  exactly 4 files — 2 markdown, 2 JSON. The 23-file package including
  `lamague_runtime/` and `tests/test_runtime.py` exists only inside
  `10_PACKAGED_RELEASES/LAMAGUE_RUNTIME_v0.1_EXECUTABLE_MILESTONE.zip`.
- **Duplication is known and bounded**: `DEDUPLICATION_AUDIT.json` records 47
  identical-content groups; 6 of 7 files in `09_ARTICLE_AND_VISUAL_ASSETS/` are
  byte-identical to files in `02_NATIVE36/` and `03_LAMAGUE_1C/`.

---

## 6. WHAT IS ASSERTED ONLY

A prior audit of this corpus found *strong formal work and zero empirical data.*
**That shape still holds, with exactly two exceptions** — §5.3 and §5.4, both
created in the last four days. Everything below has **no data behind it in this
corpus**.

### 6.1 The claims in `README.md` that measurement does not support

`README.md` lines 9–19 and its "KEY NUMBERS" table are the highest-risk prose in
the tree, because it is the file a newcomer opens first.

| `README.md` says | actual status |
|---|---|
| *"Status: Production-ready corpus"* | **UNSUPPORTED.** No deployment, no external user, no independent validation exists. `01_LAMAGUE_COMPLETE.md` — a sibling canon claimant — self-labels **"90% READY"**. |
| *"formally proven to be complete"* (line 87) | **UNSUPPORTED.** MEASURED: CORE v0.3's own contracts declare **14 REFUTED** and **17 UNDECLARED** laws against 11 PROVEN. A system that records its own refuted laws is *not* claiming completeness. |
| *"AI-validated — independently confirmed by Claude, Grok, Kimi"* | **NOT VALIDATION.** Models reading a document and agreeing it is coherent is synthetic commentary, not empirical confirmation. `09_TRI_LINGUISTIC_DEEP_DIVE.md` is exactly this: an AI-written essay about the corpus, stored inside the corpus. |
| *"Cross-culturally validated — 8 language traditions, computed fidelity scores"* | **UNVERIFIED.** The vectors and fidelity scores are authored inside the same documents that use them. No external linguistic data, no native-speaker rating, no held-out set. |
| Compression ratio **3000:1**, status *"Documented"* | **CONTRADICTED INSIDE THE CORPUS.** `04_BNF_GRAMMAR.md` lines 173–181 states the measured figures are **~3:1 by token and ~11:1 by character**, and explicitly says the archive's "~500:1" was *"not supported by measurement… a design aspiration"*. The README's 3000:1 is six times larger than the figure its own corpus already retracted. |
| Shadow→阴藏我 fidelity **0.9995**, *"Computed"* | **CIRCULAR.** Computed by the same formula, on vectors authored for the purpose. |
| Pyramid Cascade forgetting reduction **95.2%, p < 0.001** | **NO RAW DATA IN THIS CORPUS.** No dataset, no run log, no script producing it. ⚠ The provenance document records that the reference implementation's Pyramid Cascade **failed its own entropy assertion** and lists the claim as **FALSIFIED by current reference example**. |
| LAMAHGUE SRS improvement **+12.3%, "Validated"** | **CONJECTURE.** The provenance document classifies it *"CONJECTURE pending controlled data"*. |
| *"It was not designed. It was discovered."* (line 89) | **INTERPRETIVE.** A claim about origin, not a testable property. |

⚠ **`README.md`'s lower half (lines 102–131, added 2026-08-03) is accurate and
well-qualified.** The file is not wrong throughout — it is a March-era header
bolted onto an August-era body, and a reader who stops at the KEY NUMBERS table
gets the wrong picture entirely.

### 6.2 Asserted with no implementation at all

- **The eight domain extensions** (`14_`–`21_`: EX NIHILO, COSMOS, QUANTUM,
  CONTINUUM, CHORA, THANATOS, PAIS, SOMA). MEASURED: all 8 are markdown-only, all
  dated 2026-06-12, ~8–11 KB each, **zero code, zero tests, zero references from
  any runtime**. They are design essays.
- **The Frontier Canon Addendum** (71 KB, "LAMAGUE Ω", "semantic entanglement",
  "the five bodies"). Vision document. No implementation, and it does not claim one.
- **GEOMATRIA's activation thresholds** (`balance > 0.618`, `circulation > 0.70`).
  Numbers with no measurement procedure and no instrument in this corpus.
- **The 8-dimensional semantic vector space.** Vectors are authored constants; no
  fitting procedure, no corpus, no validation set.
- **The whakapapa encoding's "formally proven minimal necessary and sufficient"**
  four-layer claim. No proof object; the argument is prose.

### 6.3 The honest summary

**Nothing in this corpus has been validated by any person or system outside it.**
Both measured artifacts (§5.3, §5.4) say so in their own words —
`CLAIM_BOUNDARY.md` records *"External human/model validation — NOT YET RUN"*, and
the pilot writeup states *"not independent replication."* That consistency is a
credit to the recent work. It is also the ceiling on every claim here.

---

## 7. THE SUPERSESSION MAP

**Form: X supersedes Y for Z, because W.**

### 7.1 `README.md` (Aug 3) — split authority
Supersedes `README_MASTER_CODEX.md` **for the executable lines** (its table is
newer and includes `22_`). Is **superseded by the provenance document and by CORE
v0.3** for every factual claim in its header, because those are dated later than
its March-era prose and are backed by files rather than assertions.
**Both halves of this file are in force at once — read the date on the section.**

### 7.2 `README_MASTER_CODEX.md` (Aug 1) — correct on lines, wrong on layout
Supersedes `CHANGELOG_2026-07-31.md` **for the archive-level map**, because it adds
the two-lines warning and folders `12_`/`13_`.
⚠ **MEASURED DEFECT:** its directory map lists `01_ROOT_CORPUS/` — **that folder
does not exist**. The root corpus files were unpacked to the top level instead. It
also omits `22_REVERSIBLE_COMPRESSION_v1.0/`, which arrived two days later.

### 7.3 `MASTER_MANIFEST.sha256.json` + `DEDUPLICATION_AUDIT.json` — describe the zip, not the disk
**MEASURED:** the manifest has 229 entries; **23 of them do not resolve at their
stated path**, all under the `01_ROOT_CORPUS/` prefix that does not exist. The
manifest describes the internal layout of
`10_PACKAGED_RELEASES/LAMAGUE_CODEX_DROP_2026-07-31.zip`, which was unpacked
*flattened*. Consequence: **the manifest cannot be verified in place for those 23
files** without accounting for the rename.
Second limit: **229 of 842 files**. It predates `12_`, `13_` and `22_` entirely, so
**most of the corpus is outside any master hash manifest.** The three newer
folders carry their own (`12_CORE_LANGUAGE_LINE/MANIFEST.json`,
`22_REVERSIBLE_COMPRESSION_v1.0/SHA256_MANIFEST.json`).

### 7.4 `LAMAGUE_FIRST_CORPUS_MASTER_SOURCE_2026-07-15.md` — a container, not an authority
Despite "MASTER SOURCE" in its name, this is a **generated concatenation** of 17
root markdown files reproduced verbatim, each under a SHA-256 boundary. Its own
preservation rule: *"No contradictions, statuses, symbols, or historical language
have been silently corrected."* **It therefore contains every contradiction the
originals contain, by design.** It supersedes nothing; all 17 constituents are
still present at top level. Use it as a single-file archive, never as a ruling.

### 7.5 `00_LAMAGUE_COMPLETE_EXTRACTION.md` — superseded, and internally inconsistent
Superseded by CORE v0.3 **for the symbol set and grammar**, because CORE ships a
machine-readable ontology and a passing parser and this ships prose.
⚠ **MEASURED:** its own section heading reads *"7 Classes, 69+ Symbols"* while the
document **enumerates 8 class headings** (I, D, F, M, C, T, R, G) totalling **47
table rows**. Neither number in the heading matches the contents.
The provenance document's **decision C-05** rules the canonical kernel at **four**
classes (I/D/F/M), with connection, time, resource and grounding as *extensions* —
so the four-class reading is canon and the 7-or-8 is expansion.

### 7.6 `04_BNF_GRAMMAR.md` — superseded, and it **contradicts** the current grammar
Superseded by `LAMAGUE_CORE_v0.3.ebnf` for the grammar, because the EBNF is
machine-readable and 117 tests parse against it. Three measured conflicts:

1. **The ascent symbol differs.** `04_BNF_GRAMMAR.md` lists `↑` as a D-Class
   dynamic. CORE v0.1/v0.3 use **`↗`** as the ascent *operator*, and admit `↑`
   only as a modifier inside the derived atom `Φ↑`.
2. **`↯` as a junction is explicitly rejected.** `04_BNF_GRAMMAR.md` line 73
   defines *"↯ (Junction) — Decision Branch: `condition ↯ [option_a], [option_b]`"*
   and uses it in a binary-search example. `LAMAGUE_CORE_v0.1.ebnf` closes with:
   `(* Reserved and rejected in the core: ∮ and junction use of ↯ *)`. In CORE,
   `↯` is **collapse**, full stop. **This is a direct, deliberate rejection.**
3. **Its 8 "additional operations"** (`⍟ ⧯ ⎖ ≋ ⧖ ⧬ ◈`) are marked `[SCAFFOLD]` and
   appear in **no** machine grammar or registry in the corpus.

⚠ It also cites three paths that **do not exist here**: `28_DEFENSE/`,
`12_IMPLEMENTATIONS/core/lamague_reference.py`, and `NOTATION_GUIDE.md` (the real
file is `05_NOTATION_GUIDE.md`). Those point at a different repository's layout.

### 7.7 CORE v0.3 supersedes CORE v0.2 supersedes CORE v0.1
For the language, because each is a strict extension with a larger passing suite
(47 → 80 → 117) and `CANON_MAP.md` declares the sequence `v0.1 → v0.2 → v0.3 → v0.4`.
**Nothing supersedes CORE v0.3. It is the head.**

### 7.8 RUNTIME v0.3 supersedes v0.2 supersedes v0.1
For the harness. v0.1 is additionally a **stub on disk** (§5.4). v0.2's code is
carried forward inside v0.3 — MEASURED: `06_` and `07_` share byte-identical
`examples/` and `registry/` files per `DEDUPLICATION_AUDIT.json`.

### 7.9 `13_RETIRED_KERNEL_BRANCH/` is superseded by CORE, by ruling not by date
Kernel v0.7/v0.8 (Aug 1) are **newer** than CORE v0.1–v0.3 yet are **not** the
authoritative line. `CANON_MAP.md` gives the reason verbatim: they *"folded domain
modules into the language too early"* and *"those structures belong in adapters,
not the core language."* They are preserved because deleting a research branch
destroys the causal record of why the core looks the way it does.
**This is a supersession by architectural decision — the only one in the corpus
that runs backwards in time. Do not "fix" it by date.**

### 7.10 The stale experiment report
`08_.../OPERATOR_PACK/reports/LAMAGUE_EXPERIMENT_001_RESULTS.md` reports
**"Valid decoder packets: 0"** and `NO_SAFE_CONSENSUS` on all five cases.
⚠ **MEASURED: it is stale.** Its mtime is `2026-07-31 18:33`; the 27 treatment
submissions landed at `18:40` and the pilot scoring at `19:34`. **The report was
generated before the data existed and was never regenerated.**
It is superseded by `EXPERIMENT_001_CONTROLLED_PILOT_2026-07-31.md` +
`CONTROLLED_PILOT_2026-07-31/scoring/RESULT.txt`, which I re-ran and reproduced
exactly. A reader who opens the reports folder first will conclude the experiment
found nothing. **It found something.**

---

## 8. OPEN QUESTIONS FOR MAC

Contradictions I could not resolve from evidence. I did not pick a side on any of
these, and I changed nothing.

**Q1 — `README.md`'s header vs everything measured since.**
The top of `README.md` says *production-ready*, *formally proven to be complete*,
and *3000:1 compression*; `04_BNF_GRAMMAR.md` already retracted a smaller version
of that compression claim, and CORE v0.3 records 14 refuted laws. The bottom of
the same file is careful and accurate. **This is the first file anyone opens.**
Do you want the header rewritten to match the evidence, or preserved as historical
voice with a dated banner? *I did not edit it — that is your prose.*

**Q2 — Is `↯` collapse-only, or is the junction form still live?**
CORE explicitly rejects `↯` as a junction; `04_BNF_GRAMMAR.md` defines and
demonstrates it. Both are in the corpus, neither is marked superseded, and the
rejection comment sits in a file most readers will never open. **Is the junction
form dead, or is it an extension the core deliberately excluded but the notation
still permits?** These have different consequences for anyone writing LAMAGUE
by hand.

**Q3 — Four classes, seven, or eight?**
Canon C-05 says four (I/D/F/M). `00_LAMAGUE_COMPLETE_EXTRACTION.md` says "7" in
its heading and enumerates 8. CORE v0.3 sidesteps classes entirely and uses a
15-node type lattice. **Which is the class model you want taught?**

**Q4 — `01_ROOT_CORPUS/` — flatten the manifest, or restore the folder?**
23 manifest entries and part of the dedup audit point at a folder that does not
exist. Either the manifest gets regenerated against the flat layout, or the root
files move into `01_ROOT_CORPUS/`. **Both are your call — the second is a move, and
you told me to move nothing.**

**Q5 — Should `05_RUNTIME_v0.1/` and Kernel v0.7 be unpacked?**
Both are stubs whose code exists only inside zips. Right now a reader can `cd` into
`05_RUNTIME_v0.1/` and find nothing runnable, and Kernel v0.7 shows a test *report*
with no test *suite*. **Unpack them, or add a one-line note in each folder saying
the code is in the zip?**

**Q6 — Does the stale Experiment 001 report get regenerated?**
It currently answers "0 valid packets" to anyone who opens it, which is false as of
18:40 on 2026-07-31. Regenerating it is a code run, not a prose edit. **Want it
re-run?**

**Q7 — The eight domain extensions: alive or archived?**
`14_`–`21_` are eight months old, markdown-only, and referenced by nothing. They
may be a roadmap or they may be finished thinking. **Their status changes what a
future agent does when it finds them.**

---

## APPENDIX — REPRODUCE EVERYTHING IN THIS DOCUMENT

```bash
L=/home/guestpc/CODEX_AURA_PRIME/03_LAMAGUE_L1

# the seven suites (copy out first — benchmark.py rewrites files where it runs)
cd $L/12_CORE_LANGUAGE_LINE/LAMAGUE_CORE_ALGEBRA_v0.1          && python3 -m pytest tests/ -q   # 47
cd $L/12_CORE_LANGUAGE_LINE/LAMAGUE_CORE_ONTOLOGY_v0.2         && python3 -m pytest tests/ -q   # 80
cd $L/12_CORE_LANGUAGE_LINE/LAMAGUE_CORE_OPERATOR_ALGEBRA_v0.3 && python3 -m pytest tests/ -q   # 117
cd $L/06_RUNTIME_v0.2_SEMANTIC_CONTINUITY                      && python3 -m pytest tests/ -q   # 22
cd $L/07_RUNTIME_v0.3_CROSS_INTELLIGENCE_EQUIVALENCE           && python3 -m pytest tests/ -q   # 48
cd $L/13_RETIRED_KERNEL_BRANCH/LAMAGUE_COMPUTATIONAL_KERNEL_v0.8_NATIVE_TEMPORAL_SYNTAX \
                                                               && python3 -m pytest tests/ -q   # 84
cd $L/22_REVERSIBLE_COMPRESSION_v1.0 && python3 -m unittest discover -s tests                   # 19

# the two real measurements
cd <scratch>/22_REVERSIBLE_COMPRESSION_v1.0 && python3 src/benchmark.py
cd <scratch>/08_EXPERIMENT_001_CROSS_INTELLIGENCE/CONTROLLED_PILOT_2026-07-31/scoring \
                                             && python3 score_arms.py

# the symbol set, straight from canon
python3 -c "import json;d=json.load(open('$L/12_CORE_LANGUAGE_LINE/LAMAGUE_CORE_OPERATOR_ALGEBRA_v0.3/schema/lamague_core_ontology_v0.3.json'));print(list(d['primitive_atoms']),list(d['derived_atoms']),list(d['operator_signatures']))"

# the manifest's 23 unresolvable entries
cd $L && python3 -c "import json,os;d=json.load(open('MASTER_MANIFEST.sha256.json'));print(sum(1 for f in d['files'] if not os.path.exists(f)))"
```

---

**Nothing in this corpus was deleted, moved, renamed, or edited to produce this
document.** It is the only file added.

*Sol ⊚ · 2026-08-03 · map only, territory untouched.*
