# Anon Politician Policy Lab v0.2

**Purpose:** A local policy-workflow demonstrator plus a pre-registered draft for evaluating whether its structured workflow adds value.  
**Pilot:** New Zealand's proposed development-levies system for housing-growth infrastructure.  
**Cut-off:** 16 October 2026 (Pacific/Auckland).

## What changed from v0.1

- Tightened source grounding using the Ministry for Cities, Environment, Regions and Transport's development-levies page and technical Q&A.
- Recorded the Ministry's description of 56 consultation submissions and explicitly separated that from nationally representative public opinion.
- Added an evaluation harness comparing ordinary analysis, a structured evidence ledger, and the full Anon Politician workflow.
- Added a random blind-pack preparation script, separate private method mapping key, standalone offline HTML reviewer, and aggregation script that never produces a composite score or overall winner.
- Added controlled prompts, a reviewer manual, a run-log template, a source-baseline/novelty memo, and updated next-step instructions.

## Run the local Policy Lab

1. Open `app/index.html` in a current browser. No installation, account, API key or server is needed.
2. The app is offline-first. Cited links need internet access. It does not transmit entered text to a server.
3. Use synthetic text for UI testing. Do not enter participant personal information before a privacy, security and governance plan exists.

## Run tests

From this directory:

```bash
python -m unittest discover -s tests -v
```

Tests verify specified code behaviour only. They do not prove policy accuracy, neutrality, representativeness, or real-world effectiveness.

## Run the evaluation harness

1. Read `evaluation/benchmark_protocol.md` before generating outputs.
2. Use `evaluation/model_prompts.md` to produce one frozen output for each of three arms: ordinary analysis, structured ledger, and Anon Politician workflow. Use the same source pack and question. Record model/version, prompts, tool access, time, cost and hashes.
3. Fill the method outputs in a copy of `evaluation/raw_outputs_template.json`. Replace all placeholders.
4. Generate blind labels:

```bash
python evaluation/prepare_blind_pack.py evaluation/raw_outputs_filled.json --out-dir evaluation/blind_output
```

This creates `blind_review_pack.json` and `PRIVATE_method_mapping_key.json`. Keep the key secret until ratings are locked. Inspect key leakage warnings before distributing the pack.

5. Give reviewers `evaluation/reviewer.html` and the blind pack only. Each reviewer loads the JSON locally, assesses A/B/C, and exports one review JSON. Do not give reviewers the mapping key.
6. After reviews are locked, aggregate them:

```bash
python evaluation/aggregate_reviews.py evaluation/reviews --key evaluation/blind_output/PRIVATE_method_mapping_key.json --out evaluation/review_aggregate.json
```

Keep the private key out of the reviewers' folder and any public release until blinding closes. The aggregator reports per-dimension medians/ranges and critical issues. It does not sum dimensions, rank the methods or declare a winner.

**The template is deliberately incomplete.** The blind-pack script must fail until each method has actual output text. No comparative analysis has been run by this package.

## Files

- `app/index.html` — offline Policy Lab UI.
- `src/policy_lab.py` — evidence/claim validation and dependency-review primitives.
- `tests/` — unit tests.
- `case_study/` — neutral policy brief, source register and machine-readable packet.
- `docs/` — architecture, safeguards, monthly citizen signal protocol, evaluation plan and source baseline.
- `evaluation/benchmark_protocol.md` — preregistration draft and fair comparison protocol.
- `evaluation/model_prompts.md` — prompts for the three arms.
- `evaluation/raw_outputs_template.json` — output capture template and reference context.
- `evaluation/prepare_blind_pack.py` — anonymous candidate IDs and separate mapping key.
- `evaluation/reviewer.html` — offline blind review interface.
- `evaluation/aggregate_reviews.py` — dimension-profile aggregation without overall winner.
- `evaluation/test_evaluation.py` — evaluation-harness tests.
- `evaluation/review_manual.md` — instructions for reviewers.
- `evaluation/run_log_template.csv` — capture prompt/model/runtime details.
- `CURRENT_WORK_AND_NEXT_STEPS.md` — handoff to the next model/researcher.

## Non-negotiable rule

**AI helps people and public institutions reason; accountable humans make decisions.** Public input is not automatically representative, forecasts are not facts, and opposing models are reviewers rather than arbiters. Preserve contradictions and dissent. Keep the founder's ideas open to the same level of scrutiny as government or party claims.
