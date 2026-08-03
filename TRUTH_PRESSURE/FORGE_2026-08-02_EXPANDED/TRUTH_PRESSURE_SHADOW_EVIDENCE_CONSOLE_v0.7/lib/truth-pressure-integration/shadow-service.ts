import { scoreCASCADE } from '../cascade-score.ts';
import {
  buildAppViewModel,
  createShadowComparison,
  type AppTruthPressureViewModel,
  type ShadowComparisonRecord,
} from '../truth-pressure-rc/index.ts';
import { TRUTH_PRESSURE_BRIDGE_MODE, type TruthPressureBridgeMode } from './feature.ts';
import type { TruthPressureShadowDataset } from './shadow-store-core.ts';

export type LegacyCascadeResult = ReturnType<typeof scoreCASCADE>;

export type TruthPressureBridgeResult = {
  mode: TruthPressureBridgeMode;
  legacy: LegacyCascadeResult;
  candidate: AppTruthPressureViewModel | null;
  comparison: ShadowComparisonRecord | null;
  visible: 'LEGACY' | 'CANDIDATE_PREVIEW';
};

export type ShadowRecordWriter = {
  record(record: ShadowComparisonRecord): Promise<TruthPressureShadowDataset>;
};

export function runTruthPressureBridge(
  text: string,
  mode: TruthPressureBridgeMode = TRUTH_PRESSURE_BRIDGE_MODE,
): TruthPressureBridgeResult {
  const legacy = scoreCASCADE(text);

  if (mode === 'off') {
    return {
      mode,
      legacy,
      candidate: null,
      comparison: null,
      visible: 'LEGACY',
    };
  }

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

  return {
    mode,
    legacy,
    candidate,
    comparison,
    visible: mode === 'candidate-preview' ? 'CANDIDATE_PREVIEW' : 'LEGACY',
  };
}

export async function runAndRecordTruthPressureBridge(
  text: string,
  writer: ShadowRecordWriter,
  mode: TruthPressureBridgeMode = TRUTH_PRESSURE_BRIDGE_MODE,
): Promise<TruthPressureBridgeResult> {
  const result = runTruthPressureBridge(text, mode);
  if (result.comparison) {
    await writer.record(result.comparison);
  }
  return result;
}
