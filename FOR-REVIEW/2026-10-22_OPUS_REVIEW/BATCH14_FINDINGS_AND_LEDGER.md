# Batch 14: RV15, the LAMAGUE status register and the folders it rates

**Reviewer:** Sol (Claude Opus 5.5, xhigh), 22 October 2026.
**Branch:** `review/full-framework-2026-10-20`, HEAD `d7ae0ad`. Working tree only: nothing
committed, nothing pushed.
**Scope:** `03_LAMAGUE_L1/lamague_register.py`, `LAMAGUE_STATUS_REGISTER.json`, every
folder the register rates, `24_LAMAGUE_CHECK/`, `02_NATIVE36/`, `23_SPOKEN_LAMAGUE/`,
`25_RESEARCH_CYCLE_23_POST_CRASH_OBSERVATION/`, and `MASTER_MANIFEST` as it seals them.

**Method.** Every claim below was run here. `repro_batch14.py` runs against a `git archive HEAD`
copy (BEFORE) and the working tree (AFTER), and it never writes to the root it reads. Each new
test was run on both. Frozen and checksummed files were left alone; their fixes are staged as
patches, and each patch was applied to a HEAD copy and checked with `cmp` and `sha256sum -c`.

No file was marked reviewed from its README alone.

---

## 1. What the register says, and what was true

The register gives every file in `03_LAMAGUE_L1/` a status. Its rule is that MEASURED means a
test suite, benchmark or verifier next to the file passes here. **MEASURED**, re-run here:

| Suite | Register count | Reproduced |
|---|---|---|
| 06 | 22 | 22 pass |
| 07 | 48 | 48 pass |
| Core v0.1 / v0.2 / v0.3 | 47 / 80 / 117 | 47 / 80 / 117 pass |
| 13_RETIRED v0.8 | 84 | 84 pass |
| 22 codec | 19 | 19 pass; benchmark 324/324 on constructed mutations, with its boundaries stated |
| **Sum** | **417** | **417** |

`verify_declared_laws.py` passes. Its own boundary statement calls this "finite structural
verification", and this ledger uses the same words.

The suite counts were honest. Four things in the register were not.

### F1. An INVALID registry was reported VALID (fixed)
The register decided Native36 by checking whether `"VALID"` appeared in the validator's output.
`"INVALID"` contains `"VALID"`, so a reversed, broken registry was rated MEASURED.
**MEASURED** BEFORE: MEASURED. AFTER: SCAFFOLD. The control (the committed registry) still
passes.

### F2. A failing suite was counted as passing (fixed)
`run_tests` treated a suite as passing when its output contained `"OK"`. If a failing test's
message contained `TOKEN` (or any word with `OK` in it), the suite counted as passing.
**MEASURED** BEFORE: a planted failing test was reported as "20 tests pass", MEASURED.
AFTER: the result comes from the exit code, so the failing suite is not counted.

### F3. Spoken LAMAGUE was rated "decodability proofs" but its verifier says no (fixed)
`spl.py verify` exits 1 with `STILL AMBIGUOUS`, and the word `an` decodes two ways in both the
FLAT inventory (79 forms) and the BOUND inventory (83 forms). The register never ran it: the
folder's MEASURED status was hard-coded.
The negative is recorded honestly in `SPOKEN_LAMAGUE_FINDINGS.md`. The Sardinas–Patterson
implementation is correct on known controls:
- uniquely decodable: `{0,10,110}`, `{0,01,11}`, `{a,ab,bb}` and `{a,ba,bb}` are accepted;
- not uniquely decodable: the classic set `{a,c,ad,abb,bad,deb,bbcde}` and `{a,ab,b}` are rejected.
- **RETRACTED (Batch 16, 2026-10-22):** these two lines first said `{a,ab,b}` was accepted and
  `{a,ba,bb}` rejected. Both were wrong as written: `ab` = `a`·`b`, so `{a,ab,b}` is not uniquely
  decodable, and `{a,ba,bb}` is a prefix code, so it is. The checker gives the right verdict on
  both (`repro_batch16.py` P6a). The error was in this ledger, not the code. A separate checker
  defect, its 64-step cap, is recorded in Batch 16.

**MEASURED** BEFORE: MEASURED, "decodability proofs". AFTER: SCAFFOLD, "spl.py verify: merged
inventory NOT uniquely decodable". The status now follows the verifier's exit code. If the
inventory is ever repaired, it returns to MEASURED by itself.

### F4. The retired kernel was MEASURED against the register's own rule (fixed)
The register's rule says a retired branch is SCAFFOLD. `13_RETIRED*` was still MEASURED.
AFTER: SCAFFOLD, with evidence "retired branch; 84 tests pass".

### F5. The register header and ten stamped files claim more than the evidence (header fixed; files staged)
The sentence "`02_NATIVE36/` and `23_SPOKEN_LAMAGUE/`, which carry 417 passing tests" was false
twice over:
- the 417 tests are in the runtime suites, `12_CORE_LANGUAGE_LINE/` and `22_`, not in
  `02_NATIVE36/` or `23_SPOKEN_LAMAGUE/`;
- `23_` is a measured negative, not a pass.

The register's HEADER is fixed in place. The same sentence is stamped into the ten CONJECTURE
files, which are sealed in `MASTER_MANIFEST`, so that correction is staged as a patch (§4).

### Regenerated register
`LAMAGUE_STATUS_REGISTER.json` was regenerated with the fixed deriver. Its formatting is
byte-compatible with the committed file (ensure_ascii, indent 2, no trailing newline; the
round-trip is identical). Changes:
- the date moves to 2026-10-22;
- `13_RETIRED` and `23_SpL` change to SCAFFOLD;
- two files that were never rated get entries: `LAMAGUE_SYNTHESIS.md` and the SXP-L independent
  audit;
- the stamped files gain +20 lines because of their stamp headers;
- the README is now 173 lines;
- `22` now has 5 `.py` files (it had 4).

The totals change from 36 entries to 38: CONJECTURE 10, INDEX 3, MEASURED 10, SCAFFOLD 15.
`test_committed_register_matches_a_fresh_derivation` now fails if the committed file and the
deriver drift apart.

---

## 2. `24_LAMAGUE_CHECK/lamague_check.py`: the accountability checker

**C1. Empty values counted as present (fixed).** These all counted as present: `False`, `True`,
`["TBD", ""]`, `{"who": "", "why": None}` and `[None]`. Booleans and None now count as empty, and
a container is empty when everything inside it is empty, checked all the way down.

**C2. Negated and part-word keys counted as the field (fixed).** `no_rollback` counted as
recovery, `without_dissent` as dissent, and `disclaim` as claim. A suffix now matches only on
whole words (split on `_` and camelCase), only when it is longer than four characters, and never
after `no`, `non`, `not` or `without`. `customer_affected_parties` and `postmortemRollback`
still match.

**C3. A nested placeholder could win over the record's own field (fixed).** When a field appears
more than once, the checker now takes the shallowest match, preferring a populated one and
taking exact names before suffix matches.

**C4. Wording.** The docstring said the field deletions were "proved"; it now says they were
"measured as detectable". The no-gaps line now says what the tool cannot check: "whether each
one is true is not something this tool can check."

**Documented limit, not fixed:** a nested dependency's `owner` can still stand in for
`authority`. The README now says this, and tells the reader to check `found as`.

**Parity:** the codec's `CRITICAL_FIELDS` and the checker's `FIELDS` are the same ten names. The
new test fails if they drift apart.

---

## 3. `02_NATIVE36/`: the validator accepts damaged registries

**MEASURED, with damaged copies:**
- the committed registry is VALID;
- reversed tokens and unknown seal tokens are rejected;
- these are ACCEPTED: deleting every compound seal, duplicating a seal, and blanking glyph names
  and descriptions.

The validator checks only that the REQUIRED keys are present, plus arity, provenance and
non-empty `failure_modes`.

The validator is sealed in `MASTER_MANIFEST`, so the fix is staged (§4). With the patch applied:
deleted seals, a duplicated `seal_id` and a blanked name each exit 1, and the committed registry
stays VALID.

**The YAML registry** is a projection of a subset of the data: 36 glyphs, 0 seals, and 8 fewer
keys per glyph. It disagrees on none of the values the two share. It is not a mirror, and it
does not conflict.

---

## 4. Staged patches (not applied: the targets are sealed or checksummed)

Each patch applies to HEAD with `patch -p1` and contains no CR bytes. The patched files match
the generator's output byte for byte (`cmp`).

| Patch | Targets | Witness |
|---|---|---|
| `RV15_NATIVE36_validator_seal_checks.patch` | `02_NATIVE36/validate_lamague_native36_v0.3.py` | Refuses empty seals, duplicate `seal_id`, and blank `name` / `class` / `spoken_form` / `type_signature` / `returns`. The committed registry stays VALID. |
| `RV15_CONJECTURE_header_evidence_sentence.patch` | The ten stamped CONJECTURE files (07, 09, 14–21) | Replaces the false "417 passing tests" sentence with the one now in the register header. All 10 files apply, plus the validator (11 files identical). |
| `RV15_CYCLE23_skip_unless_root.patch` | `25_RESEARCH_CYCLE_23…/tests/test_cycle23.py` and its `SHA256SUMS.txt` line | See F6. After the patch: `OK (skipped=8)`, and `sha256sum -c` verifies all 35 lines. Unpatched: `FAILED (errors=8)`. |

Applying them also needs a decision on `MASTER_MANIFEST` (G-RESEAL below).

### F6. Cycle 23's tests need root, and say so only by crashing
`prepare_world` calls `os.chown` on fixture directories to set other uids, which needs root.
Without root, all 8 tests raise PermissionError. The folder's own `reports/tests.txt` records
`Ran 8 tests … OK`, presumably from a root run.
**Status: DID NOT RUN (environment), not FAILED.** The patch turns the crash into an honest skip
that names the reason. The folder is also a register coverage gap: the register never rates
cycle 23.

---

## 5. `MASTER_MANIFEST` is stale and nothing enforces it

Paths were mapped by basename: 215 match and 14 do not. Every mismatch is explained by a later
commit:
- 10 CONJECTURE files were stamped in `1f5fabe` (2026-08-07);
- `10_essentials.md` was also changed by `cf6ff23` (2026-10-21, a Codex review note);
- both `equivalence.py` files changed in `ebc3352` (the `field` → `field_name` lint rename);
- `README_MASTER_CODEX.md` already differed at its first commit, `a6c901d`.

The manifest has been stale since 2026-08-01 and nothing checks it. **DERIVED:** a seal that
nothing verifies protects nothing, but it still blocks honest edits. This is Mac's decision.

---

## 6. Glyph and meaning census: the four questions RV15 named

**DERIVED from the files listed.** None of this is a code defect. Each item is a spec decision.

- **Ψ has more than one meaning, and the BNF admits it.**
  - Line 108 calls Ψ the "drift field".
  - Line 150 calls it "Consciousness / drift field".
  - Lines 218–220 give three readings by context: a drift/fold operator (TRIAD), a wave
    function (quantum) and a node state (graph).
  - Lines 287 and 300 make Ψ a *kernel operator* ("bounded linear operators on ℝⁿ").

  The grammar's `<field>` production and the parser treat Ψ only as a field. In short, one
  symbol is a field in the grammar and an operator in the kernel tier.
- **`Φ↑` and `Ψ_inv` have different types in different places.** Core v0.2 types `Φ↑` as
  `modify(Φ, ↑) : Field` and `Ψ_inv` as `qualify(Ψ, inv) : Invariant`. The parser makes both of
  them a field token with a modifier or subscript, so the Invariant type exists only in Core
  v0.2.
- **Native36 shares no glyphs with the others.** Its 36 base tokens are `0–9 A–Z`, with no
  Greek letters and no arrows. It is a separate alphabet: it cannot conflict with the BNF, and
  nothing maps one to the other.
- **The pipe character is overloaded in the BNF.** `|` is both BNF alternation and the
  object-language constraint separator (`… | C(Ψ_t) ≥ C(Ψ₀)`). There are 91 ` | ` occurrences,
  and only context tells the two uses apart. The batch-13 staged BNF patch already flags that
  the parser rejects the constraint form.
- **The middle dot appears nowhere.** There are 0 occurrences of `·` in the BNF, the three Core
  READMEs, the Native36 registry and the parser. Proposal 02's `Ao · Ψ` has no specification
  anywhere.

---

## 7. Tests added (working tree)

- `tests/test_lamague_check_aliases.py`: 8 new tests (C1–C3, parity, and the demo still gives
  6).
- `tests/test_lamague_register.py`: a new file covering F1–F4, the drift check from a fresh
  derivation, and controls.

**MEASURED:** on the HEAD archive, **16 failed and 12 passed**. Every failure is a defect test;
every pass is a control. On the working tree, **28 of 28 passed**.

---

## 8. Decisions for Mac (added this batch)

- **G-RESEAL.** Re-seal `MASTER_MANIFEST` at the current tree, retire it, or put it under a
  test. The three staged patches wait on this.
- **G-NEGATIVE.** Should the register get a "MEASURED-NEGATIVE" status? Spoken LAMAGUE is now
  SCAFFOLD under the existing rule, even though its verifier ran and gave a real, reproducible
  negative.
- **G-PSI.** Pick one meaning of Ψ for the grammar, and name the kernel-tier operator
  separately (or mark it as an overload).
- **G-INV.** Is `Ψ_inv` a field with a subscript (as in the parser) or an `Invariant` (as in
  Core v0.2)?

## 9. Status

- **RV15 is reviewed** at the boundary named at the top of this file.
- **Not checked:** the content of the ten CONJECTURE documents themselves. They are marked
  CONJECTURE, and checking them is RV16+ work.
- **Not checked:** what `spl.py` should do about the `an` ambiguity. That is a design choice,
  not a defect.
