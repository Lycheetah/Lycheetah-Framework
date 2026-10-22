# BATCH 37 — RV01 · Whole architecture and the "third brain"

**Reviewer:** Sol (Claude Opus 5.5, xhigh) · **Date:** 2026-10-23 · **Branch:** `review/full-framework-2026-10-20`, working tree only, nothing staged or committed.

## Coverage, stated honestly

- **Read:**
  - `lycheetah/_bootstrap.py`, both bridge `__init__.py` files (`lycheetah/core/`, `lycheetah/applications/`), `lycheetah/__init__.py` imports, and the import block of `lycheetah/consensus/arena.py`.
  - The head of `lycheetah/assurance/runtime.py`.
  - Packaging in `pyproject.toml` (`packages`, `package-dir`, `scripts`).
  - The canonical `12_IMPLEMENTATIONS/core/__init__.py` and `applications/__init__.py`.
  - The `34_ASSURANCE_RUNTIME/action_guard/README.md` version table.
  - The `L-TRIAXIAL` entry of `34_CYBERNETICS/LOOP_MAP.json`.
- **Computed:**
  - The internal import graph of every tracked `lycheetah/*.py`.
  - Cross-tree imports from `34_ASSURANCE_RUNTIME/`, `examples/` and `papers/`.
  - A content-hash duplicate census of tracked `.py` files outside `99_ARCHIVE`.
  - A runtime census of files loaded under more than one module name.
  - A search for "third brain" in the tracked tree and in Mac's own working notes. Only the matching line was read, never the surrounding content.
- **DID NOT RUN:**
  - A wheel build and install. The bridge behaviour in an installed wheel is DERIVED from `package-dir`, not measured.
  - A diff of `lycheetah/assurance/checkpointed_workflow.py` against `action_guard/versions/v0.8/checkpointed_workflow.py`.
  - `ruff`. The review venv was lost in the machine reboot on 2026-10-23. The edited files were checked by the full test suite only.

## Findings

| # | Status | Finding |
|---|---|---|
| A1 | MEASURED | **"Third brain" names no component in the corpus.** `git grep` returns 0 tracked hits. The phrase appears only in the Caelorynth board, where it is recorded as Mac's request ("architectural soundness for the 'third brain'"), followed by a clarification question that is still unanswered. This review does not invent a referent. **Sol's reading (CONJECTURE):** the nearest live structure is `lycheetah/sovereign_harness.py`, the one module that joins the three package subsystems: `.assurance` decides, `.compaction` remembers, `.consensus` agrees. If Mac means the whole Framework as a third mind beside the two seats, that is an identity question, not a code component. G-RV01-1. |
| A2 | MEASURED | **One file was loaded as two Python modules, so the package's exported enum did not match its own reports.** `lycheetah/core/__init__.py` re-exported through a relative import, which loads `12_IMPLEMENTATIONS/core/tri_axial_checker.py` as `lycheetah.core.tri_axial_checker`. The implementation itself imports `core.tri_axial_checker`. **Known-bad:** on an AURA report whose statuses are all PASS, `report.tes_status == lycheetah.core.MetricStatus.PASS` was **False**, and `isinstance` was False too. The same split hit `SemanticExtractor` and `Extraction` inside `lycheetah.assurance.runtime`. Census: 4 files were loaded under 2 names each in one ordinary process. |
| A3 | MEASURED | **A third identity comes from `sys.path.insert` inside core modules.** Five core modules (`grey_mode`, `psi_consensus`, `seven_phase`, `unified_field_checker`, `aura_customizer`) put their own directory on `sys.path` and import siblings by bare name. As a result, `grey_mode.py` loads as both `grey_mode` and `core.grey_mode`. `RecoveryResult` and `GreyModeStatus` therefore exist twice: `GreyModeStatus` members are not equal across the copies, and `arena.py` annotates `core.grey_mode.RecoveryResult` while the monitor returns `grey_mode.RecoveryResult`. No `isinstance` or equality crossing was found in live code, so no wrong verdict was measured. This is a latent defect, not an observed failure. |
| A4 | MEASURED | **The full dotted path still makes a second copy.** `import lycheetah.core.tri_axial_checker` still loads the file under that name, because the bridge appends the canonical directory to `__path__`. Two tests use that form. The A2 repair fixes the **exported** names, not this path. Consolidation is G-RV01-2. |
| A5 | MEASURED | **Authority boundaries.** Only `lycheetah/` is imported by `examples/`. Nothing in the package imports `34_ASSURANCE_RUNTIME/` or `papers/`. Those trees are research lineages, and their `versions/v0.5–v0.8` import only their own siblings. The canonical algorithms live in `12_IMPLEMENTATIONS/`; the package maps them in through `package-dir` and `_bootstrap`. There is no recorded promotion link from `action_guard/versions/v0.8` to `lycheetah/assurance/action_guard.py`: no "promoted from" line in the code, and no version field. |
| A6 | MEASURED | **Duplicate implementations outside `99_ARCHIVE`.** They are byte-identical research snapshots, not live forks: <br>- 13 `lamague_runtime` files are identical across `06_RUNTIME_v0.2`, `07_RUNTIME_v0.3` and the `08` operator pack; <br>- `lamague_core` `core.py` and `errors.py` are identical across v0.1, v0.2 and v0.3; <br>- `frontier-controls/research_support.py` and `commit_fence.py` are mirrored into forge_v and forge_vi `upstream_mirror/`; <br>- earned-trust cycles 5–9 carry copies of their predecessors' fences. <br>None is imported by the package. They are honest as frozen snapshots, but none is marked "mirror of X at commit Y". |
| A7 | MEASURED | **Version contracts.** <br>- The package is `1.3.0`. <br>- The receipt has `SCHEMA_VERSION = "0.1"` and rejects other versions. <br>- The evaluation and regression schemas carry their own constants. <br>- The research lines carry versions in folder names only. <br>- The RV37 outbox defect (v0.9) sits in a research line that the package does not import, so the shipped `lycheetah.assurance.finality` is a separate implementation. It was not probed for the same pattern: UNVERIFIED, and named in G-RV01-3. |
| A8 | DERIVED | `pyproject.toml` lists the package `lycheetah.experiments`, mapped to `12_IMPLEMENTATIONS/experiments`, which has no `__init__.py`. Whether the wheel ships it as intended is UNVERIFIED, because no wheel was built. |

## The one diagram: data, evidence, approval, execution, recovery

```
  caller / agent
      │ action + context
      ▼
  lycheetah.assurance ── policy.py (rules) ── runtime.py ◄── core.semantic_extractor
      │  decide            evaluation/regression (evidence)    applications.aura_text_checker
      ▼                                                         (12_IMPLEMENTATIONS = canonical math)
  gateway.py ──► action_guard.py ──► checkpoint_authority.py (signed checkpoints, SQLite)
      │  approval bound to action        │
      ▼                                  ▼
  CommandExecutor (execution)      receipt.py → in_toto.py / otel.py  (evidence out)
      │
      ▼
  finality.py (evidence-capped admission)        recovery: checkpointed_workflow.py
                                                  replays from the last signed checkpoint
  sovereign_harness.py = assurance + compaction (memory: shield/codec)
                         + consensus (arena → core.psi_consensus / core.grey_mode)

  research lineages, never imported by the package:
  34_ASSURANCE_RUNTIME/action_guard/versions/v0.5→v0.8 · papers/agent-safety/frontier-controls v0.7→v1.0
```

## Repairs (working tree)

Backups are in the session scratchpad under `rv01_bak/`.

1. **`lycheetah/core/__init__.py`** and **`lycheetah/applications/__init__.py`**: both now re-export from the canonical `core.*` and `applications.*` modules, after `ensure_implementation_on_path()`. A dated RV01 comment explains why.
2. **`lycheetah/assurance/runtime.py`**: it imports `applications.aura_text_checker` and `core.semantic_extractor` by their canonical names, the same way `consensus/arena.py` already does, with a dated comment.
3. **`tests/test_package_module_identity.py`** (new), with three tests:
   - report statuses equal the exported `MetricStatus`;
   - the exported names are the canonical classes;
   - the runtime uses the analyser's extractor type.
4. **`34_CYBERNETICS/LOOP_MAP.json`**: the new test is registered as a known reader of `TriAxialChecker` under `L-TRIAXIAL`. The loop-audit gate correctly refused an unregistered reader.

## Witnesses

| Witness | Result |
|---|---|
| New test, live | 3 passed |
| **Known-bad:** the same test against the pre-fix three files (scratch copy) | **3 failed** |
| Full suite (one run, alone) | 1547 passed, 1 skipped, 1 xfailed; 1 failed: the loop map, before registration |
| `test_cybernetics.py` + new test after registration | 15 passed |
| `ruff` | DID NOT RUN (venv lost in the reboot) |

## G-items for Mac

- **G-RV01-1:** what is the "third brain"? (a) The whole Framework repository. (b) The sovereign harness: decide + remember + agree. (c) Something else you have in mind. The review left this open instead of guessing. **Sol leans to (b) as the code reading,** but your word decides it.
- **G-RV01-2:** consolidate import identity. Replace the five core modules' `sys.path.insert` + bare-name imports with `core.*` imports. Then make the bridges stop appending to `__path__`, or turn them into pure re-export shims. That ends A3 and A4. It touches canonical implementation files, so Sol proposes one batch with the full suite, not piecemeal edits.
- **G-RV01-3:** probe the shipped `lycheetah.assurance.finality` for the RV37 payload-binding pattern. A shipped package outranks a research line.
- **G-RV01-4:** mark mirrors. Add one line to each `upstream_mirror/` and duplicated runtime folder: "byte copy of <path> at <commit>; not authoritative".
- **G-RV01-5:** record promotion. Add a line to `lycheetah/assurance/action_guard.py`, or the 34 README, naming which research version it was promoted from.
