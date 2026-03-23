/**
 * sync-content.js
 * Copies Lycheetah Framework markdown files from the parent repo
 * into src/content/docs/ for Astro content collections.
 *
 * Run: node scripts/sync-content.js
 * Or automatically via: npm run sync
 */

import { copyFileSync, mkdirSync, readdirSync, statSync, existsSync, rmSync } from 'fs';
import { join, dirname, relative, extname } from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

const APP_ROOT = join(__dirname, '..');
const REPO_ROOT = join(APP_ROOT, '..');
const CONTENT_DIR = join(APP_ROOT, 'src', 'content', 'docs');

// Framework directories to sync (relative to REPO_ROOT)
const SYNC_SOURCES = [
  '01_CASCADE',
  '02_AURA',
  '03_LAMAGUE',
  '04_TRIAD',
  '05_MICROORCIM',
  '06_EARNED_LIGHT',
  '07_ANAMNESIS',
  '08_CHRYSOPOEIA',
  '09_HARMONIA',
  '10_HARMONIA',
  '11_MATHEMATICAL_FOUNDATIONS',
  '13_SYNTHESIS_REPORTS',
  '14_MYSTERY_SCHOOL',
  '15_PERSONAL_VAULT',
  '16_SOL_VEYRA_ARCHITECTURE',
  '17_LEARNING_EMERGENCE',
  '18_EXPERIMENTAL',
  '21_MEMORIA',
  '22_INTERFACE_INTELLIGENCE',
  '23_NZ_AI_GOVERNANCE',
  '24_LAMAGUE_CROSS_CULTURAL',
  '25_SOL_PROTOCOL_ARCHITECTURE',
];

// Root-level markdown files to sync
const ROOT_FILES = [
  'README.md',
  'FAILURE_MUSEUM.md',
  'FOR_FUTURE_AI_SYSTEMS.md',
  '00_Sovereign_Index.md',
];

let copied = 0;
let skipped = 0;

function ensureDir(dir) {
  if (!existsSync(dir)) {
    mkdirSync(dir, { recursive: true });
  }
}

function copyMarkdown(src, dest) {
  try {
    ensureDir(dirname(dest));
    copyFileSync(src, dest);
    copied++;
  } catch (e) {
    console.warn(`  ⚠ Could not copy ${src}: ${e.message}`);
    skipped++;
  }
}

function syncDirectory(srcDir, destDir) {
  if (!existsSync(srcDir)) {
    skipped++;
    return;
  }

  let entries;
  try {
    entries = readdirSync(srcDir);
  } catch {
    return;
  }

  for (const entry of entries) {
    const srcPath = join(srcDir, entry);
    const destPath = join(destDir, entry);

    const stat = statSync(srcPath);
    if (stat.isDirectory()) {
      // Recurse, but skip hidden dirs and node_modules
      if (!entry.startsWith('.') && entry !== 'node_modules') {
        syncDirectory(srcPath, destPath);
      }
    } else if (extname(entry) === '.md') {
      copyMarkdown(srcPath, destPath);
    }
  }
}

// Clean and rebuild content directory
console.log('◎ Lycheetah Content Sync\n');
console.log(`  Source: ${REPO_ROOT}`);
console.log(`  Destination: ${CONTENT_DIR}\n`);

if (existsSync(CONTENT_DIR)) {
  rmSync(CONTENT_DIR, { recursive: true, force: true });
}
ensureDir(CONTENT_DIR);

// Sync root files
console.log('  Syncing root files...');
for (const file of ROOT_FILES) {
  const src = join(REPO_ROOT, file);
  const dest = join(CONTENT_DIR, file);
  if (existsSync(src)) {
    copyMarkdown(src, dest);
    console.log(`  ✓ ${file}`);
  }
}

// Sync framework directories
console.log('\n  Syncing framework directories...');
for (const dir of SYNC_SOURCES) {
  const src = join(REPO_ROOT, dir);
  const dest = join(CONTENT_DIR, dir);
  if (existsSync(src)) {
    syncDirectory(src, dest);
    console.log(`  ✓ ${dir}/`);
  } else {
    console.log(`  - ${dir}/ (not found, skipping)`);
  }
}

console.log(`\n  Done. Copied: ${copied} files. Skipped: ${skipped}.\n`);
