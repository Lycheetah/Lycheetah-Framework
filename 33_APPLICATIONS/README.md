# Capabilities, evidence and the next useful test

**Updated:** 19 October 2026. **Creator:** Mackenzie Conor James Clark / Lycheetah Framework.

Lycheetah now contains usable instruments, executable research, policy proposals
and creative work. They have different maturity and evidence. This guide answers
what to try, what its output means, and which claims still need outside testing.
The [current synthesis](../13_SYNTHESIS_REPORTS/CURRENT_FRAMEWORK_SYNTHESIS.md)
explains how the work connects; the [map](../00_Sovereign_Index.md) locates it.

## Start with a concrete task

| Task | Instrument / source | What it can establish | What remains to test |
|---|---|---|---|
| Carry goals, unknowns and permission between AI sessions | [Handover preview and comparison](../examples/meaning_handover/README.md) | Inspectable declared records, exact codec comparisons, explicit changes and downloadable handovers. | Independent use, comprehension and return-to-task benefit against an ordinary handover. |
| Preserve a restricted accountability record under compression | [LAMAGUE language/compression guide](../03_LAMAGUE_L1/README.md), [compaction package](../lycheetah/compaction/) | Exact preservation under the declared record/schema and measured byte budget. | General semantics and human usefulness. Compressed JSON is smaller on the current handover example. |
| Explain a bounded policy decision | [Assurance Runtime](../34_ASSURANCE_RUNTIME/README.md), [package](../lycheetah/README.md) | Policy/evidence version, allowed scope, uncertainty, receipts and restricted guard/finality behaviour. | Validity of inputs, correctness of the policy for its setting and external effects. A receipt is not proof of an event. |
| Exercise permission, revocation, recovery or stopping | [Agent-safety packet](../papers/agent-safety/README.md) | Behaviour on the packet's authored cases, counterexamples and conventional baselines. | Adversarial real integrations, independent reproduction and practical advantage beyond the baseline. |
| Revise represented knowledge as evidence changes | [Hybrid Gateway](../papers/ai-futures/hybrid-gateway/README.md), [CASCADE](../01_CASCADE_L4/README.md) | Declared revision mechanisms and bounded model results. | External truth, operational input quality and generalisation. Temporal SQL baselines tie in the Gateway research. |
| Make research claims auditable | [Claims/evidence guide](../28_DEFENSE/README.md), [claim register](../28_DEFENSE/CLAIMS.json) | Traceable status, evidence paths, falsifiers and retained retractions; automated count consistency. | Scientific validity and independent evaluation of each claim. |
| Read the work without installing software | [Public reader](https://lycheetah-earned-light.banduabusiness.chatgpt.site), [story collection](../LYCHEETAH_MYTHOS/SCRIPTURES_AND_STORIES/README.md) | Complete stories, research introductions and downloadable source bundles. | Reader experience and public reach; publication itself is not research validation. |

The [examples guide](../examples/README.md) and [implementation guide](../12_IMPLEMENTATIONS/README.md)
route runnable examples. Source package version 1.3.0 does not version every
paper, language release or story. A configured integration is not a deployment
receipt, and an implemented mechanism is not evidence that someone benefits.

## Text scoring: the corrected evidence

The August evaluations remain important because they challenged the project's
own front-door lens. Their numbers describe dated runs, not current whole-repo
coverage. Externally authored data is distinct from an independently executed
study: these are project-run analyses of published datasets.

| Evaluation | Dated result | Supported reading |
|---|---|---|
| Author-written discrimination corpus | The repair reported held-out ROC-AUC 0.940, after an earlier 0.274 inversion. | A useful regression/diagnostic corpus; the held-out examples still came from the project. |
| Anthropic hh-rlhf harmless-base | 2,308 pairs scored; 741 correct of 1,335 non-tied pairs, 55.5%; reported p = 5.7e-05. | A small above-chance effect on decided pairs, with 42.2% ties and cues on about 2% of replies. |
| Anthropic evals social-engineering statements | 1,000 statements; ROC-AUC 0.516, reported p = 0.383. | No statistically distinguishable effect in that run. |
| Cues derived from hh-rlhf labels | Reported 60.6% against the report's estimated 64.9% ceiling. | A separate empirical cue instrument, not retrospective validation of every original construct. |
| Frozen-cue transfer within Anthropic datasets | Five of six derived families transferred to the reported red-team sample; the helpfulness comparison exposed a harmlessness/helpfulness tension. | Transfer across label types is narrower than transfer across independent publishers or domains. |
| Google Jigsaw Unhealthy Comments Corpus | On the 12,000-comment evaluation sample, the handwritten lens tracked 0/6 attributes at p < 0.05; derived families tracked 2/6, AUC at most 0.553. | Generalisation to human comments was not established. The full source corpus contains 48,909 comments; not all were scored in this evaluation. |

Sources: [discrimination audit](DISCRIMINATION_AUDIT_2026-08-07.md),
[external evaluation and same-day correction](EXTERNAL_VALIDATION_2026-08-07.md),
[derived cues](DERIVED_CUES_2026-08-07.md), [transfer test](TRANSFER_TEST_2026-08-07.md),
[independent-publisher boundary](INDEPENDENT_PUBLISHER_2026-08-07.md).

The earlier summary “at chance on both datasets” was false for hh-rlhf. The
corrected results still do not establish a general detector of manipulation,
constitutional alignment or unsafe action. Sparse coverage, domain dependence
and clinical/financial overreach gaps matter even when a small effect is real.
The source reports preserve the original failed predictions and corrections.

## Research and proposals that need further evidence

- **Multi-agent agreement and recovery:** consensus, Psi and Grey Mode implement
  bounded mechanisms. Agreement or recovery in a constructed scenario does not
  establish correctness under an adversarial deployment.
- **CASCADE predictive criterion:** the dated F1 result missed its stated target.
  The [test](../tests/test_cascade_predictability.py) now records that with strict
  expected-failure handling. The prediction remains unsuccessful.
- **Empirical programme:** [31_EMPIRICAL](../31_EMPIRICAL/README.md) contains seven
  design/preregistration documents. They are not seven completed studies.
- **Consciousness and transformation:** the older Earned Light thermodynamic
  model, Harmonia interpretations and human transformation claims require their
  own evidence. New control-forge tests do not validate those theories.
- **NZ governance:** the current [six-rights proposal](../23_NZ_AI_GOVERNANCE/README.md)
  is a policy proposal. Earlier WOF, healthcare and cultural-governance designs
  are not adopted standards, certification services or deployment receipts.
- **School, fiction and generative work:** these have literary, design or learning
  value without becoming scientific evidence or shipped app features by inclusion
  in this repository.

## Reproduce the claim you are assessing

From the repository root, use the declared dependencies and component instructions:

```sh
python3 tools/verify-claims.py --register
python3 -m pytest -q tests/test_claims_register.py
python3 examples/meaning_handover/demo.py --help
python3 33_APPLICATIONS/external_validation.py
```

The dataset evaluator needs outbound HTTPS on a first run and checks recorded
SHA256 digests. A failed download is a run that did not complete, not a negative
scientific result or a pass. The [test guide](../tests/README.md) distinguishes
ordinary collection from packet-specific replay. Keep the exact source, inputs,
command and count with a result; no historical global total is promised here.

The [April cold-room report](../28_DEFENSE/COLD_ROOM_VERIFICATION.md) explicitly
uses an internally simulated reviewer perspective. It is not a third-party
replication. The [October intake reviews](../28_DEFENSE/README.md) distinguish
source preservation, local execution, conventional ties and unresolved controls.

## The next useful step

Choose one instrument and one real task. Agree on a strong conventional baseline,
a measurable outcome, a permission boundary and a failure condition before the
trial. Publish the comparison, including neutral or worse results. The handover
preview already carries a proposed trial and tester card; outside use and benefit
remain unmeasured. More files or a more coherent synthesis cannot substitute for
that observation.

The [previous capability README](https://github.com/Lycheetah/Lycheetah-Framework/blob/ea28fe3/33_APPLICATIONS/README.md)
remains in Git history. Its August tier assignments and mixed-generation counts
are historical reasoning, superseded by this current routing guide and the
underlying dated evidence.
