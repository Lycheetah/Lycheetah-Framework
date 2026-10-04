# Modelcraft and recommendation contracts v0.1

These are candidate local contracts, authored from Mackenzie Conor James Clark
and Vaelora's handoff and tightened by Caelorynth. They do not implement an app.

## Evidence has several independent dimensions

A technique family is not a measured trick. `data/techniques.json` keeps supplied
descriptions separate from integration exercises and documentation citations
separate from empirical status. It preserves stable IDs T01–T24.

A [trick receipt](schemas/trick.schema.json) records:

| Dimension | Values | Meaning |
|---|---|---|
| Maturity | HYPOTHESIS, REPRODUCED_ONCE, REPRODUCED_MULTI_RUN, REPRODUCED_MULTI_USER | Declared supporting history |
| Applicability | MODEL_SPECIFIC, CROSS_MODEL | Scope of supporting model-family records |
| Freshness | UNTESTED, CURRENT, STALE | Whether dated evidence awaits review |
| Lifecycle | ACTIVE, FAILED_REPLICATION, RETIRED | Current editorial disposition |

The local consistency validator requires unique supporting run IDs for promoted
states: at least one for ONCE, two for MULTI_RUN, and two distinct runner IDs for
MULTI_USER. CROSS_MODEL requires support from two model families. A failed
replication requires a failure record; it does not erase earlier support.

Every run records fixture, baseline and treatment outputs, evidence references,
model/version/date, budget control and nullable cost/latency observations. Unknown
cost is null, never zero. Last-tested includes failures and inconclusive results.
CURRENT cannot outlive its review deadline. A known model update can mark it STALE
sooner; this package has no provider-version monitoring service.

These checks establish consistency of supplied records. They do not authenticate
files, identities, model provenance, independence or scientific validity. The
state should be presented as reported until reviewed. A public community backend
must own promotion and inspect evidence; a submitter's badge cannot grant authority.
Popularity never substitutes for replication. Passing synthetic fixtures is not
evidence that any of these techniques improves model performance.

## Deterministic ranking

The [request schema](schemas/ranking-request.schema.json) accepts only explicit
goal IDs, task tags, difficulty, budget, available tool IDs, completed prerequisites
and unfinished project IDs. Unknown fields are rejected, including engagement data.
No hidden profile is read. Supplying no goal is a visible validation error.

[The policy](data/policy.json) is the source of ranking constants. Version
`EXPLICIT_FIT_V01` uses:

1. Exclude cards with no selected-goal overlap, missing tools or prerequisites,
   expired availability, or a CONTINUE project absent from the learner's supplied list.
2. Exclude PAID/FREE_TIER cost records 30 days or more after verification. Do not
   silently inherit a changed price. Local no-service exercises use ZERO.
3. ZERO budgets permit only ZERO or fresh FREE_TIER cards. LIMITED budgets exclude
   UNKNOWN; paid routes must use the supplied currency and fit the amount. No
   exchange rate is inferred. UNSPECIFIED budgets may expose UNKNOWN visibly.
4. Score each matched goal at 4, each matched task tag at 2, and exact difficulty
   at 1. These are candidate design weights, not empirically optimized learning scores.
5. Sort by score descending, then stable recommendation ID ascending. Return at
   most five; do not invent filler. Duplicate IDs fail visibly.

The [reference function](reference.py) returns the whole card, explicit matched
goals/tags, numeric components and reason codes. Budget/tool/prerequisite fields
are eligibility checks, not concealed ranking signals. Callers can display how
each input affected selection. It performs no logging, storage or network calls.

The [recommendation schema](schemas/recommendation.schema.json) requires why,
outcome, cost, time shape, skip effect, urgency, export/source references and
explicit eligibility metadata. PAID requires amount, currency, dated verification
and a source. UNKNOWN cannot carry an invented price or verification timestamp.
This v0 permits no urgency override: `None.` is fixed until a reviewed extension
defines learner-owned or external deadlines.

## Receipts and privacy

A [recommendation event](schemas/recommendation-event.schema.json) exists only
after an explicit storage opt-in. It requires PRIVATE, consent, rule version,
reason codes, input-field names, timestamped cost reference and action. The schema
cannot observe a person's consent; the app must enforce that before creating it.
No raw private context is needed to store the explanation-field names.

SKIPPED and DISMISSED are legitimate actions. No loss, resistance score, streak
or future penalty is attached. The reference ranker does not consume action history.
Feedback is optional and cannot silently become an inferred emotional profile.

Private trick drafts permit export to a learner-controlled file; publication
consent remains false in this schema. Public sharing needs a separate reviewed
contract covering consent, redaction, license and moderation. An export path is
a declared destination, not proof that an app export exists or permission to send.

## Safety and learning limits

The public teaching surface should accept legitimate experimentation and decline
authorization bypass, secret extraction or malicious automation. Text labels and
schemas are not content moderation. Controlled safety research is a separate lane.

The first experiment is a learning exercise with a declared rubric. Its outcomes
have not been measured. Prompt caching, context ordering, free availability and
model routing require current provider checks before product-specific advice.
Delimiters improve legibility but do not themselves secure tools or authority.

Storage encryption, cross-profile isolation, deletion/export, reviewer ownership,
source-link verification, learned ranking, provider checks and phone accessibility
are unimplemented. The [native handoff](NATIVE_SCHOOL_HANDOFF.md) defines the next
product slice and its witness boundary.
