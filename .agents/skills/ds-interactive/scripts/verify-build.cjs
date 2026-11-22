const fs = require('node:fs');
const path = require('node:path');
const {buildPage} = require('./build.cjs');
const {rebaseFont} = require('./fonts.cjs');
const {readReview, verifyReview} = require('./review.cjs');

function requireBuildBytes(file, built) {
  if (!fs.readFileSync(file).equals(Buffer.from(built))) {
    throw Error('REBUILD_MISMATCH: ' + file);
  }
}

function checkReady(run, {archived = false} = {}) {
  run = path.resolve(run);
  const issues = verifyReview(run);
  if (issues.length) throw Error(JSON.stringify(issues));
  const sourceText = fs.readFileSync(path.join(run, 'scenario.cjs'), 'utf8');
  const built = buildPage({scenario: {sourceText}, outDir: run});
  requireBuildBytes(path.join(run, 'preview.html'), built.html);

  const checkpoints = Object.values(built.traces).reduce((total, {lineSteps}) => {
    const frames = lineSteps?.at(-1).state.frames;
    const hasNodeCalls = frames && Object.values(frames).some(frame=>frame.parameterCellId);
    return total + (hasNodeCalls ? lineSteps.length : 0);
  }, 0);
  if (checkpoints) {
    const review = readReview(run);
    const sha = (archived && review.reviewed_preview_sha256) || built.hashes.preview;
    requireNodeEvidence(path.join(run, review.checks.browser.evidence), sha, checkpoints);
  }
  return built.html;
}

function requireNodeEvidence(file, sha, checkpoints) {
  let report;
  try {
    report = JSON.parse(fs.readFileSync(file, 'utf8'));
  } catch {
    throw Error('CURRENT_NODE_UNVERIFIED: ' + file);
  }
  const combinations = [[1440, 900], [1024, 768], [375, 812]].flatMap(viewport =>
    ['light', 'dark'].map(theme => JSON.stringify([viewport, theme])));
  const passed = new Set((Array.isArray(report?.results) ? report.results : [])
    .filter(result => result?.status === 'pass' && result.sha256 === sha &&
      result.current_node_checked === checkpoints)
    .map(result => JSON.stringify([result.viewport, result.theme])));
  if (report?.status !== 'pass' || !combinations.every(combination => passed.has(combination))) {
    throw Error('CURRENT_NODE_UNVERIFIED: ' + file);
  }
}

function checkPublished(run, html) {
  const rebuilt = checkReady(run, {archived: true});
  requireBuildBytes(html, rebaseFont(rebuilt, run, path.dirname(html)));
}

module.exports = {checkReady, checkPublished};

if (require.main === module) {
  try {
    const [run, html] = process.argv.slice(2);
    if (!run) throw Error('usage: node verify-build.cjs RUN [PUBLIC_HTML]');
    if (html) checkPublished(run, html);
    else checkReady(run);
    console.log(JSON.stringify({ok: true}));
  } catch (error) {
    console.error(error.message);
    process.exitCode = 1;
  }
}
