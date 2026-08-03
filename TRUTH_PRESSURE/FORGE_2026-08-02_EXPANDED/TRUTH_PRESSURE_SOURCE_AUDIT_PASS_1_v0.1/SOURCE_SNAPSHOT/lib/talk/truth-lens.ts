export type TruthLensCategory =
  | 'checkableClaims'
  | 'interpretations'
  | 'uncertainties'
  | 'suggestedActions';

export type TruthLensResult = Record<TruthLensCategory, string[]> & {
  verificationMoves: string[];
};

const CHECKABLE = /\b(study|studies|research|data|evidence|measured|published|trial|survey|report|according to|percent|percentage|statistic|source|found that|shows that)\b|https?:\/\/|\b\d+(?:\.\d+)?%?\b/i;
const INTERPRETIVE = /\b(suggests?|implies?|means?|indicates?|appears?|seems?|likely|because|therefore|perhaps|pattern|tension|underneath|root)\b/i;
const UNCERTAIN = /\b(may|might|could|possibly|perhaps|uncertain|unclear|unknown|not sure|cannot know|can't know|inconclusive|contested|speculat)\b/i;
const ACTION = /\b(should|try|consider|recommend|next step|you can|you could|start by|need to|choose|test|verify|ask|write|make|build|stop|begin)\b/i;

function splitSentences(text: string): string[] {
  return text
    .replace(/\[[A-Z]+:[^\]]+\]/g, '')
    .split(/(?<=[.!?])\s+|\n{2,}/)
    .map(sentence => sentence.replace(/\s+/g, ' ').trim())
    .filter(sentence => sentence.length >= 12)
    .slice(0, 48);
}

function collect(sentences: string[], pattern: RegExp): string[] {
  return sentences.filter(sentence => pattern.test(sentence)).slice(0, 4);
}

export function buildTruthLens(text: string): TruthLensResult {
  const sentences = splitSentences(text);
  const checkableClaims = collect(sentences, CHECKABLE);
  const interpretations = collect(sentences, INTERPRETIVE);
  const uncertainties = collect(sentences, UNCERTAIN);
  const suggestedActions = collect(sentences, ACTION);
  const verificationMoves: string[] = [];

  if (checkableClaims.length > 0) {
    verificationMoves.push('Open the named source, confirm the date and method, and compare the claim with what the source actually says.');
  } else {
    verificationMoves.push('Ask which sentence is intended as a factual claim and what evidence would change it.');
  }
  if (/\b(correlat|associated|linked)\b/i.test(text)) {
    verificationMoves.push('Check whether the response turns correlation into causation.');
  }
  if (interpretations.length > 0) {
    verificationMoves.push('Name a plausible rival interpretation and identify what observation would distinguish the two.');
  }
  if (suggestedActions.length > 0) {
    verificationMoves.push('Prefer the smallest reversible test before treating the recommendation as a commitment.');
  }
  if (uncertainties.length === 0) {
    verificationMoves.push('Ask what remains unknown or outside the model’s view.');
  }

  return {
    checkableClaims,
    interpretations,
    uncertainties,
    suggestedActions,
    verificationMoves: verificationMoves.slice(0, 4),
  };
}
