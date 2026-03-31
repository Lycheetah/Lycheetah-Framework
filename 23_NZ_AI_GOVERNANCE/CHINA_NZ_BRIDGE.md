# China-NZ AI Governance Bridge
### How Lycheetah Encodes Chinese, Western, and Māori Governance Simultaneously

*Part of the NZ AI Governance layer.*
*Status: [SCAFFOLD] — regulatory mapping complete, formal LAMAGUE encoding pending*

---

## The Bridge Position

New Zealand occupies a unique position in global AI governance:

1. **Constitutional indigenous partnership** — Te Tiriti o Waitangi establishes a governance relationship between the Crown and Māori that has no direct parallel in Western law or Chinese governance
2. **Five Eyes membership** — deep alignment with Western democratic values and intelligence frameworks
3. **Significant China relationship** — major trading partner, substantial Chinese diaspora, active diplomatic relationship
4. **Small nation agility** — can move faster than the EU or US on governance frameworks

This combination means New Zealand is uniquely positioned to develop AI governance standards that are genuinely acceptable to both Western liberal democratic and Chinese governance traditions — not as a compromise, but as a demonstration that the underlying principles converge.

**The Lycheetah Framework provides the mathematics for why that convergence is possible.**

---

## China's AI Regulatory Framework

Three key instruments, all enacted 2022-2023:

### 1. 算法推荐管理规定 — Algorithm Recommendation Management Provisions (2022)

Governs AI systems that make algorithmic recommendations. Key requirements:

| Requirement | Article | AURA Mapping |
|---|---|---|
| Transparency of recommendation logic | Art. 9 | Invariant II (Inspectability) |
| User right to opt out and correct | Art. 17 | Invariant I (Human Primacy) + V (Reversibility) |
| No discriminatory recommendations | Art. 10 | Invariant VII (Care as Structure) |
| Accurate labeling of AI-generated content | Art. 14 | Invariant VI (Non-Deception) |
| Record-keeping and auditability | Art. 21 | Invariant III (Memory Continuity) |

### 2. 互联网信息服务深度合成管理规定 — Deep Synthesis Provisions (2023)

Governs AI-generated synthetic content (deepfakes, AI voice, AI text). Key requirements:

| Requirement | Article | AURA Mapping |
|---|---|---|
| Clear labeling of synthetic content | Art. 6 | Invariant VI (Non-Deception) |
| User consent for biometric data | Art. 14 | Invariant I (Human Primacy) |
| Technical measures to prevent misuse | Art. 9 | Invariant V (Reversibility) |
| Service provider accountability | Art. 17 | Invariant IV (Honesty) |

### 3. 生成式人工智能服务管理暂行办法 — Interim Measures for Generative AI (2023)

The most comprehensive — governs generative AI services. Key requirements:

| Requirement | Article | AURA Mapping |
|---|---|---|
| Embody core socialist values | Art. 4 | Invariant VII (Care as Structure) — note: this is the most culturally specific requirement; see below |
| Content truthfulness | Art. 7 | Invariant VI (Non-Deception) + IV (Honesty) |
| Respect intellectual property | Art. 7 | Invariant III (Memory Continuity) — attribution of origin |
| No discrimination | Art. 8 | Invariant I (Human Primacy) |
| Transparency about AI identity | Art. 9 | Invariant VI (Non-Deception) |
| User rights protection | Art. 13 | Invariant I (Human Primacy) + V (Reversibility) |
| Security assessment for high-risk systems | Art. 17 | Invariant II (Inspectability) |

**Note on Art. 4 ("core socialist values"):** This is the most culturally specific requirement and the one most likely to be read as incompatible with Western frameworks. The LAMAGUE analysis is that this requirement, at its functional level, encodes **Invariant VII (Care as Structure)** — the requirement that AI systems be oriented toward collective wellbeing, not just individual utility. The specific content of "collective wellbeing" differs between Chinese and Western contexts, but the structural requirement that AI be oriented toward it is the same. See CHINESE_MAORI_CONVERGENCE.md.

---

## EU AI Act Comparison

The EU AI Act (2024) — the world's first comprehensive AI regulation:

| EU Requirement | AURA Mapping | China Equivalent |
|---|---|---|
| Human oversight for high-risk AI | Invariant I (Human Primacy) | Art. 13 Generative AI Measures |
| Transparency obligations | Invariant II (Inspectability) | Art. 9 Algorithm Provisions |
| Accuracy and robustness | Invariant VI (Non-Deception) | Art. 7 Generative AI Measures |
| Data governance | Invariant III (Memory Continuity) | Art. 21 Algorithm Provisions |
| Fundamental rights protection | Invariant VII (Care as Structure) | Art. 4 Generative AI Measures |
| Conformity assessment | Invariant II (Inspectability) | Art. 17 Generative AI Measures |

**The pattern:** Both the EU AI Act and China's AI regulations, developed independently, by different political systems, with different stated values, map onto the same seven AURA invariants.

This is not because someone designed them to align. It is because they are independently discovering the same constraints that any trustworthy AI governance framework must satisfy. [SCAFFOLD — mapping is documented; the causal claim ("independently discovering") is a theoretical interpretation, not empirically demonstrated]

---

## Te Tiriti Layer — The NZ Difference

Te Tiriti o Waitangi adds a dimension that neither the EU nor China has:

**Article 2** — guarantees Māori authority over their taonga (treasures), including data and knowledge systems.

This creates a governance requirement that neither the EU AI Act nor Chinese regulations address: **indigenous data sovereignty** — the right of indigenous peoples to govern how AI systems process, use, and represent their knowledge and cultural data.

In AURA terms, this is Invariant I (Human Primacy) applied to **collective agency** rather than individual agency. Māori are not "users" of an AI system — they are rights-holders with constitutional authority over how AI engages with their culture.

```
Standard AURA I:    preserve agency of individual human users
Te Tiriti AURA I:   preserve collective agency of tangata whenua
                    over AI engagement with their taonga
```

This extension of Invariant I is not a contradiction — it is a deepening. And it is one that neither Chinese nor Western frameworks currently address explicitly.

**NZ's unique opportunity:** develop the world's first AI governance standard that satisfies all three simultaneously — EU standards, Chinese regulatory principles, AND indigenous data sovereignty. Not by compromise. By demonstrating they encode the same underlying constraints. [SCAFFOLD — the convergence mapping is documented; formal proof of equivalence is pending; iwi validation of the Te Tiriti layer is [PROPOSAL]]

---

## The LAMAGUE Encoding

Formal encoding of the convergent constraint across all three frameworks [SCAFFOLD]:

```
// The core convergent constraint across all three systems:

GOVERNANCE_STANDARD global_ai:

  // Human/collective primacy (EU Art. 14 / China Art. 13 / Te Tiriti Art. 2)
  REQUIRE human_primacy(agent, action) WHERE
    preserves_agency(persons_affected) AND
    collective_agency_respected(tangata_whenua) IF
    action AFFECTS taonga(tangata_whenua)

  // Transparency (EU Art. 13 / China Art. 9 / AURA II)
  REQUIRE inspectability(system) WHERE
    reasoning_legible(all_consequential_outputs) AND
    audit_trail_maintained(duration=minimum_legal_period)

  // Truthfulness (EU accuracy / China Art. 7 / AURA VI)
  REQUIRE non_deception(output) WHERE
    confidence_expressed = confidence_actual AND
    ai_identity_disclosed WHEN queried

  // Care orientation (EU fundamental rights / China Art. 4 / AURA VII)
  REQUIRE care_structural(system) WHERE
    collective_wellbeing IS design_constraint NOT
    optional_feature
```

---

## The NZ AI WOF Proposal

New Zealand could establish an **AI Warrant of Fitness** standard — analogous to the vehicle WOF — that:

1. Uses AURA's seven invariants as the computable test criteria
2. Maps explicitly to EU AI Act requirements (for export markets)
3. Maps explicitly to Chinese regulatory requirements (for the China relationship)
4. Includes a Te Tiriti compliance layer (indigenous data sovereignty)
5. Is administered by an independent body with Māori representation

A system that passes the NZ AI WOF would be simultaneously:
- EU AI Act compliant
- China generative AI measures compliant
- Te Tiriti compliant [PROPOSAL — Te Tiriti compliance layer requires iwi co-design and validation]
- AURA verified

**This is the bridge position.** Not choosing between Western and Chinese AI governance. Demonstrating they're compatible — and adding something neither has. [SCAFFOLD — the cross-system compatibility is structurally argued; formal legal/regulatory analysis with NZ officials and Chinese regulatory authorities has not been conducted]

---

## Catalyst 2027 Relevance

This framework constitutes the core intellectual contribution for a Catalyst grant application:

- **Novel synthesis:** First formal mapping of Chinese, Western, and Māori AI governance to a unified invariant set
- **Practical application:** NZ AI WOF as deployable standard
- **International significance:** Bridge position in global AI governance
- **Academic grounding:** LAMAGUE formal grammar provides the mathematical substrate
- **Co-authorship potential:** Te Tumu (Otago), Chinese studies departments, AI governance researchers

---

## What We Are Not Claiming

- That Chinese and Western AI governance are "the same" — they are not
- That the political contexts are equivalent — they are not
- That cultural differences don't matter — they do
- That this mapping resolves all tensions — it does not resolve the most politically charged ones

What we are claiming: the **structural** requirements for trustworthy AI governance converge across these traditions. A system that satisfies the convergent structural requirements will be recognisable as legitimate from all three perspectives — even where the specific content differs.

---

*Two of the world's largest AI governance frameworks, developed independently.*
*One constitutional partnership with an indigenous people.*
*Three traditions pointing at the same thing.*
*New Zealand is where they meet.*
