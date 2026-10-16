# Anon Politician — Current Work and Next Steps

**Current as of 16 October 2026, Pacific/Auckland**

## The founder's full concept in operational form

Anon Politician is intended as AI-assisted democratic policy intelligence for Aotearoa New Zealand. It is not an AI government. The central aim is to make it easier for citizens and elected representatives to create, critique and improve policies together, with evidence and future consequences visible and decisions remaining human-accountable.

The distinctive loop is:

1. **Politicians ask:** representatives can publish policy questions and request feedback on issues they are considering, with scope and decision authority stated clearly.
2. **Citizens respond repeatedly:** the founder envisions a recurring monthly public-input mechanism, including questions selected by politicians. It should capture priorities, reasoning, lived effects, alternatives and what evidence could change views.
3. **CASCADE preserves institutional memory:** policy claims, assumptions, sources and dependencies are versioned. A changed premise triggers a review queue for dependent claims; it never silently deletes a claim or resolves a contradiction.
4. **Competing perspectives challenge proposals:** the founder envisions adversarial AI supplied or trained by the opposing party. Implementation should preserve that idea while preventing any party's model from becoming the exclusive arbiter. Use symmetrical cross-party roles, independent red-team scrutiny and affected-community input on a shared evidence pack.
5. **Forecasting explores possible futures:** compare the status quo and clearly specified scenarios with data, assumptions, uncertainty, sensitivity and distributional analysis. After implementation, forecasts should be compared to measured outcomes.
6. **Leaders answer publicly:** publish what public input was heard, what changed, what did not change and why, what remains unknown, who is responsible and when outcomes will be reviewed.
7. **Leadership incentives may change:** test the hypothesis that transparent responsiveness and demonstrated delivery become useful competitive advantages for politicians. Do not assume the incentive effect; measure it.

The point is not to eliminate political disagreement. It is to make disagreement more informative and stop political origin from being treated as a reason to discard a potentially useful idea.

## What was added in this continuation

A local, offline-first Policy Lab prototype now structures one real policy workflow: the government's proposed development-levy system in the Going for Housing Growth programme. The Ministry says the relevant bill is being prepared for introduction in the first quarter of 2027 and that further input on calculation methodologies and disclosure, plus select-committee scrutiny, are expected. This gives the research a genuine upcoming procedural setting.

The prototype has six sections: case/evidence, citizen signal, adversarial review, scenarios, decision trace, and export. It allows manually recording proposal reasoning, cross-party critique, independent red-team critique, affected-group observations, public-input method, scenario assumptions, policy changes, and actual outcomes. It exports a Markdown report or JSON record locally in the browser.

It is not connected to any model, live public survey, government system, or forecasting engine. No public data or policy outcomes are invented or preloaded. Primary-source anchors are included in the interface and case brief.

## Verification status

- 11 Python unit tests pass.
- Static HTML structure and navigation references pass checks.
- JavaScript syntax passes Node.js `--check`.
- Browser-interaction smoke test was attempted but blocked by environment browser policy; manually test in an ordinary browser before relying on the UI.
- These are implementation tests only. No claim of better policy analysis, representative participation, model neutrality, prediction quality or real-world efficacy has been established.

## Recommended next three moves

### Move 1 — Try the prototype locally

Open `02_POLICY_LAB/Anon_Politician_Policy_Lab_v0_1/app/index.html`. Navigate through each section, test the draft public question, enter clearly-labelled synthetic text only for testing, export both Markdown and JSON, and check the files. Don't enter real participant information yet.

### Move 2 — Build the real source packet

Collect and version the official bill/exposure draft and supporting technical material when published, previous consultation material and submissions that may lawfully be accessed, cost methodology, datasets, official impact analysis and select-committee records. Distinguish what is enacted today from proposed changes. Verify any legal/privacy implications before processing public submissions.

### Move 3 — Run a blind comparison

Freeze one source set and compare ordinary analysis, a simple evidence ledger, and the Policy Lab workflow. Use a preregistered rubric covering source fidelity, uncertainty, counterargument quality, preservation of minority concerns, downstream dependency tracking, comprehension, time and cost. Rotate which political perspective proposes the policy. Report errors and limitations honestly.

## Important outstanding questions

- Who would own, host, audit and fund the system, and how would independence be protected?
- Which citizen participation design can combine accessibility, meaningful participation and valid population inference without pretending an opt-in poll is representative?
- How should monthly public signals relate to elections, formal consultation, Te Tiriti obligations, rights and statutory decision processes?
- How can party-contributed adversarial models be transparent and symmetric, without allowing party control over source selection or final interpretation?
- Which policy outcome metrics are meaningful without reducing wellbeing or rights to one number?
- Which claim types and CASCADE dependencies require human review, and how do we measure missed or unnecessary review triggers?
- How can outcomes be attributed to a policy in a real world with many simultaneous changes?

## Non-negotiable research discipline

Never present a founder-generated construct, LLM agreement, unit test, synthetic benchmark, public poll or forecast as proof beyond what its method supports. Preserve original claims and source fidelity; separate descriptive facts, uncertainty, normative values, preferences and decisions. The founder's assumptions must be tested as rigorously as those of political institutions. AI assists; accountable people and institutions decide.
