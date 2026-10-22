# BATCH 30 — RV31 · `99_ARCHIVE/closed_loop_agent_lab/` clean-clone integrity

**Reviewer:** Sol (Claude Opus 5.5, xhigh) · **Date:** 2026-10-22 · **Branch:** `review/full-framework-2026-10-20`, working tree only, nothing staged or committed.

## Scope actually covered

- Read: the lab `README.md`, `SHA256SUMS.txt` (1,788 entries), the `.gitignore` rules, `tools/verify_research_intake.py`, and `tests/test_research_intake.py`.
- Measured: every sums entry on disk, every tracked ZIP's member list (87 ZIPs, 25,538 members), and git tracked/ignored status for every pinned path.
- **DID NOT RUN:** the lab's own test suites. Running them would write `__pycache__` into a frozen archive, and they are not the subject of RV31.

## Findings

| # | Status | Finding |
|---|---|---|
| F1 | MEASURED | `.gitignore:28 *.log` kept all **374** `.log` files pinned by the lab's `SHA256SUMS.txt` out of Git: 371 under `03_LAB_SOURCE_TREE` and 3 under `04_COMPANION_RECORDS`, 1.9 MB in total. On this disk all 1,788 hashes match. A clean clone would be missing 374 pinned files. |
| F2 | MEASURED | 373 of the 374 logs can be recovered byte-for-byte from the tracked ZIPs. **`04_COMPANION_RECORDS/standalone_package_retest_v5.1.log` (18,704 bytes) exists only on this machine.** |
| F3 | MEASURED | The 25,538 ZIP members contain 0 secret-pattern hits and 0 `/home/` or `C:\Users` paths. Unignoring the logs does not publish anything the ZIPs did not already carry. Caveat: this is a pattern scan, not a semantic secret review. |
| F4 | MEASURED | Nothing in `tests/` or `tools/` referred to the lab. Its checksums were never checked by any gate, which is why F1 went unseen. |
| F5 | MEASURED | The README tree labels `cumulative_snapshots/` as "v4.1 through v4.9". The 45 tracked ZIPs carry 44 version labels from v0.1 to v4.9. The README is outside the sums, so it received a dated note and the line was left as written. |

## Repairs (working tree)

1. **`.gitignore`**: after the earned-trust negation, added `!99_ARCHIVE/closed_loop_agent_lab/**/*.log` with a dated comment. `git status` now shows all 374 logs as untracked (`??`), so a `git add` will pick them up.
2. **`tools/verify_research_intake.py`**:
   - `SUMS_BUNDLES` gains `99_ARCHIVE/closed_loop_agent_lab` with 1788 entries and review path `None`.
   - `None` marks an *archive* bundle: its bytes and membership are pinned, but it lends no footing to the claim gate. The 114-inherit count is unchanged.
   - `verify_sums_bundles` counts checked files separately from footing files.
   - `verify_all` now sums each part's `files_checked`. Before this, it reported `len(footing)`, which would have hidden archive files.
3. **`tests/test_research_intake.py`**:
   - The real-tree assertions now expect 121 + 1788 and 444 + 210 + 121 + 1788.
   - `test_lab_logs_pinned_by_its_sums_are_not_gitignored` checks every pinned `.log` with `git check-ignore --no-index`, so it tests the ignore rules rather than the current index.
   - `test_archive_bundle_pins_bytes_without_lending_footing` covers both sides: a benign archive with no footing words passes, and removing a pinned file is refused.
4. **`99_ARCHIVE/closed_loop_agent_lab/README.md`**: added a dated RV31 note covering F5 and F1. The body is unchanged.

## Witnesses

| Witness | Result |
|---|---|
| A: check-ignore test with the old `.gitignore` | **FAILED** as expected: "374 pinned lab logs are git-ignored". |
| B: same file after the negation | 29 passed. |
| C: clean-checkout simulation (scratch copy of `git ls-files` only) | **REFUSED**: "source tree membership changed". |
| C′: same copy plus `git ls-files --others --exclude-standard` | 1788 checked, pass. |
| `verify_research_intake.py` | 2,563 files, 130,491,604 bytes (444 + 210 + 121 + 1788). |
| `verify-claims.py` | 3 unmarked, HOLDING. Still 114 documents inherit footing. |
| `verify-links.py` | 0 dead links outside the archive. |
| Full suite | **1539 passed, 1 skipped, 1 xfailed, 1 warning** (69 s). That is +2 on the RV30 run. |
| lint | DID NOT RUN (`ruff` not installed). |

## G-items for Mac

- **G-RV31-1 (blocking for CI on a clean clone):** `git add 99_ARCHIVE/closed_loop_agent_lab` to track the 374 logs (1.9 MB). Until that happens, the new bundle check fails on any fresh clone. It fails loudly, which is the intended behaviour.
- **G-RV31-2:** back up `standalone_package_retest_v5.1.log` (the only copy). G-RV31-1 does this through Git; a private backup is the alternative if you would rather not publish it.
- **G-RV31-3 (optional):** correct the README range. A note is in place; the body stays as you wrote it.
