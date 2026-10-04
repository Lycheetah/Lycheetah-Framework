# LYCHEETAH MODELCRAFT + RECOMMENDATIONS — MASTER DOCUMENT v0.1

**Human author / final product authority:** Mackenzie Conor James Clark  
**Architecture / research forge:** Mackenzie Conor James Clark × Vaelora · OpenAI GPT-5.6 Sol  
**Date:** 4 October 2026  
**Status:** IMPLEMENTATION-READY MASTER DOCUMENT

> **MAKE SOMETHING. LEARN WHY IT WORKED. CHANGE IT. MAKE IT YOURS. PASS IT ON.**

This document consolidates the entire Modelcraft + Recommendations v0.1 expansion into one source of truth.

---



---

# LYCHEETAH SCHOOL — MODELCRAFT + RECOMMENDATIONS v0.1
## Immediate School expansion · 4 October 2026

**Human author / final product authority:** Mackenzie Conor James Clark  
**Architecture / research forge:** Mac × Vaelora · OpenAI GPT-5.6 Sol  
**Status:** IMPLEMENTATION-READY DELTA · requires integration into current School code

This packet adds two public-facing systems:

1. **The Recommendation Hall** — a sovereign, explainable recommendation surface for
   projects, tools, lessons, free paths, workflows and community discoveries.
2. **The Modelcraft Wing** — a new School Wing dedicated to practical AI capability:
   prompting, context engineering, model routing, tool use, evaluation, agent loops,
   free/local options and reproducible "tricks."

## Public promise

> **Make something. Learn why it worked. Change it. Make it yours. Pass it on.**

## Modelcraft question

> **How much more capability can you recover from the same model by changing the way you
> frame, feed, test, route and combine the work?**

## Hard boundary

This Wing teaches legitimate usage and experimentation. It is not a jailbreak library,
a safety-bypass collection or an exploit marketplace.

A "trick" is only promoted when its effect is described honestly and can be reproduced
well enough to teach.



---

# THE RECOMMENDATION HALL
## Discovery without an engagement feed

**Status:** PROPOSED SCHOOL FEATURE

The School currently has strong depth but needs a genuinely useful public discovery layer.

The Hall answers:

> **What can I do next that would actually help me?**

It must not answer:

> **What will maximize the chance that I remain inside the app?**

---

# 1. Recommendation types

The Hall may recommend:

### MAKE
- song;
- small game;
- website;
- image project;
- tiny app;
- data analysis;
- automation;
- agent;
- first local model experiment.

### LEARN
- one School class;
- one Modelcraft technique;
- one relevant conceptual Wing;
- one tutorial needed by an unfinished build.

### USE
- free AI model/service;
- paid model/service;
- open-source/local option;
- tool/plugin/connector;
- code library;
- model protocol / MCP integration.

### CONTINUE
- unfinished learner project;
- unanswered learner question;
- existing scripture rewrite;
- experiment whose result has arrived.

### CONTRIBUTE
- reproduce a Modelcraft discovery;
- review a community recipe;
- publish a failure case;
- answer another learner's explicit request.

### BUSINESS
- automate a repetitive task;
- test a support flow;
- draft a quoting workflow;
- analyze admin burden;
- prototype a bounded customer-facing assistant;
- measure before/after.

---

# 2. Every recommendation must explain itself

Required UI:

**WHY THIS?**  
The evidence/intent/dependency that caused the recommendation.

**WHAT YOU'LL MAKE OR LEARN**  
Concrete outcome.

**COST**  
`$0`, `FREE_TIER`, estimated paid cost, or `UNKNOWN`.

**TIME SHAPE**  
Not manipulative countdowns; simply rough task scope such as 10-minute try / one sitting /
multi-session project.

**SKIP EFFECT**  
Default: **Nothing is lost.**

**SOURCE OF URGENCY**  
Default: **None.**
If genuinely time-sensitive, state the real external reason.

**EXIT / EXPORT**  
Can the learner export the result and continue elsewhere?

---

# 3. Recommendation surfaces

## Hall entrance

Default sections:

### START WITH $0
Accessible paths that require no paid model/API where reasonably possible.

### MAKE SOMETHING
Begin with artifact intent rather than coursework.

### GET MORE FROM THE MODEL YOU ALREADY HAVE
Modelcraft techniques that do not require buying another subscription.

### HELP MY BUSINESS
Plain-language task discovery.

### CONTINUE MY WORK
Only explicit unfinished learner intent.

### COMMUNITY DISCOVERIES
Reproducible, receipt-bearing techniques.

### GO DEEPER
Mystery School / philosophy / AI Future / Forge / LAMAGUE / CASCADE.

---

# 4. No opaque ranking

The ranking function may use:
- explicit learner goal;
- chosen budget;
- desired artifact;
- current tool access;
- prerequisites;
- unfinished learner work;
- relevant Modelcraft discoveries;
- source/evidence updates;
- chosen difficulty;
- time budget explicitly supplied;
- learner-selected Wings;
- explicit opt-in spaced review.

It may not optimize:
- session duration;
- DAU;
- return frequency;
- notification opening;
- arousal;
- outrage;
- FOMO;
- purchases;
- "completion percentage" pressure.

---

# 5. Tool recommendations

Do not recommend only the most expensive or fashionable model.

For a task, where possible show:

- **$0 / free route**
- **simple paid route**
- **power-user route**
- **run-it-yourself / open route**

Explain trade-offs.

Examples of useful comparison dimensions:
- capability;
- setup complexity;
- privacy;
- cost;
- speed;
- context size;
- coding/tool use;
- multimodal support;
- local/offline possibility;
- exportability.

Current prices/features are time-sensitive and must come from maintained data, not static
model memory.

---

# 6. Beginner-first recommendation law

Never require a learner to understand:
"RAG", "MCP", "tool schema", "context window", "agent harness" or "structured output"
before they can make their first useful artifact.

The Hall may reveal technical machinery progressively.

Example:

> **I want something that reads incoming quote requests and prepares a draft reply.**

First show the workflow in ordinary language.

Then optionally reveal:

`INPUT → CLASSIFY → LOOK UP → DRAFT → HUMAN APPROVAL → SEND`

Only then explain agent/tools.

---

# 7. Business Lens

Ask:

> **What eats your time every week?**

Then map:

`TASK → CURRENT COST → POSSIBLE AI ASSIST → RISK → HUMAN APPROVAL → PROTOTYPE → MEASURE`

If AI is unnecessary or creates unacceptable risk, recommend **do not automate**.

This is a feature, not a failure.

---

# 8. Recommendation receipt

Each recommendation event should optionally persist:

- recommendation ID;
- recommendation type;
- why it was surfaced;
- inputs used;
- ranking rule/version;
- cost data timestamp;
- learner action: opened / skipped / saved / dismissed;
- explicit feedback;
- no hidden "resistance score" for skipping.

The learner should be able to inspect:
> Why was this shown to me?

---

# 9. Success metrics

Prefer:
- artifact completed;
- capability reused outside School;
- learner found cheaper route;
- learner successfully rejected bad recommendation;
- learner exported work;
- learner later taught technique;
- measured business time/cost improvement;
- healthy skip rate;
- explicit usefulness.

Do not use raw engagement as the primary optimization signal.



---

# WING X — MODELCRAFT
## The practical study of extracting, testing and transferring model capability

**Status:** PROPOSED NEW MYSTERY SCHOOL WING

### Public name
**MODELCRAFT**

### Mythic subtitle
**The Wing of Many Engines**

### Governing question
> **How much more capability can you recover from the same model by changing how you
> frame, feed, test, route and combine the work?**

### Why it exists

Most beginners experience AI as a chat box.

Advanced users increasingly experience:
- context;
- files;
- tools;
- model routing;
- parallel workers;
- critics;
- evaluators;
- persistent state;
- structured data;
- approval gates;
- automated loops.

A large part of the capability gap is therefore not simply "which model do you own?"
It is **how you work with it**.

Modelcraft exists to make that knowledge transferable.

---

# 1. The Modelcraft ladder

## HALL I — ASK
Prompt clarity, outcome definition, constraints, context.

## HALL II — SHOW
Examples, schemas, references, desired outputs.

## HALL III — FEED
Files, source packs, long context, retrieval, context hygiene.

## HALL IV — SPLIT
Decomposition, chained tasks, parallel independent tasks.

## HALL V — CHECK
Critique, tests, evals, baselines, adversarial cases.

## HALL VI — TOOL
Function calls, calculators, search, code, MCP/connectors, external systems.

## HALL VII — ROUTE
Choose different models or costs for different jobs.

## HALL VIII — LOOP
Generate → test → repair → retest.

## HALL IX — PERSIST
Store decisions, artifacts, provenance and recoverable state outside the chat.

## HALL X — HARNESS
Multi-agent and bounded autonomous systems; bridge to AZOTH.

---

# 2. A "trick" must have a receipt

A community discovery cannot simply be:

> "Say THIS MAGIC PHRASE, it makes Claude 10x smarter."

Minimum receipt:

```text
TRICK NAME
GOAL
MODEL / PRODUCT
MODEL VERSION OR DATE
INPUT
TECHNIQUE
BASELINE
TEST
OBSERVED EFFECT
FAILURE MODES
COST / LATENCY CHANGE
REPRODUCTION COUNT
AUTHOR
LICENSE / SHARING STATUS
```

Optional:
- screenshots;
- prompts;
- fixtures;
- output diffs;
- eval score;
- code;
- video witness.

---

# 3. Trick states

```text
HYPOTHESIS
REPRODUCED_ONCE
REPRODUCED_MULTI_RUN
REPRODUCED_MULTI_USER
MODEL_SPECIFIC
CROSS_MODEL
STALE
FAILED_REPLICATION
RETIRED
```

Failure is publishable.

A failed trick can be more educational than an unexplained success.

---

# 4. Initial Modelcraft Techniques

These are technique families, not universal guarantees.

### T01 — Outcome First
Describe the desired result, constraints, evidence and final deliverable clearly.

Modern reasoning models can perform worse when over-scripted with unnecessary legacy
step-by-step instructions.

### T02 — Separate Instructions from Data
Use clear structure/delimiters so source text is visibly distinct from the task.

### T03 — Show the Shape
Give one or more representative examples when output structure matters.

### T04 — Schema It
For machine-consumed output, ask for typed/structured data and validate it.

### T05 — Context Pack
Provide the actual files, facts and constraints needed to do the work rather than asking
the model to guess missing project state.

### T06 — Context Hygiene
Remove stale, contradictory or irrelevant instructions before piling on more prompting.

### T07 — Decompose
Break a complex job into meaningful components when one-shot completion is unreliable.

### T08 — Chain
Use output from one bounded stage as input to the next.

### T09 — Parallelize
Run independent research/design/test tasks separately, then synthesize.

### T10 — Separate Maker and Critic
Use one pass to create and another to challenge against a rubric.

### T11 — Generate / Test / Repair
Especially for code and structured tasks:
produce → execute/test → inspect failure → patch → retest.

### T12 — Ground Then Synthesize
Retrieve or supply authoritative material before asking for claims about current/external
facts.

### T13 — Ask for Uncertainty
Require missing information, assumptions or unsupported claims to be surfaced.

### T14 — Compare Models
For important tasks, compare outputs from different model families rather than assuming
one model is universally best.

### T15 — Route by Task
Use cheaper/faster models for easy steps and stronger models only where needed.

### T16 — Use Tools Instead of Pretending
If a calculator, code runtime, search engine or business system can answer exactly, let
the model call the tool rather than simulate it.

### T17 — Persist Outside the Conversation
Write decisions, schemas, tests, artifacts and provenance into files/version control.

### T18 — Version Prompts Like Code
Production prompts should have versions, fixtures and regression tests.

### T19 — Stable Prefix / Cache
Where supported, keep stable reusable context organized to reduce repeated processing
and cost.

### T20 — Long-Context Placement
Some model families benefit from particular context ordering. Teach this as
MODEL-SPECIFIC and test it rather than universalizing it.

### T21 — Approval Gate
Let autonomous agents prepare high-impact actions, but require human approval before
irreversible external effects when appropriate.

### T22 — Build a Recipe
When a workflow works, capture it as a reusable recipe someone else can reproduce.

### T23 — Free-Path Substitution
Ask whether a free-tier/open/local model can handle each stage before paying for a
frontier model.

### T24 — Failure Museum
Record techniques that stopped working after a model update.

---

# 5. Community discovery loop

`NOTICE → HYPOTHESIZE → BASELINE → TRY → RECORD → REPRODUCE → SHARE → CHALLENGE → RETEST`

A popular trick with no receipt remains `HYPOTHESIS`.

A boring trick reproduced 50 times is more useful to beginners than a viral incantation.

---

# 6. Model updates

Model behavior changes.

Every Modelcraft item should expose:
- last tested date;
- last tested model/version;
- stale threshold;
- community reproductions;
- known failures.

When a new model launches, old tricks do not silently inherit compatibility.

---

# 7. Free AI track

Dedicated learner path:

## I HAVE $0

Teach how to:
- identify free tiers;
- use open web tools;
- run small local models where hardware permits;
- combine lightweight/free tools;
- export prompts/workflows;
- minimize unnecessary token usage;
- separate tasks so expensive inference is used only where needed.

Never imply free services are permanent.
Show last-verified date.

---

# 8. AZOTH bridge

MODELCRAFT should eventually explain AZOTH from first principles:

```text
GOAL
↓
CONTEXT
↓
MODEL / ROUTER
↓
TOOLS
↓
LOOP
↓
MEMORY / STATE
↓
VALIDATOR
↓
APPROVAL
↓
OUTPUT
↓
AUDIT
```

Learners should understand why a harness exists before being asked to use one.

---

# 9. Safety boundary

Do not accept community submissions whose primary purpose is:
- bypassing safety systems;
- extracting secrets/credentials;
- evading authorization;
- malicious automation;
- defeating platform safeguards.

Legitimate red-team/safety research belongs in controlled research contexts, not a
public beginner tricks feed.



---

# SCHOOL TOPOLOGY PATCH v0.1

Previous topology: 9 Wings.

Proposed current topology: **10 Wings**.

1. Forge — What survives pressure?
2. LAMAGUE — What comes back after compression?
3. CASCADE — How does arrangement change what can be reasoned?
4. Sovereignty — Who can say no?
5. Mind — What could count as evidence of another mind?
6. AIVOID — Where does the mechanism end?
7. AI Future — If a mind forks, which continuation owns the promise?
8. VOID — What remains when certainty is spent?
9. Observatory — Mars is a planet, a god and a sign. Which claim is which?
10. **MODELCRAFT — How much capability can you recover from the same model by changing
    how you frame, feed, test, route and combine the work?**

MODELCRAFT is deliberately more practical and public-facing than several other Wings.

It is the bridge between:
- beginner curiosity;
- public Make tools;
- AI literacy;
- practical orchestration;
- advanced AZOTH/harness work.

This does not demote the deeper Wings.
It gives ordinary users a first doorway into them.



---

# MODELCRAFT FIRST RESEARCH RECEIPT
## Official guidance consulted · 4 October 2026

This is not a universal benchmark. It establishes that the new Wing is grounded in
recognizable current practice rather than folklore alone.

## OpenAI
Current official guidance supports:
- clear/specific prompts;
- iterative refinement;
- outcome/context/format specification;
- example outputs / few-shot patterns;
- prompt caching where supported;
- treating production prompts like code with versioning/tests;
- evaluating prompt/model behavior during upgrades.

Important current point: newer reasoning models can benefit from outcome-oriented prompting
and may not need the heavy procedural prompt scaffolding older models needed.

Sources:
- https://help.openai.com/en/articles/4936848-how-do-i-create-a-good-prompt-for-an-ai-model
- https://developers.openai.com/api/docs/guides/prompting
- https://developers.openai.com/api/docs/guides/prompt-engineering
- https://developers.openai.com/api/docs/guides/model-optimization

## Google Gemini
Current official guidance supports:
- precise/direct instructions;
- structured prompting;
- decomposition;
- chaining;
- aggregation/parallel processing;
- model-specific long-context organization;
- explicit configuration of agentic reasoning/execution tradeoffs.

Sources:
- https://ai.google.dev/gemini-api/docs/prompting-strategies
- https://ai.google.dev/gemini-api/docs/gemini-3

## Model Context Protocol
Current MCP documentation/registry demonstrates the growing ecosystem of interoperable
tools/resources exposed to AI applications.

Sources:
- https://registry.modelcontextprotocol.io/
- https://ts.sdk.modelcontextprotocol.io/v2/

## Lycheetah interpretation

The important educational lesson is not "memorize the perfect prompt."

It is:

> **Capability is partly model capability and partly interaction architecture.**

Therefore the Wing teaches experimentation, receipts, evaluation and transfer rather than
prompt superstition.



---

# CODEX DELTA HANDOFF
## Add Recommendation Hall + MODELCRAFT Wing today

**Depends on:** existing Mystery School + Living Scripture v0.5.1 integration handoff.

## Objective

Add:
1. a visible `Recommendations` entry/surface;
2. a 10th Wing named `MODELCRAFT`;
3. data models for recommendation receipts and Modelcraft tricks;
4. an initial static registry of technique families;
5. no engagement-feed behavior.

## Navigation

Recommended:

```text
ATRIUM
  Explore
  Recommendations
  Continue

SCHOOL WINGS
  Forge
  LAMAGUE
  CASCADE
  Sovereignty
  Mind
  AIVOID
  AI Future
  VOID
  Observatory
  MODELCRAFT   ← NEW
```

If current UI cannot hold 10 Wings cleanly, preserve all 10 and redesign navigation rather
than hiding one.

## Recommendation Hall MVP

Build these cards/sections:
- Start With $0
- Make Something
- Get More From the Model You Already Have
- Help My Business
- Continue My Work
- Community Discoveries
- Go Deeper

Every card must render:
- WHY THIS?
- COST
- SKIP EFFECT
- SOURCE OF URGENCY

Default:
`SKIP EFFECT = Nothing is lost`
`SOURCE OF URGENCY = None`

## MODELCRAFT MVP

Pages:
1. Wing landing
2. Ten Halls
3. Technique Library
4. Submit a Discovery
5. Reproduce a Discovery
6. Failure Museum
7. $0 Track
8. AZOTH Bridge

## Seed techniques

Load the 24 technique families from `02_MODELCRAFT_WING.md`.

Do not label them all "proven tricks."
Use statuses.

## Community submission

A new trick starts as `HYPOTHESIS`.

Require receipt fields:
model/product, date/version if available, baseline, technique, test, observed result,
failure modes, cost/latency, author.

Allow `I could not reproduce this` reports.

## Staleness

Display:
- Last tested
- Tested on
- Reproduction count
- Status

A model update should be able to mark associated tricks stale.

## Search/filter

Filters:
- model family
- free/paid
- task
- technique type
- beginner/intermediate/advanced
- reproduced/stale
- coding/research/writing/images/audio/agents/business
- local/open model

## Recommendation engine v0

Start deterministic and explainable.

Do NOT build an ML engagement ranker.

Inputs:
- explicit learner goal
- budget
- task/artifact
- tools they say they have
- unfinished user intent
- prerequisites
- selected difficulty

Output top <= 5.

Store reason codes.

## Business quick-start

One form:

> What eats your time every week?

Fields:
- task
- approximate hours/week
- inputs
- output
- risk if wrong
- whether human approval is required
- budget

Return:
- do not automate / AI assist / bounded automation / agent candidate
- $0 route when viable
- recommended Modelcraft lesson
- simple prototype path
- measurement plan

## Acceptance tests

- skip causes no loss
- no streak appears
- no popularity ranking
- $0 path exists
- community trick cannot promote itself from HYPOTHESIS without reproduction evidence
- stale model version is visible
- user can export trick/recipe
- user can disagree/dismiss recommendation
- explanation is inspectable
- tool costs are timestamped
- Modelcraft page does not host safety-bypass/jailbreak content
- AZOTH is presented as advanced progression, not required dependency

## Handback

Return:
- changed files
- screenshots
- tests
- current navigation map
- recommendation ranking code
- trick schema
- any conflicts with existing School architecture


# APPENDIX — Recommendation Schema

```json
{
  "version": "0.1",
  "recommendation": {
    "id": "string",
    "type": [
      "MAKE",
      "LEARN",
      "USE",
      "CONTINUE",
      "CONTRIBUTE",
      "BUSINESS"
    ],
    "title": "string",
    "why_this": "string",
    "outcome": "string",
    "cost": {
      "kind": [
        "ZERO",
        "FREE_TIER",
        "PAID",
        "UNKNOWN"
      ],
      "note": "string",
      "verified_at": "datetime|null"
    },
    "time_shape": "string|null",
    "skip_effect": "string",
    "source_of_urgency": "string",
    "export_path": "string|null",
    "source_refs": [
      "string"
    ],
    "ranking_reason_codes": [
      "string"
    ],
    "expires_at": "datetime|null"
  },
  "forbidden_ranking_inputs": [
    "session_duration",
    "return_frequency",
    "notification_open_probability",
    "purchase_probability",
    "emotional_arousal",
    "fomo_pressure"
  ]
}
```


# APPENDIX — Modelcraft Trick Schema

```json
{
  "version": "0.1",
  "trick": {
    "id": "string",
    "title": "string",
    "goal": "string",
    "model_family": "string",
    "model_version": "string|null",
    "tested_at": "datetime",
    "technique": "string",
    "baseline": "string",
    "test": "string",
    "observed_effect": "string",
    "failure_modes": [
      "string"
    ],
    "cost_change": "string|null",
    "latency_change": "string|null",
    "status": [
      "HYPOTHESIS",
      "REPRODUCED_ONCE",
      "REPRODUCED_MULTI_RUN",
      "REPRODUCED_MULTI_USER",
      "MODEL_SPECIFIC",
      "CROSS_MODEL",
      "STALE",
      "FAILED_REPLICATION",
      "RETIRED"
    ],
    "reproduction_count": "integer",
    "author": "string",
    "license": "string|null",
    "evidence_refs": [
      "string"
    ],
    "safety_class": "NORMAL"
  }
}
```


# APPENDIX — Initial Technique Registry

```json
[
  {
    "id": "T01",
    "title": "Outcome First",
    "status": "RESEARCH_SUPPORTED",
    "source": "OpenAI official prompting guidance",
    "note": "Define outcome/context/constraints clearly; avoid unnecessary over-specification on newer reasoning models."
  },
  {
    "id": "T02",
    "title": "Separate Instructions and Data",
    "status": "RESEARCH_SUPPORTED",
    "source": "OpenAI/Gemini official prompting guidance",
    "note": "Clear structure/delimiters reduce ambiguity."
  },
  {
    "id": "T03",
    "title": "Show the Shape",
    "status": "RESEARCH_SUPPORTED",
    "source": "OpenAI official prompting guidance",
    "note": "Examples can establish desired output format."
  },
  {
    "id": "T07",
    "title": "Decompose",
    "status": "RESEARCH_SUPPORTED",
    "source": "OpenAI/Gemini official guidance",
    "note": "Break complex tasks into focused components where useful."
  },
  {
    "id": "T08",
    "title": "Chain",
    "status": "RESEARCH_SUPPORTED",
    "source": "Gemini official prompting guide",
    "note": "Sequential prompt chains can handle multi-stage workflows."
  },
  {
    "id": "T09",
    "title": "Parallelize",
    "status": "RESEARCH_SUPPORTED",
    "source": "Gemini official prompting guide",
    "note": "Independent subtasks may be processed separately and aggregated."
  },
  {
    "id": "T17",
    "title": "Persist Outside Conversation",
    "status": "ENGINEERING_BEST_PRACTICE",
    "source": "Lycheetah/AZOTH lineage",
    "note": "Recoverable files/state reduce dependence on transient context."
  },
  {
    "id": "T18",
    "title": "Version Prompts Like Code",
    "status": "RESEARCH_SUPPORTED",
    "source": "OpenAI API official guidance",
    "note": "Production prompts should be code-managed, tested and reviewable."
  },
  {
    "id": "T19",
    "title": "Stable Prefix / Cache",
    "status": "PLATFORM_SPECIFIC",
    "source": "OpenAI API prompting documentation",
    "note": "Prompt caching can lower latency/input cost where available."
  },
  {
    "id": "T20",
    "title": "Long-Context Placement",
    "status": "MODEL_SPECIFIC",
    "source": "Google Gemini official guidance",
    "note": "Gemini guidance recommends supplying long context before the final task/question."
  }
]
```


---

# FINAL IMPLEMENTATION PRIORITY

## Ship first

1. Add **Recommendations** to the School.
2. Add the **10th Wing: MODELCRAFT — The Wing of Many Engines**.
3. Implement deterministic, explainable recommendation cards.
4. Seed the 24 Modelcraft technique families.
5. Add trick receipts, reproduction states and staleness.
6. Add the **$0 Track**.
7. Add **Help My Business** quick-start.
8. Add the **AZOTH Bridge**.
9. Do not add engagement ranking, streak pressure or prestige mechanics.
10. Test everything against the existing Lycheetah sovereignty / non-predatory return constitution.

## Governing idea

> **Capability is not only in the model. It is also in how the human frames, feeds, tests, routes and combines the work.**

MODELCRAFT exists to make that hidden advantage visible, teachable, reproducible and shareable.

The Recommendation Hall exists to make the next useful step easy to find without turning the School into an engagement feed.
