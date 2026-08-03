import type { OnionV3Input } from './onion.ts';
import { nonEmptyString, unitScore } from './validation.ts';

export const ONION_JUDGE_CONTRACT = 'TP-ONION-JUDGE-0.5' as const;

export type JudgeMetric = {
  value: number;
  reason: string;
  confidence: number;
};

export type OnionJudgeVerdictV5 = {
  contractVersion: typeof ONION_JUDGE_CONTRACT;
  claim: string;
  axiomLoadBearingness: JudgeMetric;
  foundationEvidence: JudgeMetric;
  structureMechanism: JudgeMetric;
  resonanceUnification: JudgeMetric;
  predictiveReach: JudgeMetric;
  coherence: JudgeMetric;
  tensionMagnitude: JudgeMetric;
  tensionHandlingQuality: JudgeMetric;
  contestedMagnitude: JudgeMetric;
  contestedHandlingQuality: JudgeMetric;
  speculativeExtent: JudgeMetric;
  speculativeLabelQuality: JudgeMetric;
  frontierClarity: JudgeMetric;
  falsifiable: { value: boolean; reason: string; confidence: number };
  objection?: string;
};

const METRIC_KEYS = [
  'axiomLoadBearingness',
  'foundationEvidence',
  'structureMechanism',
  'resonanceUnification',
  'predictiveReach',
  'coherence',
  'tensionMagnitude',
  'tensionHandlingQuality',
  'contestedMagnitude',
  'contestedHandlingQuality',
  'speculativeExtent',
  'speculativeLabelQuality',
  'frontierClarity',
] as const;

type MetricKey = typeof METRIC_KEYS[number];

function stripFence(raw: string): string {
  const trimmed = raw.trim();
  const match = trimmed.match(/^```(?:json)?\s*([\s\S]*?)\s*```$/i);
  return match ? match[1] : trimmed;
}

function metric(key: MetricKey, raw: unknown): JudgeMetric {
  if (!raw || typeof raw !== 'object') throw new TypeError(`${key} must be an object`);
  const value = raw as Record<string, unknown>;
  return {
    value: unitScore(`${key}.value`, value.value),
    reason: nonEmptyString(`${key}.reason`, value.reason).slice(0, 320),
    confidence: unitScore(`${key}.confidence`, value.confidence),
  };
}

export function parseOnionJudgeVerdictV5(raw: string): OnionJudgeVerdictV5 | null {
  try {
    const parsed = JSON.parse(stripFence(raw)) as Record<string, unknown>;
    if (parsed.contractVersion !== ONION_JUDGE_CONTRACT) return null;
    const claim = nonEmptyString('claim', parsed.claim);
    const result = {
      contractVersion: ONION_JUDGE_CONTRACT,
      claim,
    } as OnionJudgeVerdictV5;
    for (const key of METRIC_KEYS) result[key] = metric(key, parsed[key]);
    if (!parsed.falsifiable || typeof parsed.falsifiable !== 'object') return null;
    const f = parsed.falsifiable as Record<string, unknown>;
    if (typeof f.value !== 'boolean') return null;
    result.falsifiable = {
      value: f.value,
      reason: nonEmptyString('falsifiable.reason', f.reason).slice(0, 320),
      confidence: unitScore('falsifiable.confidence', f.confidence),
    };
    if (parsed.objection !== undefined) result.objection = nonEmptyString('objection', parsed.objection).slice(0, 500);
    return result;
  } catch {
    return null;
  }
}

export function onionJudgeVerdictToInput(verdict: OnionJudgeVerdictV5): OnionV3Input {
  return {
    scale: 'unit',
    claim: verdict.claim,
    axiomLoadBearingness: verdict.axiomLoadBearingness.value,
    foundationEvidence: verdict.foundationEvidence.value,
    structureMechanism: verdict.structureMechanism.value,
    resonanceUnification: verdict.resonanceUnification.value,
    predictiveReach: verdict.predictiveReach.value,
    coherence: verdict.coherence.value,
    tensionMagnitude: verdict.tensionMagnitude.value,
    tensionHandlingQuality: verdict.tensionHandlingQuality.value,
    contestedMagnitude: verdict.contestedMagnitude.value,
    contestedHandlingQuality: verdict.contestedHandlingQuality.value,
    speculativeExtent: verdict.speculativeExtent.value,
    speculativeLabelQuality: verdict.speculativeLabelQuality.value,
    frontierClarity: verdict.frontierClarity.value,
    falsifiable: verdict.falsifiable.value,
  };
}

export const ONION_JUDGE_SYSTEM_PROMPT = `You are a cautious epistemic assessment instrument. You do not decide whether a claim is true. You score explicitly separated properties of a structured knowledge block. Distinguish how much unresolved tension exists from how well the author handles that tension. Distinguish evidence from confidence and load-bearingness. Return only JSON matching contract TP-ONION-JUDGE-0.5. Scores and confidence are numbers from 0 to 1.`;

export function buildOnionJudgePrompt(claim: string, layerText: Record<string, string>): string {
  const content = Object.entries(layerText)
    .map(([name, text]) => `${name}:\n${text?.trim() || '(empty)'}`)
    .join('\n\n');
  return `CLAIM:\n${claim.trim() || '(empty)'}\n\nLAYER CONTENT:\n${content}\n\nReturn one JSON object with contractVersion \"${ONION_JUDGE_CONTRACT}\". Each metric must contain {\"value\":0-1,\"reason\":\"plain explanation\",\"confidence\":0-1}. Required metrics: ${METRIC_KEYS.join(', ')}. Also return falsifiable {value:boolean, reason:string, confidence:0-1}. tensionMagnitude means how much unresolved tension exists. tensionHandlingQuality means how well it is acknowledged and bounded. contestedMagnitude and contestedHandlingQuality follow the same separation. speculativeExtent measures how far the claim extends beyond support; speculativeLabelQuality measures how honestly that extension is labelled. Return JSON only.`;
}
