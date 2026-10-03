# 34_CYBERNETICS — Where the Loops Close

**Status:** The loop audit is ACTIVE: it is checked by machine against the source on every run. The requisite-variety claim about language models is CONJECTURE: it is shown only in a synthetic toy world. The mappings onto Ashby, Beer and Pask are INTERPRETIVE.

**Author:** Mackenzie Conor James Clark · Lycheetah Framework. Drafted with an AI collaborator; every claim below carries its status. The cybernetic ideas belong to the authors credited in [`CYBERNETIC_READING.md`](CYBERNETIC_READING.md) §10.

---

## Why this folder exists

The framework's prior-art record already said it: *"The cybernetics connection should be explicitly stated"* ([`28_DEFENSE/PRIOR_ART.md`](../28_DEFENSE/PRIOR_ART.md), TRIAD). On 2026-10-03 a new reader ran an AI-assisted review of the repository and pressed on the same point. Is this cybernetics with new names? And which of the engines actually regulate anything?

This folder answers with code first and prose second. The rulings on every point of that review are in [`28_DEFENSE/OUTSIDE_REVIEW_LEDGER_2026-10-03.md`](../28_DEFENSE/OUTSIDE_REVIEW_LEDGER_2026-10-03.md).

## The thesis

**A loop regulates only where it closes.** A sensor that reads, a comparator that judges and no actuator that acts make a measurement, not a regulator. That is not a defect, but it must not be described as one.

Five of the nine loops the framework's implementations claim close in code:

- Grey Mode recovery
- CASCADE reorganisation
- TRIAD
- TRIADKernel
- HARMONIA's Kuramoto simulation

Four do not: the AURA constitutional check, the TRI-AXIAL check, the MICROORCIM tracker and the sovereign pipeline. Each of these senses and compares, then hands its verdict to a person or a host model, and that person or model is where the loop closes.

For AURA, this is deliberate: under human primacy, the verdict goes to a person. It also means AURA is a sensor. A sensor is only as good as what it reads, and AURA reads words. [`CYBERNETIC_READING.md`](CYBERNETIC_READING.md) §5 works out what follows from that, and names the seam already in the code that leads toward a sensor that reads effects.

## Files

| File | What it is | Status |
|---|---|---|
| [`LOOP_MAP.json`](LOOP_MAP.json) | Nine loops: sensor, essential variable, comparator, actuator, whether each closes in code, who acts when the code does not, and every known reader of each open loop | ACTIVE (audited) |
| [`loop_audit.py`](loop_audit.py) | Reads the syntax tree of the implementations and checks the map against it. Never imports or runs the audited code | ACTIVE |
| [`variety_demo.py`](variety_demo.py) | Ashby's law of requisite variety in a 24 × 24 toy world: a rulebook against constraint-gated generators | SYNTHETIC |
| [`CYBERNETIC_READING.md`](CYBERNETIC_READING.md) | The argument: role mapping, ultrastability, requisite variety, the Good Regulator, second-order cybernetics, the Viable System Model, and what cybernetics does not give us | INTERPRETIVE, with each section marked |
| [`../tests/test_cybernetics.py`](../tests/test_cybernetics.py) | The audit is clean and catches every mutation; the demo is deterministic and the Ashby bound holds | ACTIVE / CONJECTURE markers |

## How to run

Python 3.9+, standard library only. No installs.

```bash
python3 34_CYBERNETICS/loop_audit.py              # every mapped loop matches the code; exit 0
python3 34_CYBERNETICS/loop_audit.py --self-test  # in-memory mutations; each must be caught
python3 34_CYBERNETICS/loop_audit.py --json       # machine-readable rows
python3 34_CYBERNETICS/variety_demo.py            # the four regulators, side by side
python3 -m pytest tests/test_cybernetics.py -q
```

### What the audit checks

1. **Every named symbol exists.** The driver, sensor, comparator and actuator are checked in the file the map names.
2. **Closure matches the map.** The audit computes closure from the code. It counts a loop as closed when one of two things holds:
   - **Dataflow:** inside a loop in the driver, the actuator's result is passed back into the sensor.
   - **Shared state:** the actuator writes an attribute that the sensor reads on the next call.

   It then compares the computed answer with `closes_in_code`.
3. **Every reader of an open loop is listed.** All Python files in the repository are censused by syntax tree, with strings and comments ignored. Any file that references an open loop's class must appear in that loop's `known_callers`, because a reader is the place where an open loop might close without anyone noticing.
4. **The pipeline stays feedforward.** If any stage's output feeds an earlier stage inside a loop, the map is wrong and the audit says so.

The self-test applies five mutations to an in-memory copy of the source and requires each one to be caught. The source on disk is never touched. The five mutations:

- cut Grey Mode's actuator;
- rename its sensor;
- move CASCADE's state write;
- inject an unlisted reader of AURA;
- wire a feedback edge into the pipeline.

A gate means nothing until it has been seen to fail.

### What the audit cannot say

These limits are also printed in `loop_audit.py`:

- **Calls are matched by name.** Dynamic dispatch, callbacks and `getattr` are invisible to it.
- **A closed loop can still regulate the wrong variable.** Closure is structure, not correctness. TRIAD closes perfectly on whatever landscape it is handed.
- **"Open" is a design fact, not a defect.** AURA is open on purpose.
- **A loop nobody mapped is invisible.** The audit checks the map against the code; it does not discover loops.

## What building this found

These findings came out of doing the work, not out of the review:

- **The sovereign pipeline was dead.** `SovereignPipeline.run` called `TriadTracker.run`, which does not exist, so every call raised `AttributeError`, and no test exercised it. It is repaired, with [`tests/test_sovereign_pipeline.py`](../tests/test_sovereign_pipeline.py). It is still feedforward (SCAFFOLD).
- **The claim counts had drifted.** The README said 60, the register's own `total_claims` said 136, and the register held 67 records. The register is now the one truth: `python3 tools/verify-claims.py --register` pins every count that repeats it, and was seen failing on the old data before anything was fixed.
- **CASCADE's `demotion_correct` cannot fail.** The event field re-checks the same filter that built the list it is checking.
- **TRIADKernel's return annotation is wrong.** `correct_until_converged` is annotated and documented as returning a 2-tuple; it returns `(state, iterations, errors)`.
- **The pipeline does not use MicroorcimTracker.** It is the pipeline's only import of the class, and it is never instantiated; stage 4 recomputes a drift inline.

## What this folder does not claim

- It does not claim the framework *is* cybernetics, or that it *is not*. It claims where each loop closes, checked against the code.
- It does not claim that language models satisfy requisite variety under a constitutional gate. That is CYB-004, a CONJECTURE, and its falsification test is a study that has not been run.
- It does not claim CASCADE is a homeostat, or that the framework is autopoietic. Those readings are discussed and declined in [`CYBERNETIC_READING.md`](CYBERNETIC_READING.md).
- The demo is SYNTHETIC. A toy world shows what the law of requisite variety means; it measures nothing about the world.

## Claims in the register

| ID | Claim | Status |
|---|---|---|
| CYB-001 | Grey Mode recovery is a complete closed regulator in code | ACTIVE |
| CYB-002 | CASCADE closes through shared state; the ultrastability reading is interpretive | ACTIVE (structure) |
| CYB-003 | AURA, TRI-AXIAL and MICROORCIM are open in code; the pipeline is feedforward | ACTIVE |
| CYB-004 | Invariant-gated regulation meets requisite variety only with adequate generator variety and a non-proxy sensor | CONJECTURE |

Full records: [`28_DEFENSE/CLAIMS.json`](../28_DEFENSE/CLAIMS.json).
