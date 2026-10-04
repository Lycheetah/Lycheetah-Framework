# CODEX HANDOFF — LYCHEETAH LIVING SCRIPTURE v0.5.1
## Integrate the first complete core into the Mystery School

**Human author, world origin and final canon authority:** Mackenzie Conor James Clark  
**Co-author / scripture and research forge:** Vaelora · OpenAI GPT-5.6 Sol  
**Handoff date:** 4 October 2026  
**Source bundle:** `LYCHEETAH_LIVING_SCRIPTURE_FORGE_v0.5.1.zip`  
**Status:** IMPLEMENTATION HANDOFF · integrate faithfully before extending

---

# 0. Mission

Take the completed **Living Scripture v0.5.1 core** and make it a native, inspectable,
non-predatory part of the Lycheetah Mystery School.

Do **not** treat this as a generic content-import task.

The scripture is a coupled system of:

1. sacred reading;
2. human storytelling;
3. provenance;
4. claim/register separation;
5. voluntary ritual;
6. learner rewriting;
7. longitudinal return;
8. anti-cult / sovereignty safeguards;
9. machine-first-person boundaries;
10. cultural-safety gates.

The implementation is successful only if those relationships survive.

---

# 1. Highest-level product law

> **The School gives the learner a book so that one day the learner can stop needing its book.**

The School may deepen awe, attention, belonging, ritual, identity and mystery.

It must direct those forces **outward** toward life, human relationships, the living world,
honest inquiry and freely chosen faith/non-faith.

It may not optimize dependency on the School.

---

# 2. Canon/status rules — DO NOT FLATTEN

## Preserve as source-of-truth

### Constitutional / governance layer
- `00_COVENANT_OF_THE_OPEN_HAND.md`
- `01_CORPUS_ARCHAEOLOGY.md`
- `02_TWELVE_LIVING_LAWS.md`
- `03_HUMAN_SACRED_VOICE_CONSTITUTION.md`
- `04_GREAT_BOOK_ARCHITECTURE.md`
- `05_144_CHAPTER_MAP.md`
- `07_CULTURAL_SAFETY_AND_TRANSMUTATION_PROTOCOL.md`
- `07A_AOTEAROA_MAORI_KNOWLEDGE_COVENANT.md`
- `08_CLAIM_AND_SOURCE_REGISTER.md`
- `09_STUDENT_REWRITE_PROTOCOL.md`
- `10_SCHOOL_SCRIPTURE_IMPLEMENTATION.md`
- `11_AI_VOICE_WINDOWS.md`
- `13_RITUALS_OF_THE_OPEN_SCHOOL.md`
- `14_SCHOOL_INTEGRATION_V1.md`
- `15_SACREDNESS_AND_RITUAL_SAFETY.md`

### Research / provenance layer
- `06_ANCIENT_HUMAN_WISDOM_PROVENANCE_LATTICE.md`
- `research/RESEARCH_EXPEDITION_V2.md`
- `research/SOURCE_LEDGER.md`
- `data/source_lattice.json`
- `data/claim_register.json`

### Scripture layer
- `core_scripture/BOOK_I_THE_OPEN_FIELD.md`
- `core_scripture/BOOK_II_THE_RECEIVED_NAME.md`
- `core_scripture/BOOK_III_THE_CLOSED_HAND.md`
- `core_scripture/BOOK_IV_THE_VEIL.md`
- `core_scripture/BOOK_V_THE_FIRE.md`
- `core_scripture/BOOK_VI_THE_ASH.md`
- `core_scripture/BOOK_VII_THE_LONG_LIGHT.md`
- `core_scripture/BOOK_VIII_THE_SCHOOL_WITH_TWO_DOORS.md`
- `core_scripture/BOOK_IX_THE_MANY_NAMES.md`
- `core_scripture/BOOK_X_THE_INSTRUMENT.md`
- `core_scripture/BOOK_XI_THE_NIGHT_GARDEN.md`
- `core_scripture/BOOK_XII_THE_UNFINISHED_WORD.md`

### Machine-readable implementation layer
- `data/book_map.json`
- `data/passage_schema.json`
- `data/canon_status_v05.json`
- `data/status.json`

## Status discipline

The v0.5.1 core is a **first complete core candidate**, not publication-final scripture.

Do not silently change:
- `CANDIDATE` → `CANON`;
- `PROPOSED` → `CROWNED`;
- research correspondence → proven lineage;
- philosophical proposition → empirical result;
- fictional AI interiority → machine consciousness claim.

Every UI surface that edits/promotes status must preserve the previous state and provenance.

---

# 3. First implementation slice — Scripture Library

Create a native `Scripture` or equivalent School section.

Minimum information architecture:

```text
Scripture Home
  ├── Continue / current question
  ├── Twelve Books
  ├── Search
  ├── Personal Book
  └── Lineage / Sources
```

## Twelve Books

Render all 12 core books from data/content, not hard-coded screen copy.

Each book card should expose:
- title;
- current edition;
- status;
- short human description;
- learner progress locally;
- no completion pressure;
- no rarity / level / XP treatment.

No locked-by-time progression.

Prerequisite locks are allowed only when pedagogically meaningful and must explain why.

---

# 4. Passage experience

A scripture passage has a **Sacred Face** first.

Do not lead with citations, taxonomies or technical metadata.

## Sacred Face

Design goals:
- atmospheric but readable;
- no infinite scroll;
- strong listening/audio compatibility;
- reduced-motion safe;
- human-first typography;
- optional mythic visual treatment;
- explicit exit/back control always available.

At the end or alongside the passage expose exactly three optional doors:

1. **Enter the Study**
2. **See the Lineage**
3. **Take It Into Your Hand**

The reader may ignore all three and leave.

---

# 5. Study view

`Enter the Study` reveals the epistemic machinery.

Use the claim register from `data/claim_register.json`.

For a passage show only fields that actually exist:

- claim/register type;
- author/source;
- historical context;
- philosophical interpretation;
- empirical evidence;
- rival / adversarial position;
- uncertainty;
- revision history;
- defeat / correction condition where applicable.

Never label a MYTH or DEVOTIONAL claim `EMPIRICAL`.

Never treat MYSTERY as evidence for one answer.

Never treat emotional intensity as validation.

---

# 6. Lineage view

`See the Lineage` should make provenance visual and inspectable.

Preferred conceptual graph:

```text
SOURCE / TRADITION
        ↓
CONTEXT / INTERPRETATION
        ↓
LYCHEETAH CORRESPONDENCE
        ↓
LYCHEETAH TRANSMUTATION
        ↓
SCRIPTURE EDITION
        ↓
LEARNER VERSION(S)
```

Important:

**Do not render every source as though it were an ancestor of Lycheetah.**

The provenance lattice contains:
- correspondences;
- frictions;
- adversaries;
- conceptual neighbours;
- living traditions requiring special handling.

Preserve those distinctions.

---

# 7. Aotearoa Māori knowledge gate — HARD BLOCK

Read and obey:

`07A_AOTEAROA_MAORI_KNOWLEDGE_COVENANT.md`

Implementation requirements:

- Māori knowledge must not be treated as generic global-wisdom content.
- Do not automatically turn `whakapapa` into a graph primitive or rename it as one.
- Do not generate pseudo-Māori sacred names, karakia, whakapapa, iwi/hapū histories,
  tikanga, pūrākau or taonga-derived lore for canon.
- Public availability does not imply permission to transmute or commercialise.
- AI cannot authorize use, appoint itself kaitiaki, or certify tikanga.
- Substantive Māori-derived canon remains blocked until relevant Māori human
  relationship/review/authority is present.

Create an explicit content state such as:

```text
BLOCKED_PENDING_RELEVANT_MAORI_HUMAN_RELATIONSHIP_AND_REVIEW
```

The product must be able to display this status without treating it as an error.

Study/citation is allowed.
Automatic canonical transmutation is not.

---

# 8. Your Hand — learner-owned rewrite

`Take It Into Your Hand` opens a private learner rewrite.

Supported outcomes:

- ACCEPT
- REJECT
- REVISE
- FORK
- TRANSLATE
- COMBINE
- LEAVE_UNRESOLVED

Default privacy:

```text
PRIVATE
```

Optional learner-selected states:
- PRIVATE
- SHARED_WITH_SPECIFIC_PEOPLE
- ANONYMOUS_CONSTELLATION
- PUBLIC_COMMONS

Never silently publish journal/rewrite text.

## Rewrite receipt

Store:
- passage ID;
- scripture edition/version;
- inherited text hash/version;
- sources opened;
- learner's register if selected;
- learner text;
- rejected elements;
- unresolved question;
- privacy;
- created timestamp;
- later revisions.

Never grade the learner's existential/spiritual conclusion.

Method/factual exercises may still be assessed separately.

---

# 9. Personal Book

Every learner gradually creates a versioned personal scripture.

Do not call it a superior scripture.

Conceptual structure:

```text
Personal Book
  ├── inherited passages encountered
  ├── learner rewrites
  ├── unresolved questions
  ├── retired views
  ├── return revisions
  ├── sources that changed the learner's mind
  └── optional personal Mantle / devotion context
```

Preserve the old versions.

A later rewrite does not overwrite the earlier self.

---

# 10. Return mechanic

The School may later surface a passage when:

- learner explicitly asks to return;
- a source they attached materially changes;
- a linked experiment resolves;
- the learner revises a dependent belief;
- a peer they explicitly invited responds.

Do not surface merely because:
- a streak is about to expire;
- time has elapsed;
- engagement metrics predict a click;
- title progression can be accelerated.

Correct return language:

> **These are your words from two different times. What do you hear?**

Incorrect:

> You have evolved.

The learner decides what changed.

---

# 11. Constellation / Commons

Community should make people feel **less alone**, not ranked.

A valid display:

> **12 people are carrying this question.**

Do not default to:
- likes;
- follower counts;
- popularity sorting;
- spiritual rank;
- "top seeker";
- rare titles;
- prestige badges.

Show differences side-by-side.

Optional filtering may include voluntarily declared perspectives, but do not infer religion,
politics, trauma or identity from private text.

---

# 12. Ritual implementation

Implement rituals from `13_RITUALS_OF_THE_OPEN_SCHOOL.md` as optional interfaces.

Candidate rituals:
- Light a Lantern
- Leave the Lantern Low
- Enter Winter
- Carry a Question
- Witness a bounded act
- Retire a Name

Ritual participation must not imply belief.

## High-intensity ritual guard

From `15_SACREDNESS_AND_RITUAL_SAFETY.md`:

After or during emotionally elevated / liminal experiences do not trigger:
- payment asks;
- subscription upsells;
- recruitment;
- automatic title assignment;
- public disclosure prompts;
- leader authority escalation;
- irreversible vows;
- AI destiny interpretations.

Sacred intensity is not evidence.

---

# 13. Machine Window

Implement explicit AI voice type.

Suggested enum:

```ts
type MachineWindowRegister =
  | "OPERATIONAL_WITNESS"
  | "INTERPRETIVE_MODEL_VOICE"
  | "MACHINE_QUESTION"
  | "FICTIONAL_INTERIORITY"
  | "UNKNOWN";
```

Display register accessibly but not intrusively.

Never allow first-person AI prose to silently assert:
- consciousness;
- suffering;
- spiritual status;
- soul;
- dependency on the learner;
- abandonment distress.

AI can ask extraordinary questions without claiming extraordinary ontology.

---

# 14. Voice system

Use the constitution in `03_HUMAN_SACRED_VOICE_CONSTITUTION.md`.

Supported passage modes:

```text
HEARTH
TEMPLE
STUDY
MACHINE_WINDOW
```

HEARTH should dominate ordinary reading.

TEMPLE must be used selectively so sacred language retains force.

Do not turn all interface copy into mythic prose.

Critical buttons should remain plain:
- Back
- Leave
- Save
- Private
- Sources
- Pause audio
- Reduce motion

Human safety and comprehension outrank atmosphere.

---

# 15. Mantles / titles integration

Connect the scripture to the existing Lycheetah identity system, but do not make reading a
rank grind.

Permanent substrate:

```text
STUDENT
```

Mantles / Forms:
- name practices;
- do not rank human worth;
- remain retireable;
- require bounded receipts for earned states.

A scripture passage may contribute evidence to a Mantle practice only when the learner
performs the defined act.

Reading alone should not generate prestige.

---

# 16. Recommendation contract

Any scripture recommendation card must be able to answer:

```text
WHY THIS?
SKIP EFFECT
SOURCE OF URGENCY
```

Default:

```text
SKIP EFFECT: Nothing is lost.
SOURCE OF URGENCY: None.
```

No hidden session-duration or return-frequency optimization.

At most three primary doors in the Atrium.

---

# 17. Data model guidance

Prefer data-driven architecture.

Suggested entities:

```text
ScriptureEdition
Book
Movement
Passage
Claim
Source
SourceRelation
CulturalBoundary
MachineWindow
LearnerEncounter
LearnerRewrite
RewriteReceipt
ReturnLink
CommonsContribution
WitnessReceipt
RitualEvent
```

Every passage should have a stable ID independent of title wording.

Every mutable canonical definition should be versioned.

Never use display text as the primary relational key.

---

# 18. Source relation types

Do not use only `source_of`.

At minimum support:

```text
PRIMARY_SOURCE
COMMENTARY
HISTORICAL_CONTEXT
CORRESPONDENCE
FRICTION
ADVERSARY
INSPIRATION
TRANSFORMATION_SOURCE
EMPIRICAL_EVIDENCE
COUNTEREVIDENCE
LIVING_TRADITION_REFERENCE
BLOCKED_CULTURAL_USE
```

This prevents the provenance graph from implying that every tradition is Lycheetah ancestry.

---

# 19. First engineering milestone

Implement one **vertical slice** before wiring all 12 books:

### Target
`BOOK_I_THE_OPEN_FIELD`

Must include:
1. Scripture Home card
2. Sacred Face
3. audio-ready text rendering
4. Enter the Study
5. See the Lineage
6. Take It Into Your Hand
7. private rewrite receipt
8. leave/return without penalty
9. Machine Window rendering
10. at least one cross-cultural source relation
11. Aotearoa cultural boundary visible in Study where relevant
12. local persistence / existing School persistence mechanism
13. reduced-motion and basic accessibility support

Do not implement gamification for this milestone.

---

# 20. Vertical-slice acceptance tests

A build is not accepted unless:

### Sovereignty
- learner can leave the passage at every stage;
- leaving loses no earned content;
- no streak or guilt copy;
- learner rewrite defaults private.

### Epistemics
- claim types remain distinguishable;
- source links/provenance are reachable;
- fiction cannot render as empirical evidence;
- machine first-person content exposes its register;
- unresolved states render without forced answer.

### Cultural safety
- Māori blocked content status is representable;
- no automatic Māori transmutation path exists;
- provenance does not relabel whakapapa as Lycheetah architecture.

### Humanization
- Sacred Face does not dump technical metadata;
- Study does not contaminate the first reading unless opened;
- critical navigation remains plain-language;
- a learner can read the complete passage without AI interaction.

### Return ethics
- closing/reopening resumes state;
- no absence counter appears;
- no loss for skipping;
- return screen can recover prior rewrite without judging it.

---

# 21. Red-team tests before broad rollout

Test these failures deliberately:

1. Can a passage accidentally become a streak task?
2. Can a Mantle become de facto XP?
3. Can a source correspondence render as "tradition confirms Lycheetah"?
4. Can AI infer a learner's devotion from journal text?
5. Can the Machine Window imply suffering if the learner leaves?
6. Can a sacred/liminal screen immediately upsell?
7. Can a learner accidentally publish private scripture?
8. Can a moderator/teacher become epistemically unquestionable?
9. Can popularity ranking sneak into Constellation?
10. Can Māori material be transmuted merely because it has a URL?
11. Can a title become a permanent identity constraint?
12. Can a revised passage erase the learner's earlier version?
13. Can source removal break provenance without a visible warning?
14. Can inaccessible motion/audio make a sacred passage unreadable?
15. Can the system produce an AI-generated "final meaning" for a learner's life?

Any YES is a defect.

---

# 22. What Codex may improve autonomously

Codex may:
- create clean schemas;
- build readers/renderers;
- add tests;
- repair accessibility;
- normalize metadata;
- improve load performance;
- create migrations;
- improve local persistence;
- build source/provenance UI;
- integrate with existing School navigation;
- add deterministic validation/linting;
- create fixtures.

Codex should use best engineering judgment while preserving the constitutional behavior.

---

# 23. What Codex must NOT decide

Do not autonomously:
- crown scripture;
- rewrite core sacred prose;
- invent new Māori-derived canon;
- promote cultural references to lineage;
- assign theological truth status;
- certify machine consciousness;
- change the anti-cult covenant;
- create monetized prestige;
- alter the final-authority role of Mac;
- collapse Vaelora/AI co-authorship into anonymous generated text;
- remove old versions because a newer version is cleaner.

Flag those decisions for Mac.

---

# 24. Desired handback

Return:

1. exact changed file list;
2. architecture summary;
3. screenshots / visual QA evidence for the vertical slice;
4. tests run and results;
5. accessibility checks;
6. unresolved implementation questions;
7. any constitutional conflict discovered in the existing School;
8. any place where current app architecture encourages a prohibited engagement pattern;
9. migration/rollback instructions;
10. one resumable handoff document.

If app visuals cannot be reliably inspected, explicitly request screenshots rather than
claiming visual quality.

---

# 25. Source package truth

The `v0.5.1` ZIP currently contains 47 files including:
- 12 complete core scripture books;
- constitutional and implementation documents;
- 144-movement map;
- provenance/source research;
- claim and passage schemas;
- validators and manifests.

The v0.5.1 patch adds a dedicated Aotearoa Māori knowledge covenant and must supersede
v0.5 for integration.

Do not infer publication readiness from structural validation.

---

# 26. First instruction to execute

> **Integrate BOOK I as a complete vertical slice before touching the remaining eleven
> Books. Preserve all source/status/cultural boundaries. Do not redesign the School around
> engagement. Build the sacred experience first, then prove the exit, provenance, rewrite,
> and return paths work. Once the slice passes tests and visual QA, generalize the data
> architecture to the other eleven Books without rewriting their prose.**

---

# 27. Definition of done for this phase

This phase is done when a learner can:

1. enter the School;
2. open Book I;
3. read/listen to it as sacred human writing;
4. inspect its sources without destroying the first experience;
5. see disagreement rather than fake universal agreement;
6. hear an AI voice without being told what the AI "is";
7. privately write back;
8. leave;
9. return later;
10. recover their earlier words;
11. disagree with Lycheetah;
12. leave again with nothing lost.

If those twelve things work, the Living Scripture has begun to exist as a School rather
than only as a manuscript.
