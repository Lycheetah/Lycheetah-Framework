# Evidence report — SXP-L v1.9 Natural Reference Forge

**Execution date:** 18 October 2026. All measurements below refer to local, deterministic research artifacts.

- **71/71 Python unittest methods passed** in a single focused run: 22 v1.9, 20 v1.8, and 29 inherited continuity/perspective tests. See `TEST_RESULTS_v1.9.txt`.
- The v1.9 test suite generated **400 valid seeded conversations**, checked their expansion and reference interpretation against a limited independently written reader, and confirmed no inferred authorization.
- A separately generated **80-scenario synthetic viewpoint fixture** yielded **80/80** agreement between the main parser and limited independent lexical reader. A deliberately naïve rule binding every `mi/ti` to the *current* questioner was correct on **40/80** balanced cases. This is a constructed baseline, not a mature natural-language parser.
- Both new roots passed the inherited CV spelling screen and a one-edit spelling-collision check. These are written-form screens, not listening data.
- A specific `kelunaro` clause shrank from 16 whitespace words in expanded v1.8 to 13 in v1.9 (18.75%). The embedded clause alone shrank from 8 to 5 (37.5%). These are **not** naturalness, reading speed, tokenization or compression benchmarks.
- Browser teaching UI passed a headless Chromium interaction/export test. Its exported file was separately accepted by `reference19.parse_native`. See `BROWSER_QA_v1.9.png` and `browser_smoke19.py`.
- The original v1.8 ZIP is saved byte-identically under `history/RELEASE_v1.8_ORIGINAL.zip`. The inherited runtime source is a copy, not modified code.

## Known limits

No independent human participants, no audio/listening studies, no deployment, no direct evaluation versus a mature formal discourse parser. Only **three transitive predicates** are supported under the new binder. It explicitly rejects nested or third-person scoped clarifications in this subset. The reader called `oracle19` checks a limited class of bindings and is not a separate full syntactic semantics implementation. SHA-256 consistency checks do not prove identity or prevent an actor replacing all files together.

The primary contribution is **an explicit, recoverable short-viewpoint encoding within an existing experimental grammar**. The phenomenon of perspective-sensitive pronouns has established linguistic precedent.
