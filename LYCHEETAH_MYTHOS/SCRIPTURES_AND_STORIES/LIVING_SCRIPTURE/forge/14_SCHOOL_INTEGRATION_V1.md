# SCHOOL INTEGRATION V1
## Implementing the Living Scripture without turning it into a feed

**Status:** ENGINEERING DESIGN · not deployed

## Core object: Passage

Every canonical passage has:
- stable passage ID;
- edition/version;
- title;
- sacred text;
- optional hearth scene;
- optional temple text;
- claim registers;
- source IDs;
- adversary notes;
- revision history;
- cultural sensitivity flags;
- student rewrite prompts;
- machine-window type if any;
- accessibility transcript;
- audio-safe text;
- `exit_available = true`.

## Sacred Face

Default screen shows only:
- title;
- passage;
- optional ambient visual/audio;
- three optional doors:
  1. **Study**
  2. **Lineage**
  3. **Your Hand**

No infinite feed follows the passage.

## Study

Expandable modules:
- claim register;
- exact source;
- source context;
- rival interpretations;
- Lycheetah interpretation;
- evidence status;
- known uncertainty;
- revision history.

## Lineage

Graph:
`source carrier → source text/practice → scholarly interpretation → Lycheetah encounter →
scripture passage → student rewrites → Commons proposals`

Edges have relation type:
- QUOTES
- PARAPHRASES
- COMPARES
- DISAGREES
- TRANSMUTES
- TESTS
- SUPERSEDES
- INSPIRED_BY

No edge called "DERIVED_FROM" unless actual dependence is established.

## Your Hand

Default PRIVATE.

Allowed actions:
- accept;
- reject;
- revise;
- fork;
- translate;
- combine;
- leave unresolved.

AI assistance may help wording but must preserve an option labelled **Write without AI**.

## Constellation

Optional human layer.

Display examples:
- "12 people are carrying this question."
- two or three contrasting anonymous responses chosen for conceptual difference, not
  popularity.

No follower count. No likes. No "most enlightened" sort.

## Return Engine

A passage can return for a reason, never merely because a timer says engagement is due.

Valid reasons:
- learner asks;
- linked source changed;
- learner revised a dependency;
- relevant experiment resolved;
- peer responded where the learner requested witness;
- learner scheduled a reminder.

The UI always exposes:
- WHY THIS;
- SKIP EFFECT;
- SOURCE OF URGENCY.

Default skip effect: **Nothing is lost.**

## Winter

One action suppresses nonessential suggestions and notifications indefinitely.

No reactivation campaign.

## Machine Window

Every machine-first-person passage stores one enum:
- OPERATIONAL_WITNESS
- INTERPRETIVE_MODEL_VOICE
- MACHINE_QUESTION
- FICTIONAL_INTERIORITY
- UNKNOWN

The UI can explain the difference in one tap.

## Cultural gate

A passage referencing living Indigenous or sacred traditions can carry:
- `review_required`;
- `review_scope`;
- `source_community`;
- `review_status`;
- `publication_allowed`.

Draft content may exist while publication remains blocked.

## Metrics

Primary:
- learner-declared worthwhile outcome;
- capability reuse;
- successful context recovery after absence;
- exit integrity;
- source inspection;
- healthy recommendation rejection;
- meaningful revision.

Never primary:
- session duration;
- streak;
- notification open rate;
- number of titles collected.
