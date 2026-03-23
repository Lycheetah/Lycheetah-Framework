/**
 * launch.js — Lycheetah Library Local Launcher
 *
 * Opens the built Astro site in your default browser
 * by serving the dist/ directory.
 *
 * Usage: npm run launch
 * Or:    node launch.js
 */

import { createServer } from 'http';
import { readFileSync, existsSync } from 'fs';
import { join, extname, dirname } from 'path';
import { fileURLToPath } from 'url';
import { exec } from 'child_process';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

const DIST_DIR = join(__dirname, 'dist');
const PORT = 4000;

const MIME = {
  '.html': 'text/html; charset=utf-8',
  '.css': 'text/css',
  '.js': 'application/javascript',
  '.json': 'application/json',
  '.svg': 'image/svg+xml',
  '.png': 'image/png',
  '.jpg': 'image/jpeg',
  '.ico': 'image/x-icon',
  '.woff2': 'font/woff2',
  '.woff': 'font/woff',
};

if (!existsSync(DIST_DIR)) {
  console.error('\n  ✗ No dist/ directory found.');
  console.error('  Run "npm run build" first, then "npm run launch".\n');
  process.exit(1);
}

const server = createServer((req, res) => {
  let url = req.url || '/';

  // Strip query strings
  url = url.split('?')[0];

  // Default to index.html
  if (url.endsWith('/')) url += 'index.html';

  // Try exact path first, then .html extension, then /index.html
  const candidates = [
    join(DIST_DIR, url),
    join(DIST_DIR, url + '.html'),
    join(DIST_DIR, url, 'index.html'),
  ];

  let file = null;
  for (const candidate of candidates) {
    if (existsSync(candidate)) {
      file = candidate;
      break;
    }
  }

  if (!file) {
    // 404 fallback
    const notFound = join(DIST_DIR, '404.html');
    if (existsSync(notFound)) {
      res.writeHead(404, { 'Content-Type': 'text/html' });
      res.end(readFileSync(notFound));
    } else {
      res.writeHead(404);
      res.end('Not found');
    }
    return;
  }

  const ext = extname(file);
  const mime = MIME[ext] || 'application/octet-stream';
  res.writeHead(200, { 'Content-Type': mime });
  res.end(readFileSync(file));
});

server.listen(PORT, '127.0.0.1', () => {
  const url = `http://localhost:${PORT}`;
  console.log('\n  ◎ Lycheetah Library\n');
  console.log(`  Running at: ${url}`);
  console.log('  Press Ctrl+C to stop.\n');

  // Open browser
  const open = process.platform === 'win32'
    ? `start "" "${url}"`
    : process.platform === 'darwin'
    ? `open "${url}"`
    : `xdg-open "${url}"`;

  exec(open);
});
