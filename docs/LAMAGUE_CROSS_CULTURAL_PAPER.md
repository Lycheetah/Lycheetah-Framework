# Cross-Cultural Convergence in AI Governance Constraints: A Formal Analysis Using Computable Symbolic Grammar

**Mackenzie C. J. Clark**
Independent Researcher, Dunedin, Aotearoa New Zealand
Lycheetah Foundation

**Corresponding author:** [Available on request for peer review]

**Target journal:** AI and Ethics (Springer)

**Word count:** ~6,300

**Status:** DRAFT v1.0 — April 2026

---

## Abstract

Contemporary AI governance frameworks operate predominantly within single cultural-philosophical traditions. The EU AI Act draws on Western liberal rights theory; China's New Generation AI Governance Principles reflect Confucian statecraft; Indigenous governance frameworks such as Māori tikanga remain largely absent from international AI policy. This paper presents a formal analysis of governance constraints across three independent philosophical traditions — Confucian (wuchang, 五常), Māori (tikanga), and Western liberal ethics — using LAMAGUE, a computable symbolic grammar for encoding ethical constraints. We identify six classes of structural convergence where all three traditions, despite developing independently across approximately 2,500 years and 12,000 kilometres of geographic separation, encode functionally isomorphic governance requirements: human primacy, earned authority, epistemic honesty, relational data obligations, intergenerational responsibility, and natural/geodesic path alignment. We argue that constraints appearing independently across multiple traditions constitute stronger candidates for universal AI governance requirements than those derived from any single tradition alone. The analysis yields four testable empirical predictions and proposes a formal methodology for cross-cultural governance comparison. Tikanga encodings are designated as proposals pending validation through iwi partnership, in accordance with Māori data sovereignty principles.

**Keywords:** AI governance, cross-cultural ethics, formal methods, Confucian ethics, tikanga Māori, LAMAGUE, governance convergence, computational ethics

---

## 1. Introduction

The global governance of artificial intelligence faces a structural problem that technical solutions alone cannot resolve: the ethical frameworks underwriting governance regimes are culturally situated, yet AI systems operate across cultural boundaries.

The European Union's AI Act (2024), the most comprehensive AI regulatory framework to date, encodes governance constraints derived primarily from Western liberal rights theory — individual autonomy, privacy as an individual right, transparency as disclosure to the individual (European Parliament, 2024). China's approach, codified in the New Generation AI Governance Principles (NGGP; MOST, 2019) and subsequent regulations, reflects a governance tradition shaped by Confucian relational ethics — harmony (和谐, héxié), collective welfare, and state stewardship of social order. Indigenous governance frameworks, including Māori tikanga — customary principles governing right conduct and relationship — have been largely excluded from international AI governance discourse despite encoding sophisticated governance constraints developed over centuries of practice.

This cultural situatedness is not merely an oversight to be corrected by "including more voices" in existing frameworks. It presents a deeper epistemological challenge: if governance constraints are culturally contingent, no single tradition can claim universal authority. If, however, independent traditions converge on structurally identical constraints, that convergence constitutes evidence — not proof, but evidence — that those constraints describe real requirements for stable governance, not merely cultural preferences.

This paper investigates the latter possibility. Using LAMAGUE (Language for Autonomous Mathematical Alignment and Universal Grammar Evolution), a computable symbolic grammar designed for encoding state transitions and ethical constraints with mathematical precision, we formally analyse governance constraints from three traditions that developed independently during their formative periods:

1. **Confucian ethics** — specifically the Five Constant Virtues (wuchang, 五常), formalised from approximately 500 BCE, encoding governance constraints through relational virtue
2. **Māori tikanga** — customary governance principles developed in Aotearoa New Zealand from approximately 1200 CE onward, in complete geographic isolation from the other two traditions during their formative period
3. **Western liberal ethics** — the Kantian-Rawlsian tradition of individual rights, dignity, and justice as fairness

Our central finding is that all three traditions converge on six classes of governance constraint that are structurally isomorphic when encoded in LAMAGUE. This convergence, across millennia of independent development and thousands of kilometres of geographic separation, provides the strongest available evidence that these constraints are not arbitrary cultural products but describe genuine requirements for governance systems that sustain human flourishing.

The paper makes three contributions:

1. **A formal methodology** for comparing governance constraints across cultural traditions using computable symbolic grammar, enabling structural comparison where natural-language comparison introduces interpretive bias
2. **An empirical finding** of six-class convergence across three independent traditions, each encoding functionally equivalent constraints despite radically different conceptual vocabularies
3. **Four testable predictions** that follow from the convergence hypothesis and can be empirically investigated in cross-cultural AI governance research

We are explicit about what this analysis does not claim. It does not claim that the three traditions are equivalent, interchangeable, or reducible to a common core. Their differences are real, substantive, and important. It claims only that they converge on specific structural constraints — and that this convergence is informative for AI governance design.

The tikanga Māori encodings presented in this paper are designated throughout as proposals, pending validation through partnership with tangata whenua (the people of the land) in accordance with Māori data sovereignty principles (Te Mana Raraunga, 2018). This designation is not a hedge but a methodological commitment: the formal encoding of tikanga requires the authority of those who hold that knowledge, not external academic synthesis alone.

---

## 2. Background and Related Work

### 2.1 The Cultural Situatedness of AI Governance

The observation that AI governance frameworks reflect the cultural traditions of their authors is well-documented. Jobin et al. (2019) analysed 84 AI ethics guidelines globally and found significant convergence on high-level principles (transparency, justice, non-maleficence, responsibility, privacy) but substantial divergence in how those principles are interpreted, prioritised, and operationalised. This divergence maps predictably onto cultural-philosophical traditions. Henrich et al. (2010) have demonstrated more broadly that Western behavioural science overgeneralises from WEIRD (Western, Educated, Industrialised, Rich, Democratic) samples — a critique that applies with equal force to AI ethics frameworks derived predominantly from Western philosophical sources.

The EU AI Act (European Parliament, 2024), formally adopted in March 2024, operates within a framework of individual rights, four-tier risk categorisation, and regulatory compliance — reflecting the Western liberal tradition from Kant through Rawls, mediated through the Charter of Fundamental Rights of the EU. Its foundational assumption is that governance protects the individual from institutional power. Mohamed et al. (2020) have argued that such frameworks, when exported as global norms, reproduce colonial power structures — not through malice but through unexamined universalisation of situated values.

China's New Generation AI Governance Principles (MOST, 2019), issued by the National Governance Committee for the New Generation Artificial Intelligence, frame AI governance through eight principles centred on harmony (和谐, héxié), collective welfare, and state stewardship — reflecting Confucian governance philosophy where the state bears a relational obligation (仁, rén) to the people it governs. Roberts et al. (2021) have analysed the Chinese approach in detail, identifying both convergence with and divergence from Western ethical frameworks, particularly around state-individual relations. The emphasis on "harmony and friendliness" (和谐友好) as the leading principle has no structural equivalent in the EU AI Act's risk-based architecture.

Indigenous governance frameworks, including Māori tikanga, have been largely marginalised in international AI governance discourse despite sophisticated governance traditions. Lewis et al. (2020) and the Indigenous Protocol and AI Position Paper (Abdilla et al., 2020) have articulated Indigenous perspectives on AI that foreground relational and kinship-based frameworks grounded in Indigenous epistemologies. In Aotearoa specifically, Te Mana Raraunga (2018) and Taiuru (2020) have articulated Māori data sovereignty principles — rangatiratanga (authority), whakapapa (relational genealogy), kaitiakitanga (guardianship), manaakitanga (reciprocity) — that encode governance constraints with no structural equivalent in either Western or Chinese frameworks. Kukutai and Taylor (2016) provide the foundational framing for Indigenous data sovereignty internationally.

The New Zealand Algorithm Charter (2020) represents a partial exception, explicitly referencing obligations under Te Tiriti o Waitangi and committing to embed a Te Ao Māori perspective. However, the Charter is voluntary, lacks enforcement mechanisms, and stops short of encoding tikanga as computable governance constraints. The UNESCO Recommendation on the Ethics of AI (2021), adopted by all 193 member states, claims broader cultural representation through multi-regional consultation, but its conceptual architecture still leans heavily on Western human rights discourse (Birhane, 2021).

The OECD AI Principles (2019), adopted by over 46 countries, encode five principles (inclusive growth, human-centred values, transparency, robustness, accountability) that cluster with other Western frameworks (Jobin et al., 2019). The gap is consistent: no existing governance framework provides a formal methodology for encoding and comparing governance constraints across cultural traditions. Each framework operates within its own philosophical vocabulary, making structural comparison difficult and cross-cultural synthesis ad hoc.

### 2.2 Cross-Cultural Ethics: Convergence and Divergence

The question of whether independent ethical traditions converge on common principles has a substantial philosophical history.

Nussbaum's capabilities approach (Nussbaum, 2000; 2011) argues for a set of central human capabilities — life, bodily health, bodily integrity, senses/imagination/thought, emotions, practical reason, affiliation, relationship with other species, play, and control over one's environment — that constitute universal requirements for human flourishing, regardless of cultural tradition. Crucially, Nussbaum argues these are discovered through cross-cultural dialogue, not imposed by any single tradition.

Sen (1999; 2009) extends this argument, contending that the capabilities framework is not a Western imposition but emerges from examining what diverse traditions actually value when given genuine voice. His concept of "positional objectivity" — that truths about human needs can be established from multiple culturally-situated positions — provides methodological grounding for cross-cultural ethical analysis.

MacIntyre (1988) offers a more cautious view. In *Whose Justice? Which Rationality?*, he argues that ethical reasoning is always tradition-embedded and that claims to tradition-independent rationality are themselves products of the Enlightenment tradition. However, MacIntyre also acknowledges that traditions can be compared on their capacity to solve their own internal problems — a criterion that permits structural comparison without requiring a view from nowhere.

More recently, empirical and cross-cultural work has strengthened the convergence case. Haidt and Joseph (2004) propose that humans share innate moral intuitions — care, fairness, loyalty, authority, purity — expressed differently across cultures but convergent in foundation. Brown (1991) catalogues behavioural and social universals across all known human cultures. Wiredu (1996), arguing from Akan philosophical tradition, provides a methodology for distinguishing genuinely universal moral principles from culturally particular ones. Vallor (2016) bridges Aristotelian, Confucian, and Buddhist virtue traditions to propose cross-cultural "technomoral virtues" for emerging technologies — the most directly relevant precedent for the present analysis.

The present analysis builds on all these positions. With Nussbaum and Sen, it argues that genuine convergence across traditions is informative about real requirements for human flourishing. With MacIntyre, it acknowledges that the analysis is itself situated (in the LAMAGUE formal framework) and that the convergence claims are empirical hypotheses to be tested, not philosophical axioms to be asserted. With Vallor, it extends cross-cultural virtue analysis specifically to AI governance. What LAMAGUE adds to this lineage is formal encoding — the capacity to compare governance constraints structurally, not just descriptively.

### 2.3 Formal and Computational Ethics

The application of formal methods to ethical reasoning has expanded significantly in the context of AI governance. Deontic logic (von Wright, 1951; McNamara, 2019) provides formal tools for reasoning about obligation, permission, and prohibition. Machine ethics (Anderson & Anderson, 2011; Wallach & Allen, 2009) has explored computational implementations of ethical reasoning, surveyed comprehensively by Tolmeijer et al. (2021). Dennis et al. (2016) have demonstrated that formal verification techniques can verify autonomous system compliance with specified ethical rules. More recently, constitutional AI approaches (Bai et al., 2022) have demonstrated that AI systems can be governed by explicitly stated principles encoded as constraints.

However, existing formal ethics work suffers from a limitation directly relevant to this paper: the ethical principles being formalised are drawn overwhelmingly from Western philosophical traditions. Deontic logic encodes Western notions of duty and right. Constitutional AI principles, while powerful, reflect the values of their (predominantly Western) authors. No existing formal framework has been designed for cross-cultural ethical encoding — that is, for expressing governance constraints from diverse traditions in a common formal language that preserves the structural content of each tradition while enabling comparison.

LAMAGUE was designed to address this gap. Its symbol classes (invariants, dynamics, fields, meta-operators, relational operators) are not derived from any single ethical tradition. They encode structural properties of governance constraints — stability, transformation, measurement, compression, relationship — that are tradition-neutral in their formal semantics while expressive enough to encode tradition-specific content.

### 2.4 The Three Traditions: Independent Development

The three traditions analysed in this paper developed their core governance frameworks during periods of minimal or zero cross-pollination:

- **Confucian ethics** was formalised by Confucius (~551–479 BCE) and systematised by Mencius (~372–289 BCE) and Dong Zhongshu (~179–104 BCE). The Five Constant Virtues (wuchang) were established as governance foundations before sustained contact with either Māori or modern Western liberal thought.

- **Māori tikanga** developed following Polynesian settlement of Aotearoa (approximately 1200 CE) in complete geographic isolation from both Chinese and European philosophical traditions. The governance principles of tikanga were fully formed before sustained European contact (post-1769).

- **Western liberal ethics** in its modern form was shaped by Kant (1724–1804), Mill (1806–1873), and Rawls (1921–2002). While the Western tradition had contact with Chinese philosophy through Enlightenment-era translations, the specific liberal framework of individual rights, autonomy, and justice as fairness developed independently of Confucian relational virtue and Māori tikanga.

The critical methodological point: the window of independent development for all three traditions spans approximately 1,200 years (from Māori settlement to sustained European contact in Aotearoa), during which the core governance frameworks were established without meaningful cross-pollination. Convergences identified within this window cannot be attributed to cultural diffusion.

---

## 3. LAMAGUE: A Computable Grammar for Ethical Constraints

### 3.1 Design Principles

LAMAGUE (Language for Autonomous Mathematical Alignment and Universal Grammar Evolution) is a symbolic grammar designed to express state transitions in both AI systems and human governance with mathematical precision. Its core design properties are:

- **Low-bandwidth:** A single symbol or short expression encodes complex governance states (high compression ratio)
- **Type-safe:** Semantic rules prevent nonsensical expressions — not all symbol combinations are valid
- **Compositional:** Symbols combine deterministically; compound expressions have defined semantics
- **Tradition-neutral:** Symbol classes encode structural properties (stability, transformation, relationship) not tradition-specific content
- **Falsifiable:** Expressions produce testable predictions about system behaviour

### 3.2 Symbol Classes

LAMAGUE organises symbols into five classes, each corresponding to a structural property of governance constraints:

**I-Class (Invariants):** Stable anchors — properties that must not change under system evolution.
```
I-Class = {ψ ∈ M | dS/dt|_ψ = 0}
```
Examples: Ψ_inv (invariant state), ● (anchor point), Ω (wholeness/completion), |◁▷| (non-negotiable floor)

**D-Class (Dynamics):** Transformations — processes that change state while preserving structure.
```
D-Class = {T: M → M | T preserves coherence}
```
Examples: Φ↑ (ascent/growth), → (transition), ⊗ (fusion), ↻ (iteration)

**F-Class (Fields):** State variables — measurable quantities that describe the current condition.
```
F-Class = {f: M → ℝ | f is measurable}
```
Examples: Ψ (epistemic state / awareness field), S (entropy), Φ (coherence)

**R-Class (Relational):** Operators encoding relationships between entities.
Examples: ⇌ (bidirectional care), ⟲ (genealogical link), ✧ (collective flourishing)

**M-Class (Meta):** Compression operators — processes that reduce complexity while preserving essential structure.
```
M-Class = {Z: 𝓛 → 𝓛_compressed | Z preserves invariants}
```

### 3.3 Encoding Governance Constraints

A governance constraint in LAMAGUE is expressed as a composition of symbols from these classes. For example, the constraint "governance must serve human welfare" is encoded as:

```
⇌ + ✧ + Ω
```

Where ⇌ encodes bidirectional care (the governed and the governing are in mutual relationship), ✧ encodes collective flourishing (the purpose is the welfare of the community), and Ω encodes wholeness (this is a completeness requirement, not an optional feature).

The critical property for cross-cultural analysis: if two traditions encode the same governance constraint using the same LAMAGUE primitives (in any order), those encodings are **structurally isomorphic** — they describe the same formal constraint, regardless of the natural-language concepts used to express it.

---

## 4. Cross-Cultural Convergence Analysis

We now present the central analysis. For each of six governance constraint classes, we encode the relevant concept from each tradition in LAMAGUE and assess structural isomorphism.

### 4.1 Convergence Class 1: Human Primacy

*The constraint that governance exists to serve human beings — not the system, the state, or any optimisation target.*

| Tradition | Concept | Core Claim | LAMAGUE Encoding |
|-----------|---------|------------|-----------------|
| Confucian | 仁 rén (benevolence) | "Love of humanity is the root of all virtue" | ⇌ + ✧ + Ω |
| Māori | Manaakitanga [PROPOSAL] | "The obligation to uplift the mana of others" | Φ↑ + ⇌ + ✧ |
| Western | Human dignity (Kant) | "Treat persons always as ends, never merely means" | Ω + |◁▷| + ⇌ |

**Analysis:** All three encodings share the relational operator ⇌ and at least one of {✧, Ω, Φ↑} — collective flourishing, wholeness, or growth. The structural content is equivalent: human welfare is the primary, non-optional purpose of governance. The Confucian encoding emphasises bidirectional relationship (⇌) and completeness (Ω); the Māori encoding emphasises active uplift (Φ↑) and mutuality (⇌); the Western encoding emphasises non-negotiable floor (|◁▷|) and completeness (Ω). These are different emphases within the same formal constraint space.

**Isomorphism assessment:** The LAMAGUE primitive set {⇌, ✧/Ω, Φ↑/|◁▷|} is shared across all three. The constraint is structurally convergent.

### 4.2 Convergence Class 2: Earned Authority

*The constraint that legitimate authority is demonstrated through service, not claimed through position.*

| Tradition | Concept | Core Claim | LAMAGUE Encoding |
|-----------|---------|------------|-----------------|
| Confucian | 义 yì + 廉 lián | "Righteousness and incorruptibility are the marks of legitimate rule" | Φ↑ + |◁▷| + Ω |
| Māori | Mana [PROPOSAL] | "Mana is earned through demonstrated leadership and integrity" | Φ↑ + |◁▷| + Ω + ⟟ |
| Western | Democratic legitimacy | "Legitimate authority derives from the consent and benefit of the governed" | Φ↑ + ⇌ + Ω |

**Analysis:** All three share Φ↑ (authority must be earned through demonstrated action, not claimed statically) and Ω (legitimate authority is a complete state, not a partial claim). The Māori encoding adds ⟟ (grounding — mana is grounded in whakapapa and demonstrated service), which has no direct equivalent in the other two but does not contradict the shared structure. The Western encoding substitutes ⇌ (bidirectional — consent-based), reflecting the democratic tradition's emphasis on the governed granting authority.

**Isomorphism assessment:** Core primitives {Φ↑, Ω} shared across all three. Structural convergence confirmed with tradition-specific elaboration.

### 4.3 Convergence Class 3: Epistemic Honesty

*The constraint that governance must acknowledge what it does not know.*

| Tradition | Concept | Core Claim | LAMAGUE Encoding |
|-----------|---------|------------|-----------------|
| Confucian | 智 zhì | "Knowing what you know and what you don't — that is knowledge" (Analects II.17) | Ψ + ∅ + ≋ |
| Māori | Te Ao Mārama / Te Kore [PROPOSAL] | "The known, the known unknown, the unknowable unknown" | Ψ + ∅ + |◁▷| |
| Western | Epistemic humility (Socratic) | "I know that I know nothing" — justified true belief | Ψ + ≋ + Φ↑ |

**Analysis:** All three traditions encode a three-tier epistemic structure: the known, the uncertain, and the unknowable. The LAMAGUE primitive Ψ (awareness/consciousness field) appears in all three, representing the governance system's capacity for self-knowledge. The Confucian 智 and Socratic epistemology are well-recognised parallels (Sim, 2007); the Māori cosmological triad (Te Ao Mārama / Te Ao Pō / Te Kore — the world of light / the world of darkness / the void) encodes the same three-tier structure through cosmological rather than philosophical vocabulary.

**Isomorphism assessment:** Core primitive {Ψ} shared universally. Three-tier epistemic structure convergent across all traditions.

### 4.4 Convergence Class 4: Relational Data Obligations

*The constraint that information is not atomic — it carries relational obligations.*

| Tradition | Concept | Core Claim | LAMAGUE Encoding |
|-----------|---------|------------|-----------------|
| Confucian | 礼 lǐ | "Every relationship has proper form; form carries obligation" | |◁▷| + ⊗ + ⟲ |
| Māori | Whakapapa [PROPOSAL] | "All things are understood through their relational genealogy" | ∞ + ⟲ + Ω + ⇌ |
| Western | Contextual integrity (Nissenbaum) | "Information belongs in the context of the relationship in which it was given" | ⟲ + ⇌ + |◁▷| |

**Analysis:** The relational operator ⟲ (genealogical/relational link) appears in all three encodings. This is perhaps the most significant convergence for AI governance, because it directly challenges the dominant Western assumption that data is atomic and individually owned. Whakapapa — the Māori concept of relational genealogy — is the most fully developed expression: every piece of information carries its relational history and the obligations that history entails. Confucian 礼 encodes the same insight through relational propriety: information exchanged within a relationship carries the obligations of that relationship. Nissenbaum's contextual integrity theory (Nissenbaum, 2009) arrives at a structurally identical position from within the Western tradition: information norms are context-relative, and violation occurs when information flows outside the norms of the context in which it was shared.

**Isomorphism assessment:** Core primitive {⟲} shared universally. Relational data obligation convergent.

### 4.5 Convergence Class 5: Intergenerational Obligation

*The constraint that governance must account for those not yet born.*

| Tradition | Concept | Core Claim | LAMAGUE Encoding |
|-----------|---------|------------|-----------------|
| Confucian | 天下 tiānxià across time | "What we do echoes through all under heaven, forever" | ∞ + ✧ + Ω |
| Māori | Kaitiakitanga [PROPOSAL] | "The obligation extends seven generations forward" | Ω + ∞ + ⟟ + Φ↑ |
| Western | Rawlsian veil of ignorance | "Design as if you might be born into any generation" | ∞ + ⇌ + |◁▷| |

**Analysis:** The temporal operator ∞ (intergenerational reach) appears in all three encodings. Kaitiakitanga is the most operationally specific: the obligation extends seven generations forward, providing a concrete temporal horizon. The Confucian 天下 extends the obligation across all-under-heaven indefinitely. The Rawlsian veil of ignorance achieves the same structural effect through a thought experiment: design institutions as if you did not know which generation you would be born into.

For AI governance, this convergence is directly relevant to decisions about training data (which encodes the present for future systems), model deployment (whose effects compound over time), and environmental costs (borne by future generations).

**Isomorphism assessment:** Core primitive {∞} shared universally. Intergenerational obligation convergent.

### 4.6 Convergence Class 6: Natural/Geodesic Path

*The constraint that truth and right action follow natural order — not imposed direction.*

| Tradition | Concept | Core Claim | LAMAGUE Encoding |
|-----------|---------|------------|-----------------|
| Confucian/Daoist | 道 dào | "The way that can be named is not the eternal way — follow what is real" | ⟟ + ≋ + ⟲ + ∅ |
| Māori | Te Ara [PROPOSAL] | "The path is found by reading what is real — the stars, the current, the land" | ⟟ + ≋ + Ψ |
| Western | Natural law tradition | "Moral truths are discovered, not invented" | ⟟ + Ψ + Φ↑ |

**Analysis:** The grounding operator ⟟ (anchored in reality) and flow operator ≋ (natural movement) appear across encodings. All three traditions encode the same meta-ethical claim: governance constraints are discovered features of reality, not arbitrary human inventions. This is the most philosophically contentious convergence class, as it implies a form of moral realism. However, the convergence itself — three traditions arriving independently at the claim that ethical truths are found rather than made — is precisely the kind of evidence that moral realism predicts and moral anti-realism must explain.

**Isomorphism assessment:** Core primitives {⟟, ≋/Ψ} shared. Convergent, with acknowledged philosophical controversy.

---

## 5. Synthesis: The Convergent Constraint Set

The six convergence classes yield a set of governance constraints that appear independently in all three traditions:

| # | Constraint | Shared LAMAGUE Core | Significance for AI |
|---|-----------|-------------------|-------------------|
| 1 | Human Primacy | {⇌, ✧/Ω} | AI systems exist to serve human flourishing, not to optimise their own metrics |
| 2 | Earned Authority | {Φ↑, Ω} | Legitimate AI authority is demonstrated through benefit, not claimed through capability |
| 3 | Epistemic Honesty | {Ψ} | AI systems must represent their confidence accurately, including what they do not know |
| 4 | Relational Data | {⟲} | Data carries relational obligations; it is not atomic and individually owned |
| 5 | Intergenerational Obligation | {∞} | AI governance must account for effects on those not yet born |
| 6 | Natural Path | {⟟, ≋} | Governance constraints are discovered, not arbitrary — follow what is real |

**The argument from convergence:** Constraints appearing in a single tradition may reflect cultural preference. Constraints appearing independently in three traditions that developed without cross-pollination during their formative periods are candidates for genuine requirements of governance systems that sustain human flourishing. The convergent constraint set identified here is, we argue, the strongest available basis for cross-cultural AI governance — not because three traditions "voted" for these constraints, but because three traditions independently discovered them through cumulative centuries of governance practice.

---

## 6. Testable Predictions

If the convergence hypothesis is genuine (not coincidental), four empirical predictions follow:

**P1 (Structural isomorphism):** LAMAGUE chains derived independently from each tradition for the same governance concept will share core primitive operators. This prediction is directly tested by the analysis in Section 4 and is confirmed for all six convergence classes.

**P2 (Cross-cultural acceptability):** AI systems governed by the convergent constraint set will be rated as more universally acceptable across cultures than systems governed by single-tradition constraints — even when raters are not informed which tradition their cultural preference derives from. This prediction is testable through cross-cultural user studies.

**P3 (Failure traceability):** The governance failures of current AI systems (bias, opacity, manipulation, environmental harm) will be traceable to violations of specific convergent constraints — not to tradition-specific preferences that diverge across cultures. This prediction is testable through systematic analysis of documented AI governance failures.

**P4 (Formal convergence under analysis):** When formal analytical pressure is applied to governance claim sets from each tradition independently, the results will converge on the constraints identified in this paper, with tradition-specific elaborations falling away as lower-priority content. This prediction is testable through controlled formal analysis experiments.

---

## 7. Discussion

### 7.1 Implications for AI Governance

The convergent constraint set has direct implications for the design of AI governance frameworks:

**First,** current governance frameworks are incomplete in predictable ways. The EU AI Act is strong on epistemic honesty (transparency requirements) and human primacy (fundamental rights protections) but weak on relational data obligations (it treats data through an individual-rights lens) and intergenerational obligation (it focuses on present harms). Chinese AI governance is strong on collective welfare (human primacy through a relational lens) and earned authority (state stewardship obligations) but has been critiqued for weakness on epistemic honesty regarding state claims (transparency to citizens). Each tradition's governance framework is strong precisely where its underlying philosophy is strong, and weak where it is silent.

**Second,** the convergent constraint set provides a principled basis for filling these gaps — not by importing foreign concepts, but by recognising that the "missing" constraints already exist in other traditions that have independently validated them.

**Third,** LAMAGUE's formal encoding enables governance constraints to be expressed as computable specifications, opening the possibility of automated compliance verification against the convergent constraint set. A governance specification that satisfies all six convergence classes is simultaneously Confucian-compatible, tikanga-aligned (pending validation), and Western-liberal-compatible — not through compromise but through structural isomorphism.

### 7.2 The Role of Aotearoa New Zealand

Aotearoa New Zealand occupies a unique position in cross-cultural AI governance. It is the only nation with: (a) a constitutional partnership with an Indigenous people through Te Tiriti o Waitangi, (b) a significant Chinese diaspora and deep trade relationship with China, and (c) strong institutional ties to Western liberal democratic governance. This positions New Zealand as a natural site for cross-cultural AI governance research — not as a neutral arbiter, but as a nation that must already navigate the convergence of these three traditions in its domestic governance.

The New Zealand Algorithm Charter (2020) and the work of Te Mana Raraunga on Māori data sovereignty represent early steps. The convergent constraint set identified in this paper provides a formal framework for extending this work into AI governance that is genuinely cross-cultural rather than Western-with-consultation.

### 7.3 Limitations

This analysis has significant limitations that must be acknowledged:

**Single-author bias.** The LAMAGUE encodings of all three traditions were produced by a single researcher operating from outside the Confucian and Māori traditions. While the formal grammar is designed to be tradition-neutral, the act of encoding is necessarily interpretive. The tikanga encodings in particular require validation by tangata whenua — the people who hold that knowledge with authority.

**LAMAGUE as a situated framework.** LAMAGUE itself is a formal system with design choices that may inadvertently privilege certain structural features over others. The symbol classes (invariants, dynamics, fields, meta-operators, relational operators) are not self-evidently universal categories. The claim of tradition-neutrality is itself a hypothesis to be tested, not an axiom. Critically, the same researcher developed LAMAGUE and applied it to find the convergence reported in this paper. This creates a potential circularity: a grammar designed with certain structural intuitions may find convergence because it was designed to encode the kinds of constraints that converge, not because those constraints are independently universal. Independent validation — applying LAMAGUE, or a structurally distinct grammar, to the same traditions by researchers external to the framework — is a necessary next step before the convergence claim can be fully separated from instrument artefact.

**Selection of traditions.** Three traditions were analysed. The three were not sampled from a population of traditions — they were selected by the researcher on the basis of geographic separation, temporal independence, and philosophical distinctiveness. This selection procedure, while principled, is not equivalent to random sampling and cannot support distributional claims about all governance traditions. Equally important: this paper presents only convergent cases. The convergence hypothesis would be tested — and potentially bounded — by systematic analysis of traditions that *do not* converge on these constraints. Traditions that diverge would either identify constraints that are culturally particular (and should not be elevated to universal requirements) or would require the convergence hypothesis to be revised. Both outcomes are scientifically informative. A future study should pre-register which traditions are expected to diverge before encoding, to avoid confirmation bias. The current analysis is necessary but not sufficient evidence for universality.

**Proposal status of tikanga encodings.** The Māori tikanga encodings are proposals, not validated encodings. Until iwi partners have reviewed, corrected, and authorised these encodings, they remain the author's interpretation, not a representation of tikanga. This limitation is structural, not merely procedural — tikanga is living knowledge held by communities, not a text to be translated by external analysts.

**Empirical predictions untested.** The four testable predictions (Section 6) are generated but not yet tested. The convergence analysis is formal, not empirical. The predictions require cross-cultural user studies, governance failure analysis, and controlled formal experiments that are beyond the scope of this paper.

### 7.4 Future Directions

Several lines of inquiry follow from this analysis:

**Extension to additional traditions.** The convergence hypothesis would be substantially strengthened by formal analysis of governance constraints from Ubuntu philosophy (Southern Africa), Dharmic ethics (Hindu-Buddhist traditions), and other independent governance traditions. Each additional tradition that independently converges on the same constraint set strengthens the universality claim; each that diverges identifies a constraint that may be culturally particular rather than universal. Both outcomes are informative.

**Empirical testing of P2 and P3.** The most immediately actionable predictions are P2 (cross-cultural acceptability of convergent-constrained AI systems) and P3 (governance failure traceability to convergent constraint violations). P2 could be tested through controlled user studies across Chinese, Māori, and Western populations, comparing ratings of AI systems governed by single-tradition versus convergent constraint sets. P3 could be tested by systematic coding of documented AI governance failures (e.g., facial recognition bias, recommendation system manipulation, automated decision-making opacity) against the six convergence classes.

**Iwi partnership for tikanga validation.** The [PROPOSAL] status of tikanga encodings is not a limitation to be overcome in future work — it is a methodological requirement to be fulfilled. The formal encoding of tikanga in LAMAGUE requires collaboration with tangata whenua who hold the cultural authority to validate, correct, and extend these encodings. Te Tumu (School of Māori, Pacific and Indigenous Studies) at the University of Otago represents one potential partnership pathway, given the university's proximity to Kāi Tahu and its existing work in Indigenous governance.

**Automated compliance verification.** If the convergent constraint set can be expressed as computable specifications — which LAMAGUE's formal structure is designed to enable — then automated verification of AI governance compliance against cross-cultural standards becomes possible. This would move beyond current compliance regimes that assess against single-tradition standards, toward a verification framework that simultaneously checks Confucian-compatibility, tikanga-alignment, and Western-liberal-compatibility through structural isomorphism rather than checklist compliance.

**LAMAGUE as an open standard.** The formal grammar itself requires scrutiny, extension, and adoption beyond its original author. The claim of tradition-neutrality must be tested by researchers embedded in the traditions being encoded. If LAMAGUE proves genuinely useful for cross-cultural ethical encoding, it should evolve through the same kind of cross-cultural dialogue that the convergence analysis itself advocates.

---

## 8. Conclusion

We have presented a formal analysis of governance constraints across three independent philosophical traditions using computable symbolic grammar. The analysis identifies six classes of structural convergence — human primacy, earned authority, epistemic honesty, relational data obligations, intergenerational responsibility, and natural path alignment — where Confucian, Māori, and Western liberal traditions encode functionally isomorphic constraints despite developing independently.

This convergence is informative. It suggests that the constraints in question are not cultural preferences but candidates for genuine requirements of any governance system that sustains human flourishing over time. For AI governance, which must operate across cultural boundaries, these convergent constraints provide a principled foundation that no single tradition can provide alone.

The work is incomplete. The tikanga encodings require iwi validation. The predictions require empirical testing. The LAMAGUE framework itself requires scrutiny as a formal tool. But the central finding — that independent traditions converge on structural governance constraints, and that this convergence is formally demonstrable — opens a path toward AI governance that is cross-cultural by construction, not by compromise.

The constraints that appear in all three traditions are the most robust candidates for universal AI governance requirements. Not because three traditions voted for them. Because three traditions independently discovered them through millennia of real-world governance practice.

---

## References

Abdilla, A., Arista, N., Baker, K., et al. (2020). Indigenous Protocol and Artificial Intelligence Position Paper. The Initiative for Indigenous Futures and the Canadian Institute for Advanced Research.

Anderson, M., & Anderson, S. L. (Eds.). (2011). *Machine Ethics*. Cambridge University Press.

Appiah, K. A. (2006). *Cosmopolitanism: Ethics in a World of Strangers*. W.W. Norton.

Bai, Y., et al. (2022). Constitutional AI: Harmlessness from AI Feedback. *arXiv preprint arXiv:2212.08073*.

Birhane, A. (2021). Algorithmic injustice: a relational ethics approach. *Patterns*, 2(2).

Brown, D. E. (1991). *Human Universals*. McGraw-Hill.

Dennis, L., Fisher, M., Slavkovik, M., & Webster, M. (2016). Formal Verification of Ethical Choices in Autonomous Systems. *Robotics and Autonomous Systems*, 77, 1–14.

European Parliament. (2024). Regulation (EU) 2024/1689 laying down harmonised rules on artificial intelligence (AI Act).

Hagendorff, T. (2020). The Ethics of AI Ethics: An Evaluation of Guidelines. *Minds and Machines*, 30, 99–120.

Haidt, J., & Joseph, C. (2004). Intuitive Ethics: How Innately Prepared Intuitions Generate Culturally Variable Virtues. *Daedalus*, 133(4), 55–66.

Henrich, J., Heine, S. J., & Norenzayan, A. (2010). The Weirdest People in the World? *Behavioral and Brain Sciences*, 33(2–3), 61–83.

Jobin, A., Ienca, M., & Vayena, E. (2019). The global landscape of AI ethics guidelines. *Nature Machine Intelligence*, 1(9), 389–399.

Kukutai, T., & Taylor, J. (Eds.). (2016). *Indigenous Data Sovereignty: Toward an Agenda*. ANU Press.

Lewis, J. E., Arista, N., Pechawis, A., & Kite, S. (2020). Making Kin with the Machines. *Journal of Design and Science*, (6).

MacIntyre, A. (1981). *After Virtue: A Study in Moral Theory*. University of Notre Dame Press.

MacIntyre, A. (1988). *Whose Justice? Which Rationality?* University of Notre Dame Press.

McNamara, P. (2019). Deontic Logic. In E. N. Zalta (Ed.), *Stanford Encyclopedia of Philosophy*.

Mohamed, S., Png, M.-T., & Isaac, W. (2020). Decolonial AI: Decolonial Theory as Sociotechnical Foresight in Artificial Intelligence. *Philosophy & Technology*, 33(4), 659–684.

MOST (Ministry of Science and Technology, China). (2019). New Generation AI Governance Principles (新一代人工智能治理原则).

New Zealand Government. (2020). Algorithm Charter for Aotearoa New Zealand.

Nissenbaum, H. (2009). *Privacy in Context: Technology, Policy, and the Integrity of Social Life*. Stanford University Press.

Nussbaum, M. C. (2000). *Women and Human Development: The Capabilities Approach*. Cambridge University Press.

Nussbaum, M. C. (2011). *Creating Capabilities: The Human Development Approach*. Harvard University Press.

OECD. (2019). Recommendation of the Council on Artificial Intelligence. OECD/LEGAL/0449.

Rawls, J. (1971). *A Theory of Justice*. Harvard University Press.

Roberts, H., Cowls, J., Morley, J., Taddeo, M., Wang, V., & Floridi, L. (2021). The Chinese approach to artificial intelligence: an analysis of policy, ethics, and regulation. *AI & Society*, 36, 59–77.

Sen, A. (1999). *Development as Freedom*. Oxford University Press.

Sen, A. (2009). *The Idea of Justice*. Harvard University Press.

Sim, M. (2007). *Remastering Morals with Aristotle and Confucius*. Cambridge University Press.

Taiuru, K. (2020). *Māori Data Sovereignty and Privacy*. Wellington.

Te Mana Raraunga — Māori Data Sovereignty Network. (2018). Principles of Māori Data Sovereignty.

Tolmeijer, S., Kneer, M., Sarasua, C., et al. (2021). Implementations in Machine Ethics: A Survey. *ACM Computing Surveys*, 53(6), Article 132.

UNESCO. (2021). Recommendation on the Ethics of Artificial Intelligence. Adopted at the 41st session of the General Conference.

Vallor, S. (2016). *Technology and the Virtues: A Philosophical Guide to a Future Worth Wanting*. Oxford University Press.

von Wright, G. H. (1951). Deontic Logic. *Mind*, 60(237), 1–15.

Wallach, W., & Allen, C. (2009). *Moral Machines: Teaching Robots Right from Wrong*. Oxford University Press.

Wiredu, K. (1996). *Cultural Universals and Particulars: An African Perspective*. Indiana University Press.

Wong, P. H. (2020). Cultural Differences as Excuses? Human Rights and Cultural Values in Global Ethics and Governance of AI. *Philosophy & Technology*, 33, 705–715.

---

**Acknowledgments**

The tikanga Māori concepts in this paper are offered with respect and genuine uncertainty. They represent the author's current understanding, not authoritative knowledge. Meaningful engagement with Māori governance requires partnership with tangata whenua. The Lycheetah Foundation is committed to that partnership.

The author acknowledges no institutional affiliation. This work was developed independently over three years of continuous research, archived in full at https://github.com/Lycheetah/Lycheetah-Framework.

---

**Author Statement**

Mackenzie C. J. Clark is an independent researcher based in Dunedin, Aotearoa New Zealand. The Lycheetah Framework, of which LAMAGUE is one component, comprises ten interdependent formal frameworks for AI alignment, ethics, governance, and epistemic dynamics. The complete development archive (1,402 pages) is publicly available at https://github.com/Lycheetah/Lycheetah-Framework.

**Conflict of Interest:** The author declares no conflicts of interest.

**Data Availability:** All formal encodings, grammar specifications, and convergence analyses are publicly available in the Lycheetah Framework repository.
