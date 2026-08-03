// ─── ⊚ REORGANISATION — the half of CASCADE that was never built ─────────────
//
// Mac, 2026-07-28: *"i want to make sure the scores do anything — whats the point
// in scoring shit that just has a score with no use right"*
//
// He was right, and the measurement was blunt. `cascade-score.ts:8` has promised,
// in a comment, since the beginning:
//
//     "When Π exceeds threshold → reorganize: contradictions demote to Edge,
//      invariants preserved in Foundation"
//
// What actually existed: a boolean, a `⚠ REORGANISE` label, and an `Alert.alert()`
// listing which blocks moved more than 15 points. **The pyramid was byte-identical
// after a cascade event.** The only `reorganize(...)` in the whole codebase was a
// STRING inside a prompt (`lamague-context.ts:82`) — pseudocode we show a model to
// describe the framework, not code that runs. The app measured pressure on a
// structure and then never let the pressure do anything to it.
//
// ⚠ THIS FILE PROPOSES. IT NEVER MUTATES. The workshop readout already states the
// rule — **"ENGINE: MEASURED · SOVEREIGN: YOUR CALL"** — so the engine's job is to
// say what SHOULD move and why, and the human's job is to accept it. An engine that
// silently restructures a person's own belief map would be the single most
// sovereignty-violating thing in the app.
//
// ⚠ AND IT ONLY DOES WHAT THE CANON PROMISES: **demote contradicted material
// outward, preserve invariants inward.** Promotion (outer → inner) is the obvious
// symmetric move and it is deliberately NOT here — the curriculum never claims it,
// and inventing doctrine to make a feature feel complete is how a framework starts
// lying. If Mac wants it, he rules it in; it is not mine to add.

import {
  ONION_LAYERS,
  computePi,
  getLayerScore,
  type LayerData,
  type ScoreMode,
} from './cascade-onion.ts';

export type BuilderLayerLike = LayerData & { content: string };

export type LayerMove = {
  from: number;
  to: number;
  kind: 'demote';
  /** plain words, shown to the human — never a score dump */
  reason: string;
};

export type Reorganisation = {
  /** did the pressure conditions actually hold? false ⇒ show nothing */
  fires: boolean;
  /** one line the human reads first */
  why: string;
  moves: LayerMove[];
  /** invariants explicitly held in place — canon names preservation as an ACT */
  preserved: number[];
  /** true when material should move but the edge has no empty slot */
  blocked: boolean;
};

/* ── the thresholds, all named and all tunable ──────────────────────────────
   τ (tau) is the curriculum's own threshold — the point where "the old structure
   can no longer contain the evidence." The value is ours and is a starting point,
   not a measurement: the same honesty as S₀, which the school's own subject
   records as a post-hoc fit awaiting calibration.

   τ = 200 is where `cascade.tsx`'s own band table crosses from MODERATE into HIGH
   (<100 LOW · <200 MODERATE · <350 HIGH). Tying the trigger to the band the user
   already sees means the UI never says MODERATE while the engine restructures. */
export const TAU = 200;
const WEAK_INNER = 40;             // an inner layer at or below this is not load-bearing
const INVARIANT_BAR = 65;          // at or above this, an inner layer is an invariant

const INNER = [0, 1, 2];           // AXIOM · FOUNDATION · STRUCTURE
const EDGE = [6, 7, 8];            // CONTESTED · SPECULATIVE · FRONTIER

const hasContent = (l: BuilderLayerLike | undefined) => !!(l?.content || '').trim();

/**
 * What SHOULD move, and why. Pure — reads, never writes.
 *
 * ⚠ Losslessness is structural here, not promised in a comment: a demotion only
 * ever targets an EMPTY edge slot. If the edge is full, the proposal reports
 * `blocked` rather than overwriting a layer the human wrote. Nothing this
 * function can produce destroys text.
 */
export function proposeReorganisation(
  layers: BuilderLayerLike[],
  mode: ScoreMode = 'framework',
): Reorganisation {
  const none: Reorganisation = { fires: false, why: '', moves: [], preserved: [], blocked: false };
  if (!layers || layers.length < 9) return none;

  const score = (i: number) => getLayerScore(layers[i], mode);
  const pi = computePi(layers, mode);
  /* ⚠ THE TRIGGER IS Π > τ AND NOTHING ELSE, and getting here took being wrong first.
     The first version of this file also required high TENSION/CONTESTED — "pressure
     must MEET friction to restructure" — which sounds right and is incoherent with
     the formula it claims to serve: strain IS S, S is the denominator, so requiring
     high strain requires low Π, and the two conditions cancel. Nothing ever fired.

     Worse, I had written a test asserting that invented rule, so the gate would have
     enshrined it. The canon is one line and it is enough: "When Π exceeds threshold →
     reorganize." A COHERENT structure under strong evidence is exactly what cascades
     — chaotic ones absorb everything and move for nothing. */
  if (pi < TAU) return none;

  const preserved = INNER.filter(i => hasContent(layers[i]) && score(i) >= INVARIANT_BAR);

  const openEdge = EDGE.filter(i => !hasContent(layers[i]));
  const candidates = INNER
    .filter(i => hasContent(layers[i]) && score(i) <= WEAK_INNER)
    .sort((a, b) => score(a) - score(b)); // weakest first — it has the least claim to the core

  const moves: LayerMove[] = [];
  for (const from of candidates) {
    const to = openEdge.shift();
    if (to === undefined) break;
    moves.push({
      from,
      to,
      kind: 'demote',
      reason:
        `${ONION_LAYERS[from].name} scores ${score(from)} inside a core averaging ` +
        `${Math.round((score(0) + score(1)) / 2)}. It is being carried as load-bearing ` +
        `and it is not holding — ${ONION_LAYERS[to].name} is where it actually sits.`,
    });
  }

  const blocked = candidates.length > moves.length;
  if (!moves.length) {
    return blocked
      ? { fires: true, why: 'The core is under load, but the edge is full — nothing can move until you clear a slot.', moves: [], preserved, blocked: true }
      : none;
  }

  return {
    fires: true,
    why:
      `Π ${pi} is past τ ${TAU} — the structure can no longer contain its own evidence. ` +
      `${moves.length} layer${moves.length === 1 ? '' : 's'} should move outward` +
      (preserved.length ? `; ${preserved.length} invariant${preserved.length === 1 ? '' : 's'} held.` : '.'),
    moves,
    preserved,
    blocked,
  };
}

/**
 * Apply a proposal. Pure — returns a NEW array, never touches the input.
 *
 * Canon requires this be lossless: "old beliefs are demoted with preserved context,
 * not deleted." So content is MOVED, and the vacated layer is left empty rather than
 * back-filled with anything invented.
 */
export function applyReorganisation(
  layers: BuilderLayerLike[],
  plan: Reorganisation,
): BuilderLayerLike[] {
  if (!plan?.fires || !plan.moves.length) return layers;
  const next = layers.map(l => ({ ...l }));
  for (const m of plan.moves) {
    next[m.to] = { ...next[m.to], content: layers[m.from].content };
    next[m.from] = { ...next[m.from], content: '' };
  }
  return next;
}

/**
 * The inverse. Reversibility is not a nicety here — a restructure a person cannot
 * undo is a restructure they will never dare accept.
 */
export function revertReorganisation(
  layers: BuilderLayerLike[],
  plan: Reorganisation,
): BuilderLayerLike[] {
  if (!plan?.fires || !plan.moves.length) return layers;
  const next = layers.map(l => ({ ...l }));
  for (const m of plan.moves) {
    next[m.from] = { ...next[m.from], content: layers[m.to].content };
    next[m.to] = { ...next[m.to], content: '' };
  }
  return next;
}
