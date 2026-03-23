/**
 * launch-server.cjs
 * CommonJS launcher for pkg compilation into standalone .exe
 * This bundles the dist/ folder and serves it locally.
 */

const http = require('http');
const fs = require('fs');
const path = require('path');
const { exec } = require('child_process');

const PORT = 4321;

// Resolve dist/ directory — try multiple strategies for pkg compatibility
function findDistDir() {
  const candidates = [
    // Next to the executable (pkg deployment)
    path.join(path.dirname(process.execPath), 'dist'),
    // Next to argv[0] (alternate pkg path)
    path.join(path.dirname(process.argv[0]), 'dist'),
    // Current working directory
    path.join(process.cwd(), 'dist'),
    // Same directory as this script (dev mode)
    path.join(__dirname, 'dist'),
  ];
  for (const c of candidates) {
    try {
      if (fs.existsSync(c) && fs.statSync(c).isDirectory()) return c;
    } catch { /* ignore */ }
  }
  return candidates[0]; // will fail gracefully below
}
const DIST_DIR = findDistDir();

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
  '.txt': 'text/plain',
};

if (!fs.existsSync(DIST_DIR)) {
  console.error('\n  [!] dist/ folder not found.');
  console.error('  Something went wrong with the package build.\n');
  process.exit(1);
}

const server = http.createServer((req, res) => {
  let url = (req.url || '/').split('?')[0];
  if (url.endsWith('/')) url += 'index.html';

  const candidates = [
    path.join(DIST_DIR, url),
    path.join(DIST_DIR, url + '.html'),
    path.join(DIST_DIR, url, 'index.html'),
  ];

  let file = null;
  for (const c of candidates) {
    if (fs.existsSync(c) && fs.statSync(c).isFile()) {
      file = c;
      break;
    }
  }

  if (!file) {
    res.writeHead(404, { 'Content-Type': 'text/plain' });
    res.end('Not found');
    return;
  }

  const ext = path.extname(file);
  const mime = MIME[ext] || 'application/octet-stream';
  res.writeHead(200, { 'Content-Type': mime });
  res.end(fs.readFileSync(file));
});

function openBrowser(url) {
  const cmd = process.platform === 'win32'
    ? 'start "" "' + url + '"'
    : process.platform === 'darwin'
    ? 'open "' + url + '"'
    : 'xdg-open "' + url + '"';
  exec(cmd);
}

server.on('error', function(err) {
  if (err.code === 'EADDRINUSE') {
    // Already running — just open the browser to the existing server
    const url = 'http://localhost:' + PORT;
    console.log('\n  ◎ Lycheetah Library is already running.');
    console.log('  Opening browser at: ' + url + '\n');
    openBrowser(url);
    // Give the browser a moment to open, then exit cleanly
    setTimeout(function() { process.exit(0); }, 2000);
  } else {
    console.error('\n  [!] Server error: ' + err.message + '\n');
    process.exit(1);
  }
});

server.listen(PORT, '127.0.0.1', function() {
  const url = 'http://localhost:' + PORT;
  console.log('\n  ◎ Lycheetah Framework Library\n');
  console.log('  Running at: ' + url);
  console.log('  Opening browser...');
  console.log('  Press Ctrl+C to stop.\n');
  openBrowser(url);
});
