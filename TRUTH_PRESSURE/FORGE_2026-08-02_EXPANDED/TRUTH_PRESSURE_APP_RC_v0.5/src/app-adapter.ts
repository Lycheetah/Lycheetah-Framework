import { analyzeText } from './text-adapter.ts';
import { scoreStructuredAssessment } from './structured.ts';
import { scoreOnionV3, type OnionV3Input } from './onion.ts';
import type { PressureScore, StructuredAssessment, TextAnalysis } from './types.ts';

export const APP_CONTRACT_VERSION = 'TP-APP-VIEW-0.5' as const;
export const ENGINE_VERSION = '0.5.0-rc.1' as const;

export type AppAnalysisInput =
  | { kind: 'text'; text: string }
  | { kind: 'structured'; assessment: StructuredAssessment }
  | { kind: 'onion'; assessment: OnionV3Input };

export type AppMode = 'TEXT_TRIAGE' | 'STRUCTURED_ASSESSMENT' | 'ONION_ASSESSMENT';
export type AppReviewState =
  | 'TRIAGE_ONLY'
  | 'THRESHOLD_NOT_CONFIGURED'
  | 'BELOW_CONFIGURED_THRESHOLD'
  | 'REVIEW_SIGNAL_OPEN';

export type AppComponentView = {
  key: 'E' | 'P' | 'S';
  label: string;
  value: number;
  displayPercent: number;
  direction: 'SUPPORTS_PRESSURE' | 'REDUCES_PRESSURE';
  meaning: string;
};

export type AppTruthPressureViewModel = {
  contractVersion: typeof APP_CONTRACT_VERSION;
  engineVersion: typeof ENGINE_VERSION;
  mode: AppMode;
  instrument: string;
  claim: string;
  headline: {
    label: 'Revision pressure index';
    value: number;
    displayPercent: number;
    unit: 'normalized index';
    disclaimer: string;
  };
  components: AppComponentView[];
  review: {
    state: AppReviewState;
    thresholdCanon: number | null;
    triggered: boolean | null;
    eligibleForStructuralProposal: boolean;
    message: string;
  };
  explanation: string[];
  warnings: string[];
  provenanceSummary: string[];
  registerSummary: string[];
  raw: PressureScore;
};

function pct(value: number): number {
  return Math.round(value * 1000) / 10;
}

function componentViews(score: PressureScore): AppComponentView[] {
  return [
    {
      key: 'E',
      label: 'Evidence',
      value: score.components.evidence,
      displayPercent: pct(score.components.evidence),
      direction: 'SUPPORTS_PRESSURE',
      meaning: 'Inspectable support available under the current assessment.',
    },
    {
      key: 'P',
      label: 'Explanatory reach',
      value: score.components.explanatoryPower,
      displayPercent: pct(score.components.explanatoryPower),
      direction: 'SUPPORTS_PRESSURE',
      meaning: 'How much mechanism, prediction, scope, or unification has been earned.',
    },
    {
      key: 'S',
      label: 'Unresolved strain',
      value: score.components.strain,
      displayPercent: pct(score.components.strain),
      direction: 'REDUCES_PRESSURE',
      meaning: 'Contradiction, ambiguity, missing evidence, or unresolved alternatives still present.',
    },
  ];
}

function reviewState(mode: AppMode, score: PressureScore): AppTruthPressureViewModel['review'] {
  if (mode === 'TEXT_TRIAGE') {
    return {
      state: 'TRIAGE_ONLY',
      thresholdCanon: score.reviewThresholdCanon,
      triggered: score.reviewTriggered,
      eligibleForStructuralProposal: false,
      message: 'Text analysis is triage only. Convert the claim into a structured or onion assessment before proposing structural movement.',
    };
  }
  if (score.reviewThresholdCanon === null) {
    return {
      state: 'THRESHOLD_NOT_CONFIGURED',
      thresholdCanon: null,
      triggered: null,
      eligibleForStructuralProposal: false,
      message: 'No validated review threshold is configured. The score is descriptive only.',
    };
  }
  if (score.reviewTriggered) {
    return {
      state: 'REVIEW_SIGNAL_OPEN',
      thresholdCanon: score.reviewThresholdCanon,
      triggered: true,
      eligibleForStructuralProposal: true,
      message: 'The configured review threshold was exceeded. This opens review; it does not authorize automatic replacement.',
    };
  }
  return {
    state: 'BELOW_CONFIGURED_THRESHOLD',
    thresholdCanon: score.reviewThresholdCanon,
    triggered: false,
    eligibleForStructuralProposal: false,
    message: 'The configured review threshold was not exceeded.',
  };
}

function dominantExplanation(score: PressureScore): string[] {
  const c = score.components;
  const result = [
    `Evidence contributes ${pct(c.evidence)}% of its normalized component range.`,
    `Explanatory reach contributes ${pct(c.explanatoryPower)}% of its normalized component range.`,
    `Unresolved strain occupies ${pct(c.strain)}% of its normalized component range and reduces pressure.`,
  ];
  if (score.interpretation.limitingComponents.length) {
    result.push(`Primary limiter: ${score.interpretation.limitingComponents.join(' and ')}.`);
  }
  result.push('The index is a revision-pressure signal under declared inputs, not a probability that the claim is true.');
  return result;
}

function textWarnings(result: TextAnalysis): string[] {
  return [
    'Text mode is pattern-based, English-oriented, and provisional.',
    ...result.warnings,
    ...result.attacks.map(x => `Adversarial pattern detected: ${x}.`),
  ];
}

export function buildAppViewModel(input: AppAnalysisInput): AppTruthPressureViewModel {
  if (input.kind === 'text') {
    const result = analyzeText(input.text);
    return {
      contractVersion: APP_CONTRACT_VERSION,
      engineVersion: ENGINE_VERSION,
      mode: 'TEXT_TRIAGE',
      instrument: result.instrument,
      claim: result.claim,
      headline: {
        label: 'Revision pressure index',
        value: result.piNormalized,
        displayPercent: pct(result.piNormalized),
        unit: 'normalized index',
        disclaimer: result.interpretation.boundary,
      },
      components: componentViews(result),
      review: reviewState('TEXT_TRIAGE', result),
      explanation: dominantExplanation(result),
      warnings: [...new Set(textWarnings(result))],
      provenanceSummary: result.provenance.evidence.length
        ? result.provenance.evidence.map(x => `${x.status}: ${x.label}`)
        : ['No inspectable evidence provenance was supplied in text mode.'],
      registerSummary: Object.entries(result.registers).map(([k, v]) => `${k}: ${v}`),
      raw: result,
    };
  }

  if (input.kind === 'structured') {
    const result = scoreStructuredAssessment(input.assessment);
    return {
      contractVersion: APP_CONTRACT_VERSION,
      engineVersion: ENGINE_VERSION,
      mode: 'STRUCTURED_ASSESSMENT',
      instrument: result.instrument,
      claim: result.claim,
      headline: {
        label: 'Revision pressure index',
        value: result.piNormalized,
        displayPercent: pct(result.piNormalized),
        unit: 'normalized index',
        disclaimer: result.interpretation.boundary,
      },
      components: componentViews(result),
      review: reviewState('STRUCTURED_ASSESSMENT', result),
      explanation: [
        ...dominantExplanation(result),
        `Handling quality is ${pct(result.handlingQuality)}%; it affects adjudication readiness, not Truth Pressure.`,
        `Load-bearingness is ${pct(result.loadBearingness)}%; it affects review priority, not evidence strength.`,
      ],
      warnings: result.diagnostics,
      provenanceSummary: result.provenance.evidence.length
        ? result.provenance.evidence.map(x => `${x.status}: ${x.label}`)
        : ['No evidence provenance was supplied.'],
      registerSummary: Object.entries(result.registers).map(([k, v]) => `${k}: ${v}`),
      raw: result,
    };
  }

  const result = scoreOnionV3(input.assessment);
  return {
    contractVersion: APP_CONTRACT_VERSION,
    engineVersion: ENGINE_VERSION,
    mode: 'ONION_ASSESSMENT',
    instrument: result.instrument,
    claim: result.claim,
    headline: {
      label: 'Revision pressure index',
      value: result.piNormalized,
      displayPercent: pct(result.piNormalized),
      unit: 'normalized index',
      disclaimer: result.interpretation.boundary,
    },
    components: componentViews(result),
    review: reviewState('ONION_ASSESSMENT', result),
    explanation: [
      ...dominantExplanation(result),
      `Handling quality is ${pct(result.handlingQuality)}%; it is tracked separately from unresolved strain.`,
      `Assessment readiness is ${pct(result.assessmentReadiness)}%.`,
    ],
    warnings: result.assumptions,
    provenanceSummary: ['Onion inputs are authored assessment values; source provenance must be attached by the calling feature.'],
    registerSummary: [
      'piCanon: DERIVED',
      'piNormalized: DERIVED',
      'onion-to-E/P/S mapping: ASSUMED',
      'handling quality: INTERPRETIVE',
    ],
    raw: result,
  };
}
