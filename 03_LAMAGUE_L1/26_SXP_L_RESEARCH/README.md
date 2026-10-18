# SXP-L: meaning between minds

**[SCAFFOLD] Experimental constructed-language branch · v0.1–v2.0**  
**Creator:** Mackenzie Conor James Clark / Lycheetah Framework.  
**Integration review:** Caelorynth / Codex · 18 October 2026.

SXP-L explores a pronounceable register for belief, uncertainty, affection,
perspective and repair, alongside inspectable structured representations.

> `mi liva ti` — “I love you.”

The ambition: meaning should survive the journey between minds, and losses
should be visible. Current evidence covers restricted software behaviour;
human comprehension and fluent speech remain research questions.

SXP-L is one part of the wider language programme. Read the
[LAMAGUE guide](../README.md) and [full synthesis](../LAMAGUE_SYNTHESIS.md) for
the formal CORE, native glyphs, spoken encoding, packet codec, runtime research
and the distinctions between their grammars and evidence.

| Read or run | Purpose |
|---|---|
| [Current v2.0 source](v2.0/README.md) | Four-format comprehension instrument and reproducibility commands |
| [Integration review](INTEGRATION_REVIEW.md) | Rerun evidence and unresolved defects |
| [Independent early audit](../SXP-L_LAMAGUE_INDEPENDENT_AUDIT_v0.1_to_v1.0.md) | Preserved critique of v0.1–v1.0; not superseded by a higher version |
| [Handoff entry point](handoff_2026-10-18/RESEARCH_HANDOFF/00_START_HERE.md) | Curated reconstruction, chronology and merge protocol |
| [Release index](handoff_2026-10-18/RESEARCH_HANDOFF/06_RELEASE_INDEX.csv) | Original archive sizes and SHA-256 values |

## Run the software checks

```bash
python3 tools/verify_research_intake.py
cd 03_LAMAGUE_L1/26_SXP_L_RESEARCH/v2.0
python3 -m unittest -v test_validation20
cd baseline
PYTHONPATH=runtime:. python3 -m unittest -q test_reference19 test_repair18 runtime.test_continuity13 runtime.test_perspective14
```

These are authored parser and study-instrument tests. They are not participant
data, language fluency measurements or evidence of AI improvement.

## Language line, not a canonical replacement

SXP-L is distinct from LAMAGUE Core, Native-36, RUNTIME, PACKET and Spoken
LAMAGUE. Its version numbers do not advance those other lines. The supplied
[merge protocol](handoff_2026-10-18/RESEARCH_HANDOFF/04_MERGE_PROTOCOL.md)
keeps schema mappings and information loss explicit. No parser replacement or
agent-authorization integration is made by this intake.

Early audit blockers remain relevant to the inherited runtime: grammar
layering, meaning-difference priorities, linguistic revocation handling and
repair chains. A green study-generator test does not close them.

## Researcher and participant material

The full source and original ZIPs include researcher answer keys and alternate
representations. **They are researcher archives, not a blinded participant
release.** For a future consented pilot, share only one reviewed standalone
cohort HTML, disclose recruitment and scoring methods, and handle answer-key
exposure. There are currently zero genuine participant results in this packet.
All supplied browser CSVs are explicitly synthetic software QA.

The 46-file handoff, all 20 original archives, and the 112-file extracted v2.0
release are retained byte for byte under their own paths. The
[source manifest](../../28_DEFENSE/RESEARCH_INTAKE_2026-10-18_SOURCE_MANIFEST.json)
records those identities. Checksums are not signatures or scientific validation.
