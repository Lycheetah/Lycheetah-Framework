# Framework website sources

**Updated:** 19 October 2026. **Creator:** Mackenzie Conor James Clark / Lycheetah Framework.

**Register:** [INTERPRETIVE] Source ownership and navigation; evidence retains its component status.

`docs/` holds the main GitHub Pages website, browser demonstrations, research reading
copies and earlier publication/support drafts. The [whole-tree map](../00_Sovereign_Index.md)
and [current synthesis](../13_SYNTHESIS_REPORTS/CURRENT_FRAMEWORK_SYNTHESIS.md) describe the larger body.

Public URL: [lycheetah.github.io/Lycheetah-Framework](https://lycheetah.github.io/Lycheetah-Framework/).
`master` is the publication-source branch. An unmerged edit is not a deployment
receipt; this guide does not report a fresh hosted-page check.

## Pages and source owners

| Page | Purpose | Edit owner / evidence boundary |
|---|---|---|
| [index.html](index.html) | Entrance to tools, research, stories and the current NZ proposal | Static HTML here; align summaries with current repository guides. |
| [playground.html](playground.html) | AURA text-heuristic demo | Static page here; output is not validated alignment detection. |
| [lamague-handover.html](lamague-handover.html) | Offline record comparison, budgets and exports | Generated from [examples/meaning_handover/](../examples/meaning_handover/README.md); edit its template/runner and regenerate. |
| [lamague-handover-report.json](lamague-handover-report.json) | Example measurements and source digests | Same runner. A digest is not authentication or a human-understanding result. |
| [nz-governance.html](nz-governance.html) | Current NZ proposal and historical context | Static HTML; [six rights for every New Zealander](../23_NZ_AI_GOVERNANCE/DATA_SOVEREIGNTY_FOR_NEW_ZEALANDERS.md) is the owning proposal, not law or an adopted standard. |
| [mystery-school.html](mystery-school.html) | Public study/orientation | Static view. [School source guide](../14_MYSTERY_SCHOOL/README.md) owns newer curriculum/design packets; those do not establish app integration. |
| [for-agents.html](for-agents.html) | Earlier method/orientation | Static view. Use the [current extraction protocol](../26_FOR_AI/AI_EXTRACTION_PROTOCOL.md) and register for evidence/status. |
| [lamague-encoder.html](lamague-encoder.html) | Cross-cultural encoding demo | Static demonstration; encoding does not establish cultural validation or community endorsement. |
| [failure-museum.html](failure-museum.html) | Website corrections/failures | The [repository Failure Museum](../28_DEFENSE/FAILURE_MUSEUM.md) owns the full record. |
| [experimental.html](experimental.html) | Experimental reading | Preserved exploratory page; [18_EXPERIMENTAL](../18_EXPERIMENTAL/README.md) names its evidence boundary. |
| [enter.html](enter.html) | Earlier alternate entrance | Preserved route; `index.html` is the main entrance. Use repository guides for current ownership. |
| [independent-no.html](independent-no.html) | Independent No overview | Static overview; [paper packet](../papers/independent-no/README.md) owns the research. |
| [Paper reading edition](research/independent-no-paper.html), [protocol](research/independent-no-protocol.html), [PDF](research/independent-no.pdf) | Working-research reading/export editions | Markdown and sources belong to [papers/independent-no/](../papers/independent-no/README.md); reading copies derive from that packet. |

[style.css](style.css) and [script.js](script.js) provide shared appearance and
behavior. Research reading pages have additional CSS/JS under `research/`.
Earlier browser receipts remain historical; this source guide does not rerun them.

## Generated views

From the repository root, use the owning guide's documented environment. The
handover runner has an explicit export route:

```sh
python3 examples/meaning_handover/demo.py \
  --write-page docs/lamague-handover.html \
  --write-report docs/lamague-handover-report.json
```

The Independent No HTML/source copies are built with
`python3 papers/independent-no/build.py`. Its PDF and earlier browser artifacts
have their own [verification/recovery boundaries](../papers/independent-no/RECOVERY_NOTE.md);
do not imply they were regenerated because Markdown or this guide changed.

## Separate public story reader

[Earned Light & Sovereign Will](https://lycheetah-earned-light.banduabusiness.chatgpt.site)
is hosted separately from GitHub Pages. Its maintained web source is
[examples/earned_light_reading/](../examples/earned_light_reading/README.md).
Story Markdown remains in the [collection](../LYCHEETAH_MYTHOS/SCRIPTURES_AND_STORIES/README.md).
Generated `dist/` and deployment checkout are mirrors, not competing manuscripts.
Public deployment and GitHub PR approval/merge are separate states.

## Other material kept here

- [Architecture](ARCHITECTURE_OVERVIEW.md), [relationship essay](HOW_THIS_RELATES.md), [press kit](PRESS_KIT.md), [manifesto](THE_SOVEREIGN_MANIFESTO.md), [creation myth](THE_CREATION_MYTH.md), [motivation](THE_WHY.md), [playground specification](PLAYGROUND_BUILD_SPEC.md) and [article draft](X_ARTICLE_SOVEREIGNTY.md) preserve public explanation/writing context. They do not override current evidence records.
- [Cross-cultural paper](LAMAGUE_CROSS_CULTURAL_PAPER.md) is a working source; [comparative-research context](../24_LAMAGUE_CROSS_CULTURAL/README.md) is not endorsement.
- [COMMUNITY/](COMMUNITY/) and [GRANTS/](GRANTS/) contain earlier resource, community and funding drafts. A saved application is not a submitted or funded one.
- [SONNET_CLEANUP_PLAN.md](SONNET_CLEANUP_PLAN.md) is an earlier maintenance plan, not today's execution router. The original co-creation PDF remains source history.

Website changes use [docs/CHANGELOG.md](CHANGELOG.md), naming the highest actual
source, browser or deployment witness and unwalked limits. Repository changes also
use [the root changelog](../CHANGELOG.md). Preserve packet-specific licences and
read [LICENSE](../LICENSE) rather than inferring terms from an older footer.
