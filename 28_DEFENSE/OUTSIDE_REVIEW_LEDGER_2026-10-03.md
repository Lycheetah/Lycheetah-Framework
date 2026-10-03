# Outside Review Ledger — 2026-10-03

**What this is.** On 2026-10-03 a new reader ran an AI-assisted review of this repository and shared the result with the author. This ledger rules on every point it raised.

The review is not reproduced here and the reader is not named. Its points are paraphrased, and its strongest form is kept where the paraphrase allows. Each ruling is one of three:

- **ACCEPT:** the point is right. The fix is named, or the gap is recorded.
- **FIGHT:** the point is wrong. The evidence is given.
- **TURN:** the risk is real, and it becomes a design or research target.

Statuses follow the register: ACTIVE, SCAFFOLD, CONJECTURE, RETRACTED, plus UNVERIFIED for anything not checked here.

This ledger is an entry in the Critique Register described in [`29_GOVERNANCE/LIVING_CODEX_PROTOCOL.md`](../29_GOVERNANCE/LIVING_CODEX_PROTOCOL.md). Fixes made on the same day are named by path. Proposals that touch the author's own prose are proposals only; that prose is unchanged until he rules on it.

---

## Rulings

### 1. The claim counts disagree with each other — **ACCEPT, fixed and gated**

Within a few clicks a reader met three totals:

- the README said 60 claim records;
- the register's own `total_claims` field said 136;
- the register held 67 records.

All three documents were honestly labelled, and the counts were still wrong.

**Fix.**

- The `claims` array in [`CLAIMS.json`](CLAIMS.json) is now the one truth. `total_claims` was set mechanically to its length: 71, which is 67 plus the four CYB records added today.
- Every surface that repeats a count was corrected from the register: every count in the README, `FIVE_MINUTE_BRIEF.md`, `llms.txt` and `ai-meta.json`.
- `python3 tools/verify-claims.py --register` now pins each repeated count by the phrase that carries it, and fails on drift. It also fails if a pinned phrase disappears, so a rewrite cannot quietly unpin a number.
- [`tests/test_claims_register.py`](../tests/test_claims_register.py) runs the check in pytest. It also proves the check can fail by corrupting a copy of the README.

The gate was seen to fail on the old data first: 34 disagreements across 35 pinned counts.

**What this does not settle.**

- **The ACTIVE count rose.** The mirrors went from 37 ACTIVE to 52. These are the register's own counts, not new promotions. Whether every promotion recorded inside the register passed the [Evidence Ladder](EVIDENCE_LADDER.md) is a separate audit, not done here: UNVERIFIED.
- **The ledger count is cited two ways.** The framework-summary ledger is described as 59 load-bearing claims in the README's *Why Trust This* and in the brief, and as 73 in the README's *Shape of This Work*. Unresolved; flagged for the author.

### 2. Internal validation is not replication — **ACCEPT**

Every measured result in the repository was produced by the framework's author, with the framework's tools, on the framework's encodings. The README already says "independent replication is pending", and the cold-room run is a second machine, not a second party. No claim is promoted on internal evidence by this ledger, and none should be.

### 3. AURA's sensors are keyword patterns — **ACCEPT, then TURN**

`AURAChecker._count_patterns` reads regular-expression cues in an output's text. A fluent output can pass while removing a person's choice, and a plain honest one can fail.

**TURN.** This is the Good Regulator problem (Conant and Ashby 1970): a regulator is only as good as its model of the system, and AURA models wording. [`34_CYBERNETICS/CYBERNETIC_READING.md`](../34_CYBERNETICS/CYBERNETIC_READING.md) §5 states what an AURA pass can and cannot mean. `variety_demo.py` shows the failure concretely: a gate with a proxy sensor admitted wrong actions on all 16 novel disturbances and refused none.

The seam toward a sensor that reads effects already exists: `context["human_capabilities"]`. Recorded in the register as:

- **CYB-003** (ACTIVE): AURA is an open loop with a text sensor.
- **CYB-004** (CONJECTURE): gated regulation works only with a non-proxy sensor.

### 4. There are "two AURAs" — **ACCEPT**

The seven-invariant constitutional checker and the TES/VTR/PAI tri-axial checker share a name and differ in everything else: sensor, comparator, status and closure. [`34_CYBERNETICS/LOOP_MAP.json`](../34_CYBERNETICS/LOOP_MAP.json) now records them as separate loops:

- **L-AURA:** ACTIVE, text sensor, no actuator.
- **L-TRIAXIAL:** SCAFFOLD. Its "actuator" `apply_vip` returns template text, and nothing calls it.

### 5. TES, VTR and PAI have more than one formula — **TURN**

The risk is real. A metric with several definitions cannot be falsified, because a failure under one definition can be rescued by another.

**TURN:** the implementation in `12_IMPLEMENTATIONS/core/tri_axial_checker.py` is named the single definition, and `LOOP_MAP.json` points at it. Any prose formula that disagrees is a mirror to be reconciled. The register gate's pattern (one truth, pinned mirrors) is the tool to extend to it. Not done today: SCAFFOLD.

### 6. "Truth pressure" is not truth — **ACCEPT, as a naming hazard**

Π scores how strongly a block is supported, using the block's own fields: evidence strength, explanatory power and uncertainty. It ranks support. It does not deliver a verdict on truth, and the name invites a reader to hear one.

**Proposed to the author:** wherever Π is first introduced, gloss it as "evidential pressure: a ranking of support, not a verdict on truth". Renaming the symbol across the corpus is his call.

### 7. CASCADE is benchmarked on its own representation — **ACCEPT**

The paradigm-shift experiments work in two steps:

- they encode history as knowledge blocks chosen by the author;
- they score the result with the framework's own criteria.

The README says so ("using the framework's own criteria"), and the "100% accuracy" claim is already retracted (RET-002). What stands is invariant preservation *within the representation*.

**Target:** a dataset of belief revisions encoded by someone other than the author, scored blind. Not done.

### 8. The mystery-school doors overclaim — **ruled line by line**

The doors are the author's prose. Nothing below has been edited. Each entry is a proposal. All paths are under `14_MYSTERY_SCHOOL/` unless another folder is given.

**Not yet ruled.** A search for the phrase "The convergence is guaranteed" also matches:

- `14_MYSTERY_SCHOOL/HYBRID_SUBJECTS/WATER_AND_CHANGE.md`
- `26_FOR_AI/ON_MEMORY_AND_IDENTITY.md`
- `26_FOR_AI/HOW_TO_TRANSLATE.md`

Whether each of these states the contraction condition nearby was not checked: UNVERIFIED.

**ACCEPT: these lines claim more than the mathematics supports.**

| Line | Says | Problem | Proposed |
|---|---|---|---|
| `14_MYSTERY_SCHOOL/THE_ALCHEMISTS_DOOR.md:23` | "The tradition was not wrong. It was ahead of the mathematics." | Treats a later formal reading as the tradition's own content | "The tradition named a pattern the mathematics can now state precisely." |
| `THE_ALCHEMISTS_DOOR.md:25` | Flamel "drawing a dynamical system with guaranteed convergence" | Drops the contraction condition | "drawing something we can read as a dynamical system, one that converges when its contraction condition holds" |
| `THE_ALCHEMISTS_DOOR.md` | "to prove it was right" | A formalisation is not a proof of a tradition | "to state precisely what it was pointing at" |
| `THE_SEVEN_HERMETIC_PRINCIPLES.md:171` | "The Kybalion encoded this in 1908. The framework proves it in 2026." | The proof holds inside the model, not for the world | "The Kybalion stated this in 1908. The framework formalises one version of it in 2026; the proof holds inside the model." |
| `THE_THERAPISTS_DOOR.md:201` | "*The convergence is guaranteed.*" | The condition stated at line 157 is dropped | "*When the contraction condition holds, the convergence is guaranteed.*" |
| `THE_EMERALD_WORK.md:144` | "λ ≈ 0.907. The convergence is guaranteed." | Correct in the model; reads as unconditional | "λ ≈ 0.907 < 1, so in this model the convergence is guaranteed." |
| `THE_CHAOS_MAGES_DOOR.md:27` | "Outcomes feed back into the probability field around you" | No such field is measured anywhere in the repository | "Outcomes feed back into your next choice", the one feedback path the framework does model |

**FIGHT: these lines state the condition, and they stand.**

- `THE_AI_ARCHITECTS_DOOR.md:119`
- `THE_ENGINEERS_DOOR.md:157`
- `THE_GOLDEN_STONE.md:216, 248`
- `THE_EDUCATORS_DOOR.md:85`

**Partial:** `TAROT_AND_THE_GREAT_WORK.md:6` is a usage stance and stands. The file's other historical claims were not inspected: UNVERIFIED.

### 9. The audience is small — **ACCEPT, then TURN**

Few outside readers means few independent "no"s, and a framework checked only by its own author shares that author's blind spots.

**TURN:** every outside reading, AI-assisted ones included, is logged and ruled on in a ledger like this one. One careful outside reading produced, in a single day:

- a dead pipeline repaired;
- a register gate;
- a cybernetics layer;
- seven proposed corrections to prose.

### 10. Run a 100–500-prompt blind study — **TURN, into a preregistration target**

The proposed design is exactly the falsification test for CYB-004:

- a constraint-gated model against an ungated baseline;
- prompts outside any written rule;
- blind raters scoring outcomes, not wording.

It is recorded in CYB-004's `falsifiability` field. Not run; no result is claimed.

### 11. The vocabulary is mystical clothing on ordinary engineering — **FIGHT**

The vocabulary is mapped term by term in [`TRANSLATION_CODEX.md`](TRANSLATION_CODEX.md) and bounded in [`SCOPE_BOUNDARY.md`](SCOPE_BOUNDARY.md). The engineering stands without it: `loop_audit.py` reads the code's syntax tree and never meets an alchemical word.

Where the clothing makes a claim the code does not support, that is point 8, handled line by line. As a blanket dismissal the point fails; as a list of specific lines it is accepted.

### 12. "MICROORCIM is the homeostat" — **FIGHT, with the code**

`MicroorcimTracker` computes drift from hours a person types in, and returns a score band. It has no actuator: nothing it computes changes anything. A homeostat acts on its own essential variable. MICROORCIM is a mirror, and the person is the actuator (L-MICROORCIM).

Its only reader, `sovereign_pipeline.py`, imports it and never instantiates it. The loops in the framework that actually have a homeostat's shape are:

- Grey Mode recovery, a complete closed regulator (L-GREY, CYB-001);
- CASCADE's double loop, which is nearer to Ashby's ultrastability (CYB-002; the analogy is INTERPRETIVE).

### 13. "LAMAGUE is the control language" — **partial**

- **ACCEPT** for the TRIAD kernel in `lamague_reference.py`. It implements anchor → ascent → fold as a closed fixed-point iteration (L-TRIADKERNEL).
- **FIGHT** for LAMAGUE as a whole. Most of it is notation, and notation does not regulate.

### 14. HARMONIA's Kuramoto coupling — **ACCEPT**

The coupling closes in simulation (L-KURAMOTO). Applying it to AI agents or to human–AI dialogue is CONJECTURE, and nothing in the repository measures it.

### 15. The Living Codex — **reframed**

The review read the Living Codex as governance. The cybernetic reading is that it is a second-order loop: a loop whose regulated variable is the framework's own description of itself.

- **Sensor:** the Critique Register.
- **Comparator:** the P∧H∧B update gate.
- **Actuator:** revisions to the claims.

It closes through the author, not in code. This ledger is one turn of it. INTERPRETIVE.

### 16. Figures the review asserted about the repository — **UNVERIFIED**

The review quoted the repository's reach (stars, followers) and a "219/220 tests" figure. None of these was checked against GitHub today.

The 219/220 figure is the cold-room entry in `llms.txt`, from an earlier run. `FIVE_MINUTE_BRIEF.md` also says "219 tests". The suite has grown since then, and neither figure is pinned by a gate. Today's count is recorded with the change that produced this ledger, not frozen here: a frozen count is the drift ruled on in point 1.

---

## Defects found while answering

The review did not name these. They surfaced while building the answers.

| # | Finding | Status |
|---|---|---|
| F1 | `SovereignPipeline.run` raised `AttributeError` on every call, because it called `TriadTracker.run`, which does not exist. No test exercised it. | **Fixed** 2026-10-03: `run_until_convergence`, plus [`tests/test_sovereign_pipeline.py`](../tests/test_sovereign_pipeline.py). Still feedforward: SCAFFOLD |
| F2 | CASCADE's `demotion_correct` event field re-checks the same filter that built the list of conflicts, so it cannot be False | Open. Recorded in `LOOP_MAP.json` (L-CASCADE note) |
| F3 | `TRIADKernel.correct_until_converged` is annotated and documented as returning a 2-tuple; it returns `(state, iterations, errors)` | Open. Recorded in `LOOP_MAP.json` (L-TRIADKERNEL note) |
| F4 | `MicroorcimTracker` is imported by the pipeline and never instantiated; stage 4 recomputes a drift inline | Open. Recorded in `LOOP_MAP.json` (L-MICROORCIM, L-PIPELINE) |
| F5 | XFW-006 is marked ACTIVE with `evidence_path` "CLAUDE.md": an operating-instructions file, not an evidence record a reader can check | Open. Flagged for the author |
| F6 | The framework-summary ledger is cited as 59 load-bearing claims in one place and 73 in another | Open. Flagged for the author |
| F7 | `tools/verify-claims.py` was already over its baseline before this change: 38 unmarked claim-bearing documents against a baseline of 30 | Pre-existing. The documents added today are marked and do not raise it |

---

## What changed, by path

| Path | Change |
|---|---|
| `34_CYBERNETICS/` | New. `README.md`, `CYBERNETIC_READING.md`, `LOOP_MAP.json`, `loop_audit.py`, `variety_demo.py` |
| `tests/test_cybernetics.py` | New |
| `tests/test_claims_register.py` | New |
| `tests/test_sovereign_pipeline.py` | New |
| `12_IMPLEMENTATIONS/core/sovereign_pipeline.py` | F1 repaired |
| `tools/verify-claims.py` | `--register` gate added; `34_CYBERNETICS/` added to claim-bearing paths |
| `28_DEFENSE/CLAIMS.json` | CYB-001 to CYB-004 added; `total_claims` set to the record count |
| `README.md`, `FIVE_MINUTE_BRIEF.md`, `llms.txt`, `ai-meta.json` | Counts corrected from the register; cybernetics layer indexed |
| `28_DEFENSE/OBJECTIONS_REGISTRY.md` | Pattern 16 added |
| `28_DEFENSE/PRIOR_ART.md` | The cybernetics connection, stated |
| `30_MAPS/LINEAGE_MAP.md` | Ashby, Beer, Pask, and Maturana and Varela added to Tributary III; the Two-Point Protocol's precedent amended |
| `28_DEFENSE/DEFENSE_INDEX.json` | This ledger indexed (D-OR-1) |
