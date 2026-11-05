# Claims and limits

All claims below are the author's (an AI coding session). Self-authored tests are engineering
checks, not independent validation. Nothing here has been reviewed by a different model or by Mac.

## Supported by observed evidence (MEASURED in this session)

1. The validator reports a named finding or blocker for each of the 22 cases in Cassian's
   test list, on hand-written records. — `tests/test_sync_zone_cycle.py`, 66 passed.
2. The tests are not vacuous for eight specific rules: removing each rule (mutations M1–M8)
   turns at least one test red. Two rules initially survived mutation (M4, M5); the tests were
   strengthened and both now fail. — `SYNC_ZONE_FINDINGS.md` SZF-05.
3. Adding the module and tests causes no regression in the maintained suite: baseline
   `1567 passed, 3 skipped, 2 xfailed`; after: see `SYNC_ZONE_PROGRESS.md` for the exact line.
4. Encoded as cycle records, the Sync Zone's dispute 1100 is invalid as written (a model
   ratified its own claim) and still unratifiable with Mac's ratification (its only review is the
   author's); the 2026-11-06 dossier drops dispute 400's standing finding from its handoff.
   — `records/retrospective_1100_report.json`.
5. Dispute 1100's script outputs follow from formulas it types in (`sqrt(1+1.5k)`;
   `alpha*(1-0.7*taste)`), not from observed agents. — `code/24_recursive_dark_node_engine.py:57-69`
   in the workshop, read and run this session.

## Plausible but untested

- Cycle records reduce lost caveats across real multi-seat handoffs (H1 in the packet). One
  live instance was caught retrospectively; no prospective comparison has been run.
- Computed independence reduces self-certification in practice.
- The ceremony is worth its cost for cross-session or cross-seat work.

## Explicitly not supported

- That any run, model, or human named in a record is who it says it is. Identity is declared.
  (`test_limit_human_identity_is_declared_not_authenticated`.)
- That a passing record means the work is correct. A circular simulation passes
  (retrospective V3). Five models sharing a fabricated source pass
  (`test_limit_shared_fabricated_source_passes_structure`).
- That the ledger resists someone who can rewrite the whole file. The head is not anchored.
- That human oversight scales, that multi-agent work is superior, that this is novel, or
  that it is safe in general.
- Dispute 1100/1200's conclusion that human steering is mathematically necessary. 1100 is
  circular by construction; 1200 is a sound Vicsek simulation whose mapping onto AI seats is
  interpretive. The protocol's human-principal rule rests on Mac's authority and on the
  repository's commitments, **not** on those simulations.
