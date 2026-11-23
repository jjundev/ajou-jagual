const {test} = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const os = require('node:os');
const path = require('node:path');
const {buildPage} = require('../scripts/build.cjs');
const {createReview, verifyReview} = require('../scripts/review.cjs');
const {rebaseFont} = require('../scripts/fonts.cjs');
const {save} = require('../scripts/save.cjs');
const {fixtureReport} = require('./fixtures/study-report.cjs');

test('saved and archived pages use the reviewed shared font from their own directories', t => {
  const tmp = fs.mkdtempSync(path.join(os.tmpdir(), 'ds font 한글 '));
  t.after(() => fs.rmSync(tmp, {recursive: true, force: true}));
  const run = path.join(tmp, 'stage', 'run');
  const dest = path.join(tmp, 'notes');
  fs.mkdirSync(path.join(run, 'evidence'), {recursive: true});
  const scenario = path.join(__dirname, '../examples/0928/value-address.cjs');
  const sourceText = fs.readFileSync(scenario, 'utf8');
  const {html, traces} = buildPage({scenario: {definition: require(scenario), sourceText}, outDir: run});
  for (const [name, text] of Object.entries({
    'preview.html': html, 'scenario.cjs': sourceText, 'trace.json': JSON.stringify(traces),
    'source.json': '{}', 'brief.md': 'fixture', 'evidence/pass.md': 'fixture',
  })) fs.writeFileSync(path.join(run, name), text);
  fs.writeFileSync(path.join(run, 'evidence/browser.json'), JSON.stringify(fixtureReport(run)));
  const review = createReview(run);
  for (const check of Object.values(review.checks)) {
    Object.assign(check, {status: 'pass', evidence: 'evidence/pass.md', notes: 'fixture'});
  }
  review.checks.browser.evidence = 'evidence/browser.json';
  fs.writeFileSync(path.join(run, 'review.json'), JSON.stringify(review));

  const result = save({run, dest, name: '값과 주소'});
  const files = [path.join(run, 'preview.html'), result.html, path.join(result.dir, 'preview.html')];
  const cssFiles = files.map(file => {
    const page = fs.readFileSync(file, 'utf8');
    assert.equal(rebaseFont(page, path.dirname(file), run), html);
    const ref = page.match(/data-ds-interactive-font href="([^"]+)"/)[1];
    return fs.realpathSync(path.resolve(path.dirname(file), decodeURIComponent(ref)));
  });
  assert.equal(new Set(cssFiles).size, 1);
  const css = fs.readFileSync(cssFiles[0], 'utf8');
  for (const [weight, name] of [[400, 'Regular'], [500, 'Medium'], [600, 'SemiBold'], [700, 'Bold']]) {
    assert.match(css, new RegExp(`font-weight: ${weight};[^}]+/woff2/Pretendard-${name}\\.woff2`));
    assert.ok(fs.existsSync(path.join(path.dirname(cssFiles[0]), `woff2/Pretendard-${name}.woff2`)));
  }
  assert.deepEqual(verifyReview(run), []);
  assert.deepEqual(verifyReview(result.dir), []);
});
