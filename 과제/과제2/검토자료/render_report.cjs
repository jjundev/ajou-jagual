const { chromium } = require('/Users/hyunjun_macbook_pro/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright-core');
const fs = require('node:fs');
const path = require('node:path');
const { pathToFileURL } = require('node:url');

(async () => {
  const root = path.resolve(__dirname, '..');
  const browser = await chromium.launch({
    executablePath: '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',
    headless: true,
  });
  try {
    const page = await browser.newPage({ viewport: { width: 1000, height: 700 } });
    await page.goto(pathToFileURL(path.join(root, '보고서_초안.html')).href);
    await page.emulateMedia({ media: 'print' });
    await page.evaluate(() => document.fonts.ready);
    const checks = await page.evaluate(() => ({
      fontsLoaded: document.fonts.check('12px Pretendard'),
      sourceParts: Array.from(document.querySelectorAll('.source-code code'), el => el.textContent),
      appendix: Array.from(document.querySelectorAll('.appendix-code code'), el => el.textContent).join(''),
      caseCount: document.querySelectorAll('.execution-grid').length,
      sourceTables: document.querySelectorAll('.source-table').length,
      screenshots: Array.from(document.querySelectorAll('.terminal-evidence img'), el => ({ loaded: el.complete && el.naturalWidth > 0, src: el.src })),
      overflow: Array.from(document.querySelectorAll('pre, td')).filter(el => el.scrollWidth > el.clientWidth + 2).map(el => el.textContent.slice(0, 100)),
    }));
    const manifest = JSON.parse(fs.readFileSync(path.join(root, '검토자료/보고서_구성.json'), 'utf8'));
    const source = fs.readFileSync(path.join(root, 'HW2.c'), 'utf8');
    if (!checks.fontsLoaded) throw new Error('Korean font did not load');
    if (checks.appendix !== source) throw new Error('Appendix differs from current source');
    if (JSON.stringify(checks.sourceParts) !== JSON.stringify(manifest.source_parts)) throw new Error('Analysis code differs from source chunks');
    if (checks.caseCount !== manifest.case_count) throw new Error('Missing execution case');
    if (checks.screenshots.length !== manifest.screenshot_count || checks.screenshots.some(image => !image.loaded)) throw new Error('Missing or unloaded actual terminal screenshot');
    if (checks.overflow.length) throw new Error('Horizontal overflow: ' + checks.overflow.join('\n'));
    await page.pdf({
      path: path.join(root, '보고서_초안.pdf'),
      printBackground: true,
      preferCSSPageSize: true,
      displayHeaderFooter: false,
      tagged: true,
    });
    fs.writeFileSync(path.join(root, '검토자료/HTML_검증.json'), JSON.stringify({ ...checks, sourceParts: checks.sourceParts.length, appendix: 'byte-equivalent UTF-8 text confirmed' }, null, 2) + '\n');
    console.log(JSON.stringify({ fontsLoaded: checks.fontsLoaded, sourceTables: checks.sourceTables, sourceParts: checks.sourceParts.length, caseCount: checks.caseCount, screenshots: checks.screenshots.length, overflow: checks.overflow.length }));
  } finally {
    await browser.close();
  }
})().catch(error => { console.error(error); process.exit(1); });
