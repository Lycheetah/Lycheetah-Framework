export type TruthPressureRcMode = 'off' | 'shadow' | 'candidate-preview';

/**
 * Recommended initial state: shadow.
 * - off: historical engine only
 * - shadow: historical UI, candidate computed privately for comparison
 * - candidate-preview: candidate visible behind a developer/research label
 */
export const TRUTH_PRESSURE_RC_MODE: TruthPressureRcMode = 'shadow';
