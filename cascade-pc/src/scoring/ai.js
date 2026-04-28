/**
 * CASCADE AI Scoring — Multi-Provider (DeepSeek / Anthropic / OpenAI / Ollama)
 * Provider selected in Settings. All AI functions route through chat() automatically.
 * Framework score is LOCKED — sovereign score stays with the user.
 */

import { buildFrameworkContext } from './frameworks.js'

// ─── Provider routing ─────────────────────────────────────────────────────────

function getProvider() {
  return localStorage.getItem('cascade_provider') || 'deepseek'
}

function getKey(provider) {
  const p = provider || getProvider()
  if (p === 'deepseek')   return localStorage.getItem('cascade_deepseek_key') || ''
  if (p === 'anthropic')  return localStorage.getItem('cascade_anthropic_key') || ''
  if (p === 'openai')     return localStorage.getItem('cascade_openai_key') || ''
  return '' // ollama needs no key
}

function getOllamaModel() {
  return localStorage.getItem('cascade_ollama_model') || 'llama3'
}

async function chat(systemPrompt, userPrompt, maxTokens = 1200) {
  const provider = getProvider()

  if (provider === 'deepseek') {
    return chatDeepSeek(systemPrompt, userPrompt, maxTokens)
  } else if (provider === 'anthropic') {
    return chatAnthropic(systemPrompt, userPrompt, maxTokens)
  } else if (provider === 'openai') {
    return chatOpenAI(systemPrompt, userPrompt, maxTokens)
  } else if (provider === 'ollama') {
    return chatOllama(systemPrompt, userPrompt, maxTokens)
  } else {
    throw new Error(`Unknown provider: ${provider}`)
  }
}

// ─── DeepSeek ─────────────────────────────────────────────────────────────────

async function chatDeepSeek(systemPrompt, userPrompt, maxTokens) {
  const key = getKey('deepseek')
  if (!key) throw new Error('No DeepSeek API key. Add one in Settings.')

  const res = await fetch('https://api.deepseek.com/chat/completions', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${key}`,
    },
    body: JSON.stringify({
      model: 'deepseek-chat',
      messages: [
        { role: 'system', content: systemPrompt },
        { role: 'user', content: userPrompt },
      ],
      max_tokens: maxTokens,
      temperature: 0.2,
    }),
  })

  if (!res.ok) {
    const err = await res.text()
    throw new Error(`DeepSeek error ${res.status}: ${err}`)
  }

  const data = await res.json()
  return data.choices[0].message.content.trim()
}

// ─── Anthropic ────────────────────────────────────────────────────────────────

async function chatAnthropic(systemPrompt, userPrompt, maxTokens) {
  const key = getKey('anthropic')
  if (!key) throw new Error('No Anthropic API key. Add one in Settings.')

  const res = await fetch('https://api.anthropic.com/v1/messages', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'x-api-key': key,
      'anthropic-version': '2023-06-01',
      'anthropic-dangerous-direct-browser-access': 'true',
    },
    body: JSON.stringify({
      model: 'claude-sonnet-4-6',
      max_tokens: maxTokens,
      system: systemPrompt,
      messages: [
        { role: 'user', content: userPrompt },
      ],
    }),
  })

  if (!res.ok) {
    const err = await res.text()
    throw new Error(`Anthropic error ${res.status}: ${err}`)
  }

  const data = await res.json()
  return data.content[0].text.trim()
}

// ─── OpenAI ───────────────────────────────────────────────────────────────────

async function chatOpenAI(systemPrompt, userPrompt, maxTokens) {
  const key = getKey('openai')
  if (!key) throw new Error('No OpenAI API key. Add one in Settings.')

  const res = await fetch('https://api.openai.com/v1/chat/completions', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${key}`,
    },
    body: JSON.stringify({
      model: 'gpt-4o',
      messages: [
        { role: 'system', content: systemPrompt },
        { role: 'user', content: userPrompt },
      ],
      max_tokens: maxTokens,
      temperature: 0.2,
    }),
  })

  if (!res.ok) {
    const err = await res.text()
    throw new Error(`OpenAI error ${res.status}: ${err}`)
  }

  const data = await res.json()
  return data.choices[0].message.content.trim()
}

// ─── Ollama (local) ───────────────────────────────────────────────────────────

async function chatOllama(systemPrompt, userPrompt, maxTokens) {
  const model = getOllamaModel()

  const res = await fetch('http://localhost:11434/api/chat', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      model,
      messages: [
        { role: 'system', content: systemPrompt },
        { role: 'user', content: userPrompt },
      ],
      stream: false,
      options: { num_predict: maxTokens, temperature: 0.2 },
    }),
  })

  if (!res.ok) {
    const err = await res.text()
    throw new Error(`Ollama error ${res.status}: ${err}`)
  }

  const data = await res.json()
  return data.message.content.trim()
}

// ─── Public API ───────────────────────────────────────────────────────────────

/**
 * Consensus scoring — score one block with all configured providers simultaneously.
 * Returns scores from each provider + agreement/divergence analysis.
 */
export async function consensusScore(blockTitle, blockContent, fileContent, frameworkIds = ['cascade']) {
  const providers = ['deepseek', 'anthropic', 'openai', 'ollama']
  const frameworkContext = buildFrameworkContext(frameworkIds)

  const system = `You are a CASCADE epistemic scoring system. Score the following knowledge block across 9 onion layers.

${frameworkContext}

ONION LAYERS: AXIOM, FOUNDATION, STRUCTURE, COHERENCE, RESONANCE, TENSION, CONTESTED, SPECULATIVE, FRONTIER

Return ONLY a JSON array of exactly 9 objects:
{ "layer_name": string, "framework_score": integer (1-100), "framework_reasoning": string }`

  const user = `Block: ${blockTitle}\nContent: ${blockContent || '(none)'}\nSource: ${(fileContent || '').slice(0, 800)}\n\nReturn JSON array only.`

  // Determine which providers are configured
  const available = []
  if (localStorage.getItem('cascade_deepseek_key')) available.push('deepseek')
  if (localStorage.getItem('cascade_anthropic_key')) available.push('anthropic')
  if (localStorage.getItem('cascade_openai_key')) available.push('openai')
  const ollamaModel = localStorage.getItem('cascade_ollama_model')
  if (ollamaModel) available.push('ollama')

  if (available.length < 2) {
    throw new Error('Consensus scoring requires at least 2 configured providers. Add more API keys in Settings.')
  }

  // Score with each available provider concurrently
  const results = await Promise.allSettled(
    available.map(async (p) => {
      const orig = localStorage.getItem('cascade_provider')
      localStorage.setItem('cascade_provider', p)
      try {
        const raw = await chat(system, user, 1200)
        const match = raw.match(/\[[\s\S]*\]/)
        if (!match) throw new Error('No JSON')
        const scored = JSON.parse(match[0])
        if (scored.length !== 9) throw new Error('Expected 9 layers')
        const aggregate = Math.round(scored.reduce((a, s) => a + (Number(s.framework_score) || 0), 0) / 9)
        return { provider: p, layers: scored, aggregate }
      } finally {
        localStorage.setItem('cascade_provider', orig)
      }
    })
  )

  const successful = results
    .filter(r => r.status === 'fulfilled')
    .map(r => r.value)

  if (successful.length < 2) throw new Error('Not enough providers responded. Check your API keys.')

  const scores = successful.map(r => r.aggregate)
  const mean = Math.round(scores.reduce((a, b) => a + b, 0) / scores.length)
  const variance = scores.reduce((a, b) => a + Math.pow(b - mean, 2), 0) / scores.length
  const stddev = Math.round(Math.sqrt(variance))
  const agreement = stddev < 8 ? 'strong' : stddev < 20 ? 'moderate' : 'divergent'

  return { providers: successful, mean, stddev, agreement }
}

/**
 * AI Gap Analysis — examines the pyramid and identifies what's MISSING.
 * Returns: gaps, suggested additions, weakest area, next research priority.
 */
export async function analyzeGaps(pyramidName, blocks) {
  const system = `You are a CASCADE gap analyst. You examine a knowledge pyramid and identify what is structurally MISSING — the knowledge gaps, unexamined assumptions, and unexplored territory that would most strengthen the pyramid.

You are proactive, not reactive. Your job is not to evaluate what's there — it's to identify what ISN'T there.

Output format — return ONLY valid JSON:
{
  "weakest_area": "<one sentence: the most underdeveloped conceptual territory in this pyramid>",
  "critical_gaps": [
    "<gap 1: specific missing knowledge that would directly strengthen the pyramid>",
    "<gap 2>",
    "<gap 3>"
  ],
  "suggested_blocks": [
    { "title": "<5-10 word suggested block title>", "reason": "<why this would strengthen the pyramid>" },
    { "title": "...", "reason": "..." }
  ],
  "unexamined_assumptions": ["<assumption 1>", "<assumption 2>"],
  "next_priority": "<one sentence: the single most important knowledge gap to address first>",
  "structural_health": <integer 1-100, how complete this pyramid's knowledge coverage is>
}`

  const blockSummary = blocks
    .sort((a, b) => (b.score_aggregate || 0) - (a.score_aggregate || 0))
    .slice(0, 20)
    .map(b => `[${b.score_aggregate || '—'}] ${b.title}${b.content ? ': ' + b.content.slice(0, 120) : ''}`)
    .join('\n')

  const user = `Pyramid: "${pyramidName}"

Current blocks:
${blockSummary}

What is this pyramid MISSING? What gaps would most strengthen it? Return JSON only.`

  const raw = await chat(system, user, 1000)
  try {
    const match = raw.match(/\{[\s\S]*\}/)
    if (!match) throw new Error('No JSON object')
    return JSON.parse(match[0])
  } catch {
    throw new Error('Gap analysis returned unexpected format. Try again.')
  }
}

/**
 * Adversarial Rescore — challenges a block's existing score.
 * Returns a second set of 9 layer scores seeking weaknesses.
 * Gap < 10 = stable. Gap 10–25 = uncertain. Gap > 25 = inflated.
 */
export async function adversarialScore(blockTitle, blockContent, fileContent, frameworkIds = ['cascade']) {
  const frameworkContext = buildFrameworkContext(frameworkIds)

  const system = `You are a CASCADE adversarial evaluator. Your job is NOT to confirm the existing score — your job is to FIND WEAKNESSES.

${frameworkContext}

ONION LAYERS (9 total):
0. AXIOM — 1. FOUNDATION — 2. STRUCTURE — 3. COHERENCE — 4. RESONANCE — 5. TENSION — 6. CONTESTED — 7. SPECULATIVE — 8. FRONTIER

ADVERSARIAL SCORING RULES:
- Seek counter-evidence, unexamined assumptions, and logical gaps
- Apply maximum critical scrutiny — assume the claim is weaker than it appears
- Look for: unfalsifiable axioms, circular reasoning, overreach, contested evidence, hidden complexity
- Do NOT simply reverse the original score — give an honest adversarial assessment
- If the claim genuinely holds under adversarial pressure, score it relatively high even here
- The adversarial score is meant to find the FLOOR, not to destroy

Return ONLY a JSON array of exactly 9 objects:
{ "layer_name": string, "framework_score": integer, "framework_reasoning": string (one sentence — name the specific weakness) }`

  const user = `ADVERSARIAL challenge: find weaknesses in this claim.

Block title: ${blockTitle}
Block content: ${blockContent || '(no additional content)'}

Source document excerpt:
${(fileContent || '').slice(0, 1500)}

Score each layer adversarially — find the weaknesses. JSON only.`

  const raw = await chat(system, user, 1400)
  try {
    const match = raw.match(/\[[\s\S]*\]/)
    if (!match) throw new Error('No JSON array')
    const scored = JSON.parse(match[0])
    if (scored.length !== 9) throw new Error('Expected 9 layers')
    return scored.map(s => ({
      layer_name: s.layer_name,
      framework_score: Math.min(Math.max(Number(s.framework_score) || 0, 0), 999),
      framework_reasoning: s.framework_reasoning || '',
    }))
  } catch {
    throw new Error('Adversarial scorer returned unexpected format. Try again.')
  }
}

/**
 * Paradoxical Truth Seek — Vector Inversion Protocol
 */
export async function paradoxSeek(claimA, claimB, context = '') {
  const system = `You are a CASCADE paradox analyst operating the Vector Inversion Protocol from the AURA Self-Upgrade Engine.

Your task: hold two opposing truths simultaneously. Do NOT resolve the paradox by choosing a side. Find the scale — the level of abstraction, scope, or frame — at which BOTH claims are simultaneously true.

This is the core mechanic: paradox held, not solved, becomes a higher-order truth.

Output format — return ONLY valid JSON:
{
  "vector_a_pressure": <integer 1-100, how much truth-pressure Claim A carries>,
  "vector_b_pressure": <integer 1-100, how much truth-pressure Claim B carries>,
  "tension": "<one sentence: what is the actual contradiction between them>",
  "inversion_scale": "<the frame/scale/dimension at which both are simultaneously true>",
  "synthesis": "<2-3 sentences: the higher-order truth that holds both — this is the upgrade>",
  "axiom": "<one sentence: the irreducible core claim of the synthesis>",
  "srs": <float 0.00-1.00, Symbiotic Resonance Score — how strongly the synthesis resolves the tension>,
  "sigma_i": <float 0.00-0.20, Integrity Variance — lower is better, <0.04 means upgrade confirmed>,
  "upgrade_confirmed": <boolean — true if srs >= 0.75 AND sigma_i < 0.04>,
  "recommended_layers": {
    "AXIOM": <integer score 1-100>,
    "FOUNDATION": <integer score 1-100>,
    "STRUCTURE": <integer score 1-100>,
    "COHERENCE": <integer score 1-100>,
    "RESONANCE": <integer score 1-100>
  }
}

Be honest. A weak synthesis scores low SRS. A forced resolution scores high σ(I). The upgrade is only confirmed when it genuinely holds.`

  const user = `Claim A: ${claimA}

Claim B: ${claimB}

${context ? `Context:\n${context}` : ''}

Run the Vector Inversion Protocol. Find the scale at which both are true. Return JSON only.`

  const raw = await chat(system, user, 1000)
  try {
    const match = raw.match(/\{[\s\S]*\}/)
    if (!match) throw new Error('No JSON object')
    return JSON.parse(match[0])
  } catch {
    throw new Error('AI returned unexpected format. Try again.')
  }
}

/**
 * Multi-block synthesis — up to 10 selected blocks, one emergent truth.
 */
export async function synthesizeBlocks(blocks) {
  const system = `You are a CASCADE multi-block synthesis engine.

You receive up to 10 knowledge blocks selected by a researcher. Your task: find the single emergent truth that arises from holding all of them simultaneously — the truth that none of them contains alone but which becomes visible when all are held together.

Cap your analysis at what the blocks actually contain. Do not inflate or speculate beyond their content.

Output format — return ONLY valid JSON:
{
  "emergent_title": "<5-10 word title for the emergent truth>",
  "core_emergence": "<one sentence: the truth only visible when all blocks are held together>",
  "synthesis": "<3-5 sentences: the full emergent truth>",
  "key_pattern": "<one sentence: the underlying pattern connecting all blocks>",
  "strongest_signal": "<title of the block carrying the most epistemic weight>",
  "outlier": "<title of the block most in tension with the others, or null if none>",
  "coherence": <integer 1-100, how strongly these blocks synthesize>,
  "axiom": "<one sentence: the irreducible core claim of the synthesis>"
}`

  const blockList = blocks
    .slice(0, 10)
    .map((b, i) => `${i + 1}. [${b.score_aggregate || '—'}] ${b.title}${b.content ? ': ' + b.content.slice(0, 200) : ''}`)
    .join('\n')

  const user = `${blocks.length} selected blocks:

${blockList}

Find the emergent truth. Return JSON only.`

  const raw = await chat(system, user, 900)
  try {
    const match = raw.match(/\{[\s\S]*\}/)
    if (!match) throw new Error('No JSON object')
    return JSON.parse(match[0])
  } catch {
    throw new Error('AI returned unexpected format. Try again.')
  }
}

/**
 * Cross-file synthesis — 2 to 10 files, emergent truth from their intersection.
 * files: array of { name, blocks }
 */
export async function crossSynthesize(files) {
  const system = `You are a CASCADE cross-reference synthesis engine.

You receive ${files.length} sets of knowledge blocks from different files. Your task: find the truth that exists at their collective intersection — the truth that none of the files contains alone, but which only becomes visible when all are held simultaneously.

This is not a merger or summary. It is the truth that ARISES BETWEEN them.

Output format — return ONLY valid JSON:
{
  "intersection_title": "<5-10 word title for the emergent truth>",
  "core_emergence": "<one sentence: the truth only visible when all files are held together>",
  "synthesis": "<3-5 sentences: the cross-reference truth in full>",
  "resonance_points": ["<shared pattern across files>", "<second resonance>"],
  "tension_points": ["<genuine conflict between files>"],
  "file_contributions": [{"file": "<name>", "contribution": "<one sentence>"}],
  "cross_coherence": <integer 1-100>,
  "axiom": "<one sentence: irreducible core claim of the emergent truth>"
}`

  const formatFile = ({ name, blocks }) => {
    const top = blocks
      .filter(b => b.score_aggregate > 0 || b.content)
      .sort((a, b) => (b.score_aggregate || 0) - (a.score_aggregate || 0))
      .slice(0, 8)
      .map(b => `  [${b.score_aggregate || '—'}] ${b.title}${b.content ? ': ' + b.content.slice(0, 120) : ''}`)
      .join('\n')
    return `File: "${name}"\n${top}`
  }

  const user = files.map(formatFile).join('\n\n') + '\n\nFind the truth that arises at the intersection of all these files. Return JSON only.'

  const raw = await chat(system, user, 1200)
  try {
    const match = raw.match(/\{[\s\S]*\}/)
    if (!match) throw new Error('No JSON object')
    return JSON.parse(match[0])
  } catch {
    throw new Error('AI returned unexpected format. Try again.')
  }
}

/**
 * Synthesize all scored blocks in a pyramid into a unified truth statement.
 */
export async function synthesizePyramid(pyramidName, blocks) {
  const system = `You are a CASCADE synthesis engine. You receive a set of scored knowledge blocks from a knowledge pyramid and produce a unified synthesis — the highest-order truth that holds all the blocks together.

This is not a summary. A summary lists. A synthesis reveals the deeper structure underneath.

Output format — return ONLY valid JSON:
{
  "synthesis_title": "<5-10 word title for the unified truth>",
  "core_claim": "<one sentence: the irreducible truth that all blocks point toward>",
  "synthesis": "<3-5 sentences: the unified truth statement that holds all blocks together>",
  "key_tensions": ["<tension 1>", "<tension 2>"],
  "strongest_block": "<title of the highest-epistemic-weight block>",
  "weakest_link": "<title of the block most at risk of pulling the pyramid apart>",
  "pyramid_coherence": <integer 1-100, overall coherence of the pyramid as a unified whole>,
  "recommended_next": "<one sentence: what knowledge would most strengthen this pyramid>"
}`

  const blockSummary = blocks
    .filter(b => b.score_aggregate > 0)
    .sort((a, b) => b.score_aggregate - a.score_aggregate)
    .map(b => `[${b.score_aggregate}] ${b.title}${b.content ? ': ' + b.content.slice(0, 200) : ''}`)
    .join('\n')

  const user = `Pyramid: "${pyramidName}"

Scored blocks (score · title · content excerpt):
${blockSummary}

Synthesize these into the unified truth they collectively point toward. Return JSON only.`

  const raw = await chat(system, user, 1000)
  try {
    const match = raw.match(/\{[\s\S]*\}/)
    if (!match) throw new Error('No JSON object')
    return JSON.parse(match[0])
  } catch {
    throw new Error('AI returned unexpected format. Try again.')
  }
}

/**
 * Recursive synthesis — takes a synthesis block (which has source_block_ids)
 * and synthesizes it with a list of NEW blocks (not in the original synthesis).
 * Produces an upgraded second-order synthesis.
 */
export async function recursiveSynthesize(synthesisBlock, newBlocks) {
  const system = `You are a CASCADE recursive synthesis engine — operating at the second order.

You receive a FIRST-ORDER SYNTHESIS block (which is itself the product of a previous synthesis)
and NEW blocks that were created or scored after that synthesis.

Your task: produce a SECOND-ORDER SYNTHESIS — an upgraded truth that holds the original synthesis AND the new blocks simultaneously.

This is not a summary. It is a truth upgrade: the original synthesis being pressured by new knowledge.

Output format — return ONLY valid JSON:
{
  "emergent_title": "<6-10 word title for the second-order synthesis>",
  "core_upgrade": "<one sentence: the specific way the new knowledge upgrades the original synthesis>",
  "synthesis": "<3-5 sentences: the full second-order truth>",
  "what_survived": "<one sentence: what from the first synthesis still holds>",
  "what_was_upgraded": "<one sentence: what the new blocks changed or extended>",
  "coherence": <integer 1-100>,
  "lineage_score": <integer 1-100, the earned starting score for the new synthesis block>,
  "axiom": "<one sentence: irreducible core claim of the second-order synthesis>"
}`

  const originalContent = `${synthesisBlock.title}\n${synthesisBlock.content || ''}`.slice(0, 800)
  const newBlockList = newBlocks
    .slice(0, 8)
    .map((b, i) => `${i + 1}. [${b.score_aggregate || '—'}] ${b.title}${b.content ? ': ' + b.content.slice(0, 150) : ''}`)
    .join('\n')

  const user = `FIRST-ORDER SYNTHESIS:
${originalContent}

NEW BLOCKS (not in original synthesis):
${newBlockList}

Produce the second-order synthesis. Return JSON only.`

  const raw = await chat(system, user, 900)
  try {
    const match = raw.match(/\{[\s\S]*\}/)
    if (!match) throw new Error('No JSON object')
    return JSON.parse(match[0])
  } catch {
    throw new Error('AI returned unexpected format. Try again.')
  }
}

/**
 * Suggest blocks from file content.
 */
export async function suggestBlocks(fileContent, fileName) {
  const system = `You are a CASCADE knowledge analyst. Extract the most epistemically significant claims from documents. These become blocks in a knowledge pyramid scored for truth pressure.`

  const user = `Document: "${fileName}"

Extract up to 9 epistemically significant claims as knowledge blocks.

Return ONLY a JSON array. Each object:
- "title": 5-10 word claim title
- "content": 1-2 sentences describing the claim

No preamble. JSON only.

Content:
${fileContent.slice(0, 4000)}`

  const raw = await chat(system, user, 800)
  try {
    const match = raw.match(/\[[\s\S]*\]/)
    if (!match) throw new Error('No JSON array')
    return JSON.parse(match[0])
  } catch {
    throw new Error('AI returned unexpected format. Try again.')
  }
}

/**
 * Score all 9 onion layers against selected framework essentials.
 */
export async function scoreBlock(blockTitle, blockContent, fileContent, frameworkIds = ['cascade']) {
  const frameworkContext = buildFrameworkContext(frameworkIds)

  const system = `You are a CASCADE epistemic scoring system operating as a framework evaluator.

You score knowledge blocks against the following framework specifications. These are the TRUTH PRESSURE REFERENCES — real documents from the Lycheetah Framework Codex. Score strictly against these frameworks. Do not invent criteria.

${frameworkContext}

---

ONION LAYERS (9 total, scored innermost to outermost):
0. AXIOM       — The irreducible core claim. If this fails, the block fails.
1. FOUNDATION  — Primary supporting evidence.
2. STRUCTURE   — Logical architecture connecting claim to evidence.
3. COHERENCE   — Internal consistency. Does the block contradict itself?
4. RESONANCE   — Connections to other known truths.
5. TENSION     — Where the claim meets genuine friction.
6. CONTESTED   — Active dispute zone. What others challenge.
7. SPECULATIVE — Beyond current proof.
8. FRONTIER    — The unknown edge.

SCORING RULES:
- Range: 1–100 calibrated | 101–999 for abstract new truths beyond verification
- Score each layer based on how strongly the claim holds AT THAT LAYER specifically
- AXIOM score is the anchor — no block should score much higher than its AXIOM
- Be honest. Weak axioms score low. Contested claims score low at CONTESTED.
- Do NOT inflate scores. Framework integrity depends on honest scoring.`

  const user = `Score this block against the framework(s) above.

Block title: ${blockTitle}
Block content: ${blockContent || '(no additional content)'}

Source document excerpt:
${(fileContent || '').slice(0, 1500)}

Return ONLY a JSON array of exactly 9 objects in layer order (AXIOM first).
The AXIOM object must include a "falsifiable" boolean — true if the core claim can in principle be proven false; false if it is unfalsifiable (e.g., tautologies, definitional truths, non-empirical metaphysics).

Each object:
{ "layer_name": string, "framework_score": integer, "framework_reasoning": string (one sentence), "falsifiable": boolean (AXIOM only — omit on other layers) }

JSON only. No preamble.`

  const raw = await chat(system, user, 1400)
  try {
    const match = raw.match(/\[[\s\S]*\]/)
    if (!match) throw new Error('No JSON array')
    const scored = JSON.parse(match[0])
    if (scored.length !== 9) throw new Error('Expected 9 layers')
    // Attach the full prompt to the AXIOM layer for transparency audit
    const auditTrail = `SYSTEM:\n${system}\n\nUSER:\n${user}\n\nRESPONSE:\n${raw}`
    return scored.map((s, i) => ({
      layer_name: s.layer_name,
      framework_score: Math.min(Math.max(Number(s.framework_score) || 0, 0), 999),
      framework_reasoning: s.framework_reasoning || '',
      ...(i === 0 && s.falsifiable !== undefined ? { falsifiable: s.falsifiable } : {}),
      ...(i === 0 ? { score_audit: auditTrail } : {}),
    }))
  } catch {
    throw new Error('AI returned unexpected format. Try again.')
  }
}
