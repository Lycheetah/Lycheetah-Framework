# Lycheetah Framework

**Tools, research and stories for intelligence that keeps human choice visible.**

Created by **Mackenzie Conor James Clark**, an independent researcher in
Ōtepoti / Dunedin, New Zealand. This repository brings together nine foundational
frameworks, executable prototypes, published failures, language experiments,
public-policy proposals, learning designs and a fictional world.

**Current orientation: 19 October 2026.** Maturity belongs to each component.
There is no single release, validation verdict or test total for the whole corpus.

## Start with something you can use or read

| What brings you here? | Start here |
|---|---|
| Read the stories and explore the new research | [Earned Light & Sovereign Will](https://lycheetah-earned-light.banduabusiness.chatgpt.site): complete stories, a research introduction and both downloadable bundles |
| Keep a goal, unknowns and permission boundaries visible between AI sessions | [LAMAGUE handover preview](https://lycheetah.github.io/Lycheetah-Framework/lamague-handover.html) · [source, comparisons and tester card](examples/meaning_handover/README.md) |
| Understand what Lycheetah has become | [Current whole-framework synthesis](13_SYNTHESIS_REPORTS/CURRENT_FRAMEWORK_SYNTHESIS.md) |
| Find a file or workstream | [Current repository map](00_Sovereign_Index.md) · [source ownership and working home](WORKING_HOME.md) |
| Build with the software | [Implementation guide](12_IMPLEMENTATIONS/README.md) · [Assurance Runtime](34_ASSURANCE_RUNTIME/README.md) |
| Check what is actually supported | [Capability and evidence guide](33_APPLICATIONS/README.md) · [claims and failure records](28_DEFENSE/CLAIMS_README.md) |
| Read the current NZ proposal | [Six data rights for every New Zealander](23_NZ_AI_GOVERNANCE/README.md) |
| Bring this corpus into an AI-assisted task | [Explore with AI](EXPLORE_WITH_AI.md) · [extraction protocol](26_FOR_AI/AI_EXTRACTION_PROTOCOL.md) |

The public reading site is live. The research's presence online does not mean
that its proposals are adopted, independently validated or production-ready.

## The current shape of the work

**Knowledge and evidence.** CASCADE models represented knowledge and revision.
Truth Pressure and the Hybrid Gateway develop evidence-aware instruments and
reviewable changes. Internal coherence is distinct from external truth.

**Meaning and continuity.** LAMAGUE spans formal language, visual/spoken forms,
record codecs and experimental conversational tools. Exact record preservation
is a different claim from better human understanding. The handover preview
keeps permission, uncertainty and recovery information inspectable.

**Action and authority.** AURA names governance commitments. The Assurance
Runtime and sovereign/action-control experiments implement restricted policy,
permission, receipt and recovery mechanisms. A policy decision does not by
itself establish that the surrounding agent or its effects are safe.

**Learning, philosophy and worldbuilding.** The Mystery School, stories and
Abstract and Generative branch explore what these ideas can create. Fiction,
symbolic value, philosophical argument and empirical evidence retain separate
statuses. Read the [synthesis](13_SYNTHESIS_REPORTS/CURRENT_FRAMEWORK_SYNTHESIS.md)
for the connections and boundaries.

## Current research entry points

| Research line | Question | Source home |
|---|---|---|
| Agent safety / frontier controls | Who may act, on which evidence, and what survives revocation or failure? | [Packet and continuation](papers/agent-safety/README.md) |
| Earned Trust | What happens between approving an action and observing its effect? | [Nine-cycle source and review](papers/agent-safety/earned-trust/README.md) |
| Earned Light | How do permission, portability and recovery preserve future choice? | [Forges I–VII](papers/agent-safety/earned-light/README.md) |
| Sovereign Choice / Sovereign Will | How can intention change, and which options remain reachable? | [Executable research](papers/agent-safety/sovereign-choice-research/README.md) · [philosophical charters](35_ABSTRACT_AND_GENERATIVE/SOVEREIGN_WILL/README.md) |
| Hybrid Gateway | How should changing evidence revise what an AI system remembers? | [v1.2 source and review](papers/ai-futures/hybrid-gateway/README.md) |
| LAMAGUE / SXP-L | What meaning, uncertainty and perspective survive representation changes? | [Language guide](03_LAMAGUE_L1/README.md) · [SXP-L research](03_LAMAGUE_L1/26_SXP_L_RESEARCH/README.md) |
| The Independent No | Can a refusal remain binding? | [Manuscript and proposed study](papers/independent-no/README.md) |

These are distinct versioned instruments. Their authored tests, archived results,
conventional-baseline ties and counterexamples do not establish one universal
safety mechanism. [Paper index](papers/README.md) ·
[October intake review](28_DEFENSE/RELEASE_AUDIT_2026-10-19.md).

## Evidence before adjectives

- The strongest claims are specific: a particular implementation, formal model,
  fixture, codec round trip or dated dataset evaluation.
- The text-scoring work carries externally authored dataset results and important
  failures. [Initial evaluation](33_APPLICATIONS/EXTERNAL_VALIDATION_2026-08-07.md)
  and the [independent-publisher boundary](33_APPLICATIONS/INDEPENDENT_PUBLISHER_2026-08-07.md)
  narrow the supported scope to AI-assistant text; they do not establish general
  human-communication or runtime-alignment verification.
- A source's `ACTIVE` tag is an internal claim classification. It is not a synonym
  for independent replication, peer review or production deployment.
- Synthetic fixtures and repeated lineage tests are not independent experiments.
  Neutral conventional-baseline results remain published.
- Convergence arguments apply under their declared mathematical assumptions.
  Consciousness thermodynamics and metaphysical interpretations remain conjectural.

[Counter-Codex](28_DEFENSE/COUNTER_CODEX.md) ·
[Failure Museum](28_DEFENSE/FAILURE_MUSEUM.md) ·
[Scope boundary](28_DEFENSE/SCOPE_BOUNDARY.md).

The [claim register](28_DEFENSE/CLAIMS.json) contains 71 structured claim records.
Its author-assigned classifications are:

| Classification | Records | How to read it |
|---|---|---|
| **ACTIVE** | 52 | An asserted result within its stated scope; inspect its evidence and assumptions. |
| **SCAFFOLD** | 12 | An incomplete structure or operational link. |
| **CONJECTURE** | 4 | An open claim requiring further evidence. |
| **RETRACTED** | 3 | A withdrawn claim retained for accountability. |

These counts describe the register, not all files or recent research additions.
They are internal classifications, not 52 independently validated findings.
`python3 tools/verify-claims.py --register` checks the count mirrors against the
actual records; it does not establish their scientific validity.

## Run this checkout

Python requirements and optional integrations are declared in
[pyproject.toml](pyproject.toml). The package source currently declares version
1.3.0; language releases, papers and story editions have their own versions.

```sh
python3 -m pip install -e .
lycheetah-assure --help
lycheetah-compact --help
python3 examples/meaning_handover/demo.py --help
```

The [core guide](12_IMPLEMENTATIONS/core/README.md) explains the foundational
modules. [Runtime documentation](34_ASSURANCE_RUNTIME/README.md) explains
policy decisions and receipts. Follow the component's focused checks and dated
receipt rather than treating an old repository-wide test count as current.

## Read, learn and create

- [Collected scriptures and stories](LYCHEETAH_MYTHOS/SCRIPTURES_AND_STORIES/README.md):
  editable sources, edition/status manifest and generated reading exports.
- [Mystery School](14_MYSTERY_SCHOOL/README.md): curriculum and design packets;
  app integration is separate from being present in this corpus.
- [Abstract and Generative](35_ABSTRACT_AND_GENERATIVE/README.md): philosophical
  and symbolic research, with a [catalogue of proposed builds](35_ABSTRACT_AND_GENERATIVE/BUILD_CATALOGUE/README.md).
- [NZ data rights](23_NZ_AI_GOVERNANCE/README.md): the current six-rights proposal;
  earlier cultural-governance drafts are historical, not concurrent national standards.

## Working with the repository

The [repository map](00_Sovereign_Index.md) is the current location guide.
Older indexes, academic snapshots and numbered research versions remain sources
for history. New material should update its area's README, evidence and changelog.
Generated exports derive from their owned manuscripts or build source.

Read [CONTRIBUTING.md](CONTRIBUTING.md), [SECURITY.md](SECURITY.md) and
[the AI extraction protocol](26_FOR_AI/AI_EXTRACTION_PROTOCOL.md) before making
or repeating consequential claims. Preserve attribution, failures and source
provenance. An idea's symbolic depth need not become a scientific claim to matter.

Code is covered by the [MIT licence](LICENSE) unless a subproject supplies its
own terms. Documents and imported packets retain their stated notices.
[Citation metadata](CITATION.cff) identifies the author and citation version;
it is not a release certificate for every workstream.
