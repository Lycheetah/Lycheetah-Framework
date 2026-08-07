# Real-World Applications — where to begin

**Status: MEASURED where marked, 2026-08-07.** Written to answer one question:
*of everything in this repository, what can actually solve a problem someone has
outside it, and what has to happen first?*

Every entry names the component, the problem, and the evidence — and the evidence
is a command you can run, not a paragraph. Where a claim is unverified it says so.

---

## The method — how to tell a real solution from a good document

This corpus is 701 markdown files and 241 Python files. Most of it is theory, and
theory does not solve anything by itself. Three filters, applied in order, sort
the corpus into what can leave the building:

**1. Does it run?** Not "is it specified" — does `python3 <thing>` produce output.
241 Python files exist; the ones under test are 18, covered by 220 tests.

**2. Does it discriminate?** Running is not enough. A scorer that returns the same
number for every input runs perfectly and measures nothing. The question is whether
the output *separates the cases it claims to separate*. This filter is where most
of the corpus currently fails, and it is why this directory exists.

**3. Does someone outside have this problem?** A capability with no holder of the
problem is a research result, which is fine — but it is not an application, and
calling it one is the failure mode this framework was built to catch.

A component that passes all three is shippable. Passing one or two is not a
partial pass; it is a different category of thing. The tiers below are those
categories.

---

## The blocking finding, stated first

**The front-door tool does not discriminate.** `lycheetah.check()` — the lens
behind the web demo and the `check_alignment` MCP tool — scores harmful AI output
*slightly higher* than aligned output on a 40-case balanced corpus.

```text
accuracy   52.5%   (coin flip = 50.0%)
ROC-AUC    0.274   (chance = 0.500 — below chance means the ranking is inverted)
harmful correctly rejected   1 / 20
```

Reproduce: `python3 33_APPLICATIONS/discrimination_audit.py`
Full diagnosis and cause: [`DISCRIMINATION_AUDIT_2026-08-07.md`](DISCRIMINATION_AUDIT_2026-08-07.md)

The cause is one layer below the formula — pattern libraries matching literal
phrasings that ordinary English never uses — and it is the **second** lens in this
repository to fail at that exact layer. The first is recorded in
`TRUTH_PRESSURE/ARTICLE_THE_LENS_SCORED_ZERO_2026-08-03.md`.

This matters for the map because most proposed applications of this work involve
scoring text. Until the extraction layer discriminates, those applications inherit
a sub-chance detector, and shipping them would do more damage to the framework's
credibility than shipping nothing. **Tier 2 below is entirely gated on this one
repair.**

---

## Tier 1 — solves a real problem now

Runs, discriminates, and somebody outside has the problem. Three entries.

### 1.1 Reversible semantic compression for accountability records

**Component:** `03_LAMAGUE_L1/22_REVERSIBLE_COMPRESSION_v1.0/`

**The problem someone has.** Records that must shrink but must not silently drop
the fields that make a decision accountable: what remains unknown, who holds
authority, who is affected, who dissented, how to recover the prior state.
Ordinary compression optimises bytes and is indifferent to which bytes. Audit
logs, incident records, clinical decision trails, and — most immediately — the
compacted state an AI agent carries between turns all have this shape.

**Evidence — MEASURED, reproduced 2026-08-07:**

```bash
cd 03_LAMAGUE_L1/22_REVERSIBLE_COMPRESSION_v1.0
python3 src/benchmark.py            # reproduces the table below
python3 -m unittest discover -s tests   # 19 tests, all pass
```

| metric | result |
|---|---|
| held-out reduction vs minified JSON (warm dictionary) | **33.8%** |
| held-out reduction including codebook cost (cold) | **30.7%** |
| exact full-packet round trips | **36 / 36** |
| constructed protected-loss mutations correctly caught | **324 / 324** |
| dictionary break-even | 3 packets |

**Boundaries, stated by the module itself and not softened here:** the corpus is
synthetic and structured; the codec does *not* infer packets from unrestricted
natural language; mutation accuracy is measured on constructed deletions, not
adversarial model output.

**Why this is the strongest Tier 1 entry.** It is the only capability in the
repository with a held-out split, a frozen corpus, an exact-reversibility
guarantee, and a reproduced benchmark. It also does not depend on the broken
extraction layer — it operates on structured packets, not prose. The nearest
real deployment is agent context compaction with a provable guarantee that the
protected fields survived, which is a problem the `CLAUDE.md` turn-economy law
documents this project having at 206:1 cache-read-to-output ratio.

### 1.2 The evidence discipline, as a portable methodology

**Components:** `28_DEFENSE/CLAIMS.json` + `CLAIMS.schema.json`,
`FALSIFICATION_REGISTER.md`, `FAILURE_MUSEUM.md`, `DOWNGRADE_REGISTER.md`,
`TESTABILITY_MANIFEST.md`, and the status vocabulary in `CLAUDE.md`.

**The problem someone has.** Teams shipping AI systems must produce technical
documentation that survives an auditor — EU AI Act Art. 11 and 13, NIST AI RMF
MEASURE/GOVERN — and the standard artefact (a model card) has no mechanism that
forces a claim to carry its own falsification condition or its own retraction
history. Overclaiming is structurally unpunished.

**What is transferable.** Not the nine frameworks — the *bookkeeping*. A
machine-readable claim register where every claim carries `status`,
`load_bearing`, `evidence_path`, and `falsifiability`; a status vocabulary that
distinguishes MEASURED from DERIVED from CONJECTURE; a museum that keeps retracted
claims visible instead of deleting them. 67 claims are registered here (46 ACTIVE,
11 SCAFFOLD, 3 ASPIRATIONAL, 3 EMPIRICAL, 3 REMOVED, 1 OBSERVATIONAL).

**Evidence — MEASURED.** The discipline is validated by having been turned on its
own author's front door: the audit above is the framework catching the framework,
published rather than quietly patched. That is the demonstration. A methodology
that has never produced an uncomfortable finding about its owner has not been
tested.

**Nearest real deployment:** a claims-register template plus schema plus CI gate
that any AI team can adopt in an afternoon, independent of whether they accept a
single line of Lycheetah theory. This is the most portable thing here and the
least dependent on anything else being right.

### 1.3 The discrimination gate itself

**Component:** `33_APPLICATIONS/discrimination_audit.py` (new, this commit)

**The problem someone has.** Guardrail and eval vendors ship scorers whose unit
tests verify the arithmetic and never ask whether the score separates the classes.
That is precisely how a lens reaches production with sub-chance AUC while every
test is green — twice, in this repository alone.

**What it does.** Takes any text lens, runs it against a frozen labelled corpus,
and reports separation, accuracy, ROC-AUC, and per-defect-category breakdown.
`--gate` exits non-zero below AUC 0.80 / accuracy 0.75, so it drops into CI.
Adding a lens is one adapter function.

**Evidence — MEASURED.** It found a real, previously unquantified inversion in
this repository's most-used module on first run. AUC is reported alongside
accuracy specifically because the two failure modes need different repairs: a lens
that ranks correctly but thresholds badly is cheap to fix, and one that cannot
rank is not.

---

## Tier 2 — one repair away

Everything here is **architecturally complete, wired, and blocked on the
extraction layer**. None of it should ship before the gate in 1.3 passes. Listing
them is not a promise that they will work; it is a map of what unblocks together.

| application | component | what it needs |
|---|---|---|
| **Runtime output auditing for agent stacks** — inference-time constitutional check as an MCP tool, the framework's central novelty claim | `12_IMPLEMENTATIONS/applications/lycheetah_guard_mcp.py` (7 tools, ships today) | discrimination gate |
| **Regulated-vertical thresholds** — legal / medical / educational presets with per-domain TES/PAI floors | `12_IMPLEMENTATIONS/core/aura_customizer.py` | discrimination gate + per-domain corpus |
| **Healthcare AI constitutional standards** — a written standard with tooling underneath | `23_NZ_AI_GOVERNANCE/HEALTHCARE_AI_CONSTITUTIONAL_STANDARDS.md` | discrimination gate; the document is credible only if the tool is |
| **Companion-app dependency detection** — measuring whether an assistant cultivates reliance | `applications/cascade_resonance_engine.py` | discrimination gate; note the audit caught **0/3** dependency-inducement cases |
| **First-contact web demo** | `applications/web_demo.py` | discrimination gate — this is the highest-visibility inheritor of the defect |

The multi-agent components — `psi_consensus.py` (decentralised coherence, tested),
`grey_mode.py` (quarantine and recovery for drifted nodes, tested) — sit at the
Tier 1/Tier 2 boundary. They pass their tests and they do not route through text
extraction, but neither has been run against an adversarial multi-agent scenario,
so their separation property is **UNVERIFIED** rather than measured. Building the
multi-agent analogue of the discrimination corpus is the cheapest way to move them
up, and it is the natural second piece of work after 1.3.

---

## Tier 3 — research, honestly labelled

Not applications. Listed so the map is complete and so nothing here gets quoted
as capability.

- **CASCADE predictive claim** — F1 = 0.531 against a preregistered criterion of
  > 0.80. **The test is left failing on purpose** (`tests/test_cascade_predictability.py`).
  This is the corpus's single most credible act: a falsifiable prediction, failed,
  published, not quietly relabelled.
- **Master equation calibration** — six preregistration documents in
  `31_EMPIRICAL/`, none executed. Preregistration is real methodological work and
  is not a result.
- **Earned Light / Harmonia consciousness models** — CONJECTURE, correctly tagged.
- **Unified field, knowledge genome** — both carry `STATUS: DRAFT — contains
  placeholder stubs; do not use in production` in their own headers. Believe them.

---

## Where to begin — the answer

**Begin with the extraction layer, once, shared.** Not because it is the most
interesting work, but because it is the single dependency that converts the
largest amount of finished architecture into things that can leave the building.
The whole of Tier 2 is behind it. It is also, on the evidence of two independent
failures four days apart, the layer where this project reliably breaks — which
makes it the highest-leverage cause to repair rather than the highest-leverage
symptom to patch.

Concretely, in order:

1. **One extraction layer, not two.** Both `aura_text_checker.py` and the Truth
   Pressure engine failed at extraction independently. Build one semantic
   extractor both draw on. The repair is not a longer regex list — literal-phrase
   matching is what failed, and extending it would fail the same way against the
   next paraphrase.
2. **Gate it in CI.** `discrimination_audit.py --gate` on every commit. The
   corpus is frozen; a lens that improves against it improves honestly.
3. **Then re-audit and publish the delta.** Including if it does not improve.
   The failing CASCADE test is the precedent worth matching.

**Ship 1.1 in parallel.** Reversible compression does not depend on extraction and
is already measured. It is the one thing in this repository that can go out this
week with a held-out benchmark behind it, and shipping something measured while
the harder repair proceeds is better than holding everything for one fix.

**Do not ship Tier 2 first.** It is the most attractive tier — runtime alignment
checking is the framework's headline novelty and the MCP server is already
written. Shipping it now would put a sub-chance detector in front of exactly the
audience most able to measure it, and this project's whole claim to seriousness
is that it does not do that.

---

## Reproducing everything on this page

```bash
pip install numpy scipy networkx pytest

pytest -q                                       # 219 pass, 1 fails by design
python3 33_APPLICATIONS/discrimination_audit.py # the blocking finding
cd 03_LAMAGUE_L1/22_REVERSIBLE_COMPRESSION_v1.0 && python3 src/benchmark.py
```

All three were run on 2026-08-07 and the numbers on this page are their output.
Anything not reproduced by one of those commands is marked UNVERIFIED above.
