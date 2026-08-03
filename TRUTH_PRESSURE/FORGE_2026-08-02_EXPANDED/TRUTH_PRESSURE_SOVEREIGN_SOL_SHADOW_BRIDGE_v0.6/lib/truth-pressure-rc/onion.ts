import { scorePressure } from './core.ts';
import type { ScoreScale } from './types.ts';
import { normalizeScaledScore, nonEmptyString } from './validation.ts';

export type OnionV3Input = {
  scale: ScoreScale;
  claim: string;
  axiomLoadBearingness: number;
  foundationEvidence: number;
  structureMechanism: number;
  resonanceUnification: number;
  predictiveReach: number;
  coherence: number;
  tensionMagnitude: number;
  tensionHandlingQuality: number;
  contestedMagnitude: number;
  contestedHandlingQuality: number;
  speculativeExtent: number;
  speculativeLabelQuality: number;
  frontierClarity: number;
  falsifiable: boolean;
};

export type OnionV3Result = ReturnType<typeof scorePressure> & {
  claim: string;
  inputScale: ScoreScale;
  loadBearingness: number;
  handlingQuality: number;
  assessmentReadiness: number;
  assumptions: string[];
};

export function scoreOnionV3(input: OnionV3Input): OnionV3Result {
  const scale = input.scale;
  const n = (name: keyof OnionV3Input) => normalizeScaledScore(String(name), input[name], scale);
  const claim = nonEmptyString('claim', input.claim);
  if (typeof input.falsifiable !== 'boolean') throw new TypeError('falsifiable must be boolean');

  const loadBearingness = n('axiomLoadBearingness');
  const evidence = n('foundationEvidence');
  const structure = n('structureMechanism');
  const resonance = n('resonanceUnification');
  const predictiveReach = n('predictiveReach');
  const coherence = n('coherence');
  const tensionMagnitude = n('tensionMagnitude');
  const tensionHandling = n('tensionHandlingQuality');
  const contestedMagnitude = n('contestedMagnitude');
  const contestedHandling = n('contestedHandlingQuality');
  const speculativeExtent = n('speculativeExtent');
  const speculativeHandling = n('speculativeLabelQuality');
  const frontierClarity = n('frontierClarity');

  const explanatoryPower = Math.min(1, structure * 0.45 + resonance * 0.25 + predictiveReach * 0.30);
  const strain = Math.min(1,
    (1 - coherence) * 0.50 +
    tensionMagnitude * 0.25 +
    contestedMagnitude * 0.15 +
    speculativeExtent * 0.10
  );
  const handlingQuality = Math.min(1,
    tensionHandling * 0.30 +
    contestedHandling * 0.25 +
    speculativeHandling * 0.20 +
    frontierClarity * 0.25
  );
  const assessmentReadiness = Math.min(1, handlingQuality * 0.70 + (input.falsifiable ? 0.30 : 0));

  return {
    ...scorePressure({ evidence, explanatoryPower, strain }),
    claim,
    inputScale: scale,
    loadBearingness,
    handlingQuality,
    assessmentReadiness,
    assumptions: [
      'Onion v3 requires an explicit unit or percent scale; no value-based scale guessing occurs.',
      'Axiom load-bearingness is separate from explanatory power.',
      'Tension magnitude is separate from tension-handling quality.',
      'The onion-to-E/P/S mapping is an authored adapter assumption, not canonical mathematics.',
      'Falsifiability affects assessment readiness, not Truth Pressure directly.',
    ],
  };
}
