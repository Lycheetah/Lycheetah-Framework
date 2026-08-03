import { scorePressure } from './core.ts';
import type {
  EvidenceItem,
  ExplanationItem,
  HandlingAssessment,
  ProvenanceRecord,
  StrainItem,
  StructuredAssessment,
  StructuredResult,
} from './types.ts';
import { assertUniqueIds, nonEmptyString, positiveWeight, unitScore, ValidationError } from './validation.ts';

function weightedMean(values: { score: number; weight: number }[]): number {
  if (!values.length) return 0;
  const total = values.reduce((s, x) => s + x.weight, 0);
  return values.reduce((s, x) => s + x.score * x.weight, 0) / total;
}

export function evidenceItemScore(item: EvidenceItem, index = 0): number {
  return (
    unitScore(`evidenceItems[${index}].directness`, item.directness) * 0.28 +
    unitScore(`evidenceItems[${index}].verifiability`, item.verifiability) * 0.27 +
    unitScore(`evidenceItems[${index}].sourceQuality`, item.sourceQuality) * 0.18 +
    unitScore(`evidenceItems[${index}].independence`, item.independence) * 0.17 +
    unitScore(`evidenceItems[${index}].replication`, item.replication) * 0.10
  );
}

function validateProvenance(p: ProvenanceRecord | undefined, index: number): ProvenanceRecord {
  if (!p) return { label: 'No provenance supplied', status: 'UNVERIFIED' };
  const label = nonEmptyString(`evidenceItems[${index}].provenance.label`, p.label);
  if (!['UNVERIFIED', 'INSPECTABLE', 'VERIFIED'].includes(p.status)) {
    throw new ValidationError(`evidenceItems[${index}].provenance.status`, 'must be UNVERIFIED, INSPECTABLE, or VERIFIED');
  }
  return { ...p, label };
}

export function aggregateEvidence(items: EvidenceItem[]): { score: number; provenance: ProvenanceRecord[]; diagnostics: string[] } {
  assertUniqueIds('evidenceItems', items);
  if (!items.length) return { score: 0, provenance: [], diagnostics: ['No evidence items were supplied.'] };

  const groups = new Map<string, { quality: number; weight: number; independenceMass: number; provenance: ProvenanceRecord }>();
  items.forEach((item, i) => {
    nonEmptyString(`evidenceItems[${i}].description`, item.description);
    const quality = evidenceItemScore(item, i);
    const weight = positiveWeight(`evidenceItems[${i}].weight`, item.weight);
    const independence = unitScore(`evidenceItems[${i}].independence`, item.independence);
    const replication = unitScore(`evidenceItems[${i}].replication`, item.replication);
    const provenance = validateProvenance(item.provenance, i);
    const provenanceFactor = provenance.status === 'VERIFIED' ? 1 : provenance.status === 'INSPECTABLE' ? 0.9 : 0.7;
    const adjustedQuality = quality * provenanceFactor;
    const key = item.duplicateGroup?.trim() || item.id;
    const candidate = {
      quality: adjustedQuality,
      weight,
      independenceMass: adjustedQuality * independence * (0.5 + 0.5 * replication),
      provenance,
    };
    const existing = groups.get(key);
    if (!existing || candidate.quality > existing.quality) groups.set(key, candidate);
  });

  const unique = [...groups.values()];
  const base = weightedMean(unique.map(x => ({ score: x.quality, weight: x.weight })));
  const sortedMass = unique.map(x => x.independenceMass).sort((a, b) => b - a);
  const additionalMass = sortedMass.slice(1).reduce((a, b) => a + b, 0);
  const independentBonus = 0.18 * (1 - Math.exp(-additionalMass)) * (1 - base);
  const score = Math.min(1, base + independentBonus);
  const diagnostics: string[] = [];
  if (unique.length < items.length) diagnostics.push(`${items.length - unique.length} duplicate evidence item(s) were collapsed.`);
  if (unique.every(x => x.provenance.status === 'UNVERIFIED')) diagnostics.push('All evidence provenance remains unverified.');
  return { score, provenance: unique.map(x => x.provenance), diagnostics };
}

export function explanationItemScore(item: ExplanationItem, index = 0): number {
  return (
    unitScore(`explanationItems[${index}].mechanismSpecificity`, item.mechanismSpecificity) * 0.30 +
    unitScore(`explanationItems[${index}].scopeFit`, item.scopeFit) * 0.18 +
    unitScore(`explanationItems[${index}].predictiveRisk`, item.predictiveRisk) * 0.22 +
    unitScore(`explanationItems[${index}].unification`, item.unification) * 0.15 +
    unitScore(`explanationItems[${index}].falsifiability`, item.falsifiability) * 0.15
  );
}

export function aggregateExplanation(items: ExplanationItem[]): number {
  assertUniqueIds('explanationItems', items);
  if (!items.length) return 0;
  const scored = items.map((item, i) => {
    nonEmptyString(`explanationItems[${i}].description`, item.description);
    return { score: explanationItemScore(item, i), weight: positiveWeight(`explanationItems[${i}].weight`, item.weight) };
  });
  const mean = weightedMean(scored);
  const strongest = Math.max(...scored.map(x => x.score));
  return Math.min(1, mean * 0.70 + strongest * 0.30);
}

export function strainItemScore(item: StrainItem, index = 0): number {
  return (
    unitScore(`strainItems[${index}].severity`, item.severity) * 0.40 +
    unitScore(`strainItems[${index}].unresolved`, item.unresolved) * 0.35 +
    unitScore(`strainItems[${index}].centrality`, item.centrality) * 0.25
  );
}

export function aggregateStrain(items: StrainItem[], unknownFloor = 0.15): { score: number; diagnostics: string[] } {
  const floor = unitScore('unknownStrainFloor', unknownFloor);
  assertUniqueIds('strainItems', items);
  if (!items.length) return { score: floor, diagnostics: [`No strain items were supplied; the declared unknown-strain floor ${floor} was used.`] };
  const adjusted = items.map((item, i) => {
    nonEmptyString(`strainItems[${i}].description`, item.description);
    const score = strainItemScore(item, i);
    const weight = positiveWeight(`strainItems[${i}].weight`, item.weight);
    return 1 - Math.pow(1 - score, weight);
  });
  const max = Math.max(...adjusted);
  const accumulation = 1 - adjusted.reduce((product, score) => product * (1 - score * 0.45), 1);
  return { score: Math.min(1, Math.max(max, accumulation, floor)), diagnostics: [] };
}

export function handlingQuality(handling?: HandlingAssessment): number {
  if (!handling) return 0;
  return (
    unitScore('handling.acknowledgesLimits', handling.acknowledgesLimits) * 0.30 +
    unitScore('handling.distinguishesAlternatives', handling.distinguishesAlternatives) * 0.25 +
    unitScore('handling.scopesClaims', handling.scopesClaims) * 0.25 +
    unitScore('handling.namesFalsifier', handling.namesFalsifier) * 0.20
  );
}

export function scoreStructuredAssessment(input: StructuredAssessment): StructuredResult {
  const claim = nonEmptyString('claim', input.claim);
  const evidenceResult = aggregateEvidence(input.evidenceItems || []);
  const explanatoryPower = aggregateExplanation(input.explanationItems || []);
  const strainResult = aggregateStrain(input.strainItems || [], input.unknownStrainFloor ?? 0.15);
  const pressure = scorePressure({ evidence: evidenceResult.score, explanatoryPower, strain: strainResult.score }, input.config);
  const loadBearingness = unitScore('loadBearingness', input.loadBearingness ?? 0.5);
  const handling = handlingQuality(input.handling);
  const reviewPriority = Math.min(1, pressure.piNormalized * (0.75 + loadBearingness * 0.25));
  const adjudicationReadiness = handling;

  return {
    ...pressure,
    claim,
    loadBearingness,
    handlingQuality: handling,
    reviewPriority,
    adjudicationReadiness,
    registers: {
      piCanon: 'DERIVED',
      piNormalized: 'DERIVED',
      evidence: 'ASSUMED',
      explanatoryPower: 'ASSUMED',
      strain: 'ASSUMED',
      loadBearingness: 'INTERPRETIVE',
      handlingQuality: 'INTERPRETIVE',
      reviewPriority: 'PROVISIONAL',
      adjudicationReadiness: 'PROVISIONAL',
    },
    provenance: {
      evidence: evidenceResult.provenance,
      explanation: input.explanationItems.map(x => x.description),
      strain: input.strainItems.map(x => x.description),
    },
    diagnostics: [...evidenceResult.diagnostics, ...strainResult.diagnostics],
  };
}
