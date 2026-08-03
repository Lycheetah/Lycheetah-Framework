import { createHash } from 'node:crypto';
import { finiteNumber, unitScore, ValidationError } from './validation.ts';

export type ReviewLayer<T = unknown> = {
  name: string;
  content: string;
  score: number;
  metadata?: T;
  invariant?: boolean;
};

export type LayerMove = { from: number; to: number; reason: string };
export type ReviewPlan = {
  version: 'TP-REVIEW-PLAN-0.3';
  fires: boolean;
  threshold: number | null;
  piCanon: number;
  sourceFingerprint: string;
  moves: LayerMove[];
  preserved: number[];
  blocked: boolean;
  why: string;
};

export type ReviewApplication<T> = {
  ok: boolean;
  error?: string;
  approved: boolean;
  before: ReviewLayer<T>[];
  after: ReviewLayer<T>[];
  beforeFingerprint: string;
  afterFingerprint: string;
  plan: ReviewPlan;
};

function stable(value: unknown): string {
  if (value === null || typeof value !== 'object') return JSON.stringify(value);
  if (Array.isArray(value)) return `[${value.map(stable).join(',')}]`;
  const obj = value as Record<string, unknown>;
  return `{${Object.keys(obj).sort().map(k => `${JSON.stringify(k)}:${stable(obj[k])}`).join(',')}}`;
}

export function fingerprintLayers<T>(layers: ReviewLayer<T>[]): string {
  return createHash('sha256').update(stable(layers)).digest('hex');
}

function validateLayers<T>(layers: ReviewLayer<T>[]): void {
  if (!Array.isArray(layers) || layers.length !== 9) throw new ValidationError('layers', 'must contain exactly nine onion layers');
  layers.forEach((layer, i) => {
    if (!layer || typeof layer.name !== 'string' || typeof layer.content !== 'string') {
      throw new ValidationError(`layers[${i}]`, 'must contain name and content strings');
    }
    unitScore(`layers[${i}].score`, layer.score);
  });
}

export function proposeReview<T>(
  layers: ReviewLayer<T>[],
  piCanonInput: number,
  thresholdCanon?: number,
  weakInner = 0.40,
  invariantBar = 0.65,
): ReviewPlan {
  validateLayers(layers);
  const piCanon = finiteNumber('piCanon', piCanonInput);
  if (piCanon < 0) throw new ValidationError('piCanon', 'must be non-negative');
  const weak = unitScore('weakInner', weakInner);
  const invariant = unitScore('invariantBar', invariantBar);
  const sourceFingerprint = fingerprintLayers(layers);
  const none = (why: string, threshold: number | null): ReviewPlan => ({
    version: 'TP-REVIEW-PLAN-0.3', fires: false, threshold, piCanon, sourceFingerprint,
    moves: [], preserved: [], blocked: false, why,
  });
  if (thresholdCanon === undefined) return none('No validated review threshold was configured.', null);
  const threshold = finiteNumber('thresholdCanon', thresholdCanon);
  if (threshold < 0) throw new ValidationError('thresholdCanon', 'must be non-negative');
  if (!(piCanon > threshold)) return none('Pressure did not exceed the configured threshold.', threshold);

  const inner = [0, 1, 2];
  const edge = [6, 7, 8];
  const preserved = inner.filter(i => Boolean(layers[i].content.trim()) && (layers[i].invariant === true || layers[i].score >= invariant));
  const open = edge.filter(i => !layers[i].content.trim());
  const candidates = inner
    .filter(i => layers[i].content.trim() && !preserved.includes(i) && layers[i].score <= weak)
    .sort((a, b) => layers[a].score - layers[b].score);
  const moves: LayerMove[] = [];
  for (const from of candidates) {
    const to = open.shift();
    if (to === undefined) break;
    moves.push({ from, to, reason: `${layers[from].name} is weak for an inner layer and should be reviewed at ${layers[to].name}.` });
  }
  const blocked = candidates.length > moves.length;
  return {
    version: 'TP-REVIEW-PLAN-0.3', fires: true, threshold, piCanon, sourceFingerprint,
    moves, preserved, blocked,
    why: moves.length
      ? `Pressure exceeded the configured threshold; ${moves.length} reversible move(s) are proposed for sovereign approval.`
      : blocked
        ? 'Pressure exceeded the threshold, but no empty edge slot is available.'
        : 'Pressure exceeded the threshold, but no weak inner layer qualified for demotion.',
  };
}

export function applyReviewPlan<T>(layers: ReviewLayer<T>[], plan: ReviewPlan, approved = false): ReviewApplication<T> {
  validateLayers(layers);
  const before = layers.map(x => ({ ...x }));
  const beforeFingerprint = fingerprintLayers(before);
  const fail = (error: string): ReviewApplication<T> => ({
    ok: false, error, approved, before, after: before.map(x => ({ ...x })), beforeFingerprint,
    afterFingerprint: beforeFingerprint, plan,
  });
  if (!approved) return fail('Sovereign approval is required before applying a review plan.');
  if (!plan.fires || !plan.moves.length) return fail('The plan contains no applicable moves.');
  if (plan.sourceFingerprint !== beforeFingerprint) return fail('The layers changed after the plan was proposed; regenerate the plan.');

  const next = before.map(x => ({ ...x }));
  for (const move of plan.moves) {
    if (!Number.isInteger(move.from) || !Number.isInteger(move.to) || move.from < 0 || move.from > 8 || move.to < 0 || move.to > 8) {
      return fail('The plan contains an invalid layer index.');
    }
    if (!next[move.from].content.trim()) return fail(`Source layer ${move.from} is empty.`);
    if (next[move.to].content.trim()) return fail(`Destination layer ${move.to} is no longer empty.`);
    const source = next[move.from];
    const destinationName = next[move.to].name;
    next[move.to] = { ...source, name: destinationName };
    next[move.from] = { ...source, content: '', score: 0, metadata: undefined, invariant: false };
  }
  return {
    ok: true, approved, before, after: next, beforeFingerprint,
    afterFingerprint: fingerprintLayers(next), plan,
  };
}

export function revertReviewApplication<T>(application: ReviewApplication<T>): ReviewLayer<T>[] {
  return application.before.map(x => ({ ...x }));
}
