# Branch Consolidation Inventory — 2026-09-25

Snapshot of the six GitHub branch tips inspected for the local consolidation. `master` was the protected default and is the recovery base. This record is an inventory, not evidence that any branch was pushed, deleted, or changed on GitHub.

| Branch | Tip SHA | Merge base | Behind / ahead of master | Unique commits | Paths changed since base | Disposition |
|---|---|---|---:|---:|---:|---|
| `master` | `4e05edf6b8af0ecd88f7ada5da1c42caa4077229` | — | 0 / 0 | 0 | 0 | Protected canonical base; retained. |
| `fix/ci-paths-2026-09-24` | `bf09b33b30e4a640c263dc7c00cfbfad19258adf` | `4e05edf6b8af0ecd88f7ada5da1c42caa4077229` | 0 / 1 | 1 | 7 | Merged locally as 7e8188b; auto-push workflow removed, promote.py retained and not run. |

<details><summary>fix/ci-paths-2026-09-24: paths changed since merge base (7; 0 line-ending-only)</summary>

- `.github/workflows/agent-deploy.yml`
- `.github/workflows/ci.yml`
- `.github/workflows/test.yml`
- `.github/workflows/update-stats.yml`
- `12_IMPLEMENTATIONS/agent-init.py`
- `12_IMPLEMENTATIONS/alexandria_agent.py`
- `promote.py`

</details>

| `framework-public-2026-09-24` | `f6bb5a19c4ff07bb658b3903a6c7e4caa8cf8135` | `4e05edf6b8af0ecd88f7ada5da1c42caa4077229` | 0 / 3 | 3 | 44 | Merged locally as 0867c83 after review of CLI, health, test, and reference improvements. |

<details><summary>framework-public-2026-09-24: paths changed since merge base (44; 0 line-ending-only)</summary>

- `12_IMPLEMENTATIONS/agent-init.py`
- `12_IMPLEMENTATIONS/alexandria_agent.py`
- `12_IMPLEMENTATIONS/applications/lycheetah_guard_mcp.py`
- `12_IMPLEMENTATIONS/applications/sol_companion.py`
- `12_IMPLEMENTATIONS/applications/web_demo.py`
- `12_IMPLEMENTATIONS/core/anamnesis_reference.py`
- `12_IMPLEMENTATIONS/core/aura_score_hexie.py`
- `12_IMPLEMENTATIONS/core/chrysopoeia_engine.py`
- `12_IMPLEMENTATIONS/core/earned_light_calculator.py`
- `12_IMPLEMENTATIONS/core/harmonia_calculator.py`
- `12_IMPLEMENTATIONS/core/lamague_reference.py`
- `12_IMPLEMENTATIONS/core/sovereign_pipeline.py`
- `12_IMPLEMENTATIONS/core/triad_wuwei.py`
- `12_IMPLEMENTATIONS/phi_bandit.py`
- `12_IMPLEMENTATIONS/systems/knowledge_genome.py`
- `12_IMPLEMENTATIONS/systems/unified_field.py`
- `14_MYSTERY_SCHOOL/implementations/visualization_system.py`
- `19_MULTI_AGENT_CHORUS/README.md`
- `19_MULTI_AGENT_CHORUS/albedo_synthesizer.py`
- `19_MULTI_AGENT_CHORUS/beacon_reflector.py`
- `19_MULTI_AGENT_CHORUS/cascade_architect.py`
- `19_MULTI_AGENT_CHORUS/harmonia_resonator.py`
- `19_MULTI_AGENT_CHORUS/healer_transmuter.py`
- `19_MULTI_AGENT_CHORUS/protector_guardian.py`
- `19_MULTI_AGENT_CHORUS/remaining_agents.py`
- `19_MULTI_AGENT_CHORUS/run_chorus.py`
- `19_MULTI_AGENT_CHORUS/solstice_illuminator.py`
- `demo.py`
- `lycheetah/cli.py`
- `pyproject.toml`
- `tests/conftest.py`
- `tests/test_anamnesis_reference.py`
- `tests/test_aura_text_checker.py`
- `tests/test_cascade_reality_bridge.py`
- `tests/test_chrysopoeia_engine.py`
- `tests/test_earned_light_calculator.py`
- `tests/test_harmonia_calculator.py`
- `tests/test_lamague_parser.py`
- `tests/test_lamague_reference.py`
- `tests/test_lamague_shelf_legacy.py`
- `tests/test_microorcim_tracker.py`
- `tests/test_sovereign_pipeline.py`
- `tests/test_threads_fixes.py`
- `tests/test_triad_wuwei.py`

</details>

| `forge/agent-assurance-runtime-2026-08-22` | `3aafd502b28e1b3675612cc1775e9223d4fcae56` | `a9bddb1fdd81d2f7975707433ba7ca772553b6c2` | 15 / 4 | 4 | 78 | Merged locally as 32bc74b; assurance remains a scaffold with internal verification only. |

<details><summary>forge/agent-assurance-runtime-2026-08-22: paths changed since merge base (78; 0 line-ending-only)</summary>

- `.github/workflows/test.yml`
- `12_IMPLEMENTATIONS/applications/LYCHEETAH_GUARD_SETUP.md`
- `12_IMPLEMENTATIONS/applications/aura_text_checker.py`
- `12_IMPLEMENTATIONS/applications/lycheetah_guard_mcp.py`
- `12_IMPLEMENTATIONS/applications/web_demo.py`
- `12_IMPLEMENTATIONS/core/aura_customizer.py`
- `12_IMPLEMENTATIONS/core/grey_mode.py`
- `12_IMPLEMENTATIONS/core/lamague_reference.py`
- `12_IMPLEMENTATIONS/core/psi_consensus.py`
- `12_IMPLEMENTATIONS/core/semantic_extractor.py`
- `12_IMPLEMENTATIONS/core/seven_phase.py`
- `12_IMPLEMENTATIONS/core/sol_self_protocol.py`
- `12_IMPLEMENTATIONS/core/tri_axial_checker.py`
- `28_DEFENSE/COLD_ROOM_VERIFICATION.md`
- `28_DEFENSE/FAILURE_MUSEUM.md`
- `34_ASSURANCE_RUNTIME/ASSURANCE_RECEIPT_SPEC_v0.1.md`
- `34_ASSURANCE_RUNTIME/CUSTOMER_SUPPORT_WALKTHROUGH.md`
- `34_ASSURANCE_RUNTIME/EVIDENCE_CAPPED_ENFORCEMENT_v0.1.md`
- `34_ASSURANCE_RUNTIME/FRONTIER_REGISTER_2026-08-22.md`
- `34_ASSURANCE_RUNTIME/INDUSTRY_CROSSWALK_2026-08-22.md`
- `34_ASSURANCE_RUNTIME/OPENTELEMETRY_BRIDGE.md`
- `34_ASSURANCE_RUNTIME/POLICY_EVALUATION_HARNESS.md`
- `34_ASSURANCE_RUNTIME/POLICY_REGRESSION_GATE.md`
- `34_ASSURANCE_RUNTIME/README.md`
- `FIVE_MINUTE_BRIEF.md`
- `QUICKSTART.md`
- `README.md`
- `START_HERE_FORGE_CHECKPOINT_2026-08-22.md`
- `examples/assurance/customer_support_baseline.eval.json`
- `examples/assurance/customer_support_eval.jsonl`
- `examples/assurance/customer_support_policy.json`
- `examples/assurance/run_customer_support.py`
- `lycheetah/__init__.py`
- `lycheetah/applications/__init__.py`
- `lycheetah/applications/aura_text_checker.py`
- `lycheetah/applications/lycheetah_guard_mcp.py`
- `lycheetah/applications/web_demo.py`
- `lycheetah/assurance/__init__.py`
- `lycheetah/assurance/cli.py`
- `lycheetah/assurance/evaluation.py`
- `lycheetah/assurance/in_toto.py`
- `lycheetah/assurance/jsonutil.py`
- `lycheetah/assurance/models.py`
- `lycheetah/assurance/otel.py`
- `lycheetah/assurance/policy.py`
- `lycheetah/assurance/receipt.py`
- `lycheetah/assurance/regression.py`
- `lycheetah/assurance/runtime.py`
- `lycheetah/assurance/schemas/evaluation-case.schema.json`
- `lycheetah/assurance/schemas/evaluation-regression-report.schema.json`
- `lycheetah/assurance/schemas/evaluation-report.schema.json`
- `lycheetah/assurance/schemas/policy.schema.json`
- `lycheetah/assurance/schemas/receipt.schema.json`
- `lycheetah/cli.py`
- `lycheetah/core/__init__.py`
- `lycheetah/core/aura_customizer.py`
- `lycheetah/core/grey_mode.py`
- `lycheetah/core/lamague_reference.py`
- `lycheetah/core/psi_consensus.py`
- `lycheetah/core/semantic_extractor.py`
- `lycheetah/core/seven_phase.py`
- `lycheetah/core/sol_self_protocol.py`
- `lycheetah/core/tri_axial_checker.py`
- `pyproject.toml`
- `tests/test_assurance_cli.py`
- `tests/test_assurance_evaluation.py`
- `tests/test_assurance_models.py`
- `tests/test_assurance_otel.py`
- `tests/test_assurance_policy.py`
- `tests/test_assurance_receipt.py`
- `tests/test_assurance_regression.py`
- `tests/test_assurance_runtime.py`
- `tests/test_assurance_schemas.py`
- `tests/test_mcp_guard.py`
- `tests/test_optional_dependencies.py`
- `tests/test_web_demo.py`
- `tools/verify_base_distribution.py`
- `tools/verify_installed_distribution.py`

</details>

| `claude/sovereign-instance-quality-xtcckq` | `dfe7c55cf375970cfda811e2e27f22178ff366b0` | `606537d43c56da9409b0ed41f2d37c921b6459db` | 16 / 13 | 13 | 103 | Integration is in progress on consolidation/2026-09-25; final merge commit will be recorded after local verification. |

<details><summary>claude/sovereign-instance-quality-xtcckq: paths changed since merge base (103; 54 line-ending-only)</summary>

- `.gitattributes`
- `.github/copilot-instructions.md`
- `.github/dependabot.yml`
- `.github/workflows/agent-deploy.yml`
- `.github/workflows/ci.yml`
- `.github/workflows/test.yml`
- `.github/workflows/update-stats.yml`
- `.gitignore`
- `.pre-commit-config.yaml`
- `03_LAMAGUE_L1/07_RUNTIME_v0.3_CROSS_INTELLIGENCE_EQUIVALENCE/lamague_runtime/equivalence.py`
- `03_LAMAGUE_L1/08_EXPERIMENT_001_CROSS_INTELLIGENCE/OPERATOR_PACK/lamague_runtime/equivalence.py`
- `03_LAMAGUE_L1/08_EXPERIMENT_001_CROSS_INTELLIGENCE/OPERATOR_PACK/reports/LAMAGUE_EXPERIMENT_001_RESULTS.csv`
- `03_LAMAGUE_L1/22_REVERSIBLE_COMPRESSION_v1.0/README.md`
- `03_LAMAGUE_L1/22_REVERSIBLE_COMPRESSION_v1.0/examples/agent_state_compaction.py`
- `03_LAMAGUE_L1/22_REVERSIBLE_COMPRESSION_v1.0/pyproject.toml`
- `03_LAMAGUE_L1/22_REVERSIBLE_COMPRESSION_v1.0/reports/packet_sizes.csv`
- `04_TRIAD_L2/TRIAD_COMPLETE.md`
- `08_INTEGRATIONS/UNIVERSAL_SYSTEM_GUIDE.md`
- `09_CHRYSOPOEIA_L4/CHRYSOPOEIA_COMPLETE.md`
- `10_HARMONIA_L6/HARMONIA_COMPLETE.md`
- `11_MATHEMATICAL_FOUNDATIONS/HIDDEN_MATHEMATICAL_TRUTHS.md`
- `11_MATHEMATICAL_FOUNDATIONS/MATHEMATICS_REALITY_ALIGNMENT.md`
- `11_MATHEMATICAL_FOUNDATIONS/MATHEMATICS_TO_REALITY_BRIDGE.md`
- `11_MATHEMATICAL_FOUNDATIONS/cascade_simulation.py`
- `11_MATHEMATICAL_FOUNDATIONS/cascade_simulation_results.json`
- `11_MATHEMATICAL_FOUNDATIONS/lyapunov_verification_results.json`
- `12_IMPLEMENTATIONS/agent-init.py`
- `12_IMPLEMENTATIONS/agent-manifest.json`
- `12_IMPLEMENTATIONS/agent-template.py`
- `12_IMPLEMENTATIONS/alexandria_agent.py`
- `12_IMPLEMENTATIONS/applications/__init__.py`
- `12_IMPLEMENTATIONS/applications/lycheetah_guard_mcp.py`
- `12_IMPLEMENTATIONS/cascade_simulation_results.json`
- `12_IMPLEMENTATIONS/core/__init__.py`
- `12_IMPLEMENTATIONS/core/calibrate_master_equation.py`
- `12_IMPLEMENTATIONS/core/grey_mode.py`
- `12_IMPLEMENTATIONS/core/harmonia_calculator.py`
- `12_IMPLEMENTATIONS/core/microorcim_tracker.py`
- `12_IMPLEMENTATIONS/core/triad_tracker.py`
- `12_IMPLEMENTATIONS/systems/knowledge_genome.py`
- `14_MYSTERY_SCHOOL/AI_CONSCIOUSNESS_SCHOOL.md`
- `14_MYSTERY_SCHOOL/SUBJECT_CATALOGUE.md`
- `14_MYSTERY_SCHOOL/THE_DANCE_WITH_MACHINES.md`
- `14_MYSTERY_SCHOOL/UNCOMMON_CATALOGUE.md`
- `14_MYSTERY_SCHOOL/VOID_CATALOGUE.md`
- `14_MYSTERY_SCHOOL/VOID_CATALOGUE_V2.md`
- `14_MYSTERY_SCHOOL/implementations/subject_catalogue.py`
- `14_MYSTERY_SCHOOL/implementations/uncommon_subject_catalogue.py`
- `14_MYSTERY_SCHOOL/implementations/void_subject_catalogue.py`
- `16_SOL_VEYRA_ARCHITECTURE/AGENTS.md`
- `19_MULTI_AGENT_CHORUS/run_chorus.py`
- `28_DEFENSE/REPRODUCIBILITY_REPORT.md`
- `32_TIANXIA/OPERATOR_AUDIT_2026-08-08.md`
- `32_TIANXIA/implementations/civilisational_governance_benchmark.py`
- `32_TIANXIA/implementations/hexie_five_fold.py`
- `32_TIANXIA/implementations/operator_audit.py`
- `32_TIANXIA/implementations/ren_zheng.py`
- `32_TIANXIA/implementations/wang_dao.py`
- `33_APPLICATIONS/BRIDGE_2026-08-08.md`
- `33_APPLICATIONS/external_validation.py`
- `99_ARCHIVE/CODEX_CHANGES/01_persona_validator_report.md`
- `99_ARCHIVE/CODEX_CHANGES/02_cascade_provenance_report.md`
- `99_ARCHIVE/CODEX_CHANGES/03_aura_benchmark_report.md`
- `99_ARCHIVE/CODEX_CHANGES/04_aura_sandbox_report.md`
- `99_ARCHIVE/CODEX_CHANGES/05_drift_visualizer_report.md`
- `99_ARCHIVE/CODEX_CHANGES/alchemical_vault_notes.md`
- `99_ARCHIVE/CODEX_CHANGES/aura_cascade_summary.md`
- `99_ARCHIVE/CODEX_CHANGES/aura_protocol_main_notes.md`
- `99_ARCHIVE/CODEX_CHANGES/session_report.md`
- `99_ARCHIVE/MATHEMATICS_AUDIT.md`
- `99_ARCHIVE/MATHEMATICS_FIXES.md`
- `CHANGELOG.md`
- `CODE_OF_CONDUCT.md`
- `README.md`
- `SECURITY.md`
- `TRUTH_PRESSURE/FORGE_2026-08-02_EXPANDED/TRUTH_PRESSURE_MEASUREMENT_PACK_v0.4/rater_packets/RATER_A_PACKET.csv`
- `TRUTH_PRESSURE/FORGE_2026-08-02_EXPANDED/TRUTH_PRESSURE_MEASUREMENT_PACK_v0.4/rater_packets/RATER_B_PACKET.csv`
- `TRUTH_PRESSURE/FORGE_2026-08-02_EXPANDED/TRUTH_PRESSURE_MEASUREMENT_PACK_v0.4/rater_packets/RATER_C_PACKET.csv`
- `docs/COMMUNITY/FREE_AI_TOOLS.md`
- `docs/GRANTS/LONGTERM_FUND_README.md`
- `docs/GRANTS/MANIFUND_README.md`
- `docs/LAMAGUE_CROSS_CULTURAL_PAPER.md`
- `docs/README.md`
- `docs/SONNET_CLEANUP_PLAN.md`
- `docs/X_ARTICLE_SOVEREIGNTY.md`
- `docs/for-agents.html`
- `docs/script.js`
- `docs/style.css`
- `generate_defense_bundle.py`
- `lycheetah/.ruff.toml`
- `lycheetah/__init__.py`
- `lycheetah/_bootstrap.py`
- `lycheetah/cli.py`
- `lycheetah/py.typed`
- `papers/CASCADE_ARXIV.tex`
- `papers/LIMITATIONS_AND_FUTURE.md`
- `papers/README.md`
- `papers/RELATED_WORK_EXPANDED.md`
- `pyproject.toml`
- `tests/test_aura_checker.py`
- `tests/test_cascade_predictability.py`
- `tests/test_entry_points.py`
- `tests/test_tianxia_operators.py`

</details>

## Independent `main` history

- Tip: `fac4523fac3b509889b22ec36535ee3ab02c04c0`; shared merge base with `master`: none; commits in its independent history: 5.
- Paths present only on `main` compared with the `master` tree: 20.
- Disposition: do not merge unrelated history. Preserve the exact branch tip under the annotated local recovery tag `pre-consolidation-main-2026-09-25`; unique tools and school maps are retained for retrieval. Existing execution reports remain under `99_ARCHIVE/CODEX_CHANGES/`.

Main-only paths:

- `01_persona_validator/persona_validator.py`
- `01_persona_validator/requirements.txt`
- `01_persona_validator/sol_persona.yaml`
- `02_cascade_provenance/provenance_checker.py`
- `02_cascade_provenance/requirements.txt`
- `03_aura_benchmark/benchmark_runner.py`
- `03_aura_benchmark/requirements.txt`
- `03_aura_benchmark/test_suite.yaml`
- `04_aura_sandbox/aura_sandbox.py`
- `04_aura_sandbox/requirements.txt`
- `05_drift_visualizer/backend/drift_scorer.py`
- `05_drift_visualizer/backend/requirements.txt`
- `05_drift_visualizer/backend/server.py`
- `05_drift_visualizer/frontend/index.html`
- `05_drift_visualizer/frontend/package.json`
- `05_drift_visualizer/frontend/src/DriftVisualizer.jsx`
- `05_drift_visualizer/frontend/src/main.jsx`
- `05_drift_visualizer/frontend/vite.config.js`
- `14_MYSTERY_SCHOOL/SOURCES/MOBILE/CLASSROOM_LESSON_SOURCE_MAP_2026-07-29.md`
- `14_MYSTERY_SCHOOL/SOURCES/MOBILE/SCHOOL_SUBJECTS_22_DOORS.md`

## Recovery anchors

Annotated local tags preserve all six inspected branch tips:

- `pre-consolidation-master-2026-09-25` → `4e05edf6b8af0ecd88f7ada5da1c42caa4077229`
- `pre-consolidation-main-2026-09-25` → `fac4523fac3b509889b22ec36535ee3ab02c04c0`
- `pre-consolidation-framework-public-2026-09-24` → `f6bb5a19c4ff07bb658b3903a6c7e4caa8cf8135`
- `pre-consolidation-fix-ci-paths-2026-09-24` → `bf09b33b30e4a640c263dc7c00cfbfad19258adf`
- `pre-consolidation-forge-agent-assurance-runtime-2026-08-22` → `3aafd502b28e1b3675612cc1775e9223d4fcae56`
- `pre-consolidation-claude-sovereign-instance-quality-2026-09-25` → `dfe7c55cf375970cfda811e2e27f22178ff366b0`

All dispositions above describe local Git work only. The protected remote `master` and remote branch refs remain untouched.
