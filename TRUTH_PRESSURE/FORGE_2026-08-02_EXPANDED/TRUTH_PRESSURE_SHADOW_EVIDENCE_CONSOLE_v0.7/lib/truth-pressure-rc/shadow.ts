import type { AppTruthPressureViewModel } from './app-adapter.ts';

export const SHADOW_RECORD_VERSION = 'TP-SHADOW-0.5' as const;

export type LegacyTruthPressureSnapshot = {
  truthPressure: number;
  coherence?: number;
  reorganisationNeeded?: boolean;
  dominantLayer?: string;
};

export type ShadowComparisonRecord = {
  version: typeof SHADOW_RECORD_VERSION;
  createdAt: string;
  inputClass: 'TEXT' | 'STRUCTURED' | 'ONION';
  privacy: 'NO_RAW_CONTENT';
  inputLength?: number;
  legacy: LegacyTruthPressureSnapshot | null;
  candidate: {
    engineVersion: string;
    mode: string;
    piNormalized: number;
    piCanon: number;
    evidence: number;
    explanatoryPower: number;
    strain: number;
    reviewState: string;
    warnings: string[];
  };
  deltas: {
    normalizedPressure: number | null;
    legacyReorganiseVsCandidateReview: 'AGREE' | 'DISAGREE' | 'NOT_COMPARABLE';
  };
};

export function createShadowComparison(
  candidate: AppTruthPressureViewModel,
  legacy: LegacyTruthPressureSnapshot | null,
  options: { createdAt?: string; inputLength?: number } = {},
): ShadowComparisonRecord {
  const comparableTrigger = legacy?.reorganisationNeeded === undefined || candidate.review.triggered === null
    ? 'NOT_COMPARABLE'
    : legacy.reorganisationNeeded === candidate.review.triggered
      ? 'AGREE'
      : 'DISAGREE';

  return {
    version: SHADOW_RECORD_VERSION,
    createdAt: options.createdAt ?? new Date().toISOString(),
    inputClass: candidate.mode === 'TEXT_TRIAGE' ? 'TEXT' : candidate.mode === 'STRUCTURED_ASSESSMENT' ? 'STRUCTURED' : 'ONION',
    privacy: 'NO_RAW_CONTENT',
    inputLength: options.inputLength,
    legacy,
    candidate: {
      engineVersion: candidate.engineVersion,
      mode: candidate.mode,
      piNormalized: candidate.headline.value,
      piCanon: candidate.raw.piCanon,
      evidence: candidate.raw.components.evidence,
      explanatoryPower: candidate.raw.components.explanatoryPower,
      strain: candidate.raw.components.strain,
      reviewState: candidate.review.state,
      warnings: candidate.warnings,
    },
    deltas: {
      normalizedPressure: legacy === null ? null : candidate.headline.value - legacy.truthPressure,
      legacyReorganiseVsCandidateReview: comparableTrigger,
    },
  };
}
