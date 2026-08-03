import type {
  TruthPressureShadowDataset,
  TruthPressureShadowSummary,
} from './shadow-store-core.ts';
import { summarizeShadowDataset } from './shadow-store-core.ts';

export type PressureBin = {
  label: string;
  minInclusive: number;
  maxInclusive: number;
  count: number;
};

export type WarningFrequency = {
  warning: string;
  count: number;
  share: number;
};

export type DeltaSummary = {
  comparableCount: number;
  meanSignedDelta: number | null;
  meanAbsoluteDelta: number | null;
  minimumDelta: number | null;
  maximumDelta: number | null;
  positiveCount: number;
  negativeCount: number;
  zeroCount: number;
};

export type EngineeringGate = {
  id: string;
  label: string;
  state: 'PASS' | 'OPEN' | 'FAIL';
  detail: string;
};

export type ShadowEvidenceReport = {
  version: 'TP-SHADOW-EVIDENCE-0.7';
  generatedAt: string;
  datasetVersion: string;
  privacy: 'NO_RAW_CONTENT';
  summary: TruthPressureShadowSummary;
  pressureBins: PressureBin[];
  warningFrequencies: WarningFrequency[];
  delta: DeltaSummary;
  triggerDisagreements: number;
  gates: EngineeringGate[];
  releaseState: 'COLLECTING' | 'ENGINEERING_REVIEW_REQUIRED' | 'ENGINEERING_GATE_MET';
  boundaries: string[];
};

const finite = (value: unknown): value is number =>
  typeof value === 'number' && Number.isFinite(value);

export function buildPressureBins(values: number[]): PressureBin[] {
  const bins: PressureBin[] = [
    { label: '0.00–0.19', minInclusive: 0, maxInclusive: 0.199999999, count: 0 },
    { label: '0.20–0.39', minInclusive: 0.2, maxInclusive: 0.399999999, count: 0 },
    { label: '0.40–0.59', minInclusive: 0.4, maxInclusive: 0.599999999, count: 0 },
    { label: '0.60–0.79', minInclusive: 0.6, maxInclusive: 0.799999999, count: 0 },
    { label: '0.80–1.00', minInclusive: 0.8, maxInclusive: 1, count: 0 },
  ];

  for (const value of values) {
    if (!finite(value) || value < 0 || value > 1) continue;
    const bin = bins.find(
      candidate => value >= candidate.minInclusive && value <= candidate.maxInclusive,
    );
    if (bin) bin.count++;
  }
  return bins;
}

export function summarizeWarnings(dataset: TruthPressureShadowDataset): WarningFrequency[] {
  const counts = new Map<string, number>();
  for (const record of dataset.records) {
    for (const warning of new Set(record.candidate.warnings)) {
      counts.set(warning, (counts.get(warning) ?? 0) + 1);
    }
  }

  const total = dataset.records.length;
  return [...counts.entries()]
    .map(([warning, count]) => ({
      warning,
      count,
      share: total ? count / total : 0,
    }))
    .sort((a, b) => b.count - a.count || a.warning.localeCompare(b.warning));
}

export function summarizePressureDeltas(
  dataset: TruthPressureShadowDataset,
): DeltaSummary {
  const values = dataset.records
    .map(record => record.deltas.normalizedPressure)
    .filter(finite);

  if (!values.length) {
    return {
      comparableCount: 0,
      meanSignedDelta: null,
      meanAbsoluteDelta: null,
      minimumDelta: null,
      maximumDelta: null,
      positiveCount: 0,
      negativeCount: 0,
      zeroCount: 0,
    };
  }

  const signed = values.reduce((sum, value) => sum + value, 0) / values.length;
  const absolute = values.reduce((sum, value) => sum + Math.abs(value), 0) / values.length;

  return {
    comparableCount: values.length,
    meanSignedDelta: signed,
    meanAbsoluteDelta: absolute,
    minimumDelta: Math.min(...values),
    maximumDelta: Math.max(...values),
    positiveCount: values.filter(value => value > 0).length,
    negativeCount: values.filter(value => value < 0).length,
    zeroCount: values.filter(value => value === 0).length,
  };
}

export function buildEngineeringGates(
  dataset: TruthPressureShadowDataset,
  summary = summarizeShadowDataset(dataset),
): EngineeringGate[] {
  const nonFiniteCount = dataset.records.filter(record => {
    const values = [
      record.candidate.piNormalized,
      record.candidate.piCanon,
      record.candidate.evidence,
      record.candidate.explanatoryPower,
      record.candidate.strain,
      record.legacy?.truthPressure,
      record.legacy?.coherence,
      record.deltas.normalizedPressure,
    ].filter(value => value !== null && value !== undefined);
    return values.some(value => !finite(value));
  }).length;

  const outOfRangeNormalized = dataset.records.filter(record =>
    record.candidate.piNormalized < 0 || record.candidate.piNormalized > 1
  ).length;

  const rawContentFlag = dataset.privacy !== 'NO_RAW_CONTENT' ||
    dataset.records.some(record => record.privacy !== 'NO_RAW_CONTENT');

  return [
    {
      id: 'GATE-SAMPLE',
      label: 'Minimum engineering sample',
      state: summary.total >= 100 ? 'PASS' : 'OPEN',
      detail: `${summary.total}/100 privacy-safe shadow comparisons collected.`,
    },
    {
      id: 'GATE-FINITE',
      label: 'Finite numerical outputs',
      state: nonFiniteCount === 0 ? 'PASS' : 'FAIL',
      detail: nonFiniteCount === 0
        ? 'No NaN or infinite values found.'
        : `${nonFiniteCount} record(s) contain invalid numerical values.`,
    },
    {
      id: 'GATE-RANGE',
      label: 'Normalized range integrity',
      state: outOfRangeNormalized === 0 ? 'PASS' : 'FAIL',
      detail: outOfRangeNormalized === 0
        ? 'All normalized candidate values are within [0,1].'
        : `${outOfRangeNormalized} record(s) fall outside [0,1].`,
    },
    {
      id: 'GATE-PRIVACY',
      label: 'No raw-content contract',
      state: rawContentFlag ? 'FAIL' : 'PASS',
      detail: rawContentFlag
        ? 'A dataset or record violates NO_RAW_CONTENT.'
        : 'Dataset and records declare NO_RAW_CONTENT.',
    },
    {
      id: 'GATE-AUTO-REORG',
      label: 'No text-mode structural authority',
      state: dataset.records.every(record =>
        record.inputClass !== 'TEXT' || record.candidate.reviewState === 'TRIAGE_ONLY'
      ) ? 'PASS' : 'FAIL',
      detail: 'Every text-mode record must remain TRIAGE_ONLY.',
    },
    {
      id: 'GATE-DISAGREEMENT-REVIEW',
      label: 'Trigger disagreements reviewed',
      state: summary.triggerDisagreements === 0 ? 'PASS' : 'OPEN',
      detail: summary.triggerDisagreements === 0
        ? 'No comparable trigger disagreements are currently recorded.'
        : `${summary.triggerDisagreements} trigger disagreement(s) require human review. No automatic pass threshold is assumed.`,
    },
  ];
}

export function buildShadowEvidenceReport(
  dataset: TruthPressureShadowDataset,
  now = new Date().toISOString(),
): ShadowEvidenceReport {
  const summary = summarizeShadowDataset(dataset);
  const gates = buildEngineeringGates(dataset, summary);
  const failed = gates.some(gate => gate.state === 'FAIL');
  const open = gates.some(gate => gate.state === 'OPEN');

  return {
    version: 'TP-SHADOW-EVIDENCE-0.7',
    generatedAt: now,
    datasetVersion: dataset.version,
    privacy: 'NO_RAW_CONTENT',
    summary,
    pressureBins: buildPressureBins(
      dataset.records.map(record => record.candidate.piNormalized),
    ),
    warningFrequencies: summarizeWarnings(dataset),
    delta: summarizePressureDeltas(dataset),
    triggerDisagreements: summary.triggerDisagreements,
    gates,
    releaseState: failed
      ? 'ENGINEERING_REVIEW_REQUIRED'
      : open
        ? 'COLLECTING'
        : 'ENGINEERING_GATE_MET',
    boundaries: [
      'Engineering gates do not establish scientific validity.',
      'A 100-case sample is a release-readiness checkpoint, not calibration.',
      'Trigger disagreement has no invented acceptable rate; each comparable disagreement requires review.',
      'The report stores no raw analyzed text.',
    ],
  };
}

function pct(value: number | null): string {
  return value === null ? 'n/a' : `${Math.round(value * 1000) / 10}%`;
}

export function renderShadowEvidenceMarkdown(report: ShadowEvidenceReport): string {
  const warningRows = report.warningFrequencies.length
    ? report.warningFrequencies
        .map(item => `| ${item.warning.replaceAll('|', '\\|')} | ${item.count} | ${pct(item.share)} |`)
        .join('\n')
    : '| None recorded | 0 | 0% |';

  const binRows = report.pressureBins
    .map(bin => `| ${bin.label} | ${bin.count} |`)
    .join('\n');

  const gateRows = report.gates
    .map(gate => `| ${gate.id} | ${gate.label} | ${gate.state} | ${gate.detail.replaceAll('|', '\\|')} |`)
    .join('\n');

  return `# Truth Pressure Shadow Evidence Report

**Version:** ${report.version}  
**Generated:** ${report.generatedAt}  
**Release state:** ${report.releaseState}  
**Privacy:** ${report.privacy}

## Dataset

- Total records: ${report.summary.total}
- Text records: ${report.summary.text}
- Structured records: ${report.summary.structured}
- Onion records: ${report.summary.onion}
- Candidate warnings: ${report.summary.candidateWarnings}
- Trigger agreements: ${report.summary.triggerAgreements}
- Trigger disagreements: ${report.summary.triggerDisagreements}
- Trigger not comparable: ${report.summary.triggerNotComparable}
- Mean candidate pressure: ${pct(report.summary.meanCandidatePressure)}
- Mean legacy pressure: ${pct(report.summary.meanLegacyPressure)}

## Engineering gates

| ID | Gate | State | Detail |
|---|---|---|---|
${gateRows}

## Candidate pressure distribution

| Normalized range | Count |
|---|---:|
${binRows}

## Legacy/candidate delta

- Comparable records: ${report.delta.comparableCount}
- Mean signed delta: ${report.delta.meanSignedDelta ?? 'n/a'}
- Mean absolute delta: ${report.delta.meanAbsoluteDelta ?? 'n/a'}
- Minimum delta: ${report.delta.minimumDelta ?? 'n/a'}
- Maximum delta: ${report.delta.maximumDelta ?? 'n/a'}
- Candidate higher: ${report.delta.positiveCount}
- Candidate lower: ${report.delta.negativeCount}
- Equal: ${report.delta.zeroCount}

## Warning frequencies

| Warning | Count | Dataset share |
|---|---:|---:|
${warningRows}

## Boundaries

${report.boundaries.map(boundary => `- ${boundary}`).join('\n')}
`;
}
