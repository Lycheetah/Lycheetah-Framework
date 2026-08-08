# Changelog

Notable changes to this repository. Format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/); versioning follows
[Semantic Versioning](https://semver.org/spec/v2.0.0.html).

This file starts at the Unreleased section below. Everything before it is in the git
history, which was the only changelog until now.

## [Unreleased]

### Fixed

- **The installed package now works.** `pip install lycheetah-framework` produced a
  distribution in which every advertised entry point raised `ModuleNotFoundError`:
  the wheel shipped only `__init__.py` and `cli.py`, while the implementation they
  re-export lives in `12_IMPLEMENTATIONS/`, which was never packaged. Both modules
  reached it through a hardcoded relative path that exists only in a source checkout.
  `lycheetah.check()`, `lycheetah.sol_assess()` and all three console scripts were
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
  now smoke-tests all three scripts rather than only the one that happened to work.
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
  hard failure, so the suite passes (266 passed, 1 xfailed). The assertion and its
  measured F1 of 0.531 are unchanged; `28_DEFENSE/REPRODUCIBILITY_REPORT.md` had
  already derived that the 0.80 criterion sits above the oracle ceiling of 0.548 at
  this base rate. `strict` means an unexpected pass fails the suite, because that
  would falsify the derivation. Choosing a replacement criterion remains open and is
  the author's decision.
- The `Failure Museum` project URL pointed at a repository-root file; it is at
  `28_DEFENSE/FAILURE_MUSEUM.md`.

### Added

- Lint, type, format and packaging gates: `ruff`, `mypy`, `python -m build`, and an
  install-the-wheel-in-a-clean-venv check — the only gate that would have caught the
  packaging defect, since the tests run from a checkout where the broken path shim
  still works.
- Two-tier `ruff` configuration: a narrow corpus-wide floor of rules that indicate a
  real defect (currently at zero, so any hit is a regression), and a strict set for
  the shipped `lycheetah/` package via `lycheetah/.ruff.toml`.
- `mypy` configuration covering the public wrapper. Clean.
- Python 3.13 added to the test matrix.
- `.gitattributes` — 57 tracked files had been committed with CRLF, including source
  and workflow files.
- `.pre-commit-config.yaml` mirroring the CI gates.
- `.github/dependabot.yml` for Actions and pip, grouped so a routine bump is one
  review. The workflows had been pinned to `checkout@v3` and `setup-python@v4` well
  past their supersession.
- `SECURITY.md`, `CODE_OF_CONDUCT.md`, and this file.
- `--strict-markers` for pytest, so an unregistered marker fails instead of silently
  leaving a test unmarked.
- `concurrency` cancellation, least-privilege `permissions`, and pip caching on both
  remaining workflows.

[Unreleased]: https://github.com/Lycheetah/Lycheetah-Framework/compare/master...HEAD
