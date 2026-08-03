// ── Π GATE — the Truth Pressure scorer, held to the school's own canon ───────
//
//   npm run verify:truth-pressure
//
// `school-content.ts` teaches the formula as: "Π = (E·P)/(S + S₀), read slowly.
// Evidence times explanatory power, over the entropy of what supports the belief,
// plus a floor." The scorer in `lib/cascade-score.ts` is the one place the app
// actually COMPUTES that, and until 2026-07-28 it did not implement it.
//
// ⚠ WHAT THIS GATE EXISTS TO STOP EVER HAPPENING AGAIN. The old implementation
// used RAW COUNTS for E and P, so their product grew quadratically with document
// length; there was no S₀; and `Math.min(1, …)` clamped the result. MEASURED
// consequence: Π read exactly 1.000 for every text past ~30 words — including a
// text with coherence 0, i.e. maximum self-contradiction. Every entry in the
// Library displayed Π 1.00. The headline number of the CASCADE feature was a
// constant wearing a formula's clothes, and it type-checked perfectly for months.
//
// So none of the checks below assert the FORMULA. They assert the BEHAVIOUR the
// formula is supposed to produce — because the broken version could recite the
// formula in a comment and still be a constant.

import { scoreCASCADE } from '../lib/cascade-score.ts';

let failures = 0;
const check = (name: string, ok: boolean, detail: string) => {
  console.log(`  ${ok ? '✅' : '❌'} ${name}`);
  if (detail) console.log(`      ${detail}`);
  if (!ok) failures++;
};

const INV = 'This is the foundation. By definition it is load-bearing. The principle is proven. Axiom. Theorem. It cannot be violated. ';
const THY = 'Because the mechanism predicts it, therefore the framework explains the pattern. Evidence suggests the model accounts for this, thus we can conclude. ';
const CONTRA = 'However this contradicts the paradox. On the other hand it is unclear and unresolved. Although, conversely, the tension remains. ';

console.log('\n  Π = (E·P)/(S + S₀) — behavioural gate\n');

// 1. NOT PINNED. The defect that motivated the gate.
const long = scoreCASCADE((INV + THY).repeat(12));
check('a long, dense, coherent text does not pin at 1.000',
  long.truthPressure < 1,
  `Π = ${long.truthPressure} on ${long.wordCount} words`);

// 2. LENGTH-INVARIANT. Saying the same thing five times is not five times the support.
const short = scoreCASCADE((INV + THY).repeat(2));
const longer = scoreCASCADE((INV + THY).repeat(10));
check('Π is invariant under repetition (density, not volume)',
  Math.abs(short.truthPressure - longer.truthPressure) < 0.02,
  `${short.wordCount}w → ${short.truthPressure}   ${longer.wordCount}w → ${longer.truthPressure}`);

// 3. DIRECTION. Canon: high entropy S ⇒ LOWER Π. The old code got this backwards
//    in its comment while the clamp hid the behaviour entirely.
const clean = scoreCASCADE((INV + THY).repeat(3));
const messy = scoreCASCADE((INV + THY).repeat(3) + CONTRA.repeat(3));
check('contradiction lowers Π (S behaves like entropy, not coherence)',
  messy.truthPressure < clean.truthPressure,
  `coherent Π=${clean.truthPressure}  ·  self-contradicting Π=${messy.truthPressure}`);

// 4. THE S₀ FLOOR. A perfectly coherent claim must not diverge — the curriculum's
//    own justification for the floor existing at all.
const perfect = scoreCASCADE(INV.repeat(8) + THY.repeat(8));
check('a perfectly coherent text stays finite and ≤ 1 (S₀ holds the floor)',
  Number.isFinite(perfect.truthPressure) && perfect.truthPressure <= 1 && perfect.truthPressure > 0,
  `Π = ${perfect.truthPressure} with zero contradiction markers`);

// 5. THE PRODUCT. E·P means evidence ALONE is not truth pressure, and neither is
//    assertion alone. A claim with power but no evidence must not score.
const assertionOnly = scoreCASCADE('This is the foundation. By definition. Axiom. It cannot be violated. The principle is proven.');
check('assertion without evidence does not earn pressure (E·P is a product)',
  assertionOnly.truthPressure < 0.15,
  `pure assertion, no causal reasoning → Π = ${assertionOnly.truthPressure}`);

// 6. MONOTONE AND DISCRIMINATING across genuinely different material.
const weak = scoreCASCADE('I walked to the river this morning. The water was high and the ducks had moved to the far bank.');
const mid = scoreCASCADE('The principle is simple: water runs downhill because gravity acts on mass. The framework predicts it.');
check('weak prose < reasoned claim (the scale actually discriminates)',
  weak.truthPressure < mid.truthPressure,
  `plain prose Π=${weak.truthPressure}  ·  reasoned Π=${mid.truthPressure}`);

console.log(failures === 0
  ? `\n  🟢 Π gate passed — the scorer implements the canon it teaches.\n`
  : `\n  🔴 ${failures} failing — the scorer and the curriculum disagree.\n`);
process.exit(failures ? 1 : 0);
