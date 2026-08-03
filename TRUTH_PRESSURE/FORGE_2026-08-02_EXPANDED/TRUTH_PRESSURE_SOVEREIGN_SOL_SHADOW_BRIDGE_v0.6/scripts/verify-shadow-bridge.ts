import assert from 'node:assert/strict';

import {
  buildAppViewModel,
  createShadowComparison,
} from '../lib/truth-pressure-rc/index.ts';
import {
  appendShadowRecord,
  createShadowRecorder,
  emptyShadowDataset,
  parseShadowDataset,
  summarizeShadowDataset,
  validateShadowRecord,
  type TruthPressureKeyValueStore,
} from '../lib/truth-pressure-integration/shadow-store-core.ts';
import {
  runTruthPressureBridge,
  runAndRecordTruthPressureBridge,
} from '../lib/truth-pressure-integration/shadow-service.ts';

class MemoryStore implements TruthPressureKeyValueStore {
  private values = new Map<string, string>();
  async getItem(key: string): Promise<string | null> {
    return this.values.get(key) ?? null;
  }
  async setItem(key: string, value: string): Promise<void> {
    this.values.set(key, value);
  }
  async removeItem(key: string): Promise<void> {
    this.values.delete(key);
  }
}

let passed = 0;
function check(name: string, fn: () => void | Promise<void>): Promise<void> {
  return Promise.resolve()
    .then(fn)
    .then(() => {
      passed++;
      console.log(`  ✅ ${name}`);
    });
}

console.log('\nTruth Pressure Sovereign Sol Shadow Bridge v0.6\n');

await check('off mode executes legacy only', () => {
  const result = runTruthPressureBridge('The model predicts the result.', 'off');
  assert.equal(result.mode, 'off');
  assert.equal(result.candidate, null);
  assert.equal(result.comparison, null);
  assert.equal(result.visible, 'LEGACY');
});

await check('shadow mode keeps legacy visible and builds candidate privately', () => {
  const result = runTruthPressureBridge(
    'A preregistered trial measured a 12 percent effect because component B mediates the process.',
    'shadow',
  );
  assert.equal(result.visible, 'LEGACY');
  assert.ok(result.candidate);
  assert.ok(result.comparison);
  assert.equal(result.comparison?.privacy, 'NO_RAW_CONTENT');
  assert.equal(result.candidate?.review.state, 'TRIAGE_ONLY');
});

await check('candidate preview remains triage-only', () => {
  const result = runTruthPressureBridge('Evidence was measured because a mechanism was proposed.', 'candidate-preview');
  assert.equal(result.visible, 'CANDIDATE_PREVIEW');
  assert.equal(result.candidate?.review.eligibleForStructuralProposal, false);
});

await check('shadow records contain no raw input text', () => {
  const secret = 'PRIVATE-SENTENCE-DO-NOT-STORE';
  const result = runTruthPressureBridge(`${secret}. A trial measured 12 percent.`, 'shadow');
  const serialized = JSON.stringify(result.comparison);
  assert.ok(!serialized.includes(secret));
  validateShadowRecord(result.comparison!);
});

await check('privacy validator rejects forbidden raw-content fields', () => {
  const candidate = buildAppViewModel({ kind: 'text', text: 'A measured result.' });
  const record = createShadowComparison(candidate, null);
  const poisoned = { ...record, rawText: 'secret' };
  assert.throws(() => validateShadowRecord(poisoned as typeof record), /forbidden field/);
});

await check('dataset is bounded to configured maximum', async () => {
  const store = new MemoryStore();
  const candidate = buildAppViewModel({ kind: 'text', text: 'A measured result.' });
  const record = createShadowComparison(candidate, null, { createdAt: '2026-08-02T00:00:00.000Z' });

  for (let i = 0; i < 5; i++) {
    await appendShadowRecord(store, { ...record, createdAt: `2026-08-02T00:00:0${i}.000Z` }, { maxRecords: 3 });
  }

  const raw = await store.getItem('truth-pressure-shadow-v0.6');
  const dataset = parseShadowDataset(raw, 3);
  assert.equal(dataset.records.length, 3);
  assert.equal(dataset.records[0]?.createdAt, '2026-08-02T00:00:02.000Z');
});

await check('serialized recorder prevents lost concurrent writes', async () => {
  const store = new MemoryStore();
  const recorder = createShadowRecorder(store, { maxRecords: 20 });
  const candidate = buildAppViewModel({ kind: 'text', text: 'A measured result.' });
  const base = createShadowComparison(candidate, null);

  await Promise.all(
    Array.from({ length: 10 }, (_, index) => recorder.record({
      ...base,
      createdAt: `2026-08-02T00:00:${String(index).padStart(2, '0')}.000Z`,
    })),
  );

  const dataset = await recorder.load();
  assert.equal(dataset.records.length, 10);
});

await check('run-and-record path persists one privacy-safe comparison', async () => {
  const store = new MemoryStore();
  const recorder = createShadowRecorder(store);
  const result = await runAndRecordTruthPressureBridge(
    'The measured result follows because the mechanism predicts it.',
    recorder,
    'shadow',
  );
  const dataset = await recorder.load();
  assert.equal(dataset.records.length, 1);
  assert.deepEqual(dataset.records[0], result.comparison);
});

await check('summary reports engineering comparison counts', async () => {
  const store = new MemoryStore();
  const recorder = createShadowRecorder(store);
  await runAndRecordTruthPressureBridge('The model predicts the result.', recorder, 'shadow');
  const summary = summarizeShadowDataset(await recorder.load());
  assert.equal(summary.total, 1);
  assert.equal(summary.text, 1);
  assert.equal(summary.triggerNotComparable, 1);
  assert.ok(summary.meanCandidatePressure !== null);
});

await check('invalid datasets fail closed', () => {
  assert.throws(() => parseShadowDataset('{broken'), /not valid JSON/);
  assert.throws(
    () => parseShadowDataset(JSON.stringify({ version: 'wrong', privacy: 'NO_RAW_CONTENT', records: [] })),
    /Unsupported shadow dataset version/,
  );
});

await check('empty dataset has explicit privacy contract', () => {
  const dataset = emptyShadowDataset(100, '2026-08-02T00:00:00.000Z');
  assert.equal(dataset.privacy, 'NO_RAW_CONTENT');
  assert.equal(dataset.maxRecords, 100);
  assert.equal(dataset.records.length, 0);
});

console.log(`\n  🟢 ${passed} bridge checks passed.\n`);
