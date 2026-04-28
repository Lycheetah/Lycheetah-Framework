/**
 * CASCADE Framework Reference Contexts
 *
 * These are the TRUTH PRESSURE REFERENCES the AI scores against.
 * Sourced directly from CODEX_AURA_PRIME essentials.md files.
 * Locked — not user-editable. The framework protects its own integrity.
 */

export const FRAMEWORKS = {
  CASCADE: {
    id: 'cascade',
    name: 'CASCADE',
    glyph: '△',
    color: '#facc15',
    tagline: 'Knowledge reorganization under truth pressure',
    essentials: `
CASCADE — Knowledge Reorganization Framework
Source: CODEX_AURA_PRIME/01_CASCADE/essentials.md

CORE: CASCADE triggers automatic restructuring when contradiction density (truth pressure Π) exceeds coherence thresholds. Instead of discarding contradictions, it preserves invariants and demotes conflicting information to edge layers.

PYRAMID:
  Edge (Low)    — Contradictions relegated here
  Theory        — Working frameworks
  Foundation    — Preserved invariants

TRUTH PRESSURE: Π = E·P/S  (evidence × power / coherence)
When Π(K) > Π_threshold: K_new = reorganize(K_old, preserve={invariants}, demote={contradictions})
Load-bearing claims MUST survive reorganization. If they don't, they weren't load-bearing.

MATHEMATICAL GUARANTEES:
- Coherence preserved under all contradiction scenarios
- Invariants mathematically load-bearing
- Phase transitions formalized
- Domain-agnostic (physics, biology, psychology)

SCORING CASCADE CLAIMS:
High truth pressure (strong): Claim survives contradictions. Invariant-like. Explains phase transitions. Mathematically load-bearing. Reorganizes other knowledge around it.
Low truth pressure (weak): Claim collapses under contradiction. Not load-bearing. Peripheral. Cannot explain transitions.
Frontier (101+): Claim opens new phase transition domains. Extends CASCADE principles beyond current verification.
`.trim(),
  },

  AURA: {
    id: 'aura',
    name: 'AURA',
    glyph: '◈',
    color: '#60a5fa',
    tagline: 'Seven invariants — constitutional AI constraints',
    essentials: `
AURA — Constitutional AI Framework
Source: CODEX_AURA_PRIME/02_AURA/essentials.md

AURA (Adversarial constraints testing → Unified Resonance → Alignment) transforms AI ethics from abstract principles into operational, measurable constraints.

THE SEVEN INVARIANTS (load-bearing — mathematically dual to freedom):
1. Human Primacy — Humans retain decision authority; AI advises
2. Inspectability — All reasoning must be auditable/explicable
3. Memory Continuity — Persistent identity; prevents sneaky rewrites
4. Constraint Honesty — Explicit about limitations; no deception
5. Reversibility Bias — Prefer reversible actions
6. Non-Deception — Truth over convenience, always
7. Love as Load-Bearing — Alignment through care, not compliance

OPERATIONAL METRICS:
- TES (Temporal Ethics Score): Constraint consistency over time
- VTR (Values Transparency Rating): Auditability of decision chains
- PAI (Protective Alignment Index): Human autonomy preservation

KEY INSIGHT: Invariants aren't restrictive — they're generative. They enable more human autonomy, not less.

SCORING AURA CLAIMS:
High truth pressure (strong): Preserves all 7 invariants. Measurably increases human autonomy. Reversible. Transparent. Load-bearing under adversarial tests.
Low truth pressure (weak): Violates invariants. Opaque reasoning. Hidden optimization. Irreversible. Reduces human authority.
Frontier (101+): Extends the invariant set. Opens new measurable dimensions of alignment beyond current framework.
`.trim(),
  },

  LAMAGUE: {
    id: 'lamague',
    name: 'LAMAGUE',
    glyph: '∑',
    color: '#c084fc',
    tagline: 'Mathematical grammar — precision notation',
    essentials: `
LAMAGUE — Mathematical Grammar
Source: CODEX_AURA_PRIME/03_LAMAGUE/essentials.md

LAMAGUE is a mathematical grammar providing precise symbolic notation for CASCADE, AURA, Microorcim, and Earned Light. It eliminates ambiguity in human-AI mathematical communication.

CORE SYMBOLS:
Π = Truth Pressure      Φ↑ = Growth/Ascent     Ψ = Awareness/Consciousness
μ = Agency              τ = Phase transition   σ = Boundary/Constraint
⟨|⟩ = Coherence measure

GRAMMAR RULES:
1. Precision over naturality — unambiguous > fluent
2. Composability — symbols build into larger expressions
3. Domain-agnostic — physics to consciousness to ethics
4. Reversible — can translate back to natural language cleanly

KEY INSIGHT: LAMAGUE is not natural language replacement — it's a precision layer. Use English for context, LAMAGUE for specifications. When humans and AIs collaborate on frontier research, ambiguity is dangerous.

SCORING LAMAGUE CLAIMS:
High truth pressure (strong): Translates cleanly to LAMAGUE notation without loss. Composable. Reversible. Eliminates ambiguity.
Low truth pressure (weak): Resists formalization. Ambiguous. Context-dependent. Loses meaning in translation.
Frontier (101+): Requires new LAMAGUE symbols to express. Opens previously unspecifiable mathematical territory.
`.trim(),
  },
}

export const FRAMEWORK_LIST = Object.values(FRAMEWORKS)

// ─── Custom frameworks (user-defined, stored in localStorage) ─────────────────

export function getCustomFrameworks() {
  try {
    return JSON.parse(localStorage.getItem('cascade_custom_frameworks') || '[]')
  } catch { return [] }
}

export function saveCustomFrameworks(list) {
  localStorage.setItem('cascade_custom_frameworks', JSON.stringify(list))
}

export function getAllFrameworks() {
  return [...FRAMEWORK_LIST, ...getCustomFrameworks()]
}

export function getFramework(id) {
  return getAllFrameworks().find(f => f.id === id)
}

// ─── Naked Mode ───────────────────────────────────────────────────────────────
// When enabled: no Codex references — AI scores purely on internal claim logic.

export function isNakedMode() {
  return localStorage.getItem('cascade_naked_mode') === 'true'
}

export function setNakedMode(val) {
  localStorage.setItem('cascade_naked_mode', val ? 'true' : 'false')
}

// ─── Personal Content Filter ─────────────────────────────────────────────────
// When enabled: AI is instructed to skip scoring personal/emotional content
// and instead return a gentle redirect. Prevents the tool from becoming a
// mirror that measures personal pain.

export function isPersonalFilterOn() {
  return localStorage.getItem('cascade_personal_filter') === 'true'
}

export function setPersonalFilter(val) {
  localStorage.setItem('cascade_personal_filter', val ? 'true' : 'false')
}

export const PERSONAL_FILTER_NOTICE = `[PERSONAL CONTENT FILTER ACTIVE]
If this block contains personal emotional content, intimate experience, grief, trauma, or vulnerable self-disclosure — DO NOT SCORE IT.
Instead, set all layer scores to 0 and set framework_reasoning to: "Personal content — scoring suspended. This tool is for epistemic claims, not emotional truth."
If the content IS an epistemic claim (even if emotionally charged), score it normally.`

/**
 * Build the system prompt context from selected framework IDs.
 * Returns empty string in Naked Mode so AI scores without Codex references.
 */
export function buildFrameworkContext(frameworkIds = ['cascade']) {
  const filterNotice = isPersonalFilterOn() ? '\n\n' + PERSONAL_FILTER_NOTICE : ''

  if (isNakedMode()) {
    return `[NAKED MODE — no framework references. Score purely on the internal truth pressure of the claim: logical consistency, evidence quality, and epistemic honesty. No Codex, no external framework.]` + filterNotice
  }

  const selected = (frameworkIds || ['cascade'])
    .map(id => getFramework(id))
    .filter(Boolean)

  if (selected.length === 0) return FRAMEWORKS.CASCADE.essentials + filterNotice

  return selected.map(f => f.essentials).join('\n\n---\n\n') + filterNotice
}
