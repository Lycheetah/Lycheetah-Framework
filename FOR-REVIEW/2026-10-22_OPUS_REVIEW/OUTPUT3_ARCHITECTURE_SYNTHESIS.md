# Output 3: Architecture synthesis

**Reviewer:** Sol (Claude Opus 5.5) · **Date:** 2026-10-23 · **Primary source:** [BATCH37](BATCH37_FINDINGS_AND_LEDGER.md), which covers the dependency diagram and sections A1–A8. Versions come from [BATCH33](BATCH33_FINDINGS_AND_LEDGER.md).

This is a reading of the ledgers, not new evidence. Status marks apply to each claim.

## 1. The shape of the repository (DERIVED, B37)

The tree holds six kinds of material, and they have different authority:

| Layer | Where | Authority | Witness |
|---|---|---|---|
| **Canonical body** (C-1.1) | `01_`–`11_` foundation folders, `28_DEFENSE/CLAIMS.json` (71 claims) | Defines what the framework claims | Self-review plus AI review only. No independent replication (G-RV36-5) |
| **Shipped package** | `lycheetah/` 1.3.0, `examples/` | The code a user installs | Package suite; import identity fixed (B37) |
| **Canonical algorithms** | `12_IMPLEMENTATIONS/` | Reference implementations behind claims | Core and applications suites |
| **Research lineages** | `34_ASSURANCE_RUNTIME/` (v0.5–v0.8), `TRUTH_PRESSURE/`, `papers/` | Experiments. **The package never imports them** (B37 A5) | Their own tests, ledgers and receipts |
| **Gates** | `tests/`, `tools/verify-claims.py`, the scripture gate, the LOOP_MAP gate, `.github/` | Decide whether a change may land | 1,571 passed locally. Hosted CI did not run (billing lock) |
| **Narrative and creative work** | `LYCHEETAH_MYTHOS/`, `LYCHEETAH_EPIC/`, `35_`, `docs/` | Interpretive; carries no empirical weight | Claims gate role markers |
| **Seat constitutions** | `CLAUDE.md`, `AGENTS.md`, `25_SOL_PROTOCOL_ARCHITECTURE/` | Govern agents working in the repository, not the framework | Proposals only (RV27) |

The boundary that holds best is the one between the shipped package and the research lineages. `examples/` imports only `lycheetah/`, and the package imports no research folder. The boundary that holds worst is between the canonical body and its evidence: 23 claim references point at files that do not exist (Appendix C), and 11 of 13 committed defense receipts cannot be regenerated from a producer script (B35).

## 2. Four version namespaces, no single contract (MEASURED, B33 and B37 A7)

| Namespace | Value today |
|---|---|
| Python package | `1.3.0` |
| Canonical body | `C-1.1` |
| Git release tag | `v1.0.0-c1.1` |
| Zenodo deposit | `tianxia-v0.2` |

No document states how these move together. One consequence: `DEFENSE_BUNDLE.pdf` still says it defends C-1.0 (B39-R2), and nothing failed when the canon moved to C-1.1. **Proposal:** add a `VERSIONS.md` contract and a gate that fails when the bundle's canon id differs from the live one.

## 3. One truth, one implementation: the duplicates (B37 A6)

- **Fixed:** one file was loaded as two modules, so an exported enum disagreed with its own reports (B37 A2). The fix is covered by an identity test.
- **Latent:** three more double identities come from the `sys.path.insert` pattern (A3). `demo.py` uses the same pattern. Each one could cause the A2 failure again (G-RV01-2).
- **Two definitions of one operator:** Ren-Zheng in `32_TIANXIA/` (G-REN-ZHENG-ONE-DEFINITION).
- **Two AI entry points:** `26_FOR_AI/DEAR_AI` and `AI_EXTRACTION_PROTOCOL` (G-DEAR-AI-RETIRE).
- **Two dependency lists:** `requirements.txt` and `pyproject.toml`. They disagree on what the defense bundle needs (B39-R3).
- **Lineage without a promotion record:** action-guard v0.8 in `34_` and the shipped `action_guard` have no recorded link (G-RV01-5). The shipped `finality` was not probed for the payload-binding defect found in the outbox (G-RV01-3, G-RV37-1).

## 4. Where the gates are honest and where they are not (B21, B32, B35, B37)

- **Honest:** the claims gate pins the public numbers and is HOLDING at 3 unmarked documents. The scripture gate checks hashes. The LOOP_MAP gate refused an unregistered reader during this review, so it has been seen to fail.
- **Not yet honest:**
  - A verifier counted a skip as a pass (G-ET-SKIP-COUNT).
  - A shadow gate recorded ENGINEERING_GATE_MET (G-TP-SHADOW-GATE).
  - The story gates are not in the suite (G-STORY-GATES-IN-SUITE).
  - ruff and mypy are pinned only by version floors (G-RV33-2).
  - Hosted CI cannot run at all while billing is locked (G-RV33-1).
  - A green local suite proves only what its tests cover.

## 5. Unresolved: the "third brain" (G-RV01-1)

The repository describes a third orchestrating component, but no single file is its owner. Candidates are the sovereign harness, the assurance runtime and the chorus. **Sol's reading (CONJECTURE):** it is the sovereign harness. This is Mac's ruling to make; until then, no document should describe it as built.

## 6. Recommended target shape (NORMATIVE, proposal only)

1. Use `pyproject.toml` as the only dependency authority, and generate `requirements.txt` from it or delete it.
2. Remove every `sys.path.insert` and import through the package or a `tests/conftest.py` root.
3. Add `VERSIONS.md` plus a gate for the four version namespaces.
4. Make every committed receipt reproducible by a named producer script, or label it ARCHIVAL.
5. Give each claim reference either a real file or a status of UNVERIFIED. Never point at a missing file.
