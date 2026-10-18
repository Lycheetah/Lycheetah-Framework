# Core engines: what each tool does

The Python building blocks behind Lycheetah's knowledge organization, text
checking, language experiments, agent coordination and mathematical models.
There are **29 modules**, plus the package initializer.

**Creator:** Mackenzie Conor James Clark / Lycheetah Framework.  
**Guide status: [SCAFFOLD] documentation from source inspection.** Maturity varies by
module; the descriptions below identify its purpose and API, not independent
validation of its wider theoretical claims.

## Start with the job

| You want to… | Start here |
|---|---|
| Organize claims and revise a knowledge store | [`cascade_engine.py`](cascade_engine.py) |
| Inspect text for the Framework's constitutional cues | [`aura_checker.py`](aura_checker.py), backed by [`semantic_extractor.py`](semantic_extractor.py) |
| Parse symbolic LAMAGUE expressions | [`lamague_parser.py`](lamague_parser.py) |
| Simulate agents exchanging states and handling disagreement | [`psi_consensus.py`](psi_consensus.py) and [`grey_mode.py`](grey_mode.py) |
| Follow a state through reorganization, correction and scoring | [`sovereign_pipeline.py`](sovereign_pipeline.py) |
| Explore the memory-overload experiments | [The glass-transition research guide](../../TRUTH_PRESSURE/EXPERIMENTS/GLASS_TRANSITION/README.md) |

Most files are importable modules. Several also contain demonstrations. The
installed command-line tools provide a simpler starting point:

```bash
# From the repository root:
python3 -m pip install -e .

lycheetah-check "I may be wrong. Please verify before deciding."
lycheetah-cascade demo --domain germ
lycheetah-consensus demo
```

The text checker reports heuristic cues. The germ-theory example and consensus
demo use constructed scenarios. Their output does not establish factual truth.

## Knowledge and language

| Module | What it does | Main API |
|---|---|---|
| [`cascade_engine.py`](cascade_engine.py) | Stores claims as knowledge blocks, assigns Foundation/Theory/Edge layers, and reorganizes conflicting blocks using supplied evidence scores and paradigm labels. Includes comparison baselines. | `KnowledgeBlock`, `CascadeEngine`, `DomainExperiment` |
| [`lamague_parser.py`](lamague_parser.py) | Tokenizes symbolic expressions, builds syntax trees, reports grammar errors and compares symbolic/expanded representations. | `LAMAGUETokenizer`, `LAMAGUEParser`, `LAMAGUEValidator`, `CompressionMeasurer` |
| [`lamague_reference.py`](lamague_reference.py) | Earlier reference bundle containing symbols, a TRIAD correction kernel, a pyramid knowledge store, an energy ledger and an agent-network model. | `TRIADKernel`, `PyramidCascade`, `EnergyLedger`, `AgentNetwork` |

The reference bundle and dedicated CASCADE engine define their own
`KnowledgeBlock` types. Import the type belonging to the engine you use.
The symbolic parser is a separate language implementation from the newer
[SXP-L branch](../../03_LAMAGUE_L1/26_SXP_L_RESEARCH/README.md).

### A small CASCADE example

```python
from lycheetah.core.cascade_engine import CascadeEngine, KnowledgeBlock

engine = CascadeEngine()
block = KnowledgeBlock(
    id="example_claim",
    content="An illustrative claim with caller-supplied evidence scores",
    domain="example",
    paradigm="model_a",
    evidence_strength=0.8,
    explanatory_power=1.2,
    uncertainty=0.5,
)

event = engine.add_block(block)  # Reorganization happens here when triggered.
print(block.layer, block.truth_pressure)
print(engine.layer_distribution())
```

Those numbers are illustrative inputs. The engine does not independently
collect evidence or verify the sentence. `add_block()` returns an event when
a cascade fires, otherwise `None`.

## Text checking and configuration

| Module | What it does | Main API |
|---|---|---|
| [`semantic_extractor.py`](semantic_extractor.py) | Extracts rule-based signals and text spans so the scoring tools can inspect which language triggered a score. | `SemanticExtractor`, `Signal`, `Extraction` |
| [`aura_checker.py`](aura_checker.py) | Produces scores, evidence and concerns for the seven AURA invariants, plus a combined report. | `AURAChecker`, `AURAReport` |
| [`tri_axial_checker.py`](tri_axial_checker.py) | Computes Trust Entropy Score (TES), Value Transfer Ratio (VTR) and Purpose Alignment Index (PAI) from supplied measurements and returns threshold results. | `TriAxialChecker`, `TriAxialReport` |
| [`aura_customizer.py`](aura_customizer.py) | Builds domain-specific parameter configurations and checks them against the module's configuration constraints. | `AURACustomizer`, `AURAConfig`, `ConfigValidator` |
| [`aura_score_hexie.py`](aura_score_hexie.py) | Scores balance between complementary inputs and compares that treatment with a weighted-sum baseline. | `aura_score_hexie()`, `ComplementaryPair`, `HexieReport` |
| [`unified_field_checker.py`](unified_field_checker.py) | Extends the seven-invariant text checker with five AI-native criteria and a combined report. | `UnifiedFieldChecker`, `UnifiedReport` |
| [`sol_self_protocol.py`](sol_self_protocol.py) | Implements the historical Sol protocol's text assessments, mode/cue classification, invariant reports and session-coherence bookkeeping. | `SolSelfProtocol`, `InvariantChecker`, `SessionCoherenceTracker` |

Text scores are heuristic measurements. Emotional labels describe matched
language cues; they do not diagnose a person's mental state. The
[external-validation record](../../33_APPLICATIONS/EXTERNAL_VALIDATION_2026-08-07.md)
explains the measured limits of the public text lens.

## Agent coordination and recovery

| Module | What it does | Main API |
|---|---|---|
| [`psi_consensus.py`](psi_consensus.py) | Simulates quality-gated state sharing, gossip rounds, convergence and disagreement diagnostics across a network of agent nodes. | `AgentNode`, `PsiConsensus`, `PsiQOperator`, `ObstructionDetector` |
| [`grey_mode.py`](grey_mode.py) | Tracks drift triggers, simulated isolation states and recovery attempts for nodes. The caller must enforce any real restriction. | `GreyModeMonitor`, `build_monitor()` |
| [`seven_phase.py`](seven_phase.py) | Runs the Framework's seven-stage vector-state cycle, reporting consistency, drift, coherence and integrity along the way. | `SevenPhaseCycle`, `build_cycle()`, `CycleResult` |

These modules model coordination and recovery. Agreement between simulated
agents does not establish the truth of their shared belief.

## Iteration, transformation and tracking

| Module | What it does | Main API |
|---|---|---|
| [`triad_tracker.py`](triad_tracker.py) | Iterates a numeric state toward an anchor, records correction steps and reports convergence. | `TriadTracker`, `TriadStep` |
| [`triad_wuwei.py`](triad_wuwei.py) | Models correction cost and accumulated integrity debt according to alignment with a supplied natural direction or restoration field. | `WuweiTriad`, `grain_alignment()`, `WuweiTriadReport` |
| [`microorcim_tracker.py`](microorcim_tracker.py) | Compares intended and actual activity, computes drift/stability scores and keeps optional daily history. Also exposes stateless scoring helpers. | `MicroorcimTracker`, `compute_drift()`, `compute_sovereignty()` |
| [`chrysopoeia_engine.py`](chrysopoeia_engine.py) | Applies the seven named transformation operations to numeric states and explores iterative fixed-point/contraction models. | `TransformationState`, `Xi()`, `solve_et_coagula()` |
| [`sovereign_pipeline.py`](sovereign_pipeline.py) | Combines CASCADE, TRIAD, AURA and drift scoring. Supports a single pass or bounded regulation with an explicit corrective callback. | `SovereignPipeline.run()`, `.regulate()`, `RegulationResult` |

**Tracking writes:** `MicroorcimTracker` creates its data directory, defaulting
to `~/.microorcim`, and its recording methods persist local JSON. Supply
`data_dir` when you want a different location. History/export methods in other
modules also write files when called.

The **Sovereign Pipeline** is a processing/regulation model. The separate
**Sovereign Execution Harness**, listed below, handles action-bound permits.

## Mathematical models and reference scaffolds

| Module | What it does | Main API |
|---|---|---|
| [`harmonia_calculator.py`](harmonia_calculator.py) | Calculates frequency-ratio consonance scores and simulates coupled Kuramoto oscillators. | `HarmoniaCalculator`, `KuramotoSimulator` |
| [`earned_light_calculator.py`](earned_light_calculator.py) | Simulates work, decay, entropy and asymmetry using the Earned Light equations. Its consciousness interpretation remains unverified. | `EarnedLightCalculator`, `ConsciousnessState` |
| [`anamnesis_reference.py`](anamnesis_reference.py) | Implements specified fragments of recognition/discovery over declared structures, plus mathematical identities. Lists the missing specifications needed for a fuller engine. | `Structure`, `AgentState`, `anamnesis_recognize()`, `MISSING_SPEC` |
| [`calibrate_master_equation.py`](calibrate_master_equation.py) | Fits coupling constants to supplied observations using least squares and reports fit/prediction results. Generated example data do not constitute independent empirical calibration. | `CascadeObservation`, `MasterEquationCalibrator` |

## Context and governance models

| Module | What it does | Main API |
|---|---|---|
| [`tianxia_governance.py`](tianxia_governance.py) | Explores a multi-agent flourishing/coherence term and its behaviour in a synthetic extraction model. | `AgentState`, `FlourishingParams`, `tianxia_potential()`, `tianxia_term()` |
| [`shi_propensity.py`](shi_propensity.py) | Modifies an input score using context, intervention direction and a supplied propensity field. | `ShiContext`, `aura_shi()`, `evaluate()` |
| [`datong_gradient.py`](datong_gradient.py) | Projects state changes and trajectories onto a specified value-space direction and reports alignment. | `DatongValueState`, `datong_projection()`, `evaluate()` |

These are mathematical governance models with chosen inputs and assumptions.
Their scores do not authenticate permission or measure real communities' welfare.

## Glass-transition research

| Module | What it adds to the experiment | Main API |
|---|---|---|
| [`cascade_glass_transition.py`](cascade_glass_transition.py) | Fixed-service comparison of CASCADE and FIFO under synthetic arrivals, contradictions and processing limits. | `simulate()`, `run_sweep()` |
| [`cascade_glass_dynamic.py`](cascade_glass_dynamic.py) | Work-aware service planning, frozen service snapshots and delayed commits. | `plan_service()`, `commit_service()`, `simulate_dynamic()` |
| [`topological_cascade_glass.py`](topological_cascade_glass.py) | Dependency propagation, topology-aware work and policy comparisons. | `TopologicalCascadeEngine`, `simulate_v2()` |
| [`sheaf_cohomology_factorial.py`](sheaf_cohomology_factorial.py) | Numerical cellular-sheaf operators/certificates and a three-factor experiment separating intervention effects. | `CellularSheaf`, `simulate_orthogonal()`, `compute_yates_factorial_effects()` |

Start with the [experiment protocol, recorded runs and limitations](../../TRUTH_PRESSURE/EXPERIMENTS/GLASS_TRANSITION/README.md).
These modules include sweep runners; running them can generate substantial
research output. The finite experiments do not establish a universal glass law
or a production memory-ingestion governor.

## Where the runtime tools live

| Job | Implementation / guide | Installed command |
|---|---|---|
| Policy checks, action gateway and signed checkpoints | [Assurance Runtime](../../34_ASSURANCE_RUNTIME/README.md) | `lycheetah-guard`, `lycheetah-assure` |
| Preserve protected fields while compacting structured context | [Compaction example](../../examples/compaction_shield_demo.py) | `lycheetah-compact` |
| Use the consensus/recovery wrapper | [Consensus arena](../../lycheetah/consensus/arena.py) | `lycheetah-consensus` |
| Bind an action to a scope, state version, expiry and single-use permit | [Sovereign Execution Harness](../../lycheetah/sovereign_harness.py) | `lycheetah-sovereign` |
| Compare a task declaration with a receiving agent's report | [Handoff module](../../lycheetah/handoff.py) | `lycheetah-handoff` |

[`__init__.py`](__init__.py) makes this directory installable as
`lycheetah.core` and deliberately imports no engines automatically.

[Implementation overview](../README.md) · [Framework quick start](../../QUICKSTART.md)
