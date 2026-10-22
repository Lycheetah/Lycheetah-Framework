# Batch 13 — RV14: the LAMAGUE parser patch and grammar conformance

**Date:** 2026-10-22 · **Branch:** `review/full-framework-2026-10-20` · **HEAD:** `d7ae0ad`
**Reviewer:** Sol (Claude Opus 5.5, xhigh) · **Working tree only. Nothing committed or pushed.**

RV14 asks for five things:
- review the actual working diff of `12_IMPLEMENTATIONS/core/lamague_parser.py`;
- check complete consumption, unknown input, parentheses, precedence, associativity, modifiers, recursion and constraint validation;
- compare the parser and BNF proposals against `03_LAMAGUE_L1/04_BNF_GRAMMAR.md` and both parsers;
- treat "33 checks pass" as no proof that the added behaviour is covered;
- reconcile the approval text with Mac's actual authorization record.

"Both parsers" is read here as the committed parser (HEAD) and the patched one in the working tree. Each probe ran against three states:
- **HEAD**, from a `git archive`;
- **B1**, the parser as this batch found it: HEAD plus the batch-1 diff;
- **AFTER**, the parser after this batch's fixes.

The repo's eight other LAMAGUE parser modules belong to RV15 and are listed in §5.

## 1. Witnesses

| Witness | What it is |
|---|---|
| `repro_batch13.py <root>` | Probes C1–C3 (controls) and P1–P15, one JSON line each. It loads the parser by path and never writes to `<root>`. |
| Parser sha256 prefixes | HEAD `93eaf11dbd22e46b` · B1 `96691fac9ed138bd` · AFTER `73cde1aaf9b92079` |
| `tests/test_lamague_parser_conformance.py` | 26 new `active` tests. Each one is a defect test or a named control. |
| Corpus census | Every markdown span in the repo that contains a LAMAGUE operator and a field or invariant symbol, validated by B1 and by AFTER (§5). |
| Aetheron's `lamague_check` wrapper tests | Run on a scratch copy. They load the repo parser by its default absolute path, so they ran against AFTER (§4). |

## 2. Findings and actions

| ID | Finding | HEAD | B1 | AFTER | Label |
|---|---|---|---|---|---|
| R14-01 | The subscript scanner stopped only at a fixed list of characters. It swallowed `↯`, `↑`, every unknown symbol and punctuation into the name: `Ψ_inv↯Ao`, `Ψ_inv@#$` and `Ao_x;y` were each **one valid field**, and an unknown symbol hidden in a subscript skipped the unknown-symbol check. `Ψ_` (empty subscript) was valid. | defect | defect | **fixed** — the body is letters and digits only. Anything else ends it and is tokenized on its own. A bare `_` is an unknown symbol. | MEASURED (P1, P15) |
| R14-02 | A subscript attached to nothing was a valid leaf: `_inv`, and `Ao → _x`. | defect | defect | **fixed** — refused with "Subscript '_x' is not attached to a symbol". | MEASURED (P15) |
| R14-03 | Only space, tab and `\n` counted as whitespace. `\r`, which every CRLF file in this repo contains, and NBSP (U+00A0) were reported as "Unknown symbol". | defect | defect | **fixed** — `str.isspace()`. | MEASURED (P9) |
| R14-04 | Nested parentheses raised an uncaught `RecursionError`: at depth 497 on HEAD and 496 on B1 (recursion limit 1000). | defect | defect | **fixed** — nesting over `MAX_NESTING = 64` is refused with an error. A depth of 4096 now returns a clean error. | MEASURED (P10) |
| R14-05 | A 1500-operator chain validated, but `tree.symbols()` and `tree.to_dict()` then raised `RecursionError`, because the tree is left-deep. The validator handed back a tree its own methods could not walk. | defect | defect | **fixed** — more than `MAX_OPERATORS = 256` operators is refused before parsing, so no tree is returned. | MEASURED (P11) |
| R14-06 | A node's `.value` dropped parentheses. `(Ao → Φ) → Ψ` and `Ao → (Φ → Ψ)` built different trees but rendered as the same string, and reparsing that string always built the left tree. | defect | defect | **fixed** — a composition written in parentheses keeps them in `.value`. A test checks that both forms round-trip to the same tree. | MEASURED (P7) |
| R14-07 | `CompressionMeasurer.build_expansion` rendered every operator as "→ transforms to:", so fusion (⊗), exchange (⇌), recursion (⟲) and collapse (↯) all read as projection. On HEAD, ↯ was the exception, because it was a DYNAMIC token. | defect | defect | **fixed** — each operator uses its own entry in `LAMAGUE_EXPANSIONS`. The compression ratios do not change (2.9 and 10.87, SAME), because `measure()` counts the supplied English, not the expansion. | MEASURED (P13, P14) |
| R14-08 | `Parser.LEAF_TYPES` listed `FIELD` twice and was never used. `_parse_leaf` repeated the same class map inline. This was batch-1 finding F04. | — | — | **fixed** — one `LEAF_CLASSES` table. | MEASURED |
| R14-09 | The module docstring cited `03_LAMAGUE_L1/BNF_GRAMMAR.md`, which does not exist (the file is `04_BNF_GRAMMAR.md`). It also presented the BNF as the grammar it implements, although it accepts a different one (§3). | defect | defect | **fixed** — the docstring now states the grammar actually accepted, the limits, where it departs from the BNF, and the measured compression figures, labelled as a demonstration on five examples. | MEASURED |
| R14-10 | `TokenType.DYNAMIC` is never produced. Since batch 1, ↯ is an OPERATOR, ↑ a MODIFIER and the other dynamics are OPERATORs. | — | unreachable | left in place. Removing an enum member is an API change, and it costs nothing. | MEASURED (P3) |
| R14-11 | `Ao↑`: HEAD **silently dropped** the ↑ (valid, parsed as `Ao`). B1 and AFTER refuse it as trailing input, because `Ao` has no ↑ merge while Ψ, Φ, S and Δ do. | silent drop | refused | refused (unchanged). Whether `Ao↑` means anything is grammar decision G5. | MEASURED (P4) |
| R14-12 | `Φ_inv↑` (↑ after a subscript) was valid on HEAD and B1 only because R14-01 swallowed the ↑ into the name. It is now refused as trailing input. The form the corpus uses is `Φ↑_inv`, which still parses. | accidental | accidental | refused. G5. | MEASURED (P1, P6) |

**Unchanged by this batch:** the controls C1 (canonical cycle valid) and C3 (newline is whitespace), P5, P13, and batch 1's own changes (C2, P2, P3, P8, P12). MEASURED, three-way.

## 3. Grammar decisions for Mac (G1–G7)

The parser and `04_BNF_GRAMMAR.md` are different grammars. This batch did not choose between them.

- **G1 — what ↯ is.** The BNF lists ↯ only as a `<dynamic>`, and its prose table calls it a *Junction* with the form `condition ↯ [option_a], [option_b]`. Batch 1 made it a binary operator, so `Ψ ↯ Ao → Φ↑ → Ψ_inv` reads as `((Ψ ↯ Ao) → Φ↑) → Ψ_inv`. Before batch 1, HEAD parsed that line as just `Ψ` and dropped the rest without a word.
- **G2 — precedence and associativity.** The BNF's `<composition> ::= <expression> <operator> <expression>` is ambiguous: it gives no precedence and no associativity. The parser uses one flat level, left-associative, so `Ψ → Ao ⊗ Φ` is `((Ψ → Ao) ⊗ Φ)` (P8).
- **G3 — dynamics standing alone.** The BNF makes `→ ⊗ ⇌ ⟲` complete expressions, because each is a `<dynamic>`. The parser refuses all four on their own but accepts a lone `↑` as a "modifier" leaf (P2).
- **G4 — the constraint language.** The parser validates each segment after `|` as an ordinary expression (batch 1). The BNF's own canonical line, `Ao → Φ↑ → Ψ → Ψ_inv | C(Ψ_t) ≥ C(Ψ₀)`, uses `C(…)` and `≥`, which neither grammar defines, so the parser rejects it (P5).
- **G5 — compounds.** `↑` and `_subscript` exist in the parser, not in the BNF. Open questions: `Ao↑`, `↑` after a subscript, and a lone `↑`.
- **G6 — `·`.** Proposal 02 adds `·`. The parser does not know the symbol (P6).
- **G7 — the BNF cannot derive its own examples.** In lines 17–50 no production yields `Φ↑` or `Ψ_inv`, so the canonical TRIAD cycle `Ao → Φ↑ → Ψ_inv` is not in the language the BNF defines. The same section still says "[ACTIVE] — grammar is formally specified and parseable". DERIVED from the grammar text.

## 4. Proposals, the "33/33" receipt, and authorization

**Proposal 01 (parser silent-drop patch).**
- Its header says APPROVED/IMPLEMENTED; its footer says "Awaiting".
- Its diff does not apply to HEAD: both hunks fail, and its context lines appear zero times in HEAD's file (MEASURED, earlier in this batch).
- The behaviour it describes is in the working tree: ↯ is an operator and input must be consumed completely (P3, C2, P12; MEASURED).
- So the change exists, but not as that diff.

**Proposal 02 (BNF harmonization).**
- Its diff is malformed: `patch` stops with "unexpectedly ends in middle of line".
- Its "Zero Runtime Breakage" claim is false against the parser: `·` is an unknown symbol, and its `<field_expr>` excludes `Φ↑_inv`, which the parser accepts (P6; MEASURED).

**"33/33" — correction to my own interim note.** Earlier in this batch I took the 33 tests to belong to the decision-record checker. **RETRACTED.** Two different tools share the name `lamague_check`:
- `03_LAMAGUE_L1/24_LAMAGUE_CHECK/lamague_check.py` (in the repo) checks JSON decision records for accountability fields. It belongs to RV15 and is not a LAMAGUE parser.
- `~/AETHERON-ANTIGRAVITY-FORGE/creations/lamague_check/` (Aetheron's forge, outside the repo) is a command-line wrapper around this repo's `lamague_parser.py`. The 33 tests are there.

**What the 33 actually cover.** MEASURED today: **33 passed**, run from a scratch copy, against the AFTER parser through the wrapper's default absolute path.
- The tests cover the wrapper: exit codes, JSON shape, the trailing-input check, explain and measure, and two mutation tests of the wrapper itself.
- Two of them touch batch-1 parser behaviour: `test_upstream_natively_rejects_trailing_input` and `test_examples_all_valid_after_patch`.
- None covers subscripts, whitespace, nesting depth, grouping, precedence or how many operands ↯ takes.
- So the 33 are a real pass for the wrapper, and evidence that this batch did not break it. They are not coverage of the parser's added behaviour.

**Aetheron's README contradicts itself.** I reported this rather than editing it, because the forge is another seat's workspace.
- Lines 60–65 say the upstream parser "silently ignores whatever follows".
- Line 72 says the same defect was patched and is "RESOLVED".
- Lines 67–68 say the upstream parser does not grammar-check `|` constraints, but batch 1 made it check them.
- Lines 109–112 say integration "waits for … Mac's go-ahead".

**Authorization.** The only written claims that Mac authorized the batch-1 parser patch are:
- Aetheron's README line 72: "[RESOLVED 2026-10-21 by Mac's authorization]";
- proposal 01's header.

I found no record in Mac's own hand. I searched `FOR-REVIEW/` and the Caelorynth evidence JSON. This does not show the patch was unauthorized; it shows the record that would prove authorization is missing. **Mac decides:** confirm it and record the date, or treat the batch-1 parser diff as unapproved.

## 5. Corpus regression census and the parser count

**Regression census.** It covered 252 distinct markdown spans that contain a LAMAGUE operator and a field or invariant symbol.
- B1 accepts 8 of them; AFTER accepts 7. No span went from invalid to valid.
- The one span lost is `Ao → Φ↑ → Ψ_inv;`, a LAMAGUE Core statement whose `;` is a statement terminator (`12_CORE_LANGUAGE_LINE/…/docs/MIGRATION_v0.1_TO_v0.2.md:8`). B1 accepted it only because R14-01 swallowed the `;` into a field named `Ψ_inv;`. Refusing it is correct for this expression parser. MEASURED.
- The other 244 spans are mostly prose, code, and statements in other LAMAGUE dialects; letters dominate the unknown symbols. The span filter is deliberately loose, so this is a regression census, **not** a measure of the corpus's notation.

**Eight other LAMAGUE parser modules.** The repo holds eight besides this one:
- three in the Core language line (`12_CORE_LANGUAGE_LINE/…/lamague_core/parser.py`, v0.1, v0.2, v0.3);
- three identical-size runtime parsers (`06_RUNTIME_v0.2…`, `07_RUNTIME_v0.3…`, `08_EXPERIMENT_001…/OPERATOR_PACK`);
- two in `13_RETIRED_KERNEL_BRANCH`.

Whether these are one grammar or several is the "one truth" question for RV15.

## 6. Collateral: batch 12 left a red it never saw

This batch's single full-suite run reported **1 failed**: `tests/test_cybernetics.py::test_every_loop_matches_the_map`, with the message "new reader of TriAxialChecker: FOR-REVIEW/2026-10-22_OPUS_REVIEW/repro_batch12.py — map stale; check whether it acts on the verdict". MEASURED.

- **Cause.** The reader it flagged is my own batch-12 probe. Batch 12's receipt ran a 30-file focused set that did not include `test_cybernetics.py`, so it never saw the failure.
- **Fix.** I added the probe to `L-TRIAXIAL.known_callers` in `34_CYBERNETICS/LOOP_MAP.json`. Batch 2 used the same route for a test caller. The probe reads `TriAxialChecker` reports and prints them; it never applies a repair. So the entry's `who_acts` ("nobody in code") stays true, and no claim in the map moves. After the fix, `test_cybernetics.py`: 12 passed.
- **Process rule from here.** A focused set cannot see the repo-wide census gates. Every batch ends with one full-suite run.

## 7. Staged, not applied

`RV14_04_BNF_GRAMMAR_parser_status.patch` makes two changes to `04_BNF_GRAMMAR.md`:
- a parser-status note under the canonical expression, saying the parser rejects the constraint clause;
- a replacement for the stale IMPLEMENTATION note, which says "A formal parser for the BNF grammar above is a future implementation task" in a file that cites `lamague_parser.py`'s measurements 140 lines earlier.

It is staged rather than applied for two reasons:
- the file is recorded in `03_LAMAGUE_L1/MASTER_MANIFEST.sha256.json`, and the current file still matches that record (`4db56603…`);
- `LAMAGUE_STATUS_REGISTER.json` lists it as SCAFFOLD.

Applying the patch makes the manifest stale. No test enforces the manifest, which I checked by grep.

The patch applies to HEAD with `patch -p1`, and the result is byte-identical to the generated file. It has no CR bytes. MEASURED.

## 8. Changed paths (batch 13)

| Path | Change |
|---|---|
| `12_IMPLEMENTATIONS/core/lamague_parser.py` | R14-01 to R14-09 |
| `tests/test_lamague_parser_conformance.py` | new, 26 tests |
| `34_CYBERNETICS/LOOP_MAP.json` | one `known_callers` line (§6) |
| `FOR-REVIEW/2026-10-22_OPUS_REVIEW/repro_batch13.py` | new probe |
| `FOR-REVIEW/2026-10-22_OPUS_REVIEW/RV14_04_BNF_GRAMMAR_parser_status.patch` | new, staged |
| `FOR-REVIEW/2026-10-22_OPUS_REVIEW/BATCH12_FINDINGS_AND_LEDGER.md` | records that every default `sol_workspace_mcp` target is missing on this machine |
| this ledger | new |

**Not touched:** `04_BNF_GRAMMAR.md`, both proposals, Aetheron's forge, and `24_LAMAGUE_CHECK`.

## 9. Verification

| Check | Result | Label |
|---|---|---|
| New tests on a HEAD archive | **17 failed, 9 passed**. The 9 are the 3 ordinary-subscript controls, the ordinary depth/length control, the 4 subscript-stop cases HEAD already handled (`→ ⊗ ⇌ ⟲`), and ↯'s expansion, which HEAD rendered correctly only because ↯ was then a DYNAMIC | MEASURED |
| New tests on the B1 state | **18 failed, 8 passed**. ↯'s expansion now also fails, because batch 1 made ↯ an OPERATOR | MEASURED |
| `test_lamague_parser.py` + conformance, working tree | **50 passed** | MEASURED |
| Aetheron wrapper suite against AFTER | **33 passed** | MEASURED |
| Full suite, before the LOOP_MAP fix | 1 failed (§6), 1442 passed, 1 skipped (`test_mcp_guard`, needs MCP SDK 2.x), 1 xfailed | MEASURED |
| Full suite, final | 1443 passed, 1 skipped, 1 xfailed, 1 warning in 85.66s (0:01:25) | MEASURED |
| Line endings | The parser, new test, LOOP_MAP, BNF and patch are all LF with 0 CR bytes, as HEAD's parser was | MEASURED |

## 10. What this does not show

- That the parser matches the BNF. It does not, and cannot until G1–G7 are decided.
- That 256 operators and 64 nesting levels are the right limits. They are my choice.
  - Why they are safe: each nesting level costs about two stack frames, and tree depth is at most the operator count. Both stay far below the default recursion limit of 1000. DERIVED.
  - No corpus span reached either limit (§5).
- Anything about LAMAGUE's compression. The 2.9:1 and 10.9:1 figures come from five examples the parser's author chose, each with English the author wrote.
- The eight other parser modules and `24_LAMAGUE_CHECK`. Both are RV15.

## 11. Open decisions added for Mac

1. Grammar: G1 to G7 (§3).
2. The batch-1 parser diff: confirm the authorization and record it, or withhold it (§4).
3. The staged BNF patch: apply it and re-seal the manifest, or leave it (§7).
4. The parser limits: keep 256 operators and 64 nesting levels, or set others.
5. Aetheron's README contradictions: pass them to Aetheron by your hand (§4).
