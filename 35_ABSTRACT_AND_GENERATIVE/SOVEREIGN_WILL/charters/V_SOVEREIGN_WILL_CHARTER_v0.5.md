# LYCHEETAH — SOVEREIGN WILL
## Forge V constitutional addendum: A right that survives execution

**18 October 2026 · Status `[PROPOSED PHILOSOPHICAL ARCHITECTURE]` + `[TESTED-LOCAL EXECUTION PROPERTY]`**  
**Founder/final canon authority:** Mackenzie Conor James Clark  
**Co-creative drafting:** Lycheetah × GPT-6  
**Prior lineage:** Sovereign Choice Forges I–IV, MICROORCIM, AURA, TIM, Earned Light, Lycheetah's *Sovereignty Is Not Dominion*.

## Thesis

> **An instruction is not perpetual ownership of the person who gave it.**

A machine can faithfully execute an old instruction and thereby violate a person's current, legitimate choice. Task success and sovereignty preservation are distinct criteria. We propose that an acting agent must respect the latest valid authority state at each protected point of consequential action, within explicitly declared limits of revocation and system finality.

This is an operational design claim, not a proof of the metaphysics of free will.

## Four registers — do not confuse them

1. **Free will (philosophy):** the open question of meaningful self-authored choice, often framed through reasons-responsiveness, control, alternatives and freedom from coercion. No code or score below proves it.
2. **Willpower (practical psychology):** the capacity to sustain *or redirect* effort toward an endorsed reason. A voluntary stop can demonstrate it. Endurance is not moral rank.
3. **MICROORCIM (symbolic language):** a recognisable episode where an intention is maintained, contested or revised under pressure. It remains a conceptual object. Its numerical drift monitor measures certain observable mismatches, not free will or personal worth.
4. **Sovereign Choice (engineering):** the runtime's answer to a narrower question: *Would this local consequential effect have been permitted if the person had validly revoked or revised their grant before finality?*

## The Sovereign Choice Counterfactual

For a specified proposed action `a`, protected finality boundary `F`, authority version `G` and context `C`:

- **Control path:** `G` is still active, matches `a`, and complies with applicable policy. The host may admit the effect.
- **Revision path:** the human legitimately withdraws or revises `G` before `F`. The host must not create a new protected effect from the stale authority generation.

The contrasting outcome measures **counterfactual sensitivity to an authoritative revision**, not authentic consent or the existential freedom of a mind.

These conditions are asymmetrical. The user must retain the ability to revoke; an agent does not thereby acquire a personal right to disregard valid instructions. The agent needs bounded operation, legitimate refusal of unsafe/unauthorised acts, transparent constraints and a review path, not ungrounded claims of personhood.

## The Local Finality Axiom

Let `generation(a)` be the generation bound to an execution handle, and let `generation(current)` and `active(current)` be transactionally checked from the same trusted database as the effect record.

A *new* protected effect may be committed only when:

`active(current) AND generation(a) = generation(current) AND hash(a) = hash(approved_action) AND handle_unused AND no_policy_veto`.

This is a **conditional specification**, not a formal proof for all possible implementations. Some conditions are enforced by the upstream `CommitFence` and some by Forge V's host-facing choice adapter. The trust boundary must prohibit agents and external parties from direct access to upstream grant methods and database writes. This code does not implement authenticated operator identity, informed consent, policy vetoes beyond its local checks, or remote effect cancellation.

An already committed effect is not a new effect: querying its previous receipt after revocation may correctly return `CONFIRMED`. Revocation changes the legality of future action, not the physical past.

## The Crash-Consistency Insight

Forge IV separated the intention journal from the upstream permission store. Both sides could be independently correct yet disagree after an interrupted multi-step update. Forge V stores intention version changes in the **same transaction** as the authority generation. A failure before that transaction commits rolls back *both*. The improvement is local crash consistency, not a guarantee against dishonest operators or provider-side races.

This is an application of standard ACID transactions and generation fencing to the established Lycheetah policy model. Neither mechanism is claimed to be novel. The distinct contribution for further evaluation is connecting the philosophical right to revise one's intention to a specific action-mediation and evidence contract.

## Seven sovereignty obligations for product designers

1. **Right to understand:** show the actual action and relevant consequences before approval; represent uncertainty.
2. **Right to narrow:** preserve precise recipients, scopes, resources, time windows and purposes; never silently broaden.
3. **Right to disagree:** refusal does not trigger shame, coercion, punishment or artificial inconvenience.
4. **Right to revise:** the user can replace an old instruction without being treated as defective or inconsistent.
5. **Right to stop:** existing active work can be halted at the system's actual reversible boundary, and in-flight exceptions are clearly disclosed.
6. **Right to a receipt:** the user can inspect what was authorised, what happened and whether completion was before or after revocation.
7. **Right to leave:** practical exit, export and a meaningful human review path exist wherever the product's stakes require them.

These are proposed acceptance obligations, not evidence that every Lycheetah product already fulfils them.

## No performance-based moral worth

A low MICROORCIM behavioural adherence score is not proof of weak will, compromised dignity or diminished autonomy. A person may freely change priorities, be constrained by poverty or disability, rest, resist coercion, protect others or reject harmful work. The right to revise must be legible **without compelling disclosure of a private explanation**.

## What would earn the broader claim?

- Authenticated approvals tied to exact, understandable action previews.
- Human-participant comprehension results, including ability to detect and refuse pressure.
- Mock and real-provider tests of cancel/revoke-under-load, unknown outcomes and recovery.
- Quantification of false blocks and lost legitimate utility, alongside stale or harmful effects.
- Independent review, baseline comparisons, operational logs and published failures.

Until then the valid public claim is bounded: **Forge V locally demonstrates atomic intention revision and protected-fence integration against SHA-verified GitHub code under controlled tests.** It does **not** prove real-world sovereignty, full alignment, free will, or universal safety.

## The public-facing proposition

> Lycheetah builds intelligence that can help you move faster without taking ownership of your direction.
>
> You may choose. You may refuse. You may learn and change your mind.
>
> The system must respect those decisions at the points where its actions matter.
>
> **Earned Light. Sovereign Will. Intelligence Without Dominion.**
