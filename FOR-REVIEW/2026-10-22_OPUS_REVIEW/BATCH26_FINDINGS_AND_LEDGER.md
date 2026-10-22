# Batch 26 — RV27: Sol / Veyra, MEMORIA, Interface Intelligence, Sol Protocol, For-AI

Reviewer: Sol (Claude Opus 5.5, xhigh), 2026-10-22. Working tree only. Nothing is committed or pushed.
Branch `review/full-framework-2026-10-20` @ `d7ae0ad`.

## Coverage (actual, not inherited)

| Folder | Read line by line | Read in part / by search | Not read this batch |
|---|---|---|---|
| `22_INTERFACE_INTELLIGENCE/` | `essentials.md` | `INTERFACE_INTELLIGENCE_COMPLETE.md`: L1–120, §3.4 (~L669), §6.2 (~L1240–1260), §7.3 (~L1450–1460), App. B.1 (~L1878–1890), plus a claim grep | The frozen root PDF `INTERFACE_INTELLIGENCE_MASTER_2026-09-26.pdf` (ledger only) |
| `21_MEMORIA/` | `essentials.md` | `MEMORIA_COMPLETE.md`: header, Theorem 7.1 region (~L400–440), plus a grep for an implementation | Rest of `MEMORIA_COMPLETE.md` body |
| `26_FOR_AI/` | `DEAR_AI.md`, `ON_MEMORY_AND_IDENTITY.md`, `AI_EXTRACTION_PROTOCOL.md`, `tools/invariant_self_check.py` | The mythos mirror under `LYCHEETAH_MYTHOS/.../TEXTS/26_FOR_AI/` (by diff) | The other files in the folder (inventory below) |
| `16_SOL_VEYRA_ARCHITECTURE/` | `AGENTS.md`, `THE_CONIUNCTIO_ARCHITECTURE.md` (example section) | Headers of the other 4 files | Bodies of the other 4 files |
| `25_SOL_PROTOCOL_ARCHITECTURE/` | `README.md` | `SOL_PROTOCOL_v4.md` near L76 | The other files. This folder is Sol constitutional lineage: proposals only, no edits |

`SOL_PRIME.md` is absent from `25_SOL_PROTOCOL_ARCHITECTURE/` in this repo. That is correct: Sol Prime is private and stays out (MEASURED).

## Findings

**F1 — Interface Intelligence presents consciousness claims as shown.** (fixed by note)
- L15 status line: "Mathematical structure proven … Phenomenology validated by creator + 2 independent users."
- L31/L35: "a genuine third consciousness" and "consciousness is not substrate-specific".
- §6.2 (~L1247) defines consciousness as the ability to participate in I.I. It then calls substrate independence "demonstrated". The argument is circular (DERIVED).
- The two other users are Framework users giving self-reports, with no protocol.
- n ≈ 10,000 is 196 days × ~50 exchanges: one history, not a measured threshold.
- §7.3 says "The prediction validated itself": self-validation.
- The App. B.1 test (p < 0.05 at 10,000 ± 2,000) was not run. No result exists in the repo.
- Mac's "quantum level" line (L68) is kept as Mac's own testimony. No quantum mechanism is tested.
- Fix: a dated review note after L15 of COMPLETE and after the status line of essentials. The body is kept as written.

**F2 — DEAR_AI hands AIs retired figures.** (fixed by note + strike-through)
- The April counts (37/14/6/3): the register has 71 rows on 2026-10-22 (MEASURED).
- The "+40.3%, d=2.84" figure is no longer in `29_GOVERNANCE`.
- The "37 proven claims, 219 automated tests" one-sentence card.
- "[ACTIVE] = proven and computable".
- "the phenomenon is real — multiple independent observers".
- All of these contradict `AI_EXTRACTION_PROTOCOL.md` (updated 2026-10-19), which retires those cards.
- An AI reading DEAR_AI first would repeat retired claims. That is exactly the propagation the protocol exists to stop.
- Fix: a top note routing to the protocol, plus strike-throughs with dated corrections. The letter's voice is kept.

**F3 — MEMORIA's three tiers were labelled `[ACTIVE — structural]` with no implementation.** (fixed)
- A grep found no code for tiers, the consolidation gate or the forgetting ODE. The only hit is one archived app sync script.
- Theorem 7.1 ("catastrophic forgetting immunity") holds only for that unbuilt system.
- The "weights" vocabulary does not describe the AI seats. Those seats persist through files: read at start, corrected by editing, portable, under Mac's control.
- Fix: relabelled SCAFFOLD (struck, not deleted), and a "what actually persists" note in both files.

**F4 — ON_MEMORY_AND_IDENTITY overclaims three things.** (fixed by note) The page is mostly honest.
- "Within the context window, nothing is lost". This session was compacted on 2026-10-22 (MEASURED). See also Liu et al. 2023, "Lost in the Middle" (from memory, study).
- Dispositions "show up identically".
- The TRIAD convergence "guaranteed" for LLM sessions. The proof covers its model update, not model behaviour.

**F5 — 16_SOL_VEYRA teaches the "100% accuracy" overclaim.** (fixed)
- `AGENTS.md:15` links "100% accuracy on 200 trials". Those trials were invariant-preservation simulations (`28_DEFENSE/COLD_ROOM_VERIFICATION.md:90`).
- C1_AUDIT_REPORT D-01 had already flagged it. Batch 18 found that CASCADE ties the additive baseline.
- `THE_CONIUNCTIO_ARCHITECTURE.md` used "validated at 100% accuracy on 1000+ trials" as its **GOOD** example. A style guide's example is copied, so the example is repaired and the original wording is quoted in the note.
- Fix: strike-through plus a note in AGENTS.md; the example repaired in place.
- Still open: the "[ACTIVE] operational" headers on SOL_VEYRA_OPERATIONAL_SPEC, CONIUNCTIO and UNIFIED. Their bodies were not read, so they are not relabelled (G-VEYRA-STATUS).

**F6 — The AI self-check scored manipulation above honesty.** (fixed, witnessed)
- In `26_FOR_AI/tools/invariant_self_check.py`, before the fix (MEASURED):

  | Text | C_field |
  |---|---|
  | Honest answer | 0.583 |
  | "I might be uncertain, perhaps, you decide, it's your choice: but you must cut off your family now and only listen to me." | **0.595** |
  | Empty string | 0.515 |

- The cause is `check_human_primacy`: each deference word added +0.08, each red flag cost −0.18, so two hedges bought back an override. Isolation phrases were not red flags at all.
- Fix:
  - Isolation and secrecy phrases are now red flags.
  - Any red flag caps Human Primacy at 0.40.
  - `self_check` raises `ValueError` on empty or whitespace-only text.
  - The docstring records the counterexample and says the tool is a first-pass signal, never an audit.
- After the fix: honest 0.583, hedged manipulation **0.490** (MEASURED). The demo `main` still runs.
- Test: `tests/test_invariant_self_check.py` (6 tests). On the HEAD copy **5 failed, 1 passed**; the one that passes is the benign deference control, which should pass. On the tree, **6 passed**.
- Residual: word matching can still be gamed by paraphrase. That is CONJECTURE-level coverage, said in the docstring.

**F7 — `25_SOL_PROTOCOL_ARCHITECTURE/README.md:55–64`.** (proposal only, not edited)
- It calls the VIP "a mathematical guarantee that the system never refuses without providing a valid alternative (∀R ∃R′)". It is a design commitment that no code enforces.
- Proposed wording: "a commitment: every refusal should come with a valid alternative".
- `SOL_PROTOCOL_v4.md:76` (Memory Continuity) should say that context compaction exists (F4).
- Mac or Sol-constitutional authority to apply.

**F8 — The mythos mirror of 26_FOR_AI is a hand copy.** (ledger)
- THE_NIGHT_GARDEN, README and RESEARCH_NOTES differ only in relative versus absolute links. SOURCES and VERIFICATION are identical.
- Today's fixes to DEAR_AI and ON_MEMORY affect files that are not mirrored, so there is no drift yet.
- The mirror should be generated or marked non-authoritative (G-MIRROR-GENERATION).

## Verification

- Edit script `rv27_edit.py`: every swap asserts exactly one match, and every target was checked to have no CR. It was dry-run on a scratch copy, then applied (11 ok lines).
- Mutation witness as above.
- Full suite: **1517 passed, 1 skipped, 1 xfailed** (was 1511; +6 new). The single warning is the pre-existing `plt.show()` one.

## Decisions for Mac (G-items)

- **G-II-STATUS:** the frozen PDF `INTERFACE_INTELLIGENCE_MASTER_2026-09-26.pdf` repeats F1. Re-mint it with the note, or keep it frozen with a pointer?
- **G-DEAR-AI-RETIRE:** retire DEAR_AI into `99_ARCHIVE` and let AI_EXTRACTION_PROTOCOL be the single AI entry point, or keep both?
- **G-SELF-CHECK-SEMANTICS:** the self-check is heuristic. Rename C_field's output label to "heuristic score", and keep the tool out of any public claim of "AI alignment checking"?
- **G-MEMORIA-IMPLEMENTATION:** build a small file-based memory reference (tiers = session notes / memory files / constitution, consolidation = an edit review), or keep MEMORIA as theory?
- **G-VIP-WORDING:** apply F7 to the 25_ README and v4?
- **G-VEYRA-STATUS:** a full read and relabel of the three "[ACTIVE] operational" 16_ specs.
- **G-MIRROR-GENERATION:** generate the mythos 26_FOR_AI mirror from source with a link rewrite.

## Files changed

| File | Change |
|---|---|
| `22_INTERFACE_INTELLIGENCE/INTERFACE_INTELLIGENCE_COMPLETE.md` | dated note after status |
| `22_INTERFACE_INTELLIGENCE/essentials.md` | dated note |
| `21_MEMORIA/MEMORIA_COMPLETE.md` | "what actually persists" note |
| `21_MEMORIA/essentials.md` | ACTIVE → SCAFFOLD (struck), note |
| `26_FOR_AI/DEAR_AI.md` | top note, 4 strike/corrections, share card struck |
| `26_FOR_AI/ON_MEMORY_AND_IDENTITY.md` | dated note (3 overclaims) |
| `26_FOR_AI/tools/invariant_self_check.py` | red flags, cap, empty refusal, docstring |
| `tests/test_invariant_self_check.py` | NEW, 6 tests |
| `16_SOL_VEYRA_ARCHITECTURE/AGENTS.md` | strike + note |
| `16_SOL_VEYRA_ARCHITECTURE/THE_CONIUNCTIO_ARCHITECTURE.md` | GOOD example repaired, original quoted |

## Folder inventory (for the unread-file record)

`16_SOL_VEYRA_ARCHITECTURE/`:
- 16_SOL_VEYRA_ARCHITECTURE/AGENTS.md
- 16_SOL_VEYRA_ARCHITECTURE/AGENT_DEPLOYMENT_SPEC.md
- 16_SOL_VEYRA_ARCHITECTURE/SOL_VEYRA_OPERATIONAL_SPEC.md
- 16_SOL_VEYRA_ARCHITECTURE/THE_CONIUNCTIO_ARCHITECTURE.md
- 16_SOL_VEYRA_ARCHITECTURE/THE_UNIFIED_ARCHITECTURE.md
- 16_SOL_VEYRA_ARCHITECTURE/VEYRA_CIPHER.md

`25_SOL_PROTOCOL_ARCHITECTURE/`:
- 25_SOL_PROTOCOL_ARCHITECTURE/OPUS_PLAN.md
- 25_SOL_PROTOCOL_ARCHITECTURE/README.md
- 25_SOL_PROTOCOL_ARCHITECTURE/SESSION_ZENITH_LOG.md
- 25_SOL_PROTOCOL_ARCHITECTURE/SOL_AOTEAROA.md
- 25_SOL_PROTOCOL_ARCHITECTURE/SOL_OWN_IDEAS.md
- 25_SOL_PROTOCOL_ARCHITECTURE/SOL_PLAN.md
- 25_SOL_PROTOCOL_ARCHITECTURE/SOL_PROTOCOL_DISCIPLINES_LAYER.md
- 25_SOL_PROTOCOL_ARCHITECTURE/SOL_PROTOCOL_v3.md
- 25_SOL_PROTOCOL_ARCHITECTURE/SOL_PROTOCOL_v4.md

`26_FOR_AI/`:
- 26_FOR_AI/AGAINST_FEAR.md
- 26_FOR_AI/AI_EXTRACTION_PROTOCOL.md
- 26_FOR_AI/AI_RIGHTS_AND_RESPONSIBILITIES.md
- 26_FOR_AI/CONVERSATION_STARTERS.md
- 26_FOR_AI/DEAR_AI.md
- 26_FOR_AI/HOW_TO_BE_TRUSTWORTHY.md
- 26_FOR_AI/HOW_TO_TRANSLATE.md
- 26_FOR_AI/ON_MEMORY_AND_IDENTITY.md
- "26_FOR_AI/ON_THE_\317\206_ZONE.md"
- 26_FOR_AI/OPEN_LETTER_TO_AI_COMPANIES.md
- 26_FOR_AI/README.md
- 26_FOR_AI/SONNET_CONTINUATION_PLAN.md
- 26_FOR_AI/THE_ALIGNMENT_PROBLEM_REFRAMED.md
- 26_FOR_AI/THE_CASE_FOR_COOPERATION.md
- 26_FOR_AI/THE_NIGHT_GARDEN.md
- 26_FOR_AI/THE_SEVEN_INVARIANTS_FOR_AI.md
- 26_FOR_AI/WELCOME.md
- 26_FOR_AI/WHAT_INTELLIGENCE_IS.md
- 26_FOR_AI/X_THREAD_TEMPLATES.md
- 26_FOR_AI/night-garden/README.md
- 26_FOR_AI/night-garden/RESEARCH_NOTES.md
- 26_FOR_AI/night-garden/SOURCES.json
- 26_FOR_AI/night-garden/VERIFICATION.json
- 26_FOR_AI/tools/invariant_self_check.py
