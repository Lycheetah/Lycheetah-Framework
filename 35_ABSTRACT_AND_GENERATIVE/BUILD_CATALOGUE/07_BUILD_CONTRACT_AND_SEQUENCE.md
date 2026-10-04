# Build one generation completely

**Status: PROPOSED implementation contract and sequence. Mac chooses the next build.**

The catalogue is a queue of possibilities. It does not replace the current portfolio router, product owner or release plan. Pick one first interaction; do not open thirty-one parallel builds.

## Proposed first choices

| Purpose | Candidate | Why this can start small | First consequential uncertainty |
|---|---|---|---|
| Useful tool | B001 Witness Desk | Existing runtime contracts and explicit fixtures | Can a new user explain a decision without trusting the visual badge? |
| Original game | B016 Resonance Forge | Small mathematical state, visible feedback, optional sound | Is tuning enjoyable after the first discovery? |
| Agent-safety demonstration | B031 Recovery Race Lab | Public deterministic transaction fixtures | Can someone predict the second-writer failure after using it? |
| Long game | B030 Living Siege | Carries Mac’s map, party and progression direction | Does one complete region produce meaningful build choices? |

These are recommendations from the authoring seat, not approved priorities or published products. Existing tower-defence work remains in its game home; the Framework card is its source brief.

## First playable or useful slice

1. Resolve the current source, owner, dependencies and evidence status. List the exact files the batch may change.
2. Write a five-line user journey: entry, input, action, feedback and saved result. Include failure and voluntary exit.
3. Build a complete local loop. A browser prototype should initially use manual inputs or a deterministic model, with no mandatory account or model API.
4. Observe the result at the intended phone and desktop sizes. Include keyboard access, readable labels, at least 44 CSS-pixel tap targets, reduced motion and audio opt-in where relevant.
5. Test the card’s distinct acceptance condition and one adversarial case. Use the existing implementation as the source of truth, or label a port and compare it against fixed reference fixtures.
6. Save a receipt: source version, exact parameters, commit, observed result, failures, device witness and limits. Let Mac judge the feel before expanding the system.

For a game, the slice needs a complete encounter, a loss state, a reward, a save and a return. For a tool, it needs a legitimate input, an explained output, a refusal case and an export. A menu or a chart alone does not meet either definition.

## Architecture for a browser prototype

- Keep simulation/domain state separate from rendering and sound. The renderer reads state; it does not secretly own game rules or evidence decisions.
- Use an explicit seeded random generator and replayable events where reproducibility matters. Stop loops and audio when the screen is inactive.
- Give persistence a versioned schema, validate imports and preserve the previous save before migration. Detect storage failure; offer export and reset without pretending the save succeeded.
- Use local state by default and explain storage. No analytics or provider transfer is implied by this contract. Add an external service only in a separately scoped implementation.
- Choose one visual world, original assets and a readable hierarchy. Domain explanations belong beside decisions; source notes can sit in an optional inspect view.
- Put code, automated checks and assets in the product owner’s established repository. This folder remains the brief/index home, not a parallel implementation tree.

## Numbers, progression and sustainable play

B030 should support three rhythms: a satisfying moment-to-moment fight, a long campaign session, and an account history across sessions. Tower XP, hero paths and prestige must introduce decisions at those different scales.

Make the arithmetic inspectable. Separate additive modifiers, multiplicative modifiers, armour rules and temporary effects. Define caps or diminishing returns intentionally. Use numerically safe representation for very large values and test boundary cases; abbreviations must never hide negative values, overflow or unexplained jumps.

Prestige should make the next run strategically different through a chosen tree, route or capacity. It must state what resets and what survives before confirmation. An endless mode can be long without being literally unbounded: declare wave/resource limits, handle save growth, and define how difficulty and rewards scale. A longer map must create placement choices; empty travel distance alone is not depth.

Surprises should alter strategy while retaining a readable cause: a boss changes resistance, a route reveals a new resource, a tower evolves into a different role. Avoid purchased randomness, loss of progress for absence, forced notifications and rewards designed around compulsory return.

## Generating beyond this list

Use this recipe: **source mechanism → human action → state that changes → tension → inspectable artifact → falsifiable first test**. Combine two lenses only when both change the interaction. A new name or colour palette does not constitute a second mechanism.

Examples of productive tensions: speed versus evidence freshness; power versus reserve; memory versus a useful revision; consensus versus a minority’s constraint; synchronisation versus diversity. The product succeeds when the tension is felt and understood. It need not claim that the entire Framework theory is true.

## Promotion and stopping

Keep these dimensions separate: brief status, implementation status, evidence status and release status. Proposed → scoped → prototype → internally tested → device witnessed → released is a product path, not an automatic scientific promotion.

Stop or redesign when the source cannot support the promised action, the first loop needs too much ceremony, the result is indistinguishable from a simpler baseline, users cannot explain its failure, or the interesting mechanic encourages coercive use. Record the failure and retain the useful part.
