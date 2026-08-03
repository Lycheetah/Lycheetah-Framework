export type LayerVerdict = { score: number; reason: string };
export type StrictJudgeVerdict = {
  layers: LayerVerdict[];
  falsifiable: boolean;
  weakestLayer?: string;
  objection?: string;
};

export function parseStrictJudgeVerdict(raw: string, mode: 'score' | 'audit' = 'score'): StrictJudgeVerdict | null {
  try {
    const match = raw.match(/\{[\s\S]*\}/);
    if (!match) return null;
    const parsed = JSON.parse(match[0]) as Record<string, unknown>;
    if (typeof parsed.falsifiable !== 'boolean') return null;

    const layers: LayerVerdict[] = [];
    for (let i = 0; i < 9; i++) {
      const item = parsed[String(i)] as Record<string, unknown> | undefined;
      if (!item || typeof item.score !== 'number' || typeof item.reason !== 'string') return null;
      if (!Number.isFinite(item.score) || item.score < 0 || item.score > 100) return null;
      const reason = item.reason.trim();
      if (!reason) return null;
      layers.push({ score: Math.round(item.score), reason: reason.slice(0, 120) });
    }

    const verdict: StrictJudgeVerdict = { layers, falsifiable: parsed.falsifiable };
    if (mode === 'audit') {
      if (typeof parsed.weakest !== 'string' || typeof parsed.objection !== 'string') return null;
      verdict.weakestLayer = parsed.weakest.slice(0, 24);
      verdict.objection = parsed.objection.slice(0, 200);
    }
    return verdict;
  } catch {
    return null;
  }
}
