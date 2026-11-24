const fs = require('node:fs');
const path = require('node:path');
const {buildPage, sha, CURRENT_UI_VERSION} = require('./build.cjs');
const {rebaseFont, withoutFontHref} = require('./fonts.cjs');
const {readReview, verifyReview} = require('./review.cjs');
const {CURRENT_THEME_VERSION, addTheme, removeTheme} = require('./theme.cjs');
const {HEADER_SELECTOR_VERSION, addHeaderSelector, removeHeaderSelector} = require('./header-selector.cjs');
const {addLegacyPresetLabel, removeLegacyPresetLabel} = require('./preset-label.cjs');

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
  const themeVersion = review.theme_version ?? 0;
  if (!archived && themeVersion !== CURRENT_THEME_VERSION) throw Error('NEW_THEME_REQUIRED: ' + run);
  const sourceText = fs.readFileSync(path.join(run, 'scenario.cjs'), 'utf8');
  const preview = path.join(run, 'preview.html');
  const built = buildPage({scenario: {sourceText}, outDir: run, uiVersion, themeVersion});
  const evidence = path.join(run, review.checks.browser.evidence);
  let reviewedSha = (archived && review.reviewed_preview_sha256) || built.hashes.preview;
  let layoutBuild = built;
  let html = built.html;
  const migrated = review.header_selector_version !== undefined;
  let migratedHtml;
  if (migrated) {
    if (!archived || uiVersion >= 3 || review.header_selector_version !== HEADER_SELECTOR_VERSION) {
      throw Error('HEADER_SELECTOR_VERSION_UNSUPPORTED: ' + run);
    }
    migratedHtml = fs.readFileSync(preview, 'utf8');
    html = removeHeaderSelector(migratedHtml);
    if (migratedHtml !== addHeaderSelector(html)) throw Error('REBUILD_MISMATCH: ' + preview);
    const headerEvidence = path.join(run, 'evidence', 'header-selector.json');
    requireBrowserResults(headerEvidence, 'HEADER_SELECTOR_UNVERIFIED', studyViewports, result =>
      result.build_sha256 === sha(withoutFontHref(migratedHtml)) &&
      result.header_selector_checked === true && result.input_behavior_checked === true);
  }

  // Reverse the scoped updates to check the exact layout that was reviewed,
  // even when its runtime assets differ from the current builder.
  const baseSha = review.theme_base_sha256;
  const presetLabelRemoved = review.preset_label_removed === true;
  if (presetLabelRemoved && (!archived || baseSha === undefined || uiVersion >= 2)) {
    throw Error('PRESET_LABEL_UPDATE_NOT_ARCHIVED: ' + run);
  }
  if (baseSha !== undefined) {
    if (!archived || themeVersion !== CURRENT_THEME_VERSION) throw Error('THEME_BASE_NOT_ARCHIVED: ' + run);
    if (!migrated) html = fs.readFileSync(preview, 'utf8');
    const beforeLabelUpdate = presetLabelRemoved ? addLegacyPresetLabel(html) : html;
    const base = removeTheme(beforeLabelUpdate);
    const restored = addTheme(base);
    const expected = presetLabelRemoved ? removeLegacyPresetLabel(restored) : restored;
    if (sha(base) !== baseSha || !base.includes('<script>' + sourceText.replace(/<\/script/gi, '<\\/script') + '</script>') ||
        expected !== html) throw Error('REBUILD_MISMATCH: ' + preview);
    layoutBuild = {...built, html: base};
    reviewedSha = review.reviewed_preview_sha256 || baseSha;
  } else {
    if (migrated && html !== built.html) throw Error('REBUILD_MISMATCH: ' + preview);
    if (!migrated) requireBuildBytes(preview, html);
  }
  if (themeVersion) requireThemeEvidence(run, sha(withoutFontHref(html)), presetLabelRemoved);
  if (built.uiVersion !== 0) {
    requireStudyEvidence(evidence, layoutBuild, reviewedSha);
    return migratedHtml ?? html;
  }
  if (built.graphView) {
    requireGraphEvidence(evidence, layoutBuild, reviewedSha);
    return migratedHtml ?? html;
  }

  const checkpoints = Object.values(built.traces).reduce((total, {lineSteps}) => {
    const frames = lineSteps?.at(-1).state.frames;
    const hasNodeCalls = frames && Object.values(frames).some(frame=>frame.parameterCellId);
    return total + (hasNodeCalls ? lineSteps.length : 0);
  }, 0);
  // Some reviewed legacy layouts predate the current-node card.
  if (checkpoints && (baseSha === undefined || /dataset\.currentNode|data-current-node/.test(layoutBuild.html))) {
    requireNodeEvidence(evidence, reviewedSha, checkpoints);
  }
  return migratedHtml ?? html;
}

function requireThemeEvidence(run, buildSha, presetLabelRemoved) {
  const file = path.join(run, 'evidence', 'theme.json');
  let report;
  try { report = JSON.parse(fs.readFileSync(file, 'utf8')); } catch {}
  if (report?.status !== 'pass' || report.build_sha256 !== buildSha ||
      ![report.system, report.storage, report.storage_unavailable, report.cross_tab].every(value => value === true) ||
      (presetLabelRemoved && report.preset_label_checked !== true)) {
    throw Error('THEME_UNVERIFIED: ' + file);
  }
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
    (built.uiVersion < 2 || result.preset_label_checked === true) &&
    (built.uiVersion < 3 || (result.header_selector_checked === true && result.input_behavior_checked === true)) &&
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
