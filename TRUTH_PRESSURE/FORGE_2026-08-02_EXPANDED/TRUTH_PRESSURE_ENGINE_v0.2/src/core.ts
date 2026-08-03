import type { PressureComponents, PressureConfig, PressureScore } from './types.ts';

export const DEFAULT_PRESSURE_CONFIG: PressureConfig = Object.freeze({
  s0: 0.05,
  appScaleFactor: 0.05,
});

export function clamp01(value: number): number {
  if (!Number.isFinite(value)) return 0;
  return Math.max(0, Math.min(1, value));
}

export function normalizeConfig(config: Partial<PressureConfig> = {}): PressureConfig {
  const merged = { ...DEFAULT_PRESSURE_CONFIG, ...config };
  if (!Number.isFinite(merged.s0) || merged.s0 <= 0) {
    throw new Error('s0 must be finite and greater than zero');
  }
  if (!Number.isFinite(merged.appScaleFactor) || merged.appScaleFactor <= 0) {
    throw new Error('appScaleFactor must be finite and greater than zero');
  }
  if (merged.reviewThresholdCanon !== undefined &&
      (!Number.isFinite(merged.reviewThresholdCanon) || merged.reviewThresholdCanon < 0)) {
    throw new Error('reviewThresholdCanon must be finite and non-negative');
  }
  return merged;
}

export function scorePressure(
  input: PressureComponents,
  configInput: Partial<PressureConfig> = {},
): PressureScore {
  const config = normalizeConfig(configInput);
  const components: PressureComponents = {
    evidence: clamp01(input.evidence),
    explanatoryPower: clamp01(input.explanatoryPower),
    strain: clamp01(input.strain),
  };

  const piCanon = (components.evidence * components.explanatoryPower) /
    (components.strain + config.s0);
  const piApp = piCanon * config.appScaleFactor;
  const threshold = config.reviewThresholdCanon ?? null;
  const reviewTriggered = threshold === null ? null : piCanon > threshold;

  const eGap = 1 - components.evidence;
  const pGap = 1 - components.explanatoryPower;
  const sBurden = components.strain;
  const max = Math.max(eGap, pGap, sBurden);
  const dominantLimiter = max < 0.05
    ? 'none'
    : max === eGap
      ? 'evidence'
      : max === pGap
        ? 'explanatoryPower'
        : 'strain';

  const limiterText = dominantLimiter === 'evidence'
    ? 'The principal limiter is the strength and inspectability of the evidence.'
    : dominantLimiter === 'explanatoryPower'
      ? 'The principal limiter is how little of the problem the current explanation earns the right to cover.'
      : dominantLimiter === 'strain'
        ? 'The principal limiter is unresolved contradiction, ambiguity, or structural strain.'
        : 'No single component is presently dominant.';

  return {
    components,
    piCanon,
    piApp,
    scaleConversion: `piApp = piCanon × ${config.appScaleFactor}`,
    reviewThresholdCanon: threshold,
    reviewTriggered,
    interpretation: {
      dominantLimiter,
      summary: `${limiterText} Pressure is a review signal, not a truth probability.`,
      boundary: 'This score represents revision pressure under the declared operationalization. It does not establish factual truth.',
    },
  };
}

export function pressureRatio(
  before: PressureComponents,
  after: PressureComponents,
  s0 = DEFAULT_PRESSURE_CONFIG.s0,
): {
  totalRatio: number | null;
  evidenceRatio: number | null;
  explanatoryRatio: number | null;
  strainRatio: number;
} {
  const b = {
    evidence: clamp01(before.evidence),
    explanatoryPower: clamp01(before.explanatoryPower),
    strain: clamp01(before.strain),
  };
  const a = {
    evidence: clamp01(after.evidence),
    explanatoryPower: clamp01(after.explanatoryPower),
    strain: clamp01(after.strain),
  };
  const evidenceRatio = b.evidence === 0 ? null : a.evidence / b.evidence;
  const explanatoryRatio = b.explanatoryPower === 0 ? null : a.explanatoryPower / b.explanatoryPower;
  const strainRatio = (b.strain + s0) / (a.strain + s0);
  const beforePi = (b.evidence * b.explanatoryPower) / (b.strain + s0);
  const afterPi = (a.evidence * a.explanatoryPower) / (a.strain + s0);
  return {
    totalRatio: beforePi === 0 ? null : afterPi / beforePi,
    evidenceRatio,
    explanatoryRatio,
    strainRatio,
  };
}
