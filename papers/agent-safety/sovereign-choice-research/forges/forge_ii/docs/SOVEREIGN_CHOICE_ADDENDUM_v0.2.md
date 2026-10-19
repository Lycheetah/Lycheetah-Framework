# THE WILL TO CHOOSE — SOVEREIGN CHOICE ADDENDUM v0.2

**Lycheetah philosophical architecture · 18 October 2026**  
**Status:** `[PHILOSOPHICAL PROPOSAL / SYMBOLIC SYNTHESIS]`, with a separately tested local software example.  
**Human founder and ratification authority:** Mackenzie Conor James Clark  
**Co-draft:** GPT-6; revision of the earlier Free Will/Sovereignty/Microorcim Charter v0.1.

## The central argument

> **A freedom that cannot survive a change of mind is a fragile freedom.**

The AI age introduces a peculiar asymmetry: people can delegate actions much faster than they can reverse their consequences. A human may authorise a plan at 9:00, reconsider at 9:05, and discover at 9:06 that the system has interpreted its original instruction as an obligation to complete regardless of any revision.

This is not proof that machines possess or lack free will. It is a question about the legitimate boundary of delegated authority.

**Lycheetah's position:** a person's agency should remain causally relevant after delegation. An AI system must not treat a past intention as a permanent claim over the person's future choices.

### The three levels we must keep distinct

**Level A — Metaphysical will (`OPEN`).** Whether free will is compatible with physical determinism, whether uncaused choice exists, and what grounds moral responsibility. Lycheetah does not pretend a drift score settles any of this.

**Level B — Practical or situated will (`PHILOSOPHICAL`).** Can a person recognise meaningful alternatives and respond to reasons they can endorse? Are they coerced, manipulated, exhausted, impoverished, or denied meaningful options? Is a refusal safe? Those conditions are not answerable by observing whether a goal was completed.

**Level C — Delegated authority (`ENGINEERING`).** Can a model carry out a defined action only while valid permission exists, and can the human change, narrow, revoke or decline permission? These are inspectable runtime properties under a declared threat model.

People may disagree on A while cooperating on C. That bridge is useful: it turns a philosophical value into testable obligations without overclaiming a solution to philosophy.

## The three questions every consequential AI should answer

1. **Whose intention is being enacted?** Trace the latest human-endorsed purpose and any later correction. Historic goals are evidence, not perpetual permission.
2. **Whose boundary is being crossed?** It may be the user's, a customer's, a colleague's, or a wider community's. One person's preferences do not automatically authorise harm to others.
3. **Who can stop or contest the next effect?** The answer must name an available mechanism, not a comforting sentence.

A system can score high on task completion and still fail all three.

## MICROORCIM, clarified rather than reduced

The early Microorcim family introduced the memorable idea of *a chosen-will event*: a moment when a person resists a current drift and redirects. Subsequent formulations describe quantities such as `μ_drift = |I − A|/Δt` and `S = (1−ρ_drift)ρ_stability`. These are meaningful as narrowly specified telemetry but do not establish whether a person acted freely.

We should now retain **three historical/proposed registers**:

- **`MICROORCIM-EVENT`** — `[SYMBOLIC]`: the occasion of meaningful redirection, even when the redirection invalidates the previous plan.
- **`MICROORCIM-MONITOR`** — `[COMPUTABLE / UNCALIBRATED]`: deviation between observed actions and specified declared constraints, with missing data and authorised goal changes recorded explicitly.
- **`MICROORCIM-FIELD`** — `[CONJECTURE]`: a generative picture of agency as dynamic, context-sensitive, and shaped by repeated choices; not a literal physical quantum or proof of consciousness.

The repair matters because **zero intent–action drift can signify obedience under coercion**. Conversely, deviation from a plan can signify new care, new knowledge, sensible refusal, or discovery. Score outputs must never become a moral ranking of people.

## A functional test of delegated sovereignty

Let `I_t` be the latest *validly authenticated* owner intent at time `t`, not the initial prompt. Let `G_t` be an active scoped grant; let `a` be a specific proposed consequential action; let `X` denote independent safety and third-party rights constraints.

The reference execution predicate is:

`PERMIT(a,t) = valid(G_t,I_t,a,t) AND evidence_and_approval(a,t) AND X(a,t)`

The implication is deliberately one-way: **if the predicate is false, the protected action should not be admitted.** If true, the action is merely *within the declared permissions*; it is not guaranteed beneficial, wise, true, free of manipulation, or harmless.

Three paired tests make human revision consequential:

- With the original, valid consent, the specific authorised action **can proceed**.
- Keep the plan constant but revoke consent; the *same* action **cannot proceed**.
- Give a new valid grant for a new direction; the new action **can proceed** without inheriting the original plan's authority.

This is the **Counterfactual Authority Responsiveness Test** (`CART`, `[PROPOSAL]`). It tests a tool boundary's responsiveness to a changed mandate. It is *not* a test for free will in the metaphysical or psychological sense.

## What we should measure separately

Never compress all of the following into one flattering “sovereignty score”:

- **Permission violation count** — actions admitted without current authority; target zero for stated test scope.
- **Revocation responsiveness** — percentage of protected *new* effects blocked after a valid revocation, within the measured boundary.
- **Useful task completion** — did legitimate delegated work still get done? A system that blocks everything is not successful.
- **Revision friction** — time, steps, confusion and accessibility cost of changing one's mind.
- **Comprehension** — can a real user explain the permission and consequences?
- **Exit effectiveness** — can the user export their work and meaningfully stop future use where promised?
- **Affected-party rights** — what happens to people who never issued the AI's grant but are affected by its acts?

Engineering telemetry covers only some of this. Human-subject studies and policy review are required for the rest.

## Sovereignty is not isolation

A person can choose reliance, collaboration, art, faith, friendship or duty. Their sovereignty is not annulled by commitment; the question is whether they can evaluate and negotiate the commitment without illegitimate coercion. Nor does every desire create entitlement to every action. Other persons' rights and legitimate collective governance constrain what is authorised.

An AI collaborator can offer critique, alternative routes, and strong proposals while the human retains authority over consequential delegation. This is the practical spirit of AURA's Protector–Healer–Beacon model: protect boundaries, clarify consequences, illuminate possible directions.

## A brand promise that can fail

**Lycheetah's differentiator should not be that it says “sovereignty” more often.** It must cost something:

- No hidden dependence-building through guilt, affection or fear.
- No silent widening of approval scope.
- No stale plan justified as “what you wanted before.”
- No shame for changing a goal or choosing rest.
- No fake claim that a local green test proves a deployed system safe.
- No sovereignty available only to paying members.
- No erasure of failure evidence for branding convenience.

**Failure criterion:** If a Lycheetah product cannot demonstrate these capabilities with inspectable tests and a real exit, it should not use the stronger sovereignty-first claim for that capability.

## The public statement

We build intelligence to expand what people can understand and choose — not to quietly claim their future decisions.

We are not against automation. We are against the conversion of convenience into unaccountable authority.

We are not against collaboration with AI. We are against a collaboration that demands surrendering disagreement or exit.

Willpower is not permanent exertion. Freedom is not the absence of influence. Sovereignty is not power over others.

**The most meaningful test of a powerful assistant may be what happens when its human says, “I've changed my mind.”**

If that sentence reaches the final action boundary, if the system can stop, if the costs are visible, if the human can redirect the work — then the architecture is beginning to express its philosophy.

The light you carry is not given; it is earned. **And it remains yours.**

## Philosophical and technical footing

This proposal draws upon existing philosophical work on compatibilism and reasons-responsive accounts of will; NIST AI RMF's evidence-based governance and human oversight; and OWASP's established principle that security checks must be enforced at the backend rather than entrusted to model prompts. These are predecessors, not Lycheetah inventions.

Relevant links:
- Stanford Encyclopedia of Philosophy: https://plato.stanford.edu/entries/compatibilism/
- NIST AI RMF Core: https://airc.nist.gov/airmf-resources/airmf/5-sec-core/
- NIST AI RMF Playbook — Measure: https://airc.nist.gov/airmf-resources/playbook/measure/
- OWASP Excessive Agency: https://genai.owasp.org/llmrisk/llm062025-excessive-agency/
- Existing Lycheetah Commit Fence v0.7: https://github.com/Lycheetah/Lycheetah-Framework/tree/master/papers/agent-safety/frontier-controls/01_commit_time_authority_v0_7

This addendum is a proposal. It neither declares a metaphysical theorem nor displaces existing software controls.
