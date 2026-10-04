/* One bounded local witness. No provider calls or external browser requests. */
const assert = require('node:assert/strict');
const fs = require('node:fs/promises');
const path = require('node:path');
const {pathToFileURL} = require('node:url');
const {chromium} = require(process.argv[2] || 'playwright');

const research = __dirname;
const root = path.resolve(research, '../..');
const site = path.join(root, 'docs');
const out = path.join(research, 'witness');
const report = {
  status: 'RUNNING',
  scope: 'Independent No local draft, paper rendering, and homepage research entrance',
  checkedAt: new Date().toISOString(),
  checks: [],
  externalRequests: [],
  browserErrors: []
};
let browser;

function passed(name) { report.checks.push({name, status: 'PASS'}); }

async function noOverflow(page, label) {
  const widths = await page.evaluate(() => ({
    content: document.documentElement.scrollWidth,
    viewport: window.innerWidth
  }));
  assert.ok(widths.content <= widths.viewport + 1, label + ' horizontal overflow: ' + JSON.stringify(widths));
  passed(label + ' fits viewport');
}

async function checkLocalLinks(filename) {
  const source = await fs.readFile(filename, 'utf8');
  const links = [...source.matchAll(/href="([^"]+)"/g)].map(m => m[1]);
  for (const href of links) {
    if (/^(https?:|mailto:)/.test(href)) continue;
    const [relative, fragment] = href.split('#');
    const target = relative ? path.resolve(path.dirname(filename), decodeURIComponent(relative)) : filename;
    await fs.access(target);
    if (fragment && target.endsWith('.html')) {
      const html = target === filename ? source : await fs.readFile(target, 'utf8');
      assert.ok(html.includes('id="' + fragment + '"'), 'Missing anchor ' + href + ' in ' + filename);
    }
  }
}

async function main() {
  await fs.mkdir(out, {recursive: true});
  const manuscript = await fs.readFile(path.join(research, 'PAPER.md'), 'utf8');
  const publishedCopy = await fs.readFile(path.join(site, 'research/independent-no-paper.md'), 'utf8');
  assert.equal(manuscript, publishedCopy);
  const sources = JSON.parse(await fs.readFile(path.join(research, 'SOURCES.json'), 'utf8'));
  const generatedSources = JSON.parse(await fs.readFile(path.join(site, 'research/independent-no-sources.json'), 'utf8'));
  assert.deepEqual(sources, generatedSources);
  assert.equal(sources.sources.length, 9);
  assert.ok(sources.sources.every(s => /^https:/.test(s.url) && s.inspected && s.does_not_support));
  passed('Generated source copies match canonical manuscript and nine-entry ledger');

  browser = await chromium.launch({
    executablePath: process.env.INO_BROWSER_EXECUTABLE || '/usr/bin/google-chrome',
    headless: true,
    args: ['--no-sandbox', '--disable-dev-shm-usage']
  });
  report.browser = browser.version();
  const context = await browser.newContext({viewport: {width: 1440, height: 1000}, reducedMotion: 'reduce'});
  await context.route(/^https?:\/\//, async route => {
    report.externalRequests.push(route.request().url());
    await route.abort();
  });
  const page = await context.newPage();
  page.on('pageerror', error => report.browserErrors.push(String(error)));
  const url = name => pathToFileURL(path.join(site, name)).href;

  await page.goto(url('research/independent-no-paper.html'));
  assert.equal(await page.locator('h1').textContent(), 'The Independent No');
  assert.ok((await page.locator('main').textContent()).includes('Proposition 3'));
  await noOverflow(page, 'Manuscript desktop');
  await page.pdf({
    path: path.join(site, 'research/independent-no.pdf'),
    format: 'A4',
    preferCSSPageSize: true,
    printBackground: true,
    displayHeaderFooter: true,
    headerTemplate: '<div></div>',
    footerTemplate: '<div style="font-family:Arial,sans-serif;font-size:8px;width:100%;text-align:center;color:#666">The Independent No · Working paper v0.1 · <span class="pageNumber"></span> / <span class="totalPages"></span></div>'
  });
  const pdf = await fs.readFile(path.join(site, 'research/independent-no.pdf'));
  assert.equal(pdf.subarray(0, 5).toString(), '%PDF-');
  report.pdfBytes = pdf.length;
  passed('Manuscript renders and PDF bytes read back');

  await page.goto(url('independent-no.html'));
  assert.ok(await page.locator('[data-explorer]').isVisible());
  assert.equal(await page.locator('#release-outcome').textContent(), 'Rejection remains binding.');
  assert.equal(await page.locator('#receipt-outcome').textContent(), 'Retained');
  assert.equal(await page.locator('#survival-outcome').textContent(), 'Survives in this model');
  passed('Default protected boundaries preserve rejection and history');
  await noOverflow(page, 'Research overview desktop');
  await page.screenshot({path: path.join(out, 'website-desktop.png')});

  for (const surface of ['rules', 'evidence', 'scope', 'release']) {
    await page.locator('#reset-explorer').click();
    await page.locator('[data-surface="' + surface + '"]').check();
    assert.equal(await page.locator('#release-outcome').textContent(), 'False support has a route.');
    assert.equal(await page.locator('#receipt-outcome').textContent(), 'Retained');
    assert.equal(await page.locator('#survival-outcome').textContent(), 'Does not survive');
    passed('Worked ' + surface + ' counterexample permits bypass while retaining receipt');
  }

  await page.locator('#reset-explorer').click();
  await page.locator('[data-surface="receipt"]').check();
  assert.equal(await page.locator('#release-outcome').textContent(), 'Rejection remains binding.');
  assert.equal(await page.locator('#receipt-outcome').textContent(), 'Can be erased');
  assert.equal(await page.locator('#survival-outcome').textContent(), 'Does not survive');
  passed('Receipt loss does not incorrectly imply a release bypass');

  await page.locator('[data-surface="release"]').check();
  await page.locator('#judge-count').selectOption('8');
  assert.equal(await page.locator('#judge-verdict').textContent(), '8 judges reject the original claim.');
  assert.equal(await page.locator('#release-outcome').textContent(), 'False support has a route.');
  assert.ok((await page.locator('#comparison-note').textContent()).includes('the same outcome'));
  passed('Additional correct judges do not alter stipulated permissions; matched comparator remains a tie');

  await page.locator('#reset-explorer').click();
  assert.equal(await page.locator('[data-surface]:checked').count(), 0);
  assert.equal(await page.locator('#judge-count').inputValue(), '1');
  await page.locator('[data-surface="release"]').focus();
  await page.keyboard.press('Space');
  assert.ok(await page.locator('[data-surface="release"]').isChecked());
  passed('Reset restores boundaries and native keyboard checkbox interaction works');
  await page.locator('#reset-explorer').click();
  await page.locator('#experiment').screenshot({path: path.join(out, 'website-explorer-desktop.png')});

  for (const width of [900, 390, 320]) {
    await page.setViewportSize({width, height: 844});
    await noOverflow(page, 'Research overview ' + width + 'px');
    if (width === 390) {
      await page.evaluate(() => window.scrollTo(0, 0));
      await page.screenshot({path: path.join(out, 'website-mobile.png')});
      await page.locator('.explorer').screenshot({path: path.join(out, 'website-explorer-mobile.png')});
    }
  }
  await page.goto(url('research/independent-no-paper.html'));
  await noOverflow(page, 'Manuscript 320px');
  await page.goto(url('research/independent-no-protocol.html'));
  assert.ok((await page.locator('h1').textContent()).includes('matched evaluation protocol'));
  await noOverflow(page, 'Study protocol 320px');
  passed('Study protocol renders');

  await page.setViewportSize({width: 1440, height: 1000});
  await page.goto(url('index.html'));
  await page.getByRole('link', {name: /^Explore the research/}).click();
  assert.ok(page.url().endsWith('/independent-no.html'));
  passed('Framework homepage research entrance reaches the overview');

  const plainContext = await browser.newContext({javaScriptEnabled: false, viewport: {width: 390, height: 844}});
  await plainContext.route(/^https?:\/\//, route => route.abort());
  const plainPage = await plainContext.newPage();
  await plainPage.goto(url('independent-no.html'));
  assert.ok(await plainPage.locator('.no-script').isVisible());
  assert.ok(!(await plainPage.locator('[data-explorer]').isVisible()));
  passed('JavaScript-disabled reader gets an honest static explanation');
  await plainContext.close();

  for (const name of ['independent-no.html', 'research/independent-no-paper.html', 'research/independent-no-protocol.html']) {
    await checkLocalLinks(path.join(site, name));
  }
  passed('New reading-page assets, downloads, and local anchors resolve');
  assert.deepEqual(report.browserErrors, []);
  assert.deepEqual(report.externalRequests, []);
  passed('No page errors or external browser requests');
  report.status = 'PASS';
}

main().catch(error => {
  report.status = 'FAIL';
  report.failure = String(error.stack || error);
  process.exitCode = 1;
}).finally(async () => {
  if (browser) await browser.close();
  await fs.mkdir(out, {recursive: true});
  await fs.writeFile(path.join(out, 'report.json'), JSON.stringify(report, null, 2) + '\n');
  console.log(JSON.stringify(report, null, 2));
});
