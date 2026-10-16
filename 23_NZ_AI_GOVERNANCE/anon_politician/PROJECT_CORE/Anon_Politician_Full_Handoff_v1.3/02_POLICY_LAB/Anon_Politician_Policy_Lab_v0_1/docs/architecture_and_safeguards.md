# Architecture and Safeguards — Policy Lab v0.1

## Purpose

Demonstrate an auditable flow from public input to policy analysis without handing policy authority to AI. The product should help elected representatives and the public understand what was proposed, what people expressed, what evidence supports or contests it, how options may behave under different assumptions, what changed after scrutiny, and who remains accountable.

## Proposed flow

1. **Policy question registry** — stable ID, scope, status, accountable institution, legal basis, version history, affected jurisdictions, dates, and deadlines.
2. **Evidence ledger** — source-linked statements with type, date, confidence rationale, limitations, affected population, method and version. Separate direct source facts from analysis and opinion.
3. **CASCADE dependency graph** — record which claims depend on which assumptions. When a parent claim changes, add downstream claims to a human review queue. Do not automatically delete, promote, demote, or resolve them.
4. **Citizen signal layer** — separate preference, reasoning, lived experience and proposals. Capture recruitment method, sample size, question wording, dates, non-response, weighting, accessibility, and privacy limitations.
5. **Multi-perspective review** — the proposer, an opposing policy lens, an independent red team, and relevant public/affected-group reviewers all critique the same evidence packet. Store outputs with model/version/prompt metadata.
6. **Scenario workbench** — compare a baseline with explicitly specified options; show assumptions, datasets, uncertainty, subgroup effects, sensitivity and failure conditions side by side.
7. **Human decision record** — record what the accountable institution decided, why, what it accepted/rejected, whether the proposal changed, which trade-offs remain, and where the public can challenge or appeal the process.
8. **Outcome review** — compare implementation and observed outcomes with pre-registered objectives and forecasts; update dependency review when evidence shifts.

## The role of party-supplied adversarial models

The founder's vision includes the opposing party providing or training the adversarial model. Preserve this as a core design hypothesis, but do not make one party's model the exclusive challenger or truth arbiter. Potential controlled implementation:

- Each party may submit a disclosed policy critique, prompt, perspective specification or model proposal.
- Both sides receive the same source pack and factual correction rules.
- Outputs are labelled by perspective and model/version; no model is allowed to use hidden evidence unavailable to other reviewers.
- An independent red team and lived-experience review remain separate from party models.
- Evaluation cases rotate which perspective proposes and which challenges, to detect asymmetric scrutiny.
- Measure factual fidelity, evidence use, counterargument quality and correction behaviour; do not judge fairness by whether outputs are politically similar.
- Disclose relevant funding, training data limitations and known model failure modes to the degree feasible.
- No proprietary model should receive a privileged veto over a policy.

## Core data distinctions

Use explicit labels:

- **Fact:** a source supports a narrowly stated descriptive claim.
- **Forecast:** a conditional projection made by a specified model or method.
- **Assumption:** a premise used for analysis but not established.
- **Public preference:** what participants say they want or prioritise under a defined method.
- **Lived experience:** a person's/collective's reported experience, which is informative but not automatically population-representative.
- **Value judgment:** a normative claim about what matters or how trade-offs should be resolved.
- **Decision:** a human institution's accountable choice.
- **Unknown/contested:** do not force a status just to create apparent closure.

Do not collapse these categories into a single “truth score”, alignment score or public-consensus score. When metrics are introduced, publish construct definitions, formulas, uncertainty, weights and validation evidence, including foreseeable gaming strategies.

## Required safeguards

### Democratic legitimacy
- AI remains advisory unless a law explicitly provides otherwise.
- Polls and models do not replace elections, parliamentary procedure, courts, statutory consultation, Te Tiriti obligations or other lawful processes.
- Public feedback informs; it does not automatically override rights, constitutional duties or well-supported evidence.
- Decision-makers must be free to disagree with public opinion, but should disclose reasons and trade-offs.

### Representativeness and anti-manipulation
- Open voluntary polls must not be described as representative of the population without a justified sampling/adjustment method.
- A monthly open portal should be supplemented, where feasible, with a carefully designed probability or stratified panel and accessible offline participation.
- Detect duplicate or coordinated participation proportionately; do not use opaque automated fraud rules to silence people.
- Publish wording, sample and response counts, dates, recruitment channels, weighting, exclusions, non-response and uncertainty.
- Report minorities and high-impact views even when they are numerically small.

### Privacy and safety
- Collect the minimum personal data needed. Separate identity verification from opinion records, and set retention/deletion schedules.
- Explain before submission whether responses may become public. Parliament's formal submission channels can publish records; a separate product should not promise confidentiality it cannot guarantee.
- Do not expose sensitive or personally identifying participant information in public model prompts or generated reports.
- Provide accessibility and language support, including appropriate Māori-language and culturally grounded engagement.
- Obtain specific legal, privacy, security and Māori governance advice before deployment.

### Evidence and model behaviour
- Every material empirical statement should have a source or explicit label as unverified.
- Distinguish the government's stated rationale from independent evaluation.
- AI-generated citations and summaries must be checked against source documents.
- Models must be allowed to return “insufficient evidence” and name what information would resolve the gap.
- Record counterevidence and preserve version history.
- No model-generated policy output becomes a decision by default.

### Accountability and contestability
- Named role/institution for each decision, with date and public rationale.
- Clear way for the public, experts and affected communities to correct factual errors and challenge omitted evidence.
- Audit log of changes to claims, prompts, model versions, options and public reports.
- Public report shows which feedback altered the proposal, which did not, and why.
- Outcomes and forecasts are reviewed after implementation, not merely at announcement.

## Failure modes to test early

- Majority-rule flattening: high-volume preference overrides serious minority harm.
- Poll capture by organised campaigns or low-cost bot participation.
- Model monoculture: several LLMs repeat similar training priors and appear to agree independently.
- False balance: treating unsupported claims as equal to well-evidenced ones merely for symmetry.
- Partisan asymmetric burden: one policy perspective receives more scrutiny or more favourable framing.
- Goodhart's law: politicians optimise the displayed metric rather than public outcomes.
- Source laundering: model paraphrase creates an apparent citation trail where the source does not support the claim.
- Forecast overconfidence and model drift.
- Participation fatigue and survey overload.
- Institutional bypass: a parallel AI process appears democratic but doesn't influence formal decisions.
- Privacy breach or chilling effect.
- CASCADE overreach: upstream change incorrectly triggers unrelated reviews, or a real dependency is missed.

## Minimum viable architecture

For a first test, use static browser UI + JSON/Markdown export + a small dependency-review module. Do not connect a live LLM, collect real opinions or publish outputs yet. The next version can add a transparent import/export schema and manually run model roles with fixed prompts. Live API integration should come only after evidence, security and privacy requirements are defined.
