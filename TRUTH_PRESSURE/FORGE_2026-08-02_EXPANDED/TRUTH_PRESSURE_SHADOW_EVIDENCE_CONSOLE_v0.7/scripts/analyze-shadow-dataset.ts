import fs from 'node:fs';
import path from 'node:path';
import process from 'node:process';

import { parseShadowDataset } from '../lib/truth-pressure-integration/shadow-store-core.ts';
import {
  buildShadowEvidenceReport,
  renderShadowEvidenceMarkdown,
} from '../lib/truth-pressure-integration/shadow-analysis.ts';

const input = process.argv[2];
const output = process.argv[3];

if (!input) {
  console.error('Usage: node --experimental-strip-types scripts/analyze-shadow-dataset.ts dataset.json [report.md]');
  process.exit(2);
}

const raw = fs.readFileSync(path.resolve(input), 'utf8');
const dataset = parseShadowDataset(raw);
const report = buildShadowEvidenceReport(dataset);
const markdown = renderShadowEvidenceMarkdown(report);

if (output) {
  fs.writeFileSync(path.resolve(output), markdown);
  console.log(`Wrote ${path.resolve(output)}`);
} else {
  process.stdout.write(markdown);
}
