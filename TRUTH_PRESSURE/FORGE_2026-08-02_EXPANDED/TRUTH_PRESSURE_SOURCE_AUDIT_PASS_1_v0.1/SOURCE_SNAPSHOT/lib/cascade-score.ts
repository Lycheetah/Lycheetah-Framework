// Legacy five-layer CASCADE text lens — retained for chat/library compatibility.
// Source: CASCADE_Research_paper_ARXIV, CODEX_AURA_PRIME/01_CASCADE
//
// This heuristic predates the current nine-layer CASCADE monument. It classifies
// text structure; it does not write to the monument or constitute a truth verdict.
// The pyramid: Foundation (invariants) → Theory (working frameworks) → Edge (contradictions/speculation)
// Truth Pressure Π = (E·P)/(S + S₀) — evidence × explanatory power, over the
// entropy of what supports the claim, plus a floor. E, P and S are DENSITIES.
// When Π exceeds threshold → reorganize: contradictions demote to Edge, invariants preserved in Foundation

export type CascadeLayer = {
  name: 'AXIOM' | 'FOUNDATION' | 'THEORY' | 'EDGE' | 'CHAOS';
  glyph: string;
  score: number;        // 0–100 density of this layer's material
  status: 'dominant' | 'present' | 'sparse';
  description: string;
  note: string;
};

export type CascadeResult = {
  layers: CascadeLayer[];
  truthPressure: number;       // Π estimate 0–1
  coherence: number;           // 0–100, inverse of contradiction density. ⚠ NOT the S of Π — S is entropy, this is its inverse.
  reorganisationNeeded: boolean;
  paradoxical: boolean;           // AXIOM > 50 AND CHAOS > 50 — Π diverges mathematically
  structuralContradiction: boolean; // FOUNDATION > 50 AND EDGE > 50 — load-bearing AND contested
  dominantLayer: 'AXIOM' | 'FOUNDATION' | 'THEORY' | 'EDGE' | 'CHAOS';
  invariantCount: number;      // claims presented as load-bearing
  contradictionCount: number;  // conflicting or unresolved claims
  wordCount: number;
  summary: string;
};

// Invariant markers — claims presented as foundational, load-bearing, non-negotiable
const INVARIANT_PATTERNS = [
  /\b(always|never|invariably|by definition|necessarily|fundamentally|at its core|the principle is|this law|cannot be violated|mathematical(ly)?|proven|demonstrated)\b/gi,
  /\b(the foundation|load.bearing|preserv(es?|ing)|ground truth|axiom|theorem|law of|principle of)\b/gi,
  /\b(∀|∃|≡|⊃|therefore|QED|proven|necessarily true|must be|logically follows)\b/gi,
];

// Theory markers — working frameworks, hypotheses, causal reasoning
const THEORY_PATTERNS = [
  /\b(because|therefore|since|thus|consequently|as a result|this means|which implies|this suggests)\b/gi,
  /\b(framework|model|theory|mechanism|pattern|structure|hypothesis|predicts|explains|accounts for)\b/gi,
  /\b(evidence suggests|research shows|data indicates|this demonstrates|we can conclude)\b/gi,
  /\b(if.*then|when.*then|given that|assuming|under the condition)\b/gi,
];

// Edge markers — contradictions, speculation, uncertainty, unresolved tension
const EDGE_PATTERNS = [
  /\b(but|however|although|yet|despite|paradox|contradiction|tension|conflict|unclear|uncertain)\b/gi,
  /\b(might|may|could|possibly|perhaps|arguably|debatable|contested|some argue|others claim)\b/gi,
  /\b(I don't know|unclear|unresolved|open question|remains to be|not yet|we still don't)\b/gi,
  /\b(except|unless|caveat|limitation|edge case|counterexample|fails when|breaks down)\b/gi,
];

// Coherence threats — things that reduce S (structural coherence)
const INCOHERENCE_PATTERNS = [
  /\b(contradicts|conflicts with|undermines|inconsistent with|disagrees with|opposed to)\b/gi,
  /\bbut (actually|in fact|really|wait)\b/gi,
];

function countAll(text: string, patterns: RegExp[]): number {
  return patterns.reduce((sum, re) => {
    re.lastIndex = 0;
    const matches = text.match(re);
    return sum + (matches ? matches.length : 0);
  }, 0);
}

function layerStatus(score: number): 'dominant' | 'present' | 'sparse' {
  if (score >= 55) return 'dominant';
  if (score >= 25) return 'present';
  return 'sparse';
}

export function scoreCASCADE(text: string): CascadeResult {
  const trimmed = text.trim();
  if (!trimmed) return emptyResult();

  const words = trimmed.split(/\s+/).filter(Boolean).length;

  const invariantHits = countAll(trimmed, INVARIANT_PATTERNS);
  const theoryHits = countAll(trimmed, THEORY_PATTERNS);
  const edgeHits = countAll(trimmed, EDGE_PATTERNS);
  const incoherenceHits = countAll(trimmed, INCOHERENCE_PATTERNS);

  const total = Math.max(invariantHits + theoryHits + edgeHits, 1);
  const wordScale = Math.min(words / 100, 1); // normalise short texts

  // Layer scores — proportion of signal belonging to each layer
  const foundationScore = Math.min(100, Math.round(
    (invariantHits / total) * 80 * wordScale +
    (words > 50 ? 10 : 0) +
    (invariantHits > 2 ? 10 : 0)
  ));

  const theoryScore = Math.min(100, Math.round(
    (theoryHits / total) * 80 * wordScale +
    (words > 30 ? 10 : 0) +
    (theoryHits > 3 ? 10 : 0)
  ));

  const edgeScore = Math.min(100, Math.round(
    (edgeHits / total) * 80 * wordScale +
    (edgeHits > 2 ? 10 : 0)
  ));

  // Coherence: high = coherent (low contradiction density). Kept for the UI, which
  // displays it directly. ⚠ It is NOT the S of the Π formula — S is entropy, and
  // this is its inverse. The old code used this variable in S's slot and labelled
  // it "S" in the Library; that conflation is what the rewrite below undoes.
  const coherence = Math.max(0, Math.round(
    100 - (incoherenceHits * 15) - (edgeHits * 3)
  ));

  /* ── TRUTH PRESSURE  Π = (E·P)/(S + S₀) ────────────────────────────────────
     The canon, as `school-content.ts` teaches it: "Evidence times explanatory
     power, over the entropy of what supports the belief, plus a floor."

     ⚠ THIS WAS MEASURED BROKEN, 2026-07-28, and it is worth writing down exactly
     how, because the old line LOOKED like the formula:

         evidencePower = (theoryHits + 1) * (invariantHits + 1)
         rawPi         = evidencePower / (100 / coherenceDiv)
         truthPressure = Math.min(1, rawPi)

     Three faults, compounding:
       1. E and P were RAW COUNTS, so they grew with document length. A product of
          two counts grows quadratically — meaning Π measured how MUCH was written,
          not how well it was supported. That is the "more words = more true"
          fallacy the school exists to attack, running inside its own instrument.
       2. There was no S₀ at all. The denominator was the constant 100.
       3. `Math.min(1, …)` then hid both faults behind a hard clamp.

     MEASURED CONSEQUENCE: Π pinned at 1.000 for any text past ~30 words — including
     a text with coherence 0, i.e. maximum self-contradiction. Every entry in the
     Library reads Π 1.00. The headline number of the CASCADE feature was a constant.

     The repair is to use the formula as written:
       · E, P, S are DENSITIES (markers per 100 words), so length cancels out;
       · each is squashed by d/(d+k) — smooth, monotone, asymptotic, never clamped;
       · S is contradiction density — real entropy, not coherence;
       · S₀ is the floor the curriculum names: without it a perfectly coherent
         system feels infinite pressure from a whisper.
     Multiplying through by S₀ lands the result in 0–1 with no truncation, so
     ordering is preserved at the top of the range — which is the only place
     "earned certainty" was ever supposed to be discriminated.                  */
  const per100 = (hits: number) => (hits / Math.max(words, 1)) * 100;
  const sat = (d: number, k: number) => d / (d + k);

  /* S₀ = 0.05 is the value the curriculum itself names, in the subject "Where the
     Formula Fails — S₀ and the Self-Found Defect" (`subjects.ts`): the empirical
     programme found 7 errors in 847 cascade events, all clustered where 1/S diverged,
     and regularised the formula the same day. That subject also records, in its own
     words, that 0.05 was "a post-hoc fit, labeled as such, awaiting pre-registered
     calibration" — so it is adopted here as the canon value, not as a measured one.
     ⚠ And honestly: our S is a normalised 0–1 DENSITY, so this number is not
     dimensionally the same quantity as the original programme's S. It is the right
     constant to inherit for consistency, and it still owes a calibration. */
  const S0 = 0.05;
  const E = sat(per100(theoryHits), 4);             // evidence density
  const P = sat(per100(invariantHits), 3);          // explanatory power
  const S = sat(per100(incoherenceHits * 2 + edgeHits), 3);  // entropy / strain

  const truthPressure = parseFloat(((E * P * S0) / (S + S0)).toFixed(3));

  // Reorganisation needed when Π high and contradiction density high
  const reorganisationNeeded = truthPressure > 0.6 && incoherenceHits > 1;

  const layers: CascadeLayer[] = [
    {
      name: 'FOUNDATION',
      glyph: '●',
      score: foundationScore,
      status: layerStatus(foundationScore),
      description: 'Load-bearing invariants. Claims that cannot fail without collapsing the structure.',
      note: foundationScore >= 55
        ? 'Strong invariant core — this text has load-bearing principles'
        : foundationScore >= 25
        ? 'Some foundational claims present'
        : 'Weak foundation — few invariants identified',
    },
    {
      name: 'THEORY',
      glyph: '△',
      score: theoryScore,
      status: layerStatus(theoryScore),
      description: 'Working frameworks. Causal reasoning, models, evidence-backed claims.',
      note: theoryScore >= 55
        ? 'Well-developed theoretical layer — strong causal reasoning'
        : theoryScore >= 25
        ? 'Some theoretical structure present'
        : 'Underdeveloped theory — limited causal reasoning',
    },
    {
      name: 'EDGE',
      glyph: '◌',
      score: edgeScore,
      status: layerStatus(edgeScore),
      description: 'Contradictions, speculation, unresolved tensions. CASCADE demotes these here.',
      note: edgeScore >= 55
        ? 'High edge density — significant contradiction or uncertainty'
        : edgeScore >= 25
        ? 'Some edge material — contradiction or speculation present'
        : 'Low edge density — few unresolved tensions',
    },
  ];

  const dominant = [...layers].sort((a, b) => b.score - a.score)[0].name;

  const fScore = layers.find(l => l.name === 'FOUNDATION')?.score ?? 0;
  const eScore = layers.find(l => l.name === 'EDGE')?.score ?? 0;
  const axiomScore = layers.find(l => l.name === 'AXIOM')?.score ?? 0;
  const chaosScore = layers.find(l => l.name === 'CHAOS')?.score ?? 0;

  const structuralContradiction = fScore > 50 && eScore > 50;
  const paradoxical = axiomScore > 50 && chaosScore > 50;

  return {
    layers,
    truthPressure,
    coherence,
    reorganisationNeeded,
    paradoxical,
    structuralContradiction,
    dominantLayer: dominant,
    invariantCount: invariantHits,
    contradictionCount: incoherenceHits,
    wordCount: words,
    summary: buildSummary(dominant, truthPressure, coherence, reorganisationNeeded, structuralContradiction, paradoxical, words),
  };
}

function buildSummary(
  dominant: string,
  pi: number,
  coherence: number,
  reorg: boolean,
  structuralContradiction: boolean,
  paradoxical: boolean,
  words: number,
): string {
  const piDesc = pi > 0.7 ? 'high Π' : pi > 0.3 ? 'moderate Π' : 'low Π';
  const cohDesc = coherence > 70 ? 'coherent' : coherence > 40 ? 'moderate coherence' : 'low coherence';
  const reorgFlag = reorg ? ' · ⚠ REORGANISE' : '';
  const paradoxFlag = paradoxical ? ' · ⚡ PARADOX' : structuralContradiction ? ' · ⚠ STRUCTURAL TENSION' : '';
  return `${words}w · ${dominant} dominant · ${piDesc} · ${cohDesc}${reorgFlag}${paradoxFlag}`;
}

function emptyResult(): CascadeResult {
  return {
    layers: [], truthPressure: 0, coherence: 100,
    reorganisationNeeded: false, paradoxical: false, structuralContradiction: false, dominantLayer: 'THEORY',
    invariantCount: 0, contradictionCount: 0, wordCount: 0,
    summary: 'Paste text to analyse with the legacy structure lens.',
  };
}
