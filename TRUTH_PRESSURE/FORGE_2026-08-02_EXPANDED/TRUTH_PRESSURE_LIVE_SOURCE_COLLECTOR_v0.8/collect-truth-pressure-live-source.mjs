#!/usr/bin/env node

/**
 * Truth Pressure Live Source Collector v0.8
 *
 * Run from the Lycheetah repository root:
 *
 *   node collect-truth-pressure-live-source.mjs
 *
 * Or supply the repository path:
 *
 *   node collect-truth-pressure-live-source.mjs /path/to/lycheetah-mobile
 *
 * The script copies only source/configuration files needed for the verified
 * Truth Pressure app patch. It never collects .env files, credentials, local
 * databases, app user data, build outputs, node_modules, or Git internals.
 */

import crypto from 'node:crypto';
import fs from 'node:fs';
import path from 'node:path';
import process from 'node:process';
import { execFileSync } from 'node:child_process';

const VERSION = 'TP-LIVE-SOURCE-COLLECTOR-0.8';
const repoRoot = path.resolve(process.argv[2] ?? process.cwd());
const outputRoot = path.join(repoRoot, '_truth-pressure-live-source-extract');

const SOURCE_EXTENSIONS = new Set([
  '.ts', '.tsx', '.js', '.jsx', '.mjs', '.cjs', '.json', '.md',
]);

const ALWAYS_INCLUDE_BASENAMES = new Set([
  'package.json',
  'package-lock.json',
  'pnpm-lock.yaml',
  'yarn.lock',
  'tsconfig.json',
  'app.json',
  'app.config.ts',
  'app.config.js',
  'metro.config.js',
  'metro.config.cjs',
  'babel.config.js',
  'babel.config.cjs',
  'expo-env.d.ts',
]);

const EXCLUDED_DIRS = new Set([
  '.git',
  '.expo',
  '.next',
  '.turbo',
  '.vscode',
  '.idea',
  'node_modules',
  'dist',
  'build',
  'coverage',
  'android',
  'ios',
  'web-build',
  outputRoot.split(path.sep).at(-1),
]);

const EXCLUDED_BASENAME_PATTERNS = [
  /^\.env(?:\.|$)/i,
  /\.pem$/i,
  /\.key$/i,
  /\.p12$/i,
  /\.pfx$/i,
  /\.jks$/i,
  /^google-services\.json$/i,
  /^GoogleService-Info\.plist$/i,
  /secret/i,
  /credential/i,
  /private[-_]?key/i,
  /\.sqlite(?:3)?$/i,
  /\.db$/i,
  /\.log$/i,
];

const SEARCH_RULES = [
  {
    id: 'LIVE-SCORE-CALL',
    description: 'Calls or imports the historical text scorer.',
    patterns: [
      /\bscoreCASCADE\s*\(/,
      /\bscoreCASCADE\b/,
      /from\s+['"][^'"]*cascade-score(?:\.ts)?['"]/,
    ],
  },
  {
    id: 'TRUTH-PRESSURE-DISPLAY',
    description: 'Displays or branches on Truth Pressure output.',
    patterns: [
      /\btruthPressure\b/,
      /\breorganisationNeeded\b/,
      /\bstructuralContradiction\b/,
      /\bdominantLayer\b/,
      /Truth\s*Pressure/i,
      /REORGANISE/i,
    ],
  },
  {
    id: 'ONION-UI',
    description: 'Renders or imports the onion profile/engine.',
    patterns: [
      /\bOnionProfile\b/,
      /cascade-onion(?:\.ts)?/,
      /\bcomputePi\s*\(/,
      /\bcomputeBlockScore\s*\(/,
      /\bONION_LAYERS\b/,
    ],
  },
  {
    id: 'REORGANISATION-UI',
    description: 'Calls or renders CASCADE reorganisation.',
    patterns: [
      /cascade-reorganise(?:\.ts)?/,
      /\bproposeReorganisation\s*\(/,
      /\bapplyReorganisation\s*\(/,
      /\brevertReorganisation\s*\(/,
      /\bdetectCascadeEvent\s*\(/,
    ],
  },
  {
    id: 'JUDGE-CALL',
    description: 'Calls the CASCADE judge or quick builder.',
    patterns: [
      /cascade-judge(?:\.ts)?/,
      /\bauditCascadeBlock\s*\(/,
      /\bquickBuildBlock\s*\(/,
      /\bapplyVerdict\s*\(/,
    ],
  },
  {
    id: 'PERSISTENCE',
    description: 'Likely local persistence path needed by the shadow bridge.',
    patterns: [
      /\bAsyncStorage\b/,
      /@react-native-async-storage\/async-storage/,
      /\bgetItem\s*\(/,
      /\bsetItem\s*\(/,
    ],
  },
];

const LIKELY_PATH_PATTERNS = [
  /(?:^|\/)components\/cascade\//i,
  /(?:^|\/)(?:app|screens)\/.*cascade/i,
  /(?:^|\/)(?:app|screens)\/.*library/i,
  /(?:^|\/)lib\/.*storage/i,
  /(?:^|\/)lib\/cascade-/i,
  /OnionProfile\.(?:ts|tsx|js|jsx)$/i,
];

function fail(message, code = 1) {
  console.error(`\nCollector stopped: ${message}\n`);
  process.exit(code);
}

function normalizeRelative(filePath) {
  return path.relative(repoRoot, filePath).split(path.sep).join('/');
}

function isExcludedBasename(name) {
  return EXCLUDED_BASENAME_PATTERNS.some(pattern => pattern.test(name));
}

function isInsideRepo(candidate) {
  const relative = path.relative(repoRoot, candidate);
  return relative && !relative.startsWith('..') && !path.isAbsolute(relative);
}

function walk(directory, files = []) {
  for (const entry of fs.readdirSync(directory, { withFileTypes: true })) {
    if (entry.isSymbolicLink()) continue;
    if (entry.isDirectory() && EXCLUDED_DIRS.has(entry.name)) continue;
    if (isExcludedBasename(entry.name)) continue;

    const absolute = path.join(directory, entry.name);
    if (entry.isDirectory()) {
      walk(absolute, files);
      continue;
    }

    if (!entry.isFile()) continue;
    if (ALWAYS_INCLUDE_BASENAMES.has(entry.name)) {
      files.push(absolute);
      continue;
    }

    if (!SOURCE_EXTENSIONS.has(path.extname(entry.name))) continue;
    files.push(absolute);
  }
  return files;
}

function readText(filePath) {
  const stat = fs.statSync(filePath);
  if (stat.size > 2_000_000) return null;
  try {
    return fs.readFileSync(filePath, 'utf8');
  } catch {
    return null;
  }
}

function hashFile(filePath) {
  return crypto.createHash('sha256').update(fs.readFileSync(filePath)).digest('hex');
}

function runGit(args) {
  try {
    return execFileSync('git', ['-C', repoRoot, ...args], {
      encoding: 'utf8',
      stdio: ['ignore', 'pipe', 'pipe'],
    }).trim();
  } catch {
    return null;
  }
}

if (!fs.existsSync(path.join(repoRoot, 'package.json'))) {
  fail(`No package.json found at ${repoRoot}`, 2);
}

const packageJson = JSON.parse(fs.readFileSync(path.join(repoRoot, 'package.json'), 'utf8'));
if (packageJson.name !== 'lycheetah-mobile') {
  console.warn(
    `Warning: expected package "lycheetah-mobile", found "${packageJson.name ?? 'unknown'}".`,
  );
}

if (fs.existsSync(outputRoot)) {
  fs.rmSync(outputRoot, { recursive: true, force: true });
}
fs.mkdirSync(outputRoot, { recursive: true });

const candidates = walk(repoRoot);
const selected = new Map();

for (const absolute of candidates) {
  if (!isInsideRepo(absolute)) continue;
  const relative = normalizeRelative(absolute);
  const basename = path.basename(absolute);

  if (ALWAYS_INCLUDE_BASENAMES.has(basename)) {
    selected.set(relative, {
      absolute,
      reasons: ['PROJECT-CONFIG'],
      matches: [],
    });
    continue;
  }

  const text = readText(absolute);
  const reasons = [];
  const matches = [];

  if (LIKELY_PATH_PATTERNS.some(pattern => pattern.test(relative))) {
    reasons.push('LIKELY-PATH');
  }

  if (text !== null) {
    for (const rule of SEARCH_RULES) {
      const hitPatterns = rule.patterns
        .filter(pattern => pattern.test(text))
        .map(pattern => String(pattern));
      if (hitPatterns.length) {
        reasons.push(rule.id);
        matches.push({
          rule: rule.id,
          description: rule.description,
          patterns: hitPatterns,
        });
      }
    }
  }

  if (reasons.length) {
    selected.set(relative, {
      absolute,
      reasons: [...new Set(reasons)],
      matches,
    });
  }
}

if (!selected.size) {
  fail('No relevant source files were found.', 3);
}

const files = [];
for (const [relative, metadata] of [...selected.entries()].sort(([a], [b]) => a.localeCompare(b))) {
  const destination = path.join(outputRoot, 'SOURCE', ...relative.split('/'));
  fs.mkdirSync(path.dirname(destination), { recursive: true });
  fs.copyFileSync(metadata.absolute, destination);

  files.push({
    path: relative,
    bytes: fs.statSync(metadata.absolute).size,
    sha256: hashFile(metadata.absolute),
    reasons: metadata.reasons,
    matches: metadata.matches,
  });
}

const commit = runGit(['rev-parse', 'HEAD']);
const branch = runGit(['branch', '--show-current']);
const status = runGit(['status', '--porcelain=v1']);
const trackedDiff = runGit(['diff', '--stat']);
const stagedDiff = runGit(['diff', '--cached', '--stat']);

let nodeVersion = process.version;
let npmVersion = null;
try {
  npmVersion = execFileSync('npm', ['--version'], { encoding: 'utf8' }).trim();
} catch {}

const receipt = {
  collectorVersion: VERSION,
  collectedAt: new Date().toISOString(),
  repositoryRootBasename: path.basename(repoRoot),
  packageName: packageJson.name ?? null,
  packageVersion: packageJson.version ?? null,
  git: {
    commit,
    branch,
    workingTreeDirty: Boolean(status),
    statusPorcelain: status || '',
    trackedDiffStat: trackedDiff || '',
    stagedDiffStat: stagedDiff || '',
  },
  environment: {
    node: nodeVersion,
    npm: npmVersion,
    platform: process.platform,
    architecture: process.arch,
  },
  privacy: {
    sourceOnly: true,
    excludedEnvironmentFiles: true,
    excludedCredentialsAndKeys: true,
    excludedDatabasesAndLogs: true,
    excludedDependenciesAndBuildOutputs: true,
  },
  fileCount: files.length,
};

fs.writeFileSync(
  path.join(outputRoot, 'SOURCE_RECEIPT.json'),
  JSON.stringify(receipt, null, 2),
);

fs.writeFileSync(
  path.join(outputRoot, 'SOURCE_MANIFEST.json'),
  JSON.stringify({
    collectorVersion: VERSION,
    files,
  }, null, 2),
);

fs.writeFileSync(
  path.join(outputRoot, 'SOURCE_HASHES.sha256'),
  files.map(file => `${file.sha256}  ${file.path}`).join('\n') + '\n',
);

const humanSummary = `# Truth Pressure Live Source Extract

Collector: ${VERSION}

## Result

- Files collected: ${files.length}
- Package: ${packageJson.name ?? 'unknown'} ${packageJson.version ?? ''}
- Git commit: ${commit ?? 'unavailable'}
- Branch: ${branch ?? 'unavailable'}
- Working tree dirty: ${Boolean(status) ? 'YES' : 'NO'}

## What was collected

Source and configuration files matching:

- scoreCASCADE calls/imports;
- Truth Pressure UI fields;
- OnionProfile and onion engine usage;
- reorganisation calls;
- CASCADE judge calls;
- AsyncStorage or persistence wrappers;
- likely CASCADE, Library, Onion, and storage paths.

## What was intentionally excluded

- .env files;
- API keys and credential files;
- private keys and signing material;
- databases and logs;
- node_modules;
- build outputs;
- Git internals;
- local app user data.

## Next step

Compress the entire \`_truth-pressure-live-source-extract\` directory and upload it to the Truth Pressure research conversation.
`;

fs.writeFileSync(path.join(outputRoot, 'README.md'), humanSummary);

console.log(`\n${VERSION}`);
console.log(`Repository: ${repoRoot}`);
console.log(`Collected: ${files.length} files`);
console.log(`Output: ${outputRoot}`);
console.log('\nMatched source files:');
for (const file of files) {
  console.log(`  ${file.path}  [${file.reasons.join(', ')}]`);
}
console.log('\nNo .env, keys, databases, logs, dependencies, builds, or user data were collected.');
console.log('\nCompress the output directory and upload it here.\n');
