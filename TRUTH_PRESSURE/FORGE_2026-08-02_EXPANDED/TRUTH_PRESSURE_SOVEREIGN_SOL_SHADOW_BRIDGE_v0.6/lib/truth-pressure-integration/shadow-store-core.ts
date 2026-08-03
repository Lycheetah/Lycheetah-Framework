import type { ShadowComparisonRecord } from '../truth-pressure-rc/index.ts';
import {
  TRUTH_PRESSURE_DEFAULT_MAX_RECORDS,
  TRUTH_PRESSURE_SHADOW_DATASET_VERSION,
  TRUTH_PRESSURE_SHADOW_STORAGE_KEY,
} from './feature.ts';

export interface TruthPressureKeyValueStore {
  getItem(key: string): Promise<string | null>;
  setItem(key: string, value: string): Promise<void>;
  removeItem(key: string): Promise<void>;
}

export type TruthPressureShadowDataset = {
  version: typeof TRUTH_PRESSURE_SHADOW_DATASET_VERSION;
  privacy: 'NO_RAW_CONTENT';
  updatedAt: string;
  maxRecords: number;
  records: ShadowComparisonRecord[];
};

export type TruthPressureShadowSummary = {
  total: number;
  text: number;
  structured: number;
  onion: number;
  triggerAgreements: number;
  triggerDisagreements: number;
  triggerNotComparable: number;
  candidateWarnings: number;
  meanCandidatePressure: number | null;
  meanLegacyPressure: number | null;
};

const FORBIDDEN_KEYS = new Set([
  'text',
  'rawText',
  'inputText',
  'content',
  'prompt',
  'message',
  'claim',
  'sourceText',
]);

function finiteOrNull(value: unknown): number | null {
  return typeof value === 'number' && Number.isFinite(value) ? value : null;
}

function assertNoRawContent(value: unknown, path = 'record'): void {
  if (Array.isArray(value)) {
    value.forEach((item, index) => assertNoRawContent(item, `${path}[${index}]`));
    return;
  }
  if (!value || typeof value !== 'object') return;

  for (const [key, child] of Object.entries(value as Record<string, unknown>)) {
    if (FORBIDDEN_KEYS.has(key)) {
      throw new Error(`Privacy boundary violated: forbidden field "${path}.${key}".`);
    }
    assertNoRawContent(child, `${path}.${key}`);
  }
}

export function validateShadowRecord(record: ShadowComparisonRecord): void {
  if (record.privacy !== 'NO_RAW_CONTENT') {
    throw new Error('Shadow record must declare NO_RAW_CONTENT.');
  }
  if (record.version !== 'TP-SHADOW-0.5') {
    throw new Error(`Unsupported shadow record version: ${record.version}`);
  }

  const values = [
    record.candidate.piNormalized,
    record.candidate.piCanon,
    record.candidate.evidence,
    record.candidate.explanatoryPower,
    record.candidate.strain,
    record.legacy?.truthPressure,
    record.legacy?.coherence,
    record.deltas.normalizedPressure,
  ].filter((value): value is number => value !== undefined && value !== null);

  if (values.some(value => !Number.isFinite(value))) {
    throw new Error('Shadow record contains NaN or an infinite numeric value.');
  }

  assertNoRawContent(record);
}

export function emptyShadowDataset(
  maxRecords = TRUTH_PRESSURE_DEFAULT_MAX_RECORDS,
  now = new Date().toISOString(),
): TruthPressureShadowDataset {
  if (!Number.isInteger(maxRecords) || maxRecords < 1) {
    throw new Error('maxRecords must be a positive integer.');
  }
  return {
    version: TRUTH_PRESSURE_SHADOW_DATASET_VERSION,
    privacy: 'NO_RAW_CONTENT',
    updatedAt: now,
    maxRecords,
    records: [],
  };
}

export function parseShadowDataset(
  raw: string | null,
  maxRecords = TRUTH_PRESSURE_DEFAULT_MAX_RECORDS,
): TruthPressureShadowDataset {
  if (!raw) return emptyShadowDataset(maxRecords);

  let parsed: unknown;
  try {
    parsed = JSON.parse(raw);
  } catch {
    throw new Error('Stored Truth Pressure shadow dataset is not valid JSON.');
  }

  if (!parsed || typeof parsed !== 'object') {
    throw new Error('Stored Truth Pressure shadow dataset is not an object.');
  }

  const candidate = parsed as Partial<TruthPressureShadowDataset>;
  if (candidate.version !== TRUTH_PRESSURE_SHADOW_DATASET_VERSION) {
    throw new Error(`Unsupported shadow dataset version: ${String(candidate.version)}`);
  }
  if (candidate.privacy !== 'NO_RAW_CONTENT') {
    throw new Error('Stored shadow dataset violates the privacy contract.');
  }
  if (!Array.isArray(candidate.records)) {
    throw new Error('Stored shadow dataset has no records array.');
  }

  candidate.records.forEach(validateShadowRecord);
  const bounded = candidate.records.slice(-maxRecords);

  return {
    version: TRUTH_PRESSURE_SHADOW_DATASET_VERSION,
    privacy: 'NO_RAW_CONTENT',
    updatedAt: typeof candidate.updatedAt === 'string'
      ? candidate.updatedAt
      : new Date().toISOString(),
    maxRecords,
    records: bounded,
  };
}

export async function loadShadowDataset(
  store: TruthPressureKeyValueStore,
  options: { key?: string; maxRecords?: number } = {},
): Promise<TruthPressureShadowDataset> {
  const key = options.key ?? TRUTH_PRESSURE_SHADOW_STORAGE_KEY;
  const maxRecords = options.maxRecords ?? TRUTH_PRESSURE_DEFAULT_MAX_RECORDS;
  return parseShadowDataset(await store.getItem(key), maxRecords);
}

export async function appendShadowRecord(
  store: TruthPressureKeyValueStore,
  record: ShadowComparisonRecord,
  options: { key?: string; maxRecords?: number; now?: string } = {},
): Promise<TruthPressureShadowDataset> {
  validateShadowRecord(record);

  const key = options.key ?? TRUTH_PRESSURE_SHADOW_STORAGE_KEY;
  const maxRecords = options.maxRecords ?? TRUTH_PRESSURE_DEFAULT_MAX_RECORDS;
  const dataset = await loadShadowDataset(store, { key, maxRecords });
  const nextRecords = [...dataset.records, record].slice(-maxRecords);

  const next: TruthPressureShadowDataset = {
    version: TRUTH_PRESSURE_SHADOW_DATASET_VERSION,
    privacy: 'NO_RAW_CONTENT',
    updatedAt: options.now ?? new Date().toISOString(),
    maxRecords,
    records: nextRecords,
  };

  // The serialized dataset is checked again before persistence.
  assertNoRawContent(next);
  await store.setItem(key, JSON.stringify(next));
  return next;
}

export async function clearShadowDataset(
  store: TruthPressureKeyValueStore,
  key = TRUTH_PRESSURE_SHADOW_STORAGE_KEY,
): Promise<void> {
  await store.removeItem(key);
}

export function summarizeShadowDataset(
  dataset: TruthPressureShadowDataset,
): TruthPressureShadowSummary {
  let text = 0;
  let structured = 0;
  let onion = 0;
  let triggerAgreements = 0;
  let triggerDisagreements = 0;
  let triggerNotComparable = 0;
  let candidateWarnings = 0;
  let candidatePressureTotal = 0;
  let candidatePressureCount = 0;
  let legacyPressureTotal = 0;
  let legacyPressureCount = 0;

  for (const record of dataset.records) {
    if (record.inputClass === 'TEXT') text++;
    else if (record.inputClass === 'STRUCTURED') structured++;
    else onion++;

    if (record.deltas.legacyReorganiseVsCandidateReview === 'AGREE') triggerAgreements++;
    else if (record.deltas.legacyReorganiseVsCandidateReview === 'DISAGREE') triggerDisagreements++;
    else triggerNotComparable++;

    candidateWarnings += record.candidate.warnings.length;

    const candidatePressure = finiteOrNull(record.candidate.piNormalized);
    if (candidatePressure !== null) {
      candidatePressureTotal += candidatePressure;
      candidatePressureCount++;
    }

    const legacyPressure = finiteOrNull(record.legacy?.truthPressure);
    if (legacyPressure !== null) {
      legacyPressureTotal += legacyPressure;
      legacyPressureCount++;
    }
  }

  return {
    total: dataset.records.length,
    text,
    structured,
    onion,
    triggerAgreements,
    triggerDisagreements,
    triggerNotComparable,
    candidateWarnings,
    meanCandidatePressure: candidatePressureCount
      ? candidatePressureTotal / candidatePressureCount
      : null,
    meanLegacyPressure: legacyPressureCount
      ? legacyPressureTotal / legacyPressureCount
      : null,
  };
}

/**
 * Serializes writes inside one app process so two simultaneous analyses do not
 * overwrite one another's local shadow record.
 */
export function createShadowRecorder(
  store: TruthPressureKeyValueStore,
  options: { key?: string; maxRecords?: number } = {},
): {
  record(record: ShadowComparisonRecord): Promise<TruthPressureShadowDataset>;
  load(): Promise<TruthPressureShadowDataset>;
  clear(): Promise<void>;
} {
  let queue: Promise<unknown> = Promise.resolve();

  const record = (nextRecord: ShadowComparisonRecord): Promise<TruthPressureShadowDataset> => {
    const operation = queue.then(() => appendShadowRecord(store, nextRecord, options));
    queue = operation.catch(() => undefined);
    return operation;
  };

  return {
    record,
    load: () => queue.then(() => loadShadowDataset(store, options)),
    clear: () => {
      const operation = queue.then(() => clearShadowDataset(
        store,
        options.key ?? TRUTH_PRESSURE_SHADOW_STORAGE_KEY,
      ));
      queue = operation.catch(() => undefined);
      return operation;
    },
  };
}
