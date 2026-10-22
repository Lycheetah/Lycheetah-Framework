# BATCH 34 — RV35 · Security and privacy

**Reviewer:** Sol (Claude Opus 5.5, xhigh) · **Date:** 2026-10-22 · **Branch:** `review/full-framework-2026-10-20`, working tree only, nothing staged or committed.

This ledger leaves out three things on purpose: personal email addresses, the private app repository's name, and anything from `15_PERSONAL_VAULT/`. It names the files that contain them and gives counts. If this ledger is committed, it should not republish what it is warning about.

## Coverage, stated honestly

- **Read whole:** `SECURITY.md`, `.gitignore` (the vault and `_PROPRIETARY/` lines), `[project.scripts]` in `pyproject.toml`, and the header of `sol_workspace_mcp.py`.
- **Probed live:**
  - Repository settings, through `gh api` with the owner's account.
  - DNS for `lycheetah.nz` and `lycheetah.org`, through DNS-over-HTTPS (`dns.google/resolve`).
- **Swept with patterns:**
  - Tracked files, untracked files, and the added lines of the pending diff: credential shapes, absolute home paths, email addresses, and the private repository name.
  - `15_PERSONAL_VAULT/`: a count of sensitive categories only. No content was copied.
- **DID NOT RUN:**
  - A **git history** secret scan. This needs `gitleaks` or `trufflehog`, and neither is installed. A full-history `git log -p` grep over this repository is heavy and was not run.
  - `npm audit` for `cascade-pc/`, because it needs network and `node_modules` is absent.
  - `pip-audit`.
  - Any check of whether the console scripts are reachable from a network. Each script was not run against a non-loopback bind.

## Findings

| # | Status | Finding |
|---|---|---|
| F1 | MEASURED | **There is no working private channel for reporting a vulnerability.** `SECURITY.md` names two routes, and both are broken. <br>1. **"Preferred: private security advisory."** `gh api repos/Lycheetah/Lycheetah-Framework/private-vulnerability-reporting` returns `{"enabled":false}`. <br>2. **"Alternative: mac@lycheetah.nz."** `lycheetah.nz` returns DNS Status 3 (NXDOMAIN), so mail cannot be delivered. <br>The policy's own fallback ("no acknowledgement in 10 days → open a private advisory") points back to route 1. A researcher who follows the policy exactly has nowhere private to go. |
| F2 | MEASURED | **Contact addresses on dead domains are spread across the corpus.** <br>- `mac@lycheetah.nz` is in `SECURITY.md`, `CODE_OF_CONDUCT.md` and `pyproject.toml` (package author metadata, which ships in every wheel). <br>- `mackenzie@lycheetah.org` is in 7 files, including `papers/CASCADE_ARXIV.tex` and the arXiv submission plan. `lycheetah.org` is also NXDOMAIN. <br>- Four distinct contact addresses are in use across the repository. |
| F3 | MEASURED | **`SECURITY.md` scope was stale.** It listed 3 console scripts, but `pyproject.toml` declares 11. It did not mention: <br>- the assurance runtime (`lycheetah/assurance/`: action guard, gateway, policy, receipts, checkpoint authority); <br>- the second MCP server, `sol_workspace_mcp.py`, which writes files over SSE on port 8766; <br>- the `cascade-pc` local API on port 7432 (see RV32 F1). <br>It also said "Nothing here should be relied on as a security boundary." That contradicts the assurance runtime, which exists to decide before execution whether an action may run. Under that sentence, a guard bypass would have been out of scope. |
| F4 | MEASURED | **Repository security settings.** The repository is public. Secret scanning is enabled, and push protection is enabled. Dependabot security updates are disabled. CI has no dependency audit, no CodeQL, and no Dependabot config. |
| F5 | MEASURED (pattern, tracked + untracked + pending diff) | **No credential shapes were found in the working tree.** 0 hits for `sk-ant`, `sk-`, `AIza`, `ghp_`, `github_pat_`, `nvapi-`, `xox`, `AKIA`, `PRIVATE KEY`, `hf_`, `gsk_`, or Stripe `sk_`/`rk_`/`whsec_`/`pk_live`. The added lines of this review's pending diff carry no key, home path or email. **Scope:** this is the tree only, not history (see DID NOT RUN). Pattern absence is not proof of absence. |
| F6 | MEASURED | **The private app repository's name appears in 7 tracked public files.** <br>- `03_LAMAGUE_L1/12_CORE_LANGUAGE_LINE/README.md` <br>- `13_SYNTHESIS_REPORTS/INGEST_2026-08-03_LAMAGUE_AND_TRUTH_PRESSURE.md` <br>- `33_APPLICATIONS/reflexive_audit.py:27` (as a `getenv` default sibling path) <br>- `LYCHEETAH_EPIC/COMIC/LIVING_COMIC_MOTION_WEAVE_V0_1.md` and its MYTHOS copy <br>- `TRUTH_PRESSURE/APP_IMPLEMENTATION_STATE_2026-08-01.md` <br>`gh` cannot resolve that repository from outside, which is consistent with it being private. The name is already in public history, so removing it from the tree does not unpublish it. The name alone exposes no code. |
| F7 | MEASURED | **A personal email address is in public files.** The owner's personal gmail is in `TRUTH_PRESSURE/IP_PROVENANCE.md`, `papers/ARXIV_ENDORSEMENT_EMAIL.md` and `papers/LYCHEETAH_SYNTHESIS_v0.1`/`v0.2`. A second personal gmail is in `28_DEFENSE/ATTRIBUTION_REQUIREMENTS.md`. Both are already in history. Whether they should stay is the owner's call, not a defect in itself. |
| F8 | MEASURED | **Absolute home paths, which publish the local username:** <br>- Tracked: root `AGENTS.md:3`. Under the RV27 boundary this gets a proposal only. <br>- Untracked, and would go public on commit: `FOR-REVIEW/LAMAGUE_STATE_DOSSIER.md:3`, `FOR-REVIEW/FULL_FRAMEWORK_REVIEW_CHECKLIST.md:88`, and `BATCH28` (three lines). <br>- The two tracked `.log` files (`Forge_07/results/verification_lab.log`, `earned_trust_cycle_009/full_tests.log`) carry 0 absolute paths and 0 emails. |
| F9 | MEASURED (counts only) | **`15_PERSONAL_VAULT/`'s intent conflicts with its own files.** It has 21 tracked files. Its `README.md` says "Public archive — intentionally so" (audited 2026-04-28), while its `.gitkeep_private` says the contents are "for us". A category census found: family 1 file, money 1, health/therapy 2 files (one is a "not clinical" disclaimer, and the other proposes CASCADE as a therapy model, which is a research idea, not a disclosure), and place names in 8 files. No hit read as a private medical, financial or family disclosure. That is a pattern judgment, and the owner should confirm it. |
| F10 | MEASURED | **The private constitution is held correctly.** `25_SOL_PROTOCOL_ARCHITECTURE/SOL_PRIME.md` is gitignored (`.gitignore:39`) and absent from the tree. `_PROPRIETARY/` is ignored. Neither appears in `git ls-files`. |
| F11 | MEASURED (census) | **392 untracked files** are waiting: 374 are closed-loop agent lab logs under `99_ARCHIVE/`, and the rest are the FOR-REVIEW ledgers and the new tests. Any commit of FOR-REVIEW needs the F8 scrub first. |

## Repairs (working tree)

1. **`SECURITY.md`** (maintained, edited in place; backup in `$S/rv35_bak/`):
   - **Dated RV35 note.** It says that both reporting routes are dead today, and why (PVR off, NXDOMAIN). It tells a researcher to open a public issue that says only "security contact needed", never one with exploit detail.
   - **Scope update.** All 11 console scripts, with `pyproject.toml` named as the list of record. The assurance runtime. Both MCP servers, noting that `sol_workspace_mcp.py` writes files. The `cascade-pc` app and its port 7432 API.
   - **Strike-through.** "Nothing here should be relied on as a security boundary" is struck with a dated reason. Guard or gateway bypass, receipt forgery or replay, checkpoint skip, workspace-MCP path escape or unauthenticated write, and cross-origin reads of the cascade-pc API are now explicitly security findings. `lycheetah.check()` scores stay a correctness question, as before.
2. Nothing else was edited. Every other finding is an owner decision or an external setting.

## Witnesses

| Witness | Result |
|---|---|
| `python3 tools/verify-links.py` after the edit | 1867 files, 2736 links, 0 dead outside the archive (22 inside `99_ARCHIVE`, unchanged) |
| `git diff --stat SECURITY.md` | 28 insertions, 4 deletions. Every original line survives, except the scope bullets that were extended and the struck sentence, which is kept under a strike. |
| PVR probe | `{"enabled":false}`, read live through `gh api` on 2026-10-22 |
| DNS | `lycheetah.nz` Status 3, `lycheetah.org` Status 3 (NXDOMAIN), via `dns.google/resolve` |
| Python suite | not re-run. This batch changed one Markdown file, and the RV34 run (1540 passed, 1 skipped, 1 xfailed) stands. |

## G-items for Mac

- **G-RV35-1 (most urgent, one click):** enable private vulnerability reporting. Use Settings → Code security → Private vulnerability reporting, or run `gh api -X PUT repos/Lycheetah/Lycheetah-Framework/private-vulnerability-reporting`. That revives route 1 at once. After that, the RV35 note in `SECURITY.md` can be shortened to point at the advisory link alone.
- **G-RV35-2:** choose **one working contact address** and decide where it goes. It would replace the address in `SECURITY.md`, `CODE_OF_CONDUCT.md` and `pyproject.toml`, and the `lycheetah.org` address in the 7 paper and pitch files. Either renew `lycheetah.nz` or pick an address you control. Sol does not pick an email for you.
- **G-RV35-3:** turn on Dependabot alerts and security updates. Optionally add `pip-audit` and `npm audit --omit=dev` jobs to CI, but CI is billing-locked (G-RV33-1).
- **G-RV35-4:** run a **history secret scan** once (`gitleaks detect` or `trufflehog git file://.`). The tree is clean, but the history has never been scanned in this review.
- **G-RV35-5:** the private repository's name in 7 public files (F6). Options:
  - (a) leave it, since it is already public and harmless alone;
  - (b) replace it with "the private app repository" going forward, and change `reflexive_audit.py`'s default to require the env var.

  Sol's stance: **(b) for the code default, (a) for the prose.** Rewriting history notes to hide a name that is already in history buys nothing.
- **G-RV35-6:** the personal gmail addresses in public papers (F7). Keep them, or move to the contact address from G-RV35-2.
- **G-RV35-7:** `15_PERSONAL_VAULT/`: public archive or private? Its README and its private marker disagree (F9). Whichever you choose, one of the two files should change to match.
- **G-RV35-8:** before any commit of `FOR-REVIEW/`, scrub the home-path lines (F8). There is also a proposal for root `AGENTS.md:3`: replace the absolute path with `~/`-relative wording. That is a proposal only, under the RV27 boundary.
