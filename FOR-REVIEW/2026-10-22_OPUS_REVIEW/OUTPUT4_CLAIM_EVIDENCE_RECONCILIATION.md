# Output 4 — Claim / evidence reconciliation (all 71)

**Reviewer:** Sol (Claude Opus 5.5) · **Date:** 2026-10-23 · Generated from `28_DEFENSE/CLAIMS.json` and the RV19 overlay. **Author statuses are Mac's and are reported, never changed.** A reviewer verdict sits beside the author status; it is not a promotion or a demotion.

- **Register:** 71 claims · author status (normalized): ACTIVE 52 · SCAFFOLD 12 · CONJECTURE 4 · RETRACTED 3
- **RV19 reviewer verdicts:** not re-audited in RV19 54 · sharpen 9 · agree 8. "Not re-audited in RV19" means the 2026-10-20 assessment stands unrevised, not that the claim was confirmed.
- **Evidence pointers now (MEASURED today by path existence):** 107 references, 23 do not resolve.
- **RV19 pointer-repair patch:** NOT APPLIED (register SHA-256 `9d8e76dccb7b…`). If applied it would take missing references from 23 to 3; the remaining three need real material, not a pointer (see Appendix C in [APPENDICES_A_F_RESOLUTION.md](APPENDICES_A_F_RESOLUTION.md)). Decision **G-RV19-POINTERS**.
- **Flagged by the mathematics checklist (B38, G-M-1):** MIC-003, ELI-003 and CAS-003 meet a counterexample or a mismatch, and LYV-001 is unsupported; all four still carry ACTIVE. Marked ⚑ below.
- **Prior art:** each row's `prior_art_supersedes` field is the author's own comparison. No claim's novelty was established against a literature search in this review, so novelty stays UNVERIFIED for all 71.
- **Independent replication:** none, for any claim (B35, G-RV36-5).

| Claim | Layer | Load-bearing | Author status | 2026-10-20 | RV19 verdict | Evidence pointer(s) | RV19 note |
|---|---|---|---|---|---|---|---|
| CAS-001 | CASCADE L4 | yes | ACTIVE | DEFINED_ARCHITECTURE | not re-audited in RV19 | ✓ `01_CASCADE_L4/essentials.md` |  |
| CAS-002 | CASCADE L4 | yes | SCAFFOLD | UNCALIBRATED_INSTRUMENT | not re-audited in RV19 | ✓ `01_CASCADE_L4/essentials.md`<br>✓ `11_MATHEMATICAL_FOUNDATIONS/MATHEMATICS_FOUNDATIONS.md` |  |
| ⚑ CAS-003 | CASCADE L4 | yes | ACTIVE | PROOF_IMPLEMENTATION_MISMATCH | agree | ✗ `01_CASCADE_L4/CASCADE_THEOREMS.md` | Matches this review's RV18 witnesses. |
| CAS-004 | CASCADE L4 | yes | SCAFFOLD | PROOF_NOT_ESTABLISHED | not re-audited in RV19 | ✗ `01_CASCADE_L4/CASCADE_THEOREMS.md` |  |
| CAS-005 | CASCADE L4 | yes | ACTIVE | PROOF_NOT_ESTABLISHED | not re-audited in RV19 | ✗ `01_CASCADE_L4/CASCADE_THEOREMS.md` |  |
| CAS-006 | CASCADE L4 | yes | SCAFFOLD | PROOF_NOT_ESTABLISHED | not re-audited in RV19 | ✗ `01_CASCADE_L4/CASCADE_THEOREMS.md` |  |
| CAS-007 | CASCADE L4 | yes | SCAFFOLD | MODEL_WITH_INVALID_STABILITY_BRIDGE | not re-audited in RV19 | ✓ `08_INTEGRATIONS/SYSTEM_INTEGRATION_GUIDE.md` |  |
| CAS-008 | CASCADE L4 | no | CONJECTURE | IMPLEMENTATION_DOES_NOT_ESTABLISH_CONJECTURE | not re-audited in RV19 | ✗ `01_CASCADE_L4/CASCADE_THEOREMS.md`<br>✓ `11_MATHEMATICAL_FOUNDATIONS/MATHEMATICS_FOUNDATIONS.md` |  |
| CAS-009 | CASCADE L4 | yes | ACTIVE | DATED_MODEL_RESULTS_NOT_GENERAL_VALIDATION | sharpen | ✗ `01_CASCADE_L4/implementations/`<br>✓ `29_GOVERNANCE/EMPIRICAL_INVENTORY.md` | Not merely unrerun: no runner exists. cascade_synthetic_experiment.py and every EMPIRICAL_RESULTS material are absent from the tree and all history. The three … |
| CAS-010 | CASCADE L4 | yes | ACTIVE | DATED_MODEL_RESULTS_NOT_GENERAL_VALIDATION | sharpen | ✗ `01_CASCADE_L4/implementations/`<br>✓ `29_GOVERNANCE/EMPIRICAL_INVENTORY.md` | Rerun here: reproduces exactly, and the additive baseline also scores 1.0 in every trial (t 0, d 0). The +110% is over a static no-update baseline; the 200 … |
| CAS-011 | CASCADE L4 | yes | ACTIVE | DATED_MODEL_RESULTS_NOT_GENERAL_VALIDATION | sharpen | ✗ `01_CASCADE_L4/implementations/`<br>✓ `29_GOVERNANCE/EMPIRICAL_INVENTORY.md` | No runner or data exists. 0.42->0.02 (register) and 1.00%->0.048% (EMPIRICAL_RESULTS) both give 95.2% from different numbers. UNVERIFIED. |
| AUR-001 | AURA L3 | yes | ACTIVE | NORMATIVE_CONSTITUTION_OR_DEFINITION | not re-audited in RV19 | ✓ `02_AURA_L3/essentials.md` |  |
| AUR-002 | AURA L3 | yes | ACTIVE | NORMATIVE_CONSTITUTION_OR_DEFINITION | not re-audited in RV19 | ✓ `02_AURA_L3/essentials.md` |  |
| AUR-003 | AURA L3 | yes | ACTIVE | NORMATIVE_CONSTITUTION_OR_DEFINITION | not re-audited in RV19 | ✓ `02_AURA_L3/essentials.md` |  |
| AUR-004 | AURA L3 | yes | ACTIVE | NORMATIVE_CONSTITUTION_OR_DEFINITION | not re-audited in RV19 | ✓ `02_AURA_L3/essentials.md` |  |
| AUR-005 | AURA L3 | yes | ACTIVE | NORMATIVE_CONSTITUTION_OR_DEFINITION | not re-audited in RV19 | ✓ `02_AURA_L3/essentials.md` |  |
| AUR-006 | AURA L3 | yes | ACTIVE | NORMATIVE_CONSTITUTION_OR_DEFINITION | not re-audited in RV19 | ✓ `02_AURA_L3/essentials.md` |  |
| AUR-007 | AURA L3 | yes | ACTIVE | NORMATIVE_CONSTITUTION_OR_DEFINITION | not re-audited in RV19 | ✓ `02_AURA_L3/essentials.md` |  |
| AUR-008 | AURA L3 | yes | CONJECTURE | OPEN_NORMATIVE_RESEARCH | not re-audited in RV19 | ✓ `02_AURA_L3/essentials.md` |  |
| AUR-009 | AURA L3 | yes | SCAFFOLD | PROOF_NOT_ESTABLISHED | not re-audited in RV19 | ✗ `02_AURA_L3/AURA_THEOREMS.md` |  |
| AUR-010 | AURA L3 | yes | ACTIVE | UNIVERSAL_GUARANTEE_NOT_ESTABLISHED | not re-audited in RV19 | ✓ `02_AURA_L3/essentials.md` |  |
| AUR-011 | AURA L3 | yes | ACTIVE | NORMATIVE_CONSTITUTION_OR_DEFINITION | not re-audited in RV19 | ✓ `02_AURA_L3/essentials.md`<br>✓ `30_MAPS/FORMAL_SPINE.md` |  |
| LAM-001 | LAMAGUE L1 | yes | ACTIVE | DEFINED_ARCHITECTURE | not re-audited in RV19 | ✓ `03_LAMAGUE_L1/10_essentials.md` |  |
| LAM-002 | LAMAGUE L1 | yes | ACTIVE | DEFINED_ARCHITECTURE | not re-audited in RV19 | ✓ `03_LAMAGUE_L1/10_essentials.md`<br>✓ `04_TRIAD_L2/essentials.md` |  |
| LAM-003 | LAMAGUE L1 | yes | ACTIVE | CONDITIONAL_ESTABLISHED_MATHEMATICS | not re-audited in RV19 | ✗ `03_LAMAGUE_L1/LAMAGUE_THEOREMS.md` |  |
| LAM-004 | LAMAGUE L1 | yes | ACTIVE | CONDITIONAL_ESTABLISHED_MATHEMATICS | not re-audited in RV19 | ✗ `03_LAMAGUE_L1/LAMAGUE_THEOREMS.md` |  |
| LAM-005 | LAMAGUE L1 | yes | SCAFFOLD | INTERPRETIVE_PROPOSAL | not re-audited in RV19 | ✓ `docs/LAMAGUE_CROSS_CULTURAL_PAPER.md` |  |
| TRI-001 | TRIAD L2 | yes | ACTIVE | DESIGN_WITH_UNPROVEN_GUARANTEE | not re-audited in RV19 | ✓ `04_TRIAD_L2/essentials.md` |  |
| TRI-002 | TRIAD L2 | yes | ACTIVE | DESIGN_WITH_UNPROVEN_GUARANTEE | not re-audited in RV19 | ✓ `04_TRIAD_L2/essentials.md`<br>✓ `30_MAPS/FORMAL_SPINE.md` |  |
| TRI-003 | TRIAD L2 | yes | ACTIVE | INVALID_DISPLAYED_PROOF_CHAIN | not re-audited in RV19 | ✗ `04_TRIAD_L2/TRIAD_THEOREMS.md` |  |
| TRI-004 | TRIAD L2 | yes | ACTIVE | INVALID_DISPLAYED_PROOF_CHAIN | not re-audited in RV19 | ✗ `04_TRIAD_L2/TRIAD_THEOREMS.md` |  |
| TRI-005 | TRIAD L2 | yes | ACTIVE | INVALID_DISPLAYED_PROOF_CHAIN | not re-audited in RV19 | ✗ `04_TRIAD_L2/TRIAD_THEOREMS.md` |  |
| TRI-006 | TRIAD L2 | yes | ACTIVE | CONDITIONAL_ESTABLISHED_MATHEMATICS | not re-audited in RV19 | ✗ `04_TRIAD_L2/TRIAD_THEOREMS.md`<br>✓ `30_MAPS/FORMAL_SPINE.md` |  |
| TRI-007 | TRIAD L2 | yes | ACTIVE | CONDITION_NOT_ESTABLISHED_AS_GENERAL_GUARANTEE | agree | ✗ `04_TRIAD_L2/TRIAD_THEOREMS.md` | Matches this review's RV18 witnesses. |
| MIC-001 | MICROORCIM L5 | yes | SCAFFOLD | UNCALIBRATED_INSTRUMENT | not re-audited in RV19 | ✓ `05_MICROORCIM_L5/essentials.md` |  |
| MIC-002 | MICROORCIM L5 | yes | SCAFFOLD | UNCALIBRATED_INSTRUMENT | not re-audited in RV19 | ✓ `05_MICROORCIM_L5/essentials.md`<br>✓ `30_MAPS/FORMAL_SPINE.md` |  |
| ⚑ MIC-003 | MICROORCIM L5 | yes | ACTIVE | COUNTEREXAMPLE_AS_STATED | agree | ✗ `05_MICROORCIM_L5/MICROORCIM_THEOREMS.md`<br>✓ `30_MAPS/FORMAL_SPINE.md` | Matches this review's RV18 witnesses. |
| MIC-004 | MICROORCIM L5 | yes | ACTIVE | EXPLICIT_SCOPE_BOUNDARY | not re-audited in RV19 | ✓ `05_MICROORCIM_L5/essentials.md`<br>✓ `28_DEFENSE/FALSIFICATION_REGISTER.md` |  |
| ELI-001 | EARNED_LIGHT L0 | yes | SCAFFOLD | CONJECTURAL_MODEL | not re-audited in RV19 | ✓ `06_EARNED_LIGHT_L0/essentials.md` |  |
| ELI-002 | EARNED_LIGHT L0 | yes | SCAFFOLD | CONJECTURAL_MODEL | not re-audited in RV19 | ✓ `06_EARNED_LIGHT_L0/essentials.md` |  |
| ⚑ ELI-003 | EARNED_LIGHT L0 | yes | ACTIVE | COUNTEREXAMPLE_AS_STATED | agree | ✓ `06_EARNED_LIGHT_L0/essentials.md` | Matches this review's RV18 witnesses. |
| ELI-004 | EARNED_LIGHT L0 | yes | ACTIVE | EXPLICIT_SCOPE_BOUNDARY | not re-audited in RV19 | ✓ `06_EARNED_LIGHT_L0/essentials.md` |  |
| ELI-005 | EARNED_LIGHT L0 | yes | SCAFFOLD | CONJECTURAL_MODEL | not re-audited in RV19 | ✓ `28_DEFENSE/FALSIFICATION_REGISTER.md` |  |
| ANA-001 | ANAMNESIS L0 | yes | ACTIVE | DEFINED_CONCEPT | not re-audited in RV19 | ✓ `07_ANAMNESIS_L0/essentials.md` |  |
| ANA-002 | ANAMNESIS L0 | yes | ACTIVE | HISTORICAL_EVIDENCE_NOT_ESTABLISHED | not re-audited in RV19 | ✓ `07_ANAMNESIS_L0/essentials.md`<br>✗ `07_ANAMNESIS_L0/TC_CATALOG.md` |  |
| ANA-003 | ANAMNESIS L0 | yes | ACTIVE | HISTORICAL_EVIDENCE_NOT_ESTABLISHED | sharpen | ✗ `07_ANAMNESIS_L0/TC_CATALOG.md` | Agree. The register's count of 4 is stated nowhere that resolves; the only resolving statement, 30_MAPS/FORMAL_SPINE.md:439, says TC(pi, >=3). TC_CATALOG.md … |
| ANA-004 | ANAMNESIS L0 | yes | ACTIVE | HISTORICAL_EVIDENCE_NOT_ESTABLISHED | sharpen | ✗ `07_ANAMNESIS_L0/TC_CATALOG.md` | Agree. FORMAL_SPINE.md:439 says TC(symmetry_groups, >=3), not 4. TC_CATALOG.md stays missing. |
| CRY-001 | CHRYSOPOEIA L4 | yes | ACTIVE | DEFINED_ARCHITECTURE | not re-audited in RV19 | ✓ `09_CHRYSOPOEIA_L4/essentials.md` |  |
| CRY-002 | CHRYSOPOEIA L4 | yes | ACTIVE | OPERATOR_SCOPE_REQUIRED | not re-audited in RV19 | ✗ `08_CHRYSOPOEIA/CHRYSOPOEIA_THEOREMS.md` |  |
| CRY-003 | CHRYSOPOEIA L4 | yes | ACTIVE | CONDITIONAL_THEOREM_WITH_UNESTABLISHED_IMPLEMENTATION_HYPOTHESES | agree | ✗ `08_CHRYSOPOEIA/CHRYSOPOEIA_THEOREMS.md` | Matches this review's RV18 witnesses. |
| CRY-004 | CHRYSOPOEIA L4 | yes | ACTIVE | INTERPRETIVE_ANALOGY | not re-audited in RV19 | ✗ `08_CHRYSOPOEIA/CHRYSOPOEIA_THEOREMS.md` |  |
| HAR-001 | HARMONIA L6 | yes | ACTIVE | INSTRUMENT_MISMATCH | agree | ✓ `10_HARMONIA_L6/essentials.md` | Matches this review's RV18 witnesses. |
| HAR-002 | HARMONIA L6 | yes | ACTIVE | NARROW_ARITHMETIC_HOLDS | agree | ✓ `10_HARMONIA_L6/essentials.md`<br>✓ `30_MAPS/FORMAL_SPINE.md` | Matches this review's RV18 witnesses. |
| HAR-003 | HARMONIA L6 | yes | ACTIVE | DEFINED_DERIVED_QUANTITY | not re-audited in RV19 | ✓ `10_HARMONIA_L6/essentials.md` |  |
| HAR-004 | HARMONIA L6 | yes | ACTIVE | INTERPRETIVE_MAPPING | sharpen | ✓ `10_HARMONIA_L6/essentials.md`<br>✓ `CLAUDE.md` | Agree on the classification. The CLAUDE.md pointer has been silent since the reforge (3980262); the table lives in AGENTS.md and 10_HARMONIA_L6/essentials.md. |
| HAR-005 | HARMONIA L6 | yes | CONJECTURE | OPEN_CONJECTURE | not re-audited in RV19 | ✓ `10_HARMONIA_L6/essentials.md` |  |
| XFW-001 | CROSS Lcross | yes | SCAFFOLD | MODEL_WITH_INVALID_STABILITY_BRIDGE | agree | ✓ `08_INTEGRATIONS/SYSTEM_INTEGRATION_GUIDE.md`<br>✓ `30_MAPS/FORMAL_SPINE.md` | Matches this review's RV18 witnesses. |
| XFW-002 | CROSS Lcross | yes | ACTIVE | INVALID_DISPLAYED_PROOF_BRIDGE | not re-audited in RV19 | ✓ `30_MAPS/FORMAL_SPINE.md`<br>✓ `30_MAPS/CODEX_DISTILLATION.md` |  |
| XFW-003 | CROSS Lcross | yes | ACTIVE | PROOF_NOT_ESTABLISHED | not re-audited in RV19 | ✓ `30_MAPS/FORMAL_SPINE.md` |  |
| XFW-004 | CROSS Lcross | yes | ACTIVE | MODEL_PREREQUISITES_REQUIRED | not re-audited in RV19 | ✓ `30_MAPS/FORMAL_SPINE.md` |  |
| XFW-005 | CROSS Lcross | yes | ACTIVE | PHILOSOPHICAL_ARCHITECTURE | sharpen | ✓ `CLAUDE.md`<br>✓ `30_MAPS/CODEX_DISTILLATION.md` | Agree on the classification. CLAUDE.md no longer states the Two-Point Protocol; THE_SOL_PROTOCOL.md:80 does. |
| XFW-006 | CROSS Lcross | yes | ACTIVE | DESIGN_MANDATE_NOT_INDEPENDENT_VERIFICATION | sharpen | ✓ `CLAUDE.md` | Agree on the classification. CLAUDE.md no longer defines PGF; THE_SOL_PROTOCOL.md:131 does. |
| ⚑ LYV-001 | MATH Lcross | yes | ACTIVE | VALIDATION_CLAIM_UNSUPPORTED | sharpen | ✓ `11_MATHEMATICAL_FOUNDATIONS/MATHEMATICS_FOUNDATIONS.md`<br>✓ `29_GOVERNANCE/EMPIRICAL_INVENTORY.md` | Agree, and RV18 measured the honest symbolic tally at 2/6 with sympy DID NOT RUN. Neither register pointer states 11/11; only … |
| LYV-002 | MATH Lcross | yes | ACTIVE | CONDITIONAL_ESTABLISHED_MATHEMATICS | not re-audited in RV19 | ✓ `11_MATHEMATICAL_FOUNDATIONS/MATHEMATICS_FOUNDATIONS.md` |  |
| CYB-001 | CROSS Lcross | no | ACTIVE | BOUNDED_CODE_STRUCTURE_SUPPORTED | not re-audited in RV19 | ✓ `34_CYBERNETICS/LOOP_MAP.json`<br>✓ `34_CYBERNETICS/loop_audit.py`<br>✓ `12_IMPLEMENTATIONS/core/grey_mode.py`<br>✓ `tests/test_cybernetics.py` |  |
| CYB-002 | CROSS Lcross | no | ACTIVE | BOUNDED_CODE_STRUCTURE_SUPPORTED | not re-audited in RV19 | ✓ `34_CYBERNETICS/LOOP_MAP.json`<br>✓ `34_CYBERNETICS/loop_audit.py`<br>✓ `34_CYBERNETICS/CYBERNETIC_READING.md`<br>✓ `12_IMPLEMENTATIONS/core/cascade_engine.py` |  |
| CYB-003 | CROSS Lcross | no | ACTIVE | BOUNDED_CODE_STRUCTURE_SUPPORTED | not re-audited in RV19 | ✓ `34_CYBERNETICS/LOOP_MAP.json`<br>✓ `34_CYBERNETICS/loop_audit.py`<br>✓ `12_IMPLEMENTATIONS/core/sovereign_pipeline.py`<br>✓ `tests/test_cybernetics.py`<br>✓ `tests/test_sovereign_pipeline.py` |  |
| CYB-004 | CROSS Lcross | no | CONJECTURE | OPEN_CONJECTURE_WITH_TOY_EVIDENCE | not re-audited in RV19 | ✓ `34_CYBERNETICS/variety_demo.py`<br>✓ `34_CYBERNETICS/CYBERNETIC_READING.md`<br>✓ `tests/test_cybernetics.py` |  |
| RET-001 | RETRACTED Lcross | no | RETRACTED | AUTHOR_WITHDRAWAL_PRESERVED | not re-audited in RV19 | ✓ `28_DEFENSE/FALSIFICATION_REGISTER.md`<br>✓ `28_DEFENSE/FAILURE_MUSEUM.md` |  |
| RET-002 | RETRACTED Lcross | no | RETRACTED | AUTHOR_WITHDRAWAL_PRESERVED | not re-audited in RV19 | ✓ `30_MAPS/COHERENCE_REGISTER.md`<br>✓ `28_DEFENSE/FALSIFICATION_REGISTER.md`<br>✓ `28_DEFENSE/FAILURE_MUSEUM.md` |  |
| RET-003 | RETRACTED Lcross | no | RETRACTED | AUTHOR_WITHDRAWAL_PRESERVED | not re-audited in RV19 | ✓ `30_MAPS/FORMAL_SPINE.md`<br>✓ `30_MAPS/ONTOLOGY.md`<br>✓ `28_DEFENSE/FAILURE_MUSEUM.md` |  |
