/**
 * CASCADE AI Scoring — DeepSeek BYOK
 * Scores against real Codex framework essentials.
 * Framework score is LOCKED — sovereign score stays with the user.
 */

import { buildFrameworkContext } from './frameworks.js'

const DEEPSEEK_URL = 'https://api.deepseek.com/chat/completions'
const MODEL = 'deepseek-chat'

function getKey() {
  return localStorage.getItem('cascade_deepseek_key') || ''
}

async function chat(systemPrompt, userPrompt, maxTokens = 1200) {
  const key = getKey()
  if (!key) throw new Error('No DeepSeek API key. Add one in Settings.')

  const res = await fetch(DEEPSEEK_URL, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${key}`,
    },
    body: JSON.stringify({
      model: MODEL,
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
 * Returns array of { layer_name, framework_score, framework_reasoning }
 *
 * The framework essentials ARE the scoring reference — not a generic AI guess.
 * This score is LOCKED after generation. Framework integrity preserved.
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

Return ONLY a JSON array of exactly 9 objects in layer order (AXIOM first):
{ "layer_name": string, "framework_score": integer, "framework_reasoning": string (one sentence) }

JSON only. No preamble.`

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
    throw new Error('AI returned unexpected format. Try again.')
  }
}
