# Civic Signal Protocol v0.3 — Voice, Inference and Deliberation

## 1. Purpose

Anon Politician proposes a recurring public channel in which people can raise priorities, consider policy trade-offs and see how their input was treated. This protocol separates three different things that are commonly blurred:

- **Voice:** what people who participate say, why they say it, and what impacts or ideas they report.
- **Population inference:** what a defined wider population is likely to think, with stated uncertainty, when an appropriate sampling and analysis design supports that inference.
- **Deliberative judgement:** what a group of selected citizens concludes after receiving balanced evidence, questioning sources and discussing trade-offs.

None is a substitute for the others. None by itself determines what a law should be. A democratic decision may also involve rights, Te Tiriti obligations, legality, fiscal limits, expert evidence, implementation realities and accountable elected judgement.

## 2. The key distinction: public voice is not automatically public consensus

The OECD's citizen-participation guidance distinguishes open opt-in surveys from opinion polls designed around random samples, noting that open surveys are often not representative. Its guidance on representative deliberative processes emphasises transparent design, participant selection, inclusiveness, access to information, privacy and public reporting of the decision-maker's response. (See `SOURCE_REGISTER.csv`.)

Use these default labels:

| Channel | What it can support | What it cannot claim by default |
|---|---|---|
| Open opt-in pulse | Participant priorities, issue discovery, lived-experience examples, arguments and proposals | "New Zealand thinks...", population prevalence, national consensus, representative mandate |
| Probability sample survey | Estimates about a defined population if sample frame, selection, response, weighting, wording and uncertainty are methodologically defensible | Perfect representativeness, certainty, informed deliberation from a simple opinion question |
| Stratified/civic-lottery deliberative panel | Reasoned recommendations and trade-off judgements of the selected panel after specified evidence/discussion | A poll estimate of the entire population; unanimous national agreement |
| Targeted consultation or stakeholder submissions | Evidence and positions of the invited/responding stakeholders; issue-specific expertise or affected perspectives | The balance of all public opinion or proof that a stakeholder position is empirically correct |
| Formal statutory consultation | The formal submissions and other participation collected under the relevant process and rules | A replacement for elections, statutory decision criteria or a representative poll |

A large sample does not fix a biased recruitment process automatically. Weighting can help with some known differences but does not prove that unmeasured differences have been corrected. Always describe the estimand (whose views are being estimated), the recruitment method and the limitations.

## 3. Monthly cycle

Monthly is a proposed cadence for visibility and accountability, not a requirement that every policy issue be put to a rapid vote. The public interface should label each cycle as exploratory, population-estimation, deliberative, formal consultation, or a combination with separate reporting.

### Step A — Establish decision context

Before asking for feedback, publish:

- the specific problem or decision stage;
- the legal/institutional decision owner;
- what is open for influence and what is already fixed;
- why input is requested now and when the decision is expected;
- the source packet and its date;
- the participation method, privacy terms, accessibility routes and deadline;
- the commitment for when/how the decision owner will respond.

Invite people to suggest future questions and publish the criteria used to select them. State who funds and administers the process.

### Step B — Use the right channel for the question

Use an open pulse for broad issue discovery and easy access. Use a probability sample when a defensible population estimate is needed. Use a deliberative panel when the question requires people to understand evidence and grapple with conflicts between legitimate priorities. Add targeted engagement where particular communities are affected or the default channel is likely to miss them.

Report results separately by method. Do not average or merge channels into one headline number unless the target quantity, weighting logic and analysis plan are defensible and published in advance.

### Step C — Ask questions that reveal reasons and trade-offs

Where appropriate, preserve both pre-information and post-information responses:

1. Initial priority, preference or concern.
2. Reasons, context and who is affected.
3. Balanced, sourced information on the proposal, plausible alternatives and the status quo.
4. Explicit trade-offs, uncertain effects and who may bear costs.
5. Reconsidered preference, including "still unsure" and "none of these".
6. Remaining questions, alternative proposals and possible harms.

Do not frame changing one's mind as failure. Do not show only post-information results if initial responses are important to understanding the process. Pre-test question order, readability and framing.

### Step D — Treat data as data, not as a verdict

The system should display:

- exact question wording and when it was asked;
- method, target population, recruitment and eligibility;
- number invited, started, completed and excluded, where available;
- response rate and nonresponse limitations where measurable;
- participation by relevant demographic, geographic and accessibility dimensions, with small-cell privacy protection;
- weighting and uncertainty method, when appropriate;
- themes and quotations only under an approved privacy/consent policy;
- minority views and high-severity concerns, not just the majority response;
- the difference between stated preferences, factual beliefs and expert claims;
- what the findings do not establish.

For open responses, summaries generated by AI must retain links to source response IDs where lawful, preserve contradictory themes and allow human correction/appeal. Never treat the model's summary as a substitute for the underlying responses or imply that a community has one voice.

### Step E — Feed the signal into policy analysis

Provide the same frozen evidence packet to each policy perspective. The workflow should reconstruct the proposal's rationale fairly; challenge it from competing perspectives; use independent red-team review; consider affected groups; compare scenarios where data support it; and register the assumptions that would trigger a CASCADE re-review.

Citizen inputs are evidence about people's expressed preferences and experiences, not direct proof about causal policy effects. Forecasts are hypotheses until compared with outcomes. Models should not assign a final public-interest score or decide what rights/values can be traded away.

### Step F — Publish a response ledger

The authority or representative publishes a response against each material theme:

- **Heard:** a faithful, source-linked description of the input;
- **Disposition:** accepted, partially accepted, not adopted, deferred, or outside authority;
- **Reason:** evidence, legal constraints, values/trade-offs and uncertainty;
- **Change:** what wording, funding, implementation, monitoring or policy design changed, if anything;
- **Dissent:** important minority concerns or unresolved contradictions;
- **Owner and date:** who is accountable for follow-up and by when;
- **Review trigger:** what new evidence or event would reopen the issue.

A decision owner should be allowed to disagree with public feedback, but should have to explain the choice plainly. Likewise, popularity alone should not justify violating rights or ignoring reliable evidence.

### Step G — Check outcomes later

At later milestones, publish what happened to the decision and its forecast indicators. Following implementation, compare observed outcomes with pre-registered targets and predictions. Note external events and confounders; do not claim causal attribution unless the evaluation design supports it. Keep a correction log when earlier public statements or forecasts were wrong.

## 4. Decision-influence quality measures

Track these separately at first; do not combine them into one opaque score:

- coverage/accessibility for the intended audience;
- recruitment, response and completion rates by channel;
- participant understanding before and after balanced information;
- response completion: how many material themes received a reasoned response by the promised date;
- traceability: proportion of substantive policy changes tied to evidence, public input, implementation learning or a stated value choice;
- minority concern preservation and unresolved issues visible in the published record;
- source corrections and time to correction;
- participant reports of whether they understand how input was treated;
- later policy outcomes compared with pre-stated expectations;
- cost, staff time and administrative burden.

These indicators evaluate process quality and accountability. They are not a ranking of politicians or a substitute for judgment.

## 5. Manipulation, privacy and inclusion

Before real collection, complete a privacy impact assessment, threat model, retention schedule, moderation and appeal rules, accessibility review, relevant Māori engagement/governance, security testing and legal review. Gather the least personal data possible. Separate contact/eligibility records from opinion content where possible. State whether verification is performed, what it can and cannot prove, and how duplicates or suspected automation are handled.

Anti-abuse controls should not exclude legitimate people with shared devices, unstable internet, disabilities, limited English, or limited access to official identification. Provide low-bandwidth and non-digital routes, language access, accessible formats, and support where feasible. Keep collection and governance consistent with Te Tiriti obligations and contextually appropriate relationships with Māori and iwi.

Do not publish raw submissions or free-text quotations automatically. Strip direct identifiers, review re-identification risk, respect consent and statutory consultation rules, and apply small-cell suppression where needed.

## 6. Failure conditions

Stop or relabel the output if:

- an opt-in pulse is presented as representative or as national consensus;
- the recruitment method or denominator is unknown but population conclusions are made;
- a forecast is presented as a measured result;
- the question hides the key trade-off or misstates a source;
- minority concerns are removed by automatic summarisation;
- the decision owner does not disclose what was and was not open to change;
- input is collected without adequate privacy/security governance;
- the public is told that their input influenced policy when no evidence of that influence is available.

## 7. First case: development levies

The Ministry's consultation page records 56 submissions from local authorities, developers, industry groups, Māori housing organisations and individuals. It describes strong support among local-government submitters for replacing development contributions, while developer views were mixed. This is a summary of submitted material, not a representative survey of New Zealanders. The same page reports further opportunities for input through select committee and later methodology/disclosure consultation. Verify the live official process before every use.
