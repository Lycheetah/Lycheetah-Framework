# BATCH 32 — RV33 · Packaging, tests, CI and migration

**Reviewer:** Sol (Claude Opus 5.5, xhigh) · **Date:** 2026-10-22 · **Branch:** `review/full-framework-2026-10-20`, working tree only, nothing staged or committed.

## Coverage, stated honestly

- **Read:** `pyproject.toml` (build system, dependencies, extras, the 11 scripts, setuptools packages and package data, ruff and mypy configuration), `.github/workflows/ci.yml`, `12_IMPLEMENTATIONS/applications/sol_workspace_mcp.py` (whole), the guard's 2.x `build_server` / `main` / `main_http`, `tests/test_sol_workspace_mcp.py`, `tests/test_consensus_integrity.py`, the strict xfail at `tests/test_cascade_predictability.py:355`, `lycheetah/consensus/arena.py` (verdict, digest and integrity), the collection normalization in `lycheetah/assurance/policy.py`, and the gateway reconcile path.
- **Built in scratch copies, never in the repository:**
  - a wheel (system setuptools 68.1.2);
  - an sdist (setuptools 84.2.1) from a minimal copy of exactly the paths the build reads;
  - a wheel rebuilt from that sdist.
- **Clean virtual environments** were made with `--without-pip`, and none reuse system site-packages:
  - **base:** cffi 2.1.1, cryptography 50.0.2, networkx 3.7, numpy 2.5.4, scipy 1.18.1;
  - **`[all]`:** adds mcp 2.3.0, Flask 3.1.3 and jsonschema 4.26.0.
- **Hosted CI:** read with `gh run list` / `gh run view` against `Lycheetah/Lycheetah-Framework`.
- **DID NOT RUN:**
  - Python 3.10 and 3.11, the other two legs of the CI matrix. Only 3.12 exists on this machine, and there is no `uv` or `pyenv`.
  - Windows or macOS.
  - Any hosted job. None can start; see F1.
  - The `stdio` MCP transport under 1.x. `main_http` was exercised live under 2.x only.
- **Earlier batches already cover three checklist items, which were cross-checked rather than redone:**
  - consent preservation in BATCH7 (RV08, a 14-value sweep in three modes);
  - the dirty-tail and reconciliation path in BATCH4 (RV05);
  - the arena's H¹ claim in BATCH19.

## Findings

| # | Status | Finding |
|---|---|---|
| F1 | MEASURED (`gh`) | **Hosted CI has not run.** Every recent Actions run, master included, ends "failure" in 3–10 s with the annotation *"The job was not started because your account is locked due to a billing issue."* Those runs are **DID NOT RUN**, not test failures. No hosted pass exists to cite for this tree or for HEAD. Pages deploys still succeed. A separate notice says `ubuntu-latest` moves to Ubuntu 26 from 19 Oct 2026, so the first run after unlocking will also be the first on a new image. |
| F2 | MEASURED (clean venv) | **`sol_workspace_mcp` crashed on the MCP SDK its own extra installs.** The `[mcp]` extra pins `mcp>=2.0,<3.0`. Under mcp 2.3.0, `build_server()` died at `@server.list_tools()` with `AttributeError: 'Server' object has no attribute 'list_tools'`, because the 1.x low-level decorators are gone in 2.x. `MCP_AVAILABLE` still read True, because `Server`, `SseServerTransport` and `types` all still import, so the guard flag hid the break. `main_http` also used the 1.x `server.run(read, write, init_options)` shape. Locally this machine has mcp 1.27.2, which is why the module, its tests and BATCH12's M11 all looked green. The module ships in the wheel as `lycheetah.applications.sol_workspace_mcp`. It is not a console script, so the 11 entry points were unaffected. |
| F3 | MEASURED (clean venv) | **SDK 2.x hides the reason for every refusal that is not a `ToolError`.** In 2.x, an exception other than `ToolError` reaches the client as `is_error=True` with only `"Error executing tool <name>"`; the text is logged server-side and withheld. A straight port therefore turned "Unknown gate '5'; expected '3', '4' or 'post'" into a bare error. The existing test caught this (`'Unknown gate' in 'Error executing tool add_task'`). |
| F4 | MEASURED (ruff 0.17.1, mypy) | **The CI lint job was already red at HEAD, with no billing involved.** On a `git archive HEAD` export, `ruff check .` reports 46 errors. The config comment says the floor "currently reports zero", which is false. All 46 sit in bundles that were frozen 17–19 Oct and are pinned by their own `MANIFEST.sha256` / `SHA256SUMS.txt`: 21 B023 in three `action_guard/versions/v0.6–v0.8` verification scripts, 22 F405 plus 1 F403 in the `25_RESEARCH_CYCLE_23` test harness, and 2 B904 in that cycle's `bridge_v0_2.py` and in `earned-light/.../right_of_return.py`. They landed while hosted CI could not start, so no gate saw them. At HEAD, `mypy lycheetah/` is clean and `ruff format --check` is clean (31 files). |
| F5 | MEASURED | **This review's own earlier batches had regressed the shipped-package gates, and that is now repaired.** On the review tree: ruff +5 (two E501 in `action_guard.py`, I001 in `arena.py`, B023 and a raw zero-width space in two FOR-REVIEW repro scripts), `ruff format` 4 files, and `mypy` 3 errors in `gateway.py`. The 3 mypy errors were a dict literal typed `dict[str, str]` assigned to a `Literal`, and the reconcile path assigning `decision.status: str \| None` into `ExecutionResult.status`. CI would have failed on these once billing unlocked. |
| F6 | MEASURED | **Clean resolution passes.** In the base venv, `tools/verify_base_distribution.py` passes (domain demos 2, every boundary true). In the `[all]` venv, `tools/verify_installed_distribution.py` passes (`schema_packaged`, `evaluation_harness`, `regression_gate` and `otel_event` all true). All **11** console scripts answer `--help` with rc 0 from a neutral working directory. The wheel has 85 members, 11 entry points, 5 assurance schemas and 0 bytecode files. The sdist has 90 members including `LICENSE` and Metadata 2.4 with all four extras, and 0 private, AZOTH, `.env` or bytecode paths. A wheel rebuilt from the sdist has the same members as the tree-built wheel; the only delta is setuptools 84 placing the licence at `dist-info/licenses/LICENSE` instead of 68's `dist-info/LICENSE`. The sdist ships no tests, by default setuptools behaviour. |
| F7 | MEASURED (earlier attempt) | **The checklist is right that reuse is not clean resolution.** A first attempt with system site-packages *falsely failed*: system Flask leaked into the base check, and system mcp 1.27.2 into the `[all]` check. Only the isolated venvs above are evidence. |
| F8 | DERIVED | **The strict CASCADE xfail is honest, not hidden.** `tests/test_cascade_predictability.py:355` is `xfail(strict=True)` against F1 > 0.80. The test's own oracle ceiling is F1 0.548 at an 8.8 % base rate, so the criterion is unattainable by construction, and strict mode would flag an unexpected pass. The criterion needs replacing, and choosing it is the author's call (G-RV33-4). |
| F9 | MEASURED (mutation) | **Consensus v2 migration fails closed, but nothing pinned the rule that does the work.** `verify_integrity` refuses a verdict without an anchor, and the `lycheetah.consensus-verdict.v2` digest binds `profile` and `anchor_vector`, so a v1 digest never verifies on a v2 verdict. There is no deserializer, so migration means "re-deliberate", as the docstring says. The existing test changed `anchor_vector=()` without re-sealing, so the digest mismatch refused it and the anchor rule was never exercised. With that rule mutated out, all 14 existing tests still passed. A re-sealed, anchorless verdict *with* a consensus vector is also refused by the vector-length rule. The case only the anchor rule refuses is a re-sealed, anchorless, unconverged verdict (`consensus_vector=None`). |
| F10 | MEASURED (mutation) | **Normalized policy collections hold and are pinned.** `_strings` copies every pattern list into a tuple, refusing non-arrays, empty strings and duplicates. `text_rules` and `phases` are snapshotted too. Mutating `_strings` to keep the caller's list fails 5 of the 6 targeted tests. One property is recorded rather than changed: the digest is order-sensitive (`["a","b"]` ≠ `["b","a"]`). That fails safe, since it can produce a false "changed" but never a false "same". |
| F11 | MEASURED (live) | **The ported SSE transport is better guarded than the old one.** Under 2.x, `main_http` on `127.0.0.1:18766` served the `/sse` endpoint event, and a request with `Host: evil.example` was refused **421**. The old hand-built Starlette app had no Host check, which is the same DNS-rebinding class fixed for cascade-pc in BATCH31. The documented client entry (`"type": "sse", "url": "http://localhost:8766/sse"`) is unchanged. |

## Repairs (working tree)

1. **`12_IMPLEMENTATIONS/applications/sol_workspace_mcp.py`, ported to SDK 2.x while keeping 1.x working.**
   - **Import:** `mcp.server.MCPServer` (2.x) falls back to `mcp.server.fastmcp.FastMCP` (1.x), each with its own `ToolError`. `MCP_SDK_MAJOR` is 2, 1 or 0, and `MCP_AVAILABLE` is now true only if the server class itself imports.
   - **One tool table:** six typed functions (`get_open_tasks`, `get_gate_status`, `complete_task(task_id: int)`, `add_task(subject, gate, file="", notes="")`, `get_app_version`, `bump_version(bump_type: Literal["patch","minor","major"])`) registered by name. The input schemas are generated from the signatures, and both SDKs produce identical schemas, compared directly.
   - **Error results:** `_refusals_reach_client` re-raises `ValueError` and `OSError` as `ToolError`, so a refusal is still `isError` and its reason reaches the client under both SDKs (F3).
   - **`main_http`:** `run("sse", host="127.0.0.1", port=…)` on 2.x; on 1.x it sets `settings.host/port` and then calls `run("sse")`.
   - Backup: `$S/rv33_bak/sol_workspace_mcp.py`.
2. **`tests/test_sol_workspace_mcp.py`.** The isError test connects with `mcp.Client` (2.x), falling back to the 1.x in-memory session.
3. **`lycheetah/assurance/gateway.py` (mypy).**
   - A module `ResultStatus` Literal, now also used by `ExecutionResult.status`.
   - Typed `_OUTCOME_STATUS` and `_SETTLED_STATUS` maps.
   - In reconcile, a settled status other than SUCCEEDED or FAILED now becomes UNKNOWN instead of passing through untyped. That branch is unreachable today, because the guard settles only to those two (`action_guard.py` `reconcile`).
4. **`ruff format`** on `action_guard.py`, `checkpointed_workflow.py`, `policy.py` and `receipt.py`. Every one was already in this review's diff, and none is unchanged from HEAD. Import sort in `arena.py`, plus removal of a duplicated `# noqa` that the autofix left behind.
5. **FOR-REVIEW repro scripts:** `repro_batch7.py` now writes the zero-width space as `"​"`, which gives the same runtime string, and `repro_batch17.py` binds `Pi` in its lambda.
6. **`pyproject.toml`.** A dated block of per-file ignores for the three frozen bundles, using the same treatment the file already gives three other frozen bundles. B023 in the race closures is genuine but harmless, because each round's threads are joined inside their own iteration. The frozen files themselves are untouched. Backup: `$S/rv33_bak/pyproject.toml`.
7. **`tests/test_consensus_integrity.py`.** Added `test_legacy_verdict_without_anchor_is_refused_even_when_resealed`. It re-seals anchorless verdicts with and without a consensus vector, refuses a v1-shaped digest, and pins the profile name.

## Witnesses

- **sol_workspace + guard tests:**

  | Environment | Before the port | After the port |
  |---|---|---|
  | mcp 2.3.0, clean `[all]` venv | `build_server` crash (F2) | **21 passed** |
  | mcp 1.27.2, local | — | **16 passed, 1 skipped** |

  - The intermediate port without `_refusals_reach_client` failed 1 test under 2.x (F3), so that test witnesses the wrapper.
  - The skip is `test_mcp_guard` on local 1.27.2, by design.
- **Live:** under 2.x, the SSE endpoint served its `/sse` endpoint event and refused a rebound Host with 421. The server was stopped by its PID.
- **Lint and type gates (ruff 0.17.1, mypy, in the scratch venv):**
  - `ruff check .`: 51 on the tree before the repairs, 46 at HEAD, **0 after** ("All checks passed!").
  - A planted undefined name in an excused frozen file was still reported. ⚠ That plant was made in the live frozen file, `versions/v0.6/run_verification.py`, and restored byte-exact (`git diff --quiet HEAD` confirmed). It should have been done in a scratch copy; recorded as a process slip.
  - `ruff format --check`: 31 files already formatted.
  - `mypy lycheetah/`: no issues in 30 source files.
- **Consensus test (scratch mutant, anchor rule removed):** the first version of the new test **passed on the mutant**, so that witness was void, and the test was tightened to cover the unconverged case (F9). The tightened test **fails on the mutant** and passes on the tree (14 passed).
- **Policy (scratch mutant, `_strings` keeps the caller's list):** 5 failed, 1 passed.
- **Full suite:**
  - local, mcp 1.27.2: **1540 passed, 1 skipped, 1 xfailed**, 1 warning (96.8 s). That is BATCH31's 1539 plus the new consensus test.
  - clean `[all]` venv, mcp 2.3.0: **1544 passed, 1 skipped, 1 xfailed** (85.5 s). The four extra passes are guard tests that skip without SDK 2.x, and the venv's one skip is a different test. Every skip is by design; the xfail is F8.

## Decisions for Mac (G-items)

- **G-RV33-1 (blocking every hosted claim): unlock GitHub billing.** Until then, no workflow runs and every red X is DID NOT RUN. The first run after the unlock lands on the Ubuntu 26 runner image.
- **G-RV33-2: `ruff` and `mypy` are pinned only by floors** (`ruff>=0.6`, `mypy>=1.11`), and the floor config says "currently reports zero", which was false for five days. Options:
  - (a) pin exact dev-tool versions so a new rule release can't redden CI on its own;
  - (b) add a "frozen bundles" lint ignore keyed to the intake verifier's bundle list, so the next frozen bundle doesn't need a hand edit.

  Sol's stance: (a) now, and (b) when the next bundle lands.
- **G-RV33-3: Python 3.10 and 3.11 are unwitnessed.** The code uses `match` (3.10+), `Literal` and PEP 604 unions, so 3.10 is plausible but UNVERIFIED. It needs the hosted matrix (G-RV33-1) or a local interpreter.
- **G-RV33-4: replace the CASCADE F1 > 0.80 criterion** with one the oracle can reach, or retire the claim. Strict xfail keeps it honest meanwhile.
- **G-RV33-5: disk.** The root filesystem was at **100 %** (717 MB free of 108 GB) when a scratch copy filled it during this batch. After clearing this review's own stale scratch it is at 99 % (about 1.4 GB free). A full disk makes builds, tests and git fail in ways that look like broken code. The cause is outside the repository and outside this review's scope.
