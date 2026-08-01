# 𝔏 THE CORE LANGUAGE LINE — v0.1 → v0.3

Consolidated **2026-08-01** from the *LAMAGUE Evolution Master Bundle*
(author: Mackenzie C. J. Clark). **479 files, verified byte-identical to the
bundle by md5 at consolidation time** — 132 here, 347 in `13_RETIRED_KERNEL_BRANCH/`.

---

## ⚠⚠ READ THIS FIRST — THERE ARE TWO v0.1/v0.2/v0.3 LINES IN THIS CORPUS

This is the single most confusing thing in `03_LAMAGUE_L1/`, and it is nobody's
mistake — two different efforts reached three versions each.

| | what it is | where |
|---|---|---|
| **CORE** | the **language**: algebra, ontology, operator contracts | `12_CORE_LANGUAGE_LINE/` ← you are here |
| **RUNTIME** | the **experiment harness**: does meaning survive crossing intelligences? | `05_` `06_` `07_` |

```
CORE    v0.1 symbolic algebra · v0.2 ontology + type lock · v0.3 operator contracts
RUNTIME v0.1 executable milestone · v0.2 semantic continuity · v0.3 cross-intelligence equivalence
```

**They are not versions of each other.** CORE v0.3 and RUNTIME v0.3 share a
number and nothing else. When you or anyone else says "LAMAGUE v0.3", say which
line, or the sentence does not mean anything.

⚠ **Never renumber either line to fix this.** The version numbers are stamped
inside the release zips, the MANIFESTs, the schema files and the test suites.
Renumbering the folder makes the folder lie about its contents — the ambiguity
lives in the NAME, so the name is where it is resolved.

---

## The authoritative sequence

```
v0.1 → v0.2 → v0.3 → v0.4
```

Per the bundle's own `CANON_MAP.md`, **this is the line to continue.**

- **v0.1** — independent algebra, grammar, normalizer, equivalence, semantic
  graph, lossless macros. *47 unit tests, 18 benchmark cases.*
- **v0.2** — typed ontology, subtype lattice, derived-symbol decomposition
  (`Φ↑ = modify(Φ, ↑)`), and `∅` as **intentional null, not missing information**.
  *80 unit tests, 30 benchmarks.*
- **v0.3** — machine-readable operator contracts, explicit law status
  (PROVEN / REFUTED / UNDECLARED / DOMAIN_DEPENDENT), rewrite traces, composition
  matrix. *117 unit tests, 36 benchmarks, declared-law verification passed.*

### ✅ MEASURED ON THIS MACHINE — 2026-08-01, pytest 9.1.0

The counts above are the bundle's own claim. They were **re-run here, and every
one matched exactly**:

```
CORE v0.1   47 passed in 0.14s     claimed 47   ✓
CORE v0.2   80 passed in 0.19s     claimed 80   ✓
CORE v0.3  117 passed in 0.25s     claimed 117  ✓
```

That upgrades them from REPORTED to **MEASURED**. Re-run any of them with:

```
cd 12_CORE_LANGUAGE_LINE/LAMAGUE_CORE_OPERATOR_ALGEBRA_v0.3 && python3 -m pytest tests/ -q
```

⚠ **A PASSING SUITE PROVES ONLY WHAT THE SUITE COVERS.** These are deterministic
software-conformance results, exactly as the bundle says. They do not establish
universal semantic validity, physical truth, alignment, consciousness, or
unrestricted compression, and nothing here upgrades that.

⚠ **THE RETIRED BRANCH IS NOT SYMMETRICAL.** Kernel v0.8 runs **84 passed**.
Kernel **v0.7 ships NO TEST SUITE AT ALL** — no `tests/` directory, no test files
anywhere in the release. It is documentation, benchmarks and reports only. That
is a fact about the release, not a failure of the run, and *"no tests ran"* must
never be read as *"tests passed"*.

**Next:** `NEXT_FORGE_v0.4.md` — canonical meaning, rewrite confluence, semantic
hash stability. Its question: *do all legal rewrite paths reach the same
canonical meaning?*

---

## The retired branch — preserved, not disowned

`13_RETIRED_KERNEL_BRANCH/` holds Computational Kernel **v0.7** and **v0.8**.

The bundle is explicit: they are **not** the authoritative core line. They proved
LAMAGUE could host temporal-evidence structures, but *"folded domain modules into
the language too early."*

Their correction, verbatim from `CANON_MAP.md`:

> those structures belong in adapters, not the core language

They should return later as `lamague-adapter-tim` and `lamague-adapter-microorcim`.
They are kept because deleting a research branch destroys the causal record of why
the core looks the way it does.

---

## The canon rule

No future adapter may:

- redefine a core primitive;
- change a core operator law;
- alias missing data to `∅`;
- silently reinterpret a glyph;
- promote domain claims into core truth;
- remove the original source representation.

---

## Where else this reaches

**`~/0sol-by-lycheetah/lib/lamague/canon/`** vendors the two v0.3 schema files so
the app can be checked against them. `npm run verify:lamague-canon` reconciles the
app's 118-card teaching registry against this canon — 19 checks.

⚠ **The app registry is NOT this, and they are deliberately not merged.** It is a
teaching corpus with years of forge-tested prose; this is a formal kernel. They
may differ. They may never **contradict** — that is all the gate enforces.

MEASURED at reconciliation: all 6 canonical operators are taught in the app,
0 cards teach a law the contracts refute, 0 contradict a declared directionality,
and **10 of 12 canonical atoms appear** — `Δ` (variation field) and `⟐`
(stable-triad marker) have no card yet. That is an authoring gap, not a defect,
and it is Mac's to close or leave.

---

## Provenance

Original bundle: `~/Downloads/LAMAGUE_EVOLUTION_MASTER_BUNDLE_2026-08-01/`.
The five original release zips are preserved unmodified in
`../10_PACKAGED_RELEASES/`, matching the pattern that folder already held.
