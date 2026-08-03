/**
 * Example drop-in shadow harness for Sovereign Sol.
 * Adjust import paths to the app's folder layout.
 *
 * Shadow mode keeps the historical result visible while computing the candidate
 * result beside it. It stores no raw content in the comparison record.
 */
import { scoreCASCADE } from '../lib/cascade-score.ts';
import {
  buildAppViewModel,
  createShadowComparison,
  type AppTruthPressureViewModel,
  type ShadowComparisonRecord,
} from '../lib/truth-pressure-rc/index.ts';

export type TruthPressureShadowOutput = {
  legacy: ReturnType<typeof scoreCASCADE>;
  candidate: AppTruthPressureViewModel;
  comparison: ShadowComparisonRecord;
};

export function runTruthPressureShadow(text: string): TruthPressureShadowOutput {
  const legacy = scoreCASCADE(text);
  const candidate = buildAppViewModel({ kind: 'text', text });
  const comparison = createShadowComparison(
    candidate,
    {
      truthPressure: legacy.truthPressure,
      coherence: legacy.coherence,
      reorganisationNeeded: legacy.reorganisationNeeded,
      dominantLayer: legacy.dominantLayer,
    },
    { inputLength: text.length },
  );
  return { legacy, candidate, comparison };
}
