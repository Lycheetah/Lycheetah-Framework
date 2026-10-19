# Sovereign Choice Research — Forges II–VIII

**Status:** Archived reproducible prototypes and authored fixtures. **Not production infrastructure.**

This directory is deliberately under `papers/agent-safety/`, rather than a replacement for the active Sovereign Harness or `CommitFence` in the main repository.

Contents of `forges/forge_ii/` through `forges/forge_viii/` are extracted **primary source files** from the original Forge ZIP archives. Historical nested copies are omitted from this tree; the seven unchanged source ZIPs are preserved alongside it under [`source_archives/`](source_archives/).

## Reproduce the complete local test lineage

From this directory, with Python 3.10+ and `cryptography` installed:

```bash
python3 verify.py
```

The integration runner works in temporary copies. It runs Forge II (28 tests),
Forge III (37), and the preserved original Forge VIII archive's replay (142,
covering Forges IV–VIII). This is 207 test executions with historical overlap;
the original 142 count alone does **not** include Forges II and III. Node.js
enables the archive's JavaScript syntax/parity checks; availability and individual
check results are reported separately.

The extracted `forges/` tree omits nested ZIP duplication. Its historical
`run_verification.py` scripts still expect those missing nested files: use the
integration runner above or unpack the corresponding original ZIP into a
disposable directory before invoking an archived verification script.

For local Forge VIII tests in this extracted tree:

```bash
cd forges/forge_viii
python -m unittest discover -s tests -v
```

**Creator:** Mackenzie Conor James Clark / Lycheetah Framework. Integration and
reproduction assisted by Caelorynth, an AI coding assistant.

[Philosophical charters](../../../35_ABSTRACT_AND_GENERATIVE/SOVEREIGN_WILL/README.md)
and [The Ninth Road Beneath the Sleeping Stars](../../../LYCHEETAH_MYTHOS/SCRIPTURES_AND_STORIES/TEXTS/ORIGINAL_NARRATIVES/LYCHEETAH_The_Ninth_Road_Beneath_the_Sleeping_Stars.md)
have separate source homes. The story is fiction; the charters are proposals.

[Dated integration review](../../../28_DEFENSE/RELEASE_AUDIT_2026-10-19.md) ·
[Import manifest](../../../28_DEFENSE/RESEARCH_INTAKE_2026-10-19_SOURCE_MANIFEST.json).
Original notes under `intake/` retain their supplied paths and upload status.

**Evidence ceiling:** Local source integration and self-authored tests. No human user study, independent security audit, or production effect execution.
Forge VII retains the 18/18 tie with a strong conventional goal-aware baseline;
Forge VIII's 7/8 differing outcomes concern fictional graphs and include an
unchanged negative control. Neither measures a person's free will or dependency.
See [the supplied limitations](../../../35_ABSTRACT_AND_GENERATIVE/SOVEREIGN_WILL/VALIDATION_AND_LIMITATIONS.md).
