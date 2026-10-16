# Anon Politician Civic Signal Integrity Kit v0.3

**Date:** 16 October 2026 (Pacific/Auckland)  
**Purpose:** Build a trustworthy public-input layer for Anon Politician's proposed recurring policy feedback system.

## Why this increment

The founder's concept includes a regular way for citizens to tell politicians what matters to them and see how their input affects policy. The central failure risk is presenting one participation channel as "the people's consensus" when it cannot support that inference.

This kit formalises a simple principle: **different civic channels produce different kinds of evidence**. An open poll is useful for issue discovery and hearing from participants; a probability sample may support estimates for a defined population when well designed and analysed; a deliberative panel can show how a recruited group reasons after balanced information; targeted submissions describe the positions and evidence of submitters. These sources should not be collapsed into one vote count.

## Contents

- `docs/CIVIC_SIGNAL_PROTOCOL_v0.3.md` — proposed participation model, channel semantics, monthly cycle and safeguards.
- `docs/DEVELOPMENT_LEVIES_QUESTION_DESIGN.md` — neutral example questions for the New Zealand development-levies case.
- `docs/DECISION_RESPONSE_LEDGER.md` — public response and accountability format.
- `src/civic_signal_validator.py` — standard-library JSON metadata validator. It flags claims that exceed the stated methodology.
- `examples/open_pulse_descriptive_only.json` — valid example of an open voluntary pulse.
- `examples/invalid_consensus_claim.json` — deliberately invalid example; the checker should flag it.
- `examples/probability_sample_template.json` — template for describing a probability sample, not proof that a particular survey is representative.
- `tests/test_civic_signal_validator.py` — automated unit tests.
- `Civic_Signal_Integrity_Checker_v0.3.html` — standalone offline browser diagnostic.
- `SOURCE_REGISTER.csv` — relevant primary/official guidance.
- `NEXT_MODEL_HANDOFF.md` — what the next model/researcher should do.

## Run the validator

From this directory:

```bash
python src/civic_signal_validator.py examples/open_pulse_descriptive_only.json
python src/civic_signal_validator.py examples/invalid_consensus_claim.json
python -m unittest discover -s tests -v
```

The validator checks the *metadata and claims declared in the file*. It cannot independently verify that random sampling occurred, that a weighting method is valid, that the survey wording is unbiased, or that the reported inputs are true. Human and methodological review remain necessary.

## The three-channel operating model

1. **Open public voice:** low-friction, recurring, opt-in feedback to discover issues, lived impacts, reasons and proposals. Describe results as views among participants, not the population.
2. **Population measurement:** when the institution needs an estimate of what a defined population thinks, use a well-designed survey with a documented frame, probability selection where feasible, nonresponse assessment, appropriate weighting/estimation and uncertainty reporting. Do not assume weighting alone repairs selection bias.
3. **Informed deliberation:** recruit a transparent, inclusive and appropriately stratified citizen panel (e.g. a civic lottery), provide balanced evidence, allow questioning and reasoned discussion, preserve initial and post-information views, and publish participant recommendations and the decision owner's response. A panel's considered judgement is not automatically a population poll.

Formal statutory consultation and stakeholder submissions remain distinct channels. The online tool must never imply that it replaces them.

## Safety and research status

- No real public data is included; all examples are synthetic.
- No AI is the decision-maker.
- The monthly cadence is a product hypothesis, not a claim that every issue should be voted on monthly.
- Do not collect identifying participant data until legal review, privacy impact assessment, security controls, retention policy, moderation/appeals design and relevant community engagement are in place.
- Tests demonstrate code behaviour only. This is not proof of representativeness, neutrality, policy quality or public trust.
