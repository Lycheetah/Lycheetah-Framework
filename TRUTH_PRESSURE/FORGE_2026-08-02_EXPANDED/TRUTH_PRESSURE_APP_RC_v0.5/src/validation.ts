import type { ScoreScale } from './types.ts';

export class ValidationError extends Error {
  readonly field: string;
  constructor(field: string, message: string) {
    super(`${field}: ${message}`);
    this.name = 'ValidationError';
    this.field = field;
  }
}

export function finiteNumber(name: string, value: unknown): number {
  if (typeof value !== 'number' || !Number.isFinite(value)) {
    throw new ValidationError(name, 'must be a finite number');
  }
  return value;
}

export function unitScore(name: string, value: unknown): number {
  const n = finiteNumber(name, value);
  if (n < 0 || n > 1) throw new ValidationError(name, 'must be within [0, 1]');
  return n;
}

export function positiveWeight(name: string, value: unknown, fallback = 1): number {
  if (value === undefined) return fallback;
  const n = finiteNumber(name, value);
  if (n <= 0 || n > 10) throw new ValidationError(name, 'must be within (0, 10]');
  return n;
}

export function nonEmptyString(name: string, value: unknown): string {
  if (typeof value !== 'string' || !value.trim()) {
    throw new ValidationError(name, 'must be a non-empty string');
  }
  return value.trim();
}

export function normalizeScaledScore(name: string, value: unknown, scale: ScoreScale): number {
  const n = finiteNumber(name, value);
  if (scale === 'unit') return unitScore(name, n);
  if (scale === 'percent') {
    if (n < 0 || n > 100) throw new ValidationError(name, 'must be within [0, 100] for percent scale');
    return n / 100;
  }
  throw new ValidationError('scale', 'must be "unit" or "percent"');
}

export function assertUniqueIds(name: string, items: Array<{ id: string }>): void {
  const seen = new Set<string>();
  for (const item of items) {
    const id = nonEmptyString(`${name}.id`, item.id);
    if (seen.has(id)) throw new ValidationError(name, `duplicate id: ${id}`);
    seen.add(id);
  }
}
