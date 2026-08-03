// CASCADE Onion Engine — 9-layer knowledge-block scoring.
// Framework: Mackenzie Conor James Clark / Lycheetah Foundation
//
// Originated in the CASCADE Cicada PC prototype and now owned by this app's tested
// runtime. The port has since corrected Π's strain direction and named its live
// constants explicitly, so historical source fidelity never outranks visible behaviour.
//
// Scoring range: 1–100 (calibrated) | 101–999 (abstract new-truth / FRONTIER territory).
// Two tracks: framework_score (AI vs Codex, locked) + sovereign_score (your own call).
// Core mechanic: Π = E·P/(S+S₀), where S is the absence of net coherence.
//
// ISOLATED MODULE — nothing imports it yet. Does NOT replace lib/cascade-score.ts (which is
// the lightweight text-layer readout for chat replies — different job, leave it alone).

export type ScoreMode = 'framework' | 'sovereign' | 'composite';

// S₀ — strain floor (regularization constant), imported from TRUTH_PRESSURE_CANON §I.
// The unregularized Π = E·P/S diverges as S → 0: a coherent system gets unbounded pressure
// from weak evidence. The canon's empirical program found this defect (7/847 errors clustered
// at S≈0.1) and fixed it with an additive floor: Π = E·P/(S + S₀), which saturates at E·P/S₀
// instead of diverging. Replaces the old crude hard floors (Math.max(…,1) / Math.max(…,5)),
// which were ALSO inconsistent between functions — this unifies them to one named constant.
// Canon value S₀=0.05 is for a 0–1 scale; this engine's S is on a 0–100 scale, so S₀≈5.
// POST-HOC / calibration-pending (same status the canon declares for its own 0.05).
export const STRAIN_FLOOR = 5;

export type OnionLayer = {
  index: number;
  name: string;
  description: string;
};

export const ONION_LAYERS: OnionLayer[] = [
  { index: 0, name: 'AXIOM',       description: 'The irreducible core claim. If this fails, the block fails.' },
  { index: 1, name: 'FOUNDATION',  description: 'Primary evidence. What holds the axiom up.' },
  { index: 2, name: 'STRUCTURE',   description: 'Logical architecture connecting claim to evidence.' },
  { index: 3, name: 'COHERENCE',   description: 'Internal consistency. Does the block contradict itself?' },
  { index: 4, name: 'RESONANCE',   description: 'Connections to other known truths within the pyramid.' },
  { index: 5, name: 'TENSION',     description: 'Where the claim meets genuine friction. Nigredo territory.' },
  { index: 6, name: 'CONTESTED',   description: 'Active dispute zone. What others challenge.' },
  { index: 7, name: 'SPECULATIVE', description: 'What the claim implies beyond what is proven.' },
  { index: 8, name: 'FRONTIER',    description: 'The unknown edge. What this claim cannot yet account for.' },
];

export type LayerData = {
  framework_score?: number;
  sovereign_score?: number;
  score?: number;       // legacy fallback
  falsifiable?: boolean; // AXIOM layer: false → falsifiability gate caps it
};

export type Block = {
  id: string;
  layers: LayerData[];          // expected length 9 (one per ONION_LAYER)
  score_aggregate?: number;
  sovereign_score_aggregate?: number;
  pinned?: boolean;
};

export type CascadeFile = {
  id: string;
  score_aggregate?: number;
};

export type ScoreBand = {
  min: number;
  max: number;
  label: string;
  color: string;
  textColor: string;
};

export const SCORE_BANDS: ScoreBand[] = [
  { min: 0,   max: 0,   label: 'UNSCORED',   color: '#1a1a1a', textColor: '#555' },
  { min: 1,   max: 20,  label: 'WEAK',       color: '#4a1942', textColor: '#e879f9' },
  { min: 21,  max: 40,  label: 'DEVELOPING', color: '#1e3a5f', textColor: '#60a5fa' },
  { min: 41,  max: 60,  label: 'MIDDLE',     color: '#1a3a2a', textColor: '#4ade80' },
  { min: 61,  max: 80,  label: 'STRONG',     color: '#2d2a10', textColor: '#facc15' },
  { min: 81,  max: 100, label: 'FOUNDATION', color: '#2a1800', textColor: '#fb923c' },
  { min: 101, max: 999, label: 'FRONTIER',   color: '#1a0a2e', textColor: '#c084fc' },
];

export function getScoreBand(score: number): ScoreBand {
  if (!score || score === 0) return SCORE_BANDS[0];
  return SCORE_BANDS.find(b => score >= b.min && score <= b.max) || SCORE_BANDS[1];
}

/* Exported 2026-07-28 for `components/cascade/OnionProfile.tsx`. A view that draws
   layer scores must read them through the SAME function the engine scores them with —
   the alternative is a second truth that drifts, which is how this file ended up with
   two different Π's in the first place. */
export function getLayerScore(layer: LayerData | undefined, mode: ScoreMode): number {
  if (!layer) return 0;
  if (mode === 'sovereign') return layer.sovereign_score || 0;
  if (mode === 'composite') {
    const f = layer.framework_score || layer.score || 0;
    const s = layer.sovereign_score || 0;
    if (f && s) return Math.round((f + s) / 2);
    return f || s || 0;
  }
  return layer.framework_score || layer.score || 0;
}

// Π = E·P/(S+S₀). E = (FOUNDATION+STRUCTURE)/2, P = AXIOM,
// net coherence = COHERENCE − TENSION×0.3 − CONTESTED×0.2, and S is its absence.
export function computePi(layers: LayerData[], mode: ScoreMode = 'framework'): number {
  if (!layers || layers.length < 6) return 0;
  const axiom      = getLayerScore(layers[0], mode);
  const foundation = getLayerScore(layers[1], mode);
  const structure  = getLayerScore(layers[2], mode);
  const coherence  = getLayerScore(layers[3], mode);
  const tension    = getLayerScore(layers[5], mode);
  const contested  = layers[6] ? getLayerScore(layers[6], mode) : 0;
  if (!axiom) return 0;
  const E = (foundation + structure) / 2;
  const P = axiom;

  /* ⚠ S WAS INVERTED HERE UNTIL 2026-07-28, and it was inverted in the one direction
     the framework's central insight depends on.

     The old line was `S = coherence − tension×0.3 − contested×0.2`, then divided by.
     So S rose with COHERENCE, and a more coherent block scored LOWER truth pressure.
     MEASURED before the fix: coherence 20 → Π 280 · coherence 90 → Π 62.

     Canon (`school-content.ts`, `classroom.ts`, `subjects.ts`) is the opposite, and
     says why out loud: "A belief resting on chaotic foundations (high S) cannot be
     moved much by any single finding — too many degrees of freedom to be pinned."
     That is the whole counter-intuitive claim of the framework — a COHERENT structure
     is the one a decisive piece of evidence can actually move, which is why coherent
     systems are the ones that cascade. Inverted, the app taught the reverse.

     The author's composite is kept: `coherence − tension×0.3 − contested×0.2` is a
     good NET COHERENCE. S is simply its absence, which is what strain means. Range
     stays 0–100, so the LOW/MODERATE/HIGH bands in `cascade.tsx` still land — they
     now land on the right texts. */
  const netCoherence = Math.max(coherence - (tension * 0.3) - (contested * 0.2), 0);
  const S = 100 - netCoherence;                // strain: the absence of net coherence
  const effectiveS = S + STRAIN_FLOOR;         // S₀ — saturates instead of diverging
  return Math.round((E * P) / effectiveS);
}

export type DependencyViolation = { layer: string; violation: string; cap: number };

// FOUNDATION ≤ AXIOM×1.1, STRUCTURE ≤ FOUNDATION×1.2
export function checkLayerDependencies(layers: LayerData[], mode: ScoreMode = 'framework'): DependencyViolation[] {
  const violations: DependencyViolation[] = [];
  if (!layers || layers.length < 3) return violations;
  const axiom = getLayerScore(layers[0], mode);
  const foundation = getLayerScore(layers[1], mode);
  const structure = getLayerScore(layers[2], mode);
  if (axiom > 0 && foundation > axiom * 1.1) {
    violations.push({ layer: 'FOUNDATION', violation: `${foundation} exceeds AXIOM (${axiom}) × 1.1`, cap: Math.round(axiom * 1.1) });
  }
  if (foundation > 0 && structure > foundation * 1.2) {
    violations.push({ layer: 'STRUCTURE', violation: `${structure} exceeds FOUNDATION (${foundation}) × 1.2`, cap: Math.round(foundation * 1.2) });
  }
  return violations;
}

export const FALSIFIABILITY_CAP = 70;

// AXIOM marked unfalsifiable → triggers the gate (capped at 70).
export function isAxiomUnfalsifiable(layers: LayerData[]): boolean {
  if (!layers || layers.length === 0) return false;
  return layers[0]?.falsifiable === false;
}

// Full CASCADE block score — dependency caps → effective coherence → dynamic weights →
// coherence multiplier → resonance amplifier → axiom cap.
export function computeBlockScore(layers: LayerData[], mode: ScoreMode = 'framework'): number {
  if (!layers || layers.length === 0) return 0;

  let axiomScore = getLayerScore(layers[0], mode);
  if (!axiomScore || axiomScore === 0) return 0; // no axiom = no block

  if (isAxiomUnfalsifiable(layers)) {
    axiomScore = Math.min(axiomScore, FALSIFIABILITY_CAP);
  }

  const foundationRaw = getLayerScore(layers[1], mode);
  const foundationCap = Math.round(axiomScore * 1.1);
  const effectiveFoundation = Math.min(foundationRaw, foundationCap);
  const structureCap = Math.round(effectiveFoundation * 1.2);

  const effectiveScores = layers.map((layer, i) => {
    let s = getLayerScore(layer, mode);
    if (i === 1) s = Math.min(s, foundationCap);
    if (i === 2) s = Math.min(s, structureCap);
    return s;
  });

  const coherence = effectiveScores[3] || 0;
  const tension   = effectiveScores[5] || 0;
  const contested = effectiveScores[6] || 0;
  /* ⚠ RENAMED 2026-07-28, BEHAVIOUR DELIBERATELY UNCHANGED. This was also called
     `effectiveS`, and it is the SAME expression that was Π's inverted S above — but
     it is not doing S's job here. It is a WEIGHTING axis for the block score, and as
     a net-coherence measure it is defensible on its own terms; only the name was
     lying. Renaming rather than "fixing" it, because I am confident the Π above was
     wrong and NOT confident this one is: changing it would move every block score in
     the app on a hunch. Flagged on the board as A3 — one concept, one implementation. */
  const netCoherence = Math.max(coherence - (tension * 0.3) - (contested * 0.2), 0) + STRAIN_FLOOR;

  // Dynamic weights: as net coherence falls, inner layers dominate.
  const pressureRatio = coherence > 0 ? Math.max(0, Math.min(1, netCoherence / 80)) : 1.0;
  const baseW     = [2.0, 1.8, 1.5, 1.3, 1.1, 0.9, 0.8, 0.7, 0.6];
  const pressureW = [2.8, 2.2, 1.8, 1.4, 0.7, 0.4, 0.3, 0.3, 0.2];
  const weights = baseW.map((b, i) => b * pressureRatio + pressureW[i] * (1 - pressureRatio));

  let weightedSum = 0;
  let totalWeight = 0;
  effectiveScores.forEach((score, i) => {
    const w = weights[i] || 0.4;
    weightedSum += score * w;
    totalWeight += w;
  });
  const raw = totalWeight > 0 ? weightedSum / totalWeight : 0;

  // Coherence floor raised 0.3 → 0.5 (Mac's calibration call, June 24). At 0.3 the multiplier
  // crushed every low-coherence claim into a ~15 mush — contested claims were indistinguishable.
  // 0.5 widens the contested band (~20–45) while keeping the hierarchy (contested still < solid).
  // Deliberate fork from the Cicada source's 0.3. Post-hoc/tunable, like S₀.
  const coherenceMultiplier = coherence > 0 ? Math.max(0.5, netCoherence / 100) : 1.0;
  const afterCoherence = raw * coherenceMultiplier;

  const resonance = effectiveScores[4] || 0;
  const resonanceBonus = resonance > 0 ? 1 + (resonance / 100) * 0.08 : 1.0; // max +8%
  const afterResonance = afterCoherence * resonanceBonus;

  const axiomCap = axiomScore * 1.2;
  return Math.min(Math.round(afterResonance), Math.round(axiomCap), 999);
}

// Pyramid-level Π — E = avg file score, P = max file score, S = score spread (variance).
// S₀ unification (Fable pass, 2026-07-11): this function still carried the crude hard floor
// (Math.max(…, 1)) that this file's own STRAIN_FLOOR comment declares was unified away. At
// spread→0 it diverged exactly the way block-Π once did at S→0 — two healthy blocks scoring
// 60 and 62 read Π≈3782 "PEAK PRESSURE." Now regularized the same way: S + S₀.
// FLAGGED, not changed (Mac ratifies math canon): using score-SPREAD as S means a uniform
// pyramid reads as maximum pressure — defensible as an anti-glass signal (uniformity is
// suspect), but it shares piBand's thresholds with block-Π, whose S means coherence. Two
// different instruments, one symbol, one band scale. Candidate fix: band pyramid-Π on its
// own scale, or report mean block-Π instead. Register: INTERPRETIVE, awaiting Mac's call.
export function computePyramidPi(files: CascadeFile[]): number {
  if (!files || files.length < 2) return 0;
  const scores = files.map(f => f.score_aggregate || 0).filter(s => s > 0);
  if (scores.length < 2) return 0;
  const E = scores.reduce((a, b) => a + b, 0) / scores.length;
  const P = Math.max(...scores);
  const mean = E;
  const variance = scores.reduce((a, b) => a + Math.pow(b - mean, 2), 0) / scores.length;
  const S = Math.sqrt(variance) + STRAIN_FLOOR;
  return Math.round((E * P) / S);
}

export function computeFileScore(blocks: Block[], mode: ScoreMode = 'framework'): number {
  if (!blocks || blocks.length === 0) return 0;
  const scores = blocks.map(b => {
    if (mode === 'sovereign') return b.sovereign_score_aggregate || 0;
    if (mode === 'composite') {
      const f = b.score_aggregate || 0;
      const s = b.sovereign_score_aggregate || 0;
      if (f && s) return Math.round((f + s) / 2);
      return f || s || 0;
    }
    return b.score_aggregate || 0;
  }).filter(s => s > 0);
  if (scores.length === 0) return 0;
  return Math.round(scores.reduce((a, b) => a + b, 0) / scores.length);
}

export type AdversarialData = Record<string, { stability?: 'stable' | 'uncertain' | 'inflated' }>;

// Confidence-weighted file score — adversarially-challenged blocks weighted by CI stability.
export function computeConfidenceWeightedScore(blocks: Block[], adversarialData: AdversarialData = {}): number {
  if (!blocks || blocks.length === 0) return 0;
  let weightedSum = 0;
  let totalWeight = 0;
  for (const b of blocks) {
    const score = b.score_aggregate || 0;
    if (score === 0) continue;
    let weight = 0.85; // default: unverified
    const ad = adversarialData[b.id];
    if (ad) {
      if (ad.stability === 'stable')         weight = 1.0;
      else if (ad.stability === 'uncertain') weight = 0.75;
      else if (ad.stability === 'inflated')  weight = 0.5;
    }
    if (b.pinned) weight = Math.min(weight * 1.1, 1.2);
    weightedSum += score * weight;
    totalWeight += weight;
  }
  if (totalWeight === 0) return 0;
  return Math.round(weightedSum / totalWeight);
}

export function computePyramidScore(files: CascadeFile[]): number {
  if (!files || files.length === 0) return 0;
  const scores = files.map(f => f.score_aggregate || 0).filter(s => s > 0);
  if (scores.length === 0) return 0;
  return Math.round(scores.reduce((a, b) => a + b, 0) / scores.length);
}

export type Tension = { blockA: Block; blockB: Block; delta: number; stronger: Block; weaker: Block };

// Two blocks are in tension if their aggregate scores diverge > 25.
export function detectTensions(blocks: Block[]): Tension[] {
  const tensions: Tension[] = [];
  const scored = blocks.filter(b => (b.score_aggregate || 0) > 0);
  for (let i = 0; i < scored.length; i++) {
    for (let j = i + 1; j < scored.length; j++) {
      const a = scored[i], b = scored[j];
      const delta = Math.abs((a.score_aggregate || 0) - (b.score_aggregate || 0));
      if (delta > 25) {
        tensions.push({
          blockA: a, blockB: b, delta,
          stronger: (a.score_aggregate || 0) > (b.score_aggregate || 0) ? a : b,
          weaker:   (a.score_aggregate || 0) > (b.score_aggregate || 0) ? b : a,
        });
      }
    }
  }
  return tensions.sort((a, b) => b.delta - a.delta).slice(0, 5);
}

export type CascadeEvent = {
  blockId: string; oldScore: number; newScore: number; drop: number;
  severity: 'critical' | 'moderate'; affected: Block[];
};

// A rescore drop > 15 = a cascade event (the structure restructured).
export function detectCascadeEvent(blockId: string, oldScore: number, newScore: number, affectedBlocks: Block[]): CascadeEvent | null {
  const drop = oldScore - newScore;
  if (drop < 15) return null;
  return {
    blockId, oldScore, newScore, drop,
    severity: drop > 30 ? 'critical' : 'moderate',
    affected: affectedBlocks.filter(b => b.id !== blockId && (b.score_aggregate || 0) > 0),
  };
}

export type TruthVelocity = 'stable' | 'rising' | 'falling' | 'volatile' | 'untracked';

export function getTruthVelocity(previousScore: number, currentScore: number): TruthVelocity {
  if (!previousScore || !currentScore) return 'untracked';
  const delta = currentScore - previousScore;
  if (Math.abs(delta) < 5) return 'stable';
  if (delta > 20) return 'rising';
  if (delta < -20) return 'falling';
  return delta > 0 ? 'rising' : 'falling';
}
