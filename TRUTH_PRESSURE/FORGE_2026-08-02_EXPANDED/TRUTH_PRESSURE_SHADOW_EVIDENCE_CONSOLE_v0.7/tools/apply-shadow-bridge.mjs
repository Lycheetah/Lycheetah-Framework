#!/usr/bin/env node
import fs from 'node:fs';
import path from 'node:path';
import process from 'node:process';
import { fileURLToPath } from 'node:url';

const here = path.dirname(fileURLToPath(import.meta.url));
const bundleRoot = path.resolve(here, '..');
const repoRoot = process.argv[2] ? path.resolve(process.argv[2]) : null;

if (!repoRoot) {
  console.error('Usage: node tools/apply-shadow-bridge.mjs /path/to/lycheetah-mobile');
  process.exit(2);
}

const packagePath = path.join(repoRoot, 'package.json');
if (!fs.existsSync(packagePath)) {
  console.error(`No package.json found at ${repoRoot}`);
  process.exit(2);
}

const pkg = JSON.parse(fs.readFileSync(packagePath, 'utf8'));
if (pkg.name !== 'lycheetah-mobile') {
  console.error(`Expected package "lycheetah-mobile", found "${pkg.name ?? 'unknown'}".`);
  process.exit(2);
}

const copyGroups = [
  ['lib/truth-pressure-rc', 'lib/truth-pressure-rc'],
  ['lib/truth-pressure-integration', 'lib/truth-pressure-integration'],
  ['hooks/useTruthPressureShadow.ts', 'hooks/useTruthPressureShadow.ts'],
  ['hooks/useTruthPressureShadowReview.ts', 'hooks/useTruthPressureShadowReview.ts'],
  ['components/cascade/TruthPressureCandidateCard.tsx', 'components/cascade/TruthPressureCandidateCard.tsx'],
  ['components/cascade/TruthPressureShadowReviewPanel.tsx', 'components/cascade/TruthPressureShadowReviewPanel.tsx'],
];

for (const [sourceRelative, destinationRelative] of copyGroups) {
  const source = path.join(bundleRoot, sourceRelative);
  const destination = path.join(repoRoot, destinationRelative);

  if (fs.existsSync(destination)) {
    console.error(`Refusing to overwrite existing path: ${destination}`);
    process.exit(3);
  }

  fs.mkdirSync(path.dirname(destination), { recursive: true });
  fs.cpSync(source, destination, { recursive: true, errorOnExist: true });
  console.log(`Copied ${destinationRelative}`);
}

console.log('\nBridge files installed without modifying existing CASCADE source or screens.');
console.log('Next: patch the live scoreCASCADE call site using docs/CALL_SITE_PATCH_TEMPLATE.md.');
