// CASCADE Judge — auto-scoring the 9 onion layers with the engine, not by hand.
// Framework: Mackenzie Conor James Clark / Lycheetah Foundation
//
// This is Truth Pressure running live. The user writes the CLAIM and the CONTENT of each of
// the 9 layers (the actual thinking). The judge reads that content and scores how well each
// layer fulfils its epistemic role — populating `framework_score` per layer. The onion engine
// (cascade-onion.ts) then turns those into Π = E·P/(S+S₀) and the block score. The human's
// `sovereign_score` stays as their OVERRIDE — their disagreement with the engine's verdict.
//
// REGISTER (Reflexive Π): the score is MEASURED, with a language model as the instrument —
// NOT gospel. The truth-pressure tool must pass its own truth-pressure test: never overclaim.
// One model call per block (all 9 layers in one structured pass). Mirrors aura-judge.ts.
//
// Two modes:
//   'score' — fast auto-score: each layer 0–100 + a short reason.
//   'audit' — Depth Audit (Nigredo): same scores PLUS the adversarial read — attacks the
//             axiom's falsifiability, the weakest layer, and the single sharpest objection.
// 'quickBuild' — single-pass: given only the claim, generate content + scores for all 9 layers.

import { sendMessageResilient } from '../ai-client';
import { ONION_LAYERS, type LayerData } from './cascade-onion';
import { resolveCascadeEngine, searchGrounding } from './cascade-engine';
import { noteFault, noteNoKey } from './cascade-diagnosis.ts';

export type CascadeJudgeMode = 'score' | 'audit';

export const CASCADE_JUDGE_SYSTEM =
  'You are the CASCADE engine — a truth-pressure instrument for the Lycheetah framework. You ' +
  'read a knowledge claim and the content of its nine epistemic layers, and you score each ' +
  'layer 0–100 by how well its CONTENT fulfils that layer\'s role. Score by MEANING and ' +
  'evidence, not length or confidence. Be honest and exacting: thin or empty content scores ' +
  'low; genuine evidence and structure score high. You are not flattering the author — you are ' +
  'measuring the claim. Respond with ONLY the requested JSON.';

// Per-layer judging key + the question the engine answers for that layer.
const LAYER_QUESTION: string[] = [
  'AXIOM — is the core claim clear, irreducible, and load-bearing? Score its strength as a claim.',
  'FOUNDATION — how strong is the primary evidence actually presented for the axiom?',
  'STRUCTURE — how sound is the logical architecture connecting claim to evidence?',
  'COHERENCE — how internally consistent is it? Penalise self-contradiction.',
  'RESONANCE — how well does it connect to other established truths?',
  'TENSION — how honestly does it name where the claim meets genuine friction? (Naming tension well scores HIGH.)',
  'CONTESTED — how well does it acknowledge active dispute / what others challenge?',
  'SPECULATIVE — how clearly does it mark what it implies beyond what is proven?',
  'FRONTIER — how honestly does it name the unknown edge it cannot yet account for?',
];

export type LayerVerdict = { score: number; reason: string };
export type CascadeVerdict = {
  layers: LayerVerdict[];       // length 9, indexed to ONION_LAYERS
  falsifiable: boolean;         // AXIOM gate
  weakestLayer?: string;        // audit mode: name of the weakest layer
  objection?: string;           // audit mode: the single sharpest objection
};

export function buildCascadePrompt(claim: string, layers: { content: string }[], mode: CascadeJudgeMode): string {
  const body = ONION_LAYERS.map((l, i) => {
    const content = (layers[i]?.content || '').trim() || '(empty)';
    return `${i}. ${l.name} — ${LAYER_QUESTION[i]}\n   CONTENT: ${content}`;
  }).join('\n');

  const scoreShape = ONION_LAYERS
    .map((l, i) => `"${i}":{"score":<0-100>,"reason":"<≤12 words>"}`)
    .join(',');

  const auditExtra = mode === 'audit'
    ? ',"falsifiable":<true|false>,"weakest":"<layer name>","objection":"<the single sharpest objection, ≤25 words>"'
    : ',"falsifiable":<true|false>';

  const stance = mode === 'audit'
    ? 'Run a NIGREDO adversarial read. Attack the claim at its weakest point. Be cold and exact.'
    : 'Score each layer honestly.';

  return (
    `${stance}\n\nCLAIM: "${claim || '(no claim stated)'}"\n\n` +
    `LAYERS:\n${body}\n\n` +
    `Empty content scores 0. Set "falsifiable" false only if the AXIOM cannot in principle be ` +
    `proven wrong.\nReturn ONLY this JSON:\n{${scoreShape}${auditExtra}}`
  );
}

// Parse the judge's JSON into a verdict. Returns null on ANY parse failure so the caller can
// leave the human's manual scores untouched — a bad judge response never corrupts the block.
export function parseCascadeVerdict(raw: string, mode: CascadeJudgeMode): CascadeVerdict | null {
  try {
    const match = raw.match(/\{[\s\S]*\}/);
    if (!match) return null;
    const parsed = JSON.parse(match[0]) as Record<string, any>;

    const layers: LayerVerdict[] = ONION_LAYERS.map((_, i) => {
      const v = parsed[String(i)];
      const rawScore = v && typeof v.score === 'number' ? v.score : 0;
      const score = Math.max(0, Math.min(100, Math.round(rawScore)));
      const reason = (v && v.reason ? String(v.reason) : '').slice(0, 120);
      return { score, reason };
    });

    // falsifiable defaults TRUE — never trip the gate on absence of data.
    const falsifiable = parsed.falsifiable === false ? false : true;
    const verdict: CascadeVerdict = { layers, falsifiable };
    if (mode === 'audit') {
      if (parsed.weakest) verdict.weakestLayer = String(parsed.weakest).slice(0, 24);
      if (parsed.objection) verdict.objection = String(parsed.objection).slice(0, 200);
    }
    return verdict;
  } catch (err) {
    // ⚠ was `catch { return null }` — see cascade-diagnosis.ts. Still returns
    // null so no caller changed; what is new is that it can now SAY why.
    noteFault('judge', err);
    return null;
  }
}

// ─── Quick Map / Deep Forge ──────────────────────────────────────────────────

const CASCADE_BUILD_SYSTEM =
  'You are the CASCADE engine — a truth-pressure builder for the Lycheetah framework. Given a ' +
  'CLAIM, construct a knowledge block from scratch: write real, substantial content for each ' +
  'of the 9 epistemic layers (what is genuinely known at that layer) AND score each 0–100. ' +
  'Do not pad. Be honest — thin evidence scores low and is named plainly; strong structure ' +
  'scores high. You are building the user\'s best honest knowledge map, not flattering the claim. ' +
  'Respond with ONLY the requested JSON.';

export type QuickBuildResult = {
  layers: { content: string; score: number }[];
  falsifiable: boolean;
  builtBy?: string;   // which engine actually answered (providerUsed) — transparency, not decoration
  grounded?: boolean; // true if real search results fed the build (Deep Forge only)
};

function parseQuickBuild(raw: string): QuickBuildResult | null {
  try {
    const match = raw.match(/\{[\s\S]*\}/);
    if (!match) return null;
    const parsed = JSON.parse(match[0]) as Record<string, any>;
    const layers = ONION_LAYERS.map((_, i) => {
      const v = parsed[String(i)];
      // A safety ceiling, not a target. Deep Forge can legitimately return a developed
      // paragraph here; Quick Map stays much smaller through its explicit prompt contract.
      const content = v?.content ? String(v.content).slice(0, 4000) : '';
      const score   = typeof v?.score === 'number'
        ? Math.max(0, Math.min(100, Math.round(v.score))) : 0;
      return { content, score };
    });
    return { layers, falsifiable: parsed.falsifiable === false ? false : true };
  } catch (err) {
    // ⚠ was `catch { return null }` — see cascade-diagnosis.ts. Still returns
    // null so no caller changed; what is new is that it can now SAY why.
    noteFault('judge', err);
    return null;
  }
}

// deepForge: the user-facing "go deep on this one" pass — forces search grounding (when a
// Brave key exists) and a wider token ceiling. Default (false) is still DeepSeek-forced and
// still real depth; deepForge is for the block worth spending extra time and tokens on.
export async function quickBuildBlock(claim: string, opts?: { deepForge?: boolean }): Promise<QuickBuildResult | null> {
  const { apiKey, model } = await resolveCascadeEngine();
  const deepForge = Boolean(opts?.deepForge);
  const grounding = deepForge ? await searchGrounding(claim) : { text: '', grounded: false };
  const depthInstruction = deepForge
    ? 'Write a developed paragraph for each layer — target 120–220 words where the material genuinely supports it.'
    : 'Make this a concise working map: 2–5 useful sentences, roughly 45–90 words per layer. Name uncertainty instead of padding.';
  const schemaDepth = deepForge
    ? 'a developed honest paragraph, ~120-220 words where earned'
    : 'a concise working map, ~45-90 words';

  const layerLines = ONION_LAYERS.map((l, i) =>
    `${i}. ${l.name} — ${LAYER_QUESTION[i]}`
  ).join('\n');

  const schema = ONION_LAYERS.map((_, i) =>
    `"${i}":{"content":"<${schemaDepth}>","score":<0-100>}`
  ).join(',');

  const prompt =
    (grounding.text
      ? `REAL SEARCH RESULTS — ground the evidence-bearing layers (Foundation, Resonance, ` +
        `Contested) in these where relevant, and say plainly where they don't help:\n${grounding.text}\n\n`
      : '') +
    `CLAIM: "${claim || '(no claim stated)'}"\n\n` +
    `Build this knowledge block. For each layer write honest content AND score it.\n` +
    `${depthInstruction}\n\n` +
    `LAYERS:\n${layerLines}\n\n` +
    `Set "falsifiable" false only if the axiom cannot in principle be proven wrong.\n` +
    `Return ONLY this JSON:\n{${schema},"falsifiable":true|false}`;

  try {
    const res = await sendMessageResilient(
      [{ role: 'user', content: prompt }],
      CASCADE_BUILD_SYSTEM,
      apiKey,
      model,
      undefined,
      'fast',
      // Quick Map is deliberately bounded: it exists to make a claim navigable, not to write
      // nine essays before the user knows the block is worth it. Deep Forge preserves the full
      // 32k ceiling for the claims that have earned that depth.
      deepForge ? 32000 : 12000,
      0.55,
    );
    const parsed = parseQuickBuild(res.text);
    if (!parsed) return null;
    return { ...parsed, builtBy: res.providerUsed as string | undefined, grounded: grounding.grounded };
  } catch (err) {
    // ⚠ was `catch { return null }` — see cascade-diagnosis.ts. Still returns
    // null so no caller changed; what is new is that it can now SAY why.
    noteFault('judge', err);
    return null;
  }
}

// Apply a verdict onto a set of layers: fills framework_score + the axiom falsifiable flag.
// Pure — returns new layer objects, leaving sovereign_score (the human's override) untouched.
export function applyVerdict<T extends LayerData>(layers: T[], verdict: CascadeVerdict): T[] {
  return layers.map((l, i) => {
    const next: T = { ...l, framework_score: verdict.layers[i]?.score ?? 0 };
    if (i === 0) next.falsifiable = verdict.falsifiable;
    return next;
  });
}

// Full async entry point: score (or audit) one block. Resolves the active key/model itself and
// uses the resilient waterfall, so a rate-limited key falls back rather than breaking the audit.
// Returns null if there is no key or the model returns unparseable output (caller keeps state).
export async function auditCascadeBlock(
  claim: string,
  layers: { content: string }[],
  mode: CascadeJudgeMode = 'score',
): Promise<CascadeVerdict | null> {
  const { apiKey, model } = await resolveCascadeEngine();
  const prompt = buildCascadePrompt(claim, layers, mode);
  try {
    const res = await sendMessageResilient(
      [{ role: 'user', content: prompt }],
      CASCADE_JUDGE_SYSTEM,
      apiKey,
      model,
      undefined,
      'fast',
      // 1024 -> 4000: same DeepSeek-is-cheap call as quickBuildBlock -- nine reasoned scores
      // plus a weakest-layer objection deserves real room, not a squeeze.
      4000,
      0.4, // low temperature — scoring wants consistency, not creativity
    );
    return parseCascadeVerdict(res.text, mode);
  } catch (err) {
    // ⚠ was `catch { return null }` — see cascade-diagnosis.ts. Still returns
    // null so no caller changed; what is new is that it can now SAY why.
    noteFault('judge', err);
    return null;
  }
}
