/**
 * CASCADE Scoring Engine
 * Isolated module — designed for extraction as CASCADE API later.
 *
 * Scoring range: 1–100 (calibrated) | 101–999 (abstract new truth territory)
 * 999 is not a cap — it is the score for claims that exist beyond current verification.
 *
 * Two score tracks:
 *   framework_score  — AI-generated, scored against Codex framework essentials (LOCKED)
 *   sovereign_score  — user's own truth pressure assessment (SOVEREIGN)
 *
 * Core mechanic: Π = E·P/S  (evidence × power / coherence)
 */

export const ONION_LAYERS = [
  { index: 0, name: 'AXIOM',       description: 'The irreducible core claim. If this fails, the block fails.' },
  { index: 1, name: 'FOUNDATION',  description: 'Primary evidence. What holds the axiom up.' },
  { index: 2, name: 'STRUCTURE',   description: 'Logical architecture connecting claim to evidence.' },
  { index: 3, name: 'COHERENCE',   description: 'Internal consistency. Does the block contradict itself?' },
  { index: 4, name: 'RESONANCE',   description: 'Connections to other known truths within the pyramid.' },
  { index: 5, name: 'TENSION',     description: 'Where the claim meets genuine friction. Nigredo territory.' },
  { index: 6, name: 'CONTESTED',   description: 'Active dispute zone. What others challenge.' },
  { index: 7, name: 'SPECULATIVE', description: 'What the claim implies beyond what is proven.' },
  { index: 8, name: 'FRONTIER',    description: 'The unknown edge. What this claim cannot yet account for.' },
]

export const SCORE_BANDS = [
  { min: 0,   max: 0,   label: 'UNSCORED',   color: '#1a1a1a', textColor: '#555' },
  { min: 1,   max: 20,  label: 'WEAK',       color: '#4a1942', textColor: '#e879f9' },
  { min: 21,  max: 40,  label: 'DEVELOPING', color: '#1e3a5f', textColor: '#60a5fa' },
  { min: 41,  max: 60,  label: 'MIDDLE',     color: '#1a3a2a', textColor: '#4ade80' },
  { min: 61,  max: 80,  label: 'STRONG',     color: '#2d2a10', textColor: '#facc15' },
  { min: 81,  max: 100, label: 'FOUNDATION', color: '#2a1800', textColor: '#fb923c' },
  { min: 101, max: 999, label: 'FRONTIER',   color: '#1a0a2e', textColor: '#c084fc' },
]

export function getScoreBand(score) {
  if (!score || score === 0) return SCORE_BANDS[0]
  return SCORE_BANDS.find(b => score >= b.min && score <= b.max) || SCORE_BANDS[1]
}

function getLayerScore(layer, mode) {
  if (mode === 'sovereign') return layer.sovereign_score || 0
  if (mode === 'composite') {
    const f = layer.framework_score || layer.score || 0
    const s = layer.sovereign_score || 0
    if (f && s) return Math.round((f + s) / 2)
    return f || s || 0
  }
  return layer.framework_score || layer.score || 0
}

/**
 * Π = E·P/S  (CASCADE truth pressure formula)
 *
 * E = evidence density — FOUNDATION + STRUCTURE average
 *     (how well the claim is evidenced and architecturally supported)
 * P = power — AXIOM score, the load-bearing claim
 * S = effective coherence — COHERENCE minus pressure from TENSION and CONTESTED
 *     (outer tension compresses the coherence field, increasing pressure)
 *
 * High Π + high coherence = strong stable knowledge
 * High Π + low coherence  = knowledge under pressure, restructuring imminent
 */
export function computePi(layers, mode = 'framework') {
  if (!layers || layers.length < 6) return 0
  const axiom     = getLayerScore(layers[0], mode)
  const foundation = getLayerScore(layers[1], mode)
  const structure  = getLayerScore(layers[2], mode)
  const coherence  = getLayerScore(layers[3], mode)
  const tension    = getLayerScore(layers[5], mode)
  const contested  = layers[6] ? getLayerScore(layers[6], mode) : 0
  if (!axiom) return 0
  const E = (foundation + structure) / 2
  const P = axiom
  // Effective S: tension and contested reduce coherence field
  const effectiveS = Math.max(coherence - (tension * 0.3) - (contested * 0.2), 1)
  return Math.round((E * P) / effectiveS)
}

/**
 * Layer dependency enforcement:
 * FOUNDATION cannot exceed AXIOM × 1.1
 * STRUCTURE cannot exceed FOUNDATION × 1.2
 * Returns array of { layer, violation, cap } for any violations
 */
export function checkLayerDependencies(layers, mode = 'framework') {
  const violations = []
  if (!layers || layers.length < 3) return violations
  const axiom = getLayerScore(layers[0], mode)
  const foundation = getLayerScore(layers[1], mode)
  const structure = getLayerScore(layers[2], mode)
  if (axiom > 0 && foundation > axiom * 1.1) {
    violations.push({ layer: 'FOUNDATION', violation: `${foundation} exceeds AXIOM (${axiom}) × 1.1`, cap: Math.round(axiom * 1.1) })
  }
  if (foundation > 0 && structure > foundation * 1.2) {
    violations.push({ layer: 'STRUCTURE', violation: `${structure} exceeds FOUNDATION (${foundation}) × 1.2`, cap: Math.round(foundation * 1.2) })
  }
  return violations
}

/**
 * Compute block aggregate score — full CASCADE mechanic.
 *
 * CASCADE THEORY: When truth pressure (Π) exceeds coherence thresholds,
 * the knowledge structure reorganises. Inner layers (AXIOM, FOUNDATION,
 * STRUCTURE) are protected invariants. Outer layers demote under pressure.
 *
 * Step 1 — AXIOM gate: no core claim = no block.
 * Step 2 — Dependency caps: FOUNDATION ≤ AXIOM×1.1, STRUCTURE ≤ FOUNDATION×1.2
 * Step 3 — Effective coherence: TENSION and CONTESTED push against the
 *           coherence field (they ARE the pressure). High outer tension
 *           compresses effective S.
 *           effectiveS = COHERENCE - (TENSION×0.3) - (CONTESTED×0.2)
 * Step 4 — Dynamic weights: when effectiveS < 50, inner layers dominate.
 *           Under pressure, the block restructures inward — CASCADE behaviour.
 * Step 5 — Coherence field multiplier on the raw weighted sum.
 * Step 6 — RESONANCE amplifier: well-integrated knowledge gets a small bonus.
 *           (max +8%) — connections to known truths make claims more load-bearing.
 * Step 7 — AXIOM cap: block cannot exceed AXIOM×1.2 (or 999 for frontier).
 */
export const FALSIFIABILITY_CAP = 70

/**
 * Check if the AXIOM layer is unfalsifiable — triggers the gate.
 * Returns true if the block's AXIOM is marked unfalsifiable by the AI.
 */
export function isAxiomUnfalsifiable(layers) {
  if (!layers || layers.length === 0) return false
  return layers[0]?.falsifiable === false
}

export function computeBlockScore(layers, mode = 'framework') {
  if (!layers || layers.length === 0) return 0

  let axiomScore = getLayerScore(layers[0], mode)
  if (!axiomScore || axiomScore === 0) return 0  // no axiom = no block

  // Falsifiability Gate — AXIOM capped at 70 if unfalsifiable
  if (isAxiomUnfalsifiable(layers)) {
    axiomScore = Math.min(axiomScore, FALSIFIABILITY_CAP)
  }

  // Step 2 — Dependency caps
  const foundationRaw = getLayerScore(layers[1], mode)
  const structureRaw  = getLayerScore(layers[2], mode)
  const foundationCap = Math.round(axiomScore * 1.1)
  const effectiveFoundation = Math.min(foundationRaw, foundationCap)
  const structureCap  = Math.round(effectiveFoundation * 1.2)

  const effectiveScores = layers.map((layer, i) => {
    let s = getLayerScore(layer, mode)
    if (i === 1) s = Math.min(s, foundationCap)
    if (i === 2) s = Math.min(s, structureCap)
    return s
  })

  // Step 3 — Effective coherence: outer tension compresses the coherence field
  const coherence  = effectiveScores[3] || 0
  const tension    = effectiveScores[5] || 0
  const contested  = effectiveScores[6] || 0
  const effectiveS = Math.max(coherence - (tension * 0.3) - (contested * 0.2), 5)

  // Step 4 — Dynamic weights: under pressure (effectiveS < 50), inner layers dominate
  // At full coherence: [2.0, 1.8, 1.5, 1.3, 1.1, 0.9, 0.8, 0.7, 0.6]
  // Under pressure:    [2.8, 2.2, 1.8, 1.4, 0.7, 0.4, 0.3, 0.3, 0.2]
  const pressureRatio = coherence > 0 ? Math.max(0, Math.min(1, effectiveS / 80)) : 1.0
  const baseW    = [2.0, 1.8, 1.5, 1.3, 1.1, 0.9, 0.8, 0.7, 0.6]
  const pressureW = [2.8, 2.2, 1.8, 1.4, 0.7, 0.4, 0.3, 0.3, 0.2]
  const weights = baseW.map((b, i) => b * pressureRatio + pressureW[i] * (1 - pressureRatio))

  let weightedSum = 0
  let totalWeight = 0
  effectiveScores.forEach((score, i) => {
    const w = weights[i] || 0.4
    weightedSum += score * w
    totalWeight += w
  })
  const raw = totalWeight > 0 ? weightedSum / totalWeight : 0

  // Step 5 — Coherence field multiplier
  const coherenceMultiplier = coherence > 0
    ? Math.max(0.3, effectiveS / 100)
    : 1.0  // unscored = neutral (don't penalise before AI runs)

  const afterCoherence = raw * coherenceMultiplier

  // Step 6 — Resonance amplifier (connections to known truths = stronger signal)
  const resonance = effectiveScores[4] || 0
  const resonanceBonus = resonance > 0 ? 1 + (resonance / 100) * 0.08 : 1.0  // max +8%

  const afterResonance = afterCoherence * resonanceBonus

  // Step 7 — Hard caps
  const axiomCap = axiomScore * 1.2
  return Math.min(Math.round(afterResonance), Math.round(axiomCap), 999)
}

/**
 * Pyramid-level Π — aggregate truth pressure across all files.
 * E = average file score (evidence density across the pyramid)
 * P = highest file score (the load-bearing knowledge node)
 * S = score spread (high variance = incoherent pyramid)
 */
export function computePyramidPi(files, mode = 'framework') {
  if (!files || files.length < 2) return 0
  const scores = files.map(f => f.score_aggregate || 0).filter(s => s > 0)
  if (scores.length < 2) return 0
  const E = scores.reduce((a, b) => a + b, 0) / scores.length
  const P = Math.max(...scores)
  const mean = E
  const variance = scores.reduce((a, b) => a + Math.pow(b - mean, 2), 0) / scores.length
  const S = Math.max(Math.sqrt(variance), 1)
  return Math.round((E * P) / S)
}

export function computeFileScore(blocks, mode = 'framework') {
  if (!blocks || blocks.length === 0) return 0
  const scores = blocks.map(b => {
    if (mode === 'sovereign') return b.sovereign_score_aggregate || 0
    if (mode === 'composite') {
      const f = b.score_aggregate || 0
      const s = b.sovereign_score_aggregate || 0
      if (f && s) return Math.round((f + s) / 2)
      return f || s || 0
    }
    return b.score_aggregate || 0
  }).filter(s => s > 0)
  if (scores.length === 0) return 0
  return Math.round(scores.reduce((a, b) => a + b, 0) / scores.length)
}

/**
 * Confidence-weighted file score.
 * Blocks that have been adversarially challenged receive a confidence weight
 * based on CI stability: stable=1.0, uncertain=0.75, inflated=0.5.
 * Blocks without CI data are treated as weight=0.85 (slight skepticism).
 * Pinned blocks get a 1.1 weight bonus — user has explicitly endorsed them.
 */
export function computeConfidenceWeightedScore(blocks, adversarialData = {}) {
  if (!blocks || blocks.length === 0) return 0
  let weightedSum = 0
  let totalWeight = 0
  for (const b of blocks) {
    const score = b.score_aggregate || 0
    if (score === 0) continue
    let weight = 0.85 // default: unverified
    const ad = adversarialData[b.id]
    if (ad) {
      if (ad.stability === 'stable')    weight = 1.0
      else if (ad.stability === 'uncertain') weight = 0.75
      else if (ad.stability === 'inflated')  weight = 0.5
    }
    if (b.pinned) weight = Math.min(weight * 1.1, 1.2)
    weightedSum += score * weight
    totalWeight += weight
  }
  if (totalWeight === 0) return 0
  return Math.round(weightedSum / totalWeight)
}

export function computePyramidScore(files, mode = 'framework') {
  if (!files || files.length === 0) return 0
  const scores = files.map(f => f.score_aggregate || 0).filter(s => s > 0)
  if (scores.length === 0) return 0
  return Math.round(scores.reduce((a, b) => a + b, 0) / scores.length)
}

/**
 * Detect cross-block tensions within a file.
 * Two blocks are in tension if their COHERENCE scores diverge > 25 points
 * and they are both scored.
 */
export function detectTensions(blocks) {
  const tensions = []
  const scored = blocks.filter(b => b.score_aggregate > 0)
  for (let i = 0; i < scored.length; i++) {
    for (let j = i + 1; j < scored.length; j++) {
      const a = scored[i], b = scored[j]
      const delta = Math.abs((a.score_aggregate || 0) - (b.score_aggregate || 0))
      if (delta > 25) {
        tensions.push({
          blockA: a, blockB: b, delta,
          stronger: a.score_aggregate > b.score_aggregate ? a : b,
          weaker: a.score_aggregate > b.score_aggregate ? b : a,
        })
      }
    }
  }
  return tensions.sort((a, b) => b.delta - a.delta).slice(0, 5)
}

/**
 * Cascade event — detect if a rescore caused a significant drop.
 * Returns event object if drop > 15 points.
 */
export function detectCascadeEvent(blockId, oldScore, newScore, affectedBlocks) {
  const drop = oldScore - newScore
  if (drop < 15) return null
  return {
    blockId, oldScore, newScore, drop,
    severity: drop > 30 ? 'critical' : 'moderate',
    affected: affectedBlocks.filter(b => b.id !== blockId && b.score_aggregate > 0),
  }
}

/**
 * Truth velocity — compare two score readings.
 * Returns: 'stable' | 'rising' | 'falling' | 'volatile'
 */
export function getTruthVelocity(previousScore, currentScore) {
  if (!previousScore || !currentScore) return 'untracked'
  const delta = currentScore - previousScore
  if (Math.abs(delta) < 5) return 'stable'
  if (delta > 20) return 'rising'
  if (delta < -20) return 'falling'
  return delta > 0 ? 'rising' : 'falling'
}

/**
 * Experiment Engine
 */
export function runExperiment(blocksA, blocksB, mode) {
  const results = []
  if (mode === 'resonance') {
    blocksA.forEach(a => {
      blocksB.forEach(b => {
        const delta = Math.abs((a.score_aggregate || 0) - (b.score_aggregate || 0))
        if (delta <= 15 && a.score_aggregate > 0 && b.score_aggregate > 0) {
          results.push({ type: 'resonance', blockA: a, blockB: b, resonanceScore: Math.round((a.score_aggregate + b.score_aggregate) / 2), delta })
        }
      })
    })
    results.sort((x, y) => y.resonanceScore - x.resonanceScore)
  }
  if (mode === 'contradiction') {
    blocksA.forEach(a => {
      blocksB.forEach(b => {
        const delta = Math.abs((a.score_aggregate || 0) - (b.score_aggregate || 0))
        if (delta > 30 && a.score_aggregate > 0 && b.score_aggregate > 0) {
          const stronger = a.score_aggregate > b.score_aggregate ? a : b
          const weaker = stronger === a ? b : a
          results.push({ type: 'contradiction', blockA: a, blockB: b, delta, stronger, weaker })
        }
      })
    })
    results.sort((x, y) => y.delta - x.delta)
  }
  if (mode === 'synthesis') {
    blocksA.forEach(a => {
      blocksB.forEach(b => {
        const scoreA = a.score_aggregate || 0
        const scoreB = b.score_aggregate || 0
        if (scoreA > 0 && scoreB > 0) {
          // Geometric mean — rewards two strong scores, penalises weak+strong pairing
          const geometricMean = Math.sqrt(scoreA * scoreB)
          // Resonance bonus: scores close together synthesise more powerfully
          // delta=0 → 1.25 multiplier. delta=50 → 1.05 multiplier.
          const delta = Math.abs(scoreA - scoreB)
          const resonanceBonus = 1.25 - (delta / 200)
          const synthesisScore = Math.min(Math.round(geometricMean * resonanceBonus), 999)
          const gain = synthesisScore - Math.max(scoreA, scoreB)
          results.push({ type: 'synthesis', blockA: a, blockB: b, synthesisScore, gain, delta })
        }
      })
    })
    results.sort((x, y) => y.synthesisScore - x.synthesisScore)
  }
  return results.slice(0, 20)
}
