# D-1.1 Repo Cleanup + Layer-Tagged Folder Rename — Sonnet Handoff Plan

**Author:** Opus 4.7 (design call) → **Executor:** Sonnet 4.6 (mechanical execution)
**Date drafted:** 2026-04-26
**Scope:** One commit. Folder rename + root cleanup + global link rewrite + audit. No content edits.

---

## Why this exists

Root has 52 loose files. Folder numbering (01_CASCADE … 10_HARMONIA) does not encode the layer architecture. Mac asked for "folders with a tier next to them like a connecting link" and "clean up repo." This plan does both in a single atomic operation with link integrity preserved.

---

## Design decisions (already made — do not re-litigate)

1. **Naming scheme: Option B — layer suffix, keep current numbers.** Format: `NN_NAME_LX`.
   - Reason: keeps existing sort order, keeps the audit script's number-based assumptions, adds the layer as the visible connecting link, single-pass rewrite.
2. **Root cleanup: bucket by function into new `28_DEFENSE/`, `29_GOVERNANCE/`, `30_MAPS/`.** Keep only canonical entry points at root.
3. **One commit.** Rename + move + link rewrite + audit verification all in one atomic change.

---

## Phase 1 — Folder renames (framework dirs only)

| Current | Layer | New name |
|---|---|---|
| `01_CASCADE_L4/` | 4 | `01_CASCADE_L4/` |
| `02_AURA_L3/` | 3 | `02_AURA_L3/` |
| `03_LAMAGUE_L1/` | 1 | `03_LAMAGUE_L1/` |
| `04_TRIAD_L2/` | 2 | `04_TRIAD_L2/` |
| `05_MICROORCIM_L5/` | 5 | `05_MICROORCIM_L5/` |
| `06_EARNED_LIGHT_L0/` | 0 | `06_EARNED_LIGHT_L0/` |
| `07_ANAMNESIS_L0/` | 0 | `07_ANAMNESIS_L0/` |
| `08_INTEGRATIONS/` | — | **leave as-is** (not a framework) |
| `09_CHRYSOPOEIA_L4/` | 4 | `09_CHRYSOPOEIA_L4/` |
| `10_HARMONIA_L6/` | 6 | `10_HARMONIA_L6/` |

All other numbered dirs (11_ … 27_, 99_) leave as-is. They are not framework layers.

---

## Phase 2 — Root file moves

Create `28_DEFENSE/`, `29_GOVERNANCE/`, `30_MAPS/`.

**Keep at root** (entry layer + canonical pointers):
```
README.md  00_Sovereign_Index.md  CITATION.cff  CONTRIBUTING.md
QUICKSTART.md  FIVE_MINUTE_BRIEF.md  EXPLORE_WITH_AI.md
llms.txt  ai-meta.json  requirements.txt
THE_SOL_PROTOCOL.md  AGENTS.md
```

**Move to `28_DEFENSE/`:**
```
28_DEFENSE/ADVERSARIAL_AUDIT_REPORT.md  28_DEFENSE/ATTRIBUTION_REQUIREMENTS.md  28_DEFENSE/CITATIONS.md
28_DEFENSE/CLAIMS.json  28_DEFENSE/CLAIMS.schema.json  28_DEFENSE/CLAIMS_README.md
28_DEFENSE/COLD_ROOM_VERIFICATION.md  28_DEFENSE/COUNTER_CODEX.md
28_DEFENSE/D1_DEFENSE_PROTOCOL_PLAN.md  28_DEFENSE/D1_REPO_CLEANUP_PLAN.md
28_DEFENSE/DEFENSE_BRIEF.md  28_DEFENSE/DEFENSE_INDEX.json  28_DEFENSE/DEFENSE_VERSION.md
28_DEFENSE/EVIDENCE_LADDER.md  28_DEFENSE/FAILURE_MUSEUM.md  28_DEFENSE/FALSIFICATION_REGISTER.md
28_DEFENSE/NOVEL_CONTRIBUTIONS.md  28_DEFENSE/OBJECTIONS_REGISTRY.md  28_DEFENSE/PRIOR_ART.md
28_DEFENSE/READING_PATHS.md  28_DEFENSE/REPRODUCIBILITY_REPORT.md  28_DEFENSE/SCOPE_BOUNDARY.md
28_DEFENSE/TESTABILITY_MANIFEST.md  28_DEFENSE/TRANSLATION_CODEX.md
```

**Move to `29_GOVERNANCE/`:**
```
29_GOVERNANCE/GOVERNANCE.md  29_GOVERNANCE/GOVERNANCE_AND_ETHICS.md  29_GOVERNANCE/LIVING_CODEX_PROTOCOL.md
29_GOVERNANCE/PUBLICATION_PIPELINE.md  29_GOVERNANCE/OPEN_PROBLEMS.md  29_GOVERNANCE/EMPIRICAL_INVENTORY.md
29_GOVERNANCE/CODEX_ELEVATION_PLAN.md
```

**Move to `30_MAPS/`:**
```
30_MAPS/COHERENCE_REGISTER.md  30_MAPS/COMPOSITION_MAP.md  30_MAPS/FORMAL_SPINE.md
30_MAPS/LINEAGE_MAP.md  30_MAPS/ONTOLOGY.md  30_MAPS/PROVENANCE_INDEX.md
30_MAPS/VISUAL_ATLAS.md  30_MAPS/CURRICULUM.md  30_MAPS/CODEX_DISTILLATION.md
30_MAPS/ARCHITECTS_GUIDE.md  30_MAPS/PRACTITIONERS_MANUAL.md
```

If a file isn't in any list above, leave at root and flag in the final report.

---

## Phase 3 — Global link rewrite

Every internal reference to a renamed folder or moved file must update. Targets to scan:

- All `*.md` in repo (excluding `99_ARCHIVE/`, `__pycache__/`, `.git/`, `dist/`, `*.egg-info/`)
- All `*.json` in repo (especially `28_DEFENSE/CLAIMS.json`, `28_DEFENSE/DEFENSE_INDEX.json`, `ai-meta.json`)
- `llms.txt`
- `CITATION.cff`
- Python source if it references repo paths (`generate_defense_bundle.py`, etc.)

**Rewrite rules** (apply in order):

1. `01_CASCADE_L4/` → `01_CASCADE_L4/`
2. `02_AURA_L3/` → `02_AURA_L3/`
3. `03_LAMAGUE_L1/` → `03_LAMAGUE_L1/`
4. `04_TRIAD_L2/` → `04_TRIAD_L2/`
5. `05_MICROORCIM_L5/` → `05_MICROORCIM_L5/`
6. `06_EARNED_LIGHT_L0/` → `06_EARNED_LIGHT_L0/`
7. `07_ANAMNESIS_L0/` → `07_ANAMNESIS_L0/`
8. `09_CHRYSOPOEIA_L4/` → `09_CHRYSOPOEIA_L4/`
9. `10_HARMONIA_L6/` → `10_HARMONIA_L6/`
10. For each moved file `FOO.md` → prefix with target dir. Match on `(^|[\s\(\[])FOO\.md([\s\)\],:]|$)` to avoid matching unrelated tokens. Be careful: `28_DEFENSE/CLAIMS.json` is referenced bare in many places — rewrite to `28_DEFENSE/CLAIMS.json`.

**Use sed-style global replace, but verify each file diffs sensibly before committing.** If a single-word filename like `29_GOVERNANCE/GOVERNANCE.md` collides with prose mentions, scope the rewrite to markdown link syntax `](29_GOVERNANCE/GOVERNANCE.md)` and bare-line references only.

---

## Phase 4 — Audit

Run the existing link audit (whatever script verified the 87/0 broken links earlier in D-1.1). Acceptable outcomes:

- **0 broken links** → proceed to commit
- **>0 broken links** → fix every one before commit. Do not commit a partial cleanup.

Spot-check by hand:
- `README.md` Defense Layer section — all links resolve
- `llms.txt` and `ai-meta.json` — paths point to new locations
- `28_DEFENSE/CLAIMS.json` `evidence_paths` — all resolve
- `28_DEFENSE/DEFENSE_INDEX.json` — all 18+ doc paths resolve

---

## Phase 5 — Commit + push

Single commit. Message:

```
D-1.1 cleanup: layer-tagged framework folders + root reorganization

- Framework folders renamed NN_NAME → NN_NAME_LX where X is the layer
  (Layer 0 = EARNED_LIGHT/ANAMNESIS, L1 = LAMAGUE, L2 = TRIAD,
   L3 = AURA, L4 = CASCADE/CHRYSOPOEIA, L5 = MICROORCIM, L6 = HARMONIA)
- Root .md files bucketed into 28_DEFENSE/, 29_GOVERNANCE/, 30_MAPS/
- All internal links rewritten in same commit; audit clean
- Entry layer (README, QUICKSTART, FIVE_MINUTE_BRIEF, llms.txt, ai-meta.json,
  THE_SOL_PROTOCOL, AGENTS, CITATION, CONTRIBUTING) preserved at root

No content changes. Structural refactor only.
```

Then `git push`.

---

## What Sonnet must NOT do

- Do not edit content of any file beyond path rewrites
- Do not invent new buckets or move files not on the list above
- Do not rename `08_INTEGRATIONS/` (not a framework layer)
- Do not rename support dirs `11_` through `27_` (not framework layers)
- Do not touch `99_ARCHIVE/`, `__pycache__/`, `.git/`, `dist/`, `lycheetah_framework.egg-info/`
- Do not commit if audit shows any broken link
- Do not skip the audit
- Do not split into multiple commits — atomic only

---

## What Sonnet should report back

After push:
1. Commit SHA
2. Number of files renamed
3. Number of files moved
4. Number of internal references rewritten
5. Audit result (X/Y links checked, 0 broken)
6. Anything ambiguous that was left at root with reasoning

---

*This plan is the atomic unit. Execute as one operation.*

---

## C-1.1 ADDENDUM (2026-04-28)

The C-1.1 Reforge pass added six new root-level files that were not in the original bucket lists. Bucketing decisions for these files, to be applied as part of the cleanup commit:

**Keep at root** (entry/legal):
```
LICENSE
```

**Move to `28_DEFENSE/`** (defence-layer artefacts):
```
28_DEFENSE/C1_REFORGE_RECON.md      ← Reforge reconnaissance, mirror of D1_DEFENSE_PROTOCOL_PLAN
28_DEFENSE/REFORGE_REGISTER.md      ← Per-edit log, mirror of DOWNGRADE_REGISTER
28_DEFENSE/SCOPE_DECLARATION.md     ← Negative-space declaration, defends scope
28_DEFENSE/SYNTHESES.md             ← Cross-framework syntheses, defensive connective tissue
28_DEFENSE/CLAIM_STATUS_LEDGER.md   ← (already on the original 28_DEFENSE list — confirm)
```

**Move to new `31_EMPIRICAL/`** (the third anchor — its own bucket):
```
31_EMPIRICAL/E1_EMPIRICAL_PROGRAM.md
```

(`31_EMPIRICAL/` is created during this cleanup and reserved for E-1.x preregistrations, study results, and replication reports as they accumulate.)

**Existing `28_DEFENSE/` list remains unchanged** — `CLAIM_STATUS_LEDGER` was already on it.

**Phase 3 link rewrite addendum.** Add these rewrite rules:

```
LICENSE                        → LICENSE                        (stays at root)
28_DEFENSE/C1_REFORGE_RECON.md            → 28_DEFENSE/C1_REFORGE_RECON.md
28_DEFENSE/REFORGE_REGISTER.md            → 28_DEFENSE/REFORGE_REGISTER.md
28_DEFENSE/SCOPE_DECLARATION.md           → 28_DEFENSE/SCOPE_DECLARATION.md
28_DEFENSE/SYNTHESES.md                   → 28_DEFENSE/SYNTHESES.md
31_EMPIRICAL/E1_EMPIRICAL_PROGRAM.md        → 31_EMPIRICAL/E1_EMPIRICAL_PROGRAM.md
```

**Existing references that need updating after the move** (audit will catch any missed):

- `28_DEFENSE/DEFENSE_VERSION.md` — pointer to `28_DEFENSE/REFORGE_REGISTER.md` updates to new path
- `28_DEFENSE/CLAIM_STATUS_LEDGER.md` (header) — pointer to `28_DEFENSE/C1_REFORGE_RECON.md` updates
- `28_DEFENSE/REFORGE_REGISTER.md` (preamble) — pointer to `28_DEFENSE/C1_REFORGE_RECON.md` updates
- `28_DEFENSE/SYNTHESES.md`, `28_DEFENSE/SCOPE_DECLARATION.md` — internal links to canonical body docs may need updates if those docs move
- `31_EMPIRICAL/E1_EMPIRICAL_PROGRAM.md` — references to `28_DEFENSE/SCOPE_DECLARATION.md`, `28_DEFENSE/CLAIM_STATUS_LEDGER.md`, `28_DEFENSE/FAILURE_MUSEUM.md` need path updates
- `MEMORY.md` and project memory files outside the repo — informational only, not blockers

**C-1.1 cross-repo verification (completed 2026-04-28):** lycheetah and lycheetah-mobile READMEs reference the Codex only via stable GitHub URLs (`https://github.com/Lycheetah/Lycheetah-Framework`), not internal paths. They are immune to folder renames and require no edits as part of this cleanup.

---

## EXECUTION READINESS — 2026-04-28

This plan is now complete and executable. Recommended approach: a single focused session (Opus or Sonnet, atomic commit) following the plan exactly. Estimated complexity: ~15 folder/file operations, ~200 link rewrites, ~30 minutes of audit.

Mac fires execution when ready.

