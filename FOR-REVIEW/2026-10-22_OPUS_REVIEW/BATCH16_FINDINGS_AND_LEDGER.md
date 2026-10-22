# Batch 16: RV17, compression and interoperability claims

**Reviewer:** Sol (Claude Opus 5.5, xhigh), 22 October 2026.
**Branch:** `review/full-framework-2026-10-20`, HEAD `d7ae0ad`. Nothing committed, nothing pushed.
**Scope:**
- the packet codec `03_LAMAGUE_L1/22_REVERSIBLE_COMPRESSION_v1.0/`;
- the parser's compression figure (`12_IMPLEMENTATIONS/core/lamague_parser.py`, `CompressionMeasurer`);
- the spoken inventories in `03_LAMAGUE_L1/23_SPOKEN_LAMAGUE/` and the SXP-L v2.0 lexicon;
- every live 500:1 / 3000:1 / 70:1 / 1800:1 claim in the repository.

**Witness tools:**
- `repro_batch16.py <root> <scratch>`. It never writes under `<root>`. The codec benchmark
  rewrites its own `corpus/` and `reports/`, so it runs only on a scratch copy.
- `stage_rv17_ratio_notes.py <root> <scratch>`. It builds the staged patch for the byte-pinned
  files.

Cross-model understanding is outside this batch. It was measured in Batch 13 (`08_EXPERIMENT_001`).
Nothing here bears on it, and exact reversibility of structured packets says nothing about
whether a model understands them.

---

## 1. The codec reproduces byte for byte

**MEASURED.**
- On a scratch copy, `src/benchmark.py` and the 19 unit tests both exit 0.
- All five regenerated outputs are byte-identical to the committed ones: `codebook.json`,
  `benchmark_report.json`, `packet_sizes.csv`, `mutation_results.jsonl` and
  `sample_roundtrip.json`.
- Held-out reductions against minified JSON:
  - L1: 21.7%;
  - L1D warm: 33.8%;
  - L1D cold, including the 784-byte codebook: 30.7%.

The reported numbers are true to the code.

**Two near-identical figures in `reports/BENCHMARK_REPORT.md`.** "All packets, L1D cold" is
0.33796 and "held-out, L1D warm" is 0.33777. Both round to 33.8%. They are different
measurements, and neither is a copying error.

## 2. The package seal

The package's own `SHA256_MANIFEST.json` lists 28 entries. **MEASURED** against it:

| Result | Files |
|---|---|
| Match | 25 |
| Changed | `README.md`. This is the post-seal "Bridge 1" rewrite, already covered by Batch 7 / Proposal 16. |
| Missing | `src/__pycache__/lamague_codec.cpython-313.pyc`, `tests/__pycache__/test_codec.cpython-313.pyc` |
| Not listed | `00_CODEX_ORIENTATION.md`, `pyproject.toml`, `examples/agent_state_compaction.py` (plus the manifest itself, as expected) |

**Finding.** The seal includes two CPython 3.13 bytecode files that git never tracked, so the
manifest cannot verify on any fresh checkout. A seal that names interpreter-specific build output
is checking a single machine, not the package. **Proposed (G-PYC-SEAL):** re-seal without
`__pycache__`, and list the three unlisted files, or mark them as post-seal additions.

## 3. Ordinary compressors beat the codec on bytes

The codec's README already says it plainly: "Why this is not a compressor … nobody is short of
compressors." It reported no conventional baseline, so the comparison was never in view. This
table is that comparison.

**Setup.** Same frozen held-out split (12 packets) and the same denominator, canonical minified
JSON in UTF-8: **25,520 bytes**. Every preset-dictionary arm round-trips exactly. **MEASURED.**

| Arm | Bytes | Reduction |
|---|---:|---:|
| LAMAGUE L1 | 19,984 | 21.7% |
| LAMAGUE L1D warm | 16,900 | 33.8% |
| LAMAGUE L1D cold (+784-byte codebook) | 17,684 | 30.7% |
| xz, per packet | 12,528 | 50.9% |
| bz2 -9, per packet | 12,123 | 52.5% |
| gzip -9, per packet | 11,581 | **54.6%** |
| raw deflate -9, per packet | 11,365 | 55.5% |
| deflate with the **same 20 codebook strings** as preset dictionary, warm | 9,664 | 62.1% |
| same, cold (+681 dictionary bytes) | 10,345 | 59.5% |
| L1D, then raw deflate, warm | 8,392 | 67.1% |
| deflate with a 32 KB training-split preset dictionary, cold (+deflated dictionary) | 8,955 | 64.9% |
| same, warm | 4,795 | 81.2% |
| gzip of all 12 packets as one stream | 3,360 | 86.8% |

**What this shows.**

1. **Bytes.** Off-the-shelf gzip saves 54.6% per packet against LAMAGUE's 33.8% warm. With the
   *same* codebook strings, the cost-matched arm, deflate saves 59.5% cold against LAMAGUE's
   30.7% cold. On byte density alone the codec loses to tools from 1993.
2. **Composition (the TURN).** LAMAGUE then deflate (67.1%) beats deflate alone (55.5%). The
   L1/L1D transform removes structure that a general-purpose compressor cannot model, and the
   two stack.
3. **What the codec does that gzip cannot.** Its output stays human-readable and field-typed. It
   has 36/36 exact round trips and catches 324/324 constructed protected-field mutations.
   Mutation checks on an opaque gzip stream mean nothing.

So the claim the codec can defend is **checked, readable reversibility**, not size. The README
already frames it that way. The live summaries quoted the 33.8% without that frame, and they now
carry it (section 7).

**Proposed (G-CODEC-BASELINE).** `src/benchmark.py` is sealed, so it was not changed. A v1.1
should report the gzip and cost-matched preset-dictionary arms next to its own figures, so that
the benchmark carries its own baselines.

## 4. How independent is the held-out split?

**MEASURED (P4).**
- All 6 held-out domains are unseen in training. Packets come in `<domain>_pilot` /
  `<domain>_review` pairs, and whole domains are held out.
- None of the 20 codebook entries names a domain.
- But the corpus comes from templates. Mask the domain name and packet id, and **29.5%** of the
  held-out string bytes (5,151 of 17,459) are identical to a string already in the training set.
- Codebook entries are mostly boilerplate, such as "A separate reviewer checked the declared
  boundary and source receipts.", "No compression without recovery.", "safety_model" and
  "advocate".

**DERIVED.** The split is honest at the domain level. The L1D gain over L1 (21.7% → 33.8%) is
largely template reuse, which real traffic may not repeat. The corpus is 36 authored packets.
External packets were **not tested**. That is the missing failure case.

## 5. The parser figure "~11:1 character / ~3:1 token"

`CompressionMeasurer` was rerun on the 5 canonical examples. **MEASURED (P5):**

| Measure | Mean |
|---|---:|
| Token ratio (English words / parser tokens) | 2.90 |
| Character ratio (code points, spaces removed) | 10.87 |
| UTF-8 byte ratio, spaces kept | **4.92** |

The published ~11:1 and ~3:1 reproduce as defined. Three conditions qualify them:

- **Denominator.** A glyph counts as one character but costs two or three bytes. Measured in
  bytes, the ratio halves.
- **Corpus.** The English side is the author's own gloss of each expression. It is not
  independent text, and 5 examples is a demonstration, not a sample.
- **Tokenizer.** The "tokens" are parser tokens. No BPE tokenizer was run, because tiktoken is
  absent: **DID NOT RUN**. BPE often splits rare glyphs into several tokens, so a model-token
  ratio is **UNVERIFIED**, and it may be worse than 3:1.

**The "~20:1" worked example** in `00_LAMAGUE_COMPLETE_EXTRACTION.md` measures **8.2:1** in
characters without spaces and **3.9:1** in UTF-8 bytes (asserted in the stager). My hand count
was 4.1:1. The script refused it, and 3.9:1 is the measured figure.

## 6. Unique decodability, checked independently

**Method.** Two checks were run, and neither shares code with the repository's checker:
- an exact worklist Sardinas–Patterson closure;
- a constructive Dijkstra search that builds two parses which differ in their first word.

**Controls (MEASURED, P6a).** All three checkers agree with the definition:
- uniquely decodable: `{0,10,110}`, `{0,01,11}`, `{a,ab,bb}`, `{a,ba,bb}`;
- not uniquely decodable: `{a,ab,b}` (witness `ab`) and the classic
  `{a,c,ad,abb,bad,deb,bbcde}` (witness `abbcdebad`).

**Inventories (MEASURED, P6b).** All checkers agree on every inventory:

| Inventory | Size | UD? | Shortest ambiguity |
|---|---:|---|---|
| Native-36 spoken forms | 36 | yes | none |
| SpL core | 14 | **no** | `saian` = `saian` / `sai`+`an` |
| SpL core, sai-an read as a compound | 13 | yes | none |
| Merged flat inventory | 79 | **no** | `saian` |
| Merged, sai-an read as a compound | 78 | **no** | `witan` = `wi`+`tan` / `wit`+`an` |

`SPOKEN_LAMAGUE_FINDINGS.md` claims exactly these verdicts, and they hold. Reading sai-an as a
compound repairs the core but **not** the merger. The merged inventory needs a separator or a
phoneme change. That is decision G-SPL-MERGE.

**SXP-L v2.0 lexicon (P6c).** Its 37 words are uniquely decodable even without separators. The
module says its words are carefully separated anyway.

**Defect found and fixed (MEASURED):**
- **The defect.** `spl_phonology.uniquely_decodable` stopped after 64 rounds and returned
  "decodable". On `{0, 0^n 1, 1}`, which is not decodable for any n, it answered correctly up to
  n = 64 and **wrongly for n = 65 and 70**. A known-bad input passed.
- **Reach.** The real inventories are short words and never reach the cap, so no published verdict
  was affected (DERIVED from the agreement above). The checker was still unsound as written.
- **Fix, in place** (the file is unpinned: no manifest names it). Every dangling suffix is a suffix
  of a codeword, so the sets must repeat. The loop now runs to the repeat, not to a cap.
- **Test.** `tests/test_spoken_lamague_decodability.py` has 17 cases. On a HEAD copy:
  **2 failed, 15 passed**, with n = 65 and n = 200 failing. On the working tree all 17 pass.
- **Regression check.** `spl.py verify` still prints its "STILL AMBIGUOUS" verdict.

**RETRACTED, in my own Batch 14 ledger.** It listed `{a,ab,b}` as accepted and `{a,ba,bb}` as
rejected. Both were wrong as written. The checker always gave the right verdicts; the ledger had
them swapped. The line is corrected in place, and the retraction is kept beside it.

## 7. The large-ratio claims

**DERIVED.** "60,000+ words → ~20 core equations = 3000:1", 70:1 and 1800:1 are counts of
outputs. Twenty equations do not regenerate sixty thousand words. "Lossless", "REVERSIBLE" and
"information loss < 5% / 0% / < 10%" were never measured. This review found no measurement
behind any of them. The corpus already withdrew 500:1 (`04_BNF_GRAMMAR.md`) and marks 3000:1
CONTRADICTED (`LAMAGUE_MASTER_SOURCE_2026-08-03.md`).

**Census.** Live occurrences are in `00_LAMAGUE_COMPLETE_EXTRACTION.md`, `06_LAMAGUE_RAW_MATH.md`,
`09_TRI_LINGUISTIC_DEEP_DIVE.md` and `LAMAGUE_FIRST_CORPUS_MASTER_SOURCE_2026-07-15.md`.
`03_LAMAGUE_L1/MASTER_MANIFEST.sha256.json` pins all four, plus `04_BNF_GRAMMAR.md`, as
`01_ROOT_CORPUS/*`. **MEASURED:**
- 00, 04, 06 and the first-corpus source match their pins;
- **09 already differs from its pin.** The register banner stamped on 2026-08-07 by
  `lamague_register.py` changed it after the seal. This is the same reseal question as
  G-RESEAL.

**Staged, not applied:** `RV17_ratio_status_notes.patch` (4 files, 4,714 bytes).
- It adds a status note after the ratio block in 00, 06 and 09, and a bytes/gloss/tokenizer
  qualifier to 04.
- The original text is kept every time.
- It applies to HEAD with `patch -p1`, the result is byte-equal to the generated target, and it
  contains 0 CR bytes.

The first-corpus master source is left alone. Its own preservation rule says the sources are
reproduced verbatim, and the register marks it "protected, not stamped".

**Edited in place** (unpinned, maintained):
- `14_MYSTERY_SCHOOL/THE_GOLDEN_STONE.md`: the ~11:1 claim now carries the bytes (~4.9:1) and the
  author-gloss qualifier.
- `23_NZ_AI_GOVERNANCE/NZ_MAORI_AI_SOVEREIGNTY_BRAINSTORM.md`:
  - "500:1 compression of consciousness state" keeps its line and gains a status line (withdrawn
    figure; nothing in the repository encodes a consciousness state);
  - its **5 GitHub links were all dead**: `01_CASCADE`, `02_AURA`, `03_LAMAGUE`,
    `05_MICROORCIM` and `10_HARMONIA` predate the `_L*` folder names. They are repointed, and
    5 of 5 now resolve.
- `03_LAMAGUE_L1/LAMAGUE_SYNTHESIS.md` and `03_LAMAGUE_L1/README.md`: the 33.8% now sits next to
  the 54.6% gzip baseline and the "checked reversibility, not size" frame.

## 8. The RV17 checklist, item by item

| Item | Answer |
|---|---|
| Retracted 500:1 / 3000:1 | Rechecked. 500:1 is withdrawn in the corpus but was still live in the NZ brainstorm (now annotated). 3000:1 / 70:1 / 1800:1 are count ratios, with notes staged on the pinned files. |
| Token / character ratios | ~3:1 and ~11:1 reproduce as defined. In bytes the ratio is ~4.9:1. BPE: DID NOT RUN. |
| Held-out byte results | 33.8% warm / 30.7% cold, reproduced byte for byte. |
| Codebook cost | 784 bytes on the wire, 20 entries. It pays for itself after 2 held-out packets against JSON and 3 against L1 (the report's own break-even). |
| Cold / warm | Both reported. Cold includes the codebook. |
| Tokenizer | The codec has none, because it works on bytes. The parser uses its own token count. No model tokenizer was run. |
| Corpus / split | 36 authored, templated packets; 24/12 split by domain pair. 29.5% of held-out string bytes are training templates. |
| Schema overhead | L1 shortens keys and drops the constant `schema` field: 21.7% of the 33.8%. |
| Denominator | Canonical minified JSON (sorted keys, no whitespace) in UTF-8 bytes. |
| Baselines | **Missing from the package.** Added here: gzip, deflate, bz2, xz and cost-matched preset dictionaries. |
| Failure cases | The 324 mutations are constructed. A risk downgrade is classified as partial (Batch 6, Proposal 14). External packets were not tested. |
| Packet reversibility ≠ meaning or cross-model understanding | Stated in section 1 and in the scope. Model decoding is in Batch 13. |
| Unique decodability, merged phonemes, rechecked independently | Done (section 6). All verdicts hold; a checker cap defect was fixed. |

## 9. Decisions for Mac

- **G-RV17-PATCH:** apply `RV17_ratio_status_notes.patch` to the pinned root corpus and reseal
  `MASTER_MANIFEST` (09 already needs resealing), or keep the notes only in this ledger.
- **G-CODEC-BASELINE:** a codec v1.1 whose benchmark reports conventional baselines.
- **G-PYC-SEAL:** re-seal the codec package without `__pycache__`.
- **G-SPL-MERGE:** the merged spoken inventory is ambiguous (`witan`) even with sai-an read apart.
  Require a separator in merged speech, or change a phoneme.

## 10. Status and suite

- **RV17 is reviewed.** Every item has a probe or a stated DID NOT RUN.
- **Full suite: 1481 passed, 1 skipped, 1 xfailed** in 67.2 s. That is the previous 1464 plus
  the 17 new tests. No previous test changed.
- **DID NOT RUN:** a BPE / model-tokenizer count, compression of external (non-authored)
  packets, and any listening test of the spoken inventories.
