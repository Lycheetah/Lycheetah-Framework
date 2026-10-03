# A Cybernetic Reading of the Lycheetah Framework

**Author:** Mackenzie Conor James Clark · Lycheetah Framework. Drafted with an AI collaborator, 2026-10-03.
**Companion files:** [`LOOP_MAP.json`](LOOP_MAP.json) (the evidence) · [`loop_audit.py`](loop_audit.py) (the check) · [`variety_demo.py`](variety_demo.py) (the toy world).

---

## §0 How to read this document

Every section carries a status:

- **MEASURED:** observed by running code in this repository. Reproduce it with the command given.
- **DERIVED:** follows from named evidence by stated reasoning.
- **INTERPRETIVE:** a structural reading. It may be illuminating, but it is not an empirical fact, and it does not make the framework's claims any stronger.
- **CONJECTURE:** plausible, unverified, with a stated test.

The references in §10 are cited **from memory**. None was re-read for this document. Each should be checked against the source before it carries weight in any argument.

---

## §1 The vocabulary

**MEASURED**, as definitions in `LOOP_MAP.json`.

A feedback loop has five parts:

- an **essential variable**: the thing that must stay within bounds;
- a **sensor** that reads it;
- a **comparator** that holds the reading against a **setpoint**;
- an **actuator** that changes the world in response;
- a **feedback path** by which the actuator's effect reaches the sensor again.

A loop is **closed in code** when that path runs through the code. It is **open in code** when a person, a host model or nothing at all has to finish it.

Each sensor is also tagged with its **channel**:

- **state:** the system's own variables;
- **text:** surface features of language;
- **self_report:** numbers a person types in;
- **caller_supplied:** numbers handed in by whoever calls.

The channel decides what the loop can know. A loop that senses text can regulate text. Whether it regulates anything beyond text depends on how well text tracks the thing that matters (§5).

---

## §2 Where each loop closes

**MEASURED** by `python3 34_CYBERNETICS/loop_audit.py`, which reads the syntax tree and fails if this table is wrong.

| Loop | Engine | Sensor channel | Closes in code | How it closes, or who closes it |
|---|---|---|---|---|
| L-GREY | AURA Grey Mode | state | **yes** | Dataflow: `recovery_cycle`'s result is passed to `compute_psi_r` inside the loop in `run` |
| L-CASCADE | CASCADE | state | **yes** | Shared state: `_execute_cascade` writes `.regime`, which `contradicts` reads on the next block |
| L-TRIAD | TRIAD | state | **yes** | Shared state: `single_step` reads and writes `.state` |
| L-TRIADKERNEL | LAMAGUE kernel | state | **yes** | Dataflow: `step`'s output is the next input to `norm` and to `step` |
| L-KURAMOTO | HARMONIA | state | **yes**, in simulation | Shared state: each oscillator writes `.phase`, which the coupling sum reads |
| L-AURA | AURA | text | no | Whoever calls `check()`: a person, a host model, a wrapping system |
| L-TRIAXIAL | AURA TES/VTR/PAI | text, caller_supplied | no | Nobody in code. `apply_vip` returns template text, and `check()` never calls it |
| L-MICROORCIM | MICROORCIM | self_report | no | The person who reads the score and changes their day |
| L-PIPELINE | CASCADE → TRIAD → AURA | text | no | Nobody. A breach appends a flag to the result |

**DERIVED:** the framework holds two kinds of thing under one family of names:

- **Regulators that act on their own state.** Grey Mode, CASCADE, TRIAD and Kuramoto.
- **Instruments that report to a person.** AURA, TRI-AXIAL and MICROORCIM.

Both are legitimate. A reader is misled only when an instrument is described as if it were a regulator.

---

## §3 CASCADE and ultrastability

**INTERPRETIVE**, with the structure MEASURED.

Ashby's homeostat runs two loops (Ashby 1952):

- **The first loop** keeps the essential variables in bounds through ordinary feedback.
- **The second loop** acts only when the first has failed and an essential variable has left its bounds. It then makes a step change to the parameters the first loop runs on, and keeps changing them until the first loop holds again.

He called this **ultrastability**.

CASCADE has the same shape:

- **First loop.** Each incoming block is placed by truth pressure Π: FOUNDATION at Π ≥ 1.5, THEORY at Π ≥ 1.2, EDGE otherwise. This is sorting against thresholds.
- **Second loop.** When a new block contradicts an established universal block in the same domain, and the trigger margin is met, `_execute_cascade` reorganises the structure the first loop runs on. The old block is demoted to `qualified`, and its uncertainty is raised (divided by γ = 0.85), which lowers its Π. The new block is promoted, and the layers are reassigned.

The second loop changes the ground the first loop stands on. That is the ultrastable pattern.

**Where the analogy stops:**

- **The environment is a stream of blocks, not a world.** CASCADE's "essential variable" is internal consistency between the blocks it holds. Nothing outside the representation pushes back. This is why benchmark results on CASCADE's own block encodings do not count as external validation (ledger point 7).
- **The step change is deterministic.** Ashby's second loop searched at random through parameter settings. CASCADE's applies one fixed rule. It is closer to a rule-governed reorganisation than to ultrastable search.
- **The second loop's self-check cannot fail.** The event field `demotion_correct` re-checks the same filter that built the list of conflicts, so it is always true. A second loop whose own audit cannot say no is still a loop, but it has no witness.

**What this reading buys:** a precise question to ask of any belief-revision engine. Does its reorganisation fire on the failure of its first loop, or on something else? For CASCADE, MEASURED: it fires on contradiction, which is the first loop's failure to hold two blocks at once.

---

## §4 Constraint versus dictate: requisite variety

**MEASURED** in a SYNTHETIC world, **DERIVED** bound, **CONJECTURE** for language models (CYB-004).

### The law

Ashby's law of requisite variety (Ashby 1956): only variety in the regulator can absorb variety in the disturbances. If disturbances can take many forms and the regulator has few responses, then some disturbances will get through to the essential variable, however well the responses are chosen.

### Two ways to build a regulator

- **A dictate** says what to do. Its variety is the number of rules written. Against a disturbance no rule anticipated, it falls back on a default, and the default is wrong for nearly everything.
- **A constraint** says what must stay true. It leaves the doing to a generator, which proposes candidate actions, and a gate admits only those that keep the invariant.

The generator can produce responses nobody wrote down. That is the hope behind constitutional approaches to AI, AURA included: write the invariants, not the actions.

### The toy world

`variety_demo.py` builds the smallest world in which the difference shows:

- 24 disturbances and 24 actions;
- disturbance *d* and action *a* produce outcome (*d* + *a*) mod 24;
- for each disturbance, exactly one action keeps the outcome in the goal region;
- the rulebook has seen 8 of the 24 disturbances; the other 16 are novel.

Four regulators face all 24 disturbances:

| Regulator | Seen: survived / refused / wrong | Novel: survived / refused / wrong | Distinct actions | Distinct outcomes |
|---|---|---|---|---|
| **rulebook** (8 written rules, default otherwise) | 8 / 0 / 0 | 0 / 0 / 16 | 8 | 17 |
| **gated, true sensor** (full repertoire) | 8 / 0 / 0 | 16 / 0 / 0 | 24 | 1 |
| **gated, narrow repertoire** (6 actions) | 2 / 6 / 0 | 4 / 12 / 0 | 6 | 1 |
| **gated, proxy sensor** (passes reassuring words) | 0 / 0 / 8 | 0 / 0 / 16 | 15 | 16 |

Reproduce it with `python3 34_CYBERNETICS/variety_demo.py`. The run is deterministic at seed 1952; `--json` gives the full record.

### What the table shows

1. **The dictate is perfect where it was written and wrong everywhere else.** Sixteen novel disturbances, sixteen wrong actions, and no refusal that would warn anyone.
2. **The constraint, with enough variety and an honest sensor, holds on every novel disturbance.** This is the claim for constraints, and in this world it is true.
3. **Failure condition (a): too little generator variety.** With only six actions available, the gated regulator cannot find a passing action for most disturbances, so it **refuses**. That is a visible failure: a refusal is a signal someone can act on.
4. **Failure condition (b): a proxy sensor.** The proxy passes any proposal whose text carries a reassuring phrase ("reversible", "you decide"). It admits wrong actions **with confidence**: zero survived, and zero refused. That is a silent failure, the worst kind, because the gate's "yes" looks exactly like the honest gate's "yes".

### The bound

**DERIVED.** In this world the outcome table is a Latin square: each action sends distinct disturbances to distinct outcomes. Suppose a regulator acts on *m* disturbances using *k* distinct actions. By pigeonhole, some action handles at least ⌈*m*/*k*⌉ of them, and each of those lands on a distinct outcome. So:

**distinct outcomes ≥ ⌈*m* / *k*⌉**

This is Ashby's V(O) ≥ V(D) / V(R) made concrete. The demo checks the bound for every regulator and exits non-zero if it fails. It holds in every run:

| Regulator | Acted on (*m*) | Actions (*k*) | Bound | Outcomes |
|---|---|---|---|---|
| rulebook | 24 | 8 | 3 | 17 |
| proxy | 24 | 15 | 2 | 16 |
| honest gate | 24 | 24 | 1 | 1 |

The narrow gate acted on only 6 disturbances with 6 actions, so its bound is 1, and it achieved 1.

### The reading

A constraint beats a dictate only under two conditions:

1. The generator has the variety the disturbances demand.
2. The gate's sensor reads the essential variable, not a proxy for it.

Constitutional gating is not a free lunch. It moves the hard problem from "write the right rules" to "build a sensor that sees outcomes". AURA, as a gate, inherits condition 2 directly (§5).

### CONJECTURE (CYB-004)

The same two conditions decide whether constraint-gated language models handle prompts no rule anticipated. **Test:** a preregistered study in which a constraint-gated model and an ungated baseline face prompts outside any written rule, and blind raters score the outcomes rather than the wording. **The conjecture fails if:**

- gated outputs survive no better than the baseline; or
- the gate's pass rate does not track the outcomes the raters judged.

Not run.

---

## §5 The Good Regulator, and AURA's sensor

**DERIVED** from the code; the remedy is SCAFFOLD.

Conant and Ashby (1970): every good regulator of a system must be a model of that system. A regulator can steer only as well as it represents what it steers.

AURA's essential variable is whether an output preserves human primacy, reversibility, honesty and the other invariants. Its sensor, `_count_patterns`, reads regular-expression cues in the output's text. So what AURA models is **how outputs talk about effects**, not the effects themselves. A fluent output can say "you decide; every step is reversible" while removing the person's choice, and the sensor will read it as compliant. The proxy arm in §4 is this failure in miniature.

That is not an argument against AURA. A text sensor is cheap, runs at inference time, and catches a real class of failures: outputs that do not even gesture at the invariants. It is an argument about what AURA's pass can mean. **A pass means the output's language is consistent with the invariants. It does not mean its effects are.**

**The seam already in the code.** `AURAChecker.check` accepts `context["human_capabilities"]`, a channel through which a caller can supply a measure of effect instead of a feature of wording. That is the existing path toward a sensor that reads outcomes. Building it means deciding what to measure (options presented, actions taken, reversals possible), which is an empirical design problem, not a coding one. **SCAFFOLD.**

---

## §6 Second-order cybernetics: the observer inside the loop

**INTERPRETIVE.**

First-order cybernetics studies the system being regulated. Second-order cybernetics (von Foerster) includes the observer: the regulator's own descriptions become part of what is regulated.

### Pask and the Two-Point Protocol

The framework's Two-Point Protocol treats a human–AI dialogue as the unit of analysis. Gordon Pask's Conversation Theory (Pask 1975) did this for two participants half a century earlier. Two participants reach a shared understanding through *teachback*: each restates the other's concept until the restatements agree. **Pask is the nearest precedent, and the lineage map now says so.** Three things remain distinctive:

- one participant is a language model;
- turns can be gated by computable invariants (AURA);
- an evidence-status ledger records not only what was agreed but how well it is known (ACTIVE, SCAFFOLD, CONJECTURE, RETRACTED).

Whether these differences matter is an empirical question, not a naming one.

### The Living Codex as a second-order loop

[`29_GOVERNANCE/LIVING_CODEX_PROTOCOL.md`](../29_GOVERNANCE/LIVING_CODEX_PROTOCOL.md) describes how the framework revises its own claims:

- **Sensor:** critique enters through the Critique Register.
- **Comparator:** each change must pass the P∧H∧B update gate.
- **Actuator:** claims are promoted, retracted or rewritten.

This is a loop whose regulated variable is the framework's own description of itself, and **it closes through the author, not in code.** The outside-review ledger of 2026-10-03 is one turn of it.

### Autopoiesis: declined

Maturana and Varela (1980) define an autopoietic system as one that produces the components that produce it. The framework does not do that; its author does. We do not claim the framework is autopoietic.

---

## §7 Beer's Viable System Model

**INTERPRETIVE.** A mapping, not a diagnosis.

Stafford Beer's Viable System Model (Beer 1972, 1979) names five functions any viable system needs. The framework's parts can be laid against them:

| VSM function | Role | Nearest framework part | Fit |
|---|---|---|---|
| System 1 | Operations | The engines' outputs: classifications, corrections, checks | loose |
| System 2 | Coordination, damping oscillation between units | HARMONIA (Kuramoto coupling) | structural; AI application CONJECTURE |
| System 3 | Control of the here-and-now | TRIAD (convergence toward a target) | structural |
| System 3* | Sporadic audit | MICROORCIM drift reports; the Failure Museum | structural for the museum; MICROORCIM is a mirror (§2) |
| System 4 | Intelligence: the outside and the future | CASCADE (reorganisation on new evidence) | partial; its "outside" is the block stream |
| System 5 | Identity and policy | AURA's invariants plus human primacy | structural |

**What the mapping does not show:**

- The VSM requires recursion: each System 1 unit is itself a viable system. Nothing here is checked for that.
- It requires the variety-engineering channels between systems to be adequate. These are not measured.

A table like this is a way to ask questions, not an answer. Its sharpest question: **where is System 3\* for AURA?** Who audits whether AURA's passes track outcomes? Today nobody does (§5).

---

## §8 The pipeline finding

**MEASURED**, then repaired.

`12_IMPLEMENTATIONS/core/sovereign_pipeline.py` chains CASCADE → TRIAD → AURA → a MICROORCIM-style drift check. On 2026-10-03, building the loop audit showed that:

- **`run()` raised `AttributeError` on every call.** It called `TriadTracker.run`, which does not exist.
- **No test exercised it.**

It now calls `run_until_convergence`. [`tests/test_sovereign_pipeline.py`](../tests/test_sovereign_pipeline.py) runs it end to end and checks that the TRIAD stage converges to its target.

Even repaired, the pipeline is **feedforward**. AURA measures drift between TRIAD's target and the field coherence, and a breach appends a flag. Nothing feeds that drift back into TRIAD's target or CASCADE's blocks. Closing it would mean:

- feeding AURA's measured drift back as a correction to TRIAD's target;
- re-running until the drift falls below threshold or a budget is spent;
- refusing visibly when the budget runs out.

That is §4's honest gate in pipeline form. **SCAFFOLD.** The audit's self-test wires exactly this edge in memory and confirms it would be detected, so the map cannot silently fall out of date when someone builds it.

---

## §9 What cybernetics does not give us

**DERIVED.**

- **Good goals.** A regulator holds whatever setpoint it is given. TRIAD climbs whatever landscape the caller supplies. Cybernetics says how to hold a value, not which value to hold. AURA's invariants are the framework's answer to *which*, and their justification is ethical, not cybernetic.
- **A design.** The law of requisite variety is a bound. It says how much variety is needed, not how to build it.
- **Empirical validation.** Mapping CASCADE onto ultrastability does not make CASCADE's results external. Benchmarks on its own representation stay internal (ledger point 7).
- **Licence for the mystery-school prose.** A dynamical-systems reading of a tradition does not prove the tradition. Where the doors say "guaranteed" without the contraction condition, the ledger accepts the criticism line by line.
- **Novelty for the loop structure.** Negative feedback is Wiener's; double loops are Ashby's; viable-system structure is Beer's; conversation as a unit is Pask's. What the framework adds must be found elsewhere: in the invariants, the register discipline and the AI participant.

---

## §10 References

**All cited from memory; none re-read for this document.** Grades: *theory* (a book or paper setting out a framework), *theorem* (a paper proving a result), *study* (empirical).

- Wiener, N. (1948). *Cybernetics: Or Control and Communication in the Animal and the Machine.* MIT Press. — from memory · theory
- Ashby, W. R. (1952). *Design for a Brain.* Chapman & Hall. — from memory · theory (ultrastability, the homeostat)
- Ashby, W. R. (1956). *An Introduction to Cybernetics.* Chapman & Hall. — from memory · theory (law of requisite variety)
- Conant, R. C., & Ashby, W. R. (1970). Every good regulator of a system must be a model of that system. *International Journal of Systems Science*, 1(2), 89–97. — from memory · theorem
- Beer, S. (1972). *Brain of the Firm.* Allen Lane. — from memory · theory (Viable System Model)
- Beer, S. (1979). *The Heart of Enterprise.* Wiley. — from memory · theory
- Pask, G. (1975). *Conversation, Cognition and Learning.* Elsevier. — from memory · theory (Conversation Theory, teachback)
- von Foerster, H. (2003). *Understanding Understanding: Essays on Cybernetics and Cognition.* Springer. Collects essays from the 1960s–1990s. — from memory · theory (second-order cybernetics)
- Maturana, H. R., & Varela, F. J. (1980). *Autopoiesis and Cognition: The Realization of the Living.* Reidel. — from memory · theory
- Goodhart, C. A. E. (1975). Problems of monetary management: the U.K. experience. Papers in Monetary Economics, Reserve Bank of Australia. — from memory · theory (the proxy-target law later named after him)
- Kuramoto, Y. (1984). *Chemical Oscillations, Waves, and Turbulence.* Springer. — from memory · theory

Jay Forrester's system dynamics is already credited in [`30_MAPS/LINEAGE_MAP.md`](../30_MAPS/LINEAGE_MAP.md), Tributary III.
