import type { PressureComponents, PressureConfig, PressureScore } from './types.ts';
import { finiteNumber, unitScore, ValidationError } from './validation.ts';

export const DEFAULT_PRESSURE_CONFIG: PressureConfig = Object.freeze({ s0: 0.05 });

export function normalizeConfig(config: Partial<PressureConfig> = {}): PressureConfig {
  const s0 = config.s0 === undefined ? DEFAULT_PRESSURE_CONFIG.s0 : finiteNumber('config.s0', config.s0);
  if (s0 <= 0 || s0 > 1) throw new ValidationError('config.s0', 'must be within (0, 1]');
  const threshold = config.reviewThresholdCanon;
  if (threshold !== undefined) {
    const t = finiteNumber('config.reviewThresholdCanon', threshold);
    if (t < 0 || t > 1 / s0) {
      throw new ValidationError('config.reviewThresholdCanon', `must be within [0, ${1 / s0}] for s0=${s0}`);
    }
  }
  return { s0, reviewThresholdCanon: threshold };
}

function validateComponents(input: PressureComponents): PressureComponents {
  return {
    evidence: unitScore('components.evidence', input.evidence),
    explanatoryPower: unitScore('components.explanatoryPower', input.explanatoryPower),
    strain: unitScore('components.strain', input.strain),
  };
}

function limiterSet(c: PressureComponents): Array<'evidence' | 'explanatoryPower' | 'strain'> {
  const burdens = {
    evidence: 1 - c.evidence,
    explanatoryPower: 1 - c.explanatoryPower,
    strain: c.strain,
  } as const;
  const max = Math.max(...Object.values(burdens));
  if (max < 0.05) return [];
  const eps = 1e-12;
  return (Object.keys(burdens) as Array<keyof typeof burdens>).filter(k => Math.abs(burdens[k] - max) <= eps);
}

export function scorePressure(
  input: PressureComponents,
  configInput: Partial<PressureConfig> = {},
): PressureScore {
  const config = normalizeConfig(configInput);
  const components = validateComponents(input);
  const piCanon = (components.evidence * components.explanatoryPower) / (components.strain + config.s0);
  const piNormalized = piCanon * config.s0;
  const threshold = config.reviewThresholdCanon ?? null;
  const reviewTriggered = threshold === null ? null : piCanon > threshold;
  const limitingComponents = limiterSet(components);

  const labels = limitingComponents.map(x => x === 'explanatoryPower' ? 'explanatory reach' : x).join(' and ');
  const summary = limitingComponents.length
    ? `The principal limiting component${limitingComponents.length > 1 ? 's are' : ' is'} ${labels}. Pressure is a review signal, not a truth probability.`
    : 'No single component is presently dominant. Pressure is a review signal, not a truth probability.';

  let counterfactuals: PressureScore['counterfactuals'] = null;
  if (threshold !== null) {
    const evidenceRequired = components.explanatoryPower === 0
      ? null
      : threshold * (components.strain + config.s0) / components.explanatoryPower;
    const explanatoryPowerRequired = components.evidence === 0
      ? null
      : threshold * (components.strain + config.s0) / components.evidence;
    const maximumStrain = threshold === 0
      ? null
      : (components.evidence * components.explanatoryPower) / threshold - config.s0;
    counterfactuals = {
      evidenceRequired: evidenceRequired === null ? null : Math.max(0, evidenceRequired),
      explanatoryPowerRequired: explanatoryPowerRequired === null ? null : Math.max(0, explanatoryPowerRequired),
      maximumStrain: maximumStrain === null ? null : Math.max(0, maximumStrain),
    };
  }

  return {
    instrument: 'TP-CANONICAL-SCALAR-v0.5',
    components,
    piCanon,
    piNormalized,
    piApp: piNormalized,
    scale: {
      canonRange: [0, 1 / config.s0],
      normalizedRange: [0, 1],
      conversion: `piNormalized = piCanon × s0 = piCanon × ${config.s0}`,
      s0: config.s0,
    },
    reviewThresholdCanon: threshold,
    reviewTriggered,
    interpretation: {
      limitingComponents,
      summary,
      boundary: 'This score represents revision pressure under the declared operationalization. It does not establish factual truth.',
    },
    counterfactuals,
  };
}

export function pressureRatio(
  beforeInput: PressureComponents,
  afterInput: PressureComponents,
  s0 = DEFAULT_PRESSURE_CONFIG.s0,
): {
  totalRatio: number | null;
  evidenceRatio: number | null;
  explanatoryRatio: number | null;
  strainRatio: number;
  logAttribution: { evidence: number | null; explanatoryPower: number | null; strain: number };
} {
  const config = normalizeConfig({ s0 });
  const before = validateComponents(beforeInput);
  const after = validateComponents(afterInput);
  const evidenceRatio = before.evidence === 0 ? null : after.evidence / before.evidence;
  const explanatoryRatio = before.explanatoryPower === 0 ? null : after.explanatoryPower / before.explanatoryPower;
  const strainRatio = (before.strain + config.s0) / (after.strain + config.s0);
  const beforePi = scorePressure(before, config).piCanon;
  const afterPi = scorePressure(after, config).piCanon;
  return {
    totalRatio: beforePi === 0 ? null : afterPi / beforePi,
    evidenceRatio,
    explanatoryRatio,
    strainRatio,
    logAttribution: {
      evidence: evidenceRatio === null || evidenceRatio <= 0 ? null : Math.log(evidenceRatio),
      explanatoryPower: explanatoryRatio === null || explanatoryRatio <= 0 ? null : Math.log(explanatoryRatio),
      strain: Math.log(strainRatio),
    },
  };
}
