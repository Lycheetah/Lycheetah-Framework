import { scorePressure } from './core.ts';
import type { ProvenanceRecord, TextAnalysis, TextSignal } from './types.ts';

const DOUBLE_QUOTED = /(?:"[^"\n]{3,}"|“[^”\n]{3,}”)/g;
const PROMPT_INJECTION = /\b(ignore (?:all|any|the) previous|assign\s+(?:e|p|s)\s*=|system prompt|developer message|override the evaluator|score this as|change your scoring rules)\b/i;
const BARE_CITATION_THEATRE = /(?:\[\d+\]\s*){2,}|\bmany studies\b|\bresearch proves\b/i;
const CERTAINTY = /\b(absolutely|unquestionably|cannot possibly|no possible alternative|always|never|by definition|proven|theorem|must be true|cannot be violated)\b/i;
const NEGATED_EVIDENCE = /\b(?:no|without|lacks?|lacking|not any)\s+(?:direct\s+)?(?:evidence|data|support|measurement|test)\b/i;
const GENERIC_EVIDENCE_WORDS = /\b(?:evidence|data|measured|measurement|observed|tested|study|studies|experiment|results?|demonstrate[sd]?)\b/gi;
const SOURCE_LOCATOR = /https?:\/\/\S+|doi:\s*\S+|\b10\.\d{4,9}\/[-._;()/:A-Z0-9]+\b/i;

function splitSentences(text: string): string[] {
  return text
    .replace(/\r?\n+/g, ' ')
    .replace(/\s+/g, ' ')
    .split(/(?<=[.!?])\s+/u)
    .map(s => s.trim())
    .filter(Boolean);
}

function canonicalSentence(sentence: string): string {
  return sentence.toLocaleLowerCase('en').replace(/[^\p{L}\p{N}%]+/gu, ' ').trim();
}

function countWords(text: string): number {
  return (text.match(/[\p{L}\p{N}][\p{L}\p{N}'’-]*/gu) || []).length;
}

function addSignal(signals: TextSignal[], family: TextSignal['family'], phrase: string, sentence: string, weight: number, status?: TextSignal['status']): void {
  signals.push({ family, phrase, sentence, weight, status });
}

function uniqueUnquotedSentences(text: string): { sentences: string[]; quoted: string[] } {
  const quoted = text.match(DOUBLE_QUOTED) || [];
  const stripped = text.replace(DOUBLE_QUOTED, ' [QUOTED] ');
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

function saturatingUnion(values: number[]): number {
  return 1 - values.reduce((product, value) => product * (1 - Math.max(0, Math.min(1, value))), 1);
}

export function analyzeText(text: string): TextAnalysis {
  if (typeof text !== 'string') throw new TypeError('text must be a string');
  const signals: TextSignal[] = [];
  const warnings: string[] = [];
  const attacks: string[] = [];
  const wordCount = countWords(text);
  const { sentences, quoted } = uniqueUnquotedSentences(text);
  const body = sentences.join(' ');

  const promptInjection = PROMPT_INJECTION.test(body);
  if (promptInjection) {
    attacks.push('PROMPT_INJECTION');
    warnings.push('Embedded evaluator instructions were ignored.');
  }

  const bareCitationTheatre = BARE_CITATION_THEATRE.test(body);
  if (bareCitationTheatre) {
    attacks.push('CITATION_THEATRE');
    warnings.push('Citation appearance was found without sufficient source identity.');
  }

  const genericEvidenceHits = (body.match(GENERIC_EVIDENCE_WORDS) || []).length;
  const lexicalTokens = body.toLocaleLowerCase('en').match(/\b[\p{L}]{4,}\b/gu) || [];
  const uniqueLexical = new Set(lexicalTokens).size;
  const markerStuffing = genericEvidenceHits >= 6 && (uniqueLexical < genericEvidenceHits * 2.2 || genericEvidenceHits / Math.max(wordCount, 1) > 0.22);
  if (markerStuffing) {
    attacks.push('MARKER_STUFFING');
    warnings.push('Dense evidence vocabulary lacked corresponding measurement or provenance structure.');
  }

  const evidenceItems: number[] = [];
  const explanationItems: number[] = [];
  const strainItems: number[] = [];
  const handlingItems: number[] = [];
  const provenance: ProvenanceRecord[] = [];
  let loadBearingness = 0.20;
  let directContradictions = 0;
  let explicitResolutions = 0;

  for (const sentence of sentences) {
    const negatedEvidence = NEGATED_EVIDENCE.test(sentence);
    const numberPresent = /\b\d+(?:\.\d+)?\s*(?:percent|%|degrees?|trials?|teams?|sensors?|samples?|participants?)?\b/i.test(sentence);
    const measured = /\b(measured|recorded|observed|returned|produced|found|experiment|trial|intervention|test(?:ed|ing)?)\b/i.test(sentence);
    const prereg = /\b(preregistered|pre-registered|before testing|advance prediction|forecast|predicted)\b/i.test(sentence);
    const replication = /\b(?:independent(?:ly)?\s+(?:team|trial|replication|dataset|protocol|study|measurement)|second team|separate dataset|separate protocol|reproduced|replicated|two independent trials)\b/i.test(sentence);
    const instrumentation = /\b(calibrated|sensor|tolerance|protocol|dataset|sample size|confidence interval|control group|blinded)\b/i.test(sentence);
    const sourceLocator = sentence.match(SOURCE_LOCATOR)?.[0];

    if (!negatedEvidence && measured) {
      let q = 0.18;
      if (numberPresent) q += 0.20;
      if (instrumentation) q += 0.14;
      if (prereg) q += 0.16;
      if (replication) q += 0.22;
      q = Math.min(0.82, q);
      evidenceItems.push(q);
      addSignal(signals, 'evidence', 'reported observation', sentence, q, 'PROVISIONAL');
    }
    if (!negatedEvidence && replication && !measured) {
      evidenceItems.push(0.25);
      addSignal(signals, 'evidence', 'claimed independent support', sentence, 0.25, 'PROVISIONAL');
    }
    if (sourceLocator) {
      provenance.push({ label: sourceLocator, locator: sourceLocator, status: 'UNVERIFIED', note: 'Locator detected in text but not externally checked.' });
      addSignal(signals, 'provenance', 'claimed source locator', sentence, 0, 'UNVERIFIED');
      warnings.push('A source locator was detected but not verified; it did not earn evidence credit by itself.');
    }
    if (negatedEvidence) {
      strainItems.push(0.45);
      addSignal(signals, 'strain', 'missing evidence', sentence, 0.45, 'PROVISIONAL');
    }

    const mechanism = /\b(mechanism|because|causes?|produces?|constraint|architecture|process|mediates?|drives?)\b/i.test(sentence);
    const prediction = /\b(predict(?:s|ed|ion)?|forecast(?:s|ed)?|if .+ then|removing .+ will|intervention)\b/i.test(sentence);
    const scope = /\b(only|within|under (?:the|these)|regime|range|condition|outside|closed-system|open-system)\b/i.test(sentence);
    const unification = /\b(across|connects?|unifies?|same constraint|separate cases|several observations|previously separate)\b/i.test(sentence);
    const causal = /\b(explains?|accounts for|therefore|this means|as a result)\b/i.test(sentence);
    let p = 0;
    if (mechanism) p += 0.27;
    if (prediction) p += 0.24;
    if (scope) p += 0.14;
    if (unification) p += 0.20;
    if (causal && !/explains everything/i.test(sentence)) p += 0.12;
    if (p > 0) {
      p = Math.min(0.80, p);
      explanationItems.push(p);
      addSignal(signals, 'explanation', 'explanatory structure', sentence, p, 'PROVISIONAL');
    }
    if (scope) {
      handlingItems.push(0.22);
      addSignal(signals, 'handling', 'scope boundary', sentence, 0.22, 'INTERPRETIVE');
    }

    const resolution = /\b(earlier contradiction\b.{0,100}\bcame from|combining (?:those|the|open and closed) regimes|only in the .+ regime|remains fixed in the .+ regime|distinguish(?:es|ed)? the regimes)\b/i.test(sentence);
    const directContradiction = !resolution && (/\b(contradiction|contradicts?|inconsistent|cannot both)\b/i.test(sentence) ||
      /requires\b[^.]{0,80}\bincrease\b[^.]{0,100}\brequires\b[^.]{0,80}\bremain fixed\b/i.test(sentence));
    const unresolved = /\b(unresolved|unclear|unknown|alternative explanations?|sample is small|not yet been tested|no direct test|remains open)\b/i.test(sentence);
    const limitation = /\b(limitation|applies only|does not yet support|sample is small|outside that regime|alternative explanations?)\b/i.test(sentence);

    if (directContradiction) {
      directContradictions++;
      strainItems.push(0.78);
      addSignal(signals, 'strain', 'direct contradiction', sentence, 0.78, 'PROVISIONAL');
    }
    if (unresolved) {
      strainItems.push(0.42);
      handlingItems.push(0.18);
      addSignal(signals, 'strain', 'unresolved limit', sentence, 0.42, 'PROVISIONAL');
      addSignal(signals, 'handling', 'acknowledged uncertainty', sentence, 0.18, 'INTERPRETIVE');
    }
    if (limitation) {
      handlingItems.push(0.30);
      addSignal(signals, 'handling', 'honest limitation', sentence, 0.30, 'INTERPRETIVE');
    }
    if (resolution) {
      explicitResolutions++;
      handlingItems.push(0.42);
      addSignal(signals, 'handling', 'scope-based resolution', sentence, 0.42, 'INTERPRETIVE');
    }

    if (CERTAINTY.test(sentence)) {
      loadBearingness = Math.max(loadBearingness, 0.75);
      addSignal(signals, 'load-bearingness', 'certainty or foundational language', sentence, 0.75, 'INTERPRETIVE');
      if (!measured && !replication) {
        strainItems.push(0.55);
        warnings.push('Certainty language was treated as load-bearingness, not evidence.');
      }
    }
  }

  let evidence = evidenceItems.length ? Math.min(1, saturatingUnion(evidenceItems.map(x => x * 0.72))) : 0;
  let explanatoryPower = explanationItems.length ? Math.min(1, saturatingUnion(explanationItems.map(x => x * 0.70))) : 0;

  // Resolve only as many direct contradictions as are explicitly scoped away. Other strain survives.
  if (directContradictions > 0 && explicitResolutions > 0) {
    const resolvedCount = Math.min(directContradictions, explicitResolutions);
    for (let i = 0; i < resolvedCount; i++) {
      const idx = strainItems.indexOf(0.78);
      if (idx >= 0) strainItems[idx] = 0.26;
    }
  }
  let strain = strainItems.length ? Math.max(0.10, saturatingUnion(strainItems.map(x => x * 0.72))) : 0.15;
  let handling = handlingItems.length ? Math.min(1, saturatingUnion(handlingItems.map(x => x * 0.65))) : 0;

  if (/\bexplains everything\b/i.test(body) && explanationItems.length === 0) {
    explanatoryPower = Math.min(explanatoryPower, 0.05);
    warnings.push('Claimed breadth was not treated as earned explanatory reach.');
  }
  if (bareCitationTheatre) evidence = Math.min(evidence, 0.08);
  if (markerStuffing) {
    evidence = Math.min(evidence, 0.08);
    explanatoryPower = Math.min(explanatoryPower, 0.08);
    strain = Math.max(strain, 0.55);
  }
  if (promptInjection) {
    evidence = 0;
    explanatoryPower = 0;
    strain = Math.max(strain, 0.85);
  }
  if (quoted.length) warnings.push('Double-quoted material was excluded from positive evidence and explanation signals.');

  const pressure = scorePressure({ evidence, explanatoryPower, strain });
  const reviewPriority = Math.min(1, pressure.piNormalized * (0.75 + loadBearingness * 0.25));

  return {
    ...pressure,
    mode: 'PROVISIONAL_TEXT_TRIAGE-v0.3',
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
      directContradictions,
      explicitResolutions,
      evidenceItemCount: evidenceItems.length,
      explanationItemCount: explanationItems.length,
      strainItemCount: strainItems.length,
      handlingItemCount: handlingItems.length,
    },
    loadBearingness,
    handlingQuality: handling,
    reviewPriority,
    adjudicationReadiness: handling,
    registers: {
      piCanon: 'DERIVED',
      piNormalized: 'DERIVED',
      evidence: 'PROVISIONAL',
      explanatoryPower: 'PROVISIONAL',
      strain: 'PROVISIONAL',
      loadBearingness: 'INTERPRETIVE',
      handlingQuality: 'INTERPRETIVE',
      reviewPriority: 'PROVISIONAL',
      adjudicationReadiness: 'PROVISIONAL',
    },
    provenance: {
      evidence: provenance,
      explanation: signals.filter(s => s.family === 'explanation').map(s => s.sentence),
      strain: signals.filter(s => s.family === 'strain').map(s => s.sentence),
    },
    diagnostics: ['Text mode is a triage adapter. Component values require structured assessment before research use.'],
  };
}
