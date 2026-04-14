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
 * Π = E·P/S
 * E = evidence density (FOUNDATION + STRUCTURE average)
 * P = power (AXIOM score — the load-bearing claim)
 * S = coherence (COHERENCE score — internal consistency)
 */
export function computePi(layers, mode = 'framework') {
  if (!layers || layers.length < 4) return 0
  const axiom = getLayerScore(layers[0], mode)
  const foundation = getLayerScore(layers[1], mode)
  const structure = getLayerScore(layers[2], mode)
  const coherence = getLayerScore(layers[3], mode)
  if (!axiom || !coherence) return 0
  const E = (foundation + structure) / 2
  const P = axiom
  const S = Math.max(coherence, 1)
  return Math.round((E * P) / S)
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
 * Compute block aggregate score from its onion layers.
 *
 * Enforcement order:
 *  1. AXIOM = 0 → block collapses to 0 (load-bearing claim missing)
 *  2. Layer dependency caps applied before weighting:
 *       FOUNDATION capped at AXIOM × 1.1
 *       STRUCTURE  capped at FOUNDATION × 1.2
 *  3. Weighted sum: inner layers carry more weight
 *  4. COHERENCE field multiplier: low coherence compresses the aggregate
 *       multiplier = coherence / 100, floored at 0.3 (some signal survives)
 *  5. Hard cap: block cannot exceed AXIOM × 1.2 or 999
 */
export function computeBlockScore(layers, mode = 'framework') {
  if (!layers || layers.length === 0) return 0

  const axiomScore = getLayerScore(layers[0], mode)
  if (!axiomScore || axiomScore === 0) return 0   // no axiom = no block

  // Enforce dependency caps in computation (not just UI warnings)
  const effectiveScores = layers.map((layer, i) => {
    let s = getLayerScore(layer, mode)
    if (i === 1 && axiomScore > 0) s = Math.min(s, Math.round(axiomScore * 1.1))   // FOUNDATION
    if (i === 2) {
      const foundationScore = Math.min(getLayerScore(layers[1], mode), Math.round(axiomScore * 1.1))
      s = Math.min(s, Math.round(foundationScore * 1.2))  // STRUCTURE
    }
    return s
  })

  const weights = [2.0, 1.8, 1.5, 1.3, 1.1, 0.9, 0.8, 0.7, 0.6]
  let weightedSum = 0
  let totalWeight = 0
  effectiveScores.forEach((score, i) => {
    const w = weights[i] || 0.5
    weightedSum += score * w
    totalWeight += w
  })
  const raw = totalWeight > 0 ? weightedSum / totalWeight : 0

  // Coherence as field multiplier — integrity of the block compresses all scores
  const coherenceScore = effectiveScores[3] || 0
  const coherenceMultiplier = coherenceScore > 0
    ? Math.max(0.3, coherenceScore / 100)
    : 1.0   // unscored coherence = neutral (don't penalise before AI runs)

  const afterCoherence = raw * coherenceMultiplier

  const axiomCap = axiomScore * 1.2
  return Math.min(Math.round(afterCoherence), Math.round(axiomCap), 999)
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
