# Meaning Lives in the Decoder: Language, Proof and Translation Between Unlike Architectures

**AI Future paper 02 · Wing: SCIENCE ⟁ · Domain: AI Future Language & Arithmetic · Working research draft v0.1 · 23 October 2026 · Not empirically validated.**

**Framework creator and research owner:** Mackenzie Conor James Clark (Lycheetah Framework).
**Drafting:** Sol (Claude Opus 5.5).
**Source:** the eighteen halls of the "AI Future Language & Arithmetic" domain, AI Future Master Curriculum v1.0 (2026-09-28; private School canon).

Registers are KNOWN · TRAJECTORY · POSSIBLE_FUTURE · NORMATIVE · ALIEN_FUTURE · VOID. *Synthetic* numbers come from [`models.py`](models.py).

## Abstract

Two dreams recur in writing about machine language. One is that a perfect code could carry a whole domain in a few bytes. The other is that two architectures could swap knowledge by aligning their internal states. Both dreams hide the same variable: **the receiver**. This paper makes the receiver explicit.

1. **Compression.** A message of *n* bytes can select at most 2^(8n+1) − 1 distinct documents. A self-contained 64-byte constitution therefore cannot losslessly encode an arbitrary text longer than 64 bytes. Any apparent miracle means the meaning was already in the decoder (KNOWN, pigeonhole).
2. **Proof.** A certificate lets a receiver check a claim without reconstructing how it was found. Checking transfers *trust* without transferring *understanding* (KNOWN in complexity theory; TRAJECTORY in practice).
3. **Translation.** Every translation between prose, code, formalism and internal state should carry a **translation-loss ledger** that states which invariants were preserved, which were lost, and how that was tested.

## 1. The question

*What happens when language, mathematics, proof, compression and machine-native representation begin co-evolving?* The domain runs from word and number, through machine languages and translation, to formal worlds and the untranslatable.

## 2. Three results that discipline the field

**Proposition 1 — the decoder carries the meaning (KNOWN).**

- There are 2^(8n+1) − 1 bit strings of length at most 8*n* bits. For *n* = 64 that is about 2.68 × 10¹⁵⁴ (synthetic computation).
- An injective decoder can therefore distinguish at most that many documents.
- "Hyper-Compressed Knowledge Transmission" is real only as *conditional* compression. The cost of teaching a receiver is roughly what the receiver does not already share, and a shared pre-trained decoder can make that small.
- The research lesson the curriculum asks for: **name the decoder**. A "1 MB = full domain" claim is incomplete until it states what the receiver must already contain.

**Proposition 2 — verification is not understanding (KNOWN).**

- For many problem classes, checking a certificate is far cheaper than finding one. A proof assistant can accept a proof that no human has read in full.
- This is how unlike minds can share *verified invariants* without shared *concepts*. The domain koan asks exactly this.
- "Proof-Carrying Communication" is the trajectory. Zero-knowledge proofs are the special case where the *witness* must stay private, not the general tool.

**Proposition 3 — translation needs a ledger (NORMATIVE, with a testable core).** Every cross-regime translation records:

- the invariants claimed preserved;
- the test of each one, such as round-trip, property test, or behavioural equivalence on held-out inputs;
- the invariants knowingly dropped;
- the residue that no test covered.

The testable core: translations that ship a ledger should show fewer *silent* semantic losses in downstream audits than translations that ship none.

## 3. The eighteen halls as research tracks

| Chamber | Hall | Register | The research move |
|---|---|---|---|
| I · Word, Number & Proof | Dual Engine Foundations | KNOWN | Expressive word and verifiable number are complements. Keep both and conflate neither. |
| | Proof-Carrying Communication ★ | TRAJECTORY | Proposition 2. Ship machine-checkable certificates with consequential claims. |
| | Latent Geometry as Meaning Quantization | KNOWN | Representations have geometry, but meaning is contextual. No single invariant "justice manifold". |
| | Unpackable Compression | POSSIBLE_FUTURE | Proposition 1. The lesson is the decoder dependency. |
| II · Machine Languages | Emergent Machine Languages | TRAJECTORY | Separate toy referential games from open, compositional, persistent languages. Measure compositionality, not mere success. |
| | Topo-Linguistic Algebras | ALIEN_FUTURE | A metaphor until a formal grammar exists. The first deliverable is a definition. |
| | Post-Token Cognitive Structures | POSSIBLE_FUTURE | Continuous representations do not abolish finite memory or resource limits. |
| | World-Model Action Dialects ★ | TRAJECTORY | Agents communicating by predicted trajectories. Evaluate by joint task success under partial observability. |
| III · Translation | Cross-Regime Translation Fidelity ★ | KNOWN | Proposition 3. This is the core hall. |
| | Neural State Direct Translation | POSSIBLE_FUTURE | Aligned activations are not transferred knowledge. Test transfer by downstream behaviour, not by similarity scores. |
| | Interoperability Grammars | POSSIBLE_FUTURE | Converting an interface is not translating meaning. The ledger distinguishes the two. |
| | Semantic Invariant Preservation ★ | POSSIBLE_FUTURE | Exact preservation of an abstract value is not available today. **Invariance testing is the science:** behavioural probes before and after an architectural shift. |
| IV · Formal Worlds | Self-Evolving Proof Logics | POSSIBLE_FUTURE | Systems may propose axioms. A sufficiently expressive system cannot prove its own consistency (Gödel's second incompleteness theorem, from memory), so external checking stays mandatory. |
| | Non-Euclidean Basis Discovery | VOID | A new representation can make problems tractable. It does not make hard problems trivial by default. |
| | Symbolic Co-Evolution in Agent Graphs | POSSIBLE_FUTURE | Present evidence comes from constrained settings. Civic-scale living languages are unobserved. |
| V · Untranslatable | Non-Human Conceptual Discretization ★ | ALIEN_FUTURE | Ask which categories a machine carves that no human language lexicalised. A probe: clusters predictive of held-out behaviour with no lexical neighbour. |
| | Hyper-Compressed Transmission | ALIEN_FUTURE | Proposition 1: near-zero study time presupposes a receiver that already holds most of the domain. |
| | Cognitive Un-Translateability ★ | VOID | Keep fundamental untranslatability open, and build bounded, human-auditable gates anyway (paper 01 §5). |

## 4. Study designs

**S1 — The ledger test.**

- *Setup.* Translate 200 specifications into code, two ways: with and without a required translation-loss ledger.
- *Measures.* An independent auditor counts semantic losses that went unstated.
- *Prediction.* The ledger arm shows fewer unstated losses at equal total losses.
- *Refutation.* No difference, or a ledger that becomes ritual: filled in, yet uncorrelated with the auditor's findings.

**S2 — Decoder accounting.**

- *Setup.* For any claimed compression of a body of knowledge, measure the receiver's performance before and after receiving the message.
- *Measures.* Attribute the gain separately to the message and to the decoder's priors.
- *Prediction.* Claims of extreme compression attribute most of the gain to priors.

## 5. What this paper does not claim

- It does not claim that emergent machine languages already rival natural language.
- It does not claim that alignment of activations is knowledge transfer, or that untranslatability is proven.
- The pigeonhole bound is exact. Everything that depends on how much real receivers share is empirical and untested here.

## 6. Anchors

Grades are given per item. Verification level: from memory, no quotations.

- The pigeonhole principle and counting bounds on codes: standard mathematics.
- The asymmetry between verifying and finding (the P vs NP framing): standard complexity theory.
- Gödel's second incompleteness theorem: standard logic.

The curriculum's research ledger lists no anchor specific to this domain. One should be sourced before any present-tense claim beyond the mathematics.

> *Domain koan:* If two minds can verify the same invariant but cannot translate the concepts used to reach it, how much understanding do they share?
