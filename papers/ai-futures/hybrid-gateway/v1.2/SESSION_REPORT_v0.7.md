# Cycle 7 Report — Canonical-CASCADE Boundary and Historical Query Audit

**Date:** 2026-10-18 (NZ)  
**Starting point:** archived v0.6; all 120 old tests passed before changes.  
**Result:** 138/138 Python `unittest` tests passed on Python 3.13.5; 18 new tests. Prior source, contract, coverage, atomic SQLite and evaluation components preserved unchanged, except `cascade_bridge.py` strengthened and public exports extended.

## Built and validated

1. Pinned opt-in canonical loader in `hybrid_gateway/canonical_loader.py`; checks Git blob identity before importing. Unit-tested against a toy fixture and altered-source negative control.
2. `hybrid_gateway/temporal_audit.py`: frozen query-case structure, deliberately weak latest-known baseline, multiple caller-supplied evidence-weight profiles, comparison reports.
3. Strengthened `hybrid_gateway/cascade_bridge.py` to compare structural state snapshots before/after diagnostic. Its earlier guard only observed event-chain head, which does not detect arbitrary mutation of indexes such as `_by_key`. Rejects booleans as evidence weights.
4. New `demo_temporal_audit.py`: four synthetic scenarios. Results: 2/4 latest-known matches ledger; one case changes *test-double* diagnostic with different authored weights; ledger abstains in the conflict case.
5. `demo_cascade_canonical.py` now uses the SHA-pinned external loader, instead of importing any file found at a user-provided path without identity verification.
6. Privacy-minimised `public_report`: excludes source bodies, raw quotes, values, case identifiers and tenant names; only explicitly bounded aggregate and ordinal diagnostic signals remain.

## Canonical provenance

Connected GitHub API returned `12_IMPLEMENTATIONS/core/cascade_engine.py`, Git blob SHA-1 `bf90a47ab17da11c0266d078fc4d74a5d95c9235`. Source inspected: genuine `CascadeEngine` and `KnowledgeBlock` classes, original conflict proxy different paradigms in same domain. GitHub URI: https://github.com/Lycheetah/Lycheetah-Framework/blob/master/12_IMPLEMENTATIONS/core/cascade_engine.py

**Canonical file execution did not occur.** This isolated runtime has no accessible local checkout or internet download. The opt-in runtime harness is shipped for execution elsewhere against a trusted, pinned checkout. The only executed engine in the v0.7 diagnostic comparison was explicitly labelled `FixtureEngine`/`MiniCascade`.

## Synthetic result table

| Case | Ledger | Naive latest-known | Profiles diverged? |
|---|---|---|---|
| January after March knowledge | ANSWER 14 | 60 | No |
| February before revision known | ANSWER 14 | 14 | No |
| February after revision known, before dispute | ANSWER 30 | 30 | No |
| February after unsuperseded 60-day dispute | ABSTAIN_CONFLICT | 60 | Yes (test double) |

A 2/4 naive baseline match and 4/4 ledger match with authored expected behavior **do not establish external generalization**. The baseline is not a competitive version-aware RAG model. The data are fictional and intentionally targeted.

## Honest boundaries

- No real inference, no independent labelled corpus, no canonical CASCADE execution, no human reviewer effort data, no state-of-the-art RAG baseline.
- No calibration of CASCADE pressure: supplied weights are illustrative values, never derived by this system.
- Structural digest detects in-process state drift after normal callback return but is not hostile-process sandboxing, rollback or multi-party attestation. Same-process malicious callback can still corrupt memory.
- Canonical pin is Git object identity, not a code-security audit or provenance signature of who authored it. Dependencies and trust of checkout remain operator responsibilities.
- Local tests emit intermittent `sqlite3.Connection` ResourceWarnings from inherited test lifecycle; tests nevertheless pass. This is maintenance debt, not a transaction failure demonstration.
- Original v0.6 unauthenticated reviewer flag and lack of external effect executor remain unchanged.

## Next research gate

1. On a system with a checked-out, explicitly pinned `Lycheetah-Framework`, execute `demo_cascade_canonical.py` and record Python/NumPy versions, stdout/stderr, commit ID and dependency environment. If the blob pin differs, inspect source diff first.
2. Build an independent temporally annotated corpus; report coverage, wrong field/scope, omissions, calibration and reviewer minutes on unseen data.
3. Compare under identical budgets to state-of-the-art version-aware retrieval, not just latest-known.
4. Audit trust and auth semantics before implementing production actions.

**Status:** Local research scaffold with repeatable test evidence. No GitHub branch created or pushed.
