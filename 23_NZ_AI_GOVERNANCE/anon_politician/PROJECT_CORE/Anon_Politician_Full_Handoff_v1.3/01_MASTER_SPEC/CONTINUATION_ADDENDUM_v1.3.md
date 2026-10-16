# Continuation Addendum v1.3 — Civic Signals and Democratic Feedback

Date: 16 October 2026 (Pacific/Auckland)

This addendum extends the historic master specification. It does not replace the original transcript or claim that older concepts have been validated.

## New design decision: civic input has different evidentiary types

The founder's idea includes recurring public feedback—potentially a monthly cycle—so citizens can tell political leaders what matters, engage with policy trade-offs, and see how their input affected the decision. The new Civic Signal Integrity Kit formalises three complementary channels:

1. Open public voice for issue discovery and participants' views.
2. Population measurement using a suitable sampling and analysis design when conclusions about a defined population are needed.
3. Informed deliberation by a transparently recruited, inclusive panel that receives balanced evidence and can ask questions.

Formal statutory consultations and stakeholder submissions remain separate evidence types. The channels should not be merged into a single "consensus" unless the estimand and methodology support that inference. Weighting an opt-in sample does not by itself remove self-selection or unmeasured coverage bias.

## New implementation

`08_CIVIC_SIGNAL_v0.3/Anon_Politician_Civic_Signal_Kit_v0_3/` contains a detailed protocol, neutral development-levies question set, metadata validator, offline browser checker, JSON schemas, synthetic examples, source register, tests and next-model instructions.

The public decision-response ledger traces:

- what participants raised;
- which channel supplied the signal;
- how the decision owner disposed of the issue;
- the evidence, constraints, values and uncertainty behind the explanation;
- what policy changed or did not change;
- what minority concerns remain; and
- who owes the next response and when.

This is the mechanism intended to make public input visible in the policy lifecycle. The policy owner may decline a suggestion, but should explain why. A high-volume poll does not automatically override evidence, law, rights, Te Tiriti obligations or accountable democratic judgement.

## First real policy case

Continue with development levies as a controlled initial case. The Ministry's published summary reports 56 submissions from councils, developers, industry groups, Māori housing organisations and individuals and describes different views by submitter type. This source is not a representative national survey. The Ministry page states the Bill is being prepared for introduction in Q1 2027 and identifies later select committee and methodology/disclosure input opportunities. Verify those live milestones before acting on them.

## Research claim to test

The project has not shown that a recurring citizen signal, CASCADE review, adversarial models or forecasting improves government decisions. The appropriate next steps are methodological review of the citizen signal kit, a browser interaction test, integration into Policy Lab, and a controlled comparison against simpler approaches. Preserve separate measures of source fidelity, traceability, distributional coverage, uncertainty, minority-concern preservation, user comprehension, cost and downstream outcomes. Avoid a single opaque quality score.
