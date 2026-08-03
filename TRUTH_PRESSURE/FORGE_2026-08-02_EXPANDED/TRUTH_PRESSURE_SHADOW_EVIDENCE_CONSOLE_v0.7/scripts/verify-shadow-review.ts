import assert from 'node:assert/strict';

import {
  buildEngineeringGates,
  buildPressureBins,
  buildShadowEvidenceReport,
  renderShadowEvidenceMarkdown,
  summarizePressureDeltas,
  summarizeWarnings,
} from '../lib/truth-pressure-integration/shadow-analysis.ts';
import {
  buildShadowEvidenceExport,
  serializeShadowEvidenceExport,
} from '../lib/truth-pressure-integration/shadow-export.ts';
import {
  emptyShadowDataset,
  type TruthPressureShadowDataset,
} from '../lib/truth-pressure-integration/shadow-store-core.ts';
import type { ShadowComparisonRecord } from '../lib/truth-pressure-rc/index.ts';

function record(
  index: number,
  options: {
    candidate?: number;
    legacy?: number | null;
    warning?: string;
    disagreement?: boolean;
  } = {},
): ShadowComparisonRecord {
  const candidate = options.candidate ?? (index % 10) / 10;
  const legacy = options.legacy === undefined ? 0.2 : options.legacy;
  return {
    version: 'TP-SHADOW-0.5',
    createdAt: `2026-08-02T00:00:${String(index % 60).padStart(2, '0')}.000Z`,
    inputClass: 'TEXT',
    privacy: 'NO_RAW_CONTENT',
    inputLength: 100 + index,
    legacy: legacy === null ? null : {
      truthPressure: legacy,
      coherence: 80,
      reorganisationNeeded: options.disagreement ? true : false,
      dominantLayer: 'THEORY',
    },
    candidate: {
      engineVersion: '0.5.0-rc.1',
      mode: 'TEXT_TRIAGE',
      piNormalized: candidate,
      piCanon: candidate * 20,
      evidence: 0.4,
      explanatoryPower: 0.5,
      strain: 0.2,
      reviewState: 'TRIAGE_ONLY',
      warnings: options.warning ? [options.warning] : [],
    },
    deltas: {
      normalizedPressure: legacy === null ? null : candidate - legacy,
      legacyReorganiseVsCandidateReview: legacy === null
        ? 'NOT_COMPARABLE'
        : options.disagreement
          ? 'DISAGREE'
          : 'NOT_COMPARABLE',
    },
  };
}

function dataset(records: ShadowComparisonRecord[]): TruthPressureShadowDataset {
  return {
    ...emptyShadowDataset(250, '2026-08-02T00:00:00.000Z'),
    records,
  };
}

let passed = 0;
function check(name: string, fn: () => void): void {
  fn();
  passed++;
  console.log(`  ✅ ${name}`);
}

console.log('\nTruth Pressure Shadow Evidence Console v0.7\n');

check('pressure bins count all valid normalized values', () => {
  const bins = buildPressureBins([0, 0.2, 0.4, 0.6, 0.8, 1]);
  assert.deepEqual(bins.map(bin => bin.count), [1, 1, 1, 1, 2]);
});

check('warning frequencies are deduplicated per record', () => {
  const a = record(1, { warning: 'Text mode is provisional.' });
  a.candidate.warnings.push('Text mode is provisional.');
  const b = record(2, { warning: 'Text mode is provisional.' });
  const warnings = summarizeWarnings(dataset([a, b]));
  assert.equal(warnings[0]?.count, 2);
  assert.equal(warnings[0]?.share, 1);
});

check('delta summary preserves signed and absolute movement', () => {
  const summary = summarizePressureDeltas(dataset([
    record(1, { candidate: 0.7, legacy: 0.2 }),
    record(2, { candidate: 0.1, legacy: 0.2 }),
  ]));
  assert.equal(summary.comparableCount, 2);
  assert.ok(Math.abs((summary.meanSignedDelta ?? 0) - 0.2) < 1e-12);
  assert.ok(Math.abs((summary.meanAbsoluteDelta ?? 0) - 0.3) < 1e-12);
});

check('sample gate remains open below 100 records', () => {
  const gates = buildEngineeringGates(dataset(Array.from({ length: 99 }, (_, i) => record(i))));
  assert.equal(gates.find(gate => gate.id === 'GATE-SAMPLE')?.state, 'OPEN');
});

check('sample gate passes at 100 privacy-safe records', () => {
  const gates = buildEngineeringGates(dataset(Array.from({ length: 100 }, (_, i) => record(i))));
  assert.equal(gates.find(gate => gate.id === 'GATE-SAMPLE')?.state, 'PASS');
});

check('text records must remain triage-only', () => {
  const bad = record(1);
  bad.candidate.reviewState = 'REVIEW_SIGNAL_OPEN';
  const gates = buildEngineeringGates(dataset([bad]));
  assert.equal(gates.find(gate => gate.id === 'GATE-AUTO-REORG')?.state, 'FAIL');
});

check('disagreements are review-open rather than silently accepted', () => {
  const gates = buildEngineeringGates(dataset([record(1, { disagreement: true })]));
  assert.equal(gates.find(gate => gate.id === 'GATE-DISAGREEMENT-REVIEW')?.state, 'OPEN');
});

check('100 clean records can meet the engineering gate', () => {
  const report = buildShadowEvidenceReport(
    dataset(Array.from({ length: 100 }, (_, i) => record(i))),
    '2026-08-02T00:00:00.000Z',
  );
  assert.equal(report.releaseState, 'ENGINEERING_GATE_MET');
});

check('engineering report carries explicit scientific boundary', () => {
  const report = buildShadowEvidenceReport(dataset([]));
  assert.ok(report.boundaries.some(boundary => boundary.includes('do not establish scientific validity')));
});

check('export contains no raw content fields', () => {
  const data = dataset([record(1)]);
  const serialized = serializeShadowEvidenceExport(data, '2026-08-02T00:00:00.000Z');
  assert.ok(!serialized.includes('"rawText"'));
  assert.equal(buildShadowEvidenceExport(data).privacy, 'NO_RAW_CONTENT');
});

check('markdown report contains gates and boundaries', () => {
  const markdown = renderShadowEvidenceMarkdown(buildShadowEvidenceReport(dataset([])));
  assert.ok(markdown.includes('## Engineering gates'));
  assert.ok(markdown.includes('## Boundaries'));
});

console.log(`\n  🟢 ${passed} evidence-console checks passed.\n`);
