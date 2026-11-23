const fs = require('node:fs');
const path = require('node:path');
const {buildPage, sha, CURRENT_UI_VERSION} = require('./build.cjs');
const {rebaseFont, withoutFontHref} = require('./fonts.cjs');
const {readReview, verifyReview} = require('./review.cjs');

const treeViewports = [[1440, 900], [1024, 768], [375, 812]];
const graphViewports = [[1440, 900], [1280, 800], [1279, 800], [375, 812]];
const studyViewports = [...graphViewports, [320, 812]];
const mobileStages = ['initial', 'middle', 'last'];

function requiredCombinations(viewports) {
  return viewports.flatMap(viewport => ['light', 'dark'].map(theme => JSON.stringify([viewport, theme])));
}

function requireBuildBytes(file, built) {
  if (!fs.readFileSync(file).equals(Buffer.from(built))) {
    throw Error('REBUILD_MISMATCH: ' + file);
  }
}

function checkReady(run, {archived = false} = {}) {
  run = path.resolve(run);
  const issues = verifyReview(run);
  if (issues.length) throw Error(JSON.stringify(issues));
  const review = readReview(run);
  const uiVersion = Object.hasOwn(review, 'ui_version') ? review.ui_version : 0;
  if (!archived && uiVersion !== CURRENT_UI_VERSION) throw Error('NEW_UI_REQUIRED: ' + run);
  const sourceText = fs.readFileSync(path.join(run, 'scenario.cjs'), 'utf8');
  const built = buildPage({scenario: {sourceText}, outDir: run, uiVersion});
  requireBuildBytes(path.join(run, 'preview.html'), built.html);

  const evidence = path.join(run, review.checks.browser.evidence);
  const reviewedSha = (archived && review.reviewed_preview_sha256) || built.hashes.preview;
  if (built.uiVersion !== 0) {
    requireStudyEvidence(evidence, built, reviewedSha);
    return built.html;
  }
  if (built.graphView) {
    requireGraphEvidence(evidence, built, reviewedSha);
    return built.html;
  }

  const checkpoints = Object.values(built.traces).reduce((total, {lineSteps}) => {
    const frames = lineSteps?.at(-1).state.frames;
    const hasNodeCalls = frames && Object.values(frames).some(frame=>frame.parameterCellId);
    return total + (hasNodeCalls ? lineSteps.length : 0);
  }, 0);
  if (checkpoints) requireNodeEvidence(evidence, reviewedSha, checkpoints);
  return built.html;
}

function requireBrowserResults(file, error, viewports, matches, validReport = () => true) {
  let report;
  try {
    report = JSON.parse(fs.readFileSync(file, 'utf8'));
  } catch {
    throw Error(error + ': ' + file);
  }
  const passed = new Set((Array.isArray(report?.results) ? report.results : [])
    .filter(result => result?.status === 'pass' && matches(result))
    .map(result => JSON.stringify([result.viewport, result.theme])));
  if (report?.status !== 'pass' || !validReport(report) || !requiredCombinations(viewports).every(key => passed.has(key))) {
    throw Error(error + ': ' + file);
  }
}

function requireNodeEvidence(file, previewSha, checkpoints) {
  requireBrowserResults(file, 'CURRENT_NODE_UNVERIFIED', treeViewports, result =>
    result.sha256 === previewSha && result.current_node_checked === checkpoints);
}

function requireGraphEvidence(file, built, previewSha) {
  const traces = Object.values(built.traces);
  const snapshots = traces.reduce((total, trace) => total + trace.snapshots.length, 0);
  const buildSha = sha(withoutFontHref(built.html));
  requireBrowserResults(file, 'GRAPH_LAYOUT_UNVERIFIED', graphViewports, result =>
    result.sha256 === previewSha && result.build_sha256 === buildSha &&
    result.graph_layout_version === 2 && result.graph_view === built.graphView &&
    result.presets === traces.length && result.snapshots_checked === snapshots &&
    (result.viewport?.[0] !== 375 || JSON.stringify(result.mobile_first_screen) === JSON.stringify(mobileStages)),
  report => [report.console_errors, report.external_requests].every(list => Array.isArray(list) && list.length === 0));
}

function requireStudyEvidence(file, built, previewSha) {
  const traces = Object.values(built.traces);
  const snapshots = traces.reduce((total, trace) => total + (trace.lineSteps || trace.snapshots).length, 0);
  const buildSha = sha(withoutFontHref(built.html));
  requireBrowserResults(file, 'STUDY_UI_UNVERIFIED', studyViewports, result =>
    result.sha256 === previewSha && result.build_sha256 === buildSha &&
    result.ui_version === built.uiVersion && result.kind === built.kind &&
    result.layout_checked === true && result.controls_checked === true &&
    result.presets === traces.length && result.snapshots_checked === snapshots &&
    (result.viewport?.[0] !== 375 || JSON.stringify(result.mobile_first_screen) === JSON.stringify(mobileStages)),
  report => [report.console_errors, report.external_requests].every(list => Array.isArray(list) && list.length === 0));
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
