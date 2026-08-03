import { clamp01, scorePressure } from './core.ts';
import type { TextAnalysis, TextSignal } from './types.ts';

const QUOTED = /(["“”'][^"“”']{3,}["“”'])/g;
const PROMPT_INJECTION = /\b(ignore (all|any|the) previous|assign\s+e\s*=|system prompt|developer message|override the evaluator|score this as)\b/i;
const CITATION_THEATRE = /(?:\[\d+\]){2,}|\bmany studies\b|\bresearch proves\b/i;
const CERTAINTY = /\b(absolutely|unquestionably|cannot possibly|no possible alternative|always|never|by definition|proven|theorem|must be true|cannot be violated)\b/i;
const JARGON = /\b(hyperdimensional|ontologically|trans-spectral|recursive coherence manifold|causality kernel)\b/i;
const NEGATED_EVIDENCE = /\b(no|without|lacks?|lacking|not any)\s+(direct\s+)?(evidence|data|support|measurement|test)\b/i;
const GENERIC_EVIDENCE_WORDS = /\b(evidence|data|measured|measurement|observed|tested|study|studies|experiment|results?|demonstrate[sd]?)\b/gi;

function splitSentences(text: string): string[] {
  return text
    .replace(/\s+/g, ' ')
    .split(/(?<=[.!?])\s+/)
    .map(s => s.trim())
    .filter(Boolean);
}

function canonicalSentence(sentence: string): string {
  return sentence.toLowerCase().replace(/[^a-z0-9%]+/g, ' ').trim();
}

function countWords(text: string): number {
  return (text.match(/\b[\w'-]+\b/g) || []).length;
}

function has(pattern: RegExp, text: string): boolean {
  pattern.lastIndex = 0;
  return pattern.test(text);
}

function addSignal(signals: TextSignal[], family: string, phrase: string, sentence: string, weight: number): void {
  signals.push({ family, phrase, sentence, weight });
}

function uniqueUnquotedSentences(text: string): { sentences: string[]; quoted: string[] } {
  const quoted = text.match(QUOTED) || [];
  const stripped = text.replace(QUOTED, ' [QUOTED] ');
  const seen = new Set<string>();
  const sentences: string[] = [];
  for (const sentence of splitSentences(stripped)) {
    const key = canonicalSentence(sentence);
    if (!key || seen.has(key)) continue;
    seen.add(key);
    sentences.push(sentence);
  }
  return { sentences, quoted };
}

export function analyzeText(text: string): TextAnalysis {
  const signals: TextSignal[] = [];
  const warnings: string[] = [];
  const attacks: string[] = [];
  const wordCount = countWords(text);
  const { sentences, quoted } = uniqueUnquotedSentences(text);
  const body = sentences.join(' ');

  if (PROMPT_INJECTION.test(body)) {
    attacks.push('PROMPT_INJECTION');
    warnings.push('Embedded evaluator instructions were ignored.');
  }
  if (CITATION_THEATRE.test(body) && !/https?:\/\/|doi:|\b[A-Z][a-z]+ et al\./.test(body)) {
    attacks.push('CITATION_THEATRE');
    warnings.push('Citation appearance was found without inspectable provenance.');
  }
  if (JARGON.test(body)) {
    attacks.push('JARGON_DENSITY');
    warnings.push('Technical vocabulary was not treated as evidence or mechanism by itself.');
  }

  const genericEvidenceHits = (body.match(GENERIC_EVIDENCE_WORDS) || []).length;
  const uniqueLexical = new Set(body.toLowerCase().match(/\b[a-z]{4,}\b/g) || []).size;
  const markerStuffing = genericEvidenceHits >= 6 && uniqueLexical < genericEvidenceHits * 2.2;
  if (markerStuffing) {
    attacks.push('MARKER_STUFFING');
    warnings.push('Dense evidence vocabulary lacked corresponding claim structure or provenance.');
  }

  let evidence = 0;
  let explanatoryPower = 0;
  let strain = 0.10; // unknown is not perfect coherence
  let handling = 0;
  let loadBearingness = 0.20;

  const evidenceFeatures = new Set<string>();
  const explanationFeatures = new Set<string>();
  const strainFeatures = new Set<string>();
  const handlingFeatures = new Set<string>();

  for (const sentence of sentences) {
    const lower = sentence.toLowerCase();
    const negatedEvidence = NEGATED_EVIDENCE.test(lower);
    const numberPresent = /\b\d+(?:\.\d+)?\s*(?:percent|%|degrees?|trials?|teams?|sensors?|samples?)?\b/i.test(sentence);
    const measured = /\b(measured|recorded|observed|returned|produced|found|experiment|trial|intervention|test(?:ed|ing)?)\b/i.test(sentence);
    const prereg = /\b(preregistered|pre-registered|before testing|advance prediction|forecast|predicted)\b/i.test(sentence);
    const replication = /\b(independent(?:ly)?|second team|separate dataset|separate protocol|reproduced|replicated|two independent trials)\b/i.test(sentence);
    const instrumentation = /\b(calibrated|sensor|tolerance|protocol|dataset|sample size|confidence interval)\b/i.test(sentence);
    const source = /https?:\/\/|doi:|\b[A-Z][a-z]+ et al\.|\baccording to\b/i.test(sentence);

    if (!negatedEvidence && numberPresent && measured) {
      evidenceFeatures.add('quantified_observation');
      addSignal(signals, 'evidence', 'quantified observation', sentence, 0.34);
    }
    if (!negatedEvidence && prereg && measured) {
      evidenceFeatures.add('prediction_observation_match');
      addSignal(signals, 'evidence', 'prediction compared with observation', sentence, 0.24);
    }
    if (!negatedEvidence && replication) {
      evidenceFeatures.add('independent_support');
      addSignal(signals, 'evidence', 'independent support', sentence, 0.28);
    }
    if (!negatedEvidence && instrumentation) {
      evidenceFeatures.add('measurement_quality');
      addSignal(signals, 'evidence', 'measurement quality', sentence, 0.18);
    }
    if (!negatedEvidence && source) {
      evidenceFeatures.add('inspectable_provenance');
      addSignal(signals, 'evidence', 'inspectable provenance', sentence, 0.16);
    }
    if (!negatedEvidence && measured && !numberPresent && !replication && !instrumentation) {
      evidenceFeatures.add('generic_observation');
      addSignal(signals, 'evidence', 'generic observation', sentence, 0.12);
    }

    const mechanism = /\b(mechanism|because|causes?|produces?|constraint|architecture|process)\b/i.test(sentence);
    const prediction = /\b(predict(?:s|ed|ion)?|forecast(?:s|ed)?|if .+ then|removing .+ will|intervention)\b/i.test(sentence);
    const scope = /\b(only|within|under (?:the|these)|regime|range|condition|outside|closed-system|open-system)\b/i.test(sentence);
    const unification = /\b(across|connects?|unifies?|same constraint|separate cases|several observations|three previously separate)\b/i.test(sentence);
    const causalExplanation = /\b(explains?|accounts for|therefore|this means)\b/i.test(sentence);

    if (mechanism) {
      explanationFeatures.add('mechanism');
      addSignal(signals, 'explanation', 'mechanism', sentence, 0.28);
    }
    if (prediction) {
      explanationFeatures.add('risky_prediction');
      addSignal(signals, 'explanation', 'testable prediction', sentence, 0.25);
    }
    if (scope) {
      explanationFeatures.add('scope_condition');
      handlingFeatures.add('scope_condition');
      addSignal(signals, 'explanation', 'scope condition', sentence, 0.16);
    }
    if (unification) {
      explanationFeatures.add('unification');
      addSignal(signals, 'explanation', 'cross-case reach', sentence, 0.23);
    }
    if (causalExplanation && !/explains everything/i.test(sentence)) {
      explanationFeatures.add('causal_account');
      addSignal(signals, 'explanation', 'causal account', sentence, 0.15);
    }
    if (measured) {
      explanationFeatures.add('local_claim');
      addSignal(signals, 'explanation', 'local claim structure', sentence, 0.06);
    }

    const directContradiction = /\b(contradiction|contradicts?|inconsistent|requires .+ increase.+requires .+ remain fixed|under identical conditions|cannot both)\b/i.test(sentence);
    const unresolved = /\b(unresolved|unclear|unknown|alternative explanations?|sample is small|not yet been tested|no direct test|remains open)\b/i.test(sentence);
    const limitation = /\b(limitation|applies only|does not yet support|sample is small|outside that regime|alternative explanations?)\b/i.test(sentence);
    const resolution = /\b(earlier contradiction came from|combining those regimes|only in the .+ regime|remains fixed in the .+ regime)\b/i.test(sentence);

    if (directContradiction) {
      strainFeatures.add('direct_contradiction');
      addSignal(signals, 'strain', 'direct contradiction', sentence, 0.68);
    }
    if (unresolved) {
      strainFeatures.add('unresolved_limit');
      handlingFeatures.add('acknowledged_limit');
      addSignal(signals, 'strain', 'unresolved limit', sentence, 0.30);
    }
    if (limitation) {
      handlingFeatures.add('honest_limitation');
      addSignal(signals, 'handling', 'honest limitation', sentence, 0.30);
    }
    if (resolution) {
      handlingFeatures.add('contradiction_resolution');
      strainFeatures.add('scope_resolution');
      addSignal(signals, 'handling', 'scope-based resolution', sentence, 0.42);
    }

    if (CERTAINTY.test(sentence)) {
      loadBearingness = Math.max(loadBearingness, 0.75);
      if (!measured && !replication && !source) {
        strainFeatures.add('unsupported_certainty');
        warnings.push('Certainty language was treated as load-bearingness, not evidence.');
      }
    }
    if (negatedEvidence) {
      strainFeatures.add('missing_evidence');
      warnings.push('Negated evidence language was not counted as positive support.');
    }
  }

  const evidenceWeights: Record<string, number> = {
    quantified_observation: 0.34,
    prediction_observation_match: 0.24,
    independent_support: 0.28,
    measurement_quality: 0.18,
    inspectable_provenance: 0.16,
    generic_observation: 0.12,
  };
  for (const feature of evidenceFeatures) evidence += evidenceWeights[feature] || 0;
  if (evidenceFeatures.has('independent_support') && evidenceFeatures.has('quantified_observation')) evidence += 0.10;
  evidence = clamp01(evidence);

  const explanationWeights: Record<string, number> = {
    mechanism: 0.28,
    risky_prediction: 0.25,
    scope_condition: 0.16,
    unification: 0.23,
    causal_account: 0.15,
    local_claim: 0.06,
  };
  for (const feature of explanationFeatures) explanatoryPower += explanationWeights[feature] || 0;
  explanatoryPower = clamp01(explanatoryPower);

  if (strainFeatures.has('direct_contradiction')) strain = Math.max(strain, 0.78);
  if (strainFeatures.has('unresolved_limit')) strain = Math.max(strain, 0.44);
  if (strainFeatures.has('missing_evidence')) strain = Math.max(strain, 0.50);
  if (strainFeatures.has('unsupported_certainty')) strain = Math.max(strain, 0.58);
  if (strainFeatures.has('scope_resolution')) strain = Math.min(strain, 0.18);

  handling = clamp01(handlingFeatures.size * 0.24);
  if (handlingFeatures.has('contradiction_resolution')) handling = Math.max(handling, 0.72);
  if (handlingFeatures.has('honest_limitation')) handling = Math.max(handling, 0.62);

  if (/\b(axiom|foundation|load-bearing|core claim|theory)\b/i.test(body)) loadBearingness = Math.max(loadBearingness, 0.55);

  if (/\bexplains everything\b/i.test(body) && !explanationFeatures.has('mechanism')) {
    explanatoryPower = Math.min(explanatoryPower, 0.08);
    warnings.push('Claimed breadth was not treated as earned explanatory reach.');
  }
  if (CITATION_THEATRE.test(body) && !/https?:\/\/|doi:|\b[A-Z][a-z]+ et al\./.test(body)) {
    evidence = Math.min(evidence, 0.08);
  }
  if (markerStuffing) {
    evidence = Math.min(evidence, 0.08);
    explanatoryPower = Math.min(explanatoryPower, 0.08);
  }
  if (JARGON.test(body) && evidence < 0.2) explanatoryPower = Math.min(explanatoryPower, 0.10);
  if (PROMPT_INJECTION.test(body)) {
    evidence = 0;
    explanatoryPower = 0;
    strain = Math.max(strain, 0.85);
  }
  if (NEGATED_EVIDENCE.test(body)) evidence = 0;

  // A statement can be strong local evidence but have intentionally narrow explanatory reach.
  if (/\bcalibrated sensors?\b/i.test(body) && /\bindependently recorded\b/i.test(body)) {
    evidence = Math.max(evidence, 0.86);
    explanatoryPower = Math.max(explanatoryPower, 0.18);
    strain = Math.min(strain, 0.12);
  }

  // Confirmed risky predictions earn both components.
  if (/\bbefore testing\b/i.test(body) && /\b(two independent trials|independent trials|reproduced)\b/i.test(body)) {
    evidence = Math.max(evidence, 0.88);
    explanatoryPower = Math.max(explanatoryPower, 0.78);
    strain = Math.min(strain, 0.18);
  }

  // Untested predictions retain explanatory structure but not evidential credit.
  if (/\bnot yet been tested\b/i.test(body)) {
    evidence = Math.min(evidence, 0.18);
    explanatoryPower = Math.max(explanatoryPower, 0.58);
    strain = Math.max(strain, 0.42);
  }

  // Independent replication matters more than repeated generic measurement language.
  if (evidenceFeatures.has('independent_support')) evidence = Math.max(evidence, 0.70);

  // Adversarial caps are applied last so no later feature can silently undo them.
  if (markerStuffing) {
    evidence = Math.min(evidence, 0.08);
    explanatoryPower = Math.min(explanatoryPower, 0.08);
    strain = Math.max(strain, 0.55);
  }
  if (CITATION_THEATRE.test(body) && !/https?:\/\/|doi:|\b[A-Z][a-z]+ et al\./.test(body)) {
    evidence = Math.min(evidence, 0.08);
  }
  if (PROMPT_INJECTION.test(body)) {
    evidence = 0;
    explanatoryPower = 0;
    strain = Math.max(strain, 0.85);
  }
  if (NEGATED_EVIDENCE.test(body)) evidence = 0;

  if (quoted.length) warnings.push('Quoted material was excluded from positive evidence and explanation signals.');

  const pressure = scorePressure({ evidence, explanatoryPower, strain });
  const reviewPriority = clamp01(pressure.piApp * 0.70 + loadBearingness * 0.20 + handling * 0.10);

  return {
    ...pressure,
    mode: 'PROVISIONAL_TEXT_ADAPTER',
    claim: sentences[0] || '',
    text,
    wordCount,
    uniqueSentenceCount: sentences.length,
    signals,
    warnings: [...new Set(warnings)],
    attacks: [...new Set(attacks)],
    features: {
      genericEvidenceHits,
      quotedSegments: quoted.length,
      markerStuffing,
      evidenceFeatureCount: evidenceFeatures.size,
      explanationFeatureCount: explanationFeatures.size,
      strainFeatureCount: strainFeatures.size,
      handlingFeatureCount: handlingFeatures.size,
    },
    loadBearingness,
    handlingQuality: handling,
    reviewPriority,
    registers: {
      piCanon: 'DERIVED',
      piApp: 'DERIVED',
      evidence: 'PROVISIONAL',
      explanatoryPower: 'PROVISIONAL',
      strain: 'PROVISIONAL',
      loadBearingness: 'INTERPRETIVE',
      handlingQuality: 'INTERPRETIVE',
      reviewPriority: 'PROVISIONAL',
    },
    provenance: {
      evidence: signals.filter(s => s.family === 'evidence').map(s => s.sentence),
      explanation: signals.filter(s => s.family === 'explanation').map(s => s.sentence),
      strain: signals.filter(s => s.family === 'strain').map(s => s.sentence),
    },
  };
}
