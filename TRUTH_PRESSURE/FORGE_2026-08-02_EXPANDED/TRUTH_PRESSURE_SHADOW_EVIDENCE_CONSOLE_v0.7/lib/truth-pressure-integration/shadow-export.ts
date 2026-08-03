import type { TruthPressureShadowDataset } from './shadow-store-core.ts';
import {
  buildShadowEvidenceReport,
  renderShadowEvidenceMarkdown,
} from './shadow-analysis.ts';

export type ShadowEvidenceExport = {
  version: 'TP-SHADOW-EXPORT-0.7';
  privacy: 'NO_RAW_CONTENT';
  createdAt: string;
  dataset: TruthPressureShadowDataset;
  report: ReturnType<typeof buildShadowEvidenceReport>;
};

export function buildShadowEvidenceExport(
  dataset: TruthPressureShadowDataset,
  now = new Date().toISOString(),
): ShadowEvidenceExport {
  return {
    version: 'TP-SHADOW-EXPORT-0.7',
    privacy: 'NO_RAW_CONTENT',
    createdAt: now,
    dataset,
    report: buildShadowEvidenceReport(dataset, now),
  };
}

export function serializeShadowEvidenceExport(
  dataset: TruthPressureShadowDataset,
  now = new Date().toISOString(),
): string {
  return JSON.stringify(buildShadowEvidenceExport(dataset, now), null, 2);
}

export function serializeShadowEvidenceMarkdown(
  dataset: TruthPressureShadowDataset,
  now = new Date().toISOString(),
): string {
  return renderShadowEvidenceMarkdown(buildShadowEvidenceReport(dataset, now));
}
