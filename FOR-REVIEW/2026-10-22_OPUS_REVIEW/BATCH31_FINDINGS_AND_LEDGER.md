# BATCH 31 — RV32 · Desktop and application reality (`cascade-pc/`, `27_SOL_AI_APP/`)

**Reviewer:** Sol (Claude Opus 5.5, xhigh) · **Date:** 2026-10-22 · **Branch:** `review/full-framework-2026-10-20`, working tree only, nothing staged or committed.

## Coverage, stated honestly

- **Read:** `main.js`, `preload.js`, `src/scoring/ai.js`, `tests/scoring-provider.test.mjs`, `package.json`, the lock's root and electron entries, `.github/workflows/build.yml`, the Settings API section, the About and footer links, `cascade-pc/README.md` (head), and `27_SOL_AI_APP/README.md`.
- **Swept, not read whole:** the React components, grepped for `innerHTML`, `dangerouslySetInnerHTML`, `window.open`, `target="_blank"`, key storage and CSP.
- **DID NOT RUN:**
  - `npm ci`, `vite build`, `electron-builder`, launching the app, or any rendered screen. `node_modules` is absent, and installing Electron is a heavy network fetch that was outside this batch.
  - `npm audit`, because it needs network.
  - Any provider call (review-only authority).
- **Consequence:** nothing here says the app builds, renders, or runs on any platform.

## Findings

| # | Status | Finding |
|---|---|---|
| F1 | MEASURED (test) | **The local API could be read through DNS rebinding.** `main.js` started `127.0.0.1:7432` at launch (`app.whenReady → startApiServer`) with no auth and no Host check. The comment said "localhost only", but binding to localhost does not stop a web page whose own hostname has been rebound to 127.0.0.1: the browser treats the reply as same-origin. That page could then read every pyramid, block body, onion layer and the audit log. A test with `Host: attacker.example:7432` received the data when the guard was mutated out, and receives 403 on the tree. |
| F2 | DERIVED (code + Electron default) | **Remote pages could carry the preload bridge.** `AboutView` calls `window.open(url,'_blank')`, and the footer uses `target="_blank"`. There was no `setWindowOpenHandler` and no `will-navigate` guard. By default, Electron child windows inherit the parent's `webPreferences`, including `preload`, so a GitHub page, or anywhere it navigates, would receive `window.cascade`: delete, export-to-path dialogs, and the full DB. The default-inheritance claim is from memory of Electron behaviour, not re-read this session; the fix is correct either way. |
| F3 | MEASURED (`gh`, owner account) | **Dead links in the app.** The About and footer links point to `github.com/Lycheetah/CODEX_AURA_PRIME`, which does not resolve even for the owner account. The About text also claimed "all public repositories". |
| F4 | MEASURED (`gh`) | **Dead README download link.** `cascade-pc/README.md` links `releases/tag/v0.1.0`, but that tag is `V.0.1.0`. The latest release is v0.3.0 with `CASCADE.CICADA.TOOL.0.3.0.exe`. |
| F5 | MEASURED (mutation) | **The provider-race repair holds.** `consensusScore` passes each provider per request (`ai.js:203`). With that argument removed, all 3 mocked tests fail; on the tree all 3 pass. Scope: these are mocks, not real provider integration. |
| F6 | DERIVED | **`cascade-pc/.github/workflows/build.yml` never runs.** GitHub only reads workflows from `.github/workflows/` at the repository root, and none of the three root workflows mention `cascade-pc`. The build matrix and the release job are inert in this repository. They may be live in the separate `cascade-cicada-tool-` repo (UNVERIFIED). |
| F7 | MEASURED | **API keys are stored in plaintext.** They sit in renderer `localStorage` (`cascade_*_key`), which persists unencrypted under userData. Anthropic calls use `anthropic-dangerous-direct-browser-access`. This is acceptable for a single-user, bring-your-own-key desktop tool, but it is unstated. Electron `safeStorage` behind IPC would be the upgrade. |
| F8 | MEASURED | **Smaller defects:** no CSP in `index.html`; Electron `^29.1.4` (lock 29.4.6), a major that has been out of support for a long time (support dates from memory); the `build` script uses Windows `set` syntax (a silent no-op under sh); footer "TCCT v0.1" against package 0.3.0; lock root `version` 0.1.0 against 0.3.0. Dependency sets and ranges match the lock exactly. |
| F9 | MEASURED | **`27_SOL_AI_APP/` is a plan, not an implementation.** It holds a single April 2026 README ("[ACTIVE] — Planning complete, build starts when API credits available"). No code here builds the mobile app. |

## Repairs (working tree)

1. **New `cascade-pc/local-api.js` (CJS).** The request handler now lives outside Electron so it can be tested.
   - **Refused:** any method except GET (405); a Host that is not `127.0.0.1:7432` or `localhost:7432` (403); and any `Origin` that is not `http://localhost` or `http://127.0.0.1` (403, `null` included).
   - **Allowed:** scripts and curl send no Origin and pass.
   - Endpoints and output are unchanged.
2. **`cascade-pc/main.js`.**
   - Uses `createApiHandler(() => db)`, `PORT` and `ENDPOINTS`.
   - Adds `setWindowOpenHandler`: http(s) URLs go to `shell.openExternal`, and every child window is denied.
   - Adds a `will-navigate` guard that blocks the window from leaving its loaded URL.
   - `node --check` passes. The navigation guard is **UNVERIFIED at runtime** because Electron was not launched.
3. **New `cascade-pc/tests/local-api.test.mjs`.** Four tests:
   - local reads pass;
   - a rebound Host is refused and the body leaks nothing;
   - a foreign or `null` Origin is refused;
   - POST gets 405.
4. **`cascade-pc/package.json`.** New `"test"` script runs both node test files. `test:scoring` is kept.
5. **Links.** `src/App.jsx` and `src/components/AboutView.jsx` now point to the public `Lycheetah-Framework` repo. `cascade-pc/README.md` now links `releases/latest` (v0.3.0), with a dated note.
6. **`27_SOL_AI_APP/README.md`.** Added a dated RV32 note: plan only, no code here, the April status is historical. The private app repo is not named.

## Witnesses

| Witness | Result |
|---|---|
| `node --test tests/*.test.mjs` (tree) | 7 pass, 0 fail |
| Mutation: `refusal()` disabled, which equals the old behaviour | 3 fail, 1 pass. The local-read control passes, as it should. |
| Mutation: Origin check alone disabled | 1 fail (the foreign-origin test). The Host and Origin checks are each witnessed. |
| Mutation: provider not passed per request (the old race) | 3 of 3 fail |
| Python suite | 1539 passed, 1 skipped, 1 xfailed, 1 warning. The node tests are not in it. |

## G-items for Mac

- **G-RV32-1:** run the app once (`npm ci && npm run dev`). Click both About links: they should open in your browser, never in an app window. Then `curl -H 'Host: x.example:7432' 127.0.0.1:7432/status` should return 403. That is the real witness for F1 and F2.
- **G-RV32-2:** should the local API **default off**? It starts at launch, and the Settings copy says so. The guard closes the browser attack, but any local process can still read everything. Default-off with a toggle is the conservative choice.
- **G-RV32-3:** move key storage to Electron `safeStorage` through IPC (F7), and add a CSP (F8). Both need a running app to witness.
- **G-RV32-4:** decide where the build workflow lives (F6): the separate `cascade-cicada-tool-` repo, or a root workflow here. Also decide whether to add `node --test cascade-pc/tests` to the root `ci.yml`. That second part is RV33 territory and is proposed, not applied.
- **G-RV32-5:** Electron major upgrade and lock `version` bump (F8): a dependency change that needs the build witness.
