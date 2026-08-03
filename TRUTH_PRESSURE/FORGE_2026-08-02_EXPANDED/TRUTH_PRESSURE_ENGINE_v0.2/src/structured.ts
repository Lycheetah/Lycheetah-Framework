import { clamp01, scorePressure } from './core.ts';
import type {
  EvidenceItem,
  ExplanationItem,
  HandlingAssessment,
  StrainItem,
  StructuredAssessment,
  StructuredResult,
} from './types.ts';

function weightedMean(values: { score: number; weight: number }[]): number {
  if (!values.length) return 0;
  const totalWeight = values.reduce((sum, x) => sum + x.weight, 0);
  if (totalWeight <= 0) return 0;
  return clamp01(values.reduce((sum, x) => sum + x.score * x.weight, 0) / totalWeight);
}

export function evidenceItemScore(item: EvidenceItem): number {
  return clamp01(
    item.directness * 0.28 +
    item.verifiability * 0.27 +
    item.sourceQuality * 0.18 +
    item.independence * 0.17 +
    item.replication * 0.10
  );
}

export function aggregateEvidence(items: EvidenceItem[]): number {
  if (!items.length) return 0;
  const groups = new Map<string, { score: number; weight: number }>();
  for (const item of items) {
    const key = item.duplicateGroup || item.id;
    const candidate = { score: evidenceItemScore(item), weight: Math.max(0.01, item.weight ?? 1) };
    const existing = groups.get(key);
    if (!existing || candidate.score > existing.score) groups.set(key, candidate);
  }
  const unique = [...groups.values()];
  const base = weightedMean(unique);
  const independentSupportBonus = unique.length <= 1
    ? 0
    : 0.16 * (1 - Math.exp(-(unique.length - 1) / 2));
  return clamp01(base + independentSupportBonus * (1 - base));
}

export function explanationItemScore(item: ExplanationItem): number {
  return clamp01(
    item.mechanismSpecificity * 0.30 +
    item.scopeFit * 0.18 +
    item.predictiveRisk * 0.22 +
    item.unification * 0.15 +
    item.falsifiability * 0.15
  );
}

export function aggregateExplanation(items: ExplanationItem[]): number {
  if (!items.length) return 0;
  const scored = items.map(item => ({
    score: explanationItemScore(item),
    weight: Math.max(0.01, item.weight ?? 1),
  }));
  const mean = weightedMean(scored);
  const strongest = Math.max(...scored.map(x => x.score));
  return clamp01(mean * 0.65 + strongest * 0.35);
}

export function strainItemScore(item: StrainItem): number {
  return clamp01(
    item.severity * 0.40 +
    item.unresolved * 0.35 +
    item.centrality * 0.25
  );
}

export function aggregateStrain(items: StrainItem[]): number {
  if (!items.length) return 0.08; // unknown is not perfect coherence
  const scores = items.map(item => strainItemScore(item) * Math.max(0.01, item.weight ?? 1));
  const max = Math.max(...scores);
  const accumulation = 1 - scores.reduce((product, score) => product * (1 - clamp01(score) * 0.55), 1);
  return clamp01(Math.max(max, accumulation));
}

export function handlingQuality(handling?: HandlingAssessment): number {
  if (!handling) return 0;
  return clamp01(
    handling.acknowledgesLimits * 0.30 +
    handling.distinguishesAlternatives * 0.25 +
    handling.scopesClaims * 0.25 +
    handling.namesFalsifier * 0.20
  );
}

export function scoreStructuredAssessment(input: StructuredAssessment): StructuredResult {
  const evidence = aggregateEvidence(input.evidenceItems);
  const explanatoryPower = aggregateExplanation(input.explanationItems);
  const strain = aggregateStrain(input.strainItems);
  const pressure = scorePressure({ evidence, explanatoryPower, strain }, input.config);
  const loadBearingness = clamp01(input.loadBearingness ?? 0.5);
  const handling = handlingQuality(input.handling);
  const reviewPriority = clamp01((pressure.piApp * 0.70) + (loadBearingness * 0.20) + (handling * 0.10));

  return {
    ...pressure,
    claim: input.claim,
    loadBearingness,
    handlingQuality: handling,
    reviewPriority,
    registers: {
      piCanon: 'DERIVED',
      piApp: 'DERIVED',
      evidence: 'ASSUMED',
      explanatoryPower: 'ASSUMED',
      strain: 'ASSUMED',
      loadBearingness: 'INTERPRETIVE',
      handlingQuality: 'INTERPRETIVE',
      reviewPriority: 'PROVISIONAL',
    },
    provenance: {
      evidence: input.evidenceItems.map(item => item.provenance || item.description),
      explanation: input.explanationItems.map(item => item.description),
      strain: input.strainItems.map(item => item.description),
    },
  };
}
