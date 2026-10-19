# GitHub Integration Plan (Non-Destructive)

**Confirmed target repository:** https://github.com/Lycheetah/Lycheetah-Framework  
**Confirmed working branch at review:** `master`. **No writes were performed by the assistant.**

## Upload destinations already aligned to the repo structure

| Incoming folder (under `repo_upload/`) | Reason |
|---|---|
| `35_ABSTRACT_AND_GENERATIVE/SOVEREIGN_WILL/` | Philosophical and symbolic work. Existing `35_ABSTRACT_AND_GENERATIVE/REGISTER.md` asks for epistemic/generative status separation. |
| `papers/agent-safety/sovereign-choice-research/` | Reproducible agent governance research, matching existing `papers/agent-safety/`. Kept separate from active production source. |
| `LYCHEETAH_MYTHOS/SCRIPTURES_AND_STORIES/ORIGINAL_NARRATIVES/` | Original creative story. Intentionally separate from confirmed epic canon and technical documentation. |

The three new destination subfolders are **proposed**, not pre-existing canonical locations. They respect the actual existing parent directories inspected in the GitHub repository. Moving or renaming them remains the human maintainer's decision.

## Safe upload

Suggested shell actions from a *reviewed local checkout*:

```bash
# Unzip this handoff locally, inspect START_HERE.md and tree, then:
cd /path/to/Lycheetah-Framework
# Ideally create a branch for review before copying anything.
git switch -c research/sovereign-will-forges-1-8
# Then copy the *contents* of repo_upload/ preserving the matching relative paths.
# Review changes before stage/commit.
git status --short
git diff --check
```

This handoff has no live permission to push or merge. The copy itself should be deliberate: avoid combining it with unrelated in-progress work. If the destination paths already exist, **diff first** rather than overwriting.

## Integrations to review AFTER landing

- Link the philosophical overview from `35_ABSTRACT_AND_GENERATIVE/README.md` and, if suitable, cross-reference `05_MICROORCIM_L5/README.md`; don't overwrite either.
- Link the engineering packet from `papers/agent-safety/README.md`; preserve current `CommitFence` and Sovereign Harness as the primary baseline.
- Link the original narrative from an existing story index only if its fictional/canonical status is made explicit.
- Consider keeping the `original_forge_archives/` ZIPs outside git or in a dedicated release asset: the expanded repo tree already contains the primary files. They are provided for faithful archival preservation and recovery.
- Upstream mirrors included in Forges V/VI are provenance snapshots; don't replace real upstream sources with them.

## Suggested commit message

`docs(research): archive sovereign-will philosophy, agent-choice experiments and ninth-road story`

## Explicit limitations

No canonical status, peer-review status, production safety certification, scientific validation of free will, or real user study is claimed. Code tests are self-authored, largely synthetic, and bounded to local execution.
