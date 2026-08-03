# 𝔏 REVERSIBLE COMPRESSION MILESTONE v1.0 — codex orientation

**Codex-authored note, 2026-08-03. Not part of the package's `SHA256_MANIFEST.json`.**
Everything else in this directory is the shipped release, byte-for-byte, and
verifies against that manifest — **28 / 28 OK at this path.** The original zip is
preserved unmodified at `../10_PACKAGED_RELEASES/LAMAGUE_REVERSIBLE_COMPRESSION_MILESTONE_v1.0.zip`
(`sha256 bf260f81…`), matching the pattern that folder already held.

Read the package's own `README.md`, then `docs/CLAIM_BOUNDARY.md`, then
`reports/BENCHMARK_REPORT.md`.

---

## ⚠⚠ THIS IS A **THIRD** LAMAGUE LINE — IT IS NOT CORE, AND IT IS NOT RUNTIME

`12_CORE_LANGUAGE_LINE/README.md` already warns that this corpus holds two
different v0.1→v0.3 progressions. **This import adds a third numbered lineage**,
and the version numbers again do not relate to each other.

| line | what it is | operators | where |
|---|---|---|---|
| **CORE** | the language: algebra, ontology, operator contracts | **6 symbolic**: `⊗ → ⇌ ⟲ ↯ ↗` | `12_CORE_LANGUAGE_LINE/` |
| **RUNTIME** | the experiment harness: does meaning survive crossing intelligences? | — | `05_` `06_` `07_` |
| **PACKET / PUBLIC CORE** | consequential semantic packets and their wire codec | **9 letter**: `O E U I G V F Y Z` | **here**, upstream `LAMAGUE_EXECUTABLE_KERNEL_v0.1` |

**MEASURED:** the two operator sets are *disjoint* — not one symbol in common.
CORE v0.3's declared set was read directly from
`12_CORE_LANGUAGE_LINE/LAMAGUE_CORE_OPERATOR_ALGEBRA_v0.3/schema/lamague_operator_contracts_v0.3.json`
(6 operators over primitive atoms `Ao Φ Ψ S Δ ⟟ ∅ ⟐ ⟁ ∞`). The 9-letter Public
Core was read from this package's `docs/SOURCE_LINEAGE.md`. They are different
alphabets serving different purposes.

⚠ This package's `upstream/LAMAGUE_EXECUTABLE_KERNEL_v0.1.zip` (`sha256 19684c6c…`)
is **not** any of the thirteen zips already in `../10_PACKAGED_RELEASES/` — hashes
compared, no match. It is a distinct upstream artifact that arrived only inside
this milestone.

⚠ **Do not renumber any of the three lines to fix this.** Version numbers are
stamped inside the release zips, manifests, schemas and test suites. The
ambiguity lives in the name, so the name is where it is resolved.

---

## ✅ MEASURED ON THIS MACHINE — 2026-08-03

The package's headline numbers are its own claim. They were **re-executed here
from a scratch copy, and every one reproduced exactly**:

```
python3 -m unittest discover -s tests     19 tests, OK, exit 0
python3 src/benchmark.py                  exit 0
```

| claim in `README.md` | re-run here |
|---|---|
| exact round trips 36 / 36 | 36 / 36 ✓ |
| constructed mutation matches 324 / 324 | accuracy 1.0 over 324 ✓ |
| safe extensions classified partial 36 / 36 | 36 / 36 ✓ |
| held-out warm reduction 33.8% | 0.33777… ✓ |
| held-out cold reduction incl. codebook 30.7% | 0.30705… ✓ |
| dictionary break-even 3 packets | 3 ✓ |

Byte totals behind those ratios: held-out baseline 25,520 → `L1` 19,984 →
`L1D` 16,900; codebook wire cost 784 bytes, charged in the cold figure.

That upgrades the headline from **CLAIMED** to **MEASURED**.

---

## ⚠ WHAT THE NUMBERS DO AND DO NOT MEAN

**This is the first artifact in `03_LAMAGUE_L1/` carrying real, reproducible
quantitative data rather than formal structure alone.** That is the reason it
matters, and it is also the reason to state its boundary precisely.

The measurement is **internal and deterministic**: a codec measured against a
36-packet corpus that the same package authored, with mutation cases the same
package constructed and froze in advance. Freezing expectations before execution
is genuine methodological hygiene, and the held-out split is real — but it is
held out **from dictionary construction only, not from codec design**. The
package says this itself, in `docs/BENCHMARK_PROTOCOL.md` and
`docs/CLAIM_BOUNDARY.md`, and does not overreach anywhere I checked.

So: **the software does what it says on the corpus it was given.** Nothing here
is evidence about unrestricted prose, human semantic agreement, cross-model
decoding, other languages, or attacks nobody defined. `docs/CLAIM_BOUNDARY.md`
lists eight things explicitly **not earned**, and its own status block records
`External human/model validation — NOT YET RUN`.

⚠ A benchmark a package runs on its own corpus is **conformance evidence, not
independent validation.** A green suite proves what the suite covers.

---

## Provenance

Source: `~/Downloads/LAMAGUE_REVERSIBLE_COMPRESSION_MILESTONE_v1.0.zip`, ingested
2026-08-03. Full receipt:
`../../13_SYNTHESIS_REPORTS/INGEST_2026-08-03_LAMAGUE_AND_TRUTH_PRESSURE.md`.
