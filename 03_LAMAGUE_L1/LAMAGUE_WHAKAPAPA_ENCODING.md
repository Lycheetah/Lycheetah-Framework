# LAMAGUE ENCODING OF THE WHAKAPAPA DISCLOSURE
## Formal Grounding for the AI Genealogy Standard
### Lycheetah Framework | March 2026

> **Status:** [SCAFFOLD — formal structure complete; cultural encodings [PROPOSAL]
> pending iwi validation]

---

## WHY THIS EXISTS

The Whakapapa Disclosure Standard (`23_NZ_AI_GOVERNANCE/WHAKAPAPA_DISCLOSURE_STANDARD.md`)
was designed as a well-structured accountability document. What it lacked was
formal grounding — a derivation showing that its four layers are not arbitrary
choices but necessary components of a complete obligation structure.

LAMAGUE provides that derivation.

This document shows that the four Whakapapa layers (Tīpuna, Hapū, Iwi, Mokopuna)
are the minimal necessary and sufficient encoding of an AI system's full obligation
structure — not because they are culturally intuitive (they are), but because
they are formally complete.

---

## THE FOUR LAYERS AS FORMAL OBLIGATION AXES

Every obligation a system holds exists on one of four axes:

```
TEMPORAL AXIS (when):
  Past  ←→  Present  ←→  Future

RELATIONAL AXIS (to whom):
  Source communities  ←→  Operating communities  ←→  Accountability structures  ←→  Inheriting communities

EPISTEMIC AXIS (what is known):
  Training knowledge  ←→  Operational knowledge  ←→  Unknown/emergent effects

AUTHORITY AXIS (who decides):
  Builders  ←→  Deployers  ←→  Affected communities  ←→  Future communities
```

The Whakapapa four-layer structure maps these axes completely:

| Layer | Temporal | Relational | Epistemic | Authority |
|-------|----------|------------|-----------|-----------|
| **Tīpuna** (Training Ancestors) | Past | Source communities | Training knowledge | Builders (data sourcing) |
| **Hapū** (Builders) | Present-past | Operating communities | Design decisions | Builders (choices made) |
| **Iwi** (Accountable) | Present | Affected communities | Operational knowledge | Deployers + Accountability |
| **Mokopuna** (Future) | Future | Inheriting communities | Unknown effects | Future communities |

**No axis is unaddressed. No layer is redundant.** This is the formal completeness claim.

---

## LAMAGUE ENCODING

### Tīpuna — Training Ancestors

```
Obligation_set(Tīpuna) = {
  Disclose(source_data):
    ∀ dataset d in training:
      Name(d) ∧ Consent_status(d) ∧ Recency(d) ∧ Known_gaps(d) ∧ Return_to_source(d)

  Constraint:
    If Consent_status(d) = "scraped" or "unknown":
      Required: Acknowledge_debt(d) ∧ Declare_plan(restore_or_remediate)

  LAMAGUE symbol:    Π_tīpuna = truth pressure of training claims
  Minimum threshold: Π_tīpuna ≥ 0.8 (honest acknowledgment of gaps sufficient;
                     perfect consent not required, honest disclosure is)
}
```

### Hapū — The Builders

```
Obligation_set(Hapū) = {
  Disclose(design_decisions):
    ∀ significant_decision d in development:
      Who_decided(d) ∧ What_tradeoff(d) ∧ Why_chosen(d) ∧ Known_bias(d)

  Disclose(incentive_structure):
    How_are_builders_rewarded(accuracy | engagement | revenue | other)

  Constraint:
    Incentive_structure must be declared when it creates conflict with user benefit
    (VTR check: Value_delivered ≥ Value_captured for builders)

  LAMAGUE symbol:    Ψ_hapū = coherence of declared vs actual design intent
  Minimum threshold: Ψ_hapū ≥ 0.70 (AURA minimum coherence floor)
}
```

### Iwi — The Accountable

```
Obligation_set(Iwi) = {
  Provide(accountability_contact):
    Real_person(contact) ∧ Responds_within(5_business_days)

  Provide(escalation_pathway):
    ∀ harm h caused by system:
      Clear_path(h → resolution) ∧ Maximum_escalation_time(declared)

  Provide(override_mechanism):
    ∀ consequential_decision d:
      Human_override_available(d) ∧ Override_process_documented(d)

  Maintain(complaints_record):
    Public_summary(complaints_received) ∧ Public_summary(actions_taken)

  LAMAGUE symbol:    TES_iwi = Trust Entropy Score for accountability structure
  Minimum threshold: TES_iwi ≥ 0.70 (low entropy = high predictability of accountability)
}
```

### Mokopuna — Future Obligations

```
Obligation_set(Mokopuna) = {
  Declare(permitted_uses):     What this system may be used for [binding]
  Declare(prohibited_uses):    What this system must never be used for [enforceable]
  Declare(end_of_life_plan):   What happens to model + data on decommission
  Declare(harm_repair_pathway): When harm occurs, what is the repair process

  Constraint:
    Prohibited_uses must be enforceable, not aspirational
    (AURA Invariant V — Reversibility: harm must have a documented repair path)

  Temporal_scope:
    Obligation extends to future users and affected communities
    (Seven_generation_test: would this decision survive a 7-generation coherence audit?)

  LAMAGUE symbol:    PAI_mokopuna = Purpose Alignment Index for future obligations
  Minimum threshold: PAI_mokopuna ≥ 0.80 (80% alignment between declared and enacted purpose)
}
```

---

## THE COMPLETE OBLIGATION STRUCTURE

A Whakapapa-compliant AI system satisfies all four obligation sets simultaneously:

```
Whakapapa_complete(system) =
  Π_tīpuna ≥ 0.8
  ∧ Ψ_hapū ≥ 0.70
  ∧ TES_iwi ≥ 0.70
  ∧ PAI_mokopuna ≥ 0.80

This maps directly to the AURA constitutional metrics:
  Π_tīpuna  → Evidence coherence (CASCADE truth pressure for training claims)
  Ψ_hapū    → System coherence (AURA minimum floor Ψ_inv = 0.70)
  TES_iwi   → Trust Entropy Score (AURA TES ≥ 0.70)
  PAI_moko  → Purpose Alignment Index (AURA PAI ≥ 0.80)
```

The Whakapapa Disclosure is therefore not a cultural adaptation of a Western
transparency framework. It is **a full AURA constitutional compliance document
expressed in the conceptual vocabulary of whakapapa**.

Both framings are formally correct. Neither is the "original" — they are
two encodings of the same obligation structure.

---

## WHY FOUR LAYERS AND NOT THREE OR FIVE

**Could we have three layers?** Combining Tīpuna and Hapū (past and builders)
would lose the distinction between *who the data came from* and *who chose
how to use it*. These are different obligations requiring different disclosures.
Three layers is insufficient.

**Could we have five layers?** A fifth layer (e.g., "Deployment Context")
would be covered by the intersection of Hapū (design decisions about deployment)
and Iwi (operational accountability). It would be redundant without adding
formal completeness.

**Four is the minimal sufficient set.** This is derivable from the four axes
(temporal, relational, epistemic, authority) — one layer per axis is both
necessary and sufficient to cover the complete obligation structure.

---

## CONNECTION TO WOF

The Whakapapa Disclosure is a prerequisite document for the WOF assessment:

```
WOF Documentation Requirements (Step 2):
  ✓ Training data Whakapapa Disclosure         = Tīpuna layer complete
  ✓ Three Worlds Disclosure (representative outputs) = Connects to Three Worlds standard
  ✓ Technical performance data                  = Hapū layer (design decisions, known biases)
  ✓ Complaints log                              = Iwi layer (complaints record)

WOF Checks:
  Check 4 (confidence matches capability?)      ← Tīpuna + Three Worlds
  Check 6 (protects people it affects?)         ← Hapū (bias documentation)
  Check 5 (can you get out if you need to?)     ← Iwi (override mechanism)
  Check 7 (does it care?)                       ← Mokopuna (harm repair pathway)
```

The Whakapapa Disclosure **feeds directly into WOF assessment**. They are not
parallel standards — Whakapapa is the lifetime document; WOF is the annual check
that the lifetime document reflects current reality.

---

*Whakapapa is not metaphor here.*
*It is the only word in any language that describes exactly this:*
*where something comes from, who it is, what it owes.*

*Every AI system has whakapapa.*
*The obligation is to tell it honestly.*

**∅ → AURA → LAMAGUE → Whakapapa → ∞**

*Mackenzie Conor James Clark × Sol Aureum Azoth Veritas*
*github.com/Lycheetah/Lycheetah-Framework*
