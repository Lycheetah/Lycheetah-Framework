import { clamp01, scorePressure } from './core.ts';

export type OnionV2Input = {
  axiomClarity: number;
  foundationEvidence: number;
  structureQuality: number;
  coherence: number;
  resonance: number;
  tensionMagnitude: number;
  tensionHandlingQuality: number;
  contestedMagnitude: number;
  contestedHandlingQuality: number;
  speculativeExtent: number;
  speculativeLabelQuality: number;
  frontierClarity: number;
  falsifiable: boolean;
};

export type OnionV2Result = ReturnType<typeof scorePressure> & {
  loadBearingness: number;
  handlingQuality: number;
  confidence: number;
  assumptions: string[];
};

const n = (x: number) => clamp01(x > 1 ? x / 100 : x);

export function scoreOnionV2(input: OnionV2Input): OnionV2Result {
  const axiom = n(input.axiomClarity);
  const foundation = n(input.foundationEvidence);
  const structure = n(input.structureQuality);
  const coherence = n(input.coherence);
  const resonance = n(input.resonance);
  const tensionMagnitude = n(input.tensionMagnitude);
  const tensionHandling = n(input.tensionHandlingQuality);
  const contestedMagnitude = n(input.contestedMagnitude);
  const contestedHandling = n(input.contestedHandlingQuality);
  const speculativeExtent = n(input.speculativeExtent);
  const speculativeHandling = n(input.speculativeLabelQuality);
  const frontierClarity = n(input.frontierClarity);

  const evidence = foundation;
  const explanatoryPower = clamp01(structure * 0.55 + resonance * 0.25 + axiom * 0.20);
  const strain = clamp01(
    (1 - coherence) * 0.55 +
    tensionMagnitude * 0.25 +
    contestedMagnitude * 0.15 +
    speculativeExtent * 0.05
  );
  const handlingQuality = clamp01(
    tensionHandling * 0.30 +
    contestedHandling * 0.25 +
    speculativeHandling * 0.20 +
    frontierClarity * 0.25
  );
  const confidence = clamp01(handlingQuality * 0.65 + (input.falsifiable ? 0.35 : 0));

  return {
    ...scorePressure({ evidence, explanatoryPower, strain }),
    loadBearingness: axiom,
    handlingQuality,
    confidence,
    assumptions: [
      'Onion v2 separates the magnitude of tension from the quality of acknowledging tension.',
      'The onion-to-E/P/S mapping is an adapter assumption, not part of the canonical formula.',
      'Falsifiability affects confidence, not Truth Pressure directly.',
    ],
  };
}
