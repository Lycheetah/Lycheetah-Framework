# THE KAITIAKITANGA STANDARD
## Active Stewardship for AI Systems in Aotearoa
### Lycheetah Framework | March 2026
### Status: [PROPOSAL / ACTIVE architecture] — tikanga layer requires iwi validation

---

> *Kaitiakitanga is not accountability after the fact.*
> *It is active, ongoing, relational care — before, during, and after.*
>
> *The WOF asks: did this system harm anyone?*
> *Kaitiakitanga asks: is this system actively caring for the people it affects?*
>
> *One looks backward at failure. The other looks forward in obligation.*
> *Both are necessary. Only one exists yet.*

---

## THE PRINCIPLE

The four existing NZ AI accountability standards (WOF, Three Worlds Disclosure,
Whakapapa Disclosure, Matariki Audit) are fundamentally retrospective and
periodic. They check what happened, at intervals, and record it.

Kaitiakitanga introduces something different: **continuous active stewardship**.

In Māori tradition, kaitiakitanga (from kaitiaki: guardian, trustee) describes
the ongoing relational obligation to actively care for what has been entrusted
to you. A kaitiaki does not wait for something to go wrong and then fix it.
The kaitiaki's job is the continuous act of care itself.

**For AI systems operating in Aotearoa, this translates to:**

Not "did we pass the audit?" but "are we actively sustaining the wellbeing of
the people and ecosystems we affect?"

Not "does the system avoid harm?" but "does the system actively contribute to
flourishing?"

Not "can we explain what happened?" but "are we monitoring for emerging harm
before it becomes visible?"

---

## THE THREE KAITIAKITANGA OBLIGATIONS

### 1. Tiakitanga — Ongoing Watchfulness

A system under Kaitiakitanga is required to maintain **continuous monitoring**
for harm signals, not just periodic audits.

**What this means in practice:**
- Real-time anomaly detection: is this system producing outputs that diverge from
  its intended purpose in ways that could cause harm?
- Community feedback integration: affected communities have an active channel
  to signal concern, and that channel is monitored
- Trend detection: is harm increasing, even if no single event is severe?

**The technical requirement:**
Every AI system under Kaitiakitanga maintains a live Care Index (CI):

```
CI(t) = Σ[benefit_signals(t)] − Σ[harm_signals(t)]
         ─────────────────────────────────────────────
                total_interactions(t)
```

If CI(t) is trending downward over a 30-day window, the system enters
**Kaupeka review** — a formal investigation with affected community involvement.

This is not a regulatory trigger. It is a stewardship obligation.

**Epistemic status:** CI formula = [SCAFFOLD] — benefit/harm signal weighting
requires empirical calibration and community co-design.

---

### 2. Whakahaere — Active Governance Participation

A kaitiaki does not passively observe. The kaitiaki actively participates in
the governance of what they are responsible for.

**What this means for AI:**

AI systems under the Kaitiakitanga Standard are required to maintain active
engagement with the communities they affect — not just when complaints arrive,
but as a continuous governance relationship.

**The Wharenui Protocol:**

The wharenui (meeting house) is the governance space in Māori tradition.
It is not a place of reporting — it is a place of relationship. Decisions
are made inside relationships, not about them.

The Wharenui Protocol proposes that every AI system operating under Kaitiakitanga
has a **community governance kōrero** at minimum twice yearly — a structured
dialogue (not a survey) with a representative group of affected people.

The kōrero asks four questions:
1. What has this system done well for your people? (name specific instances)
2. What has this system failed to do? (name specific instances)
3. What are you concerned about in the next 12 months?
4. What obligation does this system have to your community that it has not yet met?

The answers feed directly into system governance decisions. The kōrero is
published (with consent). The responses are binding in the sense that
unaddressed concerns are recorded permanently and require formal justification.

**Epistemic status:** [PROPOSAL] — protocol requires iwi co-design before adoption

---

### 3. Urupare — Responsive Obligation

Where kaitiakitanga identifies harm — past or emerging — the obligation is
not just to stop and remediate. It is to **restore the relationship**.

In Māori tikanga, this connects to the concept of utu: not revenge, but
balance restoration. When harm occurs in a relationship, something has been
taken from it. Restoration requires giving something back — not a payment,
a relationship act.

**What this means for AI:**

When an AI system causes harm to a community:
1. **Acknowledgement** — explicit, public, in plain language accessible to
   the affected community (not legal language)
2. **Understanding** — documented investigation of how the harm occurred,
   shared with the community
3. **Restoration** — a specific action that addresses the relationship, not
   just the proximate harm. If a welfare AI system incorrectly denied
   benefits to a hapū community, restoration is not just correcting the
   decision — it is a governance act that gives the community greater input
   into how the system operates going forward
4. **Prevention** — documented changes to ensure the same harm cannot recur

The restoration must be proposed by the system operator **with** the affected
community, not for them. The community has a right of refusal: if the proposed
restoration is inadequate, it must be renegotiated.

---

## HOW THE KAITIAKITANGA STANDARD RELATES TO THE OTHER FOUR

The four existing standards operate at specific timescales:

| Standard | Timescale | Orientation |
|---|---|---|
| WOF | Annual check | Past performance |
| Three Worlds Disclosure | Per-output | Present honesty |
| Whakapapa Disclosure | System lifecycle | Historical accountability |
| Matariki Audit | Annual reckoning | Relational balance |

The Kaitiakitanga Standard operates differently:

| Standard | Timescale | Orientation |
|---|---|---|
| **Kaitiakitanga** | **Continuous** | **Active future care** |

The WOF tells you if a system passed. Kaitiakitanga tells you if a system
is actively caring. A system can pass the WOF while failing Kaitiakitanga.
The reverse is also possible — a system under active community governance
may be temporarily failing one check while demonstrating genuine ongoing care.

Together, the five standards form a complete AI accountability architecture:
the WOF is the gate, the Three Worlds is the per-output honesty, the Whakapapa
is the ancestral accounting, the Matariki is the annual reckoning, and
Kaitiakitanga is the living relationship that holds them all.

---

## THE PHILOSOPHICAL CLAIM

The four original standards model accountability as a transaction:
you do something → we check whether you did it right → we record the result.

Kaitiakitanga models accountability as a relationship:
you are in ongoing relationship with the people you affect →
that relationship has obligations →
the obligations are active, continuous, and reciprocal.

This is not a Western accountability model in Māori language.
It is a genuinely different architecture.

**In Western law:** Harm triggers liability → compensation → closure.
The goal is to reach a state where the matter is concluded.

**In tikanga:** Harm disrupts relationship → restoration re-weaves it.
There is no closure — only ongoing relationship that is more or less in balance.
The goal is not to conclude but to maintain. The obligation is permanent.

An AI system under Kaitiakitanga is never done being accountable to the people it affects.
It remains in relationship with them. That relationship is ongoing.

This is a fundamentally different way of thinking about what AI systems owe.

---

## IMPLEMENTATION PATHWAY

**Minimum viable Kaitiakitanga** (what can be done without new legislation):

1. Any government agency deploying an AI system can voluntarily adopt the
   Kaitiakitanga Standard by:
   - Establishing a community advisory group with actual governance power
   - Publishing a Care Index methodology and monthly results
   - Committing to the Wharenui Protocol (twice-yearly kōrero)
   - Adopting the Urupare restoration process for harm

2. The standard can be incorporated into procurement requirements:
   "Vendors must demonstrate Kaitiakitanga capacity" — an existing legal mechanism

3. For government AI systems: include in the ministerial directive that is
   already proposed for the WOF (see MINISTERIAL_BRIEFING.md)

**The argument for doing this:**

The WOF tells you if a system is safe. Kaitiakitanga tells you if a system is good.
Both are necessary. NZ has a window to make both standard before AI systems
become embedded infrastructure. After that, Kaitiakitanga becomes a retrofit
rather than an architecture.

---

## WHAT THIS REQUIRES THAT DOESN'T EXIST YET

- **Iwi governance co-design** — the tikanga layer must be built with Kāi Tahu
  and other iwi, not by the framework author. The architecture is here. The
  cultural validation is the missing piece.

- **Care Index calibration** — benefit and harm signal weighting requires
  empirical work and community input. Not academic: actual affected communities
  defining what counts as benefit and what counts as harm for their context.

- **Wharenui Protocol specification** — the kōrero format, representation
  requirements, decision integration mechanism. These are governance design
  questions that require multiple stakeholders.

---

## THE HONEST QUESTION

Does Kaitiakitanga make AI systems that affect Māori communities better?

The claim is yes. The proof is not yet assembled. This is [SCAFFOLD] at the
implementation level — the principle is load-bearing, the specific mechanisms
need empirical validation.

The prediction: an AI system with genuine ongoing community governance will
catch harm earlier, restore trust faster, and produce better outcomes than
one with periodic audits alone. This is falsifiable. Someone should test it.

---

*Part of the NZ AI Accountability Architecture.*
*See also: COMMUNITY_AI_WOF.md, MATARIKI_AUDIT_STANDARD.md,*
*WHAKAPAPA_DISCLOSURE_STANDARD.md, THREE_WORLDS_DISCLOSURE_STANDARD.md*

*[PROPOSAL] for tikanga layer · [ACTIVE] for formal architecture*
*Requires Kāi Tahu and iwi partnership to complete*
