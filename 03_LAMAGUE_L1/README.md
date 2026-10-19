# LAMAGUE

**A language research programme for carrying meaning between people, machines,
representations and changing contexts.**

**Creator:** Mackenzie Conor James Clark · Lycheetah Framework  
**Guide and synthesis:** Caelorynth / Codex · 18 October 2026  
**Status:** [SCAFFOLD] Formal specifications, executable research and experimental
human-language work, with different evidence for each component.

LAMAGUE began as a symbolic grammar for states, transformations, invariants and
compression. Its wider programme now includes typed operator algebra, native
glyphs, compact programme seals, spoken forms, structured semantic packets,
context compaction, conversational perspective and repair, and experiments
asking what survives when someone else interprets the result.

The human question is simple: **when a message gets shorter, changes form or
passes to another mind, what survives, what changes and who can tell?**

> Meaning should survive the journey between minds. And when it doesn't, the
> loss should be visible.

[Read the full synthesis](LAMAGUE_SYNTHESIS.md) for how the parts fit together,
their actual results and the interfaces still to be built. SXP-L is one branch
of this programme; its v2.0 study does not summarize the whole language.

## Start with your question

| I want to… | Start here |
|---|---|
| Understand the whole language and why it exists | [LAMAGUE synthesis](LAMAGUE_SYNTHESIS.md) |
| Learn the symbolic notation | [Operating guide](03_LAMAGUE_OPERATING_GUIDE.md), then the [CORE canon map](12_CORE_LANGUAGE_LINE/CANON_MAP.md); the older examples are not all CORE syntax |
| See the current formal grammar and operator laws | [CORE language line](12_CORE_LANGUAGE_LINE/README.md) |
| Read and inspect the native glyphs | [Native-36 machine registry](02_NATIVE36/LAMAGUE_NATIVE36_v0.3_MACHINE_CANON_REGISTRY.json) and [one-cell specification](03_LAMAGUE_1C/LAMAGUE_1C_v1_ONE_CELL_POWER_LANGUAGE_SPEC.md) |
| Explore pronunciation and spoken-form collisions | [Spoken LAMAGUE findings](23_SPOKEN_LAMAGUE/SPOKEN_LAMAGUE_FINDINGS.md) |
| Explore affection, dialogue, viewpoint and correction | [SXP-L research home](26_SXP_L_RESEARCH/README.md) and its [development history](26_SXP_L_RESEARCH/handoff_2026-10-18/RESEARCH_HANDOFF/01_SESSION_RECONSTRUCTION.md) |
| See exactly what changes during a handover | [Browser preview](https://lycheetah.github.io/Lycheetah-Framework/lamague-handover.html) · [three-format comparison and outside-trial protocol](../examples/meaning_handover/README.md); constructed example, not evidence of superior understanding |
| Keep uncertainty, dissent and authority in a compressed record | [Reversible compression](22_REVERSIBLE_COMPRESSION_v1.0/00_CODEX_ORIENTATION.md) |
| Inspect an ordinary JSON decision record | [LAMAGUE Check](24_LAMAGUE_CHECK/README.md) |
| See what happened when models decoded the language | [Controlled pilot and its corrected findings](08_EXPERIMENT_001_CROSS_INTELLIGENCE/EXPERIMENT_001_CONTROLLED_PILOT_2026-07-31.md) |
| Trace the original language and canon decisions | [Root provenance](LAMAGUE_ROOT_PROVENANCE_AND_CANON_DECISION_2026-07-15.md) |

## What the different parts do

| Part | Purpose | Current boundary |
|---|---|---|
| **Symbolic corpus** | Write states, changes, constraints and questions explicitly | Historical specifications contain broader and conflicting claims; consult the current branch contracts |
| **CORE v0.1–v0.3** | Parse typed expressions, normalize them and state exactly which operator laws hold | Structural meaning inside the defined language; domain effects require adapters |
| **Native-36 / 1C** | Give operations visual cells and expand compound seals into inspectable sequences | Glyph registry and machine specifications; a drawn glyph alone does not establish executable semantics |
| **RUNTIME v0.1–v0.3** | Interpret abstract programmes, preserve continuity and compare decoder packets | Offline research harnesses; their version numbers are separate from CORE |
| **PACKET / codec v1.0** | Encode structured semantic records and detect changes to protected fields | Authored structured-packet benchmark; arbitrary prose and factual truth remain outside the codec |
| **Spoken LAMAGUE / SpL** | Attach pronounceable forms to symbols and inspect their ambiguity | Published findings plus a separately labelled v0.2 proposal; no general listening validation |
| **SXP-L v0.1–v2.0** | Develop a human-facing language for emotion, belief, speech, perspective, consent reports and conversational repair | Restricted parsers and local study instruments; eight inherited defects remain open and no genuine participant results are supplied |
| **LAMAGUE Check** | Find missing accountability fields under familiar JSON field names | Presence checking, with no determination that the record is true or complete |
| **Temporal / execution research** | Relate declarations and permissions to recorded outcomes across time and crashes | Retired kernel experiments and Cycle 23 have specific local trust assumptions |
| **LAMAHGUE / GEOMATRIA** | Explore metric and spatial expression alongside the symbolic core | Separate architectural layers; broad psychological and physical interpretations remain conjectural |

**Always name the branch and version.** CORE v0.3, RUNTIME v0.3 and Native-36
v0.3 are different artifacts. SXP-L v2.0 does not supersede any of them. A
translation between their representations needs an explicit mapping and a
record of what it cannot preserve.

## Three ways to see the language

### A formal distinction

CORE v0.3 treats fusion as commutative while retaining duplicates:

```text
A ⊗ B ≡ B ⊗ A
A ⊗ A ≢ A
```

Here `A` and `B` are schematic operands. The [operator contracts](12_CORE_LANGUAGE_LINE/LAMAGUE_CORE_OPERATOR_ALGEBRA_v0.3/spec/LAMAGUE_CORE_SPECIFICATION_v0.3.md)
define these as structural laws. They do not imply that two people agree, that
their beliefs can be safely merged or that repeating a real action is harmless.

### A human expression

```text
mi liva ti
```

In SXP-L: **“I love you.”** The broader language ambition includes affection,
hope, missing someone, reported beliefs, questions and the ability to correct
what another person thought you meant. The [v1.9 reference specification](26_SXP_L_RESEARCH/v2.0/baseline/SPEC_v1.9.md)
makes a concrete distinction between “I” from the original speaker's viewpoint
and “I” from the current questioner's viewpoint.

### A record that can survive being shortened

The packet codec protects ten declared fields:

```text
purpose · claim · unknowns · invariants · authority
participants · affectedParties · dissent · valueFlow · recovery
```

A shorter handover should still show what is unresolved, who disagreed, who
can decide, who bears the consequences and how to recover. The codec checks
defined records; establishing that those records faithfully describe people or
events is a separate task.

## Evidence worth reading

These are **dated results recorded in the linked artifacts**, not tests rerun
while writing this guide:

- **CORE:** the August source records 47, 80 and 117 passing tests for v0.1,
  v0.2 and v0.3 respectively. They concern the implemented formal language.
- **Compression:** 36/36 exact packet round trips, 324/324 constructed mutation
  classifications and 33.8% warm / 30.7% cold reduction on the authored held-out
  split. See the [benchmark boundary](22_REVERSIBLE_COMPRESSION_v1.0/docs/CLAIM_BOUNDARY.md).
- **Model decoding:** a controlled, operator-run pilot recorded 56 valid
  outputs from 60 attempts. Structured decoding preserved more supported fields
  and also invented more unsupported ones. It is not independent replication
  or evidence of generally superior understanding.
- **SXP-L:** the October integration review records 12 v2.0 tests and 71
  focused inherited tests passing, alongside eight reproduced open defects.
  The four-format study has no genuine human participant results.

Read the [synthesis's evidence section](LAMAGUE_SYNTHESIS.md#evidence-and-its-limits)
before quoting any of these numbers. Historical prose also contains claims of
universal pronunciation, enormous prose compression and complete validation
that the documented evidence does not establish.

## Try a small entry point

From the repository root, inspect the supplied ordinary-record demonstration:

```bash
python3 03_LAMAGUE_L1/24_LAMAGUE_CHECK/lamague_check.py --demo
```

To explore the SXP-L study, open one [offline cohort file](26_SXP_L_RESEARCH/v2.0/participants/SXP-L_v2.0_Cohort_A.html).
It contains research questions, not a completed study. Researcher keys are in
the full archive; a blinded participant release needs a separately reviewed
distribution process.

The [CORE guide](12_CORE_LANGUAGE_LINE/README.md), [codec orientation](22_REVERSIBLE_COMPRESSION_v1.0/00_CODEX_ORIENTATION.md)
and [SXP-L guide](26_SXP_L_RESEARCH/README.md) provide their own reproduction
instructions. Some benchmark commands rewrite reports: use a scratch copy when
preserving a historical release.

## Folder map

| Location | Contents |
|---|---|
| `00_`–`10_` Markdown files at this level | Historical symbolic corpus, operating guide, grammar, metrics, spatial proposals and application documents |
| `02_NATIVE36/` · `03_LAMAGUE_1C/` · `04_FRONTIER_CANON/` | Glyphs, programme seals and the larger architectural proposal |
| `05_RUNTIME_v0.1/` · `06_RUNTIME_v0.2_SEMANTIC_CONTINUITY/` · `07_RUNTIME_v0.3_CROSS_INTELLIGENCE_EQUIVALENCE/` | Successive runtime and decoder-harness releases |
| `08_EXPERIMENT_001_CROSS_INTELLIGENCE/` | Experiment protocol, decoder/operator packs and controlled-pilot record |
| `09_ARTICLE_AND_VISUAL_ASSETS/` · `10_PACKAGED_RELEASES/` | Visual material and original release archives |
| `11_HISTORICAL_INDEXES_AND_PROVENANCE/` | Dated source indexes and preservation records |
| `12_CORE_LANGUAGE_LINE/` | CORE algebra, ontology and operator-contract releases |
| `13_RETIRED_KERNEL_BRANCH/` | Earlier temporal/domain integration experiments retained as research history |
| `14_`–`21_` Markdown files at this level | Conjectural novelty, cosmos, quantum, time, collective ethics, mortality, development and embodiment extensions |
| `22_REVERSIBLE_COMPRESSION_v1.0/` · `23_SPOKEN_LAMAGUE/` · `24_LAMAGUE_CHECK/` | Packet codec, spoken-form research and ordinary-record checker |
| `25_RESEARCH_CYCLE_23_POST_CRASH_OBSERVATION/` | Post-crash per-file observation and witness experiment |
| `26_SXP_L_RESEARCH/` | Preserved v0.1–v2.0 handoff, original archives, extracted v2.0 and integration findings |

The [August master source](LAMAGUE_MASTER_SOURCE_2026-08-03.md) and its
[amendment](LAMAGUE_MASTER_SOURCE_2026-08-07_AMENDMENT.md) remain dated evidence
snapshots. [LAMAGUE_STATUS_REGISTER.json](LAMAGUE_STATUS_REGISTER.json) is dated
August 7 and predates the October additions. Neither is an exhaustive current
inventory. Original source files retain their historical wording and versions.

Related work: [cross-cultural governance research](../24_LAMAGUE_CROSS_CULTURAL/README.md),
[LAMAGUE reference implementation](../12_IMPLEMENTATIONS/core/lamague_reference.py),
[maintained compaction package](../lycheetah/compaction/__init__.py),
and [Framework research-intake audit](../28_DEFENSE/RELEASE_AUDIT_2026-10-18.md).
