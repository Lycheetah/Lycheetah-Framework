# Changelog

Notable changes to this repository. Format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/); versioning follows
[Semantic Versioning](https://semver.org/spec/v2.0.0.html).

This file starts at the Unreleased section below. Everything before it is in the git
history, which was the only changelog until now.

## [Unreleased]

### Public integration and build catalogue — 4 October 2026

- Added thirty-one proposed tools, games and interactions in a seven-part Build Catalogue, with stable IDs, source boundaries, first slices and observable acceptance. No new game or tool prototype is implied by these briefs.
- Integrated eight historical frontier-control packets, with explicit missing-file/hash reconciliation and new public-only packaging adapters. Added a SCAFFOLD finality evidence recheck and Linux execution-cell candidate; witness authentication, provider atomicity and production containment remain open.
- Added the public Compensation Race experiment. Proprietary research remains outside this public repository. Local reruns, known failures and packaging gates are recorded alongside each public packet.
- Repaired existing public-package lint/type failures, marked provisional paper/index footing without increasing the claim budget, and fixed navigation links in six collected source copies while retaining original import hashes and private snapshots.
- The existing non-conjecture suite passed 695 tests before final packaging corrections. Final verification and remote references are recorded in the publication receipt; original source reports are not relabelled as independent results.

### Modelcraft and Recommendation Hall contracts — 4 October 2026

- Preserved Mac × Vaelora's original master unchanged and completed the registry of 24 technique families across ten internal teaching Halls. Added one checklist experiment and a business worksheet; all families remain untested in this packet and supplied provider links remain unverified.
- Added strict schemas for recommendations, explicit ranking inputs, opt-in private events and private trick receipts. Evidence maturity, compatibility, freshness and lifecycle are separate; structural checks cannot authenticate reproductions or enforce actual storage privacy.
- Added a local stateless ranking reference using explicit fit, prerequisites, tools and budget, with inspectable components and stable ties. Unknown/stale service costs cannot pass a zero-budget claim; ranking does not accept engagement, popularity or inferred-identity fields.
- Linked the package from current School/Framework navigation and recorded the ten-Wing proposal versus the earlier fourteen-Wing app snapshot. Native navigation, persistence, community review, phone witness and learner outcomes remain open. No native app write or provider call; included in the 4 October master publication batch.
- Highest witness: seventeen focused contract/ranking tests, four Draft 2020-12 schemas, byte-exact source preservation, thirty-eight local links and backup recovery. A malformed-date validation failure was repaired and its original failure log preserved. These are local data/reference checks, not model experiments or native-app validation.

### Living Scripture and School source integration — 4 October 2026

- Integrated Mac × Vaelora’s v0.5.1 twelve-book candidate into the existing scripture collection, preserving authored core bytes, source/register boundaries, the dedicated Aotearoa covenant and the original implementation contract. Historical Mythos and fiction remain preserved; no canon promotion.
- Recovered fourteen missing machine-readable/validator files from the Identity Return v0.3 archive. The current School source home now includes eighteen Mantles, fifty-four Forms, versioned title receipts and voluntary-return design data.
- Added a Book I data fixture with seven exact sections, four named interlocutors, stable IDs and explicit private/cultural/status defaults. Focused data/schema and import-mutation gates cover those contracts; they do not implement app behavior or validate learner outcomes.
- Updated collection/School navigation and generated the combined reading editions. The inspected live app’s fourteen Wings conflict with the supplied nine-Wing design; the resumable native handoff records this without changing the app.
- Highest witness: local source hashes, structural/data validators, negative fixture cases, reading-link checks and archive preservation. Native app persistence, phone visuals, cultural review, empirical outcomes remain open. No native app write or provider call; included in the 4 October master publication batch.

### Framework consolidation — 4 October 2026

- Established one working Framework checkout on master and a source guide in WORKING_HOME.md. Recovered The Independent No manuscript, evaluation protocol, source ledger, reading editions, PDF and historical witness artifacts; added current paper/site index links.
- Recovered two historical School reference maps, explicitly marked as older designs rather than the current Sol release plan. Preserved newer code, claim corrections and retired-workflow decisions. Private variants, previous navigation bytes and Git worktrees remain recoverable.
- Local file/hash, backup round-trip, source-routing, link and diff checks verify consolidation. No new browser/model experiment was performed during consolidation. The 4 October publication receipt records subsequent tests and remote verification.

### Fixed

- **The installed package now works.** `pip install lycheetah-framework` produced a
  distribution in which every advertised entry point raised `ModuleNotFoundError`:
  the wheel shipped only `__init__.py` and `cli.py`, while the implementation they
  re-export lives in `12_IMPLEMENTATIONS/`, which was never packaged. Both modules
  reached it through a hardcoded relative path that exists only in a source checkout.
  `lycheetah.check()`, `lycheetah.sol_assess()` and all four console scripts were
  affected. `pyproject.toml` now maps the implementation directories onto
  `lycheetah.core` and `lycheetah.applications`, and path resolution moved into
  `lycheetah/_bootstrap.py`, which handles both layouts and raises a named error when
  neither is present.
- **`lycheetah-guard` could never have started**, from 1.0.0 onward. Three failures
  were stacked in it: `build_server()` is annotated `-> Server`, a name bound only
  inside the `try: from mcp.server import Server` block, so importing without the
  optional `mcp` extra raised `NameError` before the `MCP_AVAILABLE` flag could be
  read; `lycheetah/cli.py` imported a `main` that did not exist, the module defining
  only `main_stdio` and `main_http`, so the script was broken even *with* `mcp`
  installed; and the `MCP_AVAILABLE` check sat in the `if __name__ == "__main__"`
  block, which a console script never runs, leaving the intended "install mcp"
  message unreachable. The module now uses `from __future__ import annotations`,
  exposes a real `main()` behind an `argparse` parser (so `--help` works and both
  `--port=N` and `--port N` parse), and gates on the missing extra with a named,
  actionable error. `tests/test_entry_points.py` covers it, and the CI packaging gate
  now smoke-tests all four scripts, including the assurance CLI.
- `lycheetah/py.typed` was declared in package data since 1.0.0 but never existed, so
  the distribution claimed PEP 561 typing and shipped no marker.
- Two modules could not be imported at all: `subject_catalogue.py` carried a stray
  `-e ` line that raised `NameError`, and `run_chorus.py` used `Dict` and `List` in
  annotations without importing them.
- `knowledge_genome.py` called `json.dump` with no `json` import.
- `grey_mode.py` built an audit-trail entry from an undefined name behind a dead
  `if False` guard, then overwrote it with a second clock reading; the clock is now
  read once and the trail agrees with `entry_time`.
- Duplicate `×` key in the ASCII table in `generate_defense_bundle.py`.
- `assert False` in three `32_TIANXIA` self-tests, which `python -O` strips — those
  tests would have passed silently under optimisation.
- A closure over a loop variable in `cascade_simulation.py`, and a loop variable
  shadowing the imported `dataclasses.field` in both copies of `equivalence.py`.
- `--context` on `lycheetah-check`, and the `context` argument to `lycheetah.check()`,
  were accepted and silently discarded. The analyser still does not use them; the CLI
  now says so on stderr rather than appearing to have applied them.

### Changed

- **Scriptures and stories now have one collected working home** in
  `LYCHEETAH_MYTHOS/SCRIPTURES_AND_STORIES/`: a 1,849-word editorial distillation,
  a master containing 20 complete reading texts, a browser reading edition, and
  48 preserved textual sources including writing/research context. Mac's future
  revisions belong in the collection; older source paths and manuscript statuses
  remain intact. Local source hashes, master navigation and ZIP round-trip checks
  passed. The browser layout has not been visually witnessed. Local and uncommitted;
  no publication or app integration performed.

- **The Night Garden reading edition:** explained Framework names on first use,
  shortened dense passages, and moved graph notation and detailed source limitations
  into the companion notebook. Preserved the scenes, citations and research boundaries.
  Highest witness: authoring-seat editorial review and local content/navigation checks;
  readability has not been tested with independent readers.

- **CI now runs the checks it claimed to run.** Three of four workflows could not
  have passed and one had never triggered:
  - `ci.yml` invoked `alexandria_agent.py` at the repository root; it lives in
    `12_IMPLEMENTATIONS/`.
  - `update-stats.yml` invoked `promote.py`, which exists nowhere in the repository.
    Removed rather than repaired — it also pushed to `master` on success.
  - `agent-deploy.yml` triggered on `main` and `develop`; the default branch is
    `master`. Its assertions referenced two files that do not exist, a manifest key
    that has never been present, an agent state shape the bootstrap does not write,
    three CLI flags nothing parses, a class name that does not exist, and Python 3.9,
    below the `requires-python` floor. Rewritten against the real bootstrap contract.
  - `test.yml` folded into `ci.yml`.
- **The Alexandria drift audit stopped passing vacuously.** It compared a directory
  that does not exist against a file defining none of the constants it searched for,
  skipped every check, printed `NO DIVERGENCE DETECTED` and exited 0. It now checks
  constants actually bound in code, reports how many checks ran, and fails as
  `INCONCLUSIVE` when a check cannot be evaluated.
- The Alexandria health check resolved paths against its own directory, so it searched
  `12_IMPLEMENTATIONS/12_IMPLEMENTATIONS/` and reported all five core modules missing.
  It now imports and smoke-tests 5/5.
- `agent-init.py` had the same root-relative bug plus stale directory names predating
  the `_L<n>` suffixes: 0/14 components found on a complete checkout, now 14/14.
- `agent-manifest.json`'s documented bootstrap command and two of its six entry points
  pointed at paths that do not exist.
- The cascade predictability conjecture test is `xfail(strict=True)` rather than a
  hard failure. The assertion and its
  measured F1 of 0.531 are unchanged; `28_DEFENSE/REPRODUCIBILITY_REPORT.md` had
  already derived that the 0.80 criterion sits above the oracle ceiling of 0.548 at
  this base rate. `strict` means an unexpected pass fails the suite, because that
  would falsify the derivation. Choosing a replacement criterion remains open and is
  the author's decision.
- The `Failure Museum` project URL pointed at a repository-root file; it is at
  `28_DEFENSE/FAILURE_MUSEUM.md`.

### Added

- **The Night Garden:** an exploratory night-reading essay connecting the Lycheetah
  Framework with AI futures, cybernetics, memory, dissent, translation and revisable
  institutions. Includes a source ledger, six candidate research questions and
  explicit counterarguments. Local content/navigation checks are recorded alongside
  the essay; no new empirical validation or runtime capability is claimed.

- Lint, type, format and packaging gates: `ruff`, `mypy`, `python -m build`, and an
  install-the-wheel-in-a-clean-venv check — the only gate that would have caught the
  packaging defect, since the tests run from a checkout where the broken path shim
  still works.
- Two-tier `ruff` configuration: a narrow corpus-wide floor of rules that indicate a
  real defect (currently at zero, so any hit is a regression), and a strict set for
  the shipped `lycheetah/` package via `lycheetah/.ruff.toml`.
- `mypy` configuration covering the public wrapper. Clean.
- `.gitattributes` preserves the repository's existing line endings while marking
  binary assets and archival material for GitHub language statistics.
- `.pre-commit-config.yaml` mirroring the CI gates.
- `.github/dependabot.yml` for Actions and pip, grouped so a routine bump is one
  review. The workflows had been pinned to `checkout@v3` and `setup-python@v4` well
  past their supersession.
- `SECURITY.md`, `CODE_OF_CONDUCT.md`, and this file.
- `--strict-markers` for pytest, so an unregistered marker fails instead of silently
  leaving a test unmarked.
- The experimental Assurance Runtime package, schemas, examples, and
  `lycheetah-assure` command, with explicit internal-verification limits.
- The Abstract and Generative collection and its September session records, retained
  as symbolic or speculative work rather than empirical claims.
- `concurrency` cancellation, least-privilege `permissions`, and pip caching on both
  remaining workflows.

[Unreleased]: https://github.com/Lycheetah/Lycheetah-Framework/compare/master...HEAD
