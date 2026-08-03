export type TruthPressureBridgeMode = 'off' | 'shadow' | 'candidate-preview';

/**
 * Initial release posture.
 *
 * off:
 *   Historical CASCADE text lens only.
 *
 * shadow:
 *   Historical result remains visible. Candidate runs privately and records a
 *   privacy-safe comparison with no raw text.
 *
 * candidate-preview:
 *   Candidate view may be rendered behind an explicit developer/research label.
 *   It remains descriptive and cannot reorganise knowledge from text mode.
 */
export const TRUTH_PRESSURE_BRIDGE_MODE: TruthPressureBridgeMode = 'shadow';

export const TRUTH_PRESSURE_SHADOW_STORAGE_KEY = 'truth-pressure-shadow-v0.6';
export const TRUTH_PRESSURE_SHADOW_DATASET_VERSION = 'TP-SHADOW-DATASET-0.6' as const;
export const TRUTH_PRESSURE_DEFAULT_MAX_RECORDS = 250;
