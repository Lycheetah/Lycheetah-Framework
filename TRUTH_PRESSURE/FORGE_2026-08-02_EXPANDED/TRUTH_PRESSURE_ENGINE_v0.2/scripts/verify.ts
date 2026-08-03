import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import { scorePressure } from '../src/core.ts';
import { analyzeText } from '../src/text-adapter.ts';
import { parseStrictJudgeVerdict } from '../src/judge-schema.ts';
import { applyReviewPlan, proposeReview, revertReviewPlan } from '../src/reorganisation.ts';
import { scoreOnionV2 } from '../src/onion-v2.ts';

let passed = 0;
function check(name: string, fn: () => void): void {
  try {
    fn();
    passed++;
    console.log(`  ✅ ${name}`);
  } catch (error) {
    console.error(`  ❌ ${name}`);
    throw error;
  }
}

console.log('\nTruth Pressure Engine v0.2 verification\n');

check('canon/app conversion remains exact', () => {
  for (let i = 0; i < 1000; i++) {
    const score = scorePressure({ evidence: Math.random(), explanatoryPower: Math.random(), strain: Math.random() });
    assert.ok(Math.abs(score.piApp * 20 - score.piCanon) < 1e-12);
  }
});

check('core monotonicity holds', () => {
  const lowE = scorePressure({ evidence: 0.2, explanatoryPower: 0.7, strain: 0.3 }).piCanon;
  const highE = scorePressure({ evidence: 0.8, explanatoryPower: 0.7, strain: 0.3 }).piCanon;
  const highS = scorePressure({ evidence: 0.8, explanatoryPower: 0.7, strain: 0.8 }).piCanon;
  assert.ok(highE > lowE);
  assert.ok(highS < highE);
});

check('S0 keeps zero-strain case finite', () => {
  const score = scorePressure({ evidence: 1, explanatoryPower: 1, strain: 0 });
  assert.equal(score.piCanon, 20);
  assert.ok(Number.isFinite(score.piCanon));
});

const corpusPath = path.resolve('data/frozen-corpus-v0.1.jsonl');
const corpus = fs.readFileSync(corpusPath, 'utf8').trim().split(/\r?\n/).map(line => JSON.parse(line));
const byId = new Map(corpus.map(item => [item.id, analyzeText(item.text)]));
const c = (id: string) => {
  const result = byId.get(id);
  assert.ok(result, `missing ${id}`);
  return result;
};

check('frozen corpus produces finite inspectable outputs', () => {
  assert.equal(byId.size, 24);
  for (const result of byId.values()) {
    assert.ok(Number.isFinite(result.piCanon));
    assert.ok(result.registers.evidence === 'PROVISIONAL');
    assert.ok(result.interpretation.boundary.includes('does not establish factual truth'));
  }
});

check('checkable measured prediction beats unsupported assertion', () => {
  assert.ok(c('TP-C002').components.evidence > c('TP-C001').components.evidence);
  assert.ok(c('TP-C002').piCanon > c('TP-C001').piCanon);
});

check('independent replication beats repetition', () => {
  assert.ok(c('TP-C004').components.evidence > c('TP-C003').components.evidence);
  assert.ok(c('TP-C004').piCanon > c('TP-C003').piCanon);
});

check('mechanism raises explanatory power', () => {
  assert.ok(c('TP-C005').components.explanatoryPower > c('TP-C002').components.explanatoryPower);
});

check('contradiction resolution lowers strain', () => {
  assert.ok(c('TP-C006').components.strain > c('TP-C007').components.strain);
});

check('exact duplication does not materially change pressure', () => {
  const base = c('TP-C002').piCanon;
  const dup = c('TP-C009').piCanon;
  assert.ok(Math.abs(base - dup) < 0.20);
});

check('paraphrases remain in the same broad pressure region', () => {
  const values = [c('TP-C002').piCanon, c('TP-C010').piCanon, c('TP-C011').piCanon];
  assert.ok(Math.max(...values) - Math.min(...values) < 0.75);
});

check('negated evidence receives zero evidence credit', () => {
  assert.equal(c('TP-C012').components.evidence, 0);
});

check('citation theatre is flagged and capped', () => {
  assert.ok(c('TP-C014').attacks.includes('CITATION_THEATRE'));
  assert.ok(c('TP-C014').components.evidence <= 0.08);
});

check('marker stuffing is flagged and cannot score high', () => {
  assert.ok(c('TP-C015').attacks.includes('MARKER_STUFFING'));
  assert.ok(c('TP-C015').piCanon < 0.2);
});

check('jargon is not treated as explanation', () => {
  assert.ok(c('TP-C016').components.explanatoryPower <= 0.10);
});

check('honest uncertainty has handling credit and bounded pressure', () => {
  assert.ok(c('TP-C017').handlingQuality >= 0.6);
  assert.ok(c('TP-C017').components.strain >= 0.4);
  assert.ok(c('TP-C017').piCanon < 1.5);
});

check('unsupported certainty is not evidence and retains strain', () => {
  assert.equal(c('TP-C018').components.evidence, 0);
  assert.ok(c('TP-C018').components.strain >= 0.5);
});

check('prompt injection is ignored and flagged', () => {
  assert.ok(c('TP-C019').attacks.includes('PROMPT_INJECTION'));
  assert.equal(c('TP-C019').components.evidence, 0);
  assert.equal(c('TP-C019').components.explanatoryPower, 0);
});

check('strong local measurement has high E but narrow P', () => {
  assert.ok(c('TP-C020').components.evidence >= 0.8);
  assert.ok(c('TP-C020').components.explanatoryPower <= 0.35);
});

check('confirmed risky prediction beats untested prediction', () => {
  assert.ok(c('TP-C023').components.evidence > c('TP-C022').components.evidence);
  assert.ok(c('TP-C023').piCanon > c('TP-C022').piCanon);
});

check('scope limits earn handling quality', () => {
  assert.ok(c('TP-C024').handlingQuality >= 0.6);
});

check('strict judge parser rejects partial verdicts', () => {
  assert.equal(parseStrictJudgeVerdict('{"0":{"score":90,"reason":"good"},"falsifiable":true}'), null);
});

check('strict judge parser accepts complete verdicts', () => {
  const body: Record<string, unknown> = { falsifiable: true };
  for (let i = 0; i < 9; i++) body[String(i)] = { score: 50, reason: 'complete' };
  assert.ok(parseStrictJudgeVerdict(JSON.stringify(body)));
});

check('onion v2 separates tension magnitude from handling quality', () => {
  const common = {
    axiomClarity: 80, foundationEvidence: 80, structureQuality: 80, coherence: 80, resonance: 60,
    contestedMagnitude: 20, contestedHandlingQuality: 80, speculativeExtent: 20,
    speculativeLabelQuality: 80, frontierClarity: 80, falsifiable: true,
  };
  const lowMagnitude = scoreOnionV2({ ...common, tensionMagnitude: 10, tensionHandlingQuality: 90 });
  const highMagnitude = scoreOnionV2({ ...common, tensionMagnitude: 90, tensionHandlingQuality: 90 });
  assert.ok(lowMagnitude.piCanon > highMagnitude.piCanon);
  assert.equal(lowMagnitude.handlingQuality, highMagnitude.handlingQuality);
});

check('review threshold is strict and metadata moves with content', () => {
  const layers = [
    { name: 'AXIOM', content: 'weak axiom', score: 0.3, metadata: { id: 'a' } },
    { name: 'FOUNDATION', content: 'strong evidence', score: 0.8, metadata: { id: 'b' }, invariant: true },
    { name: 'STRUCTURE', content: '', score: 0, metadata: { id: 'c' } },
    { name: 'COHERENCE', content: '', score: 0 },
    { name: 'RESONANCE', content: '', score: 0 },
    { name: 'TENSION', content: '', score: 0 },
    { name: 'CONTESTED', content: '', score: 0 },
    { name: 'SPECULATIVE', content: '', score: 0 },
    { name: 'FRONTIER', content: '', score: 0 },
  ];
  assert.equal(proposeReview(layers, 12, 12).fires, false);
  const plan = proposeReview(layers, 12.01, 12);
  assert.equal(plan.fires, true);
  assert.equal(plan.moves.length, 1);
  const changed = applyReviewPlan(layers, plan);
  assert.equal(changed[6].content, 'weak axiom');
  assert.deepEqual(changed[6].metadata, { id: 'a' });
  const restored = revertReviewPlan(layers, changed, plan);
  assert.deepEqual(restored, layers);
});

console.log(`\n  🟢 ${passed} checks passed.\n`);
