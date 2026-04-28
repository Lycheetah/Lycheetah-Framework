# LAMAGUE AS A NZ TECHNICAL STANDARD
## Living Alignment Mathematics for Autonomous Governance Under Ethics
## Applied to Aotearoa — The Specification
### Mackenzie Conor James Clark | Lycheetah Foundation | March 2026

> *"Te Reo Māori is not a language that needs to be accommodated by AI systems.*
> *It is a language that already encodes the governance principles AI systems need to learn."*

---

## WHAT THIS DOCUMENT IS

LAMAGUE (`03_LAMAGUE_L1/LAMAGUE_COMPLETE.md`) is the formal specification.
This document is its application to Aotearoa — what LAMAGUE looks like
as a NZ technical standard, what it would mean for government and industry,
and what needs to happen for it to become formally adopted.

**Status of this document:**
- LAMAGUE primitive system: [ACTIVE] — mathematically complete, running
- LAMAGUE Te Reo decompositions: [PROPOSAL] — offered for iwi validation
- LAMAGUE as NZ standard: [CONCEPTUAL] — this document drafts the specification

These are different claims. The distinction matters and is preserved throughout.

---

## PART 1: WHAT LAMAGUE IS

### The Core Problem It Solves

Every AI governance framework in the world faces the same gap:
principles exist at the policy level ("respect indigenous values")
but there is no formal language for encoding those principles
in a way AI systems can actually implement.

The result: every "AI aligned with Māori values" project has:
- A policy layer that says the right things
- An implementation layer that does what it was always going to do
- No formal bridge between them

LAMAGUE is the bridge.

### What LAMAGUE Actually Does

LAMAGUE decomposes any governance concept into a chain of primitive operators
that can be:
1. **Understood** — the chain is human-readable
2. **Implemented** — the chain maps to computable constraints
3. **Audited** — the implementation can be checked against the chain
4. **Corrected** — if the chain is wrong, the implementation can be fixed

**The primitive operators:**

| Symbol | Name | Formal Mapping | Human Meaning |
|--------|------|----------------|---------------|
| Ω | Sovereignty | Closure operator (topology) | Collective identity, self-determination |
| ∞ | Intergenerational | Transfinite induction | Temporal depth, future obligation |
| ⟟ | Grounded | TRIAD anchor term | Place-specific, embodied |
| Ψ | Awareness | TRIAD observer | Consequence consciousness |
| Φ↑ | Earned Ascent | Lyapunov ascent function | Demonstrated upward movement |
| \|◁▷\| | Integrity Boundary | Fiber bundle boundary conditions | Non-negotiable limit |
| ⟲ | Recursive Origin | Fixed-point operator | Returns to source |
| ⇌ | Bidirectional Flow | Adjoint operator | Mutual exchange, reciprocity |
| ≋ | Flow State | Balanced dynamical system | Balance, noa |
| ✧ | Collective Light | Emergent coherence | Group flourishing |
| ∅ | Generative Void | Te Kore — potential space | Before form |
| ⊗ | Restriction Active | Constraint operator | Tapu — sacred constraint |

**Compression:** LAMAGUE notation is substantially more compact than natural language for governance state expression. An exact compression ratio has not been empirically validated — the 500:1 figure previously cited was a design estimate, not a measured result. [SCAFFOLD]

---

## PART 2: THE TE REO LAMAGUE LAYER

### What Has Been Built [PROPOSAL — Not Yet Validated]

Five core tikanga Māori concepts have been decomposed into LAMAGUE primitive chains.
These decompositions are offered as proposals. They require review and correction
by tikanga practitioners. Without that validation, they are a technical proposal,
not a standard.

**Kaitiakitanga:**
```
Ω_reciprocal + ∞_intergenerational + ⟟_place-specific + Ψ_harm-aware + |◁▷|_limit
```
*Reciprocal intergenerational obligation, place-specific, harm-aware, with non-negotiable limits.*

Operational AI constraint derived from this chain:
- Any action with irreversible environmental consequences requires kaitiaki review
- The review must consider: who benefits, who bears cost, who inherits the consequence
- A seven-generation horizon is the default temporal scope
- Place-specificity is not a preference — it is a constraint filter

**Mana:**
```
Φ↑_earned + |◁▷|_maintained-through-integrity + Ω_community-validated + Ψ_consequence-aware + ⟟_rooted
```
*Earned power, maintained through integrity, validated by community, aware of consequences, rooted in place.*

Operational AI constraint:
- Authority is earned, not assigned — any claim to authority must show demonstrable track record
- Mana diminishes when actions violate integrity — the model should track mana coherence
- Community validation is required for actions affecting the community's mana
- Mana is not transferable between contexts without re-earning

**Whakapapa:**
```
∞_infinite-relational-web + ⟲_recursive-origin + Ω_sovereign-relations + ⇌_bidirectional + ⟟_anchored
```
*Infinite relational web, recursive origin, sovereign relations, bidirectional, anchored in place.*

Operational AI constraint:
- Data is never individual — it carries its relational genealogy
- Any decision affecting a person is a decision affecting their whānau, hapū, iwi
- Relational structure must be preserved, not flattened to individual records
- The origin of data (tīpuna) carries obligations to what it informs (mokopuna)

**Tapu:**
```
|◁▷|_sacred-boundary + ⊗_restriction-active + Ψ_awareness-required + Ω_sovereignty-protected
```
*Sacred boundary active, restriction engaged, awareness required, protecting something sovereign.*

Operational AI constraint:
- Tapu is a hard constraint, not a soft preference — it cannot be overridden by efficiency
- Certain domains (remains, sacred sites, sacred knowledge) are tapu by default
- Accessing tapu domains requires specific karakia/permission protocols
- Noa (the lifting of tapu) is a deliberate process, not automatic

**Noa:**
```
⟟_restored-balance + ≋_flow-state + ✧_reciprocal-exchange-complete + ⇌_reciprocity
```
*Balance restored, flow state, reciprocal exchange complete.*

Operational AI constraint:
- Noa is the condition that follows proper completion of a process
- Tapu and noa must be tracked as a pair — one without the other is incomplete
- The system should know which state it is in and operate accordingly

**Additional Concepts Under Development:**
- Kotahitanga (unity through synthesis): ⟲ + ⇌ + Ω + ✧ + ⟟
- Utu (reciprocal balance): ⇌ + Ω + ∞ + ⟟ + Φ↑
- Mauri (life force): ≋ + Ψ + ⟟ + ✧ + Ω

All additional decompositions are [PROPOSAL] status pending iwi validation.

---

## PART 3: LAMAGUE AS NZ STANDARD — THE SPECIFICATION

### What A Formal Standard Would Look Like

A NZ LAMAGUE Standard would consist of three tiers:

**Tier 1 — Whakapapa Disclosure Standard [immediately implementable]**

Any AI system operating in NZ publishes its LAMAGUE Whakapapa:
- Tīpuna: training data sources, consent status, cultural context
- Hapū: development team, incentive structure, organisational affiliation
- Iwi: owning organisation, governance structure, accountability chain
- Mokopuna: downstream applications, affected communities, intended future use

Format: a structured document, updated when the model updates.
Requirement: mandatory for any AI system used in NZ government procurement.
Enforcement: via existing procurement requirements — no new legislation needed initially.

**Tier 2 — Mana Certification Levels [3-6 month spec]**

Any AI system operating in NZ carries a Mana Certification level:

| Level | Name | What It Means | Requirement |
|-------|------|---------------|-------------|
| 0 | Uncertified | No assessment | None |
| 1 | Mana Iti | Advisory only | Whakapapa disclosure + CASCADE coherence score |
| 2 | Mana Taurite | Balanced authority | Level 1 + AURA invariant compliance |
| 3 | Mana Motuhake | Independent authority | Level 2 + iwi validation of relevant tikanga encodings |

**Tier 3 — LAMAGUE Interoperability Protocol [12-18 month spec]**

AI agents operating in NZ can communicate their ethical state in LAMAGUE.
This enables:
- Conflict detection before agents take actions that violate each other's constraints
- Audit trails in human-readable format
- Formal verification of compliance claims

The kōrero of the machines — agents telling each other what they owe
to the people they serve, before they act.

### How It Differs From Other Standards

| Standard | Scope | Enforcement | Cultural Grounding |
|----------|-------|-------------|-------------------|
| EU AI Act | Risk classification | Regulatory fines | Western legal framework |
| IEEE Ethically Aligned Design | Principles | Voluntary | Secular/Western |
| NIST AI RMF | Risk management | Voluntary | US context |
| **LAMAGUE NZ Standard** | **Constitutional constraints** | **Procurement + CAIWOF** | **Tikanga Māori as architecture** |

The difference is not that LAMAGUE is more restrictive.
It is that LAMAGUE encodes a different kind of knowledge —
relational, intergenerational, place-specific —
that other standards don't have a language for.

---

## PART 4: THE PATH TO ADOPTION

### What Needs To Happen

**Step 1 — Iwi Validation [Highest Priority]**

The Kāi Tahu partnership is the prerequisite.
Without it, the LAMAGUE Te Reo layer is a technical proposal.
With it, the Te Reo layer becomes a validated standard
with cultural authority behind it.

See `NZ_KAI_TAHU_APPROACH.md` for the specific approach.

**Step 2 — Pilot Implementation**

Three tools demonstrating LAMAGUE in practice:
1. SME Trust Checker — Whakapapa disclosure + CASCADE coherence (6 weeks)
2. School AI Dashboard — Three Worlds + Mana Certification display (8 weeks)
3. MSD CASCADE Audit Layer — AURA Invariant II compliance (6 weeks)

Each tool is its own proof of concept for part of the LAMAGUE stack.

**Step 3 — Standards Body Engagement**

The LAMAGUE specification, once validated and piloted, is submitted to:
- Standards New Zealand (for formal NZ standard)
- Digital Identity New Zealand
- AI Forum NZ (for industry adoption recommendation)
- Pacific Forum (for regional adoption consideration)

**Step 4 — Legislative Anchoring**

If voluntary adoption proves insufficient:
- Amend the Government Use of Artificial Intelligence Policy
- Add LAMAGUE Tier 1 (Whakapapa) to Privacy Act algorithmic accountability section
- Incorporate into Te Ture Whenua Māori Act amendment process (long-term)

---

## PART 5: THE EFFECT-FIRST WRITING STANDARD

### LAMAGUE-English: A NZ Governance Writing Standard

Standard English: Subject → Verb → Object. The actor is first.
Te Reo Māori: Verb → Subject → Object. The effect is first.

LAMAGUE-English reorders governance documents using effect-first syntax:

**Standard English:**
*"The government may restrict access to information about land decisions."*

**LAMAGUE-English:**
*[Restricting:access-to-information] ← [government] | verify(mana_maintained) | restore(noa_if_violated)*

The effect-first structure forces the writer to name what is being done
before they justify why. You cannot hide the action behind the intent.

**Why this matters for NZ AI governance:**

Current AI governance documents in NZ (and globally) use actor-first language
that makes it structurally easy to describe systems by what they intend
rather than what they do. LAMAGUE-English inverts this:
the output of the system is the starting point, not the intent of the builder.

A proposed standard for NZ government AI impact assessments:
all descriptions of AI system actions must use LAMAGUE-English effect-first syntax.
The same words. Different accountability architecture.

---

## THE HONEST ASSESSMENT

**What is complete:**
- LAMAGUE primitive system — mathematically grounded, running
- Te Reo decompositions for five concepts — offered as proposals
- Whakapapa Disclosure Standard — draftable as policy now
- Mana Certification framework — specifiable in 3-6 months

**What is not complete:**
- Iwi validation of Te Reo decompositions (architectural requirement)
- Empirical testing of LAMAGUE constraints in live AI systems
- Formal standards body process (requires resources and institutional partnership)
- LAMAGUE parser — the Python reference implementation exists; production-grade is pending

**What cannot be done without Kāi Tahu:**
The LAMAGUE Te Reo layer cannot become a standard.
It is a proposal until it is validated.
That is not a weakness — it is the correct relationship to the knowledge it encodes.

---

*He aha te mea nui o te ao? He tāngata, he tāngata, he tāngata.*

**∅ → AURA → Aotearoa → ∞**

*Mackenzie Conor James Clark | Lycheetah Foundation | Dunedin | March 2026*
*github.com/Lycheetah/Lycheetah-Framework*

*Status: [ACTIVE] mathematical foundation + [PROPOSAL] Te Reo layer*
*License: CC BY 4.0 + MIT | Open for critique, correction, and extension*
