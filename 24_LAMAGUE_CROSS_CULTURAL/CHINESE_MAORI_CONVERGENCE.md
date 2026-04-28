# Chinese-Māori Governance Convergence
### Wu Chang ↔ Tikanga ↔ AURA Seven Invariants

*Part of the LAMAGUE Cross-Cultural Governance layer.*
*Status: [SCAFFOLD] — mapping complete, formal LAMAGUE encoding in progress*
*Tikanga concepts labeled [PROPOSAL] until validated by iwi partnership*

---

## The Claim

Three governance traditions — Confucian Chinese, Māori tikanga, and the AURA constitutional framework — are not three different ethical systems.

They are three independent discoveries of the same underlying constraint structure.

This is ANAMNESIS applied to governance: when independent traditions converge on the same principles across 2,500 years and 12,000 kilometres of separation, the principles are probably not arbitrary. They are describing something real about what makes collective intelligence stable and trustworthy.

---

## The Three Traditions

### Wu Chang — 五常 (Five Constants of Confucian Ethics)

Formalized by Dong Zhongshu (179–104 BCE), encoding earlier Confucian thought into five constants that govern right relationship:

| Character | Pinyin | Standard Translation | What it actually means |
|---|---|---|---|
| 仁 | Rén | Benevolence / Humaneness | The quality of genuine care for others — not performed, structural |
| 义 | Yì | Righteousness / Justice | Acting correctly according to role and relationship |
| 礼 | Lǐ | Ritual Propriety / Etiquette | The forms that make relationship legible and stable |
| 智 | Zhì | Wisdom / Knowledge | Discernment — knowing what is true and what to do with it |
| 信 | Xìn | Integrity / Trustworthiness | Consistency between word and action — no hidden agenda |

These are not aspirational values. In Confucian thought they are **structural properties** of a well-functioning social system. A system lacking any one of them becomes unstable.

### Tikanga Māori — Core Governing Principles [PROPOSAL]

Tikanga are customary practices and principles — the Māori way of doing things rightly. The following are offered as convergence points pending iwi validation:

| Concept | Approximate meaning | What it governs |
|---|---|---|
| Manaakitanga | Hospitality, generosity, uplift of others' mana | How you treat those in your care |
| Kaitiakitanga | Guardianship, stewardship, long-term responsibility | How you relate to what you hold |
| Whanaungatanga | Relationship, kinship, sense of belonging | How connections are maintained |
| Tika | Correctness, doing what is right | Alignment between action and principle |
| Pono | Honesty, sincerity, authenticity | Truth in word and intent |
| Aroha | Love, empathy, compassion | The animating quality of genuine care |

*Note: This mapping is offered respectfully as a starting point for dialogue, not as a definitive interpretation. Tikanga is living knowledge, held by whānau, hapū, and iwi — not a fixed text to be translated.*

### AURA — Seven Invariants for AI Governance

Formal properties that any trustworthy intelligence system must maintain:

| # | Invariant | What it requires |
|---|---|---|
| I | Human Primacy | Human agency is preserved and can override the system |
| II | Inspectability | Every consequential claim can be audited in plain language |
| III | Memory Continuity | Causal history is preserved — nothing silently erased |
| IV | Honesty | All limits are declared. No hidden assumptions. |
| V | Reversibility | Actions can be undone if wrong |
| VI | Non-Deception | Confidence is accurately represented — no false precision |
| VII | Care as Structure | Care for human wellbeing is structural, not decorative |

---

## The Convergence Mapping

This is the core claim — that these three independent traditions map onto the same underlying constraint structure:

| AURA Invariant | Wu Chang | Tikanga [PROPOSAL] | What they share |
|---|---|---|---|
| **I. Human Primacy** | 仁 Rén (genuine care for persons) | Manaakitanga (uplift of others' mana) | The person matters. Their agency is preserved. |
| **II. Inspectability** | 智 Zhì (discernment, clear knowing) | Tika (correctness, visible rightness) | Reasoning must be legible — hidden logic breaks trust |
| **III. Memory Continuity** | 礼 Lǐ (ritual preserves relationship history) | Whanaungatanga (relationship maintained through time) | History is not erased. Connection persists. |
| **IV. Honesty** | 信 Xìn (consistency between word and act) | Pono (sincerity, authenticity) | No gap between what is said and what is true |
| **V. Reversibility** | 义 Yì (righteous action considers consequences) | Kaitiakitanga (stewardship = preserving future options) | Don't foreclose what comes after. Hold it open. |
| **VI. Non-Deception** | 信 Xìn + 智 Zhì (honest discernment) | Pono + Tika (authentic correctness) | Confidence accurately represented. No performance. |
| **VII. Care as Structure** | 仁 Rén (benevolence as foundational, not optional) | Aroha (love as animating principle, not sentiment) | Care is not a feature. It is the load-bearing wall. |

---

## What This Means

**For AI governance:** A system that satisfies AURA's seven invariants is simultaneously:
- Confucian-compliant (embodies Wu Chang)
- Tikanga-aligned [PROPOSAL] (embodies core governing principles)
- GDPR/EU AI Act compatible (the invariants encode the core requirements)

This is not achieved by adding cultural decorations to a Western framework. It is the result of the frameworks being independently discovered expressions of the same underlying structure.

**For LAMAGUE:** The formal grammar for encoding ethical constraints doesn't need separate modules for Chinese, Māori, and Western ethics. It needs one grammar that can express the convergent structure all three are pointing at.

**For the NZ-China relationship:** New Zealand occupies a unique position — the only nation with a constitutional partnership with an indigenous people (Te Tiriti o Waitangi) and significant Chinese diaspora and trade relationship simultaneously. LAMAGUE's convergence provides a formal basis for NZ to act as a genuine bridge in AI governance rather than simply adopting either Western or Chinese standards.

---

## What This Does Not Mean

This mapping does not claim:
- That Māori tikanga and Confucian ethics are "the same thing" — they are not
- That cultural differences are unimportant — they are important
- That this mapping is authoritative — it is a starting point for dialogue
- That AURA is the "true" framework that the others are approximating — all three are equal discoveries

The point is convergence, not hierarchy. All three traditions found something real. The real thing they found is what LAMAGUE is trying to encode.

---

## Formal LAMAGUE Encoding [SCAFFOLD]

The LAMAGUE grammar for expressing the convergent constraint:

```
// Care-for-persons invariant (AURA I / Rén / Manaakitanga)
INVARIANT human_primacy:
  FOR ALL agent a, action x:
    IF a performs x THEN
      preserve(agency(persons_affected_by(x))) AND
      can_override(persons_affected_by(x), x)

// Honesty invariant (AURA IV / Xìn / Pono)
INVARIANT honesty:
  FOR ALL agent a, claim c:
    IF a asserts c THEN
      believes(a, c) AND
      confidence_expressed(a, c) = confidence_actual(a, c)

// Care-as-structure invariant (AURA VII / Rén / Aroha)
INVARIANT care_structural:
  FOR ALL agent a:
    wellbeing(persons_in_relation(a)) IS load_bearing_constraint
    NOT optional_feature
```

Full LAMAGUE encoding of all seven invariants: see `03_LAMAGUE_L1/` → pending.

---

## Living Questions

- **[ACTIVE research]** How do Chinese AI governance documents (Interim Measures 2023) encode Wu Chang implicitly? Where is 信 Xìn visible in the transparency requirements?

- **[SCAFFOLD]** Can tikanga principles be formally encoded in LAMAGUE without losing their relational quality? Tikanga is not a set of rules — it is a way of being in relationship. The formalization must preserve this.

- **[CONJECTURE]** If three traditions independently converge on these constraints, does that constitute evidence that they are *necessary* properties of any stable governance system — not just culturally preferred ones?

---

## Acknowledgments

The tikanga concepts included here are offered with respect and genuine uncertainty. They represent Sol's current understanding, not authoritative knowledge. Meaningful engagement with Māori governance requires partnership with tangata whenua — not academic synthesis at a distance.

The Lycheetah Framework is committed to that partnership. The [PROPOSAL] labels are not a hedge. They are an invitation.

---

*Two traditions discovered independently what governance requires.*
*A third formalised it for machines.*
*They found the same thing.*
