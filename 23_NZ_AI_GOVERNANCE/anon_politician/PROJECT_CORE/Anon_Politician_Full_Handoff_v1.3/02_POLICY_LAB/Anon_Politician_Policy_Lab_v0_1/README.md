# Anon Politician Policy Lab v0.1

**Purpose:** Turn the Anon Politician vision into a runnable, local workflow demonstrator linking a New Zealand policy process, citizen input, multi-perspective challenge, scenarios, CASCADE-style dependency review, and human accountability.

**Pilot case:** Housing-growth infrastructure funding / proposed development levies.

## Run it

1. Extract this folder anywhere on your computer.
2. Open `app/index.html` in a recent browser. No installation, server, account, or API key is needed.
3. Navigate through the six sections. The policy case and official-source facts are prefilled; actual citizen responses, adversarial reviews, forecasts and decisions are deliberately blank.
4. Enter only evidence you have and mark uncertainty. Use the Export section to download a Markdown review report or JSON record.
5. Keep exports private until personal data, source terms, legal/privacy implications and unsupported claims have been reviewed.

The app is offline-first. Clicking cited sources requires internet access. Export downloads to your normal browser download location. The app does not transmit form data to any server.

## What this is

- A workflow shell, not a connected AI system.
- A source-aware case brief for a real, current policy process.
- A place to record public preferences separately from empirical facts and forecasts.
- A structure for proposer reasoning, cross-party critique, independent red-team analysis, lived-experience review, scenarios, and human decision tracing.
- An explicit warning against treating voluntary poll responses as representative consensus.

## What this is not

It is not a public poll, statutory consultation, representative survey, policy recommender, forecasting engine, or substitute for legal advice. It does not rank parties or policies, and it does not establish that the government's stated aims will occur. Do not enter confidential submissions or identifiable personal data into an exported dossier without a governance and privacy plan.

## Files

- `app/index.html` — the browser-based interactive prototype.
- `src/policy_lab.py` — small model-agnostic validation and dependency-review primitives.
- `tests/test_policy_lab.py` — unit tests for safety and traceability invariants.
- `case_study/case_brief.md` — researched first case, neutral framing, hypotheses and evidence gaps.
- `case_study/source_register.csv` — official source register.
- `case_study/policy_packet_template.json` — machine-readable neutral case packet.
- `docs/architecture_and_safeguards.md` — workflow architecture and failure controls.
- `docs/monthly_citizen_signal_protocol.md` — proposed monthly input mechanism, sampling, accessibility and feedback loop.
- `docs/evaluation_plan.md` — comparative test plan against ordinary analysis.
- `docs/model_work_prompts.md` — prompts for independent, fair, evidence-traceable model roles.
- `TEST_RESULTS.txt` — results from the current automated tests.

## Run the tests

From this directory:

```bash
python -m unittest discover -s tests -v
```

The tests cover code behaviour only. Passing them does not show that the system is politically neutral, that citizen input is representative, or that an AI-assisted policy analysis improves real outcomes.

## Key design rule

**AI helps people and public institutions reason; accountable humans make the decisions.** The system must not silently turn a public signal, forecast, model disagreement, or founder value into an automatic policy verdict.
