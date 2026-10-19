# LYCHEETAH — Sovereign Choice Forge V

**18 October 2026 · Tested local GitHub integration · Philosophy + working code · Not deployed**

> An instruction is not perpetual ownership of the person who gave it.

## Result

The Forge IV integration tests have now run against the actual upstream `CommitFence` and `Action` implementations, with source verified by Git blob hash. Forge V additionally shows how a companion intention version can be written atomically with the existing authority-generation fence *in the same database* rather than a second journal. Existing `issue_handle` and `commit` methods remain unchanged.

This is an experimental trusted-host adapter, **not** a claim of authenticated consent, real-world provider cancellation, personal free will measurement, or production safety.

## Contents

- `choice_ledger.py`: atomic intention revision, withdrawal and exact-action endorsement in upstream SQLite finality store.
- `tests/test_choice_ledger.py`: adversarial tests against the SHA-verified GitHub upstream source.
- `compare_crash_window.py`: reproducible failed-update comparison with Forge IV's separate database journal.
- `comparison_results.json`: numerical result of that comparison.
- `prototype/sovereign_choice_lab.html`: offline interactive educational interface, no tool calls or external effects.
- `docs/RESEARCH_FINDINGS.md`: observations, limitations, threat model, adoption path, and falsifiers.
- `upstream_mirror/`: **unmodified** SHA-verified current source files, copied from public Lycheetah GitHub; MIT licence and attribution included.
- `lineage/FORGE_IV_COMPLETE.zip`: preserved complete Forge IV handoff, including earlier Forge archives.
- `results.json`, `MANIFEST_SHA256.json`: test/evidence bookkeeping and deterministic file digests.

## Reproduce

Use Python 3.10+ standard library:

```sh
cd sovereign_choice_forge_v
python -m unittest discover -s tests -v
python compare_crash_window.py
```

Previous Forge IV suites can be run separately with `LYCHEETAH_REPO_ROOT` pointed to `upstream_mirror`:

```sh
cd ../sovereign_choice_forge_iv
LYCHEETAH_REPO_ROOT=../sovereign_choice_forge_v/upstream_mirror python -m unittest discover -s tests -v
```

## Scientific scope

`MICROORCIM-event` is a philosophical object naming the moment of redirection; this code implements an operational *authorization* property and does not infer anything about consciousness, freedom, identity or worth. The real remote-provider and trusted-host boundaries remain unresolved; review findings before reuse.

**No GitHub files were changed.**
