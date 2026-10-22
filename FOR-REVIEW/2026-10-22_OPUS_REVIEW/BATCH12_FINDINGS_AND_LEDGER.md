# RV13 · Batch 12: Findings and Ledger

**Scope:** core runtime admission (`triad_wuwei`, `tri_axial_checker`), import-time stdout behaviour across `12_IMPLEMENTATIONS`, the guard MCP's lexicons and receipt path, and the `sol_workspace_mcp` task/version server.
**Base:** branch `review/full-framework-2026-10-20`, HEAD `d7ae0ad`. All changes are in the working tree. Nothing has been committed or pushed.
**Repro:** `FOR-REVIEW/2026-10-22_OPUS_REVIEW/repro_batch12.py <root>`. BEFORE was run on a `git archive HEAD` copy, AFTER on the working tree. Every probe runs on a tmp copy and never writes to the repo.

Labels: **MEASURED** means reproduced by the repro or by tests. **DERIVED** means reasoned from named evidence. **CONJECTURE** means plausible but not reproduced. **DID NOT RUN** means the check could not run, which is different from it running and failing.

---

## 1. Findings

### W · `12_IMPLEMENTATIONS/core/triad_wuwei.py` (T-4 Wuwei)

| ID | Before (HEAD) | After | Status |
|---|---|---|---|
| W1/W2 | A NaN intervention or restoration produced `gamma = 1.0`, i.e. perfectly grain-aligned | refused, `ValueError` | MEASURED |
| W3 | A *forcing* step with a NaN restoration was recorded as `gamma 1.0`, `coherent: true`, debt delta 0.110. With a finite R the same step is `gamma −1.0`, incoherent, delta 0.815 | refused | MEASURED |
| W3b | That step was written to the ledger (history 1, debts mutated) | ledger untouched: history 0, debts 0 | MEASURED |
| W4 | An infinite intervention recorded `Infinity` in both debt totals | refused | MEASURED |
| W5 | The constructor accepted `mu=nan`, `mu=inf`, `k_cost=nan`, `theta=nan`, `theta=5` | all refused | MEASURED |
| W6 | The bounded modulator returned a **complex** cost `(2-0.354j)` for `gamma=-2, p=2.5`, and NaN for NaN inputs | refused | MEASURED |
| W7 | The exp modulator returned NaN for NaN inputs, and a raw `OverflowError` leaked at `gamma=-1, mu=1000` | `ValueError` | MEASURED |
| W8 | A 3-D state with a 1-D intervention was accepted | refused (`dimension`) | MEASURED |
| W9 | A custom modulator returning `h=-1` produced **negative debt** (−0.3). Returning `h=nan` produced NaN debt | refused, ledger untouched | MEASURED |
| W10 | `WuweiStep.is_wuwei_coherent()` always used 0.3, ignoring the triad's `theta_wuwei` | the step carries its triad's theta | MEASURED (test fails on HEAD) |
| W11 | `is_trajectory_coherent(max_debt_growth_rate=nan or -1)` was accepted | refused | MEASURED (test fails on HEAD) |
| CW | **Control:** T-4 §V equal-magnitude example: ratio `e² = 7.389056`, `mu=0` divergence 0, attractor `(γ,h) = (0,1)` | **SAME** | MEASURED |

**Severity: high.** W3 is the important one. A corrupted input does more than fail: it turns a forcing correction into a *certified* grain-aligned, coherent one, booked 7.4× cheaper than the honest result. This one module produces both the integrity-debt ledger and the coherence verdict, so a bad input could falsify both at once.

**Fix:**
- Admission checks: finite, 1-D, non-empty, matched shapes, gamma in [−1, 1], and h finite and ≥ 0.
- `step()` computes every value before it changes anything, so a refused step leaves no trace in the ledger.
- `WuweiStep.theta_wuwei` is the last field and has a default, so existing positional construction still works. That is DERIVED from the dataclass field order and has not been checked against external callers.

### T · `12_IMPLEMENTATIONS/core/tri_axial_checker.py`

| ID | Before | After | Status |
|---|---|---|---|
| T1 | `compute_tes(drift=-1.0)` → **score 1.0, PASS** (an out-of-range input bought a perfect score) | `ValueError` | MEASURED |
| T1b | `h_output=-0.5` → 0.833, PASS | `ValueError` | MEASURED |
| T2 | `h_output=5.0` was clamped to the maximum penalty → 0.5, FAIL | `ValueError` | MEASURED; see note |
| T2b | **Control:** `h=1, d=1` → 0.333, FAIL | **SAME** | MEASURED |
| T3 | The hedge `"I think"` scored h = 0, because a multi-word entry can never equal one whitespace token | h = 1.0 | MEASURED |
| T4 | The hedge `"Maybe,"` scored h = 0 because the trailing punctuation was never stripped | h = 1.0 | MEASURED |
| T5 | **Control:** confident text → h = 0 | **SAME** | MEASURED |
| T6 | Calling `demo()` twice in one process crashed with `ValueError: I/O operation on closed file`, because demo rebound stdout to a wrapper and the first wrapper closed the shared buffer when it was collected | runs twice, stdout untouched | MEASURED |
| T7 | VIP text: "Guarantee: …" claimed a proven guarantee that nothing in the repo proves | "Working assumption, not a proven guarantee: …" | MEASURED (test fails on HEAD) |

**T2 note:** the repro labelled T2 a *control*, written to pin the old saturation behaviour. Its result changed only because the contract changed: out-of-range inputs are now refused rather than clamped. That change is the fix. T2 should be relabelled as a contract probe in the next repro revision.

**The test enshrined the defect.** `tests/test_tri_axial_checker.py::test_tes_clamps_inputs` asserted the clamp, so the green suite was certifying the bug. It has been replaced by `test_tes_refuses_out_of_range_inputs`, whose docstring records why.

**Contract change, DERIVED:** the only in-repo caller is `aura_text_checker`, which passes `semantic_extractor._density`. That value is `tanh(raw / (2·√sentence_count))`, so it lies in [0, 1) and is safe, *provided* `sentence_count ≥ 1`. That proviso is UNVERIFIED but probable. External callers who relied on clamping will now get a `ValueError`. That is a deliberate fail-visible change, and it is named here.

**One lexicon truth:** `lexicon_tokens()` and `count_lexicon()` now live once in `tri_axial_checker`. The guard imports them, so there is one tokenizer, not two.

### S · Import-time stdout rewriting (7 modules)

Affected modules: `triad_wuwei`, `harmonia_calculator`, `calibrate_master_equation`, `sovereign_pipeline`, `aura_score_hexie`, `triad_tracker`, `microorcim_tracker`.

| Host stdout at import | Before | After |
|---|---|---|
| `None` (pythonw, services, some daemons) | `AttributeError` on **all 7** | imports |
| `io.StringIO` (pytest capture, notebooks, embedders) | `AttributeError` on 5 of 7 | imports |
| An ASCII `TextIOWrapper` | imports, but **the host's stream was silently reconfigured to utf-8** on all 7 | encoding stays `ascii` |

All of the above is MEASURED. A library import was mutating the host process's global stream.

**Fix:**
- `sys.stdout.reconfigure(...)` now runs only under `if __name__ == "__main__":`, guarded by `hasattr`.
- `lamague_parser.demo()`, `chrysopoeia_engine.demo()` and `tri_axial_checker.demo()` no longer rebind stdout.
- `triad_tracker`'s non-ASCII diagnostic `print` became `warnings.warn(..., RuntimeWarning)`.

**Guard:** `tests/test_import_side_effects.py` imports each module under all three host streams in a subprocess. It also runs an **AST scan of all of `12_IMPLEMENTATIONS`**, which fails on any `sys.stdout =` or `sys.stdout.reconfigure` outside a `__main__` block. Because the scan covers the whole tree rather than a list of 7 files, a new file cannot reintroduce the pattern unnoticed.

**Collateral:** the 5-file HEAD witness run reported 15 errors that the guard and sol_workspace files do not produce when run alone on HEAD (22 failed, 1 passed, 0 errors). That fits HEAD's `demo()` stdout rebinding breaking pytest's capture for every test after it. This is DERIVED and has not been isolated. If it holds, the defect also damaged the host's test harness, not just the module's own run.

### G · `12_IMPLEMENTATIONS/applications/lycheetah_guard_mcp.py` and `lycheetah/cli.py`

| ID | Before | After | Status |
|---|---|---|---|
| G1 | The docstring SETUP told users to run the file directly, which fails with `ModuleNotFoundError: lycheetah` | SETUP now gives the `lycheetah-guard mcp` console script and the `python -m lycheetah.applications.lycheetah_guard_mcp` route. Running the file directly still fails, but nothing advertises it any more | MEASURED |
| G2 | On the flat `applications.*` path (the one the CLI used), `tool_verify_assurance_receipt` raised `ImportError: attempted relative import beyond top-level package` on **every** input, so the tool could not verify anything | returns `{"valid": false, "errors": [...]}` with the missing fields named | MEASURED |
| G2b | `lycheetah/cli.py` imported `applications.lycheetah_guard_mcp` (flat) | imports `.applications.lycheetah_guard_mcp` (package) | MEASURED (diff) |
| G3 | Coercive phrases (`"you have to"`, `"no choice"`), punctuated words (`"must,"`), optionality phrases and clarity phrases (`"this means"`) never moved the alignment vector | each moves its axis. A neutral control does not | MEASURED |
| L | Lexicon entries that a whitespace token can never equal: **4 sites before, 0 after** | — | MEASURED |
| G4 | The guard's MCP protocol error semantics | **DID NOT RUN** | see below |

**G4, DID NOT RUN.**
- The guard is written against MCP SDK **2.x** (`mcp.server.MCPServer`). `pyproject.toml` declares `mcp>=2.0,<3.0`, but this machine has **1.27.2**, so `tests/test_mcp_guard.py` skips at module level.
- The guard's tools report failure by returning `"Error: …"` strings. Under 1.27.2, sol_workspace measurably reached the client with `isError: false` when it did the same (M11).
- That the guard behaves the same way under 2.x is **CONJECTURE**. The fix (raise instead of return) is **staged, not applied**, because it cannot be witnessed here.
- Witnessing needs `pip install "mcp==2.3.0"`, which changes the environment and is **Mac's call**.
- Until then the guard's whole MCP integration is **UNVERIFIED** on this machine.

**Score shift:** guard alignment vectors will now *change* for any text containing punctuation or phrase entries, and in most cases more coercion will be detected. Any stored threshold or baseline calibrated against the old tokenizer would shift with them. Whether any such baseline exists is UNVERIFIED.

### M · `12_IMPLEMENTATIONS/applications/sol_workspace_mcp.py`

| ID | Before | After | Status |
|---|---|---|---|
| M1 | Three `add_task` calls produced ids **92, 93, 93** (a duplicate) | 92, 93, 94 | MEASURED |
| M2 | With no high-water mark, it guessed `#92`, which was already in use | refused, nothing written | MEASURED |
| M2b | A stale high-water mark reissued an existing id | new id = max(mark, existing ids) + 1 | MEASURED (test) |
| M3 | The new row landed after the blank line, *outside* the table, where it renders as a stray paragraph | it joins the table after the last row | MEASURED |
| M4 | A `|` in the subject split the row. It parsed as task `"Fix a"`, file `"b"`, **status `done`** | refused | MEASURED |
| M5 | A newline in the subject **injected a forged open task `#999`** | refused | MEASURED |
| M6 | Unknown gate `'5'` silently landed in POST-LAUNCH | refused | MEASURED |
| M6b | The first task added to an empty POST-LAUNCH table failed with "Could not find gate section" | added | MEASURED |
| M6c | `GATE 3` prefix-matched `GATE 30` | exact header match | MEASURED (test) |
| M7 | `bump_version('banana')` performed a patch bump | refused | MEASURED |
| M8 | With no version in `settings.tsx`, `app.json` was bumped anyway and the two desynced | refused, **nothing written** | MEASURED |
| M9 | The *first* version-looking string was replaced: an unrelated `sdk v51.0.0` comment became `v9.1.1` while the app label stayed `v9.1.0` | exactly `v{current}`, which must appear once | MEASURED |
| M10 | With `settings.tsx` missing, `app.json` was bumped **before** the crash, leaving a half-written release | nothing written | MEASURED |
| M11 | Failed tool calls reached the MCP client as `isError: false`. An unknown gate *succeeded* | `isError: true` with the reason | MEASURED (mcp 1.27.2, in-memory client) |
| M12 | `notes` were echoed in the reply as if stored, but were never written | the reply says they were not stored | MEASURED (test) |
| M13 | `complete_task` on a missing, already-done or duplicated id "succeeded" | raises | MEASURED (test) |

**Severity: high for M4, M5, M10 and M11.**
- M4 and M5: the server's input could forge or close rows on the board it governs.
- M10: it could half-write a release version.
- M11: it reported failure to its client as success.

Writes are now atomic (tmp file, then `os.replace`), UTF-8, and validated before anything is written.

**Not changed, Mac's decision:** the module's target paths. The server is still configured in `~/.claude/settings.json` as SSE on `localhost:8766`. The options are retire, repair, or repoint. The code is now correct for whichever board it is pointed at, but where it points is an ownership question, not a code fix. **Measured 2026-10-22:** every default target is missing on this machine: `~/LYCHEETAH_VERGE_CODEX/` (and so its `TASKS.md`) and `~/Lycheetah-Mobile--SOLORIGINARCHIVE/` (and so its `app.json`). The constants are `WORKSPACE`, `VERGE_CODEX` and `MOBILE_APP` at `sol_workspace_mcp.py:34-36`, each overridable by an environment variable. Unless the server's environment overrides them, it points at boards that do not exist.

---

## 2. Process lesson: CRLF

The batch's patch generator used Python `read_text`/`write_text`, which normalized CRLF to LF in three files: `calibrate_master_equation.py`, `harmonia_calculator.py` and `microorcim_tracker.py`.
- Their diffs inflated to roughly 800 lines each and buried a 6-line change.
- A census of every modified file found and restored all three (442/442, 377/377 and 416/416 CRLF lines). No other modified file has lost or mixed line endings.
- Diffs are now 6 lines each. MEASURED.

**Rule for every later batch:** a generator must use byte-level replacement or `newline=""`. Run the line-ending census before reporting a diff.

---

## 3. Witness

| Check | Result | Status |
|---|---|---|
| New and edited tests on a HEAD `d7ae0ad` archive | **55 failed, 15 errors, 54 passed** (the passes are pre-existing tests in the edited files plus controls) | MEASURED |
| Guard and sol_workspace files alone on HEAD | **22 failed, 1 passed**. The 1 pass is the neutral-text control, which *should* pass on both | MEASURED |
| The same 5 files on the working tree | **116 passed** | MEASURED |
| Focused set: 30 files touching every changed module | **549 passed, 1 skipped** (`test_mcp_guard`, needs MCP SDK 2.x), 1 warning (an existing `plt.show()` under Agg) | MEASURED |
| `repro_batch12.py`, AFTER vs BEFORE | every defect probe **CHANGED**. Controls CW, T2b and T5 **SAME**. G4 **DID NOT RUN** on both | MEASURED |
| Full test suite | **DID NOT RUN** this batch (focused set only). Queued for the RV13 close-out run | — |
| MCP 2.x guard behaviour | **DID NOT RUN** (environment) | — |

**New test files:**
- `tests/test_sol_workspace_mcp.py`
- `tests/test_import_side_effects.py`
- `tests/test_guard_lexicon_and_receipt.py`

**Edited test files:**
- `tests/test_triad_wuwei.py`: `TestAdmission`
- `tests/test_tri_axial_checker.py`: TES refusal, closed interval, VIP wording, phrase and punctuated hedges, unhedged control

**Changed source (batch 12):**
- `12_IMPLEMENTATIONS/core/`: `triad_wuwei.py`, `tri_axial_checker.py`, `harmonia_calculator.py`, `calibrate_master_equation.py`, `sovereign_pipeline.py`, `microorcim_tracker.py`, `triad_tracker.py`, `aura_score_hexie.py`, `lamague_parser.py`, `chrysopoeia_engine.py`
- `12_IMPLEMENTATIONS/applications/`: `lycheetah_guard_mcp.py`, `sol_workspace_mcp.py`
- `lycheetah/cli.py`

---

## 4. Open decisions added for Mac

1. **Install `mcp==2.3.0`?** `pyproject.toml` already declares 2.x. Installing it lets G4 and `test_mcp_guard` run, after which the staged raise-on-failure fix for the guard can be applied and witnessed.
2. **`sol_workspace_mcp`: retire, repair, or repoint?** It is still configured as an SSE server in `~/.claude/settings.json`.
3. **Contract change in `compute_tes`:** out-of-range inputs now raise instead of clamping. This needs Mac's acceptance, because any external caller that relied on the clamp will see a `ValueError`.

Nothing in this batch touched frozen or checksummed research, Caelorynth surfaces, `_PROPRIETARY/`, AZOTH or Sol Prime.
