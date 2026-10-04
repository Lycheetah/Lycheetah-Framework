# Modelcraft — The Wing of Many Engines

**Make something. Learn why it worked. Change it. Make it yours. Pass it on.**

Modelcraft studies how framing, context, tools, evaluation and recoverable state
change what someone can accomplish with a model. Its practical question is:
how much useful capability can you recover by changing how you work?

**Human author and final product authority:** Mackenzie Conor James Clark.
**Source collaboration:** Mac × Vaelora; AI attribution supplied as OpenAI GPT-5.6 Sol.
**Framework integration and reference implementation:** Caelorynth · 4 October 2026.
**Status:** candidate curriculum, local data contracts and reference code; publication source on master.

## Start with one useful experiment

[Make a portable build checklist](FIRST_EXPERIMENT.md). Define its outcome, compare
two ways of requesting it, inspect the results and export your recipe. No result
has been run or pre-certified by this packet. You may record that it failed.

The exercise can begin on paper. Optional model use has its own access, privacy,
hardware and cost requirements. "$0" labels here refer to the required local
reading/planning exercise, not a promise of free inference.

## What is here

- [24 technique families](data/techniques.json), with the original descriptions and
  separately labelled integration exercises.
- [Ten teaching Halls](data/halls.json): Ask, Show, Feed, Split, Check, Tool, Route,
  Loop, Persist and Harness. Teaching Halls are internal to Modelcraft; they are
  not ten additional School Wings.
- [Recommendation catalogue](data/recommendations.json): seven proposed sections
  and six local exercise cards. Continue remains empty until the learner supplies
  explicit unfinished work. The community card prepares a private draft; no live
  community or submission system is claimed.
- [Contracts](CONTRACTS.md), four [schemas](schemas/), [ranking policy](data/policy.json)
  and a [local reference implementation](reference.py).
- [Business quick-start](BUSINESS_QUICK_START.md) and [the app handoff](NATIVE_SCHOOL_HANDOFF.md).
- [Source ledger](data/sources.json) and the [unchanged incoming master](source/LYCHEETAH_MODELCRAFT_RECOMMENDATIONS_MASTER_v0.1.md).

## Source and evidence status

The incoming master calls itself implementation-ready. This intake preserves that
authored label but does not adopt it as a certification. Its example "schemas"
were illustrative shapes, its JSON registry contained ten of the 24 techniques,
and its status field mixed evidence, compatibility and freshness. The maintained
contracts here resolve those data issues explicitly.

The provider links were supplied by the handoff and have not been fetched or
independently checked in this batch. Documentation citations are distinct from
empirical results. All 24 families remain `UNTESTED_IN_THIS_PACKET`; none has a
measured capability multiplier. The example trick remains a hypothesis.

Newer supplied design proposes ten School Wings, adding Modelcraft to the previous
nine-Wing proposal. The [earlier app intake](../../LYCHEETAH_MYTHOS/SCRIPTURES_AND_STORIES/LIVING_SCRIPTURE/integration/NATIVE_SCHOOL_HANDOFF.md)
recorded fourteen different Wings. Their content and identity mapping remains a
product decision. No app navigation or curriculum migration happened here.

## Recommendation boundaries

Suggestions explain the selected goals, score components, costs and reason codes.
The ranker is stateless and accepts only explicit inputs. It has no engagement,
popularity, purchase, emotional-state or inferred-identity field. Skip has no loss;
urgency defaults to none. The existing [recommendation constitution](../IDENTITY_AND_RETURN/source/RECOMMENDATION_CONSTITUTION.md)
remains the source boundary. This v0 deliberately uses fewer inputs than that
constitution permits; identity-based diversification is not implemented.

Recipe drafts and example receipts default private. A field named PRIVATE does
not secure a storage system. Publication, moderation, independent reproduction,
real persistence and deletion/export behavior remain app work.

## Run the focused checks

From this directory, using Python and the repository's existing `jsonschema` dev dependency:

```sh
python3 -m unittest discover -s tests -v
python3 reference.py
```

The first command checks contract and ranking failures; the second prints the
sample recommendation. Neither contacts a provider nor stores a learner event.
Test reproductions use synthetic records and are not model experiments.

The 4 October intake passed 17 focused test methods, four schema loads, 38 local
links and source/backup hash checks. A malformed-date failure was repaired before
closure. The [verification snapshot](VERIFICATION.json) records the local gate;
it is not independent replication or a native phone witness.

Future edits belong in this package. The source master is an intake snapshot,
not a second editable specification. No full-suite run, phone visual witness,
learner study, commit, push or release is claimed.
