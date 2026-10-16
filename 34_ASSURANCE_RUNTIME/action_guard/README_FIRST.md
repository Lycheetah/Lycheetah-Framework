# Lycheetah Action Guard — Preservation Archive

**Archive date:** 17 October 2026  
**Scope:** The Action Guard research thread, from the v0.5 prototype through v0.8.  
**Latest integrated snapshot:** `versions/v0.8/`

This is a preservation bundle, not a claim that the system is production-ready. It includes the extracted source/tests/reports/results for each historical release, plus the original release ZIPs so each packaged snapshot is retained exactly as delivered.

## Start here

1. Read `RESEARCH_HISTORY.md` for how the idea evolved and which claims are supported.
2. Read `versions/v0.8/README.md` for the latest implementation layout and run instructions.
3. Read `versions/v0.8/RESEARCH_REPORT.md` for methodology, results, limitations, citations and next experiment.
4. Inspect `versions/v0.8/verification_results.json` and `versions/v0.8/v07_synthetic_benchmark_results.json` for machine-readable results.
5. Validate the archive's file checksums from this directory with `sha256sum -c ARCHIVE_MANIFEST.sha256`.

## Version map

- `versions/v0.5/` — action-specific approval binding and in-process replay control.
- `versions/v0.6/` — SQLite persistence, single-use effect intent, authority epochs, explicit `UNKNOWN` outcome and concurrency/restart tests.
- `versions/v0.7/` — hash-chained audit history and a retained checkpoint required at the dispatch boundary.
- `versions/v0.8/` — a separate local checkpoint-authority process using signed checkpoints, audit-extension validation, operational-state reconciliation, a fail-closed workflow wrapper, simulated provider, and a no-network GitHub request preview.
- `original_release_zips/` — byte-preserved original ZIP files from each release.

## Evidence discipline

The included test and benchmark results are locally authored, deterministic/synthetic verification of the supplied prototype. They are not independent security validation. The v0.8 service ran as a separate OS process on the same host; that does **not** constitute an independent production trust domain. No live GitHub API call, credential, repository write or merge was used. See the version reports for complete qualifications.

## Important security boundary

Do not use this archive as an authorization component for real high-impact actions. The prototype needs an independent code/threat-model review, separately administered checkpoint storage/key custody, authenticated human approval, real-provider read-only/dry-run integration, and recovery testing before any live-write experiment. Merge writes remain out of scope.
