# Progress — Sync Zone forge, 2026-11-06

**Objective:** investigate, formalize, falsify and minimally scaffold Cassian's Sync Zone
proposal, on evidence, without widening any authority.

**Branch / baseline:** `claude/youthful-volta-di3ma8` from `master` at
`c4d24c9a72200dc8fe4c29318d55c9127213c0dc` (the same commit the packet was researched on).
Workshop inspected read-only at `a41c2a79d70666f243d971ed8ca70c3a5723973f`.

## Inspected

`AGENTS.md`, `CLAUDE.md`, `WORKING_HOME.md`, `CONTRIBUTING.md`, root `README.md`,
`lycheetah/handoff.py`, `lycheetah/sovereign_harness.py`, `lycheetah/assurance/{__init__,gateway,finality,in_toto}.py`,
`lycheetah/compaction/codec.py`, `lycheetah/consensus/arena.py`, `19_MULTI_AGENT_CHORUS/` (ran it),
`18_EXPERIMENTAL/README.md` and `agent-role-hybridisation/{README,COMMON_CONTRACT}.md`,
`28_DEFENSE/FAILURE_MUSEUM.md`, `FOR-REVIEW/FULL_FRAMEWORK_REVIEW_CHECKLIST.md`,
`34_CYBERNETICS/LOOP_MAP.json`, `pyproject.toml`, `tests/test_chorus_honesty.py`.
Workshop: `README.md`, `CHARTER.md`, `ARCHITECTURE.md`, `.githooks/commit-msg`,
`commons/cross-seat-contracts.md`, `disputes/{README,LEDGER}.md`, disputes 400/700/1100/1200,
`code/24_*`, `code/26_*`, `tools/zone-check.mjs`, `tools/cold-boot-audit.py`, `evidence/predictions-ledger.md`.
Supplied: Cassian's packet 00–04 (SOURCES.md was referenced but not supplied) and Aetheron's dossier.

## Changed

New: everything under `18_EXPERIMENTAL/sync-zone-recursive-framework/`, `tests/test_sync_zone_cycle.py`.
Edited: `CHANGELOG.md` (new entry), `18_EXPERIMENTAL/README.md` (one inventory row).

## Tests — exact commands and outcomes

| Command (repo root, Python 3.13 venv) | Outcome |
|---|---|
| `python -m pytest -q -p no:cacheprovider` before any change | `1567 passed, 3 skipped, 2 xfailed` |
| `python -m pytest -q -p no:cacheprovider tests/test_sync_zone_cycle.py` | `66 passed` |
| `ruff check 18_EXPERIMENTAL/sync-zone-recursive-framework tests/test_sync_zone_cycle.py` | `All checks passed!` |
| Mutation probes M1–M8 (rule removed, focused suite rerun, source restored) | all 8 caught after strengthening; M4, M5 initially survived (SZF-05) |
| `python -m pytest -q -p no:cacheprovider` after | `1633 passed, 3 skipped, 2 xfailed` |
| `python3 -B experiments/retrospective_1100.py --write` | V1, V2, H1 invalid or unratifiable; V3 passes (the null result) |
| `python3 -B experiments/session_cycle.py --write` | see `records/SZ-0001_report.json`; its evidence E1–E3 are these checks rerun and bound to the candidate digest |
| Workshop: `node tools/zone-check.mjs` | `692 checks, 0 failures, 2 warnings` |
| Workshop: each `code/*test*.py` under pytest | `83 passed` total |
| Workshop: `python3 disputes/1100-.../run.py` | prints `VERDICT: FALLS` from typed-in formulas |

## Unresolved

See `SYNC_ZONE_FINDINGS.md`. Open: SZF-02 and SZF-04 in the workshop; SZF-07 stale checklist;
SZF-11 the contract cannot see circular evidence; SZF-12 push unavailable.

## Next concrete action

A different-model review of this branch (SZ-009), then the handoff-fidelity comparator
(SZ-010) with its prediction written down first.

## Needs Mac

Ratify/amend/reject `sz-rules-v0.1`; choose the reviewer; decide on the workshop disputes;
decide how the branch lands. Details in `README.md` → Decision memo.
