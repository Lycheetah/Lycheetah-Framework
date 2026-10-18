# SXP-L v2.0 — Human Understanding Pilot Protocol (draft, not preregistered)

## Research question

Can new learners accurately distinguish **referents and discourse force** in short SXP-L utterances using a compact viewpoint marker? Compare against fully named SXP-L, controlled English, and structured JSON.

**Primary outcome:** correct selection from fixed options, reporting `correct / assigned` (including unsure and missing as not-correct). Secondary outcomes: correct/attempted, count unsure, count missing, approximate time-on-screen (descriptive only; not a reaction-time measurement). Report by format AND item category.

## Design

Within-participant four-representation exploratory task; between-cohort Latin-square allocation A–D. Each participant sees 32 **different** scenarios, eight in each format; each of the 32 scenarios is shown in every format across the four cohorts. Each format receives two subject-identification, two object-identification, two clarification-force, and two direct-utterance-force tasks per cohort. Order is deterministic shuffled, one shuffle per cohort.

The 24 scoped-clarification stimuli originate in actual `reference19.parse_native()` outputs, with independent limited confirmation by `oracle19.read()`. The eight direct-utterance controls parse through the inherited engine. English and JSON stimuli are constructed to match those machine-generated roles; they are not independently verified by an English semantics oracle.

**Learning conditions:** all participants see one short learner card explaining the grammar, symbols, and representational differences. This is *not* a test of zero-shot intuition; it is a short instructed comprehension task. There are no participant identifiers or server telemetry. There are no audio stimuli.

## Fixed evaluation decisions before real data

- Use the case IDs and key in `researcher/`; do not change these after collecting any data.
- Treat **unsure and missing as not correct** for the primary `correct / assigned` measure. Also report *attempted-only accuracy* and the counts of abstentions separately.
- Do not pool anonymous CSV files as if they represented distinct people unless consented and the organizer can establish they are distinct sessions. The raw export contains no stable participant identifier, by design.
- Report case mix, cohort balance, per-format accuracy and uncertainty. Do not publish inferential superiority claims from a few pilot participants.
- Do not infer understanding from the passing software tests or self-generated CSV scores.
- Record deviations, exclusions, dropouts, recruitment details and previous linguistic/programming familiarity before interpretation. A formal sample-size determination is required before confirmatory claims.

## Suggested first external validation

A small feasibility pilot of **at least one completely unfamiliar consenting volunteer per cohort** may reveal catastrophic instrument problems; four participants are far too few for conclusions. If feasible, invite a wider, genuinely independent sample under a reviewed protocol, with a study designer checking statistical power and accessibility. Consider the trade-off of mixed difficulty and within-person learning: substantial practice with SXP-L could affect later conditions.

Ask volunteers whether they found any wording confusing (outside the scored CSV), avoiding names or private content. Keep a separate record of any instrument edits; freeze version before comparing results.

## Threats to validity

1. **Baseline familiarity:** every participant already knows English; very few know SXP-L; experienced programmers may read JSON rapidly. A difference in score would reflect training and prior familiarity, not intrinsically better notation.
2. **Not independent semantics:** controlled English is a hand-authored paraphrase, and the JSON design reflects author decisions. Have uninvolved reviewers audit intended equivalence.
3. **Within-participant learning/fatigue:** 32 repeated-style items may induce pattern learning, despite the shuffle.
4. **Limited coverage:** only three verbs, four proper names, two viewpoint markers, and one clarification structure. No metaphor, free-form speech, audio, spontaneous dialogue, or general translation.
5. **No authentic speech:** a successful answer doesn't show the utterance occurred or that its content is true; no permission or action follows from it.
6. **No formal human-subject authorization:** this is a prototype evaluation instrument, not a funded or institutional research study.
7. **Timing:** browser-on-screen measurements mix reading, revisits, breaks and navigation. Do not analyze as controlled reaction time.
8. **Item difficulty not equal:** one four-case block has variants and lexical relationships that may differ in difficulty; the Latin square can balance item by cohort only with adequate recruitment.

## Privacy

The offline page has no network requests, does not require login, does not prompt for a name or email, and only exports CSV after a click. A researcher must explicitly receive a file to analyze it. Voluntary sharing of a CSV is not automatic consent to public release; ask separately.

## When to promote the research claim

Only when unfamiliar participants can independently learn the grammar and comprehend held-out clauses should we report actual human performance. Any potential advantage should be compared to tested baselines, with uncertainty intervals and adequate sample size. Until then, v2.0 is a **tested experimental instrument**, not an evaluated linguistic improvement.
