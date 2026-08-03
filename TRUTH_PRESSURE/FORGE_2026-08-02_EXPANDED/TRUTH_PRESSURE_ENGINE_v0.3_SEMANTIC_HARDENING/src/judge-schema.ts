import { nonEmptyString, unitScore, ValidationError } from './validation.ts';

export const JUDGE_CONTRACT = 'TP-JUDGE-0.3' as const;
export const JUDGE_LAYER_NAMES = [
  'AXIOM', 'FOUNDATION', 'STRUCTURE', 'COHERENCE', 'RESONANCE',
  'TENSION', 'CONTESTED', 'SPECULATIVE', 'FRONTIER',
] as const;

export type JudgeLayer = {
  name: typeof JUDGE_LAYER_NAMES[number];
  score: number;
  reason: string;
  confidence: number;
};

export type JudgeVerdictV3 = {
  contractVersion: typeof JUDGE_CONTRACT;
  layers: JudgeLayer[];
  falsifiable: { value: boolean; reason: string; confidence: number };
  weakestLayer?: typeof JUDGE_LAYER_NAMES[number];
  objection?: string;
};

function stripFence(raw: string): string {
  const trimmed = raw.trim();
  const match = trimmed.match(/^```(?:json)?\s*([\s\S]*?)\s*```$/i);
  return match ? match[1] : trimmed;
}

export function parseJudgeVerdictV3(raw: string, mode: 'score' | 'audit' = 'score'): JudgeVerdictV3 | null {
  try {
    const parsed = JSON.parse(stripFence(raw)) as Record<string, unknown>;
    if (parsed.contractVersion !== JUDGE_CONTRACT) return null;
    if (!Array.isArray(parsed.layers) || parsed.layers.length !== 9) return null;

    const layers = parsed.layers.map((rawLayer, i) => {
      if (!rawLayer || typeof rawLayer !== 'object') throw new ValidationError(`layers[${i}]`, 'must be an object');
      const layer = rawLayer as Record<string, unknown>;
      if (layer.name !== JUDGE_LAYER_NAMES[i]) throw new ValidationError(`layers[${i}].name`, `must be ${JUDGE_LAYER_NAMES[i]}`);
      const score = unitScore(`layers[${i}].score`, layer.score);
      const confidence = unitScore(`layers[${i}].confidence`, layer.confidence);
      const reason = nonEmptyString(`layers[${i}].reason`, layer.reason).slice(0, 240);
      return { name: JUDGE_LAYER_NAMES[i], score, reason, confidence };
    });

    if (!parsed.falsifiable || typeof parsed.falsifiable !== 'object') return null;
    const f = parsed.falsifiable as Record<string, unknown>;
    if (typeof f.value !== 'boolean') return null;
    const falsifiable = {
      value: f.value,
      reason: nonEmptyString('falsifiable.reason', f.reason).slice(0, 240),
      confidence: unitScore('falsifiable.confidence', f.confidence),
    };

    const verdict: JudgeVerdictV3 = { contractVersion: JUDGE_CONTRACT, layers, falsifiable };
    if (mode === 'audit') {
      if (!JUDGE_LAYER_NAMES.includes(parsed.weakestLayer as typeof JUDGE_LAYER_NAMES[number])) return null;
      verdict.weakestLayer = parsed.weakestLayer as typeof JUDGE_LAYER_NAMES[number];
      verdict.objection = nonEmptyString('objection', parsed.objection).slice(0, 400);
    }
    return verdict;
  } catch {
    return null;
  }
}
