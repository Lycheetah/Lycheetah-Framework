# Output 5: Repair sequence

**Reviewer:** Sol (Claude Opus 5.5) · **Date:** 2026-10-23

Order the work by **what breaks first if left alone**. Every ID is listed in [G_DECISIONS_FOR_MAC.md](G_DECISIONS_FOR_MAC.md) with the ledger that raised it. A tier waits for the one above it only where the "after" column says so.

## T0: deadlines and security (do first)

| ID | Why now | After |
|---|---|---|
| G-TP-ANNOTATION-INTEGRITY | Annotation integrity must be fixed **before the first packet is opened**; after that the blind is spent | — |
| G-TP-COLLECTOR-SECRETS | Do not run the v0.8 collector until its secrets patch lands | — |
| G-RV37-1 + G-RV01-3 | The outbox has a payload-binding defect. Probe whether the shipped `finality` shares it | — |
| G-RV35-1 | Turn on private vulnerability reporting | — |
| G-RV35-4 | Run a history secret scan of a public repository | — |
| G-RV32-1 / G-RV32-2 | cascade-pc local API: host-header guard and key storage | — |

## T1: truth of public claims

| ID | What | After |
|---|---|---|
| G-OUTREACH-SENT | Were the corrected outreach drafts sent before they were corrected? (B24) | — |
| G-FOUNDATION-ENTITY / G-RV34-5 | "Lycheetah Foundation" appears as an author; is there a legal entity? | — |
| G-M-1 | MIC-003, ELI-003, CAS-003 and LYV-001 are ACTIVE but meet counterexamples or mismatches. Mac decides each status | — |
| G-RV19-POINTERS | Apply the pointer patch: 23 missing references fall to 3 | G-M-1 |
| G-EMPIRICAL / G-PREREG-FILING | File the pre-registration, or stop calling it pre-registered | — |
| G-CONVERGENCE-HEADLINE, G-RV36-1, G-RV34-2/3/6 | Public headlines and indexes that overstate or name absent files | — |
| G-CRISIS-LIST-OWNER | Someone must own the crisis-line list and re-check it on a date | — |
| B39-R1, B39-R2, B39-R4 | Stale "80 tests"; the defense bundle on C-1.0; the unbannered `08_INTEGRATIONS` | — |

## T2: CI and gates

| ID | What | After |
|---|---|---|
| G-RV33-1 | Unlock GitHub billing, or move CI. Until then every hosted check is DID NOT RUN | — |
| G-RV33-2 | Pin ruff and mypy exactly | G-RV33-1 |
| G-ET-SKIP-COUNT → G-CI-CONTINUATIONS | A skip must never count as a pass; then add the continuations to CI | — |
| G-STORY-GATES-IN-SUITE, G-RV36-2 | Put the story gates in the suite | — |
| G-RV35-3 | Dependabot. **Mac's decision is pending** | — |
| Appendix D | Run ruff once a venv exists, then scope the frozen files | G-RV33-2 |

## T3: architecture

| ID | What |
|---|---|
| G-RV01-2 | Remove `sys.path.insert`; one import identity per module |
| G-RV01-4 / G-RV01-5 | Version contract; promotion record from v0.8 to the shipped action guard |
| G-FORGE-REMINT, G-RESEAL, G-PYC-SEAL | Reseal manifests after any change to sealed sources |
| G-RV01-1 | Name the "third brain" owner |
| B39-R3 | One dependency authority (`pyproject.toml`) |

## T4: mathematics

| ID | What |
|---|---|
| G-MASTER-EQ, G-PITH, G-LYAP | The master equation cannot bifurcate at Π_th as stated; the Lyapunov argument is restricted |
| G-M-2 | Harmonia metric versus its prime-factor specification (strict xfail holds it) |
| G-M-4 | Narrow the published conditions (N1–N3 addenda) |
| G-PAID-WORK → G-FACTORIAL-RECORD | The factorial record waits on paid-work scope |
| G-SHEAF-ENCODING, G-RV37-3/4 | Sheaf encoding; the Hexie aggregate's binding-constraint claim |

## T5: housekeeping and taste (Mac's eye)

G-COMIC-ART-WEIGHT (128 MB of PNGs), G-DEAR-AI-RETIRE, G-MEMORIA-IMPLEMENTATION, G-EPIC-LISTENING-SOURCE, G-VEYRA-STATUS, G-II-STATUS, and the three still-unmarked documents (Appendix E).

## Outside validation (parallel to everything)

**G-RV36-5:** the register is self-review plus AI review. Nothing in T0–T5 replaces one human reviewer or one submitted paper. Start that conversation now; it takes the longest.
