import { useCallback, useState } from 'react';
import {
  runAndRecordTruthPressureBridge,
  runTruthPressureBridge,
  type TruthPressureBridgeResult,
} from '../lib/truth-pressure-integration/shadow-service.ts';
import { truthPressureShadowRecorder } from '../lib/truth-pressure-integration/shadow-store-async.ts';
import type { TruthPressureBridgeMode } from '../lib/truth-pressure-integration/feature.ts';

export type UseTruthPressureShadowState = {
  result: TruthPressureBridgeResult | null;
  running: boolean;
  error: string | null;
  analyze(text: string, options?: { persist?: boolean; mode?: TruthPressureBridgeMode }): Promise<TruthPressureBridgeResult | null>;
  reset(): void;
};

/**
 * Explicit-submit hook. It deliberately does not analyze or persist on every
 * keystroke.
 */
export function useTruthPressureShadow(): UseTruthPressureShadowState {
  const [result, setResult] = useState<TruthPressureBridgeResult | null>(null);
  const [running, setRunning] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const analyze = useCallback(async (
    text: string,
    options: { persist?: boolean; mode?: TruthPressureBridgeMode } = {},
  ): Promise<TruthPressureBridgeResult | null> => {
    const normalized = text.trim();
    if (!normalized) {
      setError('Enter text before running Truth Pressure.');
      return null;
    }

    setRunning(true);
    setError(null);
    try {
      const next = options.persist === false
        ? runTruthPressureBridge(normalized, options.mode)
        : await runAndRecordTruthPressureBridge(
            normalized,
            truthPressureShadowRecorder,
            options.mode,
          );
      setResult(next);
      return next;
    } catch (cause) {
      const message = cause instanceof Error ? cause.message : 'Truth Pressure analysis failed.';
      setError(message);
      return null;
    } finally {
      setRunning(false);
    }
  }, []);

  const reset = useCallback(() => {
    setResult(null);
    setError(null);
    setRunning(false);
  }, []);

  return { result, running, error, analyze, reset };
}
