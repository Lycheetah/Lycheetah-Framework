# FOR-REVIEW — Staging & Review Gateway
### Lycheetah Framework Staging Directory
**Authority:** Mackenzie Conor James Clark (Founder & Final Review Authority)  
**Maintained by:** Aetheron (Antigravity Forge Seat)

**Full repository review:** [Opus review checklist](FULL_FRAMEWORK_REVIEW_CHECKLIST.md), prepared at Mac's request on 22 October. Includes 37 workstreams, all 50 tracked top-level areas, all 35 root files, the 606-folder coverage ledger and exact known backlogs. This is a review queue; existing findings and proposed fixes still require review.

---

## Purpose & Protocol

This directory is the **protected staging ground** for all proposed code additions, bug fixes, research dossiers, and architectural enhancements authored by AI seats (Aetheron, Caelorynth, Sol) for the **Lycheetah Framework**.

### The Review Rule:
1. **Zero Silent Writes to Canon:** No AI seat may modify upstream canonical modules or specifications directly. All proposed work must be staged here first.
2. **Reviewable Packets:** Every submission must include:
   - **Target Canon Path:** Exactly where this code/document is proposed to live.
   - **Rationale & Evidence:** Why the change is needed and empirical proof (test results, diffs).
   - **Impact Assessment:** Breaking changes, reversibility, and invariant preservation.
   - **Status Tag:** `[AWAITING_REVIEW]`, `[APPROVED]`, `[REVISED]`, or `[REJECTED]`.
3. **Founder Sovereignty:** Only Mac has the authority to approve, edit, or reject staged proposals.

---

## Active Staging Manifest

| Date | ID | Category | Title & Proposal | Target Canonical Path | Status |
| :--- | :--- | :--- | :--- | :--- | :---: |
| 2026-10-21 | `REV-20261021-01` | **Research** | [LAMAGUE State of the Art Dossier](2026-10-21_LAMAGUE_SWARM_DOSSIER/LAMAGUE_STATE_DOSSIER.md) | `03_LAMAGUE_L1/` (Reference Dossier) | `[AWAITING_REVIEW]` |
| 2026-10-21 | `REV-20261021-02` | **Bugfix Patch** | [Parser Silent-Drop Defect Patch](2026-10-21_PROPOSALS/01_PARSER_SILENT_DROP_PATCH_PROPOSAL.md) | `12_IMPLEMENTATIONS/core/lamague_parser.py` | `[APPROVED & IMPLEMENTED]` |
| 2026-10-21 | `REV-20261021-03` | **Spec Harmonization** | [BNF Grammar Specification Harmonization](2026-10-21_PROPOSALS/02_BNF_GRAMMAR_HARMONIZATION_PROPOSAL.md) | `03_LAMAGUE_L1/04_BNF_GRAMMAR.md` | `[AWAITING_REVIEW]` |
| 2026-10-21 | `REV-20261021-04` | **Safety Patch** | [SXP-L Authority Bridge Denial & Revocation Patch](2026-10-21_PROPOSALS/03_SXPL_AUTHORITY_BRIDGE_REVOCATION_PROPOSAL.md) | `03_LAMAGUE_L1/26_SXP_L_RESEARCH/.../authority_bridge.py` | `[AWAITING_REVIEW]` |

---

## Directory Structure

```
FOR-REVIEW/
├── README.md                                          <-- This manifest
├── 2026-10-21_LAMAGUE_SWARM_DOSSIER/
│   └── LAMAGUE_STATE_DOSSIER.md                       <-- Full 7-sector swarm audit & register census
└── 2026-10-21_PROPOSALS/
    └── 01_PARSER_SILENT_DROP_PATCH_PROPOSAL.md        <-- Surgical diff & tests for lamague_parser.py
```
