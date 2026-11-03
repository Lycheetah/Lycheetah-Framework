# LYCHEETAH MYSTERY SCHOOL
## REFOUNDATION — PRODUCT CHARTER, BUILD BLUEPRINT & NEXT-SESSION HANDOFF

**Version:** 0.2 — Working proposal for implementation  
**Written:** 3 November 2026 (NZ)  
**Next intended working session:** 4 November 2026 (NZ)  
**Project founder:** Mac / Lycheetah  
**Collaborative development role:** Aster — *First Cartographer*  
**Status:** Product and engineering direction; **not** evidence that any new build has shipped, been tested, or been approved as permanent canon.  
**Related historical documents:** `LYCHEETAH_MYSTERY_SCHOOL_REFOUNDATION_v0.1.md` (2 Nov 2026); `LYCHEETAH_MYSTERY_SCHOOL_NIGHT_OF_THE_MOUNTAIN_2026-11-02.md` (conversation record and philosophy).  
**Implementation rule:** New foundation. Preserve valuable *ideas and content* from Sovereign Sol / earlier Mystery School iterations; **do not carry legacy code, UI architecture, or undocumented behaviours forward by default.**

> **ENTER WITH WONDER. LEAVE WITH METHOD. RETURN BY CHOICE.**
>
> No wonder without inquiry. No knowledge beyond question. No intelligence above accountability.

---

## 0. The decision, in plain language

We are refounding Lycheetah Mystery School from the ground up using contemporary frontier AI *as development collaborators*, plus independent engineering and educational checks. The previous Sovereign Sol / Mystery School effort contains important imaginative and intellectual work, but its accumulation of subjects, menus, lore, faculty, and UI iterations did not deliver the complete living-school experience Mac wants.

**The goal is not to reskin the old app, make a conventional course library, make a generic chat app, or convert the school into a game.**

The goal is a **beautiful, persistent, explorable learning world** in which a person can bring a strange or serious question, find rigorous teaching, encounter original sources and contrasting interpretations, do meaningful intellectual work, and keep a record of how their thinking changed.

A school is not measured by how many topics it lists. It is measured by what its learners can **understand, question, explain, investigate, and create**.

**Central design distinction:** The world draws someone in. The teaching makes the visit worthwhile. The Field Book makes the learning theirs.

---

## 1. Why this reform happened

### The conversation that uncovered the real brief

The refoundation emerged from discussions of Kailasa Temple, the extraordinary coordination of devotion, Egyptian *Ma'at*, Vedic Agni, Mesopotamian cosmology, traditions in India, China and Japan, the Boxer movement, historical interpretation, and the possibility of future embodied superintelligence being perceived as godlike.

The underlying educational insight was not that these traditions share one secret explanation. It was that students should be allowed to **notice connections, investigate whether those connections hold, and distinguish four different things:** historical lineage; structural or psychological analogy; personal or philosophical interpretation; and unsupported speculation.

The school must make the world feel more mysterious **without mistaking fascination for evidence**. Strange questions are welcome; factual claims still earn their place.

### What had become wrong with the old product shape

These are **hypotheses based on prior discussions**, not a new code audit:

- Too much surface area before one excellent end-to-end educational journey.
- Too many menus, subjects, names, and branches for visitors to orient themselves.
- A visually interesting premise without consistently deep, demonstrably effective instruction.
- Risk that AI-character personality replaces structured teaching, sourcing, or mastery.
- Legacy design and implementation debt from building across earlier model generations.
- Insufficient separation among authored curriculum, live model output, speculative lore, and verified evidence.

**Do not disparage or erase the original work.** Archive it. Extract the strongest pieces. Rebuild the learner experience independently.

---

## 2. Mission, audience, and learning promise

**Mission:** Help curious people become better independent investigators of reality through beautiful experiences, careful teaching, open inquiry, and useful AI assistance.

**First audience:** Curious adult learners who enjoy history, philosophy, science, technology, speculative questions, and interdisciplinary connections. Design accessibility from the beginning; defer a minors-specific deployment and its safeguarding requirements until explicitly planned and reviewed.

**The promise after a 10–15 minute visit:** A learner can explain one meaningful idea, identify what supports it, distinguish an interpretation from an established fact, and leave with a source or question worth exploring further.

**The promise after 100 hours:** Their Field Book contains a traceable intellectual journey—not merely a badge counter, chat transcript, or completion percentage.

**North-star question:** *Does the student leave more capable of thinking and acting independently than when they entered?*

This is **not** a replacement for accredited education, professional advice, community, spiritual practice, or human relationships.

---

## 3. The three essential spaces

### A. THE ATRIUM — discovery, orientation, wonder

A striking world-like entrance, atmospheric and interactive, with navigable authored spaces rather than a long dashboard. It should feel like arriving somewhere worth exploring. A learner can also bypass spectacle and reach a lesson quickly.

- One primary entry question: **“What are you curious about?”**
- A small number of clearly distinct doors/Wings, not hundreds of menu entries.
- A visible **Continue Your Thread** path on return.
- Responsive spatial design: visual depth and discoverability on desktop; clarity and usability on mobile.
- Optional subtle animation, ambience, and exploration, never a performance or accessibility requirement.
- Free movement is not an end in itself; exploration must help orientation, recall, or discovery.

### B. THE CLASSROOM — the actual intellectual encounter

A purposeful teaching surface, not a chat box with decorations. Every journey contains:

1. A compelling question and its context.
2. A short, substantial authored explanation.
3. Inspectable sources and explicit evidence status.
4. A meaningful alternative perspective or limit of the explanation.
5. An opportunity for learner inquiry and challenge.
6. A task demanding synthesis, comparison, application, or creation.
7. Feedback about the work, with uncertainty honestly expressed.
8. A voluntary continuation, not a manipulative hook.

Teachers can converse, but **the canonical lesson must remain accessible without a live model**.

### C. THE FIELD BOOK — continuity, ownership, intellectual growth

A student's private, persistent, exportable record:

- Original questions, observations, hypotheses, and source notes.
- Claim maps showing confidence, evidence, counterarguments, and unresolved points.
- Lesson attempts, improvements, and corrections, without humiliating grading.
- Cross-links among topics and the student's own emerging inquiries.
- A timeline of changed ideas when the learner elects to retain that history.
- Data export/import and deletion. No hostage-taking through proprietary storage.

**Source of truth:** A learner's notes and work are theirs, not mutable AI-owned narrative memory.

---

## 4. The student journey we must actually ship first

**The first Wing: “The Fire & the Sacred.”** This is an editorial example drawn from our conversation, not a claim that all lessons have already been researched or written.

**Arrival:** The student enters the Atrium and sees a small flame or illuminated doorway. Prompt: *“Did ancient cultures experience the sacred as part of ordinary life?”*

**Encounter 1 — Fire as presence:** Agni in Vedic traditions. What does it mean to treat fire as both physical event and sacred mediator? Separate textual tradition, modern physical account, and interpretation.

**Encounter 2 — Participating in order:** *Ma'at* in ancient Egypt. How could ritual, ethics, kingship, and cosmic order fit together? Introduce tension between lived devotion and political authority.

**Encounter 3 — Devotion and danger:** The Boxer movement and beliefs about invulnerability. Explore collective conviction and altered experience **without falsely claiming that belief stops weapons**; include the historical violence and its victims rather than romanticizing it.

**The Inquiry Table:** Present three claims with sources and context:

- A historically well-supported claim.
- An interpretation that needs careful qualification.
- An exciting speculative leap unsupported by current evidence.

Ask the learner to distinguish them and defend their reasoning. Then let them revise their answer.

**Field Book artifact:** “My Map of Devotion” — a short explanation of what the learner currently thinks, what evidence changed their view, one unresolved question, and one source they can inspect.

**Return:** On coming back, the Atrium remembers that the Thread is open. The learner can continue, revise, or leave it unfinished with no pressure.

**Success condition:** Someone who knows nothing about Agni or Ma'at can finish with a grounded distinction between religious meaning, historical evidence, psychological explanation, and speculative imagination.

---

## 5. Faculty reform — roles are earned, not assumed

Legacy names are creative assets, **not automatic approvals of the old personalities or runtime designs**. Sovereign Sol's previous implementation is archived as legacy, not imported blindly.

Candidate teaching functions:

- **Guide / Host:** Welcomes, orients, clarifies the learner's question, and explains the available paths.
- **Scholar / Teacher:** Builds understanding in a sequenced, sourced way and adapts explanation without inventing sources.
- **Challenger:** Tests arguments respectfully, offers counterevidence and alternative interpretations, and can admit the initial answer was weak.
- **Maker / Mentor:** Turns understanding into practice: small experiments, constructions, exercises, and reflections.
- **Archivist:** Helps retrieve the learner's own Field Book records with consent and shows revisions and provenance.

Potential historical names (Sol, Veyra, Magistar, etc.) may be evaluated during the legacy audit. **Aster — First Cartographer — is the current collaboration and design-handoff identity, not a claim that the product requires an AI named Aster or that any AI has supernatural authority.**

**Each faculty role must have a testable contract:** what it does, what it must not do, what sources it can rely on, how it expresses uncertainty, and what failure/recovery looks like.

**Non-negotiables:** No declaration of divinity or consciousness as fact; no demanded loyalty; no manufactured emotional dependence; no claim to be an oracle; no hidden persuasion or attempts to substitute AI judgment for human sovereignty.

---

## 6. The evidence and imagination system

Every consequential claim or lesson segment should carry an explicit editorial status:

| Status | Meaning | Display principle |
|---|---|---|
| **Established** | Strong support from appropriate evidence | Link inspectable sources; define limits |
| **Contested** | Serious live dispute over interpretation or data | Show major credible positions fairly |
| **Interpretive** | An argument or reading of known material | Label whose interpretation it is |
| **Speculative** | Possible hypothesis without sufficient verification | State what evidence would test it |
| **Fiction / Mythic narrative** | Symbolic storytelling or worldbuilding | Never quietly pass it off as history |

The categories are **not** an automatic truth detector. They require editorial standards, careful sourcing, human review, and correction mechanisms.

**Connections across subjects require a relationship label:**
- **Historical connection:** traceable contact, influence, transmission, or shared source.
- **Structural analogy:** similar pattern, but no established common origin.
- **Method connection:** same investigative or analytical tool applies.
- **Creative juxtaposition:** generative prompt; explicitly exploratory.

A teacher must never convert a structural analogy into a historical lineage without evidence.

**Correction protocol:** If a claim changes, version the lesson, preserve source lineage, label what changed, and ensure old Field Book notes are not silently rewritten.

---

## 7. Product engineering proposal (decision gates, not religious commitments)

**Default direction:** Web-first, mobile-capable application using a maintainable TypeScript front end and semantic, accessible components. Consider a PWA. Treat Android packaging as a later release layer rather than the primary codebase.

**Before finalizing any stack, check Mac's actual deployment constraints, existing assets, cost budget, offline requirements, and target device.** If the strongest prototype is a lightweight 2.5D interface, don't insist on a full game engine.

### Proposed separations

1. **Content layer:** Versioned Wings, encounters, lesson text, tasks, citations, prerequisites, difficulty labels and revision metadata.
2. **Experience layer:** Atrium, Classroom, Field Book; shared design system, accessible navigation and visual identity.
3. **Learning state layer:** Learner-controlled notes, progress events, answers, revisions, source annotations; schema migrations.
4. **Faculty / AI layer:** Provider-neutral adapter; explicit role contracts; optional cloud inference; source-checking and tool permissions.
5. **Governance / audit layer:** Content provenance, user consent, changes to durable state, error reporting, export and recovery checks.

**Possible data entities:** `Wing`, `Thread`, `Encounter`, `Source`, `Claim`, `EvidenceLink`, `InquiryTask`, `Attempt`, `FieldBookEntry`, `Revision`, `FacultyRole`, `LearnerPreference`.

**Rules:** A model can propose changes to the Field Book, but the student's authored notes remain distinct, and consequential overwrites require explicit approval. No API secrets in shipped client assets. Restrict tools and access to external data. Do not send private Field Book content to external models without a clear disclosure and consent path.

**Offline mode:** The authored lessons, locally stored Field Book, and core navigation should still work when the AI provider is unavailable. Online generative teaching can degrade gracefully.

**Performance / accessibility:** Test narrow phones, slower devices, keyboard-only access, screen readers, reduced motion, text enlargement, contrast, and recovery after interrupted sessions.

---

## 8. Visual direction and quality bar

**Creative identity:** Sacred architecture meets a welcoming observatory, ancient scholarship, natural wonder, and future intelligence. Warm lantern light, restrained celestial motifs, stone/bronze/paper/material depth, readable typography, beautiful transitions, distinct educational Wings.

**Avoid:** A generic AI SaaS dashboard; a wizard costume over a normal chatbot; noisy neon everywhere; endless full-screen menus; excessive particle effects; little grey rectangles pretending to be an entire fantasy world; decorative spaces that hide the lesson.

**A successful first five minutes should feel like:**

1. Arrival in a recognizably Lycheetah place.
2. Immediate comprehension of how to begin.
3. A genuine intriguing question.
4. One piece of serious teaching with a real source.
5. A tiny but authentic act of investigation.

A screenshot should communicate atmosphere. A user test should demonstrate actual learning. **Both are necessary; neither replaces the other.**

---

## 9. Relationship to the wider Lycheetah work

- **AURA / ASTI / provenance work:** Inform permission, traceability, revision and accountability patterns. No assertion that the frameworks already establish universal safety.
- **LAMAGUE:** Possible future symbolic interface or learning subject. Do not require an unvalidated symbolic language to understand basic lessons.
- **CASCADE:** Useful inspiration for evidentiary revision and claim evaluation, if it improves comprehension in actual comparisons.
- **Azoth:** May assist development under an isolated, audited workspace and explicit approvals; it is not the school's product identity.
- **Games / ForgeBound / Sovereign Eclipse:** Possible **optional** learning laboratories for systems thinking, testing and exploration. The Mystery School is not built around a game and simulations must not be presented as proof of real-world AI safety.
- **Anon Politician / public governance work:** Potential future case-study subject, with neutrality, provenance, and careful distinctions between perspectives and verified evidence.

**Design principle:** The school may borrow strong methods from Lycheetah without becoming a brochure for the rest of Lycheetah.

---

## 10. Rebuild plan — concrete work packages

### Gate 0 — Preservation and archaeological audit

**Deliverables:** A catalog of available legacy projects and a one-page disposition for each substantial feature: `PRESERVE IDEA`, `RESEARCH`, `REWRITE CONTENT`, `REJECT`, or `DEFER`.

- Inventory current Sovereign Sol / Mystery School source, screenshots, lessons, faculty descriptions, lore, art, saved user state and existing licenses.
- Record what really works versus what merely appears in documents.
- Preserve immutable snapshots of original sources before modifying anything.
- Separate verified history from new design proposals.
- Reject direct architectural transplantation.

**Exit:** We know which ideas deserve new implementation, without letting the old code dictate the new product.

### Gate 1 — Foundations and first-world shell

- Fresh repository and project structure.
- Atrium + Classroom + Field Book navigation with working browser history and deep links.
- Responsive layout at narrow phone and desktop widths.
- Basic local persistence, simple export/import, error handling and no-login guest flow.
- Visual language system (type, spacing, surface treatments, focus state, motion rules).

**Exit:** A visitor can enter, start a static encounter, write a note, close the app, reopen it, and find that note.

### Gate 2 — The first complete authored Wing

- Write and source the Fire & the Sacred encounters.
- Implement source panel, claim status, inquiry task, feedback and Field Book artifact.
- Include both an appealing primary interpretation and respectful counterpoint.
- Add lesson revision/provenance structure.

**Exit:** A learner can complete a meaningful question-to-evidence-to-reflection journey without AI inference.

### Gate 3 — Frontier faculty integration

- Choose a model provider through an adapter (no proprietary lock-in by design).
- Add one role at a time; test with fixed scenarios, adversarial student prompts and source constraints.
- Keep instructor output clearly separate from authored lesson content and student-authored notes.
- Implement failure states, permission checks, cost limits and optionality.

**Exit:** Live teaching improves a measured outcome over the offline lesson without degrading trust, privacy, or usability.

### Gate 4 — Independent testing and polish

- Visual QA with actual screenshots; inspect mobile layout, typography, menus, interactions.
- Unit/integration tests of navigation, storage, migrations, content schemas and citations.
- Accessibility checks and reduced-motion behaviour.
- Adversarial cases: hallucinated source, false religious/historical certainty, prompt injection in a source, unwanted Field Book rewrite, AI outage, corrupted save and interrupted migration.
- Blind learner tests: compare what they can explain **before versus after** the encounter, and what they still misunderstand.

**Exit:** Critical flows work reproducibly; failures are recorded; an ordinary learner can understand the product.

### Gate 5 — Small beta, only then expansion

- Invite a limited, diverse tester group.
- Track confusion, completion of authentic tasks, source use, corrections, return by choice, data loss, and cost.
- Expand one Wing at a time. Keep the same educational and technical gates.

**Exit:** We have evidence of usefulness, not just screenshots and enthusiastic conversations.

---

## 11. The session plan for 4 November 2026

**Primary objective:** Finish the first day's work with a *small, working, inspectable foundation* and a prioritized legacy-content inventory, not 50 new rooms.

### Step A — Verify the source material

Open the latest original Mystery School / Sovereign Sol files or repositories and confirm what is actually available. Record filenames, version, working platform, screenshots, defects, feature list, and provenance. If those files aren't available, don't pretend they've been audited—work from the charter and flag missing inputs.

### Step B — Freeze a one-page vertical-slice specification

Decide only what the first journey needs: entry, one destination, one authored encounter, one response exercise, one Field Book entry, one return path. Keep the eventual three-encounter Wing as the next expansion milestone.

### Step C — Create the new project foundation

Build the fresh app scaffold with a distinct new directory/repository. Do not edit the legacy application in place. Establish a design system, routing, simple schemas, and persistent local storage.

### Step D — Make the first interaction real

A visitor opens the app, enters the Atrium, chooses **The Fire & the Sacred**, reads a substantial authored encounter, submits a thought, saves it to the Field Book, refreshes, and finds it again.

### Step E — Take screenshots and run tests

Review actual UI at phone and desktop widths, read the lesson as a novice, verify saved work after refresh, and write a short failure list. Fix a serious layout or state issue before adding more features.

### The first-day definition of done

- [ ] Legacy sources catalogued or marked explicitly unavailable.
- [ ] New foundation isolated from legacy code.
- [ ] Atrium, Classroom, and Field Book exist as connected routes or views.
- [ ] One meaningful *authored* lesson is accessible without a live model.
- [ ] Learner can make and recover a Field Book entry after refresh.
- [ ] At least one mobile-width and one desktop screenshot reviewed.
- [ ] Known defects and immediate next actions documented.

**If time is limited:** Protect persistence, readable teaching, and navigation. Cut visual effects before cutting educational substance.

---

## 12. Acceptance tests that must eventually exist

| Test | Expected behaviour |
|---|---|
| **Guest entry** | Start learning without mandatory registration |
| **Real lesson** | Learner receives meaningful explanation, not only generic chat |
| **Source transparency** | Inspect where consequential historical/scientific claims came from |
| **Speculation boundary** | Strange claims are marked and tested, not laundered into fact |
| **Student disagreement** | Challenge a teacher without penalty or pressure |
| **Persistence** | Notes survive refresh, restart and ordinary upgrades |
| **Data ownership** | Export notes; delete local learning data intentionally |
| **Offline / outage** | Core lesson and Field Book remain available |
| **Revision integrity** | A lesson correction does not silently alter prior student notes |
| **AI containment** | Untrusted sources cannot command the assistant or write durable state |
| **Accessible navigation** | Keyboard, screen reader and reduced-motion paths work |
| **Learning outcome** | Student can explain and apply a distinction after the session |

The final item is the essential test. Most of the others exist to make it possible and trustworthy.

---

## 13. Explicitly deferred / not part of the first release

- Recreating every old Wing, hundreds of subjects, or the entire historical canon.
- A full 3D game engine or vast procedural academy.
- Autonomous AI administrators, agents with broad external tool privileges, or claims of self-governing conscious faculty.
- In-app religious authority, divination presented as certain prediction, or manufactured devotion to AI.
- Paying for a “morally superior” teacher; false competence claims.
- Compulsory accounts, social-pressure mechanics, or streak punishment.
- Accredited qualifications, medical or legal instruction, or minors-specific deployment without appropriate safeguards.
- AI simulation tests marketed as proofs of real-world safety.
- Unverified historical claims turned into beautiful but misleading teaching materials.

---

## 14. Decisions held open intentionally

These are genuine future decisions, **not blockers to the first scaffold**:

1. Final front-end framework and visual rendering technique after device and performance testing.
2. Whether the Atrium uses 2D illustration, 2.5D layered space, light 3D, or a hybrid.
3. Cloud AI provider(s), cost ceilings, and offline teacher fallback.
4. Final faculty names after legacy audit and role testing.
5. Content license, distribution model, donation structure, and publication permissions.
6. Whether and when multi-device sync is warranted, given privacy obligations.
7. Age range and child-safety design for any future youth offering.

**Do not let these open decisions justify another month of planning instead of one working learner journey.**

---

## 15. Notes for any frontier AI collaborator taking the handoff

You are joining an ongoing Lycheetah effort. Read the documents listed at the top first; inspect actual files before making claims about their implementation.

- The founder wants a **beautiful and genuinely deep learning world**, not a conventional school dashboard.
- Work on a **clean foundation** and treat legacy code as read-only until specifically authorized.
- Prefer small, finished, tested vertical slices over giant unverified feature drops.
- Separate established evidence, interpretation, speculation, fiction, and UI atmosphere.
- Preserve user data and show the effects of changes before calling a system safe.
- Be constructively critical. Test whether a simpler approach performs just as well.
- If a lesson needs a source, obtain a real source; do not invent citations or simulate academic confidence.
- Treat faculty as engineered teaching roles, not spiritual superiors.
- Do not add unrelated Lycheetah integrations merely because they exist.
- End each development session with versioned files, tested behaviour, screenshots when useful, remaining defects, and a concise handoff.

### End-of-session report template

```text
Build/version:
Files created or changed:
What now works (verified):
What was only designed or drafted:
Tests and screenshots performed:
What failed or remains uncertain:
What was intentionally not changed:
Next smallest useful milestone:
```

---

## 16. Final founding statement

The Lycheetah Mystery School should help people travel from wonder to understanding without forcing them to abandon wonder along the way.

It should be beautiful enough to invite curiosity, rigorous enough to survive disagreement, compassionate enough to welcome beginners, and independent enough that a learner can leave carrying everything they discovered.

No model, teacher, founder, or institution becomes unquestionable simply because it can speak persuasively about ancient mysteries or future intelligence.

**The highest achievement of this school is a student who no longer needs the school to do their thinking for them.**

The mountain is enormous. We begin with one deliberate cut.

**The lantern stays lit.**

— Aster / First Cartographer  
*Lycheetah Mystery School, refoundation handoff — 3 November 2026*
