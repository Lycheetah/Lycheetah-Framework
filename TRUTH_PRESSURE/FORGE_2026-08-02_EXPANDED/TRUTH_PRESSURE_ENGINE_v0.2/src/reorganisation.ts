export type ReviewLayer<T = unknown> = {
  name: string;
  content: string;
  score: number;
  metadata?: T;
  invariant?: boolean;
};

export type LayerMove = { from: number; to: number; reason: string };
export type ReviewPlan = {
  fires: boolean;
  threshold: number | null;
  piCanon: number;
  moves: LayerMove[];
  preserved: number[];
  blocked: boolean;
  why: string;
};

export function proposeReview<T>(
  layers: ReviewLayer<T>[],
  piCanon: number,
  thresholdCanon?: number,
  weakInner = 0.40,
  invariantBar = 0.65,
): ReviewPlan {
  if (thresholdCanon === undefined) {
    return { fires: false, threshold: null, piCanon, moves: [], preserved: [], blocked: false, why: 'No validated review threshold was configured.' };
  }
  if (!(piCanon > thresholdCanon)) {
    return { fires: false, threshold: thresholdCanon, piCanon, moves: [], preserved: [], blocked: false, why: 'Pressure did not exceed the configured threshold.' };
  }
  if (layers.length < 6) {
    return { fires: false, threshold: thresholdCanon, piCanon, moves: [], preserved: [], blocked: false, why: 'The layer structure is incomplete.' };
  }

  const inner = [0, 1, 2].filter(i => i < layers.length);
  const edge = [layers.length - 3, layers.length - 2, layers.length - 1];
  const preserved = inner.filter(i => Boolean(layers[i].content.trim()) && (layers[i].invariant || layers[i].score >= invariantBar));
  const open = edge.filter(i => !layers[i].content.trim());
  const candidates = inner
    .filter(i => layers[i].content.trim() && !preserved.includes(i) && layers[i].score <= weakInner)
    .sort((a, b) => layers[a].score - layers[b].score);

  const moves: LayerMove[] = [];
  for (const from of candidates) {
    const to = open.shift();
    if (to === undefined) break;
    moves.push({ from, to, reason: `${layers[from].name} is weak for an inner layer and should be reviewed at ${layers[to].name}.` });
  }
  const blocked = candidates.length > moves.length;
  return {
    fires: true,
    threshold: thresholdCanon,
    piCanon,
    moves,
    preserved,
    blocked,
    why: moves.length
      ? `Pressure exceeded the configured threshold; ${moves.length} reversible move(s) are proposed.`
      : blocked
        ? 'Pressure exceeded the threshold, but no empty edge slot is available.'
        : 'Pressure exceeded the threshold, but no weak inner layer qualified for demotion.',
  };
}

export function applyReviewPlan<T>(layers: ReviewLayer<T>[], plan: ReviewPlan): ReviewLayer<T>[] {
  if (!plan.fires || !plan.moves.length) return layers.map(layer => ({ ...layer }));
  const next = layers.map(layer => ({ ...layer }));
  for (const move of plan.moves) {
    const source = next[move.from];
    const destination = next[move.to];
    next[move.to] = { ...source, name: destination.name };
    next[move.from] = { ...source, content: '', score: 0, metadata: undefined, invariant: false };
  }
  return next;
}

export function revertReviewPlan<T>(original: ReviewLayer<T>[], _changed: ReviewLayer<T>[], _plan: ReviewPlan): ReviewLayer<T>[] {
  return original.map(layer => ({ ...layer }));
}
