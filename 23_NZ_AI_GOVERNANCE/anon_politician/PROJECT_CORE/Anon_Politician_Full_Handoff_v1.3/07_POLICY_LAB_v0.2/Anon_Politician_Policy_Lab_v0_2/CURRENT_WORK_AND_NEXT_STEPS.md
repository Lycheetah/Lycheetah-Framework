# Anon Politician — Current Work and Next Steps

**Current as of 16 October 2026, Pacific/Auckland**

## Project direction

Anon Politician is an AI-assisted democratic policy intelligence concept for Aotearoa New Zealand. It is not an AI government. It aims to connect citizens and elected representatives through recurring public input, evidence, reciprocal political challenge, future-scenario analysis, CASCADE-style institutional memory, and transparent decision tracing.

The user's core incentive hypothesis is that leaders may gain a competitive advantage by listening to public priorities, explaining evidence and trade-offs, improving proposals and showing what happened after implementation. This is a hypothesis to test, not a guaranteed consequence.

## What was already built in v0.1

An offline-first browser Policy Lab was created for the proposed development-levies policy process. It contains case/evidence, citizen signal, adversarial review, scenarios, decision trace and export sections. It is a workflow shell, not connected AI, a live public survey, or a forecasting model. The original 11 unit tests passed. These tests establish code behaviour only.

## What is new in v0.2

The next increment is an **evaluation harness**, intended to test whether the elaborate workflow adds value over simpler analysis rather than presuming it does.

It defines three comparison arms: (A) ordinary policy analysis, (B) a structured evidence ledger, and (C) the full Anon Politician workflow. It includes controlled prompt templates, a blinded-review pack generator, a private mapping key, an offline HTML reviewer, and an aggregation script that reports dimension profiles without a composite score or an overall winner.

The reviewer evaluates source fidelity, claim traceability, uncertainty, adversarial fairness, distributional coverage, scenario reasoning, public-input interpretation, non-erasure/value pluralism, and actionability/accountability. Critical errors are flagged separately and cannot be averaged away.

**No comparative outputs have yet been run. No quality improvement has yet been demonstrated.** This package prepares a repeatable experiment; it does not fake results.

## New source-grounding refinement

The official MCERT development-levies page reports 56 submissions to the 2025–26 consultation from councils, developers, industry groups, Māori housing organisations and individuals. It reports councils strongly supported replacement, while developer views were mixed, including both support for consistency/transparency and concerns about over-charging. Four strong feedback themes were levy-area definitions, calculation detail, recovery horizons beyond 10-year plans, and transition design.

These submissions are not a representative sample of New Zealanders. This is a particularly useful stress test for the project: it must preserve consultation feedback without mislabelling it national consensus. Official source: https://www.mcert.govt.nz/our-work/local-government/local-government-policy/development-levies/

The Treasury's Living Standards Framework and CBAx are established baselines to reuse and compare against. Anon Politician's possible contribution is the integrated continuity loop—recurring input, symmetric challenge, dependency review, transparent disposition and later outcome feedback—not a claim to have invented cost-benefit analysis or wellbeing analysis.

## Immediate operating sequence

1. Read `evaluation/benchmark_protocol.md` and `evaluation/model_prompts.md`.
2. Freeze the current case packet and source files; record SHA-256 hashes.
3. Generate outputs for all three arms from the same exact factual source set. Record exact prompts, model/version, tool access, time and cost.
4. Paste outputs into `evaluation/raw_outputs_template.json` and run `prepare_blind_pack.py`.
5. Have at least two independent reviewers assess the anonymous candidates using `evaluation/reviewer.html`, without the private method key.
6. Lock the reviews; then run `aggregate_reviews.py` with the key. Report criterion profiles, evidence notes, critical flags, reviewer disagreement, time and cost. Do not compute a single winner.
7. Repeat with more than one case and rotate which perspective supplies the proposal or challenge before making broad claims.

## Useful commands

From this directory:

```bash
python -m unittest discover -s tests -v
python evaluation/prepare_blind_pack.py evaluation/raw_outputs_template.json --out-dir evaluation/blind_output
python evaluation/aggregate_reviews.py path/to/review_jsons --key path/to/PRIVATE_method_mapping_key.json --out evaluation/review_aggregate.json
```

The template will intentionally fail blind-pack preparation until the placeholder texts are replaced with real outputs.

## Non-negotiable controls

- No AI is the accountable decision-maker.
- Voluntary public input is not called representative without a documented sampling/inference method.
- No political policy or party is automatically ranked or endorsed.
- Claims, sources, assumptions, value judgments and preferences remain distinct.
- Changed foundations queue affected claims for human review; they do not automatically delete them.
- Keep minority concerns and unresolved contradictions visible.
- Don't infer a policy's impact from a government's intended outcome.
- Don't present unit tests, synthetic tests or agreement between models as external validation.
- Protect participant privacy; do not collect identifiable data before a lawful, secure governance plan exists.

## Current limitation

The local browser page and Python primitives are available, and the prior v0.1 tests pass. This environment did not complete a true interactive browser smoke test. The evaluator code must be manually tested by loading a real blind pack, entering dummy ratings, exporting a review JSON, and running aggregation before any real review.
