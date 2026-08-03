import { useCallback, useEffect, useState } from 'react';
import { truthPressureShadowRecorder } from '../lib/truth-pressure-integration/shadow-store-async.ts';
import {
  buildShadowEvidenceReport,
  type ShadowEvidenceReport,
} from '../lib/truth-pressure-integration/shadow-analysis.ts';
import type { TruthPressureShadowDataset } from '../lib/truth-pressure-integration/shadow-store-core.ts';
import {
  serializeShadowEvidenceExport,
  serializeShadowEvidenceMarkdown,
} from '../lib/truth-pressure-integration/shadow-export.ts';

export type TruthPressureShadowReviewState = {
  dataset: TruthPressureShadowDataset | null;
  report: ShadowEvidenceReport | null;
  loading: boolean;
  error: string | null;
  refresh(): Promise<void>;
  clear(): Promise<void>;
  exportJson(): string | null;
  exportMarkdown(): string | null;
};

export function useTruthPressureShadowReview(): TruthPressureShadowReviewState {
  const [dataset, setDataset] = useState<TruthPressureShadowDataset | null>(null);
  const [report, setReport] = useState<ShadowEvidenceReport | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const refresh = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const next = await truthPressureShadowRecorder.load();
      setDataset(next);
      setReport(buildShadowEvidenceReport(next));
    } catch (cause) {
      setError(cause instanceof Error ? cause.message : 'Unable to load shadow evidence.');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    void refresh();
  }, [refresh]);

  const clear = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      await truthPressureShadowRecorder.clear();
      await refresh();
    } catch (cause) {
      setError(cause instanceof Error ? cause.message : 'Unable to clear shadow evidence.');
      setLoading(false);
    }
  }, [refresh]);

  return {
    dataset,
    report,
    loading,
    error,
    refresh,
    clear,
    exportJson: () => dataset ? serializeShadowEvidenceExport(dataset) : null,
    exportMarkdown: () => dataset ? serializeShadowEvidenceMarkdown(dataset) : null,
  };
}
