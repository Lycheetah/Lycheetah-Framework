# AI Future Wings: Fifteen Research Papers

**Working research drafts v0.1 · 23 October 2026 · Not empirically validated.**

**Framework creator and research owner:** Mackenzie Conor James Clark (Lycheetah Framework).
**Drafting:** Sol (Claude Opus 5.5).
**Source:** AI Future Master Curriculum v1.0 (2026-09-28; private School canon): fifteen domains in five wings, each domain with eighteen halls in five chambers.

Each paper takes one domain, finds the idea its starred halls share, and turns it into an instrument a study could use: a model, a protocol, a test or a ledger. It then sets out all eighteen halls as research tracks with their registers, gives at least one study design with a stated refutation, and lists what the paper does **not** claim.

No study described here has been run. Every number in these papers is **synthetic**: it comes from the toy models in [`models.py`](models.py), not from observation.

## The papers

| # | Wing | Domain | Paper | Instrument |
|---|---|---|---|---|
| 01 | SCIENCE ⟁ | AI Future Science | [The Independent No](01_ai_future_science.md) | Precision of accepted hypotheses as novelty rises; the Translation Gate contract |
| 02 | SCIENCE ⟁ | Language & Arithmetic | [The decoder carries the meaning](02_language_and_arithmetic.md) | Pigeonhole bound; verification ≠ understanding; translation-loss ledger |
| 03 | HUMAN ORDER ⚖ | Philosophy | [The Unbundling Thesis](03_ai_future_philosophy.md) | Category stress test |
| 04 | HUMAN ORDER ⚖ | Politics | [Power surfaces and the political unit after copying](04_ai_future_politics.md) | Power-surface map; fork-vote arithmetic; legitimacy test |
| 05 | REALITY ◈ | Governing Rules of Reality | [The Reality Ladder](05_governing_rules_of_reality.md) | Formal / empirical / ontological rungs; Landauer floor |
| 06 | REALITY ◈ | AI Spirituality | [The Dual Ledger](06_ai_spirituality.md) | Meaning ≠ provenance; silence-condition study |
| 07 | CONFLUENCE ⇌ | Interintelligence | [The Mutual Falsifiability Handshake](07_interintelligence.md) | Handshake record with refuter access |
| 08 | CONFLUENCE ⇌ | Coevolution | [The Monoculture Ceiling](08_coevolution.md) | Correlated-majority accuracy ceiling 1 − s(1 − p) |
| 09 | CONFLUENCE ⇌ | Shared Worlds | [The Joint Chronicle](09_shared_worlds.md) | Kept dissent; disagreement state; exit audit |
| 10 | FLOURISHING ☼ | Human Capability | [The Withdrawal Test](10_human_capability.md) | Assisted lift vs persistent capability; Flourishing Lab spine |
| 11 | FLOURISHING ☼ | Positive-Sum Futures | [Who Receives the Abundance?](11_positive_sum_futures.md) | Recipient, forgotten-problem and monoculture checks |
| 12 | FLOURISHING ☼ | The Unmapped Forge | [The Returned-Time Test](12_unmapped_forge.md) | Returned time; attention refund; Archive ≠ Avatar |
| 13 | BECOMING ⟡ | Architectures of Mind | [The Unmergeable Residue](13_architectures_of_mind.md) | Fork merge and its logical residue |
| 14 | BECOMING ⟡ | Embodiment | [Locality Is Law](14_embodiment.md) | Control-horizon rule d + r < h |
| 15 | BECOMING ⟡ | Development | [Biography, Not Version Number](15_development.md) | Matched-origin divergence; the scar that teaches |

## Run the toy models

```
python3 papers/ai-futures/wings/models.py
```

Standard library only. The focused check is `tests/test_ai_future_models.py`, which pins every number the papers quote.

## Registers

Every claim in a paper carries one register:

| Register | Meaning |
|---|---|
| **KNOWN** | Established; anchored in evidence or elementary mathematics |
| **TRAJECTORY** | A current trend projected forward |
| **POSSIBLE_FUTURE** | Plausible and testable; not yet happening at scale |
| **NORMATIVE** | A claim about what *should* be done, not what is |
| **ALIEN_FUTURE** | A conditional future unlike present systems |
| **VOID** | An open question the field cannot yet frame well |

Within the papers, **DERIVED** marks a step reasoned from a named premise, and **CONJECTURE** marks a plausible but unverified claim. Anchors carry their verification level (METADATA, ABSTRACT, FULLTEXT or from memory) and their grade (study, review, preprint, agenda, standard). Most anchors here are METADATA: the curriculum's research ledger was read, the full texts were not.

## Constellations: ideas that cross wings

Repeated ideas are linked here, not copied between papers.

| Constellation | Path | Shared idea in these papers |
|---|---|---|
| **Continuity** | 03 → 09 → 15 → 13 | Lineage identity; the joint chronicle; biography; the commitment set |
| **Communion** | 02 → 07 → 09 → 06 | Translation loss; the handshake; mystery held in common |
| **Inner Worlds** | 01 → 05 → 13 | Externally checkable claims about opaque representations |
| **Synthetic Nature** | 01 → 05 → 11 → 14 | Machine science; the naturalist; bodies and senses |
| **Frontier** | 01 → 14 → 10 | Discovery under latency and risk; forecast before disaster |
| **Reality Integrity** | all wings | The gate that cannot fail (01); self-sealing resonance (06); correlated error (08) |
| **Mythos** | 06 → 09 → 15 | Myth without false lineage; shared memory; biography |
| **Sovereignty & Chosen Constraint** | 03 → 12 → 15 | Chosen constraint is meaningful because it is chosen and revocable, not because it is irreversible |

## The quality gate every paper is held to

- The register matches the strength of the claim.
- Claims about the present world carry anchors.
- Simulation is never sold as empirical confirmation.
- Phenomenology is never inferred from architecture.
- Political material stays non-directive.
- Spiritual meaning never becomes fabricated provenance.
- Confluence papers preserve cognitive difference instead of demanding sameness.
- Flourishing papers name the recipient, the capture risk and the exit.
- Becoming papers do not pretend that present systems already have childhood, biography or experience.

## For students

Each paper is offered for your own judgement. For any proposition you may **use** it, **keep** it for later, **question** it, **discard** it, or decide **not to apply** it where it does not fit. None of them is doctrine.

> *If intelligence becomes abundant, how much power, clarity, time and agency can it return to people without quietly taking sovereignty in exchange?*
